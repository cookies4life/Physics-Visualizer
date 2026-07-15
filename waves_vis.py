"""Water wave visualization: a ripple tank showing wave propagation,
reflection off walls, and diffraction through gaps and around obstacles.

The water surface is a real 2D finite-difference wave-equation simulation
(numpy grid), not a canned animation — dragging the cursor genuinely injects
a disturbance that propagates, reflects off the tank walls, and diffracts
around whatever obstacles you place.
"""

import math
import tkinter as tk
from tkinter import ttk

import numpy as np
from PIL import Image, ImageTk

import viz_common

NX, NY = 176, 108
SCALE = 5
CANVAS_W, CANVAS_H = NX * SCALE, NY * SCALE
FRAME_MS = 33
DT = 1.0

SHAPE_TOOLS = ('wave', 'wall', 'circle', 'rect', 'source', 'erase')


def open_waves_window(master=None):
    """Create the ripple-tank wave/diffraction demo window."""
    win = tk.Toplevel(master) if master else tk.Tk()
    win.title("Waves — Ripple Tank & Diffraction")
    win.geometry("1320x900+40+20")

    def _maximize_or_fullscreen_max(win_obj: tk.Toplevel):
        try:
            win_obj.state('zoomed')
        except Exception:
            pass
    win.after(100, lambda: _maximize_or_fullscreen_max(win))

    header = ttk.Frame(win, padding=(10, 8))
    header.pack(fill=tk.X)
    ttk.Label(header, text="Waves — Ripple Tank & Diffraction", font=(None, 16, 'bold')).pack(anchor='n')

    explanation = (
        "This is a real water-wave simulation, not an animation loop — every pixel's height is computed "
        "from the 2D wave equation each frame. Click and drag anywhere on the water to make ripples, the "
        "same way touching a real pond sends circular waves outward from your fingertip.\n"
        "Add a wall with a gap and watch what happens where the wave passes through: instead of leaving a "
        "sharp 'shadow' behind the gap the way a beam of particles would, the wave bends and spreads out on "
        "the far side in a fan — that spreading is diffraction, and it happens whenever a wave passes an "
        "edge or squeezes through an opening. It's strongest when the gap is about the same size as the "
        "wavelength; a gap much wider than the wavelength barely bends the wave at all, while a very narrow "
        "gap makes it fan out almost like a fresh point source. Try the single-slit and double-slit presets "
        "below, and adjust the source frequency to change the wavelength and see the effect strengthen or "
        "weaken.")
    ttk.Label(header, text=explanation, wraplength=1280, justify=tk.LEFT, foreground='#3a3d42').pack(anchor='w', pady=(6, 0))

    # --- Equations panel with tabs, positioned beside the main window ---
    eq_win, update_live_tab = _open_equations_tabs(win, "Waves")
    win.protocol("WM_DELETE_WINDOW", lambda: (eq_win.destroy(), win.destroy()))

    ctrl = ttk.Frame(win, padding=(10, 4))
    ctrl.pack(fill=tk.X)

    tool = tk.StringVar(value='wave')
    tools_frame = ttk.Frame(ctrl)
    tools_frame.pack(side=tk.LEFT)
    for name, label in [('wave', 'Make waves'), ('wall', 'Wall (line)'), ('circle', 'Circle obstacle'),
                         ('rect', 'Rectangle obstacle'), ('source', 'Place source'), ('erase', 'Erase obstacle')]:
        ttk.Radiobutton(tools_frame, text=label, variable=tool, value=name).pack(side=tk.LEFT, padx=2)

    ctrl2 = ttk.Frame(win, padding=(10, 0, 10, 4))
    ctrl2.pack(fill=tk.X)

    wave_speed = tk.DoubleVar(value=0.16)   # c^2 term, kept in the stable range
    damping = tk.DoubleVar(value=0.9985)
    src_freq = tk.DoubleVar(value=0.08)     # cycles per frame
    src_amp = tk.DoubleVar(value=1.0)

    ttk.Label(ctrl2, text='Wave speed').pack(side=tk.LEFT)
    ttk.Scale(ctrl2, from_=0.02, to=0.24, variable=wave_speed, orient=tk.HORIZONTAL, length=120).pack(side=tk.LEFT, padx=(4, 12))
    ttk.Label(ctrl2, text='Damping').pack(side=tk.LEFT)
    ttk.Scale(ctrl2, from_=0.95, to=0.9999, variable=damping, orient=tk.HORIZONTAL, length=120).pack(side=tk.LEFT, padx=(4, 12))
    ttk.Label(ctrl2, text='Source frequency').pack(side=tk.LEFT)
    ttk.Scale(ctrl2, from_=0.01, to=0.2, variable=src_freq, orient=tk.HORIZONTAL, length=120).pack(side=tk.LEFT, padx=(4, 12))
    ttk.Label(ctrl2, text='Source amplitude').pack(side=tk.LEFT)
    ttk.Scale(ctrl2, from_=0.2, to=3.0, variable=src_amp, orient=tk.HORIZONTAL, length=120).pack(side=tk.LEFT, padx=(4, 4))

    ctrl3 = ttk.Frame(win, padding=(10, 0, 10, 6))
    ctrl3.pack(fill=tk.X)

    canvas = tk.Canvas(win, width=CANVAS_W, height=CANVAS_H, highlightthickness=1, highlightbackground='#8a8f98', cursor='crosshair')
    canvas.pack(padx=10, pady=(0, 8))

    # --- Simulation state ---
    u_curr = np.zeros((NY + 2, NX + 2), dtype=np.float64)
    u_prev = np.zeros((NY + 2, NX + 2), dtype=np.float64)
    wall = np.zeros((NY + 2, NX + 2), dtype=bool)
    wall[0, :] = wall[-1, :] = wall[:, 0] = wall[:, -1] = True

    state = {'running': False, 'photo': None, 'frame': 0, 'source': None}

    def to_grid(event):
        ix = min(max(0, event.x // SCALE), NX - 1)
        iy = min(max(0, event.y // SCALE), NY - 1)
        return ix, iy

    def stamp_wall(ix, iy, value, radius=1):
        y0, y1 = max(0, iy - radius), min(NY - 1, iy + radius)
        x0, x1 = max(0, ix - radius), min(NX - 1, ix + radius)
        wall[y0 + 1:y1 + 2, x0 + 1:x1 + 2] = value
        if value:
            u_curr[y0 + 1:y1 + 2, x0 + 1:x1 + 2] = 0.0
            u_prev[y0 + 1:y1 + 2, x0 + 1:x1 + 2] = 0.0

    def stamp_circle(cx, cy, r, value):
        yy, xx = np.ogrid[0:NY, 0:NX]
        mask = (xx - cx) ** 2 + (yy - cy) ** 2 <= r * r
        wall[1:-1, 1:-1][mask] = value
        if value:
            u_curr[1:-1, 1:-1][mask] = 0.0
            u_prev[1:-1, 1:-1][mask] = 0.0

    def stamp_rect(x0, y0, x1, y1, value):
        xa, xb = sorted((max(0, min(x0, NX - 1)), max(0, min(x1, NX - 1))))
        ya, yb = sorted((max(0, min(y0, NY - 1)), max(0, min(y1, NY - 1))))
        wall[ya + 1:yb + 2, xa + 1:xb + 2] = value
        if value:
            u_curr[ya + 1:yb + 2, xa + 1:xb + 2] = 0.0
            u_prev[ya + 1:yb + 2, xa + 1:xb + 2] = 0.0

    def inject(ix, iy, amplitude=2.5, radius=2):
        y0, y1 = max(0, iy - radius), min(NY - 1, iy + radius)
        x0, x1 = max(0, ix - radius), min(NX - 1, ix + radius)
        yy, xx = np.mgrid[y0:y1 + 1, x0:x1 + 1]
        d2 = (xx - ix) ** 2 + (yy - iy) ** 2
        bump = amplitude * np.exp(-d2 / (2.0 * max(1, radius / 1.6) ** 2))
        region = u_curr[y0 + 1:y1 + 2, x0 + 1:x1 + 2]
        region_wall = wall[y0 + 1:y1 + 2, x0 + 1:x1 + 2]
        region[:] = np.where(region_wall, region, region + bump)

    def clear_water():
        u_curr[:] = 0.0
        u_prev[:] = 0.0

    def clear_obstacles():
        wall[:] = False
        wall[0, :] = wall[-1, :] = wall[:, 0] = wall[:, -1] = True
        state['source'] = None

    def preset_slit(num_gaps):
        clear_obstacles()
        mid = NY // 2
        stamp_wall_row = np.ones(NX, dtype=bool)
        gap_w = max(3, NX // 22)
        if num_gaps == 1:
            centers = [NX // 2]
        else:
            centers = [NX // 3, 2 * NX // 3]
        for c in centers:
            stamp_wall_row[max(0, c - gap_w):min(NX, c + gap_w)] = False
        wall[mid + 1, 1:-1] = stamp_wall_row
        wall[mid + 2, 1:-1] = stamp_wall_row
        u_curr[mid:mid + 3, :] = 0.0
        u_prev[mid:mid + 3, :] = 0.0

    # --- Mouse interaction ---
    drag = {'on': False, 'start': None, 'preview': None}

    def clear_preview():
        if drag['preview'] is not None:
            canvas.delete(drag['preview'])
            drag['preview'] = None

    def on_press(event):
        ix, iy = to_grid(event)
        t = tool.get()
        drag['on'] = True
        drag['start'] = (ix, iy)
        if t == 'wave':
            inject(ix, iy, amplitude=src_amp.get() * 2.5)
        elif t == 'wall':
            stamp_wall(ix, iy, True, radius=1)
        elif t == 'erase':
            stamp_wall(ix, iy, False, radius=2)
        elif t == 'source':
            state['source'] = (ix, iy)
            draw_static_overlay()

    def on_drag(event):
        if not drag['on']:
            return
        ix, iy = to_grid(event)
        t = tool.get()
        if t == 'wave':
            inject(ix, iy, amplitude=src_amp.get() * 2.5)
        elif t == 'wall':
            stamp_wall(ix, iy, True, radius=1)
        elif t == 'erase':
            stamp_wall(ix, iy, False, radius=2)
        elif t in ('circle', 'rect'):
            clear_preview()
            sx, sy = drag['start']
            if t == 'circle':
                r = math.hypot(ix - sx, iy - sy)
                drag['preview'] = canvas.create_oval((sx - r) * SCALE, (sy - r) * SCALE, (sx + r) * SCALE, (sy + r) * SCALE,
                                                       outline='#c1440e', width=2, dash=(4, 3), tags='preview')
            else:
                drag['preview'] = canvas.create_rectangle(sx * SCALE, sy * SCALE, ix * SCALE, iy * SCALE,
                                                            outline='#c1440e', width=2, dash=(4, 3), tags='preview')

    def on_release(event):
        if not drag['on']:
            return
        ix, iy = to_grid(event)
        t = tool.get()
        sx, sy = drag['start']
        if t == 'circle':
            r = math.hypot(ix - sx, iy - sy)
            stamp_circle(sx, sy, max(2, r), True)
        elif t == 'rect':
            stamp_rect(sx, sy, ix, iy, True)
        clear_preview()
        drag['on'] = False
        draw_static_overlay()

    def on_hover(event):
        cursors = {'wave': 'crosshair', 'wall': 'pencil', 'circle': 'circle', 'rect': 'tcross',
                   'source': 'target', 'erase': 'X_cursor'}
        canvas.config(cursor=cursors.get(tool.get(), 'crosshair'))

    canvas.bind('<ButtonPress-1>', on_press)
    canvas.bind('<B1-Motion>', on_drag)
    canvas.bind('<ButtonRelease-1>', on_release)
    canvas.bind('<Motion>', on_hover)

    def draw_static_overlay():
        canvas.delete('source_marker')
        if state['source'] is not None:
            sx, sy = state['source']
            px, py = sx * SCALE, sy * SCALE
            canvas.create_oval(px - 6, py - 6, px + 6, py + 6, outline='#f2d24b', width=2, tags='source_marker')

    # --- Physics + rendering ---
    def physics_step():
        c2 = wave_speed.get()
        interior = u_curr[1:-1, 1:-1]
        lap = (u_curr[:-2, 1:-1] + u_curr[2:, 1:-1] + u_curr[1:-1, :-2] + u_curr[1:-1, 2:] - 4 * interior)
        nxt_interior = (2 * interior - u_prev[1:-1, 1:-1] + c2 * lap) * damping.get()
        nxt = np.zeros_like(u_curr)
        nxt[1:-1, 1:-1] = nxt_interior
        nxt[wall] = 0.0
        return nxt

    def render():
        amp = np.clip(u_curr[1:-1, 1:-1] / 1.6, -1.0, 1.0)
        r = (30 + 70 * amp)
        g = (110 + 90 * amp)
        b = (195 + 60 * amp)
        rgb = np.stack([r, g, b], axis=-1)
        rgb[wall[1:-1, 1:-1]] = (138, 143, 152)
        rgb = np.clip(rgb, 0, 255).astype(np.uint8)
        img = Image.fromarray(rgb, mode='RGB').resize((CANVAS_W, CANVAS_H), Image.NEAREST)
        photo = ImageTk.PhotoImage(img)
        state['photo'] = photo  # keep a reference alive
        canvas.delete('wave_img')
        canvas.create_image(0, 0, anchor='nw', image=photo, tags='wave_img')
        canvas.tag_lower('wave_img')
        canvas.tag_raise('preview')
        canvas.tag_raise('source_marker')

    def update_live_readout():
        c2 = wave_speed.get()
        c_speed = math.sqrt(c2)  # grid cells per frame
        f = src_freq.get()
        wavelength = c_speed / f if f > 1e-9 else float('inf')
        lines = [
            f"Wave speed setting: c² = {c2:.3f}  (c ≈ {c_speed:.2f} cells/frame)",
            f"Source frequency: f = {f:.3f} cycles/frame",
            f"Wavelength: λ = c / f ≈ {wavelength:.1f} cells",
            f"Damping: {damping.get():.4f}",
            f"Frame: {state['frame']}",
            "",
            "Rule of thumb: diffraction is strongest when the gap width is",
            "close to λ, and weakest when the gap is much wider than λ.",
        ]
        update_live_tab(lines)

    def step():
        if not state['running']:
            return
        nonlocal_swap()
        if state['source'] is not None:
            sx, sy = state['source']
            phase = 2 * math.pi * src_freq.get() * state['frame']
            inject(sx, sy, amplitude=src_amp.get() * math.sin(phase) * 0.9, radius=1)
        render()
        state['frame'] += 1
        if state['frame'] % 6 == 0:
            update_live_readout()
        win.after(FRAME_MS, step)

    def nonlocal_swap():
        nonlocal u_curr, u_prev
        nxt = physics_step()
        u_prev[:] = u_curr
        u_curr[:] = nxt

    def start():
        if not state['running']:
            state['running'] = True
            step()

    def stop():
        state['running'] = False

    def reset():
        stop()
        clear_water()
        clear_obstacles()
        state['frame'] = 0
        render()
        update_live_readout()

    preset_row = ttk.Frame(win, padding=(10, 0, 10, 6))
    preset_row.pack(fill=tk.X)
    ttk.Button(preset_row, text='Single-slit preset', command=lambda: (preset_slit(1), render())).pack(side=tk.LEFT, padx=4)
    ttk.Button(preset_row, text='Double-slit preset', command=lambda: (preset_slit(2), render())).pack(side=tk.LEFT, padx=4)
    ttk.Button(preset_row, text='Clear obstacles', command=lambda: (clear_obstacles(), render())).pack(side=tk.LEFT, padx=4)
    ttk.Button(preset_row, text='Clear water', command=lambda: (clear_water(), render())).pack(side=tk.LEFT, padx=4)

    btn_row = ttk.Frame(win, padding=(10, 0, 10, 10))
    btn_row.pack(fill=tk.X)
    ttk.Button(btn_row, text='Reset', command=reset).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=4)
    ttk.Button(btn_row, text='Start', command=start).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=4)
    ttk.Button(btn_row, text='Stop', command=stop).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=4)

    reset()
    return win


def _open_equations_tabs(master, title):
    """Equations popup with real tabs (ttk.Notebook), as requested for Waves."""
    win = tk.Toplevel(master)
    win.title(f"{title} — Equations")
    master.update_idletasks()
    x = master.winfo_x() + master.winfo_width() + 14
    y = master.winfo_y()
    win.geometry(f"380x560+{x}+{y}")

    notebook = ttk.Notebook(win)
    notebook.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)

    def make_tab(name, lines):
        frame = ttk.Frame(notebook)
        notebook.add(frame, text=name)
        text = tk.Text(frame, wrap='word', font=('Courier', 10), bg='#f7f6f2', fg='black',
                        insertbackground='black', relief=tk.FLAT, padx=8, pady=8)
        text.pack(fill=tk.BOTH, expand=True)
        text.insert('1.0', "\n".join(lines))
        text.config(state='disabled')
        return text

    make_tab("Wave Basics", [
        "Wave speed, frequency, wavelength",
        "  v = f λ",
        "  (speed = frequency × wavelength)",
        "",
        "The 2D wave equation (what this simulation solves",
        "at every grid cell, every frame):",
        "  ∂²u/∂t² = c² ∇²u",
        "  = c² (∂²u/∂x² + ∂²u/∂y²)",
        "",
        "u(x,y,t) is the water height. c is the wave speed —",
        "the 'Wave speed' slider controls c² directly. Higher",
        "damping bleeds energy out of the tank over time, the",
        "same way real water waves lose energy to friction.",
    ])
    make_tab("Diffraction", [
        "Diffraction is the bending/spreading of a wave when",
        "it passes an edge or squeezes through a gap.",
        "",
        "Huygens' principle: every point on a wavefront acts",
        "as its own tiny source of circular wavelets. Far from",
        "an obstacle those wavelets combine into a straight",
        "wavefront — but right at an edge or a narrow gap,",
        "there's nothing to cancel the wavelets that curve",
        "sideways, so the wave visibly bends around corners.",
        "",
        "How much a wave diffracts depends on the ratio of",
        "wavelength (λ) to the opening's width (a):",
        "  a >> λ  →  barely bends; a sharp 'shadow' behind",
        "             the gap, like light through a doorway",
        "  a ≈ λ   →  bends strongly; fans out in an arc",
        "  a << λ  →  the gap acts almost like a fresh point",
        "             source, radiating in all directions",
        "",
        "Try the double-slit preset with a low source frequency",
        "(long wavelength) — the two fans overlap and interfere,",
        "the same phenomenon behind Young's double-slit experiment.",
    ])
    live_text = make_tab("Live Readout", ["(press Start to begin the simulation)"])

    def update_live(lines):
        live_text.config(state='normal')
        live_text.delete('1.0', tk.END)
        live_text.insert('1.0', "\n".join(lines))
        live_text.config(state='disabled')

    return win, update_live
