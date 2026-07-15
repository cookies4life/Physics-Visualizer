"""Kinematics visualization for projectile motion with live graphs."""

import tkinter as tk
from tkinter import ttk
import math

import viz_common


def open_kinematics_window(master=None):
    """Create the projectile motion window with controls, animation, and graphs."""
    win = tk.Toplevel(master) if master else tk.Tk()
    win.title("Kinematics — Projectile Motion")
    win.geometry("1200x640")

    def _maximize_or_fullscreen_max(win_obj: tk.Toplevel):
        """Best-effort maximize for cross-platform Tk.

        Use after() so the window manager has finished creating the window.
        """
        try:
            win_obj.state('zoomed')
        except Exception:
            pass

    # Start as maximized.
    win.after(100, lambda: _maximize_or_fullscreen_max(win))


    # Create the top title and description for the visualization.

    header = ttk.Frame(win)
    header.pack(fill=tk.X)
    ttk.Label(header, text="Kinematics — Projectile Motion", font=(None, 16, 'bold')).pack(anchor='n')
    ttk.Label(header, text="Shows a projectile under constant gravity and live plots of distance, speed and acceleration vs time.", wraplength=1000).pack(anchor='n')

    # Create the left-side control panel for changing the simulation parameters.
    controls = ttk.Frame(win, padding=8)
    controls.pack(side=tk.LEFT, fill=tk.Y)

    # Create the main animation canvas where the projectile is drawn.
    canvas_w, canvas_h = 800, 560
    GROUND_Y = canvas_h - 60
    ORIGIN_X = 20
    VECTOR_PX_PER_MPS = 3.0
    anim_frame = ttk.Frame(win)
    anim_frame.pack(side=tk.LEFT, padx=8, pady=8)
    ttk.Label(anim_frame, text='Animation — Projectile Motion', font=(None, 12, 'bold')).pack()
    canvas = tk.Canvas(anim_frame, bg="#eaf6ff", width=canvas_w, height=canvas_h, highlightthickness=0)
    canvas.pack()

    # Create the right-side area for the live graphs.
    graphs_frame = ttk.Frame(win)
    graphs_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=8, pady=8)

    # Add three stacked graph panels for distance, speed, and acceleration.
    g1 = ttk.Frame(graphs_frame)
    ttk.Label(g1, text='x(t) — Distance vs Time', font=(None, 11, 'bold')).pack(anchor='w')
    graph_xt = tk.Canvas(g1, bg='white', height=140)
    graph_xt.pack(fill=tk.BOTH, expand=True)
    g1.pack(fill=tk.BOTH, expand=True)

    g2 = ttk.Frame(graphs_frame)
    ttk.Label(g2, text='|v|(t) — Speed vs Time', font=(None, 11, 'bold')).pack(anchor='w')
    graph_vt = tk.Canvas(g2, bg='white', height=140)
    graph_vt.pack(fill=tk.BOTH, expand=True)
    g2.pack(fill=tk.BOTH, expand=True)

    g3 = ttk.Frame(graphs_frame)
    ttk.Label(g3, text='|a|(t) — Acceleration vs Time', font=(None, 11, 'bold')).pack(anchor='w')
    graph_at = tk.Canvas(g3, bg='white', height=140)
    graph_at.pack(fill=tk.BOTH, expand=True)
    g3.pack(fill=tk.BOTH, expand=True)

    # Define the user-adjustable simulation variables.
    initial_speed = tk.DoubleVar(value=40.0)
    angle_deg = tk.DoubleVar(value=45.0)
    gravity = tk.DoubleVar(value=9.81)
    dt_var = tk.DoubleVar(value=0.03)
    mass = tk.DoubleVar(value=0.43)  # kg — a regulation football is ~0.41-0.45 kg

    # Keep a small label beside each slider showing the current numeric value.
    def _bind_display(var, display_var):
        def _update(*_args):
            display_var.set(f"{var.get():.2f}")
        var.trace_add("write", _update)
        _update()

    initial_speed_display = tk.StringVar(); angle_deg_display = tk.StringVar(); gravity_display = tk.StringVar(); dt_display = tk.StringVar(); mass_display = tk.StringVar()
    _bind_display(initial_speed, initial_speed_display); _bind_display(angle_deg, angle_deg_display); _bind_display(gravity, gravity_display); _bind_display(dt_var, dt_display); _bind_display(mass, mass_display)

    ttk.Label(controls, text="Initial speed (m/s)").pack()
    ttk.Scale(controls, from_=0, to=100, variable=initial_speed, orient=tk.HORIZONTAL).pack(fill=tk.X)
    ttk.Label(controls, textvariable=initial_speed_display).pack()

    ttk.Label(controls, text="Launch angle (deg)").pack(pady=(8,0))
    ttk.Scale(controls, from_=0, to=90, variable=angle_deg, orient=tk.HORIZONTAL).pack(fill=tk.X)
    ttk.Label(controls, textvariable=angle_deg_display).pack()

    ttk.Label(controls, text="Football mass (kg)").pack(pady=(8,0))
    ttk.Scale(controls, from_=0.1, to=5.0, variable=mass, orient=tk.HORIZONTAL).pack(fill=tk.X)
    ttk.Label(controls, textvariable=mass_display).pack()

    ttk.Label(controls, text="Gravity (m/s^2)").pack(pady=(8,0))
    ttk.Scale(controls, from_=0.1, to=20, variable=gravity, orient=tk.HORIZONTAL).pack(fill=tk.X)
    ttk.Label(controls, textvariable=gravity_display).pack()

    ttk.Label(controls, text="Timestep dt (s)").pack(pady=(8,0))
    ttk.Scale(controls, from_=0.005, to=0.1, variable=dt_var, orient=tk.HORIZONTAL).pack(fill=tk.X)
    ttk.Label(controls, textvariable=dt_display).pack()

    btn_frame = ttk.Frame(controls)
    btn_frame.pack(pady=12, fill=tk.X)

    # --- Small companion window showing the equations being demonstrated ---
    EQ_W, EQ_H = 340, 420
    eq_win, update_equations_text = viz_common.create_equations_panel(win, "Projectile Motion", width=EQ_W, height=EQ_H)
    win.protocol("WM_DELETE_WINDOW", lambda: (eq_win.destroy(), win.destroy()))

    def _reposition_eq_panel():
        # The main window maximizes shortly after creation, so "beside it"
        # (computed at eq-panel-creation time) would be stale; pin it to the
        # screen's top-right corner instead once the window has settled.
        sw = win.winfo_screenwidth()
        eq_win.geometry(f"{EQ_W}x{EQ_H}+{sw - EQ_W - 20}+40")
    win.after(150, _reposition_eq_panel)

    def update_equations(t, v0, theta_deg, g, x, y, vx, vy):
        speed = math.hypot(vx, vy)
        lines = [
            "Position (kinematics with constant acceleration)",
            "  x(t) = v0 cosθ · t",
            f"  = ({v0:.2f})cos({theta_deg:.1f}°)×{t:.2f} = {x:.2f} m",
            "  y(t) = v0 sinθ · t − 1/2 g t²",
            f"  = ({v0:.2f})sin({theta_deg:.1f}°)×{t:.2f} − 0.5×{g:.2f}×{t:.2f}²",
            f"  = {y:.2f} m",
            "",
            "Velocity",
            "  vx(t) = v0 cosθ  (constant)",
            f"  = {vx:.2f} m/s",
            "  vy(t) = v0 sinθ − g t",
            f"  = {vy:.2f} m/s",
            f"  |v| = {speed:.2f} m/s",
            "",
            "Acceleration (gravity only)",
            "  ax = 0 m/s²",
            f"  ay = -g = {-g:.2f} m/s²",
            "",
            f"t = {t:.2f} s",
        ]
        update_equations_text(lines)

    # Store the current running state and the simulation time.
    running = {'on': False}
    sim = {'t': 0.0}

    # Store historical values for drawing the graphs.
    traj = []
    times = []
    xs = []
    vs = []
    as_ = []
    # dynamic scaling factors (pixels per meter)
    scales = {'x_scale': 5.0, 'y_scale': 5.0}
    dragging = {'on': False}

    # The football grows with mass so heavier balls are visibly larger.
    def football_size():
        m = min(5.0, max(0.1, mass.get()))
        length = 16 + m * 24
        return length, length * 0.55

    # Where the adjustable velocity-vector arrow currently ends, in canvas coords.
    def arrow_tip():
        theta = math.radians(angle_deg.get())
        max_len = max(40, canvas_w - ORIGIN_X - 60)
        speed_px = min(initial_speed.get() * VECTOR_PX_PER_MPS, max_len)
        return ORIGIN_X + speed_px * math.cos(theta), GROUND_Y - speed_px * math.sin(theta)

    # Draw the football field with the adjustable launch vector, shown whenever
    # the simulation isn't actively running.
    def draw_idle_preview():
        canvas.delete('all')
        viz_common.draw_football_field(canvas, canvas_w, canvas_h, GROUND_Y)

        theta_deg = angle_deg.get()
        tip_x, tip_y = arrow_tip()
        viz_common.draw_arrow(canvas, ORIGIN_X, GROUND_Y, tip_x, tip_y, '#1d4fd8', 3)

        r = 50
        if theta_deg > 1:
            canvas.create_arc(ORIGIN_X - r, GROUND_Y - r, ORIGIN_X + r, GROUND_Y + r, start=0, extent=-theta_deg, style='arc', outline='#333333', width=2)
        mid = math.radians(theta_deg / 2)
        canvas.create_text(
            ORIGIN_X + (r + 26) * math.cos(mid), GROUND_Y - (r + 26) * math.sin(mid),
            text=f"θ={theta_deg:.1f}°", font=('Arial', 11, 'bold'), fill='#1d4fd8')
        canvas.create_text(tip_x + 10, tip_y - 10, text=f"v0={initial_speed.get():.1f} m/s", fill='#1d4fd8', font=('Arial', 10, 'bold'), anchor='w')

        length, width_ = football_size()
        viz_common.draw_football(canvas, ORIGIN_X, GROUND_Y - width_ / 2, length, width_, math.radians(-theta_deg))
        viz_common.draw_readout(canvas, f"Drag the arrow tip to set v0 and θ   |   v0={initial_speed.get():.1f} m/s  θ={theta_deg:.1f}°")

    def refresh_idle(*_args):
        if not running['on']:
            draw_idle_preview()

    for var in (initial_speed, angle_deg, mass):
        var.trace_add("write", refresh_idle)
    canvas.bind('<Configure>', refresh_idle)

    # --- Let the user drag the velocity-vector arrow to set v0 and angle ---
    def near_tip(x, y):
        tx, ty = arrow_tip()
        return math.hypot(x - tx, y - ty) <= 16

    def on_press(event):
        if not running['on'] and near_tip(event.x, event.y):
            dragging['on'] = True

    def on_drag(event):
        if not dragging['on']:
            return
        dx = max(0.0, event.x - ORIGIN_X)
        dy = max(0.0, GROUND_Y - event.y)
        r_px = max(6.0, math.hypot(dx, dy))
        theta = math.degrees(math.atan2(dy, dx)) if (dx > 0 or dy > 0) else 0.0
        angle_deg.set(max(0.0, min(90.0, theta)))
        initial_speed.set(max(0.0, min(100.0, r_px / VECTOR_PX_PER_MPS)))

    def on_release(_event):
        dragging['on'] = False

    def on_hover(event):
        canvas.config(cursor='fleur' if (not running['on'] and near_tip(event.x, event.y)) else '')

    canvas.bind('<ButtonPress-1>', on_press)
    canvas.bind('<B1-Motion>', on_drag)
    canvas.bind('<ButtonRelease-1>', on_release)
    canvas.bind('<Motion>', on_hover)

    # Reset the simulation so it starts from a clean state.
    def reset():
        running['on'] = False
        sim['t'] = 0.0
        traj.clear()
        times.clear(); xs.clear(); vs.clear(); as_.clear()
        graph_xt.delete('all'); graph_vt.delete('all'); graph_at.delete('all')
        draw_idle_preview()
        v0 = initial_speed.get()
        theta_deg = angle_deg.get()
        g = gravity.get()
        theta = math.radians(theta_deg)
        update_equations(0.0, v0, theta_deg, g, 0.0, 0.0, v0 * math.cos(theta), v0 * math.sin(theta))

    # Start the projectile motion animation.
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

    # Advance the projectile by one time step and redraw the scene.
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

        update_equations(sim['t'], v0, angle_deg.get(), g, x, y, vx, vy)

        # record for graphs (use magnitude for v and a)
        times.append(sim['t'])
        xs.append(x)
        vs.append(math.hypot(vx, vy))
        as_.append(math.hypot(a_x, a_y))

        # Convert to canvas coords using dynamic scales
        xscale = scales['x_scale']
        yscale = scales['y_scale']
        cx = ORIGIN_X + x * xscale
        cy = GROUND_Y - y * yscale

        if cy > GROUND_Y:
            # hit the ground
            running['on'] = False
            draw_graphs()
            return

        traj.append((cx, cy))
        canvas.delete('all')
        viz_common.draw_football_field(canvas, canvas_w, canvas_h, GROUND_Y)
        # draw trajectory
        for i in range(1, len(traj)):
            x1, y1 = traj[i-1]
            x2, y2 = traj[i]
            canvas.create_line(x1, y1, x2, y2, fill='#1d4fd8', width=2)
        # draw the football, oriented along its current velocity direction
        length, width_ = football_size()
        orientation = math.atan2(-vy, vx)
        viz_common.draw_football(canvas, cx, cy, length, width_, orientation)

        # show numeric info and dt
        speed = math.hypot(vx, vy)
        info = f"t={sim['t']:.2f}s  x={x:.2f} m  y={max(y,0):.2f} m  |v|={speed:.2f} m/s  th0={angle_deg.get():.1f} deg  dt={dt:.2f}s"
        viz_common.draw_readout(canvas, info)

        draw_graphs()
        win.after(int(dt*1000), step)

    # Draw the three graphs from the recorded motion data.
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

    ttk.Button(btn_frame, text="Start", command=start).pack(side=tk.LEFT, expand=True, fill=tk.BOTH, padx=4)
    ttk.Button(btn_frame, text="Reset", command=reset).pack(side=tk.LEFT, expand=True, fill=tk.BOTH, padx=4)


    ttk.Label(controls, text="Notes:").pack(pady=(12,0))
    ttk.Label(controls, wraplength=220, text="This demo shows a football's projectile motion and live plots of x(t), |v|(t), and |a|(t). Use the sliders, or drag the blue arrow's tip on the field to set the launch speed and angle.").pack()

    reset()
    return win
