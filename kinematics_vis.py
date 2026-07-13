import tkinter as tk
from tkinter import ttk
import math


def open_kinematics_window(master=None):
    win = tk.Toplevel(master) if master else tk.Tk()
    win.title("Kinematics — Projectile Motion")
    win.geometry("1200x640")

    # Header/title and short description for users
    header = ttk.Frame(win)
    header.pack(fill=tk.X)
    ttk.Label(header, text="Kinematics — Projectile Motion", font=(None, 16, 'bold')).pack(anchor='n')
    ttk.Label(header, text="Shows a projectile under constant gravity and live plots of distance, speed and acceleration vs time.", wraplength=1000).pack(anchor='n')

    controls = ttk.Frame(win, padding=8)
    controls.pack(side=tk.LEFT, fill=tk.Y)

    # Main animation canvas (larger)
    canvas_w, canvas_h = 800, 560
    canvas = tk.Canvas(win, bg="white", width=canvas_w, height=canvas_h)
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
    initial_speed = tk.DoubleVar(value=40.0)
    angle_deg = tk.DoubleVar(value=45.0)
    gravity = tk.DoubleVar(value=9.81)
    dt_var = tk.DoubleVar(value=0.03)

    def _bind_display(var, display_var):
        def _update(*_args):
            display_var.set(f"{var.get():.2f}")
        var.trace_add("write", _update)
        _update()

    initial_speed_display = tk.StringVar(); angle_deg_display = tk.StringVar(); gravity_display = tk.StringVar(); dt_display = tk.StringVar()
    _bind_display(initial_speed, initial_speed_display); _bind_display(angle_deg, angle_deg_display); _bind_display(gravity, gravity_display); _bind_display(dt_var, dt_display)

    ttk.Label(controls, text="Initial speed (m/s)").pack()
    ttk.Scale(controls, from_=0, to=100, variable=initial_speed, orient=tk.HORIZONTAL).pack(fill=tk.X)
    ttk.Label(controls, textvariable=initial_speed_display).pack()

    ttk.Label(controls, text="Launch angle (deg)").pack(pady=(8,0))
    ttk.Scale(controls, from_=0, to=90, variable=angle_deg, orient=tk.HORIZONTAL).pack(fill=tk.X)
    ttk.Label(controls, textvariable=angle_deg_display).pack()

    ttk.Label(controls, text="Gravity (m/s^2)").pack(pady=(8,0))
    ttk.Scale(controls, from_=0.1, to=20, variable=gravity, orient=tk.HORIZONTAL).pack(fill=tk.X)
    ttk.Label(controls, textvariable=gravity_display).pack()

    ttk.Label(controls, text="Timestep dt (s)").pack(pady=(8,0))
    ttk.Scale(controls, from_=0.005, to=0.1, variable=dt_var, orient=tk.HORIZONTAL).pack(fill=tk.X)
    ttk.Label(controls, textvariable=dt_display).pack()

    btn_frame = ttk.Frame(controls)
    btn_frame.pack(pady=12, fill=tk.X)

    running = {'on': False}
    sim = {'t': 0.0}

    traj = []
    times = []
    xs = []
    vs = []
    as_ = []
    # dynamic scaling factors (pixels per meter)
    scales = {'x_scale': 5.0, 'y_scale': 5.0}

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
        # compute predicted range & height to choose scales so projectile stays on screen
        v0 = initial_speed.get()
        theta = math.radians(angle_deg.get())
        g = gravity.get()
        # predicted max range (ideal, ignoring negative or zero)
        try:
            max_range = max(0.1, (v0**2) * math.sin(2*theta) / g)
        except Exception:
            max_range = 50.0
        max_height = max(0.1, (v0**2) * (math.sin(theta)**2) / (2*g))
        # leave margins
        scales['x_scale'] = (canvas_w - 60) / (max_range + 1.0)
        scales['y_scale'] = (canvas_h - 120) / (max_height + 1.0)
        step()

    def step():
        if not running['on']:
            return
        dt = float(dt_var.get())
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

        # Convert to canvas coords using dynamic scales
        xscale = scales['x_scale']
        yscale = scales['y_scale']
        cx = 20 + x * xscale
        # ground offset
        ground_y = canvas_h - 40
        cy = ground_y - y * yscale

        if cy > ground_y:
            # hit the ground
            running['on'] = False
            draw_graphs()
            return

        traj.append((cx, cy))
        canvas.delete('all')
        # draw ground
        canvas.create_line(0, ground_y, canvas_w, ground_y, fill='sienna')
        # draw trajectory
        for i in range(1, len(traj)):
            x1, y1 = traj[i-1]
            x2, y2 = traj[i]
            canvas.create_line(x1, y1, x2, y2, fill='blue')
        # draw projectile
        canvas.create_oval(cx-6, cy-6, cx+6, cy+6, fill='red')

        # show numeric info and dt
        speed = math.hypot(vx, vy)
        info = f"t={sim['t']:.2f}s  x={x:.2f} m  y={max(y,0):.2f} m  |v|={speed:.2f} m/s  dt={dt:.2f}s"
        canvas.create_text(10, 10, anchor='nw', text=info, fill='black')

        draw_graphs()
        win.after(int(dt*1000), step)

    def draw_graphs():
        # draw axes, ticks, titles for each graph and the timeseries
        def draw_on(canvas_obj, data, color, y_label, title):
            canvas_obj.delete('all')
            if not data:
                # draw axes and titles even if empty
                w = int(canvas_obj.winfo_width() or canvas_obj['width'])
                h = int(canvas_obj.winfo_height() or canvas_obj['height'])
                pad = 32
                # axes
                canvas_obj.create_line(pad, h-pad, w-pad, h-pad, fill='black')
                canvas_obj.create_line(pad, pad, pad, h-pad, fill='black')
                canvas_obj.create_text(10, 10, anchor='nw', text=title)
                canvas_obj.create_text(pad-20, h//2, text=y_label, angle=90)
                canvas_obj.create_text(w//2, h-pad+18, text='time (s)')
                return
            w = int(canvas_obj.winfo_width() or canvas_obj['width'])
            h = int(canvas_obj.winfo_height() or canvas_obj['height'])
            pad = 40
            n = len(data)
            tmax = max(1.0, times[-1])
            ymin = min(data)
            ymax = max(data)
            if abs(ymax - ymin) < 1e-6:
                ymin -= 1
                ymax += 1
            # draw axes
            canvas_obj.create_line(pad, h-pad, w-pad, h-pad, fill='black')
            canvas_obj.create_line(pad, pad, pad, h-pad, fill='black')
            # y ticks
            for i in range(5):
                yy = pad + i*(h-2*pad)/4
                val = ymax - (i*(ymax-ymin)/4)
                canvas_obj.create_line(pad-5, int(yy), pad, int(yy), fill='black')
                canvas_obj.create_text(pad-30, int(yy), text=f"{val:.2f}")
            # x ticks
            for i in range(5):
                xx = pad + i*(w-2*pad)/4
                tval = i*(tmax/4)
                canvas_obj.create_line(int(xx), h-pad, int(xx), h-pad+5, fill='black')
                canvas_obj.create_text(int(xx), h-pad+18, text=f"{tval:.2f}")
            # plot data
            for i in range(1, n):
                x1 = int(pad + (times[i-1]/tmax)*(w-2*pad))
                x2 = int(pad + (times[i]/tmax)*(w-2*pad))
                y1 = int(h-pad - ((data[i-1]-ymin)/(ymax-ymin))*(h-2*pad))
                y2 = int(h-pad - ((data[i]-ymin)/(ymax-ymin))*(h-2*pad))
                canvas_obj.create_line(x1, y1, x2, y2, fill=color)
            # labels
            canvas_obj.create_text(10, 10, anchor='nw', text=title)
            canvas_obj.create_text(pad-20, h//2, text=y_label, angle=90)
            canvas_obj.create_text(w//2, h-pad+18, text='time (s)')

        draw_on(graph_xt, xs, 'green', 'distance (m)', 'x(t) — Distance vs Time')
        draw_on(graph_vt, vs, 'blue', 'speed (m/s)', '|v|(t) — Speed vs Time')
        draw_on(graph_at, as_, 'red', 'acceleration (m/s^2)', '|a|(t) — Acceleration vs Time')

    ttk.Button(btn_frame, text="Start", command=start).pack(side=tk.LEFT, expand=True, fill=tk.X, padx=4)
    ttk.Button(btn_frame, text="Reset", command=reset).pack(side=tk.LEFT, expand=True, fill=tk.X, padx=4)

    ttk.Label(controls, text="Notes:").pack(pady=(12,0))
    ttk.Label(controls, wraplength=220, text="This demo shows projectile motion and live plots of x(t), |v|(t), and |a|(t). Use sliders to change parameters.").pack()

    reset()
