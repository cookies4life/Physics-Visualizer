"""Rotational motion visualizations: a torque-driven spinning disk, and
centripetal force demonstrated with a spinning cup of water — vertical
(with gravity, showing why the water doesn't fall out at the top) and
horizontal (without gravity, showing the pure, unvarying centripetal case)."""

import math
import tkinter as tk
from tkinter import ttk

import viz_common

DT = 0.03
_TABLETOP_BG = '#e4e8ee'


def open_rotation_window(master=None):
    """Create the rotational motion window with a mode switch between the
    torque-driven disk demo and the centripetal-force cup-of-water demo."""
    win = tk.Toplevel(master) if master else tk.Tk()
    win.title("Rotational Motion")
    win.geometry("1080x900+60+30")

    def _maximize_or_fullscreen_max(win_obj: tk.Toplevel):
        try:
            win_obj.state('zoomed')
        except Exception:
            pass
    win.after(100, lambda: _maximize_or_fullscreen_max(win))

    header = ttk.Frame(win, padding=(10, 8))
    header.pack(fill=tk.X)
    ttk.Label(header, text="Rotational Motion", font=(None, 16, 'bold')).pack(anchor='n')
    desc_var = tk.StringVar()
    ttk.Label(header, textvariable=desc_var, wraplength=1020).pack(anchor='n', pady=(4, 0))

    mode = tk.StringVar(value='torque')       # 'torque' | 'centripetal'
    plane = tk.StringVar(value='vertical')    # 'vertical' | 'horizontal' (centripetal only)

    mode_row = ttk.Frame(win, padding=(10, 4))
    mode_row.pack(fill=tk.X)
    ttk.Label(mode_row, text="Mode:").pack(side=tk.LEFT)
    ttk.Radiobutton(mode_row, text='Torque & Angular Momentum (spinning disk)', variable=mode, value='torque').pack(side=tk.LEFT, padx=6)
    ttk.Radiobutton(mode_row, text='Centripetal Force (spinning cup of water)', variable=mode, value='centripetal').pack(side=tk.LEFT, padx=6)

    plane_row = ttk.Frame(win, padding=(10, 0, 10, 4))
    plane_row.pack(fill=tk.X)
    ttk.Label(plane_row, text="Spin plane:").pack(side=tk.LEFT)
    ttk.Radiobutton(plane_row, text='Vertical (with gravity)', variable=plane, value='vertical').pack(side=tk.LEFT, padx=6)
    ttk.Radiobutton(plane_row, text='Horizontal (no gravity)', variable=plane, value='horizontal').pack(side=tk.LEFT, padx=6)

    body = ttk.Frame(win)
    body.pack(fill=tk.BOTH, expand=True)

    # --- Equations panel, shared by both modes (content swaps with the mode) ---
    eq_win, update_equations_text = viz_common.create_equations_panel(win, "Rotational Motion", width=360, height=560)
    win.protocol("WM_DELETE_WINDOW", lambda: (eq_win.destroy(), win.destroy()))

    running = {'on': False}

    # =====================================================================
    # Mode 1: Torque-driven spinning disk
    # =====================================================================
    torque_page = ttk.Frame(body)

    t_control = ttk.Frame(torque_page, padding=(10, 8))
    t_control.pack(fill=tk.X)
    t_control.columnconfigure(1, weight=1)

    mass = tk.DoubleVar(value=2.0)
    radius = tk.DoubleVar(value=0.5)
    torque = tk.DoubleVar(value=1.0)

    def _bind_display(var, display_var, fmt="{:.2f}"):
        def _update(*_a):
            display_var.set(fmt.format(var.get()))
        var.trace_add("write", _update)
        _update()

    mass_display = tk.StringVar(); radius_display = tk.StringVar(); torque_display = tk.StringVar()
    _bind_display(mass, mass_display); _bind_display(radius, radius_display); _bind_display(torque, torque_display)

    ttk.Label(t_control, text="Mass").grid(row=0, column=0, sticky='w', pady=4)
    ttk.Scale(t_control, from_=0.1, to=20.0, variable=mass, orient=tk.HORIZONTAL).grid(row=0, column=1, sticky='we', padx=8)
    ttk.Label(t_control, textvariable=mass_display).grid(row=0, column=2, sticky='e')

    ttk.Label(t_control, text="Radius").grid(row=1, column=0, sticky='w', pady=4)
    ttk.Scale(t_control, from_=0.05, to=2.0, variable=radius, orient=tk.HORIZONTAL).grid(row=1, column=1, sticky='we', padx=8)
    ttk.Label(t_control, textvariable=radius_display).grid(row=1, column=2, sticky='e')

    ttk.Label(t_control, text="Applied torque").grid(row=2, column=0, sticky='w', pady=4)
    ttk.Scale(t_control, from_=-10.0, to=10.0, variable=torque, orient=tk.HORIZONTAL).grid(row=2, column=1, sticky='we', padx=8)
    ttk.Label(t_control, textvariable=torque_display).grid(row=2, column=2, sticky='e')

    t_canvas = tk.Canvas(torque_page, bg='#eaf6ff', height=460, highlightthickness=0)
    t_canvas.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 8))

    t_btn_row = ttk.Frame(torque_page, padding=(10, 0, 10, 10))
    t_btn_row.pack(fill=tk.X)

    t_state = {'omega': 0.0, 'theta': 0.0, 't': 0.0}
    t_energy_hist = {'rot': [], 't': []}
    MAX_HISTORY = 300
    _TORQUE_LEGEND = [('Applied torque', '#7c4fd6'), ('Angular momentum arm', '#c1440e')]

    def compute_moi():
        return 0.5 * mass.get() * radius.get() ** 2

    def compute_alpha(I):
        return torque.get() / I if I != 0 else 0.0

    def draw_torque_graph(w, h):
        gx, gy = 20, h - 130
        gw, gh = max(300, w - 220), 100
        t_canvas.create_rectangle(gx, gy, gx + gw, gy + gh, outline='#333333', fill='white')
        if t_energy_hist['t']:
            tmax = max(0.1, t_energy_hist['t'][-1])
            vmax = max(0.5, max(t_energy_hist['rot'], default=0.5))
            for i in range(5):
                yy = gy + int(i * (gh / 4))
                val = vmax * (1 - i / 4)
                t_canvas.create_line(gx, yy, gx + gw, yy, fill='#dddddd')
                t_canvas.create_text(gx - 6, yy, text=f"{val:.1f}", anchor='e', font=('Courier', 8))
            for i in range(1, len(t_energy_hist['rot'])):
                x1 = gx + int(gw * t_energy_hist['t'][i - 1] / tmax)
                x2 = gx + int(gw * t_energy_hist['t'][i] / tmax)
                y1 = gy + gh - int(t_energy_hist['rot'][i - 1] / vmax * gh)
                y2 = gy + gh - int(t_energy_hist['rot'][i] / vmax * gh)
                t_canvas.create_line(x1, y1, x2, y2, fill='#1d4fd8', width=2)
        t_canvas.create_text(gx + 6, gy - 10, anchor='w', text='Rotational KE (J) vs time', font=('Arial', 9, 'bold'))

    def draw_torque_scene():
        t_canvas.delete('all')
        w = max(420, t_canvas.winfo_width())
        h = max(340, t_canvas.winfo_height())
        viz_common.draw_sky(t_canvas, w, h, h)

        cx, cy = w // 2, 180
        pix_r = max(50, min(160, int(radius.get() * 110)))

        # a simple wall bracket the disk is mounted on
        t_canvas.create_rectangle(cx - 14, 20, cx + 14, cy - pix_r + 6, fill='#8a8f98', outline='#5a5f68')
        t_canvas.create_oval(cx - pix_r, cy - pix_r, cx + pix_r, cy + pix_r, outline='#333333', fill='#f4f4f4', width=2)
        t_canvas.create_oval(cx - 12, cy - 12, cx + 12, cy + 12, fill='#333333')

        x = cx + pix_r * math.cos(t_state['theta'])
        y = cy - pix_r * math.sin(t_state['theta'])
        viz_common.draw_arrow(t_canvas, cx, cy, x, y, '#c1440e', 4)
        t_canvas.create_line(cx - pix_r - 10, cy, cx + pix_r + 10, cy, dash=(4, 4), fill='#8a8f98')
        t_canvas.create_line(cx, cy - pix_r - 10, cx, cy + pix_r + 10, dash=(4, 4), fill='#8a8f98')

        arrow_x = cx + pix_r + 20
        direction = 1 if torque.get() >= 0 else -1
        viz_common.draw_arrow(t_canvas, arrow_x, cy, arrow_x + 60 * direction, cy, '#7c4fd6', 4, f"τ={torque.get():.2f} N·m")

        viz_common.draw_legend(t_canvas, _TORQUE_LEGEND, w)

        I = compute_moi()
        alpha = compute_alpha(I)
        ke = 0.5 * I * t_state['omega'] ** 2
        L = I * t_state['omega']
        viz_common.draw_readout(t_canvas, f"I={I:.3f} kg*m^2  a={alpha:.2f} rad/s^2  w={t_state['omega']:.2f} rad/s  L={L:.2f} kg*m^2/s  KE={ke:.2f} J  t={t_state['t']:.2f}s")

        draw_torque_graph(w, h)

    def update_torque_equations():
        I = compute_moi()
        alpha = compute_alpha(I)
        ke = 0.5 * I * t_state['omega'] ** 2
        L = I * t_state['omega']
        lines = [
            "Moment of inertia (solid disk)",
            "  I = 1/2 m r²",
            f"  = 0.5×{mass.get():.2f}×{radius.get():.2f}²",
            f"  = {I:.3f} kg·m²",
            "",
            "Newton's 2nd law for rotation",
            "  τ = I α  →  α = τ / I",
            f"  α = {torque.get():.2f} / {I:.3f} = {alpha:.3f} rad/s²",
            "",
            "Kinematics",
            f"  ω = {t_state['omega']:.3f} rad/s",
            f"  θ = {math.degrees(t_state['theta']) % 360:.1f}°",
            "",
            "Angular momentum",
            "  L = I ω",
            f"  = {I:.3f}×{t_state['omega']:.3f} = {L:.3f} kg·m²/s",
            "",
            "Rotational kinetic energy",
            "  KE = 1/2 I ω²",
            f"  = 0.5×{I:.3f}×{t_state['omega']:.3f}² = {ke:.3f} J",
        ]
        update_equations_text(lines)

    def torque_step():
        if not running['on'] or mode.get() != 'torque':
            return
        I = compute_moi()
        alpha = compute_alpha(I)
        t_state['omega'] += alpha * DT
        t_state['theta'] += t_state['omega'] * DT
        t_state['t'] += DT
        if len(t_energy_hist['t']) >= MAX_HISTORY:
            t_energy_hist['t'].pop(0); t_energy_hist['rot'].pop(0)
        t_energy_hist['t'].append(t_state['t'])
        t_energy_hist['rot'].append(0.5 * I * t_state['omega'] ** 2)
        draw_torque_scene()
        update_torque_equations()
        win.after(int(DT * 1000), torque_step)

    def torque_reset():
        t_state['omega'] = 0.0; t_state['theta'] = 0.0; t_state['t'] = 0.0
        t_energy_hist['rot'].clear(); t_energy_hist['t'].clear()
        draw_torque_scene()
        update_torque_equations()

    ttk.Button(t_btn_row, text='Reset', command=torque_reset).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=4)
    ttk.Button(t_btn_row, text='Start', command=lambda: (running.update(on=True), torque_step())).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=4)
    ttk.Button(t_btn_row, text='Stop', command=lambda: running.update(on=False)).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=4)

    for var in (mass, radius, torque):
        var.trace_add('write', lambda *_a: (draw_torque_scene(), update_torque_equations()) if mode.get() == 'torque' else None)
    t_canvas.bind('<Configure>', lambda _e: (draw_torque_scene(), update_torque_equations()) if mode.get() == 'torque' else None)

    # =====================================================================
    # Mode 2: Centripetal force — spinning cup of water
    # =====================================================================
    centripetal_page = ttk.Frame(body)

    c_control = ttk.Frame(centripetal_page, padding=(10, 8))
    c_control.pack(fill=tk.X)
    c_control.columnconfigure(1, weight=1)

    c_mass = tk.DoubleVar(value=0.6)     # kg, cup + water
    c_radius = tk.DoubleVar(value=0.7)   # m, string/arm length
    c_omega = tk.DoubleVar(value=4.0)    # rad/s
    c_gravity = tk.DoubleVar(value=9.81)

    c_mass_display = tk.StringVar(); c_radius_display = tk.StringVar()
    c_omega_display = tk.StringVar(); c_gravity_display = tk.StringVar()
    _bind_display(c_mass, c_mass_display); _bind_display(c_radius, c_radius_display)
    _bind_display(c_omega, c_omega_display); _bind_display(c_gravity, c_gravity_display)

    ttk.Label(c_control, text="Mass (cup + water, kg)").grid(row=0, column=0, sticky='w', pady=4)
    ttk.Scale(c_control, from_=0.1, to=5.0, variable=c_mass, orient=tk.HORIZONTAL).grid(row=0, column=1, sticky='we', padx=8)
    ttk.Label(c_control, textvariable=c_mass_display).grid(row=0, column=2, sticky='e')

    ttk.Label(c_control, text="Radius (arm/string length, m)").grid(row=1, column=0, sticky='w', pady=4)
    ttk.Scale(c_control, from_=0.2, to=1.5, variable=c_radius, orient=tk.HORIZONTAL).grid(row=1, column=1, sticky='we', padx=8)
    ttk.Label(c_control, textvariable=c_radius_display).grid(row=1, column=2, sticky='e')

    ttk.Label(c_control, text="Spin rate ω (rad/s)").grid(row=2, column=0, sticky='w', pady=4)
    ttk.Scale(c_control, from_=0.0, to=15.0, variable=c_omega, orient=tk.HORIZONTAL).grid(row=2, column=1, sticky='we', padx=8)
    ttk.Label(c_control, textvariable=c_omega_display).grid(row=2, column=2, sticky='e')

    gravity_row = ttk.Frame(c_control)
    gravity_row.grid(row=3, column=0, columnspan=3, sticky='we')
    gravity_row.columnconfigure(1, weight=1)
    gravity_label = ttk.Label(gravity_row, text="Gravity (m/s²)")
    gravity_label.grid(row=0, column=0, sticky='w', pady=4)
    gravity_scale = ttk.Scale(gravity_row, from_=0.0, to=20.0, variable=c_gravity, orient=tk.HORIZONTAL)
    gravity_scale.grid(row=0, column=1, sticky='we', padx=8)
    ttk.Label(gravity_row, textvariable=c_gravity_display).grid(row=0, column=2, sticky='e')

    c_canvas = tk.Canvas(centripetal_page, bg='#eaf6ff', height=460, highlightthickness=0)
    c_canvas.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 8))

    c_btn_row = ttk.Frame(centripetal_page, padding=(10, 0, 10, 10))
    c_btn_row.pack(fill=tk.X)

    c_state = {'theta': math.pi / 2, 't': 0.0}  # start at the top for vertical mode drama
    _CENTRIPETAL_LEGEND_V = [('Weight (mg)', '#222222'), ('Normal force (cup on water)', '#1f8a3b'), ('Centrifugal (apparent)', '#d9740c')]
    _CENTRIPETAL_LEGEND_H = [('Normal force (cup on water)', '#1f8a3b'), ('Centrifugal (apparent)', '#d9740c')]

    def compute_centripetal(theta):
        m = c_mass.get(); r = c_radius.get(); omega = c_omega.get()
        vertical = plane.get() == 'vertical'
        g = c_gravity.get() if vertical else 0.0
        ac = omega * omega * r
        Fc = m * ac
        g_radial = m * g * math.sin(theta) if vertical else 0.0
        N = Fc - g_radial
        omega_min = math.sqrt(g / r) if (vertical and r > 1e-9) else 0.0
        v_min = omega_min * r
        return {'m': m, 'r': r, 'omega': omega, 'g': g, 'ac': ac, 'Fc': Fc,
                'g_radial': g_radial, 'N': N, 'omega_min': omega_min, 'v_min': v_min, 'vertical': vertical}

    def draw_cup(cx, cy, dir_x, dir_y, spilling):
        """Draw a small cup at (cx,cy) with its opening facing the pivot (-dir)."""
        # dir points from pivot to cup (outward); the cup opening faces inward (-dir)
        perp_x, perp_y = -dir_y, dir_x
        half_w = 20
        depth = 26
        base = (cx + dir_x * depth * 0.5, cy + dir_y * depth * 0.5)
        mouth_l = (cx - dir_x * depth * 0.5 + perp_x * half_w, cy - dir_y * depth * 0.5 + perp_y * half_w)
        mouth_r = (cx - dir_x * depth * 0.5 - perp_x * half_w, cy - dir_y * depth * 0.5 - perp_y * half_w)
        base_l = (base[0] + perp_x * half_w * 0.7, base[1] + perp_y * half_w * 0.7)
        base_r = (base[0] - perp_x * half_w * 0.7, base[1] - perp_y * half_w * 0.7)
        c_canvas.create_polygon(mouth_l[0], mouth_l[1], mouth_r[0], mouth_r[1], base_r[0], base_r[1], base_l[0], base_l[1],
                                 fill='#c7ccd4', outline='#5a5f68', width=2)
        # water fill (a slightly inset polygon), always pressed toward the outward wall
        water_l = (mouth_l[0] + (base_l[0] - mouth_l[0]) * 0.15, mouth_l[1] + (base_l[1] - mouth_l[1]) * 0.15)
        water_r = (mouth_r[0] + (base_r[0] - mouth_r[0]) * 0.15, mouth_r[1] + (base_r[1] - mouth_r[1]) * 0.15)
        water_color = '#c1440e' if spilling else '#2ea3f2'
        c_canvas.create_polygon(water_l[0], water_l[1], water_r[0], water_r[1], base_r[0], base_r[1], base_l[0], base_l[1],
                                 fill=water_color, outline='')
        if spilling:
            for f in (-0.5, 0.0, 0.5):
                dx = perp_x * half_w * f
                dy = perp_y * half_w * f
                c_canvas.create_oval(cx + dx - 3, cy + dy - 22, cx + dx + 3, cy + dy - 16, fill='#2ea3f2', outline='')
        return (cx, cy)

    def draw_centripetal_scene():
        c_canvas.delete('all')
        w = max(420, c_canvas.winfo_width())
        h = max(340, c_canvas.winfo_height())
        vertical = plane.get() == 'vertical'

        if vertical:
            ground_y = h - 60
            viz_common.draw_backdrop(c_canvas, w, h, ground_y)
            pivot_x, pivot_y = w // 2, ground_y - 260
            c_canvas.create_oval(pivot_x - 6, pivot_y - 6, pivot_x + 6, pivot_y + 6, fill='#333333')
        else:
            c_canvas.create_rectangle(0, 0, w, h, fill=_TABLETOP_BG, outline='')
            pivot_x, pivot_y = w // 2, h // 2
            for rr in (60, 120, 180):
                c_canvas.create_oval(pivot_x - rr, pivot_y - rr, pivot_x + rr, pivot_y + rr, outline='#c7ccd4', dash=(3, 4))
            c_canvas.create_oval(pivot_x - 6, pivot_y - 6, pivot_x + 6, pivot_y + 6, fill='#333333')

        pix_r = max(70, min(220, c_radius.get() * 180))
        theta = c_state['theta']
        cx = pivot_x + pix_r * math.cos(theta)
        cy = pivot_y - pix_r * math.sin(theta)
        dir_x = math.cos(theta)
        dir_y = -math.sin(theta)

        c_canvas.create_oval(pivot_x - pix_r, pivot_y - pix_r, pivot_x + pix_r, pivot_y + pix_r, outline='#8a8f98', dash=(3, 4))
        c_canvas.create_line(pivot_x, pivot_y, cx, cy, fill='#5a5f68', width=2)

        vals = compute_centripetal(theta)
        spilling = vertical and vals['N'] < 0

        draw_cup(cx, cy, dir_x, dir_y, spilling)

        toward_x, toward_y = -dir_x, -dir_y  # unit vector toward the pivot (centripetal direction)
        arrow_scale = 6.0

        if vertical:
            viz_common.draw_arrow(c_canvas, cx, cy, cx, cy + vals['m'] * vals['g'] * arrow_scale * 0.6, '#222222', 2, f"W={vals['m'] * vals['g']:.2f} N")
        n_mag = max(0.0, vals['N'])
        if n_mag > 1e-6:
            viz_common.draw_arrow(c_canvas, cx, cy, cx + toward_x * n_mag * arrow_scale, cy + toward_y * n_mag * arrow_scale, '#1f8a3b', 3, f"N={vals['N']:.2f} N")
        viz_common.draw_arrow(c_canvas, cx, cy, cx - toward_x * vals['Fc'] * arrow_scale * 0.7, cy - toward_y * vals['Fc'] * arrow_scale * 0.7, '#d9740c', 3, f"F_cf={vals['Fc']:.2f} N")

        viz_common.draw_legend(c_canvas, _CENTRIPETAL_LEGEND_V if vertical else _CENTRIPETAL_LEGEND_H, w)

        status = ""
        if vertical:
            status = "  |  WATER SPILLING!" if spilling else f"  |  min ω to stay in = {vals['omega_min']:.2f} rad/s"
        viz_common.draw_readout(c_canvas, f"theta={math.degrees(theta) % 360:.0f} deg  N={vals['N']:.2f} N  Fc={vals['Fc']:.2f} N{status}")

    def update_centripetal_equations():
        vals = compute_centripetal(c_state['theta'])
        theta_deg = math.degrees(c_state['theta']) % 360
        if vals['vertical']:
            lines = [
                "Centripetal acceleration",
                "  a_c = ω² r",
                f"  = {vals['omega']:.2f}²×{vals['r']:.2f} = {vals['ac']:.2f} m/s²",
                "",
                "Required centripetal force",
                "  F_c = m ω² r",
                f"  = {vals['m']:.2f}×{vals['ac']:.2f} = {vals['Fc']:.2f} N",
                "",
                "Gravity's pull toward the center (changes with angle)",
                "  = mg sinθ",
                f"  = {vals['m']:.2f}×{vals['g']:.2f}×sin({theta_deg:.0f}°) = {vals['g_radial']:.2f} N",
                "",
                "Normal force from the cup (Newton's 2nd law, radial)",
                "  N + mg sinθ = m ω² r",
                f"  N = {vals['Fc']:.2f} − ({vals['g_radial']:.2f}) = {vals['N']:.2f} N",
            ]
            if vals['N'] < 0:
                lines.append("  → N can't be negative — the water leaves the cup here!")
            else:
                lines.append("  → N ≥ 0, so the cup can hold the water in.")
            lines += [
                "",
                "Minimum spin rate so water stays in at the top",
                "  ω_min = sqrt(g / r)",
                f"  = sqrt({vals['g']:.2f} / {vals['r']:.2f}) = {vals['omega_min']:.2f} rad/s",
                f"  (v_min = sqrt(g r) = {vals['v_min']:.2f} m/s)",
                "",
                "Centrifugal force — apparent only",
                "  Felt inside the spinning cup's frame, always equal and",
                "  opposite to the true centripetal force. It is not a real",
                "  Newtonian force — nothing is actually pulling outward.",
                f"  magnitude = m ω² r = {vals['Fc']:.2f} N",
            ]
        else:
            lines = [
                "No gravity in this mode — the water's centripetal force",
                "comes entirely from the cup wall, and doesn't change as",
                "the cup goes around (contrast with the vertical case).",
                "",
                "Centripetal acceleration",
                "  a_c = ω² r",
                f"  = {vals['omega']:.2f}²×{vals['r']:.2f} = {vals['ac']:.2f} m/s²",
                "",
                "Required centripetal force = Normal force from the cup",
                "  F_c = N = m ω² r",
                f"  = {vals['m']:.2f}×{vals['ac']:.2f} = {vals['Fc']:.2f} N  (same at every angle)",
                "",
                "Centrifugal force — apparent only",
                "  Felt inside the spinning cup's frame, always equal and",
                "  opposite to the true centripetal force. It is not a real",
                "  Newtonian force — nothing is actually pulling outward.",
                f"  magnitude = m ω² r = {vals['Fc']:.2f} N",
            ]
        update_equations_text(lines)

    def centripetal_step():
        if not running['on'] or mode.get() != 'centripetal':
            return
        c_state['theta'] += c_omega.get() * DT
        c_state['t'] += DT
        draw_centripetal_scene()
        update_centripetal_equations()
        win.after(int(DT * 1000), centripetal_step)

    def centripetal_reset():
        c_state['theta'] = math.pi / 2
        c_state['t'] = 0.0
        draw_centripetal_scene()
        update_centripetal_equations()

    ttk.Button(c_btn_row, text='Reset', command=centripetal_reset).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=4)
    ttk.Button(c_btn_row, text='Start', command=lambda: (running.update(on=True), centripetal_step())).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=4)
    ttk.Button(c_btn_row, text='Stop', command=lambda: running.update(on=False)).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=4)

    for var in (c_mass, c_radius, c_omega, c_gravity, plane):
        var.trace_add('write', lambda *_a: (draw_centripetal_scene(), update_centripetal_equations()) if mode.get() == 'centripetal' else None)
    c_canvas.bind('<Configure>', lambda _e: (draw_centripetal_scene(), update_centripetal_equations()) if mode.get() == 'centripetal' else None)

    # =====================================================================
    # Mode switching
    # =====================================================================

    def refresh_mode(*_a):
        running.update(on=False)
        is_centripetal = mode.get() == 'centripetal'
        if is_centripetal:
            torque_page.pack_forget()
            plane_row.pack(fill=tk.X)
            gravity_row.grid()
            is_vertical = plane.get() == 'vertical'
            gravity_label.grid() if is_vertical else gravity_label.grid_remove()
            gravity_scale.grid() if is_vertical else gravity_scale.grid_remove()
            centripetal_page.pack(fill=tk.BOTH, expand=True)
            desc_var.set(
                "Spin a cup of water in a circle. In the vertical plane, gravity fights the required "
                "centripetal force — watch the normal force drop (and the water spill) if you spin too "
                "slowly near the top. In the horizontal plane there's no gravity to fight, so the force "
                "stays constant all the way around.")
            centripetal_reset()
        else:
            centripetal_page.pack_forget()
            plane_row.pack_forget()
            torque_page.pack(fill=tk.BOTH, expand=True)
            desc_var.set(
                "Use mass, radius, and torque to see how angular acceleration, angular momentum, and "
                "rotational kinetic energy build up in a spinning disk.")
            torque_reset()

    mode.trace_add('write', refresh_mode)
    plane.trace_add('write', refresh_mode)
    refresh_mode()

    return win
