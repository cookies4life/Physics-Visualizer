"""Newton's laws visualizations for forces, friction, and incline motion."""

import tkinter as tk
from tkinter import ttk
import math


def create_incline_demo_window(master=None, title="Incline Demo", description="", mode='slide'):
    """Create a window showing a block on an incline with force vectors and motion."""
    win = tk.Toplevel(master) if master else tk.Tk()
    win.title(title)
    win.geometry("980x680")

    header = ttk.Frame(win)
    header.pack(fill=tk.X)
    ttk.Label(header, text=title, font=(None, 16, 'bold')).pack(anchor='n')
    ttk.Label(header, text=description, wraplength=940).pack(anchor='n')

    frm = ttk.Frame(win, padding=8)
    frm.pack(fill=tk.BOTH, expand=True)

    mass = tk.DoubleVar(value=2.0)
    force = tk.DoubleVar(value=0.0)
    friction_on = tk.BooleanVar(value=False)
    friction_mu = tk.DoubleVar(value=0.30)
    incline_angle = tk.DoubleVar(value=20.0)
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
    _bind_display(mass, mass_display)
    _bind_display(force, force_display)
    _bind_display(friction_mu, mu_display)
    _bind_display(incline_angle, angle_display)

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
    ttk.Scale(frm, from_=-45, to=45, variable=incline_angle, orient=tk.HORIZONTAL).grid(row=4, column=1, sticky='we')
    ttk.Label(frm, textvariable=angle_display).grid(row=4, column=2)

    ttk.Checkbutton(frm, text="Show force vectors", variable=show_forces).grid(row=5, column=0, columnspan=3, sticky='w')
    ttk.Checkbutton(frm, text="Show weight", variable=show_weight).grid(row=6, column=0, columnspan=3, sticky='w')
    ttk.Checkbutton(frm, text="Show normal force", variable=show_normal).grid(row=7, column=0, columnspan=3, sticky='w')
    ttk.Checkbutton(frm, text="Show friction force", variable=show_friction).grid(row=8, column=0, columnspan=3, sticky='w')

    canvas = tk.Canvas(frm, bg='white', height=420)
    canvas.grid(row=9, column=0, columnspan=2, sticky='nsew', pady=8)
    graph_canvas = tk.Canvas(frm, bg='white', width=320, height=420)
    graph_canvas.grid(row=9, column=2, padx=(8, 0), sticky='nsew')
    frm.columnconfigure(1, weight=1)
    frm.columnconfigure(2, weight=0)

    # Store motion data for the graph and the current simulation state.
    history = []
    state = {'s': 0.0, 'v': 0.0}
    running = {'on': False}

    # Reset the incline demo back to the starting position.
    def reset():
        if mode == 'push':
            state['s'] = 220.0
        else:
            state['s'] = 0.0
        state['v'] = 0.0
        running['on'] = False
        history.clear()
        history.append({'s': state['s'], 'v': state['v']})
        draw_scene(0.0, 0.0, 0.0, 0.0)

    # Draw the wooden incline surface used in the animation.
    def draw_wooden_incline(angle, base_x, base_y, length):
        x2 = base_x + length * math.cos(angle)
        y2 = base_y - length * math.sin(angle)
        canvas.create_polygon(
            base_x, base_y,
            x2, y2,
            x2, base_y,
            fill='#d2a679', outline='sienna', width=3)
        for i in range(9):
            interp = i / 8
            xi = base_x + interp * (x2 - base_x)
            yi = base_y - interp * (base_y - y2)
            canvas.create_line(xi, yi, xi + 24 * math.cos(angle + math.pi / 2), yi - 24 * math.sin(angle + math.pi / 2), fill='#b5835f', width=2)
        canvas.create_line(base_x, base_y, x2, base_y, fill='sienna', width=4)
        return x2, y2

    # Draw the motion graph showing position and velocity over time.
    def draw_graph():
        graph_canvas.delete('all')
        width = 320
        height = 420
        margin = 40
        graph_canvas.create_rectangle(margin, margin, width - 10, height - 10, outline='black')
        graph_canvas.create_line(margin, height - margin, width - 10, height - margin, arrow='last')
        graph_canvas.create_line(margin, height - margin, margin, margin + 10, arrow='last')
        graph_canvas.create_text(width / 2, height - 15, text='time', anchor='center')
        graph_canvas.create_text(15, height / 2, text='value', anchor='center', angle=90)

        if len(history) < 2:
            return
        max_t = len(history) - 1
        max_s = max(abs(point['s']) for point in history) or 1.0
        max_v = max(abs(point['v']) for point in history) or 1.0
        for label, color, key in [('s', 'blue', 's'), ('v', 'red', 'v')]:
            points = []
            for idx, point in enumerate(history):
                x = margin + (width - margin - 10) * idx / max_t
                y = height - margin - (height - margin - 10) * abs(point[key]) / (max_s if key == 's' else max_v)
                points.extend([x, y])
            graph_canvas.create_line(*points, fill=color, smooth=True, width=2)
            graph_canvas.create_text(width - 30, margin + 10 + (0 if key == 's' else 20), text=label, fill=color, anchor='w')

    # Draw the entire scene with the incline, block, and force arrows.
    def draw_scene(a, g_par, N, friction_mag):
        canvas.delete('all')
        angle = math.radians(incline_angle.get())
        base_x = 100
        base_y = 340
        length = 440
        x2, y2 = draw_wooden_incline(angle, base_x, base_y, length)

        dx = x2 - base_x
        dy = y2 - base_y
        incline_length = math.hypot(dx, dy)
        dir_x = dx / incline_length
        dir_y = dy / incline_length
        normal_x = -dir_y
        normal_y = dir_x

        block_x = base_x + state['s'] * dir_x
        block_y = base_y + state['s'] * dir_y
        box_w = 140
        box_h = 70
        box_cx = block_x + normal_x * (box_h / 2 + 10)
        box_cy = block_y + normal_y * (box_h / 2 + 10)
        canvas.create_rectangle(
            box_cx - box_w / 2,
            box_cy - box_h / 2,
            box_cx + box_w / 2,
            box_cy + box_h / 2,
            fill='gray', outline='black', width=2)
        canvas.create_text(box_cx, box_cy, text=f"m={mass.get():.2f} kg", fill='white')

        if show_weight.get():
            wx = box_cx
            wy = box_cy
            canvas.create_line(wx, wy, wx, wy + 120, arrow='last', fill='black', width=2)
            canvas.create_text(wx - 25, wy + 130, text=f"W={mass.get() * 9.81:.2f} N")

        if show_normal.get():
            nx = box_cx + normal_x * 90
            ny = box_cy + normal_y * 90
            canvas.create_line(box_cx, box_cy, nx, ny, arrow='last', fill='green', width=2)
            canvas.create_text(nx + 10, ny - 5, text=f"N={N:.2f} N")

        if show_friction.get() and friction_on.get():
            friction_sign = -math.copysign(1.0, state['v']) if abs(state['v']) > 1e-3 else -math.copysign(1.0, g_par - force.get())
            friction = friction_sign * friction_mag
            fx = box_cx + friction * 0.8 * dir_x
            fy = box_cy + friction * 0.8 * dir_y
            fx2 = fx - friction_sign * normal_x * 60
            fy2 = fy - friction_sign * normal_y * 60
            canvas.create_line(fx, fy, fx2, fy2, arrow='last', fill='brown', width=2)
            canvas.create_text(fx2 - 10, fy2 + 10, text=f"F_fric={friction_mag:.2f} N")

        if show_forces.get():
            F_up = force.get()
            arrow_x = box_cx - F_up * 0.8 * dir_x
            arrow_y = box_cy - F_up * 0.8 * dir_y
            canvas.create_line(box_cx, box_cy, arrow_x, arrow_y, arrow='last', fill='blue', width=3)
            canvas.create_text(arrow_x - 15, arrow_y - 15, text=f"F_up={F_up:.2f} N", fill='blue')

        fgx = box_cx + g_par * 0.8 * dir_x
        fgy = box_cy + g_par * 0.8 * dir_y
        canvas.create_line(box_cx, box_cy, fgx, fgy, arrow='last', fill='orange', width=3)
        canvas.create_text(fgx + 5, fgy + 5, text=f"mg sinθ={g_par:.2f} N", fill='orange')

        canvas.create_text(20, 20, anchor='nw', text=f"vx={state['v']:.2f} m/s   s={state['s']:.2f} m   θ={incline_angle.get():.2f}°")
        draw_graph()

    def advance():
        m = mass.get()
        F_up = force.get()
        angle = math.radians(incline_angle.get())
        g = 9.81
        g_par = m * g * abs(math.sin(angle))
        N = m * g * math.cos(abs(angle))
        mu = friction_mu.get() if friction_on.get() else 0.0
        friction_mag = mu * N
        net_downhill = g_par - F_up
        if friction_on.get():
            if abs(state['v']) > 1e-3:
                friction = -math.copysign(1.0, state['v']) * friction_mag
            else:
                friction = -math.copysign(1.0, net_downhill) * friction_mag if abs(net_downhill) > friction_mag else 0.0
        else:
            friction = 0.0
        a = (net_downhill + friction) / m
        state['v'] += a * 0.03
        state['s'] += state['v'] * 0.03
        max_s = 220.0
        if state['s'] < 0.0:
            state['s'] = 0.0
            state['v'] = 0.0
        elif state['s'] > max_s:
            state['s'] = max_s
            state['v'] = 0.0
        history.append({'s': state['s'], 'v': state['v']})
        if len(history) > 120:
            history.pop(0)
        draw_scene(a, g_par, N, friction_mag)
        if running['on']:
            win.after(30, advance)

    ttk.Button(frm, text='Reset', command=reset).grid(row=10, column=0, sticky='w')
    ttk.Button(frm, text='Start', command=lambda: running.update({'on': True}) or advance()).grid(row=10, column=1)
    ttk.Button(frm, text='Stop', command=lambda: running.update({'on': False})).grid(row=10, column=2, sticky='e')

    reset()


def open_push_up_incline_window(master=None):
    """Open the incline demo where the block is pushed up the slope."""
    return create_incline_demo_window(
        master,
        title="Push-Up Incline Demo",
        description="A block is pushed up a wooden incline. The applied force points up the slope while gravity pulls down parallel to the incline.",
        mode='push')


def open_slide_down_incline_window(master=None):
    """Open the incline demo where the block slides down the slope."""
    return create_incline_demo_window(
        master,
        title="Slide-Down Incline Demo",
        description="A block slides down a wooden incline. Gravity pulls it along the slope, and friction resists the motion.",
        mode='slide')


def open_newton_window(master=None):
    """Create the main Newton's laws window with horizontal-motion and incline demos."""
    win = tk.Toplevel(master) if master else tk.Tk()
    win.title("Newton's Laws — Force Visualizer")
    win.geometry("900x420")

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

    canvas = tk.Canvas(frm, bg='white', height=240)
    canvas.grid(row=8, column=0, columnspan=3, sticky='nsew', pady=8)
    frm.columnconfigure(1, weight=1)

    # Track the horizontal block's position and velocity.
    pos = {'x': 50.0, 'v': 0.0}
    running = {'on': False}

    # Reset the horizontal block demo to its starting position.
    def reset():
        pos['x'] = 50.0
        pos['v'] = 0.0
        running['on'] = False
        draw_forces(0, 0, mass.get(), 0)

    def draw_forces(F, F_fric, m, v):
        """Draw the block and the visible force arrows for the horizontal motion demo."""
        canvas.delete('all')
        canvas.create_text(10, 10, anchor='nw', text=f"a={((F+F_fric)/m):.2f} m/s^2   v={v:.2f} m/s   μ={friction_mu.get():.2f}")
        canvas.create_line(0, 220, 880, 220, fill='sienna')
        xpix = max(20, min(720, pos['x']))
        canvas.create_rectangle(xpix, 150, xpix+80, 190, fill='gray')
        canvas.create_text(xpix+40, 170, text=f"m={m:.2f} kg", fill='white')
        midx = xpix + 40

        if show_forces.get() and abs(F) > 1e-6:
            length = max(20, min(160, abs(F)*3))
            arrow_y = 130
            if F > 0:
                canvas.create_line(midx, arrow_y, midx+length, arrow_y, arrow='last', width=3, fill='blue')
                canvas.create_text(midx+length+30, arrow_y, text=f"F={F:.2f} N")
            else:
                canvas.create_line(midx, arrow_y, midx-length, arrow_y, arrow='first', width=3, fill='blue')
                canvas.create_text(midx-length-30, arrow_y, text=f"F={F:.2f} N")

        if show_friction.get() and friction_on.get() and abs(F_fric) > 1e-6:
            length = max(20, min(140, abs(F_fric)*3))
            arrow_y = 210
            if F_fric > 0:
                canvas.create_line(midx, arrow_y, midx+length, arrow_y, arrow='last', width=2, fill='brown')
            else:
                canvas.create_line(midx, arrow_y, midx-length, arrow_y, arrow='first', width=2, fill='brown')
            canvas.create_text(midx, arrow_y+15, text=f"F_fric={F_fric:.2f} N")

        if show_weight.get():
            wx = xpix - 40
            canvas.create_line(wx, 130, wx, 190, arrow='last', fill='black', width=2)
            canvas.create_text(wx-10, 120, text=f"W={m*9.81:.2f} N")
        if show_normal.get():
            nx = xpix + 120
            canvas.create_line(nx, 190, nx, 130, arrow='last', fill='green', width=2)
            canvas.create_text(nx+10, 120, text=f"N={m*9.81:.2f} N")

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
        draw_forces(F, F_fric, m, pos['v'])
        if running['on']:
            win.after(30, advance)

    ttk.Button(frm, text='Reset', command=reset).grid(row=9, column=0, sticky='w')
    ttk.Button(frm, text='Start', command=lambda: running.update({'on': True}) or advance()).grid(row=9, column=1)
    ttk.Button(frm, text='Stop', command=lambda: running.update({'on': False})).grid(row=9, column=2, sticky='e')
    ttk.Button(frm, text='Open push-up incline demo', command=lambda: open_push_up_incline_window(win)).grid(row=10, column=0, columnspan=3, pady=4)
    ttk.Button(frm, text='Open slide-down incline demo', command=lambda: open_slide_down_incline_window(win)).grid(row=11, column=0, columnspan=3, pady=4)

    reset()
