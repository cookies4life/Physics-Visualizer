"""Quantum mechanics visualizations: particle-in-a-box, measurement randomness,
an interpretations "comic book", and the double-slit wave-particle-duality demo."""

import math
import random
import tkinter as tk
from tkinter import ttk

import viz_common


# ---------------------------------------------------------------------------
# Small shared drawing helpers for the comic-book illustrations
# ---------------------------------------------------------------------------

def _draw_eye(canvas, cx, cy, w, iris_color='#3a56b0'):
    """Draw a simple eye icon (used to represent 'measurement'/observation)."""
    h = w * 0.55
    canvas.create_polygon(
        cx - w / 2, cy, cx - w / 4, cy - h / 2, cx + w / 4, cy - h / 2,
        cx + w / 2, cy, cx + w / 4, cy + h / 2, cx - w / 4, cy + h / 2,
        smooth=True, fill='white', outline='#222222', width=2)
    canvas.create_oval(cx - h / 4, cy - h / 4, cx + h / 4, cy + h / 4, fill=iris_color, outline='#1c2b57', width=1)
    canvas.create_oval(cx - h / 10, cy - h / 10, cx + h / 10, cy + h / 10, fill='#111111', outline='')


def _draw_wavy_line(canvas, x0, x1, y, amp, cycles, color='#7c4fd6', width=3, fade=False):
    n = 80
    pts = []
    for i in range(n + 1):
        t = i / n
        x = x0 + t * (x1 - x0)
        local_amp = amp * (1 - t) if fade else amp
        yy = y + local_amp * math.sin(2 * math.pi * cycles * t)
        pts.append((x, yy))
    canvas.create_line(*[c for p in pts for c in p], fill=color, width=width, smooth=True)


def _draw_gaussian_curve(canvas, cx, cy, sigma, height, color, half_width=80):
    n = 60
    pts = []
    for i in range(n + 1):
        x = cx - half_width + i * (2 * half_width / n)
        g = math.exp(-((x - cx) ** 2) / (2 * sigma * sigma))
        pts.append((x, cy - g * height))
    canvas.create_line(cx - half_width, cy, cx + half_width, cy, fill='#999999', width=1)
    canvas.create_line(*[c for p in pts for c in p], fill=color, width=3, smooth=True)


def _draw_barrier_with_slits(canvas, x, y_top, y_bottom, slit_centers, slit_w, color='#8a8f98'):
    cur = y_top
    for sc in sorted(slit_centers):
        if sc - slit_w / 2 > cur:
            canvas.create_rectangle(x - 5, cur, x + 5, sc - slit_w / 2, fill=color, outline='')
        cur = sc + slit_w / 2
    if y_bottom > cur:
        canvas.create_rectangle(x - 5, cur, x + 5, y_bottom, fill=color, outline='')


# ---------------------------------------------------------------------------
# Generic paginated "comic book" viewer, reused by both comics below
# ---------------------------------------------------------------------------

def _open_comic_book(master, win_title, pages):
    """Open a small paginated comic-book window.

    `pages` is a list of (page_title, draw_fn, caption) tuples, where
    draw_fn(canvas, cx, cy) draws that page's illustration.
    """
    win = tk.Toplevel(master) if master else tk.Tk()
    win.title(win_title)
    win.geometry("520x640")
    win.resizable(False, False)

    state = {'page': 0}

    tk.Label(win, text=win_title, font=(None, 15, 'bold'), fg='black', pady=8).pack(fill=tk.X)

    panel = tk.Frame(win, bg='#fffbe8', highlightbackground='#2b2b2b', highlightthickness=3, bd=0)
    panel.pack(fill=tk.BOTH, expand=True, padx=16, pady=(0, 8))

    page_title_lbl = tk.Label(panel, text='', font=(None, 13, 'bold'), bg='#fffbe8', fg='black', pady=8)
    page_title_lbl.pack(fill=tk.X)

    canvas = tk.Canvas(panel, bg='#fffbe8', width=460, height=320, highlightthickness=0)
    canvas.pack(padx=10)

    caption = tk.Label(panel, text='', font=(None, 11), bg='#fff6c6', fg='black', wraplength=430, justify='left', padx=12, pady=10, relief=tk.RIDGE, bd=2)
    caption.pack(fill=tk.X, padx=10, pady=(10, 12))

    nav = ttk.Frame(win)
    nav.pack(fill=tk.X, pady=(0, 12), padx=16)
    page_lbl = ttk.Label(nav, text='')
    page_lbl.pack(side=tk.LEFT)

    def show_page():
        i = state['page']
        title, draw_fn, cap_text = pages[i]
        canvas.delete('all')
        page_title_lbl.config(text=title)
        caption.config(text=cap_text)
        draw_fn(canvas, 230, 150)
        page_lbl.config(text=f"Page {i + 1} of {len(pages)}")
        prev_btn.config(state='normal' if i > 0 else 'disabled')
        next_btn.config(state='normal' if i < len(pages) - 1 else 'disabled')

    def go_prev():
        if state['page'] > 0:
            state['page'] -= 1
            show_page()

    def go_next():
        if state['page'] < len(pages) - 1:
            state['page'] += 1
            show_page()

    prev_btn = ttk.Button(nav, text='< Previous', command=go_prev)
    prev_btn.pack(side=tk.LEFT, padx=(20, 4))
    next_btn = ttk.Button(nav, text='Next >', command=go_next)
    next_btn.pack(side=tk.LEFT, padx=4)
    ttk.Button(nav, text='Close', command=win.destroy).pack(side=tk.RIGHT)

    show_page()
    return win


# ---------------------------------------------------------------------------
# "Interpretations of quantum mechanics" comic book
# ---------------------------------------------------------------------------

def _page_intro(canvas, cx, cy):
    canvas.create_text(cx, cy - 60, text="ψ", font=('Times', 60, 'italic'))
    canvas.create_text(cx, cy + 20, text="?   ?   ?", font=(None, 28, 'bold'), fill='#7c4fd6')
    viz_common.draw_atom_icon(canvas, cx, cy + 100, 50)


def _page_copenhagen(canvas, cx, cy):
    _draw_wavy_line(canvas, cx - 170, cx - 20, cy, 28, 3.5)
    canvas.create_text(cx - 95, cy - 55, text="probability wave", font=(None, 9), fill='#5a5a5a')
    _draw_eye(canvas, cx + 60, cy, 70)
    canvas.create_oval(cx + 128, cy - 8, cx + 144, cy + 8, fill='#d9740c', outline='#7a3d00', width=2)
    canvas.create_text(cx + 136, cy + 30, text="collapse!", font=(None, 10, 'bold'), fill='#d9740c')


def _page_many_worlds(canvas, cx, cy):
    start_x, branch_x = cx - 170, cx - 40
    canvas.create_line(start_x, cy, branch_x, cy, fill='#333333', width=3)
    ends = [(cy - 70, '#1d4fd8'), (cy - 25, '#1f8a3b'), (cy + 25, '#d9740c'), (cy + 70, '#c1440e')]
    for ey, col in ends:
        canvas.create_line(branch_x, cy, cx + 150, ey, fill=col, width=3)
        canvas.create_oval(cx + 150 - 7, ey - 7, cx + 150 + 7, ey + 7, fill=col, outline='')
    canvas.create_text(branch_x, cy - 95, text="measurement", font=(None, 9), fill='#5a5a5a')


def _page_pilot_wave(canvas, cx, cy):
    _draw_wavy_line(canvas, cx - 170, cx + 170, cy - 35, 22, 3, color='#9fb8ff', width=2)
    n = 80
    pts = []
    for i in range(n + 1):
        t = i / n
        x = cx - 170 + t * 340
        y = cy + 30 + 12 * math.sin(2 * math.pi * 3 * t + 0.6)
        pts.append((x, y))
    canvas.create_line(*[c for p in pts for c in p], fill='#333333', width=2, smooth=True, dash=(4, 2))
    ex, ey = pts[-1]
    canvas.create_oval(ex - 7, ey - 7, ex + 7, ey + 7, fill='#d9740c', outline='#7a3d00', width=2)
    canvas.create_text(cx, cy - 75, text="a real wave guides a real particle", font=(None, 9), fill='#5a5a5a')


def _page_objective_collapse(canvas, cx, cy):
    _draw_gaussian_curve(canvas, cx - 110, cy, 60, 60, '#1d4fd8')
    canvas.create_text(cx - 110, cy + 80, text="spread out", font=(None, 9))
    canvas.create_line(cx - 45, cy - 20, cx + 45, cy - 20, arrow='last', fill='#333333', width=2)
    canvas.create_text(cx, cy - 35, text="spontaneous!", font=(None, 9, 'bold'), fill='#c1440e')
    _draw_gaussian_curve(canvas, cx + 110, cy, 12, 60, '#c1440e')
    canvas.create_text(cx + 110, cy + 80, text="randomly localizes", font=(None, 9))


def _page_closing(canvas, cx, cy):
    viz_common.draw_atom_icon(canvas, cx, cy - 30, 55)
    canvas.create_text(cx, cy + 70, text="All of these interpretations predict\nthe exact same experimental results.", font=(None, 11), justify='center')
    canvas.create_text(cx, cy + 115, text="Nobody has ever measured which one is ‘true’.", font=(None, 10, 'italic'), fill='#5a5a5a')


_INTERPRETATION_PAGES = [
    ("What does it all mean?", _page_intro,
     "Quantum mechanics predicts probabilities perfectly, but physicists still argue about WHY measurement outcomes are random and what's really happening underneath. Here are the leading interpretations."),
    ("Copenhagen Interpretation", _page_copenhagen,
     "The wavefunction only describes probabilities. Before measurement there's no definite value — measuring it causes a random 'collapse' to one outcome. Chance is fundamental, not just our ignorance. (Bohr & Heisenberg, 1920s)"),
    ("Many-Worlds Interpretation", _page_many_worlds,
     "Nothing ever collapses. Every possible outcome actually happens, each in its own branching universe. What feels like random luck is really just which branch you find yourself in. (Hugh Everett, 1957)"),
    ("Pilot-Wave Theory", _page_pilot_wave,
     "Particles are always real and have a definite position, silently guided by a real physical wave. Randomness only reflects our ignorance of the exact starting conditions. (de Broglie & Bohm)"),
    ("Objective Collapse", _page_objective_collapse,
     "Wavefunctions spontaneously and randomly collapse on their own, all the time — and collapse gets dramatically more likely the more particles are involved. That's why big objects look definite without anyone 'looking'. (Ghirardi-Rimini-Weber)"),
    ("So... which one is right?", _page_closing,
     "All of these interpretations make the exact same testable predictions, so no ordinary experiment can tell them apart. It remains one of the biggest open questions in physics."),
]


def open_interpretations_comic(master=None):
    """Open the comic book explaining interpretations of quantum mechanics."""
    return _open_comic_book(master, "Interpretations of Quantum Mechanics", _INTERPRETATION_PAGES)


# ---------------------------------------------------------------------------
# Double-slit wave-particle-duality comic strip
# ---------------------------------------------------------------------------

def _page_ds_title(canvas, cx, cy):
    _draw_wavy_line(canvas, cx - 170, cx - 20, cy, 22, 2.5)
    _draw_barrier_with_slits(canvas, cx - 10, cy - 100, cy + 100, [cy - 20, cy + 20], 18)
    canvas.create_line(cx + 30, cy - 90, cx + 30, cy + 90, fill='#333333', width=3)


def _page_ds_unobserved(canvas, cx, cy):
    _draw_barrier_with_slits(canvas, cx - 40, cy - 110, cy + 110, [cy - 20, cy + 20], 16)
    _draw_wavy_line(canvas, cx - 170, cx - 44, cy, 18, 2.5)
    rng = random.Random(42)
    screen_x = cx + 140
    for _ in range(260):
        y = rng.gauss(0, 55)
        weight = (math.cos(y * 0.09) ** 2) * math.exp(-(y * y) / (2 * 70 * 70))
        if rng.random() < weight:
            x = screen_x + rng.uniform(-3, 3)
            canvas.create_oval(x - 1.5, cy + y - 1.5, x + 1.5, cy + y + 1.5, fill='#1d4fd8', outline='')
    canvas.create_line(screen_x, cy - 110, screen_x, cy + 110, fill='#333333', width=3)


def _page_ds_observed(canvas, cx, cy):
    _draw_barrier_with_slits(canvas, cx - 40, cy - 110, cy + 110, [cy - 20, cy + 20], 16)
    _draw_eye(canvas, cx - 40, cy - 140, 40)
    canvas.create_oval(cx - 62, cy - 42, cx - 18, cy + 2, outline='#d9740c', width=2)
    canvas.create_oval(cx - 62, cy - 2, cx - 18, cy + 42, outline='#d9740c', width=2)
    rng = random.Random(7)
    screen_x = cx + 140
    for _ in range(220):
        center = rng.choice([-20, 20])
        y = rng.gauss(center, 18)
        x = screen_x + rng.uniform(-3, 3)
        canvas.create_oval(x - 1.5, cy + y - 1.5, x + 1.5, cy + y + 1.5, fill='#c1440e', outline='')
    canvas.create_line(screen_x, cy - 110, screen_x, cy + 110, fill='#333333', width=3)


def _page_ds_closing(canvas, cx, cy):
    canvas.create_text(cx, cy - 50, text="Measuring WHICH slit a particle used\ndestroys the wave interference.", font=(None, 12, 'bold'), justify='center')
    canvas.create_text(cx, cy + 25, text="The particles' behavior depends on\nwhether anyone is watching —\none of the deepest mysteries in physics.", font=(None, 11), justify='center', fill='#5a5a5a')
    viz_common.draw_atom_icon(canvas, cx, cy + 105, 40)


_DOUBLE_SLIT_COMIC_PAGES = [
    ("Young's Double-Slit Experiment", _page_ds_title,
     "Fire particles of light (or even electrons!) one at a time through two narrow slits toward a screen. What pattern builds up over time?"),
    ("Nobody's watching...", _page_ds_unobserved,
     "If nothing detects which slit each particle passes through, the particles behave like WAVES — passing through both slits at once and interfering with themselves. Striped interference fringes build up on the screen."),
    ("Now we're watching!", _page_ds_observed,
     "Add a detector at each slit to see which one the particle really used. Now particles behave like ordinary PARTICLES — going through exactly one slit. The interference fringes vanish, leaving just two simple clumps."),
    ("The mystery", _page_ds_closing,
     "The act of measurement itself changes the outcome. This isn't a flaw in the experiment — it's a genuine, deep feature of how quantum mechanics works."),
]


def open_double_slit_comic(master=None):
    """Open the comic strip explaining the double-slit observer effect."""
    return _open_comic_book(master, "Wave-Particle Duality Explained", _DOUBLE_SLIT_COMIC_PAGES)


# ---------------------------------------------------------------------------
# Particle-in-a-box: wavefunction plot + measurement-randomness demo
# ---------------------------------------------------------------------------

def _prob_density(nval, x, Lval):
    """|psi(x)|^2 for a stationary energy eigenstate — time-independent, since
    a stationary state's time dependence is a pure complex phase exp(-iEt/hbar)
    that vanishes when you take the modulus squared."""
    spatial = math.sqrt(2.0 / Lval) * math.sin(nval * math.pi * x / Lval)
    return spatial * spatial


def _sample_position(nval, Lval):
    """Randomly sample a measured position, following the Born rule |psi(x)|^2."""
    max_density = 2.0 / Lval
    for _ in range(200):
        x = random.uniform(0, Lval)
        if random.uniform(0, max_density) <= _prob_density(nval, x, Lval):
            return x
    return Lval / 2.0


def open_quantum_window(master=None):
    """Create the quantum wavefunction visualization window."""
    win = tk.Toplevel(master) if master else tk.Tk()
    win.title("Quantum Mechanics — Particle in a Box (1D)")
    win.geometry("1000x620")

    def _maximize_or_fullscreen_max(win_obj: tk.Toplevel):
        """Best-effort maximize for cross-platform Tk."""
        try:
            win_obj.state('zoomed')
        except Exception:
            pass

    win.after(100, lambda: _maximize_or_fullscreen_max(win))

    header = ttk.Frame(win)
    header.pack(fill=tk.X)
    ttk.Label(header, text="Quantum Mechanics — Particle in a Box (1D)", font=(None, 16, 'bold')).pack(anchor='n')
    ttk.Label(
        header,
        text="The purple curve is the real part of the wavefunction (it oscillates in time). The green curve is the "
             "probability density |ψ(x)|², which stays fixed for a stationary state. Click 'Measure' to see the "
             "genuine randomness of where a real measurement would actually find the particle.",
        wraplength=960,
    ).pack(anchor='n')

    frm = ttk.Frame(win, padding=8)
    frm.pack(fill=tk.BOTH, expand=True)

    n = tk.IntVar(value=1)
    L = tk.DoubleVar(value=1.0)

    canvas = tk.Canvas(frm, bg='white', height=340, highlightthickness=0)
    canvas.pack(fill=tk.BOTH, expand=True)

    ctrl = ttk.Frame(frm)
    ctrl.pack(fill=tk.X, pady=(6, 0))
    ttk.Label(ctrl, text='Quantum number n').pack(side=tk.LEFT)
    ttk.Scale(ctrl, from_=1, to=10, variable=n, orient=tk.HORIZONTAL).pack(side=tk.LEFT, fill=tk.X, expand=True)
    ttk.Label(ctrl, text='Box length L (m)').pack(side=tk.LEFT, padx=(10, 0))
    ttk.Scale(ctrl, from_=0.2, to=5.0, variable=L, orient=tk.HORIZONTAL).pack(side=tk.LEFT)

    # animation / measurement state
    state = {'t': 0.0, 'playing': True}
    measurements = []

    def draw():
        """Draw the wavefunction, probability density, and measurement histogram."""
        canvas.delete('all')
        Lval = L.get(); nval = n.get()
        w = int(canvas.winfo_width() or 800)
        h = int(canvas.winfo_height() or 340)
        # Scale each curve to the canvas using the theoretical peak for the
        # current L (spatial amplitude maxes out at sqrt(2/L), so the peak
        # prob density is 2/L) — a fixed scale factor would push the curve
        # off-canvas for small L, since amplitude grows as L shrinks.
        max_amplitude = math.sqrt(2.0 / Lval)
        real_scale = (h * 0.22) / max(1e-6, max_amplitude)
        prob_scale = (h * 0.55) / max(1e-6, max_amplitude * max_amplitude)

        points_real = []
        points_prob = []
        for i in range(0, w):
            x = (i / w) * Lval
            spatial = max_amplitude * math.sin(nval * math.pi * x / Lval)
            real_val = spatial * math.cos((nval ** 2) * state['t'])
            prob = spatial * spatial
            points_real.append((i, h / 2 - real_val * real_scale))
            points_prob.append((i, h - prob * prob_scale))

        for i in range(1, len(points_real)):
            canvas.create_line(*points_real[i - 1], *points_real[i], fill='purple')
        for i in range(1, len(points_prob)):
            canvas.create_line(*points_prob[i - 1], *points_prob[i], fill='green', width=2)

        # Measurement histogram: each past measurement stacks a small dot above
        # the axis at its measured x — the pile-up should trace out |psi(x)|^2.
        bucket_h = 5
        counts = {}
        for x in measurements:
            xi = int((x / Lval) * w)
            counts[xi] = counts.get(xi, 0) + 1
            stacked = counts[xi]
            cy = h - 6 - (stacked - 1) * bucket_h
            canvas.create_oval(xi - 3, cy - 3, xi + 3, cy + 3, fill='#d9740c', outline='#7a3d00')

        viz_common.draw_legend(canvas, [('Re(ψ) — oscillates in time', 'purple'), ('|ψ|² — fixed probability density', 'green'), ('measured positions', '#d9740c')], w)
        viz_common.draw_readout(canvas, f"n={nval}  L={Lval:.2f} m  t={state['t']:.2f}  measurements={len(measurements)}")

    def animate():
        if not win.winfo_exists():
            return
        if state['playing']:
            state['t'] += 0.05
            draw()
        win.after(50, animate)

    def toggle_play():
        state['playing'] = not state['playing']
        play_btn.config(text='Pause' if state['playing'] else 'Resume')

    def measure_once():
        measurements.append(_sample_position(n.get(), L.get()))
        draw()

    def measure_many():
        for _ in range(100):
            measurements.append(_sample_position(n.get(), L.get()))
        draw()

    def clear_measurements():
        measurements.clear()
        draw()

    for var in (n, L):
        var.trace_add("write", lambda *_: clear_measurements())

    meas_row = ttk.Frame(frm)
    meas_row.pack(fill=tk.X, pady=(6, 0))
    ttk.Label(meas_row, text="Randomness of measurement (Born rule):").pack(side=tk.LEFT)
    play_btn = ttk.Button(meas_row, text='Pause', command=toggle_play)
    play_btn.pack(side=tk.LEFT, padx=(16, 4))
    ttk.Button(meas_row, text='Measure once', command=measure_once).pack(side=tk.LEFT, padx=4)
    ttk.Button(meas_row, text='Measure x100', command=measure_many).pack(side=tk.LEFT, padx=4)
    ttk.Button(meas_row, text='Clear measurements', command=clear_measurements).pack(side=tk.LEFT, padx=4)

    modes_row = ttk.Frame(frm)
    modes_row.pack(fill=tk.X, pady=(10, 0))
    ttk.Button(modes_row, text='Open interpretations comic book', command=lambda: open_interpretations_comic(win)).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 4))
    ttk.Button(modes_row, text="Open double-slit experiment (wave-particle duality)", command=lambda: open_double_slit_window(win)).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=4)

    animate()
    return win


# ---------------------------------------------------------------------------
# Double-slit experiment: observer effect on wave-particle duality
# ---------------------------------------------------------------------------

def _screen_intensity(y, y_range, detectors_on, fringe_k):
    envelope_sigma = y_range * 0.55
    envelope = math.exp(-(y * y) / (2 * envelope_sigma * envelope_sigma))
    if detectors_on:
        # Two well-separated blobs (one per slit) — the separation needs to be
        # several times the blob width, or the two Gaussians just blend into
        # one hump instead of showing as two distinguishable clumps.
        center = y_range * 0.42
        blob_sigma = y_range * 0.14
        return (math.exp(-((y - center) ** 2) / (2 * blob_sigma * blob_sigma))
                + math.exp(-((y + center) ** 2) / (2 * blob_sigma * blob_sigma)))
    return (math.cos(fringe_k * y) ** 2) * envelope * 2.0


def open_double_slit_window(master=None):
    """Create the Young's double-slit wave-particle-duality demo window."""
    win = tk.Toplevel(master) if master else tk.Tk()
    win.title("Wave-Particle Duality — Young's Double-Slit Experiment")
    win.geometry("1040x680")

    def _maximize_or_fullscreen_max(win_obj: tk.Toplevel):
        try:
            win_obj.state('zoomed')
        except Exception:
            pass
    win.after(100, lambda: _maximize_or_fullscreen_max(win))

    header = ttk.Frame(win)
    header.pack(fill=tk.X)
    ttk.Label(header, text="Young's Double-Slit Experiment", font=(None, 16, 'bold')).pack(anchor='n')
    ttk.Label(
        header,
        text="Particles are fired one at a time through two slits toward a screen. With no detectors, each particle "
             "behaves like a wave passing through both slits, and an interference (diffraction) pattern slowly builds "
             "up. Turn on the detectors to measure which slit each particle really used — the interference pattern "
             "disappears, leaving just two simple clumps.",
        wraplength=1000,
    ).pack(anchor='n')

    frm = ttk.Frame(win, padding=8)
    frm.pack(fill=tk.BOTH, expand=True)

    detectors_on = tk.BooleanVar(value=False)
    rate = tk.IntVar(value=8)

    ctrl = ttk.Frame(frm)
    ctrl.pack(fill=tk.X)
    ttk.Checkbutton(ctrl, text='Detectors at slits (measure which path)', variable=detectors_on).pack(side=tk.LEFT)
    ttk.Label(ctrl, text='Emission rate').pack(side=tk.LEFT, padx=(20, 4))
    ttk.Scale(ctrl, from_=1, to=20, variable=rate, orient=tk.HORIZONTAL, length=160).pack(side=tk.LEFT)

    canvas = tk.Canvas(frm, bg='#0c0c14', height=460, highlightthickness=0)
    canvas.pack(fill=tk.BOTH, expand=True, pady=8)

    geom = {}
    running = {'on': False}
    tick_state = {'count': 0}
    particles = []
    hit_count = {'n': 0}
    dist_cache = {'ys': None, 'cdf': None, 'key': None}

    def ensure_distribution(h):
        key = (detectors_on.get(), h)
        if dist_cache['key'] == key:
            return
        y_range = h * 0.42
        bins = 400
        fringe_k = 0.09
        ys = [-y_range + 2 * y_range * i / (bins - 1) for i in range(bins)]
        weights = [max(0.0, _screen_intensity(y, y_range, detectors_on.get(), fringe_k)) for y in ys]
        total = sum(weights) or 1.0
        cdf = []
        acc = 0.0
        for wgt in weights:
            acc += wgt
            cdf.append(acc / total)
        dist_cache.update(ys=ys, cdf=cdf, key=key)

    def sample_y(h):
        ensure_distribution(h)
        r = random.random()
        ys, cdf = dist_cache['ys'], dist_cache['cdf']
        lo, hi = 0, len(cdf) - 1
        while lo < hi:
            mid = (lo + hi) // 2
            if cdf[mid] < r:
                lo = mid + 1
            else:
                hi = mid
        return ys[lo]

    def draw_static_scene():
        canvas.delete('static')
        w = max(200, canvas.winfo_width() or 1000)
        h = max(160, canvas.winfo_height() or 460)
        cy = h / 2
        x_source = w * 0.06
        x_barrier = w * 0.32
        x_screen = w * 0.88
        slit_gap = min(60, h * 0.12)
        slit_w = 16
        s1, s2 = cy - slit_gap / 2, cy + slit_gap / 2
        geom.update(w=w, h=h, cy=cy, x_source=x_source, x_barrier=x_barrier, x_screen=x_screen, s1=s1, s2=s2)

        canvas.create_rectangle(0, 0, w, h, fill='#0c0c14', outline='', tags='static')
        canvas.create_oval(x_source - 10, cy - 10, x_source + 10, cy + 10, fill='#f2d24b', outline='', tags='static')
        canvas.create_text(x_source, cy - 26, text='source', fill='#cccccc', font=('Arial', 9), tags='static')

        _draw_barrier_with_slits(canvas, x_barrier, 20, h - 20, [s1, s2], slit_w, color='#8a8f98')

        if detectors_on.get():
            for sy in (s1, s2):
                canvas.create_oval(x_barrier - 18, sy - 18, x_barrier + 18, sy + 18, outline='#d9740c', width=2, tags='static')
            _draw_eye(canvas, x_barrier, 40, 34)
            canvas.create_text(x_barrier, 62, text='detectors ON — which-path known', fill='#d9740c', font=('Arial', 10, 'bold'), tags='static')
        else:
            canvas.create_text(x_barrier, 40, text='no detectors — wave-like', fill='#4c9aff', font=('Arial', 10, 'bold'), tags='static')

        canvas.create_line(x_screen, 20, x_screen, h - 20, fill='#e5e5e5', width=3, tags='static')
        canvas.create_text(x_screen, h - 8, text='screen', fill='#cccccc', font=('Arial', 9), tags='static')

    def draw_counter():
        canvas.delete('counter')
        w = geom.get('w', 1000)
        canvas.create_text(w - 20, 20, anchor='ne', text=f"{hit_count['n']} particles detected", fill='#e5e5e5', font=('Arial', 10, 'bold'), tags='counter')

    def emit_particle():
        w, h, cy = geom['w'], geom['h'], geom['cy']
        x_source, x_barrier, x_screen = geom['x_source'], geom['x_barrier'], geom['x_screen']
        s1, s2 = geom['s1'], geom['s2']
        target_y = sample_y(h)
        if detectors_on.get():
            slit_y = random.choice([s1, s2])
            path = [(x_source, cy), (x_barrier, slit_y), (x_screen, cy + target_y)]
            color = '#ff8a3d'
        else:
            mid_y = (s1 + s2) / 2
            path = [(x_source, cy), (x_barrier, mid_y), (x_screen, cy + target_y)]
            color = '#4c9aff'
        pid = canvas.create_oval(-10, -10, -6, -6, fill=color, outline='', tags='particle')
        particles.append({'id': pid, 'path': path, 'seg': 0, 'frac': 0.0, 'color': color})

    def step_particles():
        speed = 0.09
        done = []
        for p in particles:
            p['frac'] += speed
            if p['frac'] >= 1.0:
                p['frac'] = 0.0
                p['seg'] += 1
                if p['seg'] >= len(p['path']) - 1:
                    lx, ly = p['path'][-1]
                    jitter = random.uniform(-2, 2)
                    canvas.create_oval(lx - 2 + jitter, ly - 2, lx + 2 + jitter, ly + 2, fill=p['color'], outline='', tags='hit')
                    canvas.delete(p['id'])
                    hit_count['n'] += 1
                    done.append(p)
                    continue
            x0, y0 = p['path'][p['seg']]
            x1, y1 = p['path'][p['seg'] + 1]
            x = x0 + (x1 - x0) * p['frac']
            y = y0 + (y1 - y0) * p['frac']
            canvas.coords(p['id'], x - 4, y - 4, x + 4, y + 4)
        for p in done:
            particles.remove(p)
        draw_counter()

    def tick():
        if not win.winfo_exists() or not running['on']:
            return
        tick_state['count'] += 1
        if tick_state['count'] % max(1, 21 - rate.get()) == 0:
            emit_particle()
        step_particles()
        win.after(30, tick)

    def start():
        if not running['on']:
            running['on'] = True
            tick()

    def stop():
        running['on'] = False

    def reset():
        running['on'] = False
        particles.clear()
        hit_count['n'] = 0
        dist_cache['key'] = None
        canvas.delete('hit')
        canvas.delete('particle')
        draw_static_scene()
        draw_counter()

    detectors_on.trace_add('write', lambda *_: reset())
    # Redraw the static scene on resize (e.g. the auto-maximize shortly after
    # opening) without touching `running` or clearing accumulated hits — a
    # full reset() here would silently stop an in-progress simulation the
    # instant the window finished maximizing.
    canvas.bind('<Configure>', lambda _e: draw_static_scene())

    btn_row = ttk.Frame(frm)
    btn_row.pack(fill=tk.X, pady=(0, 4))
    ttk.Button(btn_row, text='Start', command=start).pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=4)
    ttk.Button(btn_row, text='Stop', command=stop).pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=4)
    ttk.Button(btn_row, text='Reset', command=reset).pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=4)
    ttk.Button(btn_row, text='Explain this! (comic strip)', command=lambda: open_double_slit_comic(win)).pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=4)

    reset()
    return win
