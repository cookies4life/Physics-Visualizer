"""Rotational motion visualization for a spinning disk with torque and energy."""

import tkinter as tk
from tkinter import ttk
import math


def open_rotation_window(master=None):
    """Create the rotational motion demo with a spinning disk and live physics values."""
    win = tk.Toplevel(master) if master else tk.Tk()
    win.title("Rotational Motion — Spinning Disk")
    win.geometry("760x520")
    win.minsize(700, 460)

    def _maximize_or_fullscreen_max(win_obj: tk.Toplevel):
        """Best-effort maximize for cross-platform Tk."""
        try:
            win_obj.state('zoomed')
        except Exception:
            pass

    win.after(100, lambda: _maximize_or_fullscreen_max(win))

    header = ttk.Frame(win, padding=(10, 8))
    header.pack(fill=tk.X)
    ttk.Label(header, text="Rotational Motion — Spinning Disk", font=(None, 16, 'bold')).pack(anchor='n')
    ttk.Label(
        header,
        text=(
            "Use mass, radius, and torque controls to observe angular acceleration, angular velocity, "
            "angular momentum, and rotational kinetic energy."
        ),
        wraplength=740,
    ).pack(anchor='n', pady=(4, 0))

    control_frame = ttk.Frame(win, padding=(10, 8))
    control_frame.pack(fill=tk.X)
    control_frame.columnconfigure(1, weight=1)

    mass = tk.DoubleVar(value=2.0)
    radius = tk.DoubleVar(value=0.5)
    torque = tk.DoubleVar(value=1.0)

    mass_display = tk.StringVar()
    radius_display = tk.StringVar()
    torque_display = tk.StringVar()

    ttk.Label(control_frame, text="Mass").grid(row=0, column=0, sticky='w', pady=4)
    ttk.Scale(control_frame, from_=0.1, to=20.0, variable=mass, orient=tk.HORIZONTAL).grid(row=0, column=1, sticky='we', padx=(8, 8))
    ttk.Label(control_frame, textvariable=mass_display).grid(row=0, column=2, sticky='e')

    ttk.Label(control_frame, text="Radius").grid(row=1, column=0, sticky='w', pady=4)
    ttk.Scale(control_frame, from_=0.05, to=2.0, variable=radius, orient=tk.HORIZONTAL).grid(row=1, column=1, sticky='we', padx=(8, 8))
    ttk.Label(control_frame, textvariable=radius_display).grid(row=1, column=2, sticky='e')

    ttk.Label(control_frame, text="Applied torque").grid(row=2, column=0, sticky='w', pady=4)
    ttk.Scale(control_frame, from_=-10.0, to=10.0, variable=torque, orient=tk.HORIZONTAL).grid(row=2, column=1, sticky='we', padx=(8, 8))
    ttk.Label(control_frame, textvariable=torque_display).grid(row=2, column=2, sticky='e')

    status_frame = ttk.Frame(win, padding=(10, 0, 10, 6))
    status_frame.pack(fill=tk.X)
    info_text = tk.StringVar()
    ttk.Label(status_frame, textvariable=info_text, font=('Courier', 10)).pack(anchor='w')
    ttk.Label(
        status_frame,
        text="Start the simulation and watch how torque changes the disk rotation, angular momentum and kinetic energy.",
        wraplength=740,
    ).pack(anchor='w', pady=(4, 0))

    canvas = tk.Canvas(win, bg='white', height=340)
    canvas.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 8))

    button_frame = ttk.Frame(win, padding=(10, 0, 10, 10))
    button_frame.pack(fill=tk.X)
    start_button = ttk.Button(button_frame, text='Start', command=lambda: start_sim())
    stop_button = ttk.Button(button_frame, text='Stop', command=lambda: stop_sim())
    reset_button = ttk.Button(button_frame, text='Reset', command=lambda: reset_sim())
    start_button.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=4)
    stop_button.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=4)
    reset_button.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=4)

    state = {'omega': 0.0, 'theta': 0.0, 't': 0.0, 'running': False, 'job': None}
    energy_hist = {'rot': [], 't': []}
    DT = 0.03
    MAX_HISTORY = 300

    def compute_moi():
        m = mass.get()
        r = radius.get()
        return 0.5 * m * r * r

    def compute_alpha(I):
        return torque.get() / I if I != 0 else 0.0

    def draw_energy_graph():
        gx, gy = 20, max(160, canvas.winfo_height() - 130)
        gw, gh = max(300, canvas.winfo_width() - 40), 90
        canvas.create_rectangle(gx, gy, gx + gw, gy + gh, outline='black')

        if energy_hist['t']:
            tmax = max(0.1, energy_hist['t'][-1])
            vmax = max(0.5, max(energy_hist['rot'], default=0.5))
            for i in range(5):
                yy = gy + int(i * (gh / 4))
                value = vmax * (1 - i / 4)
                canvas.create_line(gx, yy, gx + gw, yy, fill='#dddddd')
                canvas.create_text(gx - 6, yy, text=f"{value:.1f}", anchor='e', font=('Courier', 8))

            for i in range(5):
                xx = gx + int(i * (gw / 4))
                time_label = tmax * i / 4
                canvas.create_line(xx, gy + gh, xx, gy + gh + 4, fill='black')
                canvas.create_text(xx, gy + gh + 16, text=f"{time_label:.1f}", font=('Courier', 8))

            for i in range(1, len(energy_hist['rot'])):
                x1 = gx + int(gw * energy_hist['t'][i - 1] / tmax)
                x2 = gx + int(gw * energy_hist['t'][i] / tmax)
                y1 = gy + gh - int(energy_hist['rot'][i - 1] / vmax * gh)
                y2 = gy + gh - int(energy_hist['rot'][i] / vmax * gh)
                canvas.create_line(x1, y1, x2, y2, fill='#1f77b4', width=2)

        canvas.create_text(gx + 6, gy - 10, anchor='w', text='Rotational kinetic energy (J)', font=('Arial', 9, 'bold'))
        canvas.create_text(gx + gw, gy + gh + 20, anchor='e', text='time (s)', font=('Arial', 9))

    def draw_scene():
        canvas.delete('all')
        width = max(420, canvas.winfo_width())
        height = max(340, canvas.winfo_height())
        disk_cx = width // 2
        disk_cy = 160
        pix_r = max(40, min(140, int(radius.get() * 110)))

        canvas.create_oval(
            disk_cx - pix_r,
            disk_cy - pix_r,
            disk_cx + pix_r,
            disk_cy + pix_r,
            outline='black',
            fill='#f0f0f0',
            width=2,
        )
        canvas.create_oval(disk_cx - 12, disk_cy - 12, disk_cx + 12, disk_cy + 12, fill='#333333')

        x = disk_cx + pix_r * math.cos(state['theta'])
        y = disk_cy - pix_r * math.sin(state['theta'])
        canvas.create_line(disk_cx, disk_cy, x, y, width=4, fill='#dd3333')
        canvas.create_line(disk_cx - pix_r - 10, disk_cy, disk_cx + pix_r + 10, disk_cy, dash=(4, 4), fill='#888888')
        canvas.create_line(disk_cx, disk_cy - pix_r - 10, disk_cx, disk_cy + pix_r + 10, dash=(4, 4), fill='#888888')

        arrow_x = disk_cx + pix_r + 20
        arrow_length = 60
        arrow_direction = 1 if torque.get() >= 0 else -1
        canvas.create_line(
            arrow_x,
            disk_cy,
            arrow_x + arrow_length * arrow_direction,
            disk_cy,
            arrow='last',
            width=4,
            fill='purple',
        )
        canvas.create_text(
            arrow_x + arrow_length * arrow_direction + 8 * arrow_direction,
            disk_cy,
            anchor='w' if torque.get() >= 0 else 'e',
            text=f"τ = {torque.get():.2f} N·m",
            fill='purple',
            font=('Arial', 10, 'bold'),
        )

        I = compute_moi()
        alpha = compute_alpha(I)
        ke = 0.5 * I * state['omega'] ** 2
        L = I * state['omega']

        lines = [
            f"Mass = {mass.get():.2f} kg",
            f"Radius = {radius.get():.2f} m",
            f"I = {I:.3f} kg·m²",
            f"Torque τ = {torque.get():.2f} N·m",
            f"Angular accel α = {alpha:.3f} rad/s²",
            f"Angular vel ω = {state['omega']:.3f} rad/s",
            f"Angular momentum L = {L:.3f} kg·m²/s",
            f"Rotational KE = {ke:.3f} J",
            f"Time = {state['t']:.2f} s",
        ]
        canvas.create_text(20, 18, anchor='nw', text="\n".join(lines), font=('Courier', 9), fill='black')

        draw_energy_graph()

    def _update_value_labels(*_args):
        mass_display.set(f"{mass.get():.2f} kg")
        radius_display.set(f"{radius.get():.2f} m")
        torque_display.set(f"{torque.get():.2f} N·m")
        draw_scene()

    mass.trace_add("write", _update_value_labels)
    radius.trace_add("write", _update_value_labels)
    torque.trace_add("write", _update_value_labels)
    _update_value_labels()

    def update_info_text():
        I = compute_moi()
        alpha = compute_alpha(I)
        ke = 0.5 * I * state['omega'] ** 2
        L = I * state['omega']
        info_text.set(
            f"t={state['t']:.2f}s   ω={state['omega']:.2f} rad/s   α={alpha:.2f} rad/s²   L={L:.2f} kg·m²/s   KE={ke:.2f} J"
        )

    def step():
        if not state['running']:
            return

        I = compute_moi()
        alpha = compute_alpha(I)
        state['omega'] += alpha * DT
        state['theta'] += state['omega'] * DT
        state['t'] += DT

        if len(energy_hist['t']) >= MAX_HISTORY:
            energy_hist['t'].pop(0)
            energy_hist['rot'].pop(0)
        energy_hist['t'].append(state['t'])
        energy_hist['rot'].append(0.5 * I * state['omega'] ** 2)

        draw_scene()
        update_info_text()
        state['job'] = win.after(int(DT * 1000), step)

    def start_sim():
        if not state['running']:
            state['running'] = True
            if state['job'] is None:
                state['job'] = win.after(int(DT * 1000), step)
            info_text.set('Running...')

    def stop_sim():
        state['running'] = False
        if state['job'] is not None:
            win.after_cancel(state['job'])
            state['job'] = None
        update_info_text()

    def reset_sim():
        stop_sim()
        state['omega'] = 0.0
        state['theta'] = 0.0
        state['t'] = 0.0
        energy_hist['rot'].clear()
        energy_hist['t'].clear()
        draw_scene()
        update_info_text()

    draw_scene()
    update_info_text()

    ttk.Label(control_frame, text="Radius").grid(row=1, column=0, sticky='w', pady=4)
    ttk.Scale(control_frame, from_=0.05, to=2.0, variable=radius, orient=tk.HORIZONTAL).grid(row=1, column=1, sticky='we', padx=(8, 8))
    ttk.Label(control_frame, textvariable=radius_display).grid(row=1, column=2, sticky='e')

    ttk.Label(control_frame, text="Applied torque").grid(row=2, column=0, sticky='w', pady=4)
    ttk.Scale(control_frame, from_=-10.0, to=10.0, variable=torque, orient=tk.HORIZONTAL).grid(row=2, column=1, sticky='we', padx=(8, 8))
    ttk.Label(control_frame, textvariable=torque_display).grid(row=2, column=2, sticky='e')

    status_frame = ttk.Frame(win, padding=(10, 0, 10, 6))
    status_frame.pack(fill=tk.X)
    info_text = tk.StringVar()
    ttk.Label(status_frame, textvariable=info_text, font=('Courier', 10)).pack(anchor='w')
    ttk.Label(
        status_frame,
        text="Start the simulation and watch how torque changes the disk rotation, angular momentum and kinetic energy.",
        wraplength=740,
    ).pack(anchor='w', pady=(4, 0))

    canvas = tk.Canvas(win, bg='white', height=340)
    canvas.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 8))

    button_frame = ttk.Frame(win, padding=(10, 0, 10, 10))
    button_frame.pack(fill=tk.X)
    start_button = ttk.Button(button_frame, text='Start', command=lambda: start_sim())
    stop_button = ttk.Button(button_frame, text='Stop', command=lambda: stop_sim())
    reset_button = ttk.Button(button_frame, text='Reset', command=lambda: reset_sim())
    start_button.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=4)
    stop_button.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=4)
    reset_button.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=4)

    state = {'omega': 0.0, 'theta': 0.0, 't': 0.0, 'running': False, 'job': None}
    energy_hist = {'rot': [], 't': []}
    DT = 0.03
    MAX_HISTORY = 300

    def compute_moi():
        m = mass.get()
        r = radius.get()
        return 0.5 * m * r * r

    def compute_alpha(I):
        return torque.get() / I if I != 0 else 0.0

    def draw_energy_graph():
        gx, gy = 20, max(160, canvas.winfo_height() - 130)
        gw, gh = max(300, canvas.winfo_width() - 40), 90
        canvas.create_rectangle(gx, gy, gx + gw, gy + gh, outline='black')

        if energy_hist['t']:
            tmax = max(0.1, energy_hist['t'][-1])
            vmax = max(0.5, max(energy_hist['rot'], default=0.5))
            for i in range(5):
                yy = gy + int(i * (gh / 4))
                value = vmax * (1 - i / 4)
                canvas.create_line(gx, yy, gx + gw, yy, fill='#dddddd')
                canvas.create_text(gx - 6, yy, text=f"{value:.1f}", anchor='e', font=('Courier', 8))

            for i in range(5):
                xx = gx + int(i * (gw / 4))
                time_label = tmax * i / 4
                canvas.create_line(xx, gy + gh, xx, gy + gh + 4, fill='black')
                canvas.create_text(xx, gy + gh + 16, text=f"{time_label:.1f}", font=('Courier', 8))

            for i in range(1, len(energy_hist['rot'])):
                x1 = gx + int(gw * energy_hist['t'][i - 1] / tmax)
                x2 = gx + int(gw * energy_hist['t'][i] / tmax)
                y1 = gy + gh - int(energy_hist['rot'][i - 1] / vmax * gh)
                y2 = gy + gh - int(energy_hist['rot'][i] / vmax * gh)
                canvas.create_line(x1, y1, x2, y2, fill='#1f77b4', width=2)

        canvas.create_text(gx + 6, gy - 10, anchor='w', text='Rotational kinetic energy (J)', font=('Arial', 9, 'bold'))
        canvas.create_text(gx + gw, gy + gh + 20, anchor='e', text='time (s)', font=('Arial', 9))

    def draw_scene():
        canvas.delete('all')
        width = max(420, canvas.winfo_width())
        height = max(340, canvas.winfo_height())
        disk_cx = width // 2
        disk_cy = 160
        pix_r = max(40, min(140, int(radius.get() * 110)))

        canvas.create_oval(
            disk_cx - pix_r,
            disk_cy - pix_r,
            disk_cx + pix_r,
            disk_cy + pix_r,
            outline='black',
            fill='#f0f0f0',
            width=2,
        )
        canvas.create_oval(disk_cx - 12, disk_cy - 12, disk_cx + 12, disk_cy + 12, fill='#333333')

        x = disk_cx + pix_r * math.cos(state['theta'])
        y = disk_cy - pix_r * math.sin(state['theta'])
        canvas.create_line(disk_cx, disk_cy, x, y, width=4, fill='#dd3333')
        canvas.create_line(disk_cx - pix_r - 10, disk_cy, disk_cx + pix_r + 10, disk_cy, dash=(4, 4), fill='#888888')
        canvas.create_line(disk_cx, disk_cy - pix_r - 10, disk_cx, disk_cy + pix_r + 10, dash=(4, 4), fill='#888888')

        arrow_x = disk_cx + pix_r + 20
        arrow_length = 60
        arrow_direction = 1 if torque.get() >= 0 else -1
        canvas.create_line(
            arrow_x,
            disk_cy,
            arrow_x + arrow_length * arrow_direction,
            disk_cy,
            arrow='last',
            width=4,
            fill='purple',
        )
        canvas.create_text(
            arrow_x + arrow_length * arrow_direction + 8 * arrow_direction,
            disk_cy,
            anchor='w' if torque.get() >= 0 else 'e',
            text=f"τ = {torque.get():.2f} N·m",
            fill='purple',
            font=('Arial', 10, 'bold'),
        )

        I = compute_moi()
        alpha = compute_alpha(I)
        ke = 0.5 * I * state['omega'] ** 2
        L = I * state['omega']

        lines = [
            f"Mass = {mass.get():.2f} kg",
            f"Radius = {radius.get():.2f} m",
            f"I = {I:.3f} kg·m²",
            f"Torque τ = {torque.get():.2f} N·m",
            f"Angular accel α = {alpha:.3f} rad/s²",
            f"Angular vel ω = {state['omega']:.3f} rad/s",
            f"Angular momentum L = {L:.3f} kg·m²/s",
            f"Rotational KE = {ke:.3f} J",
            f"Time = {state['t']:.2f} s",
        ]
        canvas.create_text(20, 18, anchor='nw', text="\n".join(lines), font=('Courier', 9), fill='black')

        draw_energy_graph()

    def update_info_text():
        I = compute_moi()
        alpha = compute_alpha(I)
        ke = 0.5 * I * state['omega'] ** 2
        L = I * state['omega']
        info_text.set(
            f"t={state['t']:.2f}s   ω={state['omega']:.2f} rad/s   α={alpha:.2f} rad/s²   L={L:.2f} kg·m²/s   KE={ke:.2f} J"
        )

    def step():
        if not state['running']:
            return

        I = compute_moi()
        alpha = compute_alpha(I)
        state['omega'] += alpha * DT
        state['theta'] += state['omega'] * DT
        state['t'] += DT

        if len(energy_hist['t']) >= MAX_HISTORY:
            energy_hist['t'].pop(0)
            energy_hist['rot'].pop(0)
        energy_hist['t'].append(state['t'])
        energy_hist['rot'].append(0.5 * I * state['omega'] ** 2)

        draw_scene()
        update_info_text()
        state['job'] = win.after(int(DT * 1000), step)

    def start_sim():
        if not state['running']:
            state['running'] = True
            if state['job'] is None:
                state['job'] = win.after(int(DT * 1000), step)
            info_text.set('Running...')

    def stop_sim():
        state['running'] = False
        if state['job'] is not None:
            win.after_cancel(state['job'])
            state['job'] = None
        update_info_text()

    def reset_sim():
        stop_sim()
        state['omega'] = 0.0
        state['theta'] = 0.0
        state['t'] = 0.0
        energy_hist['rot'].clear()
        energy_hist['t'].clear()
        draw_scene()
        update_info_text()

    draw_scene()
    update_info_text()
