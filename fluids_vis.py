import tkinter as tk
from tkinter import ttk


def open_fluids_window(master=None):
    win = tk.Toplevel(master) if master else tk.Tk()
    win.title("Fluids & Statics — Buoyancy & Pressure")
    win.geometry("800x420")

    header = ttk.Frame(win)
    header.pack(fill=tk.X)
    ttk.Label(header, text="Fluids & Statics — Buoyancy & Pressure", font=(None, 16, 'bold')).pack(anchor='n')
    ttk.Label(header, text="Shows hydrostatic pressure with depth (Pa) and buoyant force vs weight; toggles show whether an object floats or sinks.", wraplength=780).pack(anchor='n')

    frm = ttk.Frame(win, padding=8)
    frm.pack(fill=tk.BOTH, expand=True)

    depth = tk.DoubleVar(value=2.0)
    rho = tk.DoubleVar(value=1000.0)
    vol = tk.DoubleVar(value=0.01)
    mass = tk.DoubleVar(value=5.0)

    control = ttk.Frame(frm)
    control.pack(fill=tk.X)
    ttk.Label(control, text='Fluid density (kg/m³)').pack(side=tk.LEFT)
    ttk.Scale(control, from_=100, to=2000, variable=rho, orient=tk.HORIZONTAL, command=lambda e: update()).pack(side=tk.LEFT, fill=tk.X, expand=True)
    ttk.Label(control, textvariable=rho).pack(side=tk.LEFT, padx=6)

    ttk.Label(control, text='Depth (m)').pack(side=tk.LEFT, padx=(10,0))
    ttk.Scale(control, from_=0, to=50, variable=depth, orient=tk.HORIZONTAL, command=lambda e: update()).pack(side=tk.LEFT, fill=tk.X, expand=True)
    ttk.Label(control, textvariable=depth).pack(side=tk.LEFT, padx=6)

    ttk.Label(control, text='Volume (m³)').pack(side=tk.LEFT, padx=(10,0))
    ttk.Scale(control, from_=0.0001, to=1, variable=vol, orient=tk.HORIZONTAL, command=lambda e: update()).pack(side=tk.LEFT, fill=tk.X, expand=True)
    ttk.Label(control, textvariable=vol).pack(side=tk.LEFT, padx=6)

    ttk.Label(control, text='Mass (kg)').pack(side=tk.LEFT, padx=(10,0))
    ttk.Scale(control, from_=0.01, to=200, variable=mass, orient=tk.HORIZONTAL, command=lambda e: update()).pack(side=tk.LEFT, fill=tk.X, expand=True)
    ttk.Label(control, textvariable=mass).pack(side=tk.LEFT, padx=6)

    canvas = tk.Canvas(frm, bg='lightblue', height=260)
    canvas.pack(fill=tk.BOTH, expand=True, pady=8)

    info = ttk.Label(frm, text='')
    info.pack()

    state = {'y': 100.0, 'vy': 0.0}

    def update():
        d = depth.get(); R = rho.get(); V = vol.get(); m = mass.get()
        p = R * 9.81 * d
        buoy = R * 9.81 * V
        state_text = "Floats" if buoy > m*9.81 else "Sinks"
        info.config(text=f"Pressure at depth {d:.2f} m: {p:.2f} Pa   Buoyant: {buoy:.2f} N   Weight: {m*9.81:.2f} N → {state_text}")
        draw()

    def draw():
        canvas.delete('all')
        w = int(canvas.winfo_width() or 760)
        h = int(canvas.winfo_height() or 260)
        # draw water surface
        canvas.create_rectangle(0, 0, w, h, fill='lightblue', outline='')
        # draw pressure gradient bars on right
        # pressure gradient with metric labels
        for i in range(10):
            y = int(i*(h/10))
            depth_i = (i/10.0) * depth.get()
            p = rho.get()*9.81*depth_i
            shade = int(min(200, p/10))
            color = f"#{shade:02x}{(200-shade):02x}{(200):02x}"
            canvas.create_rectangle(w-80, y, w, y+(h/10), fill=color, outline='')
            # label pressure in Pa at intervals
            if i % 2 == 0:
                canvas.create_text(w-120, y+8, text=f"{p:.0f} Pa", anchor='w')

        # draw object as rectangle at vertical position depending on buoyant equilibrium
        # map physical depth to pixel height
        # simple equilibrium: buoyant force vs weight
        buoy = rho.get()*9.81*vol.get()
        if buoy > mass.get()*9.81:
            # floats: find submerged fraction
            submerged_frac = (mass.get()*9.81) / buoy
            submerged_pix = int(submerged_frac * 120)
            x0 = 50
            y0 = 80
            canvas.create_rectangle(x0, y0, x0+120, y0+120, fill='brown')
            # show submerged portion
            canvas.create_rectangle(x0, y0+120-submerged_pix, x0+120, y0+120, fill='darkblue', stipple='gray25')
            canvas.create_text(x0+10, y0+10, anchor='nw', text='Object (partial)')
        else:
            # sink: show fully submerged
            x0 = 50
            y0 = 80
            canvas.create_rectangle(x0, y0, x0+120, y0+120, fill='brown')
            canvas.create_text(x0+10, y0+10, anchor='nw', text='Object (sunk)')
        # label units
        canvas.create_text(10, h-10, anchor='sw', text=f"Fluid density: {rho.get():.0f} kg/m³   Depth: {depth.get():.2f} m   Buoyant force: {buoy:.2f} N")

    update()
