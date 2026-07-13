import tkinter as tk
from tkinter import ttk
import math
#energy vis 

def open_energy_window(master=None):
    win = tk.Toplevel(master) if master else tk.Tk()
    win.title("Work, Energy & Power — Mass-Spring Demo")
    win.geometry("800x360")

    # Header and description
    header = ttk.Frame(win)
    header.pack(fill=tk.X)
    ttk.Label(header, text="Work, Energy & Power — Mass-Spring Demo", font=(None, 16, 'bold')).pack(anchor='n')
    ttk.Label(header, text="Animated mass-spring system showing kinetic and potential energies (in joules) over time.", wraplength=780).pack(anchor='n')

    frm = ttk.Frame(win, padding=8)
    frm.pack(fill=tk.BOTH, expand=True)

    mass = tk.DoubleVar(value=1.0)
    k = tk.DoubleVar(value=50.0)
    x0 = tk.DoubleVar(value=0.5)

    control = ttk.Frame(frm)
    control.pack(fill=tk.X)
    ttk.Label(control, text='Mass (kg)').pack(side=tk.LEFT)
    ttk.Scale(control, from_=0.1, to=10, variable=mass, orient=tk.HORIZONTAL).pack(side=tk.LEFT, fill=tk.X, expand=True)
    ttk.Label(control, textvariable=mass).pack(side=tk.LEFT, padx=8)

    ttk.Label(control, text='k (N/m)').pack(side=tk.LEFT, padx=(10,0))
    ttk.Scale(control, from_=1, to=500, variable=k, orient=tk.HORIZONTAL).pack(side=tk.LEFT, fill=tk.X, expand=True)
    ttk.Label(control, textvariable=k).pack(side=tk.LEFT, padx=8)

    canvas = tk.Canvas(frm, bg='white', height=220)
    canvas.pack(fill=tk.BOTH, expand=True, pady=8)

    graph = tk.Canvas(frm, bg='white', height=100)
    graph.pack(fill=tk.BOTH)

    state = {'x': x0.get(), 'v': 0.0}
    energy_history = {'ke': [], 'pe': [], 't': []}

    def reset():
        state['x'] = x0.get()
        state['v'] = 0.0
        energy_history['ke'].clear(); energy_history['pe'].clear(); energy_history['t'].clear()

    def step():
        m = mass.get(); kk = k.get()
        # spring attached at left wall x=50, equilibrium at x=150 (pixels->meters mapping)
        dt = 0.02
        # simple hooke's law with rest at x=0
        a = - (kk/m) * state['x']
        state['v'] += a * dt
        state['x'] += state['v'] * dt

        # draw spring-mass
        canvas.delete('all')
        cx = 80
        xpix = cx + state['x']*120  # convert m to pixels
        canvas.create_line(50,110, xpix-30, 110, fill='black', width=2)
        canvas.create_rectangle(xpix-20, 90, xpix+40, 130, fill='steelblue')
        canvas.create_text(10, 10, anchor='nw', text=f"x={state['x']:.2f} m  v={state['v']:.2f} m/s  a={a:.2f} m/s^2")

        # energies
        ke = 0.5 * m * state['v']**2
        pe = 0.5 * kk * state['x']**2
        energy_history['ke'].append(ke)
        energy_history['pe'].append(pe)
        energy_history['t'].append(len(energy_history['t'])*dt if energy_history['t'] else 0.0)

        draw_energy_graph()
        win.after(int(dt*1000), step)

    def draw_energy_graph():
        graph.delete('all')
        ke = energy_history['ke']; pe = energy_history['pe']; t = energy_history['t']
        if not t:
            return
        w = int(graph.winfo_width() or graph['width'])
        h = int(graph.winfo_height() or graph['height'])
        pad = 6
        tmax = max(0.1, t[-1])
        vmax = max(max(ke) if ke else 1, max(pe) if pe else 1)
        # draw axes with metric ticks
        graph.create_line(pad, h-pad, w-pad, h-pad, fill='black')
        graph.create_line(pad, pad, pad, h-pad, fill='black')
        # y ticks and labels (energy in J)
        for i in range(5):
            yy = pad + i*(h-2*pad)/4
            val = vmax - (i*(vmax/4))
            graph.create_line(pad-5, int(yy), pad, int(yy), fill='black')
            graph.create_text(pad-30, int(yy), text=f"{val:.2f}")
        # plot curves
        for arr, color in ((ke,'blue'), (pe,'orange')):
            for i in range(1, len(arr)):
                x1 = int(pad + (t[i-1]/tmax)*(w-2*pad))
                x2 = int(pad + (t[i]/tmax)*(w-2*pad))
                y1 = int(h-pad - (arr[i-1]/vmax)*(h-2*pad))
                y2 = int(h-pad - (arr[i]/vmax)*(h-2*pad))
                graph.create_line(x1,y1,x2,y2, fill=color)
        graph.create_text(10,10, anchor='nw', text='KE (blue)  PE (orange)')
        graph.create_text(pad-20, h//2, text='Energy (J)', angle=90)
        graph.create_text(w//2, h-pad+12, text='time (s)')

    ttk.Button(frm, text='Reset', command=reset).pack(side=tk.LEFT, padx=6)
    ttk.Button(frm, text='Start', command=step).pack(side=tk.LEFT)

    reset()
