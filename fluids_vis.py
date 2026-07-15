"""Fluids and statics visualization: a water tank showing hydrostatic pressure,
buoyancy, and floating/sinking, with real cursor-driven sloshing physics."""

import math
import tkinter as tk
from tkinter import ttk

import viz_common

DT = 0.03
N_SURFACE = 48  # number of points across the water surface for the sloshing simulation


def open_fluids_window(master=None):
    """Create the buoyancy/pressure water-tank demo, matching the rest of the app's design."""
    win = tk.Toplevel(master) if master else tk.Tk()
    win.title("Fluids & Statics — Water Tank")
    win.geometry("1040x820+60+30")

    def _maximize_or_fullscreen_max(win_obj: tk.Toplevel):
        try:
            win_obj.state('zoomed')
        except Exception:
            pass
    win.after(100, lambda: _maximize_or_fullscreen_max(win))

    header = ttk.Frame(win)
    header.pack(fill=tk.X)
    ttk.Label(header, text="Fluids & Statics — Water Tank", font=(None, 16, 'bold')).pack(anchor='n')
    ttk.Label(
        header,
        text="A block floats or sinks depending on fluid density, its volume, and its mass. Click and drag "
             "the tank left and right to shake it — the water actually sloshes, driven by the same kind of "
             "wave physics as the ripple-tank demo, and the block bobs with the surface.",
        wraplength=1000,
    ).pack(anchor='n', pady=(4, 0))

    frm = ttk.Frame(win, padding=8)
    frm.pack(fill=tk.BOTH, expand=True)

    rho = tk.DoubleVar(value=1000.0)
    obj_vol = tk.DoubleVar(value=0.01)
    obj_mass = tk.DoubleVar(value=5.0)
    tank_depth = tk.DoubleVar(value=2.0)   # meters, for the pressure readout scale

    def _bind_display(var, display_var):
        def _update(*_a):
            display_var.set(f"{var.get():.2f}")
        var.trace_add("write", _update)
        _update()

    rho_display = tk.StringVar(); vol_display = tk.StringVar()
    mass_display = tk.StringVar(); depth_display = tk.StringVar()
    _bind_display(rho, rho_display); _bind_display(obj_vol, vol_display)
    _bind_display(obj_mass, mass_display); _bind_display(tank_depth, depth_display)

    control = ttk.Frame(frm)
    control.pack(fill=tk.X)
    ttk.Label(control, text='Fluid density (kg/m³)').pack(side=tk.LEFT)
    ttk.Scale(control, from_=500, to=2000, variable=rho, orient=tk.HORIZONTAL).pack(side=tk.LEFT, fill=tk.X, expand=True)
    ttk.Label(control, textvariable=rho_display).pack(side=tk.LEFT, padx=6)

    ttk.Label(control, text='Object volume (m³)').pack(side=tk.LEFT, padx=(10, 0))
    ttk.Scale(control, from_=0.001, to=0.05, variable=obj_vol, orient=tk.HORIZONTAL).pack(side=tk.LEFT, fill=tk.X, expand=True)
    ttk.Label(control, textvariable=vol_display).pack(side=tk.LEFT, padx=6)

    ttk.Label(control, text='Object mass (kg)').pack(side=tk.LEFT, padx=(10, 0))
    ttk.Scale(control, from_=0.1, to=60, variable=obj_mass, orient=tk.HORIZONTAL).pack(side=tk.LEFT, fill=tk.X, expand=True)
    ttk.Label(control, textvariable=mass_display).pack(side=tk.LEFT, padx=6)

    ttk.Label(control, text='Tank depth (m)').pack(side=tk.LEFT, padx=(10, 0))
    ttk.Scale(control, from_=0.5, to=5.0, variable=tank_depth, orient=tk.HORIZONTAL).pack(side=tk.LEFT, fill=tk.X, expand=True)
    ttk.Label(control, textvariable=depth_display).pack(side=tk.LEFT, padx=6)

    canvas = tk.Canvas(frm, bg='#eaf6ff', height=460, highlightthickness=0, cursor='fleur')
    canvas.pack(fill=tk.BOTH, expand=True, pady=8)

    # --- Equations panel ---
    eq_win, update_equations_text = viz_common.create_equations_panel(win, "Fluids & Statics")
    win.protocol("WM_DELETE_WINDOW", lambda: (eq_win.destroy(), win.destroy()))

    _FLUIDS_LEGEND = [('Weight (mg)', '#222222'), ('Buoyant force', '#1f8a3b')]

    # --- Sloshing surface: a 1D wave equation across the tank width, with
    # reflecting (Neumann) walls so the water can pile up against the glass
    # instead of being clamped to zero there. ---
    surface = [0.0] * N_SURFACE
    surface_prev = [0.0] * N_SURFACE
    slosh_c2 = 0.12
    slosh_damping = 0.975  # settle within a couple of seconds rather than several
    MAX_SURFACE_UNITS = 3.0  # hard cap so a hard shake can't visually blow past the tank walls

    drag = {'on': False, 'last_x': None, 'tank_offset': 0.0, 'tank_vel': 0.0}

    def slosh_step():
        nonlocal surface, surface_prev
        ext = [surface[1]] + surface + [surface[-2]]  # mirror (Neumann) boundary
        nxt = [0.0] * N_SURFACE
        for i in range(N_SURFACE):
            lap = ext[i] + ext[i + 2] - 2 * ext[i + 1]
            v = (2 * surface[i] - surface_prev[i] + slosh_c2 * lap) * slosh_damping
            # Hard safety clamp: a big/fast shake shouldn't be able to push the
            # rendered surface visually past the tank walls.
            nxt[i] = max(-MAX_SURFACE_UNITS, min(MAX_SURFACE_UNITS, v))
        surface_prev = surface
        surface = nxt

    def surface_height_at(frac):
        """Interpolated surface offset at horizontal fraction frac in [0,1]."""
        pos = frac * (N_SURFACE - 1)
        i0 = max(0, min(N_SURFACE - 2, int(pos)))
        t = pos - i0
        return surface[i0] * (1 - t) + surface[i0 + 1] * t

    def geometry(w, h):
        tank_x0, tank_x1 = w * 0.12, w * 0.88
        tank_y0, tank_y1 = h * 0.10, h * 0.86
        return tank_x0, tank_y0, tank_x1, tank_y1

    def draw_scene():
        canvas.delete('all')
        w = max(420, canvas.winfo_width())
        h = max(340, canvas.winfo_height())
        ground_y = h - 40
        viz_common.draw_backdrop(canvas, w, h, ground_y)

        tank_x0, tank_y0, tank_x1, tank_y1 = geometry(w, h)
        offset = drag['tank_offset']
        tank_x0 += offset
        tank_x1 += offset

        R = rho.get()
        V = obj_vol.get()
        m = obj_mass.get()
        buoy = R * 9.81 * V
        weight = m * 9.81
        floats = buoy > weight

        # water surface polygon (top edge follows the sloshing wave)
        water_top_base = tank_y0 + (tank_y1 - tank_y0) * 0.18
        n_pts = N_SURFACE
        surface_pts = []
        for i in range(n_pts):
            frac = i / (n_pts - 1)
            x = tank_x0 + frac * (tank_x1 - tank_x0)
            y = water_top_base + surface[i] * 22
            surface_pts.append((x, y))

        water_poly = surface_pts + [(tank_x1, tank_y1), (tank_x0, tank_y1)]
        canvas.create_polygon(*[c for p in water_poly for c in p], fill='#2ea3f2', outline='')

        # pressure-with-depth shading: a few translucent-look bands (solid blends since Tk has no alpha)
        bands = 6
        for i in range(bands):
            frac0 = i / bands
            frac1 = (i + 1) / bands
            y0 = water_top_base + frac0 * (tank_y1 - water_top_base)
            y1 = water_top_base + frac1 * (tank_y1 - water_top_base)
            shade = 0.55 + 0.35 * frac0
            col = f"#{int(30*shade):02x}{int(120*(1-frac0*0.5)):02x}{int(210*shade):02x}"
            canvas.create_rectangle(tank_x0, y0, tank_x1, y1, fill=col, outline='')

        # tank glass walls (drawn after water so they sit on top visually)
        canvas.create_rectangle(tank_x0, tank_y0, tank_x1, tank_y1, outline='#5a5f68', width=3)
        canvas.create_line(tank_x0, tank_y1, tank_x0, tank_y0 - 10, fill='#5a5f68', width=3)
        canvas.create_line(tank_x1, tank_y1, tank_x1, tank_y0 - 10, fill='#5a5f68', width=3)
        canvas.create_line(tank_x0, tank_y1, tank_x1, tank_y1, fill='#5a5f68', width=3)

        # floating / sinking object, bobbing with the local surface height
        obj_size = max(24, min(70, (V ** (1 / 3)) * 260))
        obj_frac_x = 0.5
        local_surface_y = water_top_base + surface_height_at(obj_frac_x) * 22
        if floats:
            submerged_frac = min(1.0, weight / buoy) if buoy > 1e-9 else 1.0
            obj_top = local_surface_y - obj_size * (1 - submerged_frac)
        else:
            obj_top = tank_y1 - obj_size - 4
        obj_cx = tank_x0 + obj_frac_x * (tank_x1 - tank_x0)
        ox0, oy0 = obj_cx - obj_size / 2, obj_top
        ox1, oy1 = obj_cx + obj_size / 2, obj_top + obj_size
        viz_common.draw_flat_block(canvas, ox0, oy0, ox1, oy1, m)

        box_cx, box_cy = (ox0 + ox1) / 2, (oy0 + oy1) / 2
        viz_common.draw_arrow(canvas, box_cx, box_cy, box_cx, box_cy + 50, '#222222', 2, f"W={weight:.2f} N")
        viz_common.draw_arrow(canvas, box_cx, box_cy, box_cx, box_cy - 50, '#1f8a3b', 2, f"F_b={buoy:.2f} N")

        viz_common.draw_legend(canvas, _FLUIDS_LEGEND, w)
        state_text = "Floats" if floats else "Sinks"
        viz_common.draw_readout(canvas, f"rho={R:.0f} kg/m^3  V={V:.4f} m^3  m={m:.2f} kg  Fb={buoy:.2f} N  W={weight:.2f} N -> {state_text}")

    def update_equations():
        R = rho.get(); V = obj_vol.get(); m = obj_mass.get(); d = tank_depth.get()
        p_bottom = R * 9.81 * d
        buoy = R * 9.81 * V
        weight = m * 9.81
        floats = buoy > weight
        lines = [
            "Hydrostatic pressure (Pascal's principle)",
            "  P = ρ g h",
            f"  = {R:.0f}×9.81×{d:.2f} = {p_bottom:.1f} Pa  (at the tank bottom)",
            "",
            "Archimedes' principle — buoyant force",
            "  F_b = ρ g V_displaced",
            f"  = {R:.0f}×9.81×{V:.4f} = {buoy:.2f} N",
            "",
            "Weight of the object",
            "  W = m g",
            f"  = {m:.2f}×9.81 = {weight:.2f} N",
            "",
            "Floating condition",
            "  F_b > W  →  floats;   F_b < W  →  sinks",
            f"  {buoy:.2f} N {'>' if floats else '<'} {weight:.2f} N  →  {'floats' if floats else 'sinks'}",
        ]
        if floats and buoy > 1e-9:
            frac = min(1.0, weight / buoy)
            lines += [
                "",
                "Submerged fraction at equilibrium (floating)",
                "  f = W / F_b_max = m g / (ρ g V)",
                f"  = {weight:.2f} / {R*9.81*V:.2f} = {frac:.2f}  ({frac*100:.0f}% submerged)",
            ]
        lines += [
            "",
            "Sloshing (shake the tank with your cursor!)",
            "  The surface follows a simplified 1D wave equation,",
            "  ∂²y/∂t² = c² ∂²y/∂x², driven by how fast you drag the",
            "  tank — the same physics family as the ripple-tank demo.",
        ]
        update_equations_text(lines)

    def refresh(*_a):
        draw_scene()
        update_equations()

    for var in (rho, obj_vol, obj_mass, tank_depth):
        var.trace_add("write", refresh)
    canvas.bind('<Configure>', refresh)

    # --- Shake the tank with the cursor ---
    def on_press(event):
        drag['on'] = True
        drag['last_x'] = event.x

    def on_drag(event):
        if not drag['on']:
            return
        dx = event.x - drag['last_x']
        drag['last_x'] = event.x
        drag['tank_vel'] += dx * 0.15
        drag['tank_vel'] = max(-40, min(40, drag['tank_vel']))
        # Accelerating the tank tilts the water surface (inertial pseudo-force
        # in the tank's frame) — inject a linear tilt across the array, not a
        # uniform shift. A uniform shift has zero curvature everywhere, so it
        # never engages the wave equation's spatial coupling term and the
        # "surface" just bobs rigidly instead of actually sloshing.
        impulse = max(-0.6, min(0.6, dx * 0.05))
        for i in range(N_SURFACE):
            tilt = (i / (N_SURFACE - 1) - 0.5) * 2.0  # -1 .. +1 across the tank
            surface_prev[i] -= impulse * tilt

    def on_release(_event):
        drag['on'] = False
        drag['last_x'] = None

    canvas.bind('<ButtonPress-1>', on_press)
    canvas.bind('<B1-Motion>', on_drag)
    canvas.bind('<ButtonRelease-1>', on_release)

    running = {'on': False}

    def step():
        if not running['on']:
            return
        slosh_step()
        # tank visually springs back toward center
        drag['tank_vel'] *= 0.9
        drag['tank_offset'] += drag['tank_vel'] * DT
        drag['tank_offset'] *= 0.9
        draw_scene()
        win.after(30, step)

    def start():
        if not running['on']:
            running['on'] = True
            step()

    def stop():
        running['on'] = False

    def reset():
        stop()
        for i in range(N_SURFACE):
            surface[i] = 0.0
            surface_prev[i] = 0.0
        drag['tank_offset'] = 0.0
        drag['tank_vel'] = 0.0
        refresh()

    btn_row = ttk.Frame(frm)
    btn_row.pack(fill=tk.X, pady=(0, 4))
    ttk.Button(btn_row, text='Reset', command=reset).pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=4)
    ttk.Button(btn_row, text='Start', command=start).pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=4)
    ttk.Button(btn_row, text='Stop', command=stop).pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=4)

    reset()
    start()
    return win
