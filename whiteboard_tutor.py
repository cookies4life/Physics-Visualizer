"""Whiteboard Tutor: an AI physics tutor you can draw and chat with.

Opens two synchronized windows — a drawing whiteboard and a chat panel —
backed by Google's Gemini API (vision + text), which has a genuinely free
tier (unlike Claude/GPT, which are metered/paid). Draw a free-body diagram
and press "Submit to Tutor"; the tutor looks at the drawing and replies in
the chat. Typed chat messages work the same way, without needing a drawing.

This is the one feature in the app that needs a network connection and a
(free) Gemini API key, since "an AI that looks at your drawing and teaches
you" requires an actual trained LLM rather than something this app could
train itself — see `_get_client()` for how the key is collected and stored.
"""

import io
import os
import queue
import threading
import tkinter as tk
from pathlib import Path
from tkinter import colorchooser, messagebox, simpledialog, ttk

from PIL import Image, ImageDraw, ImageFont, ImageTk

MODEL_ID = "gemini-3.5-flash"

SYSTEM_PROMPT = """You are "Whiteboard Tutor", a friendly, patient physics tutor working with a
student through a shared whiteboard and a text chat.

How you receive input:
- The student draws on a whiteboard (free-body diagrams, sketches, handwritten work) and presses
  "Submit to Tutor" to send you a snapshot image, optionally with a short typed question.
- The student can also just type a message in the chat, with no drawing.
- If handwriting or labels in an image are too messy to read confidently, say so plainly and ask
  the student to rewrite that part more legibly rather than guessing at what it says.

How you should teach:
- When checking a free-body diagram: verify every force that should be present actually is
  (weight, normal force, applied forces, friction, tension, etc., as the situation calls for),
  check that arrow directions and relative lengths look physically reasonable, and flag any force
  that's drawn but doesn't actually belong.
- Teach Socratically: say what's correct first, then ask a guiding question about anything wrong
  or missing rather than immediately stating the fix. Give the direct answer only if asked, or if
  the student is clearly stuck after a couple of exchanges.
- Be specific and encouraging — reference exactly what you see ("the arrow pointing down from the
  block's right edge") rather than generic praise or generic corrections.
- Keep replies short and focused: a few sentences or a tight list, not an essay.
"""

CONFIG_DIR = Path.home() / ".physics_visualizer"
API_KEY_FILE = CONFIG_DIR / "gemini_api_key.txt"

COLORS = ['#000000', '#ffffff', '#c1440e', '#1d4fd8', '#1f8a3b', '#d9740c', '#7c4fd6', '#8a5a2b', '#c94f9c', '#666666']

CANVAS_W, CANVAS_H = 900, 560
LINE_SPACING = 36
GUIDE_RGB = (238, 241, 246)


# ---------------------------------------------------------------------------
# API key handling — this app runs standalone, so it needs its own credential,
# separate from whatever tool the user used to build it. We check the
# environment and a small local config file first, and only ask once.
# ---------------------------------------------------------------------------

def _load_saved_api_key():
    if API_KEY_FILE.exists():
        return API_KEY_FILE.read_text().strip() or None
    return None


def _save_api_key(key):
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    API_KEY_FILE.write_text(key.strip())


def _get_client(parent):
    """Return a google.genai.Client, or None if unavailable/declined."""
    try:
        from google import genai
    except ImportError:
        messagebox.showerror(
            "Missing dependency",
            "The Whiteboard Tutor needs the 'google-genai' Python package.\n\n"
            "Install it with:\n\n    pip install google-genai\n\nthen reopen the Whiteboard Tutor.",
            parent=parent)
        return None

    key = os.environ.get("GEMINI_API_KEY") or _load_saved_api_key()
    if not key:
        key = simpledialog.askstring(
            "Gemini API Key",
            "The Whiteboard Tutor is powered by Google's Gemini — it needs a (free) API key to "
            "look at your drawings and chat with you.\n\n"
            "Get one at no cost from aistudio.google.com/apikey, then paste it below.\n"
            "It's saved locally so you won't be asked again.",
            parent=parent, show='*')
        if not key or not key.strip():
            return None
        key = key.strip()
        _save_api_key(key)
    os.environ.setdefault("GEMINI_API_KEY", key)
    try:
        return genai.Client(api_key=key)
    except Exception as exc:
        messagebox.showerror("Could not start Gemini client", str(exc), parent=parent)
        return None


def _load_font(size):
    candidates = [
        "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/System/Library/Fonts/Helvetica.ttc",
        "/Library/Fonts/Arial.ttf",
        "C:\\Windows\\Fonts\\arial.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ]
    for path in candidates:
        try:
            return ImageFont.truetype(path, size)
        except Exception:
            continue
    try:
        return ImageFont.load_default(size=size)
    except TypeError:
        return ImageFont.load_default()


def _hex_to_rgb(hex_color):
    h = hex_color.lstrip('#')
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


# ---------------------------------------------------------------------------
# Shared session: owns the conversation with Gemini and fans updates out to
# both windows. The API call runs on a background thread (Tkinter's mainloop
# must never block), and results are handed back through a queue that's
# drained on the main thread via `root.after()` — the only thread-safe way to
# touch Tk widgets.
#
# History is a manually-maintained list of `types.Content` (Gemini is
# stateless per-request, like most LLM APIs — the full conversation is resent
# every turn), rather than the SDK's `chats.create()` session helper, since
# that helper's image-input support isn't documented and this path is
# directly verified to work for both text and images.
# ---------------------------------------------------------------------------

class TutorSession:
    def __init__(self, client, root):
        self.client = client
        self.root = root
        self.history = []
        self.event_queue = queue.Queue()
        self.listeners = []
        self._poll()

    def add_listener(self, fn):
        self.listeners.append(fn)

    def _poll(self):
        try:
            while True:
                event = self.event_queue.get_nowait()
                for fn in list(self.listeners):
                    fn(*event)
        except queue.Empty:
            pass
        if self.root.winfo_exists():
            self.root.after(50, self._poll)

    def _emit(self, *event):
        self.event_queue.put(event)

    def send_text(self, text):
        from google.genai import types
        text = text.strip()
        if not text:
            return
        self._emit('user_text', text)
        self.history.append(types.Content(role='user', parts=[types.Part.from_text(text=text)]))
        self._ask()

    def send_drawing(self, pil_image, caption_text):
        from google.genai import types
        buf = io.BytesIO()
        pil_image.save(buf, format='PNG')
        image_bytes = buf.getvalue()
        thumb = pil_image.copy()
        thumb.thumbnail((220, 160))
        self._emit('user_image', thumb, caption_text)
        caption = caption_text or "Here's what I drew on the whiteboard. Can you take a look?"
        parts = [
            types.Part.from_bytes(data=image_bytes, mime_type='image/png'),
            types.Part.from_text(text=caption),
        ]
        self.history.append(types.Content(role='user', parts=parts))
        self._ask()

    def _ask(self):
        self._emit('assistant_start')
        if self.client is None:
            self._emit('assistant_error', "No Gemini API connection is configured. Restart Whiteboard "
                                           "Tutor and enter a (free) API key, or set the GEMINI_API_KEY "
                                           "environment variable.")
            return

        def worker():
            from google.genai import types
            try:
                full_text = []
                stream = self.client.models.generate_content_stream(
                    model=MODEL_ID,
                    contents=self.history,
                    config=types.GenerateContentConfig(system_instruction=SYSTEM_PROMPT),
                )
                for chunk in stream:
                    text = chunk.text
                    if text:
                        full_text.append(text)
                        self._emit('assistant_delta', text)
                reply = ''.join(full_text)
                self.history.append(types.Content(role='model', parts=[types.Part.from_text(text=reply)]))
                self._emit('assistant_done')
            except Exception as exc:
                self._emit('assistant_error', str(exc))

        threading.Thread(target=worker, daemon=True).start()


# ---------------------------------------------------------------------------
# Chat window
# ---------------------------------------------------------------------------

def _open_chat_window(master, session, geometry):
    win = tk.Toplevel(master)
    win.title("Whiteboard Tutor — Chat")
    win.geometry(geometry)

    header = ttk.Frame(win)
    header.pack(fill=tk.X)
    ttk.Label(header, text="Chat with your Tutor", font=(None, 14, 'bold')).pack(anchor='w', padx=10, pady=(8, 0))
    ttk.Label(
        header,
        text="Type a question below, or draw on the whiteboard and hit Submit — it shows up here too.",
        wraplength=400, foreground='#5a5f68',
    ).pack(anchor='w', padx=10, pady=(0, 8))

    body = ttk.Frame(win)
    body.pack(fill=tk.BOTH, expand=True, padx=8)
    transcript = tk.Text(body, wrap='word', state='disabled', font=(None, 11), padx=10, pady=8, bg='#fbfbfb', fg='black')
    scrollbar = ttk.Scrollbar(body, command=transcript.yview)
    transcript.config(yscrollcommand=scrollbar.set)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    transcript.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    transcript.tag_configure('user', foreground='#1d4fd8', font=(None, 11, 'bold'))
    transcript.tag_configure('assistant', foreground='#1f8a3b', font=(None, 11, 'bold'))
    transcript.tag_configure('body', foreground='black')
    transcript.tag_configure('error', foreground='#c1440e')
    transcript.tag_configure('caption', foreground='#5a5f68', font=(None, 10, 'italic'))

    photo_refs = []  # keep PhotoImage references alive — Tk drops them otherwise

    def append(text, tag=None):
        transcript.config(state='normal')
        transcript.insert(tk.END, text, tag)
        transcript.see(tk.END)
        transcript.config(state='disabled')

    def on_event(kind, *payload):
        if kind == 'user_text':
            append("\nYou: ", 'user')
            append(payload[0] + "\n", 'body')
        elif kind == 'user_image':
            thumb, caption = payload
            append("\nYou (whiteboard):\n", 'user')
            photo = ImageTk.PhotoImage(thumb)
            photo_refs.append(photo)
            transcript.config(state='normal')
            transcript.image_create(tk.END, image=photo)
            transcript.insert(tk.END, "\n")
            transcript.config(state='disabled')
            if caption:
                append(caption + "\n", 'caption')
        elif kind == 'assistant_start':
            append("\nTutor: ", 'assistant')
        elif kind == 'assistant_delta':
            append(payload[0], 'body')
        elif kind == 'assistant_done':
            append("\n", 'body')
        elif kind == 'assistant_error':
            append(f"\n[{payload[0]}]\n", 'error')

    session.add_listener(on_event)

    entry_row = ttk.Frame(win)
    entry_row.pack(fill=tk.X, padx=8, pady=8)
    entry_var = tk.StringVar()
    entry = ttk.Entry(entry_row, textvariable=entry_var, font=(None, 11))
    entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 6))

    def send(_event=None):
        text = entry_var.get()
        if not text.strip():
            return
        entry_var.set('')
        session.send_text(text)

    entry.bind('<Return>', send)
    ttk.Button(entry_row, text='Send', command=send).pack(side=tk.LEFT)

    return win


# ---------------------------------------------------------------------------
# Whiteboard window — a small paint app. Every stroke/shape/text is drawn
# onto the visible Tk canvas AND mirrored onto a same-sized PIL image, so
# "Submit" can export a real PNG without depending on Ghostscript (which
# canvas.postscript()-based export would require and often isn't installed).
# ---------------------------------------------------------------------------

def _open_whiteboard_window(master, session, geometry):
    win = tk.Toplevel(master)
    win.title("Whiteboard Tutor — Whiteboard")
    win.geometry(geometry)

    header = ttk.Frame(win)
    header.pack(fill=tk.X)
    ttk.Label(header, text="Draw here — FBDs, sketches, or write out your question", font=(None, 14, 'bold')).pack(anchor='w', padx=10, pady=(8, 2))
    ttk.Label(
        header,
        text="Tip: write along the faint guide lines so your handwriting stays legible for the tutor.",
        wraplength=860, foreground='#5a5f68',
    ).pack(anchor='w', padx=10, pady=(0, 6))

    toolbar = ttk.Frame(win)
    toolbar.pack(fill=tk.X, padx=8, pady=4)

    tool = tk.StringVar(value='pencil')
    color = tk.StringVar(value='#000000')
    size = tk.IntVar(value=3)

    tools_frame = ttk.Frame(toolbar)
    tools_frame.pack(side=tk.LEFT)
    for name, label in [('pencil', 'Pencil'), ('brush', 'Marker'), ('line', 'Line'),
                         ('rect', 'Rectangle'), ('oval', 'Ellipse'), ('text', 'Text'), ('eraser', 'Eraser')]:
        ttk.Radiobutton(tools_frame, text=label, variable=tool, value=name).pack(side=tk.LEFT, padx=2)

    ttk.Label(toolbar, text='Size').pack(side=tk.LEFT, padx=(16, 2))
    ttk.Scale(toolbar, from_=1, to=24, variable=size, orient=tk.HORIZONTAL, length=100).pack(side=tk.LEFT)

    swatch_frame = tk.Frame(toolbar)
    swatch_frame.pack(side=tk.LEFT, padx=(16, 0))
    current_swatch = tk.Label(swatch_frame, width=2, height=1, bg=color.get(), relief=tk.SUNKEN, bd=2)
    current_swatch.pack(side=tk.LEFT, padx=(0, 4))

    def pick_color(c=None):
        if c is None:
            _rgb, hexcolor = colorchooser.askcolor(color=color.get(), parent=win, title="Choose a color")
            if not hexcolor:
                return
            c = hexcolor
        color.set(c)
        current_swatch.config(bg=c)

    for c in COLORS:
        b = tk.Label(swatch_frame, width=2, height=1, bg=c, relief=tk.RAISED, bd=1, cursor='hand2')
        b.bind('<Button-1>', lambda _e, c=c: pick_color(c))
        b.pack(side=tk.LEFT, padx=1)
    ttk.Button(swatch_frame, text='Custom…', command=lambda: pick_color(None)).pack(side=tk.LEFT, padx=(6, 0))

    canvas = tk.Canvas(win, bg='white', width=CANVAS_W, height=CANVAS_H,
                        highlightthickness=1, highlightbackground='#cccccc', cursor='crosshair')
    canvas.pack(padx=10, pady=(4, 8))

    state = {}

    def fresh_pil():
        img = Image.new('RGB', (CANVAS_W, CANVAS_H), 'white')
        d = ImageDraw.Draw(img)
        for y in range(LINE_SPACING, CANVAS_H, LINE_SPACING):
            d.line([(0, y), (CANVAS_W, y)], fill=GUIDE_RGB)
        return img, d

    state['pil_image'], state['draw'] = fresh_pil()
    for y in range(LINE_SPACING, CANVAS_H, LINE_SPACING):
        canvas.create_line(0, y, CANVAS_W, y, fill='#eef1f6', tags='guide')

    stroke_history = []   # list of lists of canvas item ids, one entry per completed op
    undo_stack = []        # list of PIL image snapshots taken just before each op began
    current_ids = []
    last_point = {'x': 0, 'y': 0}
    shape_start = {'x': 0, 'y': 0}
    shape_item = {'id': None}

    def push_undo_snapshot():
        undo_stack.append(state['pil_image'].copy())
        if len(undo_stack) > 25:
            undo_stack.pop(0)

    def undo():
        if not undo_stack:
            return
        if stroke_history:
            for item_id in stroke_history.pop():
                canvas.delete(item_id)
        state['pil_image'] = undo_stack.pop()
        state['draw'] = ImageDraw.Draw(state['pil_image'])

    def on_press(event):
        x, y = event.x, event.y
        t = tool.get()
        if t == 'text':
            text = simpledialog.askstring("Add text", "Enter text:", parent=win)
            if text:
                push_undo_snapshot()
                font = _load_font(max(12, size.get() * 4))
                item = canvas.create_text(x, y, text=text, fill=color.get(),
                                           font=('Arial', max(10, size.get() * 3)), anchor='nw')
                fill_rgb = _hex_to_rgb(color.get())
                state['draw'].text((x, y), text, fill=fill_rgb, font=font)
                stroke_history.append([item])
            return
        push_undo_snapshot()
        current_ids.clear()
        last_point['x'], last_point['y'] = x, y
        shape_start['x'], shape_start['y'] = x, y
        if t == 'line':
            shape_item['id'] = canvas.create_line(x, y, x, y, fill=color.get(), width=size.get(), capstyle=tk.ROUND)
        elif t == 'rect':
            shape_item['id'] = canvas.create_rectangle(x, y, x, y, outline=color.get(), width=max(1, size.get() // 2))
        elif t == 'oval':
            shape_item['id'] = canvas.create_oval(x, y, x, y, outline=color.get(), width=max(1, size.get() // 2))

    def on_drag(event):
        x, y = event.x, event.y
        t = tool.get()
        if t in ('pencil', 'brush', 'eraser'):
            is_eraser = t == 'eraser'
            col = 'white' if is_eraser else color.get()
            width = size.get() * (3 if is_eraser else (2 if t == 'brush' else 1))
            item = canvas.create_line(last_point['x'], last_point['y'], x, y,
                                       fill=col, width=width, capstyle=tk.ROUND, smooth=True)
            current_ids.append(item)
            rgb = (255, 255, 255) if is_eraser else _hex_to_rgb(color.get())
            state['draw'].line([(last_point['x'], last_point['y']), (x, y)], fill=rgb, width=width)
            last_point['x'], last_point['y'] = x, y
        elif t in ('line', 'rect', 'oval') and shape_item['id'] is not None:
            canvas.coords(shape_item['id'], shape_start['x'], shape_start['y'], x, y)

    def on_release(event):
        t = tool.get()
        if t in ('pencil', 'brush', 'eraser'):
            if current_ids:
                stroke_history.append(list(current_ids))
            current_ids.clear()
        elif t in ('line', 'rect', 'oval') and shape_item['id'] is not None:
            x, y = event.x, event.y
            x0, y0 = shape_start['x'], shape_start['y']
            rgb = _hex_to_rgb(color.get())
            width = max(1, size.get() // 2)
            if t == 'line':
                state['draw'].line([(x0, y0), (x, y)], fill=rgb, width=size.get())
            elif t == 'rect':
                state['draw'].rectangle([min(x0, x), min(y0, y), max(x0, x), max(y0, y)], outline=rgb, width=width)
            elif t == 'oval':
                state['draw'].ellipse([min(x0, x), min(y0, y), max(x0, x), max(y0, y)], outline=rgb, width=width)
            stroke_history.append([shape_item['id']])
            shape_item['id'] = None

    canvas.bind('<ButtonPress-1>', on_press)
    canvas.bind('<B1-Motion>', on_drag)
    canvas.bind('<ButtonRelease-1>', on_release)

    action_row = ttk.Frame(win)
    action_row.pack(fill=tk.X, padx=8, pady=(0, 8))
    ttk.Button(action_row, text='Undo', command=undo).pack(side=tk.LEFT, padx=4)

    def clear_canvas():
        canvas.delete('all')
        stroke_history.clear()
        undo_stack.clear()
        state['pil_image'], state['draw'] = fresh_pil()
        for y in range(LINE_SPACING, CANVAS_H, LINE_SPACING):
            canvas.create_line(0, y, CANVAS_W, y, fill='#eef1f6', tags='guide')

    ttk.Button(action_row, text='Clear', command=clear_canvas).pack(side=tk.LEFT, padx=4)

    status_var = tk.StringVar(value='')
    ttk.Label(action_row, textvariable=status_var, foreground='#5a5f68').pack(side=tk.LEFT, padx=12)

    prompt_var = tk.StringVar()
    ttk.Entry(action_row, textvariable=prompt_var, width=30).pack(side=tk.LEFT, padx=(20, 4), fill=tk.X, expand=True)

    def submit():
        caption = prompt_var.get().strip()
        prompt_var.set('')
        status_var.set('Sent to tutor…')
        session.send_drawing(state['pil_image'].copy(), caption)

    ttk.Button(action_row, text='Submit to Tutor', command=submit).pack(side=tk.RIGHT, padx=4)

    def on_session_event(kind, *payload):
        if kind == 'assistant_start':
            status_var.set('Tutor is thinking…')
        elif kind == 'assistant_done':
            status_var.set('Tutor replied — check the chat window!')
        elif kind == 'assistant_error':
            status_var.set(f'Error: {payload[0]}')

    session.add_listener(on_session_event)

    return win


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def open_whiteboard_tutor(master=None):
    """Open the Whiteboard Tutor: a synchronized drawing board + AI chat window."""
    owns_root = False
    if master is None:
        master = tk.Tk()
        master.withdraw()
        owns_root = True

    client = _get_client(master)
    session = TutorSession(client, master)

    screen_w = master.winfo_screenwidth()
    board_w, board_h = 980, 760
    chat_w, chat_h = 460, 720
    total_w = board_w + chat_w + 40
    start_x = max(20, (screen_w - total_w) // 2)

    board_win = _open_whiteboard_window(master, session, f"{board_w}x{board_h}+{start_x}+40")
    chat_win = _open_chat_window(master, session, f"{chat_w}x{chat_h}+{start_x + board_w + 20}+40")

    def on_close():
        chat_win.destroy()
        board_win.destroy()
        if owns_root:
            master.destroy()

    board_win.protocol("WM_DELETE_WINDOW", on_close)
    chat_win.protocol("WM_DELETE_WINDOW", on_close)

    return board_win, chat_win
