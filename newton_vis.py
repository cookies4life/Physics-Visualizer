"""Newton's laws visualizations for forces, friction, and incline motion."""

import tkinter as tk
from tkinter import ttk
import math

import viz_common

# Pixels-per-meter scale for the incline animation, and the block's real-world
# size in meters. Keeping physics in meters (rather than treating 1 px = 1 m,
# which made the "ramp" hundreds of meters long and motion imperceptibly slow)
# is what makes the animation actually move at a watchable pace.
PPM = 80.0
BOX_W_M = 1.0
BOX_H_M = 0.5

# Cap on upward (up-slope) speed: a push demonstrates the block accelerating
# briefly, then holding a steady pace up the ramp, instead of continuously
# accelerating off the top of the incline. Downhill motion under gravity is
# left uncapped since speeding up while sliding down is the expected behavior.
MAX_UP_SPEED_MS = 2.5


def create_incline_demo_window(master=None, title="Incline Demo", description="", mode='slide', initial_force=0.0):
    """Create a window showing a block on an incline with force vectors and motion."""
    win = tk.Toplevel(master) if master else tk.Tk()
    win.title(title)
    win.geometry("1020x880+60+30")

    header = ttk.Frame(win)
    header.pack(fill=tk.X)
    ttk.Label(header, text=title, font=(None, 16, 'bold')).pack(anchor='n')
    ttk.Label(header, text=description, wraplength=960).pack(anchor='n')

    frm = ttk.Frame(win, padding=8)
    frm.pack(fill=tk.BOTH, expand=True)

    mass = tk.DoubleVar(value=2.0)
    force = tk.DoubleVar(value=initial_force)
    friction_on = tk.BooleanVar(value=False)
    friction_mu = tk.DoubleVar(value=0.30)
    incline_angle = tk.DoubleVar(value=20.0)
    gravity_enabled = tk.BooleanVar(value=True)
    gravity_force = tk.DoubleVar(value=9.81)
    show_forces = tk.BooleanVar(value=True)
    show_weight = tk.BooleanVar(value=True)
    show_normal = tk.BooleanVar(value=True)
    show_friction = tk.BooleanVar(value=True)

    def _bind_display(var, display_var):
        def _update(*_args):
            display_var.set(f"{var.get():.2f}")
        var.trace_add("write", _update)
        _update()

    mass_display = tk.StringVar()
    force_display = tk.StringVar()
    mu_display = tk.StringVar()
    angle_display = tk.StringVar()
    gravity_display = tk.StringVar()
    _bind_display(mass, mass_display)
    _bind_display(force, force_display)
    _bind_display(friction_mu, mu_display)
    _bind_display(incline_angle, angle_display)
    _bind_display(gravity_force, gravity_display)

    ttk.Label(frm, text="Mass (kg)").grid(row=0, column=0, sticky='w')
    ttk.Scale(frm, from_=0.1, to=20, variable=mass, orient=tk.HORIZONTAL).grid(row=0, column=1, sticky='we')
    ttk.Label(frm, textvariable=mass_display).grid(row=0, column=2)

    ttk.Label(frm, text="Applied force along incline (N)").grid(row=1, column=0, sticky='w')
    ttk.Scale(frm, from_=-50, to=50, variable=force, orient=tk.HORIZONTAL).grid(row=1, column=1, sticky='we')
    ttk.Label(frm, textvariable=force_display).grid(row=1, column=2)

    ttk.Checkbutton(frm, text="Include kinetic friction", variable=friction_on).grid(row=2, column=0, columnspan=3, sticky='w')
    ttk.Label(frm, text="Friction coefficient μ").grid(row=3, column=0, sticky='w')
    ttk.Scale(frm, from_=0.0, to=1.0, variable=friction_mu, orient=tk.HORIZONTAL).grid(row=3, column=1, sticky='we')
    ttk.Label(frm, textvariable=mu_display).grid(row=3, column=2)

    ttk.Label(frm, text="Incline angle (deg)").grid(row=4, column=0, sticky='w')
    ttk.Scale(frm, from_=0, to=90, variable=incline_angle, orient=tk.HORIZONTAL).grid(row=4, column=1, sticky='we')
    ttk.Label(frm, textvariable=angle_display).grid(row=4, column=2)

    ttk.Checkbutton(frm, text="Enable gravity", variable=gravity_enabled).grid(row=5, column=0, columnspan=3, sticky='w')
    ttk.Label(frm, text="Gravity (m/s²)").grid(row=6, column=0, sticky='w')
    ttk.Scale(frm, from_=0.0, to=20.0, variable=gravity_force, orient=tk.HORIZONTAL).grid(row=6, column=1, sticky='we')
    ttk.Label(frm, textvariable=gravity_display).grid(row=6, column=2)

    ttk.Checkbutton(frm, text="Show force vectors", variable=show_forces).grid(row=7, column=0, columnspan=3, sticky='w')
    ttk.Checkbutton(frm, text="Show weight", variable=show_weight).grid(row=8, column=0, columnspan=3, sticky='w')
    ttk.Checkbutton(frm, text="Show normal force", variable=show_normal).grid(row=9, column=0, columnspan=3, sticky='w')
    ttk.Checkbutton(frm, text="Show friction force", variable=show_friction).grid(row=10, column=0, columnspan=3, sticky='w')

    canvas = tk.Canvas(frm, bg='#eaf6ff', width=960, height=480, highlightthickness=0)
    canvas.grid(row=11, column=0, columnspan=3, sticky='nsew', pady=8)
    frm.columnconfigure(0, weight=1)
    frm.rowconfigure(11, weight=1)

    # --- Small companion window showing the equations being demonstrated ---
    eq_win, update_equations_text = viz_common.create_equations_panel(win, title)

    def update_equations(v):
        friction_dir = "up-slope" if v['friction'] > 1e-6 else "down-slope" if v['friction'] < -1e-6 else "none"
        lines = [
            "Normal force",
            "  N = mg cosθ",
            f"  N = ({v['m']:.2f})({v['g']:.2f})cos({v['angle_deg']:.1f}°)",
            f"  N = {v['N']:.2f} N",
            "",
            "Gravity component along incline",
            "  mg sinθ",
            f"  = ({v['m']:.2f})({v['g']:.2f})sin({v['angle_deg']:.1f}°)",
            f"  = {v['g_par']:.2f} N (points down-slope)",
            "",
        ]
        if v['friction_on']:
            lines += [
                "Kinetic friction",
                "  f = μN",
                f"  = ({v['mu']:.2f})({v['N']:.2f})",
                f"  = {v['friction_mag']:.2f} N ({friction_dir})",
                "",
            ]
        lines += [
            "Newton's 2nd law (along incline, up-slope +)",
            "  F_applied − mg sinθ + f = ma",
            f"  {v['F']:.2f} − {v['g_par']:.2f} + ({v['friction']:+.2f}) = ({v['m']:.2f})a",
            f"  a = {v['a']:.2f} m/s²",
            "",
            "Kinematics",
            f"  v = {v['v']:.2f} m/s",
            f"  s = {v['s']:.2f} m  (0 = bottom, {v['max_s']:.1f} = top)",
        ]
        if v.get('capped'):
            lines += [
                "",
                f"(Up-slope speed capped at {MAX_UP_SPEED_MS:.1f} m/s so the",
                " block doesn't keep accelerating off the top of the ramp.)",
            ]
        update_equations_text(lines)

    win.protocol("WM_DELETE_WINDOW", lambda: (eq_win.destroy(), win.destroy()))

    # Store the current simulation state (s in meters along the incline, v in m/s).
    state = {'s': 0.0, 'v': 0.0}
    running = {'on': False}

    # Compute the incline's on-screen geometry, shared by drawing and physics.
    def incline_geometry():
        angle = math.radians(incline_angle.get())
        base_x = 90
        base_y = 380
        canvas_w = canvas.winfo_width() or 960
        canvas_h = canvas.winfo_height() or 480
        length_px = max(700, canvas_w - base_x - 60)
        x2 = base_x + length_px * math.cos(angle)
        y2 = base_y - length_px * math.sin(angle)
        dx = x2 - base_x
        dy = y2 - base_y
        incline_length_px = math.hypot(dx, dy)
        dir_x = dx / incline_length_px
        dir_y = dy / incline_length_px
        incline_length_m = incline_length_px / PPM
        return {
            'angle': angle, 'base_x': base_x, 'base_y': base_y,
            'x2': x2, 'y2': y2, 'dir_x': dir_x, 'dir_y': dir_y,
            'normal_x': dir_y, 'normal_y': -dir_x,
            'max_s': max(0.5, incline_length_m - BOX_W_M),
            'canvas_w': canvas_w, 'canvas_h': canvas_h,
        }

    # Compute the current forces/acceleration without stepping the simulation,
    # so sliders can be dragged (while stopped) and everything stays in sync.
    def compute_dynamics():
        m = mass.get()
        F = force.get()
        angle_deg = incline_angle.get()
        angle = math.radians(angle_deg)
        g = gravity_force.get() if gravity_enabled.get() else 0.0
        g_par = m * g * abs(math.sin(angle))
        N = m * g * math.cos(abs(angle))
        mu = friction_mu.get() if friction_on.get() else 0.0
        friction_mag = mu * N
        net = F - g_par
        if friction_on.get():
            if abs(state['v']) > 1e-3:
                friction = -math.copysign(1.0, state['v']) * friction_mag
            else:
                friction = -math.copysign(1.0, net) * friction_mag if abs(net) > friction_mag else 0.0
        else:
            friction = 0.0
        a = (net + friction) / m
        return {
            'a': a, 'g_par': g_par, 'N': N, 'friction_mag': friction_mag, 'friction': friction,
            'm': m, 'F': F, 'mu': mu, 'angle_deg': angle_deg, 'g': g,
            'friction_on': friction_on.get(), 'v': state['v'], 's': state['s'],
            'max_s': incline_geometry()['max_s'],
        }

    # Reset the incline demo back to the starting position.
    def reset():
        geo = incline_geometry()
        state['s'] = 0.0 if mode == 'push' else geo['max_s']
        state['v'] = 0.0
        running['on'] = False
        draw_scene(compute_dynamics())

    def _draw_incline(geo):
        base_x, base_y = geo['base_x'], geo['base_y']
        x2, y2 = geo['x2'], geo['y2']
        nx, ny = geo['normal_x'], geo['normal_y']
        canvas.create_polygon(base_x, base_y, x2, y2, x2, base_y, fill='#c98a4b', outline='#6b4423', width=3)
        for i in range(14):
            t = i / 13
            xi = base_x + t * (x2 - base_x)
            yi = base_y - t * (base_y - y2)
            canvas.create_line(xi, yi, xi + 20 * nx, yi + 20 * ny, fill='#a9713f', width=2)
        inset = 5
        canvas.create_line(base_x - inset * nx, base_y - inset * ny, x2 - inset * nx, y2 - inset * ny, fill='#e3b27b', width=2)
        canvas.create_line(base_x, base_y, x2, base_y, fill='#4a2d15', width=4)
        m = 14
        canvas.create_line(x2 - m, base_y, x2 - m, base_y - m, x2, base_y - m, fill='#4a2d15', width=1)
        angle_deg = math.degrees(geo['angle'])
        if angle_deg > 1:
            r = 46
            canvas.create_arc(base_x - r, base_y - r, base_x + r, base_y + r, start=0, extent=-angle_deg, style='arc', outline='#333333', width=2)
            mid = math.radians(angle_deg / 2)
            canvas.create_text(base_x + (r + 20) * math.cos(mid), base_y - (r + 20) * math.sin(mid), text=f"θ={angle_deg:.1f}°", font=('Arial', 10, 'bold'))

    _INCLINE_LEGEND = [('Applied force', '#1d4fd8'), ('Weight (mg)', '#222222'), ('Normal force', '#1f8a3b'), ('Friction', '#7a4a22'), ('Gravity ∥ incline', '#d9740c')]

    # Draw the entire scene with the incline, block, and force arrows.
    def draw_scene(v):
        canvas.delete('all')
        geo = incline_geometry()
        base_x, base_y = geo['base_x'], geo['base_y']
        dir_x, dir_y = geo['dir_x'], geo['dir_y']
        normal_x, normal_y = geo['normal_x'], geo['normal_y']

        viz_common.draw_backdrop(canvas, geo['canvas_w'], geo['canvas_h'], base_y)
        _draw_incline(geo)

        block_x = base_x + state['s'] * PPM * dir_x
        block_y = base_y + state['s'] * PPM * dir_y
        box_w = BOX_W_M * PPM
        box_h = BOX_H_M * PPM
        box_cx = block_x + normal_x * (box_h / 2)
        box_cy = block_y + normal_y * (box_h / 2)
        # Tilted rectangle corners (parallel to incline, lower edge touching incline)
        lower_left = (block_x - box_w / 2 * dir_x, block_y - box_w / 2 * dir_y)
        lower_right = (block_x + box_w / 2 * dir_x, block_y + box_w / 2 * dir_y)
        upper_right = (lower_right[0] + box_h * normal_x, lower_right[1] + box_h * normal_y)
        upper_left = (lower_left[0] + box_h * normal_x, lower_left[1] + box_h * normal_y)
        corners = [lower_left, lower_right, upper_right, upper_left]
        viz_common.draw_tilted_block(canvas, corners, box_cx, box_cy, mass.get())

        if show_weight.get():
            viz_common.draw_arrow(canvas, box_cx, box_cy, box_cx, box_cy + 120, '#222222', 2, f"W={v['m'] * v['g']:.2f} N")

        if show_normal.get():
            viz_common.draw_arrow(canvas, box_cx, box_cy, box_cx + normal_x * 90, box_cy + normal_y * 90, '#1f8a3b', 2, f"N={v['N']:.2f} N")

        if show_friction.get() and v['friction_on'] and abs(v['friction']) > 1e-6:
            # dir_x/dir_y already point up-slope, so the signed friction value
            # alone determines the arrow's direction — no separate sign logic needed.
            viz_common.draw_arrow(canvas, box_cx, box_cy, box_cx + v['friction'] * 0.8 * dir_x, box_cy + v['friction'] * 0.8 * dir_y, '#7a4a22', 2, f"f={abs(v['friction']):.2f} N")

        if show_forces.get() and abs(v['F']) > 1e-6:
            # Positive applied force points up-slope (+dir), matching the physics in compute_dynamics().
            viz_common.draw_arrow(canvas, box_cx, box_cy, box_cx + v['F'] * 0.8 * dir_x, box_cy + v['F'] * 0.8 * dir_y, '#1d4fd8', 3, f"F={v['F']:.2f} N")

        if v['g_par'] > 1e-6:
            # Gravity's incline-parallel component always pulls down-slope (-dir).
            viz_common.draw_arrow(canvas, box_cx, box_cy, box_cx - v['g_par'] * 0.8 * dir_x, box_cy - v['g_par'] * 0.8 * dir_y, '#d9740c', 3, f"mg sinθ={v['g_par']:.2f} N")

        viz_common.draw_legend(canvas, _INCLINE_LEGEND, geo['canvas_w'])
        viz_common.draw_readout(canvas, f"a={v['a']:.2f} m/s^2  v={state['v']:.2f} m/s  s={state['s']:.2f} m  th={v['angle_deg']:.1f} deg")
        update_equations(v)

    def refresh(*_args):
        if not running['on']:
            draw_scene(compute_dynamics())

    for var in (mass, force, friction_on, friction_mu, incline_angle, gravity_enabled, gravity_force, show_forces, show_weight, show_normal, show_friction):
        var.trace_add("write", refresh)
    canvas.bind('<Configure>', refresh)

    def advance():
        v = compute_dynamics()
        a = v['a']
        if abs(math.radians(v['angle_deg'])) < 1e-3 and abs(v['F']) < 1e-3:
            a = 0.0
            state['v'] = 0.0
        state['v'] += a * 0.03
        capped = state['v'] > MAX_UP_SPEED_MS
        if capped:
            state['v'] = MAX_UP_SPEED_MS
        state['s'] += state['v'] * 0.03
        max_s = v['max_s']
        if state['s'] < 0.0:
            state['s'] = 0.0
            state['v'] = 0.0
        elif state['s'] > max_s:
            state['s'] = max_s
            state['v'] = 0.0
        draw_scene(compute_dynamics() | {'a': a, 'capped': capped})
        if running['on']:
            win.after(30, advance)

    ttk.Button(frm, text='Reset', command=reset).grid(row=12, column=0, sticky='nsew')
    ttk.Button(frm, text='Start', command=lambda: running.update({'on': True}) or advance()).grid(row=12, column=1, sticky='nsew')
    ttk.Button(frm, text='Stop', command=lambda: running.update({'on': False})).grid(row=12, column=2, sticky='nsew')
    frm.rowconfigure(10, weight=1)
    frm.columnconfigure(0, weight=1)
    frm.columnconfigure(1, weight=1)
    frm.columnconfigure(2, weight=1)


    reset()
    return win


def open_push_up_incline_window(master=None):
    """Open the incline demo where the block is pushed up the slope."""
    return create_incline_demo_window(
        master,
        title="Push-Up Incline Demo",
        description="A block starts at the bottom of a wooden incline. The applied force (defaulted to a push) points up the slope while gravity pulls down parallel to the incline.",
        mode='push',
        initial_force=20.0)


def open_push_down_incline_window(master=None):
    """Open the incline demo where the block starts at the top and is pushed down the slope."""
    return create_incline_demo_window(
        master,
        title="Push-Down Incline Demo",
        description="A block starts at the top of a wooden incline. Gravity pulls it down the slope, an applied force can push it down or resist its slide, and friction opposes the motion.",
        mode='slide',
        initial_force=0.0)


def open_newton_window(master=None):
    """Create the main Newton's laws window with horizontal-motion and incline demos."""
    win = tk.Toplevel(master) if master else tk.Tk()
    win.title("Newton's Laws — Force Visualizer")
    win.geometry("900x420")

    def _maximize_or_fullscreen_max(win_obj: tk.Toplevel):
        """Best-effort maximize for cross-platform Tk.

        Use after() so the window manager has finished creating the window.
        """
        try:
            win_obj.state('zoomed')
        except Exception:
            pass

    # Start as maximized.
    win.after(100, lambda: _maximize_or_fullscreen_max(win))



    header = ttk.Frame(win)
    header.pack(fill=tk.X)
    ttk.Label(header, text="Newton's Laws — Force Visualizer", font=(None, 16, 'bold')).pack(anchor='n')
    ttk.Label(header, text="Horizontal block simulation with adjustable friction and force vector visualization.", wraplength=880).pack(anchor='n')

    frm = ttk.Frame(win, padding=8)
    frm.pack(fill=tk.BOTH, expand=True)

    mass = tk.DoubleVar(value=2.0)
    force = tk.DoubleVar(value=5.0)
    friction_on = tk.BooleanVar(value=False)
    friction_mu = tk.DoubleVar(value=0.30)
    show_forces = tk.BooleanVar(value=True)
    show_weight = tk.BooleanVar(value=True)
    show_normal = tk.BooleanVar(value=True)
    show_friction = tk.BooleanVar(value=True)

    def _bind_display(var, display_var):
        def _update(*_args):
            display_var.set(f"{var.get():.2f}")
        var.trace_add("write", _update)
        _update()

    mass_display = tk.StringVar()
    force_display = tk.StringVar()
    mu_display = tk.StringVar()
    _bind_display(mass, mass_display)
    _bind_display(force, force_display)
    _bind_display(friction_mu, mu_display)

    ttk.Label(frm, text="Mass (kg)").grid(row=0, column=0, sticky='w')
    ttk.Scale(frm, from_=0.1, to=20, variable=mass, orient=tk.HORIZONTAL).grid(row=0, column=1, sticky='we')
    ttk.Label(frm, textvariable=mass_display).grid(row=0, column=2)

    ttk.Label(frm, text="Applied force (N)").grid(row=1, column=0, sticky='w')
    ttk.Scale(frm, from_=-50, to=50, variable=force, orient=tk.HORIZONTAL).grid(row=1, column=1, sticky='we')
    ttk.Label(frm, textvariable=force_display).grid(row=1, column=2)

    ttk.Checkbutton(frm, text="Include kinetic friction", variable=friction_on).grid(row=2, column=0, columnspan=3, sticky='w')
    ttk.Label(frm, text="Friction coefficient μ").grid(row=3, column=0, sticky='w')
    ttk.Scale(frm, from_=0.0, to=1.0, variable=friction_mu, orient=tk.HORIZONTAL).grid(row=3, column=1, sticky='we')
    ttk.Label(frm, textvariable=mu_display).grid(row=3, column=2)

    ttk.Checkbutton(frm, text="Show force vectors", variable=show_forces).grid(row=4, column=0, columnspan=3, sticky='w')
    ttk.Checkbutton(frm, text="Show weight", variable=show_weight).grid(row=5, column=0, columnspan=3, sticky='w')
    ttk.Checkbutton(frm, text="Show normal force", variable=show_normal).grid(row=6, column=0, columnspan=3, sticky='w')
    ttk.Checkbutton(frm, text="Show friction force", variable=show_friction).grid(row=7, column=0, columnspan=3, sticky='w')

    canvas = tk.Canvas(frm, bg='#eaf6ff', height=280, highlightthickness=0)
    canvas.grid(row=8, column=0, columnspan=3, sticky='nsew', pady=8)
    frm.columnconfigure(1, weight=1)

    GROUND_Y = 220
    _FLAT_LEGEND = [('Applied force', '#1d4fd8'), ('Weight (mg)', '#222222'), ('Normal force', '#1f8a3b'), ('Friction', '#7a4a22')]

    # Track the horizontal block's position (meters from the left margin) and velocity (m/s).
    pos = {'x': 0.5, 'v': 0.0}
    running = {'on': False}

    def max_x_m():
        canvas_w = canvas.winfo_width() or 900
        return max(1.0, (canvas_w - 80) / PPM - BOX_W_M)

    # Reset the horizontal block demo to its starting position.
    def reset():
        pos['x'] = 0.5
        pos['v'] = 0.0
        running['on'] = False
        draw_forces(0, 0, mass.get(), 0)

    def draw_forces(F, F_fric, m, v):
        """Draw the block and the visible force arrows for the horizontal motion demo."""
        canvas.delete('all')
        canvas_w = canvas.winfo_width() or 900
        canvas_h = canvas.winfo_height() or 280
        viz_common.draw_backdrop(canvas, canvas_w, canvas_h, GROUND_Y)

        box_w = BOX_W_M * PPM
        box_h = BOX_H_M * PPM
        x0 = 40 + pos['x'] * PPM
        x1 = x0 + box_w
        y1 = GROUND_Y
        y0 = y1 - box_h
        cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
        viz_common.draw_flat_block(canvas, x0, y0, x1, y1, m)

        if show_weight.get():
            viz_common.draw_arrow(canvas, cx, cy, cx, cy + 120, '#222222', 2, f"W={m * 9.81:.2f} N")
        if show_normal.get():
            viz_common.draw_arrow(canvas, cx, cy, cx, cy - 90, '#1f8a3b', 2, f"N={m * 9.81:.2f} N")
        if show_forces.get() and abs(F) > 1e-6:
            viz_common.draw_arrow(canvas, cx, cy, cx + F * 4, cy, '#1d4fd8', 3, f"F={F:.2f} N")
        if show_friction.get() and friction_on.get() and abs(F_fric) > 1e-6:
            viz_common.draw_arrow(canvas, cx, cy, cx + F_fric * 4, cy, '#7a4a22', 2, f"f={abs(F_fric):.2f} N")

        viz_common.draw_legend(canvas, _FLAT_LEGEND, canvas_w)
        viz_common.draw_readout(canvas, f"a={((F + F_fric) / m):.2f} m/s^2  v={v:.2f} m/s  x={pos['x']:.2f} m")

    def advance():
        m = mass.get()
        F = force.get()
        mu = friction_mu.get() if friction_on.get() else 0.0
        g = 9.81
        if abs(pos['v']) > 1e-3:
            F_fric = -mu * m * g * (1 if pos['v'] > 0 else -1)
        else:
            F_fric = -mu * m * g * (1 if F > 0 else -1) if abs(F) > mu*m*g else 0
        F_net = F + F_fric
        a = F_net / m

        pos['v'] += a * 0.03
        pos['x'] += pos['v'] * 0.03
        max_x = max_x_m()
        if pos['x'] < 0.0:
            pos['x'] = 0.0
            pos['v'] = 0.0
        elif pos['x'] > max_x:
            pos['x'] = max_x
            pos['v'] = 0.0
        draw_forces(F, F_fric, m, pos['v'])
        if running['on']:
            win.after(30, advance)

    ttk.Button(frm, text='Reset', command=reset).grid(row=9, column=0, sticky='nsew')
    ttk.Button(frm, text='Start', command=lambda: running.update({'on': True}) or advance()).grid(row=9, column=1, sticky='nsew')
    ttk.Button(frm, text='Stop', command=lambda: running.update({'on': False})).grid(row=9, column=2, sticky='nsew')
    frm.rowconfigure(9, weight=1)
    frm.columnconfigure(0, weight=1)
    frm.columnconfigure(1, weight=1)
    frm.columnconfigure(2, weight=1)

    ttk.Button(frm, text='Open push-up incline demo', command=lambda: open_push_up_incline_window(win)).grid(row=10, column=0, columnspan=3, sticky='nsew', pady=4)
    ttk.Button(frm, text='Open push-down incline demo', command=lambda: open_push_down_incline_window(win)).grid(row=11, column=0, columnspan=3, sticky='nsew', pady=4)


    reset()
    return win
