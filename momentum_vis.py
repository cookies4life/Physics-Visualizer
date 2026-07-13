"""Animated 1D collision demo showing momentum conservation."""

import tkinter as tk
from tkinter import ttk


def open_momentum_window(master=None):
    """Create the collision simulator window with controls and animated blocks."""
    win = tk.Toplevel(master) if master else tk.Tk()
    win.title("Momentum & Collisions — Animated 1D Collision")

    def _maximize_or_fullscreen_max(win_obj: tk.Toplevel):
        """Best-effort maximize for cross-platform Tk (maximized window).

        Uses 'zoomed' when available. Avoid fullscreen toggle to prevent a
        visible flash.
        """
        try:
            win_obj.state('zoomed')
        except Exception:
            pass

    # Start as maximized.
    win.after(100, lambda: _maximize_or_fullscreen_max(win))




    # Header and description
    header = ttk.Frame(win)
    header.pack(fill=tk.X)
    ttk.Label(header, text="Momentum & Collisions — 1D Collision", font=(None, 16, 'bold')).pack(anchor='n')
    ttk.Label(
        header,
        text="Animated 1D collision showing conservation of momentum. Velocities shown are in m/s; positions are in pixels for visualization.",
        wraplength=980,
    ).pack(anchor='n')

    frm = ttk.Frame(win, padding=8)
    frm.pack(fill=tk.BOTH, expand=True)

    m1 = tk.DoubleVar(value=2.0)
    v1 = tk.DoubleVar(value=10.0)
    m2 = tk.DoubleVar(value=1.0)
    v2 = tk.DoubleVar(value=-2.0)
    elastic = tk.BooleanVar(value=True)

    def _bind_display(var, display_var):
        def _update(*_args):
            display_var.set(f"{var.get():.2f}")

        var.trace_add("write", _update)
        _update()

    m1_display = tk.StringVar()
    v1_display = tk.StringVar()
    m2_display = tk.StringVar()
    v2_display = tk.StringVar()
    _bind_display(m1, m1_display)
    _bind_display(v1, v1_display)
    _bind_display(m2, m2_display)
    _bind_display(v2, v2_display)

    control = ttk.Frame(frm)
    control.pack(fill=tk.X)
    ttk.Label(control, text='m1').pack(side=tk.LEFT)
    ttk.Scale(control, from_=0.1, to=20, variable=m1, orient=tk.HORIZONTAL).pack(side=tk.LEFT, fill=tk.X, expand=True)
    ttk.Label(control, textvariable=m1_display).pack(side=tk.LEFT, padx=6)
    ttk.Label(control, text='v1').pack(side=tk.LEFT)
    ttk.Scale(control, from_=-50, to=50, variable=v1, orient=tk.HORIZONTAL).pack(side=tk.LEFT, fill=tk.X, expand=True)
    ttk.Label(control, textvariable=v1_display).pack(side=tk.LEFT, padx=6)
    ttk.Label(control, text='m2').pack(side=tk.LEFT)
    ttk.Scale(control, from_=0.1, to=20, variable=m2, orient=tk.HORIZONTAL).pack(side=tk.LEFT, fill=tk.X, expand=True)
    ttk.Label(control, textvariable=m2_display).pack(side=tk.LEFT, padx=6)
    ttk.Label(control, text='v2').pack(side=tk.LEFT)
    ttk.Scale(control, from_=-50, to=50, variable=v2, orient=tk.HORIZONTAL).pack(side=tk.LEFT, fill=tk.X, expand=True)
    ttk.Label(control, textvariable=v2_display).pack(side=tk.LEFT, padx=6)
    ttk.Checkbutton(control, text='Elastic', variable=elastic).pack(side=tk.LEFT, padx=6)

    canvas = tk.Canvas(frm, bg='white', height=160)
    canvas.pack(fill=tk.BOTH, expand=True, pady=8)

    # positions in pixels
    # Note: box widths are dynamic based on mass.
    state = {
        'x1': 120.0,  # left edge for box 1
        'x2': 740.0,  # left edge for box 2
        'v1': v1.get(),
        'v2': v2.get(),
        'running': False,
    }

    def box_size(mass_value: float) -> tuple[float, float]:
        """Return the width and height of a block based on its mass.

        Larger masses become visually larger so the animation is easier to follow.
        """
        m = float(mass_value)
        # Map mass (0.1..20) -> size range in px.
        # width: 30..110, height: 30..90
        w = 30.0 + (m / 20.0) * 80.0
        h = 30.0 + (m / 20.0) * 60.0
        return w, h



    def compute_after_vels():
        """Calculate the post-collision velocities for the two blocks."""
        M1 = m1.get()
        V1 = state['v1']
        M2 = m2.get()
        V2 = state['v2']
        if elastic.get():
            u1 = (V1 * (M1 - M2) + 2 * M2 * V2) / (M1 + M2)
            u2 = (V2 * (M2 - M1) + 2 * M1 * V1) / (M1 + M2)
        else:
            u = (M1 * V1 + M2 * V2) / (M1 + M2)
            u1 = u2 = u
        return u1, u2

    def reset():
        """Reset the collision scene to its initial positions and velocities."""
        state['x1'] = 120.0
        state['x2'] = 740.0
        state['v1'] = v1.get()
        state['v2'] = v2.get()
        state['running'] = False

    def step():
        """Advance the collision animation by one frame and redraw the scene."""
        state['running'] = True
        dt = 0.02

        # update velocities and positions
        state['x1'] += state['v1'] * dt * 10
        state['x2'] += state['v2'] * dt * 10

        # detect collision (simple overlap)
        w1, _h1 = box_size(m1.get())
        w2, _h2 = box_size(m2.get())

        if state['x1'] + w1 >= state['x2']:


            u1, u2 = compute_after_vels()
            # convert back to pixel/sec scale
            state['v1'] = u1
            state['v2'] = u2

        # draw
        canvas.delete('all')
        canvas.create_line(0, 140, 1000, 140, fill='sienna')

        # Add labels above each block so the user can identify them easily.
        ttk_text_y = 40
        canvas.create_text(260, ttk_text_y, text="Block 1", fill='black', anchor='center')
        canvas.create_text(740, ttk_text_y, text="Block 2", fill='black', anchor='center')


        # Draw block 1 and its velocity arrow.
        w1, h1 = box_size(m1.get())

        x1_left = state['x1']
        x1_right = x1_left + w1
        # Scale TOTAL size: use dynamic height too.
        y_top1 = 140 - h1
        y_bottom1 = 140
        canvas.create_rectangle(x1_left, y_top1, x1_right, y_bottom1, fill='skyblue')


        # Velocity vector for block 1
        v1_now = state['v1']
        x1_mid = x1_left + w1 / 2
        box_center_y1 = (y_top1 + y_bottom1) / 2


        # Center arrows vertically inside the (dynamic-height) box.
        y_vec = (y_top1 + y_bottom1) / 2

        # Scale arrow length with box size as well as |v|.
        # (Keeps arrows proportional when boxes get taller.)
        arrow_scale = max(0.5, h1 / 60.0)
        v1_len = min(160, max(0, abs(v1_now) * 8 * arrow_scale))


        if v1_len > 1e-6:
            if v1_now >= 0:
                # Start at the box center; arrow head shows velocity direction.
                canvas.create_line(x1_mid, y_vec, x1_mid + v1_len, y_vec, arrow='last', width=3, fill='blue')
                canvas.create_text(
                    x1_mid + v1_len + 10,
                    y_vec,

                    text=f"v1={v1_now:.2f} m/s",
                    fill='blue',
                    anchor='w',
                )
            else:
                # Start at box center for negative velocities too.
                canvas.create_line(x1_mid, y_vec, x1_mid - v1_len, y_vec, arrow='first', width=3, fill='blue')

                canvas.create_text(
                    x1_mid - v1_len - 10,
                    y_vec,
                    text=f"v1={v1_now:.2f} m/s",
                    fill='blue',
                    anchor='e',
                )
        else:
            canvas.create_text(x1_mid, y_vec, text=f"v1={v1_now:.2f} m/s", fill='blue')

        canvas.create_text(x1_left + w1 / 2, 60, text=f"m1={m1.get():.2f} kg", fill='black')


        # Draw block 2 and its velocity arrow.
        w2, h2 = box_size(m2.get())
        x2_left = state['x2']
        x2_right = x2_left + w2
        # Scale TOTAL size: use dynamic height too.
        y_top2 = 140 - h2
        y_bottom2 = 140
        canvas.create_rectangle(x2_left, y_top2, x2_right, y_bottom2, fill='orange')


        # Velocity vector for block 2
        v2_now = state['v2']
        x2_mid = x2_left + w2 / 2

        # Velocity arrow centered vertically within block 2.
        y_vec = (y_top2 + y_bottom2) / 2


        # Scale arrow length with box height too.
        arrow_scale = max(0.5, h2 / 60.0)
        v2_len = min(160, max(0, abs(v2_now) * 8 * arrow_scale))


        # Velocity arrow should show motion direction.
        # For v2 < 0, arrow should clearly point RIGHT-TO-LEFT (head at the left).
        if v2_len > 1e-6:
            if v2_now >= 0:
                # Start arrow from box center; head shows direction.
                x_start = x2_mid
                x_end = x_start + v2_len

                canvas.create_line(x_start, y_vec, x_end, y_vec, arrow='last', width=3, fill='red')
                canvas.create_text(x_end + 10, y_vec, text=f"v2={v2_now:.2f} m/s", fill='red', anchor='w')
            else:
                # Start arrow from box center; head shows direction.
                x_start = x2_mid
                x_end = x_start - v2_len

                # arrow='last' keeps the head at the end point (left)
                canvas.create_line(x_start, y_vec, x_end, y_vec, arrow='last', width=3, fill='red')
                canvas.create_text(x_end - 10, y_vec, text=f"v2={v2_now:.2f} m/s", fill='red', anchor='e')
        else:
            canvas.create_text(x2_mid, y_vec, text=f"v2={v2_now:.2f} m/s", fill='red')




        canvas.create_text(x2_left + w2 / 2, 60, text=f"m2={m2.get():.2f} kg", fill='black')


        if state['running']:

            win.after(int(dt * 1000), step)

    ttk.Button(frm, text='Reset', command=reset).pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=6, pady=6)
    ttk.Button(frm, text='Start', command=step).pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=6, pady=6)


    reset()

