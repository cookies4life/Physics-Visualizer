import tkinter as tk
from tkinter import ttk
import math


def open_quantum_window(master=None):
    win = tk.Toplevel(master) if master else tk.Tk()
    win.title("Quantum Mechanics — Particle in a Box (1D)")
    win.geometry("900x420")

    frm = ttk.Frame(win, padding=8)
    frm.pack(fill=tk.BOTH, expand=True)

    n = tk.IntVar(value=1)
    L = tk.DoubleVar(value=1.0)

    canvas = tk.Canvas(frm, bg='white', height=300)
    canvas.pack(fill=tk.BOTH, expand=True)

    ctrl = ttk.Frame(frm)
    ctrl.pack(fill=tk.X)
    ttk.Label(ctrl, text='Quantum number n').pack(side=tk.LEFT)
    ttk.Scale(ctrl, from_=1, to=10, variable=n, orient=tk.HORIZONTAL).pack(side=tk.LEFT, fill=tk.X, expand=True)
    ttk.Label(ctrl, text='Box length L (m)').pack(side=tk.LEFT)
    ttk.Scale(ctrl, from_=0.2, to=5.0, variable=L, orient=tk.HORIZONTAL).pack(side=tk.LEFT)

    # animation state
    state = {'t': 0.0}

    def psi(nval, x, Lval, t):
        # real part with simple time dependence cos(omega t), omega ~ n^2
        spatial = math.sqrt(2.0 / Lval) * math.sin(nval * math.pi * x / Lval)
        omega = (nval**2)
        return spatial * math.cos(omega * t)

    def draw():
        canvas.delete('all')
        Lval = L.get(); nval = n.get()
        w = int(canvas.winfo_width() or 800)
        h = int(canvas.winfo_height() or 300)
        points_real = []
        points_prob = []
        for i in range(0, w):
            x = (i / w) * Lval
            val = psi(nval, x, Lval, state['t'])
            prob = val*val
            # map real part centered vertically, prob scaled
            y_real = int(h/2 - val*(h/3))
            y_prob = int(h - prob*(h*0.9))
            points_real.append((i, y_real))
            points_prob.append((i, y_prob))
        # draw real part
        for i in range(1, len(points_real)):
            x1, y1 = points_real[i-1]
            x2, y2 = points_real[i]
            canvas.create_line(x1, y1, x2, y2, fill='purple')
        # draw probability density
        for i in range(1, len(points_prob)):
            x1, y1 = points_prob[i-1]
            x2, y2 = points_prob[i]
            canvas.create_line(x1, y1, x2, y2, fill='green')
        canvas.create_text(10, 10, anchor='nw', text=f"n={nval}  L={Lval:.2f} m  t={state['t']:.2f}")

    def animate():
        state['t'] += 0.05
        draw()
        win.after(50, animate)

    animate()
