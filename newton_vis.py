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
    _bind_display(mass, mass_display)
    _bind_display(force, force_display)

    ttk.Label(frm, text="Mass (kg)").grid(row=0, column=0, sticky='w')
    ttk.Scale(frm, from_=0.1, to=20, variable=mass, orient=tk.HORIZONTAL).grid(row=0, column=1, sticky='we')
    ttk.Label(frm, textvariable=mass_display).grid(row=0, column=2)

    ttk.Label(frm, text="Applied force (N)").grid(row=1, column=0, sticky='w')
    ttk.Scale(frm, from_=-50, to=50, variable=force, orient=tk.HORIZONTAL).grid(row=1, column=1, sticky='we')
    ttk.Label(frm, textvariable=force_display).grid(row=1, column=2)

    ttk.Checkbutton(frm, text="Include kinetic friction (μ=0.3)", variable=friction_on).grid(row=2, column=0, columnspan=3, sticky='w')
    ttk.Checkbutton(frm, text="Show force vectors", variable=show_forces).grid(row=3, column=0, columnspan=3, sticky='w')
    ttk.Checkbutton(frm, text="Show weight", variable=show_weight).grid(row=4, column=0, columnspan=3, sticky='w')
    ttk.Checkbutton(frm, text="Show normal force", variable=show_normal).grid(row=5, column=0, columnspan=3, sticky='w')

    canvas = tk.Canvas(frm, bg='white', height=200)
    canvas.grid(row=6, column=0, columnspan=3, sticky='nsew', pady=8)
    frm.columnconfigure(1, weight=1)

    pos = {'x': 50.0, 'v': 0.0}

    def reset():
        pos['x'] = 50.0
        pos['v'] = 0.0

    def draw_forces(F, F_fric, m, v):
        canvas.delete('all')
        # ground
        canvas.create_line(0, 180, 880, 180, fill='sienna')
        # cart
        xpix = max(10, min(700, pos['x']))
        canvas.create_rectangle(xpix, 120, xpix+80, 180, fill='gray')

        # draw applied force arrow
        midx = xpix + 40
        if show_forces.get():
            if abs(F) > 1e-6:
                length = max(20, min(160, abs(F)*3))
                if F > 0:
                    canvas.create_line(midx, 140, midx+length, 140, arrow='last', width=3, fill='blue')
                    canvas.create_text(midx+length+30, 140, text=f"F={F:.2f} N")
                else:
                    canvas.create_line(midx, 140, midx-length, 140, arrow='first', width=3, fill='blue')
                    canvas.create_text(midx-length-30, 140, text=f"F={F:.2f} N")

            # friction
            if abs(F_fric) > 1e-6:
                length = max(10, min(140, abs(F_fric)*3))
                if F_fric > 0:
                    canvas.create_line(midx, 150, midx+length, 150, arrow='last', width=2, fill='brown')
                else:
                    canvas.create_line(midx, 150, midx-length, 150, arrow='first', width=2, fill='brown')
                canvas.create_text(midx, 110, text=f"F_fric={F_fric:.2f} N")

        # weight and normal
        if show_weight.get():
            canvas.create_line(midx-60, 90, midx-60, 140, arrow='last', fill='black')
            canvas.create_text(midx-60, 80, text=f"W={m*9.81:.2f} N")
        if show_normal.get():
            canvas.create_line(midx+60, 140, midx+60, 90, arrow='last', fill='green')
            canvas.create_text(midx+60, 80, text=f"N={m*9.81:.2f} N")

        canvas.create_text(10, 10, anchor='nw', text=f"a={((F+F_fric)/m):.2f} m/s^2  v={v:.2f} m/s")

    def step():
        m = mass.get()
        F = force.get()
        mu = 0.3 if friction_on.get() else 0.0
        g = 9.81
        # friction model: kinetic friction opposing motion or applied force
        if abs(pos['v']) > 1e-3:
            F_fric = -mu * m * g * (1 if pos['v'] > 0 else -1)
        else:
            # static friction threshold approximation
            F_fric = -mu * m * g * (1 if F > 0 else -1) if abs(F) > mu*m*g else 0
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
