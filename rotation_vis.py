import tkinter as tk
from tkinter import ttk
import math


def open_rotation_window(master=None):
    win = tk.Toplevel(master) if master else tk.Tk()
    win.title("Rotational Motion — Spinning Disk")
    win.geometry("700x420")

    frm = ttk.Frame(win, padding=8)
    frm.pack(fill=tk.BOTH, expand=True)

    mass = tk.DoubleVar(value=2.0)
    radius = tk.DoubleVar(value=0.5)
    torque = tk.DoubleVar(value=1.0)

    ttk.Label(frm, text="Mass (kg)").grid(row=0, column=0, sticky='w')
    ttk.Scale(frm, from_=0.1, to=20, variable=mass, orient=tk.HORIZONTAL).grid(row=0, column=1, sticky='we')
    ttk.Label(frm, textvariable=mass).grid(row=0, column=2)

    ttk.Label(frm, text="Radius (m)").grid(row=1, column=0, sticky='w')
    ttk.Scale(frm, from_=0.05, to=2, variable=radius, orient=tk.HORIZONTAL).grid(row=1, column=1, sticky='we')
    ttk.Label(frm, textvariable=radius).grid(row=1, column=2)

    ttk.Label(frm, text="Applied torque (N·m)").grid(row=2, column=0, sticky='w')
    ttk.Scale(frm, from_=-10, to=10, variable=torque, orient=tk.HORIZONTAL).grid(row=2, column=1, sticky='we')
    ttk.Label(frm, textvariable=torque).grid(row=2, column=2)

    canvas = tk.Canvas(frm, bg='white', height=300)
    canvas.grid(row=3, column=0, columnspan=3, pady=8)
    frm.columnconfigure(1, weight=1)

    state = {'omega': 0.0, 'theta': 0.0, 't': 0.0}

    energy_hist = {'rot': [], 't': []}

    def step():
        m = mass.get(); r = radius.get(); tau = torque.get()
        I = 0.5 * m * r * r  # solid disk
        alpha = tau / I if I != 0 else 0.0
        dt = 0.03
        state['omega'] += alpha * dt
        state['theta'] += state['omega'] * dt
        state['t'] += dt

        # rotational KE = 1/2 I ω^2, angular momentum L = I ω
        rot_ke = 0.5 * I * state['omega']**2
        energy_hist['rot'].append(rot_ke)
        energy_hist['t'].append(state['t'])

        canvas.delete('all')
        cx, cy = 350, 150
        pix_r = max(10, min(140, int(r * 100)))
        canvas.create_oval(cx-pix_r, cy-pix_r, cx+pix_r, cy+pix_r, outline='black', fill='lightgray')
        # draw a radius marker
        x = cx + pix_r * math.cos(state['theta'])
        y = cy + pix_r * math.sin(state['theta'])
        canvas.create_line(cx, cy, x, y, width=3, fill='red')
        # show torque arrow
        canvas.create_line(cx+pix_r+20, cy, cx+pix_r+80, cy, arrow='last', fill='purple', width=3)
        canvas.create_text(10, 10, anchor='nw', text=f"ω={state['omega']:.2f} rad/s  α={alpha:.2f} rad/s²  I={I:.2f} kg·m²  L={I*state['omega']:.2f}")

        # small energy plot
        gx, gy = 10, 300
        gw, gh = 300, 80
        # draw border
        canvas.create_rectangle(gx, gy, gx+gw, gy+gh, outline='black')
        if energy_hist['t']:
            tmax = max(0.1, energy_hist['t'][-1])
            vmax = max(energy_hist['rot']) if energy_hist['rot'] else 1
            for i in range(1, len(energy_hist['rot'])):
                x1 = gx + int((energy_hist['t'][i-1]/tmax)*(gw))
                x2 = gx + int((energy_hist['t'][i]/tmax)*(gw))
                y1 = gy+gh - int((energy_hist['rot'][i-1]/vmax)*gh)
                y2 = gy+gh - int((energy_hist['rot'][i]/vmax)*gh)
                canvas.create_line(x1,y1,x2,y2, fill='blue')

        win.after(int(dt*1000), step)

    ttk.Button(frm, text='Start', command=step).grid(row=4, column=0, sticky='w')
    ttk.Button(frm, text='Reset', command=lambda: state.update({'omega': 0.0, 'theta': 0.0, 't': 0.0}) or energy_hist['rot'].clear() or energy_hist['t'].clear()).grid(row=4, column=1)

    step()
