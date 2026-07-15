"""Animated 1D collision demo showing momentum conservation, with cars on a road."""

import math
import tkinter as tk
from tkinter import ttk

import viz_common

FRAME_MS = 20
FRAME_DT = FRAME_MS / 1000.0
PX_PER_MPS = 10.0  # how many pixels of motion one (m/s) of velocity covers per second


def open_momentum_window(master=None):
    """Create the collision simulator window with controls and animated cars."""
    win = tk.Toplevel(master) if master else tk.Tk()
    win.title("Momentum & Collisions — Animated 1D Collision")

    def _maximize_or_fullscreen_max(win_obj: tk.Toplevel):
        """Best-effort maximize for cross-platform Tk (maximized window).

        Uses 'zoomed' when available. Avoid fullscreen toggle to prevent a
        visible flash.
        """
        try:
            win_obj.state('zoomed')
        except Exception:
            pass

    # Start as maximized.
    win.after(100, lambda: _maximize_or_fullscreen_max(win))

    # Header and description
    header = ttk.Frame(win)
    header.pack(fill=tk.X)
    ttk.Label(header, text="Momentum & Collisions — 1D Collision", font=(None, 16, 'bold')).pack(anchor='n')
    ttk.Label(
        header,
        text="Two cars collide on a road. Momentum is always conserved; kinetic energy is conserved only for elastic collisions. Drag a car with your cursor to reposition it.",
        wraplength=980,
    ).pack(anchor='n')

    frm = ttk.Frame(win, padding=8)
    frm.pack(fill=tk.BOTH, expand=True)

    m1 = tk.DoubleVar(value=2.0)
    v1 = tk.DoubleVar(value=10.0)
    m2 = tk.DoubleVar(value=1.0)
    v2 = tk.DoubleVar(value=-2.0)

    # Collision mode:
    # - elastic: momentum + kinetic energy conserved (coefficient of restitution e=1).
    # - inelastic: momentum conserved, cars stick together (e=0).
    # - partial: "somewhat elastic" — momentum conserved, some kinetic energy lost (0<e<1).
    collision_mode = tk.StringVar(value='elastic')
    restitution_e = tk.DoubleVar(value=0.5)

    friction_on = tk.BooleanVar(value=False)
    friction_mu = tk.DoubleVar(value=0.10)

    def _bind_display(var, display_var):
        def _update(*_args):
            display_var.set(f"{var.get():.2f}")

        var.trace_add("write", _update)
        _update()

    m1_display = tk.StringVar()
    v1_display = tk.StringVar()
    m2_display = tk.StringVar()
    v2_display = tk.StringVar()
    e_display = tk.StringVar()
    mu_display = tk.StringVar()
    _bind_display(m1, m1_display)
    _bind_display(v1, v1_display)
    _bind_display(m2, m2_display)
    _bind_display(v2, v2_display)
    _bind_display(restitution_e, e_display)
    _bind_display(friction_mu, mu_display)

    control = ttk.Frame(frm)
    control.pack(fill=tk.X)

    ttk.Label(control, text='m1').pack(side=tk.LEFT)
    ttk.Scale(control, from_=0.1, to=20, variable=m1, orient=tk.HORIZONTAL).pack(side=tk.LEFT, fill=tk.X, expand=True)
    ttk.Label(control, textvariable=m1_display).pack(side=tk.LEFT, padx=6)
    ttk.Label(control, text='v1').pack(side=tk.LEFT)
    ttk.Scale(control, from_=-50, to=50, variable=v1, orient=tk.HORIZONTAL).pack(side=tk.LEFT, fill=tk.X, expand=True)
    ttk.Label(control, textvariable=v1_display).pack(side=tk.LEFT, padx=6)
    ttk.Label(control, text='m2').pack(side=tk.LEFT)
    ttk.Scale(control, from_=0.1, to=20, variable=m2, orient=tk.HORIZONTAL).pack(side=tk.LEFT, fill=tk.X, expand=True)
    ttk.Label(control, textvariable=m2_display).pack(side=tk.LEFT, padx=6)
    ttk.Label(control, text='v2').pack(side=tk.LEFT)
    ttk.Scale(control, from_=-50, to=50, variable=v2, orient=tk.HORIZONTAL).pack(side=tk.LEFT, fill=tk.X, expand=True)
    ttk.Label(control, textvariable=v2_display).pack(side=tk.LEFT, padx=6)

    mode_row = ttk.Frame(frm)
    mode_row.pack(fill=tk.X, pady=(4, 0))
    ttk.Label(mode_row, text="Collision mode:").pack(side=tk.LEFT, padx=(0, 6))
    ttk.Radiobutton(mode_row, text='Elastic', variable=collision_mode, value='elastic').pack(side=tk.LEFT, padx=4)
    ttk.Radiobutton(mode_row, text='Totally inelastic', variable=collision_mode, value='inelastic').pack(side=tk.LEFT, padx=4)
    ttk.Radiobutton(mode_row, text='Somewhat elastic', variable=collision_mode, value='partial').pack(side=tk.LEFT, padx=4)
    ttk.Label(mode_row, text='restitution e').pack(side=tk.LEFT, padx=(16, 0))
    ttk.Scale(mode_row, from_=0.0, to=1.0, variable=restitution_e, orient=tk.HORIZONTAL, length=140).pack(side=tk.LEFT, padx=4)
    ttk.Label(mode_row, textvariable=e_display).pack(side=tk.LEFT, padx=4)

    friction_row = ttk.Frame(frm)
    friction_row.pack(fill=tk.X, pady=(4, 0))
    ttk.Checkbutton(friction_row, text='Road friction', variable=friction_on).pack(side=tk.LEFT)
    ttk.Label(friction_row, text='μ').pack(side=tk.LEFT, padx=(10, 0))
    ttk.Scale(friction_row, from_=0.0, to=1.0, variable=friction_mu, orient=tk.HORIZONTAL, length=160).pack(side=tk.LEFT, padx=4)
    ttk.Label(friction_row, textvariable=mu_display).pack(side=tk.LEFT, padx=4)

    canvas = tk.Canvas(frm, bg='#eaf6ff', height=240, highlightthickness=0)
    canvas.pack(fill=tk.BOTH, expand=True, pady=8)

    _MOMENTUM_LEGEND = [('Car 1 velocity', '#1d4fd8'), ('Car 2 velocity', '#c1440e')]

    # --- Small companion window showing the equations being demonstrated ---
    EQ_W, EQ_H = 360, 480
    eq_win, update_equations_text = viz_common.create_equations_panel(win, "Momentum & Collisions", width=EQ_W, height=EQ_H)
    win.protocol("WM_DELETE_WINDOW", lambda: (eq_win.destroy(), win.destroy()))

    def _reposition_eq_panel():
        sw = win.winfo_screenwidth()
        eq_win.geometry(f"{EQ_W}x{EQ_H}+{sw - EQ_W - 20}+40")
    win.after(150, _reposition_eq_panel)

    # positions in pixels (recomputed in reset based on current canvas width)
    state = {
        'x1': 0.0,
        'x2': 0.0,
        'v1': v1.get(),
        'v2': v2.get(),
        'running': False,
    }
    drag = {'car': None, 'offset': 0.0}

    def box_size(mass_value: float) -> tuple[float, float]:
        """Return the width and height of a car based on its mass.

        Larger masses become visually larger so the animation is easier to follow.
        """
        m = float(mass_value)
        w = 50.0 + (m / 20.0) * 90.0
        h = 34.0 + (m / 20.0) * 46.0
        return w, h

    def mode_label():
        mode = collision_mode.get()
        if mode == 'elastic':
            return "Elastic (e=1.00)"
        if mode == 'inelastic':
            return "Totally inelastic (e=0.00)"
        return f"Somewhat elastic (e={restitution_e.get():.2f})"

    def restitution():
        mode = collision_mode.get()
        if mode == 'elastic':
            return 1.0
        if mode == 'inelastic':
            return 0.0
        return restitution_e.get()

    def compute_after_vels():
        """Calculate post-collision velocities using the coefficient of restitution e.

        u1 = ((m1 - e*m2)v1 + (1+e)m2 v2) / (m1+m2)
        u2 = ((m2 - e*m1)v2 + (1+e)m1 v1) / (m1+m2)
        e=1 reduces to the elastic formulas; e=0 reduces to both cars sharing one
        final velocity (perfectly inelastic).
        """
        M1 = m1.get(); V1 = state['v1']
        M2 = m2.get(); V2 = state['v2']
        e = restitution()
        u1 = ((M1 - e * M2) * V1 + (1 + e) * M2 * V2) / (M1 + M2)
        u2 = ((M2 - e * M1) * V2 + (1 + e) * M1 * V1) / (M1 + M2)
        return u1, u2

    def region_bounds():
        canvas_width = max(200, canvas.winfo_width() or 900)
        return 0.0, float(canvas_width)

    def update_equations():
        M1, V1 = m1.get(), state['v1']
        M2, V2 = m2.get(), state['v2']
        p_total = M1 * V1 + M2 * V2
        ke_total = 0.5 * M1 * V1 ** 2 + 0.5 * M2 * V2 ** 2
        e = restitution()
        lines = [
            "Conservation of momentum",
            "  m1 v1 + m2 v2 = m1 u1 + m2 u2",
            f"  ({M1:.2f})({V1:.2f}) + ({M2:.2f})({V2:.2f})",
            f"  p_total = {p_total:.2f} kg·m/s",
            "",
            f"Collision mode: {mode_label()}",
            "  u1 = ((m1 - e·m2)v1 + (1+e)m2 v2)/(m1+m2)",
            "  u2 = ((m2 - e·m1)v2 + (1+e)m1 v1)/(m1+m2)",
            "  (e also sets the wall-bounce restitution)",
            "",
            "Kinetic energy",
            "  KE = 1/2 m1 v1² + 1/2 m2 v2²",
            f"  = {ke_total:.2f} J",
        ]
        if e < 1.0:
            lines += ["  (KE is not conserved — some is lost on impact)"]
        if friction_on.get():
            lines += [
                "",
                "Kinetic friction (decelerates both cars)",
                "  a_friction = -μ g · sign(v)",
                f"  μ={friction_mu.get():.2f}  →  a = {friction_mu.get() * 9.81:.2f} m/s²",
            ]
        lines += [
            "",
            f"v1 = {V1:.2f} m/s   v2 = {V2:.2f} m/s",
        ]
        update_equations_text(lines)

    def draw_scene():
        canvas.delete('all')
        canvas_width = max(200, canvas.winfo_width() or 900)
        canvas_height = max(140, canvas.winfo_height() or 240)
        road_y = canvas_height - 55
        viz_common.draw_road(canvas, canvas_width, canvas_height, road_y)

        w1, h1 = box_size(m1.get())
        w2, h2 = box_size(m2.get())
        x1_left, x1_right = state['x1'], state['x1'] + w1
        x2_left, x2_right = state['x2'], state['x2'] + w2

        viz_common.draw_car(canvas, x1_left, x1_right, road_y, h1, '#3a56b0', '#7c94e0', f"m1={m1.get():.2f} kg")
        viz_common.draw_car(canvas, x2_left, x2_right, road_y, h2, '#c1440e', '#e8875a', f"m2={m2.get():.2f} kg")

        v1_now, v2_now = state['v1'], state['v2']
        x1_mid, x2_mid = (x1_left + x1_right) / 2, (x2_left + x2_right) / 2
        y_vec1 = road_y - h1 - 24
        y_vec2 = road_y - h2 - 24

        if abs(v1_now) > 1e-6:
            length = max(-140, min(140, v1_now * 4))
            viz_common.draw_arrow(canvas, x1_mid, y_vec1, x1_mid + length, y_vec1, '#1d4fd8', 3, f"v1={v1_now:.2f} m/s")
        if abs(v2_now) > 1e-6:
            length = max(-140, min(140, v2_now * 4))
            viz_common.draw_arrow(canvas, x2_mid, y_vec2, x2_mid + length, y_vec2, '#c1440e', 3, f"v2={v2_now:.2f} m/s")

        p_total = m1.get() * v1_now + m2.get() * v2_now
        viz_common.draw_legend(canvas, _MOMENTUM_LEGEND, canvas_width)
        viz_common.draw_readout(canvas, f"p_total={p_total:.2f} kg*m/s   mode={mode_label()}")

    # Reset the collision scene to its initial positions and velocities.
    def reset():
        region_left, region_right = region_bounds()
        region_width = region_right - region_left

        w1, _h1 = box_size(m1.get())
        w2, _h2 = box_size(m2.get())

        # Keep a visible gap between the cars (scale with widths).
        gap = max(40.0, 0.2 * (w1 + w2))
        total_width = w1 + w2 + gap

        x1_left = region_left + max(0.0, (region_width - total_width) / 2.0)
        x2_left = x1_left + w1 + gap

        state['x1'] = x1_left
        state['x2'] = x2_left
        state['v1'] = v1.get()
        state['v2'] = v2.get()
        state['running'] = False

        draw_scene()
        update_equations()

    def refresh(*_args):
        if not state['running']:
            draw_scene()
            update_equations()

    for var in (m1, v1, m2, v2, collision_mode, restitution_e, friction_on, friction_mu):
        var.trace_add("write", refresh)

    # Advance the collision animation by one frame and redraw the scene.
    def step():
        if not state['running']:
            return
        dt = FRAME_DT

        if friction_on.get():
            mu = friction_mu.get()
            decel = mu * 9.81 * dt
            for key in ('v1', 'v2'):
                v = state[key]
                if abs(v) <= decel:
                    state[key] = 0.0
                elif abs(v) > 1e-9:
                    state[key] -= math.copysign(decel, v)

        state['x1'] += state['v1'] * dt * PX_PER_MPS
        state['x2'] += state['v2'] * dt * PX_PER_MPS

        region_left, region_right = region_bounds()
        w1, _h1 = box_size(m1.get())
        w2, _h2 = box_size(m2.get())
        e_wall = restitution()

        # Bounce off the walls at the edges of the screen.
        if state['x1'] < region_left:
            state['x1'] = region_left
            state['v1'] = -state['v1'] * e_wall
        elif state['x1'] + w1 > region_right:
            state['x1'] = region_right - w1
            state['v1'] = -state['v1'] * e_wall

        if state['x2'] < region_left:
            state['x2'] = region_left
            state['v2'] = -state['v2'] * e_wall
        elif state['x2'] + w2 > region_right:
            state['x2'] = region_right - w2
            state['v2'] = -state['v2'] * e_wall

        # Detect car-car collision (simple overlap test) and resolve it.
        if state['x1'] + w1 >= state['x2']:
            u1, u2 = compute_after_vels()
            state['v1'], state['v2'] = u1, u2
            overlap = (state['x1'] + w1) - state['x2']
            if overlap > 0:
                state['x1'] -= overlap / 2
                state['x2'] += overlap / 2

        draw_scene()
        update_equations()
        if state['running']:
            win.after(FRAME_MS, step)

    def start():
        if not state['running']:
            state['running'] = True
            step()

    def stop():
        state['running'] = False

    # --- Let the user drag a car horizontally with the cursor ---
    def car_under(x):
        w1, _h1 = box_size(m1.get())
        w2, _h2 = box_size(m2.get())
        if state['x1'] <= x <= state['x1'] + w1:
            return 1
        if state['x2'] <= x <= state['x2'] + w2:
            return 2
        return None

    def on_press(event):
        car = car_under(event.x)
        drag['car'] = car
        if car == 1:
            drag['offset'] = event.x - state['x1']
        elif car == 2:
            drag['offset'] = event.x - state['x2']

    def on_drag(event):
        if drag['car'] is None:
            return
        region_left, region_right = region_bounds()
        if drag['car'] == 1:
            w1, _h1 = box_size(m1.get())
            state['x1'] = min(max(event.x - drag['offset'], region_left), region_right - w1)
        else:
            w2, _h2 = box_size(m2.get())
            state['x2'] = min(max(event.x - drag['offset'], region_left), region_right - w2)
        draw_scene()

    def on_release(_event):
        drag['car'] = None

    def on_hover(event):
        canvas.config(cursor='fleur' if car_under(event.x) is not None else '')

    canvas.bind('<ButtonPress-1>', on_press)
    canvas.bind('<B1-Motion>', on_drag)
    canvas.bind('<ButtonRelease-1>', on_release)
    canvas.bind('<Motion>', on_hover)
    canvas.bind('<Configure>', refresh)

    ttk.Button(frm, text='Reset', command=reset).pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=6, pady=6)
    ttk.Button(frm, text='Start', command=start).pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=6, pady=6)
    ttk.Button(frm, text='Stop', command=stop).pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=6, pady=6)

    reset()
    return win
