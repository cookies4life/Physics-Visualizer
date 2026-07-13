import tkinter as tk
from tkinter import ttk
import math


def open_newton_window(master=None):
    win = tk.Toplevel(master) if master else tk.Tk()
    win.title("Newton's Laws — Force Visualizer")
    win.geometry("900x380")

    # Header and description
    header = ttk.Frame(win)
    header.pack(fill=tk.X)
    ttk.Label(header, text="Newton's Laws — Force Visualizer", font=(None, 16, 'bold')).pack(anchor='n')
    ttk.Label(header, text="Interactive demonstration of forces on a block: applied force, friction, weight and normal force. Toggle force vectors and friction.", wraplength=880).pack(anchor='n')

    frm = ttk.Frame(win, padding=8)
    frm.pack(fill=tk.BOTH, expand=True)

    mass = tk.DoubleVar(value=2.0)
    force = tk.DoubleVar(value=5.0)
    friction_on = tk.BooleanVar(value=False)
    friction_mu = tk.DoubleVar(value=0.30)
    incline_on = tk.BooleanVar(value=False)
    incline_angle = tk.DoubleVar(value=20.0)
    show_forces = tk.BooleanVar(value=True)
    show_weight = tk.BooleanVar(value=True)
    show_normal = tk.BooleanVar(value=True)

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

    ttk.Label(frm, text="Applied force (N)").grid(row=1, column=0, sticky='w')
    ttk.Scale(frm, from_=-50, to=50, variable=force, orient=tk.HORIZONTAL).grid(row=1, column=1, sticky='we')
    ttk.Label(frm, textvariable=force_display).grid(row=1, column=2)

    ttk.Checkbutton(frm, text="Include kinetic friction", variable=friction_on).grid(row=2, column=0, columnspan=3, sticky='w')
    ttk.Label(frm, text="Friction coefficient μ").grid(row=3, column=0, sticky='w')
    ttk.Scale(frm, from_=0.0, to=1.0, variable=friction_mu, orient=tk.HORIZONTAL).grid(row=3, column=1, sticky='we')
    ttk.Label(frm, textvariable=mu_display).grid(row=3, column=2)

    ttk.Checkbutton(frm, text="Show incline plane", variable=incline_on).grid(row=4, column=0, columnspan=3, sticky='w')
    ttk.Label(frm, text="Incline angle (deg)").grid(row=5, column=0, sticky='w')
    ttk.Scale(frm, from_=0, to=45, variable=incline_angle, orient=tk.HORIZONTAL).grid(row=5, column=1, sticky='we')
    ttk.Label(frm, textvariable=angle_display).grid(row=5, column=2)

    ttk.Checkbutton(frm, text="Show force vectors", variable=show_forces).grid(row=6, column=0, columnspan=3, sticky='w')
    ttk.Checkbutton(frm, text="Show weight", variable=show_weight).grid(row=7, column=0, columnspan=3, sticky='w')
    ttk.Checkbutton(frm, text="Show normal force", variable=show_normal).grid(row=8, column=0, columnspan=3, sticky='w')

    canvas = tk.Canvas(frm, bg='white', height=240)
    canvas.grid(row=10, column=0, columnspan=3, sticky='nsew', pady=8)
    frm.columnconfigure(1, weight=1)

    pos = {'x': 50.0, 'v': 0.0}

    def reset():
        pos['x'] = 50.0
        pos['v'] = 0.0

    def draw_forces(F, F_fric, m, v):
        canvas.delete('all')
        canvas.create_text(10, 10, anchor='nw', text=f"a={((F+F_fric)/m):.2f} m/s^2   v={v:.2f} m/s   μ={friction_mu.get():.2f}")
        if incline_on.get():
            # incline plane mode
            angle = math.radians(incline_angle.get())
            base_y = 220
            base_x = 80
            length = 400
            # draw incline plane
            x2 = base_x + length * math.cos(angle)
            y2 = base_y - length * math.sin(angle)
            canvas.create_line(base_x, base_y, x2, y2, fill='sienna', width=3)
            canvas.create_line(base_x, base_y, x2, base_y, fill='black', dash=(4,2))

            # block on incline
            block_center = (base_x + 120 * math.cos(angle), base_y - 120 * math.sin(angle))
            block_w = 40
            block_h = 30
            # block rotated approximation using a simple polygon
            dx = block_w * math.cos(angle)
            dy = block_w * math.sin(angle)
            tx = block_h * math.sin(angle)
            ty = block_h * math.cos(angle)
            p1 = (block_center[0] - dx/2 + ty/2, block_center[1] - dy/2 - tx/2)
            p2 = (block_center[0] + dx/2 + ty/2, block_center[1] + dy/2 - tx/2)
            p3 = (block_center[0] + dx/2 - ty/2, block_center[1] + dy/2 + tx/2)
            p4 = (block_center[0] - dx/2 - ty/2, block_center[1] - dy/2 + tx/2)
            canvas.create_polygon(p1, p2, p3, p4, fill='gray')
            canvas.create_text(block_center[0], block_center[1], text=f"m={m:.2f} kg", fill='white')

            # forces on incline
            if show_weight.get():
                wx, wy = block_center
                wy2 = wy + 60
                canvas.create_line(wx, wy, wx, wy2, arrow='last', fill='black', width=2)
                canvas.create_text(wx-20, wy2+10, text=f"W={m*9.81:.2f} N")
            if show_normal.get():
                nx = block_center[0] - math.sin(angle) * 50
                ny = block_center[1] - math.cos(angle) * 50
                nx2 = nx + math.sin(angle) * 40
                ny2 = ny - math.cos(angle) * 40
                canvas.create_line(nx, ny, nx2, ny2, arrow='last', fill='green', width=2)
                canvas.create_text(nx2+10, ny2-10, text=f"N={((m*9.81)*math.cos(angle)):.2f} N")
            if friction_on.get() and abs(F_fric) > 1e-6:
                fx = block_center[0] + math.cos(angle) * 50 * (1 if F_fric < 0 else -1)
                fy = block_center[1] + math.sin(angle) * 50 * (1 if F_fric < 0 else -1)
                fx2 = fx - math.sin(angle) * 40 * (1 if F_fric < 0 else -1)
                fy2 = fy + math.cos(angle) * 40 * (1 if F_fric < 0 else -1)
                canvas.create_line(fx, fy, fx2, fy2, arrow='last', fill='brown', width=2)
                canvas.create_text(fx2-10, fy2+10, text=f"F_fric={F_fric:.2f} N")
            return

        # horizontal cart mode
        # ground
        canvas.create_line(0, 220, 880, 220, fill='sienna')
        # cart
        xpix = max(10, min(700, pos['x']))
        canvas.create_rectangle(xpix, 140, xpix+80, 190, fill='gray')
        canvas.create_text(xpix+40, 165, text=f"m={m:.2f} kg", fill='white')
        midx = xpix + 40
        if show_forces.get():
            if abs(F) > 1e-6:
                length = max(20, min(160, abs(F)*3))
                if F > 0:
                    canvas.create_line(midx, 165, midx+length, 165, arrow='last', width=3, fill='blue')
                    canvas.create_text(midx+length+30, 165, text=f"F={F:.2f} N")
                else:
                    canvas.create_line(midx, 165, midx-length, 165, arrow='first', width=3, fill='blue')
                    canvas.create_text(midx-length-30, 165, text=f"F={F:.2f} N")

            if friction_on.get() and abs(F_fric) > 1e-6:
                length = max(10, min(140, abs(F_fric)*3))
                if F_fric > 0:
                    canvas.create_line(midx, 180, midx+length, 180, arrow='last', width=2, fill='brown')
                else:
                    canvas.create_line(midx, 180, midx-length, 180, arrow='first', width=2, fill='brown')
                canvas.create_text(midx, 130, text=f"F_fric={F_fric:.2f} N")

        if show_weight.get():
            canvas.create_line(midx-80, 110, midx-80, 160, arrow='last', fill='black')
            canvas.create_text(midx-90, 105, text=f"W={m*9.81:.2f} N")
        if show_normal.get():
            canvas.create_line(midx+80, 160, midx+80, 110, arrow='last', fill='green')
            canvas.create_text(midx+90, 105, text=f"N={m*9.81:.2f} N")

    def step():
        m = mass.get()
        F = force.get()
        mu = friction_mu.get() if friction_on.get() else 0.0
        g = 9.81
        if incline_on.get():
            angle = math.radians(incline_angle.get())
            # component of gravity along incline
            g_parallel = g * math.sin(angle)
            g_perp = g * math.cos(angle)
            weight_along = m * g_parallel
            F_fric = -mu * m * g_perp * (1 if (pos['v'] > 0) else -1) if abs(pos['v']) > 1e-3 else -mu * m * g_perp * (1 if F < 0 else -1) if abs(F) > mu*m*g_perp else 0
            F_net = F - weight_along + F_fric
        else:
            F_fric = -mu * m * g * (1 if pos['v'] > 0 else -1) if abs(pos['v']) > 1e-3 else -mu * m * g * (1 if F > 0 else -1) if abs(F) > mu*m*g else 0
            F_net = F + F_fric
        a = F_net / m

        dt = 0.03
        pos['v'] += a * dt
        pos['x'] += pos['v'] * dt

        draw_forces(F, F_fric, m, pos['v'])
        win.after(int(dt*1000), step)

    ttk.Button(frm, text='Reset', command=reset).grid(row=7, column=0, sticky='w')
    ttk.Button(frm, text='Start', command=step).grid(row=7, column=1)

    reset()
