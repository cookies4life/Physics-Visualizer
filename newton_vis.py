import tkinter as tk
from tkinter import ttk
import math


def open_incline_window(master=None):
    win = tk.Toplevel(master) if master else tk.Tk()
    win.title("Newton's Laws — Incline Plane Simulation")
    win.geometry("900x500")

    header = ttk.Frame(win)
    header.pack(fill=tk.X)
    ttk.Label(header, text="Incline Plane Simulation", font=(None, 16, 'bold')).pack(anchor='n')
    ttk.Label(header, text="Separate incline plane simulation with replicated toggle controls and a moving block on the slope.", wraplength=880).pack(anchor='n')

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

    canvas = tk.Canvas(frm, bg='white', height=480)
    canvas.grid(row=9, column=0, columnspan=3, sticky='nsew', pady=8)
    frm.columnconfigure(1, weight=1)

    state = {'s': 0.0, 'v': 0.0, 'top': (0, 0), 'force_handle': (0, 0)}
    running = {'on': False}
    dragging = {'mode': None}

    def on_canvas_press(event):
        top_x, top_y = state['top']
        fx, fy = state['force_handle']
        if (event.x - fx) ** 2 + (event.y - fy) ** 2 <= 16 ** 2:
            dragging['mode'] = 'force'
            return
        if (event.x - top_x) ** 2 + (event.y - top_y) ** 2 <= 16 ** 2:
            dragging['mode'] = 'ramp'
            return
        dragging['mode'] = None

    def on_canvas_release(event):
        dragging['mode'] = None

    def on_canvas_drag(event):
        if dragging['mode'] is None:
            return
        base_x = 100
        base_y = 280
        if dragging['mode'] == 'ramp':
            dx = event.x - base_x
            dy = base_y - event.y
            if abs(dx) < 20:
                dx = 20 if dx >= 0 else -20
            angle_rad = math.atan2(dy, dx)
            angle_deg = max(-45.0, min(45.0, math.degrees(angle_rad)))
            incline_angle.set(angle_deg)
            draw_plot(0, 0, 0, 0)
        else:
            angle = math.radians(incline_angle.get())
            length = 280
            x2 = base_x + length * math.cos(angle)
            y2 = base_y - length * math.sin(angle)
            top_x, top_y, bottom_x, bottom_y = (x2, y2, base_x, base_y) if y2 < base_y else (base_x, base_y, x2, y2)
            dx = bottom_x - top_x
            dy = bottom_y - top_y
            incline_length = math.hypot(dx, dy)
            dir_x = dx / incline_length
            dir_y = dy / incline_length
            # Project drag onto incline direction for force value
            center_x = top_x + state['s'] * dir_x
            center_y = top_y + state['s'] * dir_y
            proj = (event.x - center_x) * dir_x + (event.y - center_y) * dir_y
            force.set(max(-50.0, min(50.0, proj * 0.5)))
            draw_plot(0, 0, 0, 0)

    canvas.bind('<ButtonPress-1>', on_canvas_press)
    canvas.bind('<ButtonRelease-1>', on_canvas_release)
    canvas.bind('<B1-Motion>', on_canvas_drag)

    def reset():
        state['s'] = 0.0
        state['v'] = 0.0
        running['on'] = False
        draw_plot(0, 0, 0, 0)

    def draw_plot(ax=0, ay=0, an=0, af=0):
        canvas.delete('all')
        angle = math.radians(incline_angle.get())
        base_y = 280
        base_x = 100
        length = 280
        x2 = base_x + length * math.cos(angle)
        y2 = base_y - length * math.sin(angle)
        canvas.create_line(base_x, base_y, x2, y2, fill='sienna', width=4)
        canvas.create_line(base_x, base_y, x2, base_y, fill='black', dash=(4, 2))

        top_x, top_y, bottom_x, bottom_y = (x2, y2, base_x, base_y) if y2 < base_y else (base_x, base_y, x2, y2)
        canvas.create_oval(top_x-10, top_y-10, top_x+10, top_y+10, fill='blue', outline='black')
        canvas.create_text(top_x+20, top_y-10, text='Drag handle', anchor='w', fill='black', font=(None, 8))
        state['top'] = (top_x, top_y)

        dx = bottom_x - top_x
        dy = bottom_y - top_y
        incline_length = math.hypot(dx, dy)
        dir_x = dx / incline_length
        dir_y = dy / incline_length
        normal_x = -dir_y
        normal_y = dir_x

        block_x = top_x + state['s'] * dir_x
        block_y = top_y + state['s'] * dir_y
        box_w = 120
        box_h = 70
        box_cx = block_x + normal_x * (box_h / 2 + 6)
        box_cy = block_y + normal_y * (box_h / 2 + 6)
        canvas.create_rectangle(
            box_cx - box_w / 2,
            box_cy - box_h / 2,
            box_cx + box_w / 2,
            box_cy + box_h / 2,
            fill='gray', outline='black')
        canvas.create_text(box_cx, box_cy, text=f"m={mass.get():.2f} kg", fill='white')

        g_val = 9.81
        g_par = mass.get() * g_val * abs(math.sin(angle))
        g_perp = mass.get() * g_val * math.cos(abs(angle))

        if show_weight.get():
            wx = box_cx
            wy = box_cy
            canvas.create_line(wx, wy, wx, wy + 100, arrow='last', fill='black', width=2)
            canvas.create_text(wx - 25, wy + 110, text=f"W={mass.get()*g_val:.2f} N")

        if show_normal.get():
            nx = box_cx + normal_x * 80
            ny = box_cy + normal_y * 80
            canvas.create_line(box_cx, box_cy, nx, ny, arrow='last', fill='green', width=2)
            canvas.create_text(nx + 10, ny - 5, text=f"mg cosθ={g_perp:.2f} N")

        if show_friction.get() and friction_on.get():
            friction_mag = friction_mu.get() * g_perp
            direction = -1 if state['v'] > 0 else 1
            if abs(state['v']) < 1e-3 and ax < 0:
                direction = 1
            fx = box_cx + direction * dir_x * 90
            fy = box_cy + direction * dir_y * 90
            fx2 = fx - direction * normal_x * 60
            fy2 = fy - direction * normal_y * 60
            canvas.create_line(fx, fy, fx2, fy2, arrow='last', fill='brown', width=2)
            canvas.create_text(fx2 - 10, fy2 + 10, text=f"F_fric={friction_mag:.2f} N")

        frx = box_cx + dir_x * 110
        fry = box_cy + dir_y * 110
        state['force_handle'] = (frx, fry)
        if show_forces.get():
            canvas.create_line(box_cx, box_cy, frx, fry, arrow='last', fill='blue', width=3)
            canvas.create_text(frx + 15, fry + 15, text=f"F={force.get():.2f} N")
        canvas.create_oval(frx-8, fry-8, frx+8, fry+8, fill='lightblue', outline='black')
        canvas.create_text(frx+15, fry+8, text='Drag F', anchor='w', fill='black', font=(None, 8))

        cgx = box_cx + dir_x * 80
        cgy = box_cy + dir_y * 80
        canvas.create_line(box_cx, box_cy, cgx, cgy, arrow='last', fill='orange', width=2)
        canvas.create_text(cgx + 10, cgy + 10, text=f"mg sinθ={g_par:.2f} N", fill='orange')

        canvas.create_text(10, 10, anchor='nw', text=f"vx={state['v']:.2f} m/s   s={state['s']:.2f} m   θ={incline_angle.get():.2f}°")

    def advance():
        m = mass.get()
        F = force.get()
        angle = math.radians(incline_angle.get())
        g = 9.81
        g_par = m * g * abs(math.sin(angle))
        N = m * g * math.cos(abs(angle))
        mu = friction_mu.get() if friction_on.get() else 0.0
        friction_mag = mu * N
        net_force_down = F + g_par
        if abs(state['v']) < 1e-3 and abs(net_force_down) < friction_mag:
            a = 0.0
            friction = 0.0
        else:
            direction = math.copysign(1.0, state['v']) if abs(state['v']) > 1e-3 else math.copysign(1.0, net_force_down)
            friction = -direction * friction_mag if friction_on.get() else 0.0
            a = (net_force_down + friction) / m
        state['v'] += a * 0.03
        state['s'] += state['v'] * 0.03
        max_s = 280 / 8 + 4
        min_s = -4
        if state['s'] < min_s:
            state['s'] = min_s
            state['v'] = 0
        elif state['s'] > max_s:
            state['s'] = max_s
            state['v'] = 0
        draw_plot(a, g_par, N, friction_mag)
        if running['on']:
            win.after(30, advance)

    ttk.Button(frm, text='Reset', command=reset).grid(row=10, column=0, sticky='w')
    ttk.Button(frm, text='Start', command=lambda: running.update({'on': True}) or advance()).grid(row=10, column=1)
    ttk.Button(frm, text='Stop', command=lambda: running.update({'on': False})).grid(row=10, column=2, sticky='e')

    reset()


def open_newton_window(master=None):
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

    pos = {'x': 50.0, 'v': 0.0}
    running = {'on': False}

    def reset():
        pos['x'] = 50.0
        pos['v'] = 0.0
        running['on'] = False
        draw_forces(0, 0, mass.get(), 0)

    def draw_forces(F, F_fric, m, v):
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
    ttk.Button(frm, text='Open incline simulation', command=lambda: open_incline_window(win)).grid(row=10, column=0, columnspan=3, pady=8)

    reset()
