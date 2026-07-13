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
    ttk.Scale(frm, from_=0, to=45, variable=incline_angle, orient=tk.HORIZONTAL).grid(row=4, column=1, sticky='we')
    ttk.Label(frm, textvariable=angle_display).grid(row=4, column=2)

    ttk.Checkbutton(frm, text="Show force vectors", variable=show_forces).grid(row=5, column=0, columnspan=3, sticky='w')
    ttk.Checkbutton(frm, text="Show weight", variable=show_weight).grid(row=6, column=0, columnspan=3, sticky='w')
    ttk.Checkbutton(frm, text="Show normal force", variable=show_normal).grid(row=7, column=0, columnspan=3, sticky='w')
    ttk.Checkbutton(frm, text="Show friction force", variable=show_friction).grid(row=8, column=0, columnspan=3, sticky='w')

    canvas = tk.Canvas(frm, bg='white', height=280)
    canvas.grid(row=9, column=0, columnspan=3, sticky='nsew', pady=8)
    frm.columnconfigure(1, weight=1)

    state = {'s': 0.0, 'v': 0.0}
    running = {'on': False}

    def reset():
        state['s'] = 0.0
        state['v'] = 0.0
        running['on'] = False
        draw_plot(0, 0, 0, 0)

    def draw_plot(ax=0, ay=0, an=0, af=0):
        canvas.delete('all')
        angle = math.radians(incline_angle.get())
        base_y = 240
        base_x = 100
        length = 520
        x2 = base_x + length * math.cos(angle)
        y2 = base_y - length * math.sin(angle)
        canvas.create_line(base_x, base_y, x2, y2, fill='sienna', width=4)
        canvas.create_line(base_x, base_y, x2, base_y, fill='black', dash=(4, 2))

        block_x = base_x + state['s'] * 8 * math.cos(angle)
        block_y = base_y - state['s'] * 8 * math.sin(angle)
        block_w = 50
        block_h = 30
        dx = block_w * math.cos(angle)
        dy = block_w * math.sin(angle)
        tx = block_h * math.sin(angle)
        ty = block_h * math.cos(angle)
        p1 = (block_x - dx/2 + ty/2, block_y - dy/2 - tx/2)
        p2 = (block_x + dx/2 + ty/2, block_y + dy/2 - tx/2)
        p3 = (block_x + dx/2 - ty/2, block_y + dy/2 + tx/2)
        p4 = (block_x - dx/2 - ty/2, block_y - dy/2 + tx/2)
        canvas.create_polygon(p1, p2, p3, p4, fill='gray')
        canvas.create_text(block_x, block_y, text=f"m={mass.get():.2f} kg", fill='white')

        if show_weight.get():
            wx, wy = block_x, block_y
            wy2 = wy + 80
            canvas.create_line(wx, wy, wx, wy2, arrow='last', fill='black', width=2)
            canvas.create_text(wx-25, wy2+10, text=f"W={mass.get()*9.81:.2f} N")
        if show_normal.get():
            nx = block_x - math.sin(angle) * 50 - 20
            ny = block_y - math.cos(angle) * 50 + 10
            nx2 = nx + math.sin(angle) * 60
            ny2 = ny - math.cos(angle) * 60
            canvas.create_line(nx, ny, nx2, ny2, arrow='last', fill='green', width=2)
            canvas.create_text(nx2+10, ny2-10, text=f"N={mass.get()*9.81*math.cos(angle):.2f} N")
        if show_friction.get() and friction_on.get():
            fg = friction_mu.get() * mass.get() * 9.81 * math.cos(angle)
            direction = -1 if state['v'] > 0 else 1
            if abs(state['v']) < 1e-3 and ax < 0:
                direction = 1
            fx = block_x + direction * math.cos(angle) * 70
            fy = block_y + direction * math.sin(angle) * 70
            fx2 = fx - direction * math.sin(angle) * 50
            fy2 = fy + direction * math.cos(angle) * 50
            canvas.create_line(fx, fy, fx2, fy2, arrow='last', fill='brown', width=2)
            canvas.create_text(fx2-10, fy2+10, text=f"F_fric={fg:.2f} N")
        if show_forces.get():
            frx = block_x + math.cos(angle) * 70
            fry = block_y + math.sin(angle) * 70
            canvas.create_line(block_x, block_y, frx, fry, arrow='last', fill='blue', width=3)
            canvas.create_text(frx+15, fry+15, text=f"F={force.get():.2f} N")

        canvas.create_text(10, 10, anchor='nw', text=f"vx={state['v']:.2f} m/s   s={state['s']:.2f} m   θ={incline_angle.get():.2f}°")

    def advance():
        m = mass.get()
        F = force.get()
        angle = math.radians(incline_angle.get())
        g = 9.81
        N = m * g * math.cos(angle)
        g_par = m * g * math.sin(angle)
        mu = friction_mu.get() if friction_on.get() else 0.0
        friction_mag = mu * N
        direction = -1 if state['v'] > 0 else 1
        if abs(state['v']) < 1e-3 and abs(F - g_par) < friction_mag:
            a = 0.0
        else:
            friction = -direction * friction_mag if friction_on.get() else 0.0
            if direction * (F - g_par) < 0:
                friction = -direction * friction_mag
            a = (F - g_par + friction) / m
        state['v'] += a * 0.03
        state['s'] += state['v'] * 0.03
        if state['s'] < 0:
            state['s'] = 0
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
