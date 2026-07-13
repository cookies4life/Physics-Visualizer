import tkinter as tk
from tkinter import ttk
import math


def open_kinematics_window(master=None):
    win = tk.Toplevel(master) if master else tk.Tk()
    win.title("Kinematics — Projectile Motion")
    win.geometry("1100x600")

    controls = ttk.Frame(win, padding=8)
    controls.pack(side=tk.LEFT, fill=tk.Y)

    # Main animation canvas
    canvas = tk.Canvas(win, bg="white", width=640, height=480)
    canvas.pack(side=tk.LEFT, padx=8, pady=8)

    # Graphs canvas (x(t), v(t), a(t)) stacked vertically
    graphs_frame = ttk.Frame(win)
    graphs_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=8, pady=8)

    graph_xt = tk.Canvas(graphs_frame, bg='white', height=140)
    graph_vt = tk.Canvas(graphs_frame, bg='white', height=140)
    graph_at = tk.Canvas(graphs_frame, bg='white', height=140)
    graph_xt.pack(fill=tk.BOTH, expand=True)
    graph_vt.pack(fill=tk.BOTH, expand=True)
    graph_at.pack(fill=tk.BOTH, expand=True)

    # Parameters
    initial_speed = tk.DoubleVar(value=50.0)
    angle_deg = tk.DoubleVar(value=45.0)
    gravity = tk.DoubleVar(value=9.81)

    ttk.Label(controls, text="Initial speed (m/s)").pack()
    ttk.Scale(controls, from_=0, to=200, variable=initial_speed, orient=tk.HORIZONTAL).pack(fill=tk.X)
    ttk.Label(controls, textvariable=initial_speed).pack()

    ttk.Label(controls, text="Launch angle (deg)").pack(pady=(8,0))
    ttk.Scale(controls, from_=0, to=90, variable=angle_deg, orient=tk.HORIZONTAL).pack(fill=tk.X)
    ttk.Label(controls, textvariable=angle_deg).pack()

    ttk.Label(controls, text="Gravity (m/s^2)").pack(pady=(8,0))
    ttk.Scale(controls, from_=0.1, to=20, variable=gravity, orient=tk.HORIZONTAL).pack(fill=tk.X)
    ttk.Label(controls, textvariable=gravity).pack()

    btn_frame = ttk.Frame(controls)
    btn_frame.pack(pady=12, fill=tk.X)

    running = {'on': False}
    sim = {'t': 0.0}

    traj = []
    times = []
    xs = []
    vs = []
    as_ = []

    def reset():
        running['on'] = False
        sim['t'] = 0.0
        traj.clear()
        times.clear(); xs.clear(); vs.clear(); as_.clear()
        canvas.delete('all')
        graph_xt.delete('all'); graph_vt.delete('all'); graph_at.delete('all')

    def start():
        if running['on']:
            return
        running['on'] = True
        sim['t'] = 0.0
        traj.clear()
        times.clear(); xs.clear(); vs.clear(); as_.clear()
        step()

    def step():
        if not running['on']:
            return
        dt = 0.03
        sim['t'] += dt
        v0 = initial_speed.get()
        theta = math.radians(angle_deg.get())
        g = gravity.get()

        x = v0 * math.cos(theta) * sim['t']
        y = v0 * math.sin(theta) * sim['t'] - 0.5 * g * sim['t'] ** 2

        vx = v0 * math.cos(theta)
        vy = v0 * math.sin(theta) - g * sim['t']
        a_x = 0.0
        a_y = -g

        # record for graphs (use magnitude for v and a)
        times.append(sim['t'])
        xs.append(x)
        vs.append(math.hypot(vx, vy))
        as_.append(math.hypot(a_x, a_y))

        # Convert to canvas coords
        scale = 5.0
        cx = 20 + x * scale
        cy = 460 - y * scale

        if cy > 480:
            # hit the ground
            running['on'] = False
            draw_graphs()
            return

        traj.append((cx, cy))
        canvas.delete('all')
        # draw ground
        canvas.create_line(0, 460, 640, 460, fill='sienna')
        # draw trajectory
        for i in range(1, len(traj)):
            x1, y1 = traj[i-1]
            x2, y2 = traj[i]
            canvas.create_line(x1, y1, x2, y2, fill='blue')
        # draw projectile
        canvas.create_oval(cx-6, cy-6, cx+6, cy+6, fill='red')

        # show numeric info
        speed = math.hypot(vx, vy)
        info = f"t={sim['t']:.2f}s  x={x:.2f}m  y={max(y,0):.2f}m  |v|={speed:.2f}m/s"
        canvas.create_text(10, 10, anchor='nw', text=info, fill='black')

        draw_graphs()
        win.after(int(dt*1000), step)

    def draw_graphs():
        # simple scaling to draw timeseries on small canvas
        def draw_on(canvas_obj, data, color):
            canvas_obj.delete('all')
            if not data:
                return
            w = int(canvas_obj.winfo_width() or canvas_obj['width'])
            h = int(canvas_obj.winfo_height() or canvas_obj['height'])
            # pad
            pad = 8
            n = len(data)
            xmax = max(1.0, times[-1])
            ymin = min(data)
            ymax = max(data)
            if abs(ymax - ymin) < 1e-6:
                ymin -= 1
                ymax += 1
            for i in range(1, n):
                x1 = int(pad + (times[i-1]/xmax) * (w - 2*pad))
                x2 = int(pad + (times[i]/xmax) * (w - 2*pad))
                y1 = int(h - pad - ((data[i-1]-ymin)/(ymax-ymin)) * (h - 2*pad))
                y2 = int(h - pad - ((data[i]-ymin)/(ymax-ymin)) * (h - 2*pad))
                canvas_obj.create_line(x1, y1, x2, y2, fill=color)

        draw_on(graph_xt, xs, 'green')
        graph_xt.create_text(10, 10, anchor='nw', text='x(t) (m)')
        draw_on(graph_vt, vs, 'blue')
        graph_vt.create_text(10, 10, anchor='nw', text='|v|(t) (m/s)')
        draw_on(graph_at, as_, 'red')
        graph_at.create_text(10, 10, anchor='nw', text='|a|(t) (m/s^2)')

    ttk.Button(btn_frame, text="Start", command=start).pack(side=tk.LEFT, expand=True, fill=tk.X, padx=4)
    ttk.Button(btn_frame, text="Reset", command=reset).pack(side=tk.LEFT, expand=True, fill=tk.X, padx=4)

    ttk.Label(controls, text="Notes:").pack(pady=(12,0))
    ttk.Label(controls, wraplength=220, text="This demo shows projectile motion and live plots of x(t), |v|(t), and |a|(t). Use sliders to change parameters.").pack()

    reset()
