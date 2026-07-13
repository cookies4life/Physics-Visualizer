import tkinter as tk
from tkinter import ttk


def open_momentum_window(master=None):
    win = tk.Toplevel(master) if master else tk.Tk()
    win.title("Momentum & Collisions — Animated 1D Collision")
    win.geometry("1000x300")

    frm = ttk.Frame(win, padding=8)
    frm.pack(fill=tk.BOTH, expand=True)

    m1 = tk.DoubleVar(value=2.0)
    v1 = tk.DoubleVar(value=10.0)
    m2 = tk.DoubleVar(value=1.0)
    v2 = tk.DoubleVar(value=-2.0)
    elastic = tk.BooleanVar(value=True)

    control = ttk.Frame(frm)
    control.pack(fill=tk.X)
    ttk.Label(control, text='m1').pack(side=tk.LEFT)
    ttk.Scale(control, from_=0.1, to=20, variable=m1, orient=tk.HORIZONTAL).pack(side=tk.LEFT, fill=tk.X, expand=True)
    ttk.Label(control, textvariable=m1).pack(side=tk.LEFT, padx=6)
    ttk.Label(control, text='v1').pack(side=tk.LEFT)
    ttk.Scale(control, from_=-50, to=50, variable=v1, orient=tk.HORIZONTAL).pack(side=tk.LEFT, fill=tk.X, expand=True)
    ttk.Label(control, textvariable=v1).pack(side=tk.LEFT, padx=6)
    ttk.Label(control, text='m2').pack(side=tk.LEFT)
    ttk.Scale(control, from_=0.1, to=20, variable=m2, orient=tk.HORIZONTAL).pack(side=tk.LEFT, fill=tk.X, expand=True)
    ttk.Label(control, textvariable=m2).pack(side=tk.LEFT, padx=6)
    ttk.Label(control, text='v2').pack(side=tk.LEFT)
    ttk.Scale(control, from_=-50, to=50, variable=v2, orient=tk.HORIZONTAL).pack(side=tk.LEFT, fill=tk.X, expand=True)
    ttk.Label(control, textvariable=v2).pack(side=tk.LEFT, padx=6)
    ttk.Checkbutton(control, text='Elastic', variable=elastic).pack(side=tk.LEFT, padx=6)

    canvas = tk.Canvas(frm, bg='white', height=160)
    canvas.pack(fill=tk.BOTH, expand=True, pady=8)

    # positions in pixels
    state = {'x1': 120.0, 'x2': 740.0, 'v1': v1.get(), 'v2': v2.get(), 'running': False}

    def compute_after_vels():
        M1 = m1.get(); V1 = state['v1']; M2 = m2.get(); V2 = state['v2']
        if elastic.get():
            u1 = (V1*(M1-M2) + 2*M2*V2) / (M1+M2)
            u2 = (V2*(M2-M1) + 2*M1*V1) / (M1+M2)
        else:
            u = (M1*V1 + M2*V2) / (M1+M2)
            u1 = u2 = u
        return u1, u2

    def reset():
        state['x1'] = 120.0
        state['x2'] = 740.0
        state['v1'] = v1.get()
        state['v2'] = v2.get()
        state['running'] = False

    def step():
        state['running'] = True
        dt = 0.02
        # update velocities and positions
        state['x1'] += state['v1'] * dt * 10
        state['x2'] += state['v2'] * dt * 10

        # detect collision (simple overlap)
        if state['x1'] + 50 >= state['x2']:
            u1, u2 = compute_after_vels()
            # convert back to pixel/sec scale
            state['v1'] = u1
            state['v2'] = u2

        # draw
        canvas.delete('all')
        canvas.create_line(0, 140, 1000, 140, fill='sienna')
        canvas.create_rectangle(state['x1'], 80, state['x1']+50, 140, fill='skyblue')
        canvas.create_text(state['x1']+25, 60, text=f"m1={m1.get():.1f}\nv1={state['v1']:.2f}")
        canvas.create_rectangle(state['x2'], 80, state['x2']+50, 140, fill='orange')
        canvas.create_text(state['x2']+25, 60, text=f"m2={m2.get():.1f}\nv2={state['v2']:.2f}")

        if state['running']:
            win.after(int(dt*1000), step)

    ttk.Button(frm, text='Reset', command=reset).pack(side=tk.LEFT, padx=6)
    ttk.Button(frm, text='Start', command=step).pack(side=tk.LEFT)

    reset()
