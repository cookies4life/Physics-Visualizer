import tkinter as tk
from tkinter import ttk
import math
#energy vis spring vis

def open_energy_window(master=None):
    win = tk.Toplevel(master) if master else tk.Tk()
    win.title("Work, Energy & Power — Mass-Spring Demo")
    win.geometry("800x360")

    # Header and description
    header = ttk.Frame(win)
    header.pack(fill=tk.X)
    ttk.Label(header, text="Work, Energy & Power — Mass-Spring Demo", font=(None, 16, 'bold')).pack(anchor='n')
    ttk.Label(header, text="Animated mass-spring system showing kinetic and potential energies (in joules) over time.", wraplength=780).pack(anchor='n')

    frm = ttk.Frame(win, padding=8)
    frm.pack(fill=tk.BOTH, expand=True)

    mass = tk.DoubleVar(value=1.0)
    k = tk.DoubleVar(value=50.0)
    x0 = tk.DoubleVar(value=0.5)

    def _format_two_decimals(var):
        return f"{var.get():.2f}"

    control = ttk.Frame(frm)
    control.pack(fill=tk.X)

    mass_display = tk.StringVar()
    k_display = tk.StringVar()
    x0_display = tk.StringVar()

    def _update_value_display(*_args):
        mass_display.set(_format_two_decimals(mass))
        k_display.set(_format_two_decimals(k))
        x0_display.set(_format_two_decimals(x0))

    mass.trace_add("write", _update_value_display)
    k.trace_add("write", _update_value_display)
    x0.trace_add("write", _update_value_display)
    _update_value_display()

    ttk.Label(control, text='Mass (kg)').pack(side=tk.LEFT)
    ttk.Scale(control, from_=0.1, to=10, variable=mass, orient=tk.HORIZONTAL).pack(side=tk.LEFT, fill=tk.X, expand=True)
    ttk.Label(control, textvariable=mass_display).pack(side=tk.LEFT, padx=8)

    ttk.Label(control, text='k (N/m)').pack(side=tk.LEFT, padx=(10,0))
    ttk.Scale(control, from_=1, to=500, variable=k, orient=tk.HORIZONTAL).pack(side=tk.LEFT, fill=tk.X, expand=True)
    ttk.Label(control, textvariable=k_display).pack(side=tk.LEFT, padx=8)
    
    # initial displacement control
    ttk.Label(control, text='x0 (m)').pack(side=tk.LEFT, padx=(10,0))
    ttk.Scale(control, from_=-2.0, to=2.0, variable=x0, orient=tk.HORIZONTAL).pack(side=tk.LEFT, fill=tk.X, expand=True)
    ttk.Label(control, textvariable=x0_display).pack(side=tk.LEFT, padx=8)
    
    # Gravity and air resistance controls
    gravity = tk.BooleanVar(value=False)
    air = tk.BooleanVar(value=False)
    b = tk.DoubleVar(value=0.5)  # damping coefficient
    ttk.Checkbutton(control, text='Gravity', variable=gravity).pack(side=tk.LEFT, padx=(10,0))
    ttk.Checkbutton(control, text='Air Resist', variable=air).pack(side=tk.LEFT, padx=(6,0))
    ttk.Label(control, text='damping b').pack(side=tk.LEFT, padx=(6,0))
    ttk.Scale(control, from_=0.0, to=50.0, variable=b, orient=tk.HORIZONTAL).pack(side=tk.LEFT, fill=tk.X, expand=True)

    b_display = tk.StringVar()
    def _update_b_display(*_args):
        b_display.set(_format_two_decimals(b))

    b.trace_add("write", _update_b_display)
    _update_b_display()
    ttk.Label(control, textvariable=b_display).pack(side=tk.LEFT, padx=8)

    canvas = tk.Canvas(frm, bg='white', height=260)
    canvas.pack(fill=tk.BOTH, expand=True, pady=(8, 0))

    help_text = ttk.Label(frm, text="The wave-like spring shape shows how the mass stretches and compresses the spring over time; it is a visual of stored elastic energy.", wraplength=760, justify=tk.LEFT)
    help_text.pack(anchor='w', padx=8, pady=(4, 6))

    graph = tk.Canvas(frm, bg='white', height=100)
    graph.pack(fill=tk.BOTH)

    state = {'x': x0.get(), 'v': 0.0, 'running': False, 'deformed': False}
    energy_history = {'ke': [], 'pe': [], 't': []}

    def draw_spring(cnv, cx, y1, y2, deformed=False):
        # draw a vertical spring from y1 (anchor) to y2 (top of mass)
        if deformed:
            # draw a red stretched/broken spring
            cnv.create_line(cx, y1, cx, y2, fill='red', width=3, dash=(4,4))
            cnv.create_text(cx+60, y1+10, text='Spring deformed', fill='red', anchor='nw')
            return
        length = max(10, int(y2 - y1))
        coils = max(6, length // 8)
        amp = 12
        points = []
        for i in range(coils+1):
            t = i / coils
            y = int(y1 + t * (y2 - y1))
            x = cx + (amp if (i % 2 == 0) else -amp)
            points.append((x, y))
        # start and end anchors
        cnv.create_line(cx, y1, points[0][0], points[0][1], fill='black', width=2)
        for i in range(len(points)-1):
            cnv.create_line(points[i][0], points[i][1], points[i+1][0], points[i+1][1], fill='black', width=2)
        cnv.create_line(points[-1][0], points[-1][1], cx, y2, fill='black', width=2)

    def reset():
        state['x'] = x0.get()
        state['v'] = 0.0
        energy_history['ke'].clear(); energy_history['pe'].clear(); energy_history['t'].clear()
        # redraw static initial frame
        canvas.delete('all')
        # vertical spring: anchor at (cx, top)
        cx = int(canvas.winfo_width()/2) if canvas.winfo_width() else 200
        top = 20
        rest_pix = 80  # pixels at x=0
        scale = 120
        ypix = top + rest_pix + state['x']*scale
        # draw spring
        draw_spring(canvas, cx, top, ypix-30, deformed=state.get('deformed'))
        # draw mass
        rect_w = 60; rect_h = 40
        canvas.create_rectangle(cx-rect_w//2, ypix-20, cx+rect_w//2, ypix+20, fill='steelblue' if not state.get('deformed') else 'red')
        # show mass and weight inside box
        g = 9.81
        mval = mass.get()
        weight = mval * g
        canvas.create_text(cx, ypix, text=f"{mval:.2f} kg\n{weight:.2f} N", fill='white')
        draw_energy_graph()

    def step():
        if not state.get('running'):
            return
        m = mass.get(); kk = k.get()
        dt = 0.02
        g = 9.81 if gravity.get() else 0.0
        damping = b.get() if b.get() > 0 else 0.0

        # acceleration: m a = -k x - b v + m g
        a = (-kk * state['x'] - damping * state['v'] + m * g) / m
        state['v'] += a * dt
        state['x'] += state['v'] * dt

        # check static equilibrium and possible deformation
        if gravity.get():
            x_eq = (m * 9.81) / kk
        else:
            x_eq = 0.0
        max_safe = 1.0  # meters
        if x_eq > max_safe:
            state['deformed'] = True
            # allow mass to fall to a maximum extension
            max_extension = 1.5
            if state['x'] > max_extension:
                state['x'] = max_extension
                state['v'] = 0.0
                state['running'] = False
        else:
            state['deformed'] = False

        # draw spring-mass vertically
        canvas.delete('all')
        cx = int(canvas.winfo_width()/2) if canvas.winfo_width() else 200
        top = 20
        rest_pix = 80
        scale = 120
        ypix = top + rest_pix + state['x']*scale
        draw_spring(canvas, cx, top, ypix-30, deformed=state.get('deformed'))
        rect_w = 60; rect_h = 40
        canvas.create_rectangle(cx-rect_w//2, ypix-20, cx+rect_w//2, ypix+20, fill='steelblue' if not state.get('deformed') else 'red')
        mval = m
        weight = mval * 9.81
        canvas.create_text(cx, ypix, text=f"{mval:.2f} kg\n{weight:.2f} N", fill='white')
        canvas.create_text(10, 10, anchor='nw', text=f"x={state['x']:.2f} m  v={state['v']:.2f} m/s  a={a:.2f} m/s^2")

        # energies (spring PE + gravitational PE if enabled)
        ke = 0.5 * m * state['v']**2
        pe_spring = 0.5 * kk * state['x']**2
        pe_grav = m * 9.81 * state['x'] if gravity.get() else 0.0
        pe = pe_spring + pe_grav
        energy_history['ke'].append(ke)
        energy_history['pe'].append(pe)
        energy_history['t'].append(len(energy_history['t'])*dt if energy_history['t'] else 0.0)

        draw_energy_graph()
        if state.get('running'):
            win.after(int(dt*1000), step)

    def draw_energy_graph():
        graph.delete('all')
        ke = energy_history['ke']; pe = energy_history['pe']; t = energy_history['t']
        if not t:
            return
        w = int(graph.winfo_width() or graph['width'])
        h = int(graph.winfo_height() or graph['height'])
        pad = 6
        tmax = max(0.1, t[-1])
        vmax = max(max(ke) if ke else 1, max(pe) if pe else 1)
        # draw axes with metric ticks
        graph.create_line(pad, h-pad, w-pad, h-pad, fill='black')
        graph.create_line(pad, pad, pad, h-pad, fill='black')
        # y ticks and labels (energy in J)
        for i in range(5):
            yy = pad + i*(h-2*pad)/4
            val = vmax - (i*(vmax/4))
            graph.create_line(pad-5, int(yy), pad, int(yy), fill='black')
            graph.create_text(pad-30, int(yy), text=f"{val:.2f}")
        # plot curves
        for arr, color in ((ke,'blue'), (pe,'orange')):
            for i in range(1, len(arr)):
                x1 = int(pad + (t[i-1]/tmax)*(w-2*pad))
                x2 = int(pad + (t[i]/tmax)*(w-2*pad))
                y1 = int(h-pad - (arr[i-1]/vmax)*(h-2*pad))
                y2 = int(h-pad - (arr[i]/vmax)*(h-2*pad))
                graph.create_line(x1,y1,x2,y2, fill=color)
        graph.create_text(10,10, anchor='nw', text='KE (blue)  PE (orange)')
        graph.create_text(pad-20, h//2, text='Energy (J)', angle=90)
        graph.create_text(w//2, h-pad+12, text='time (s)')

    def start():
        if not state.get('running'):
            state['running'] = True
            step()

    def stop():
        state['running'] = False

    ttk.Button(frm, text='Reset', command=reset).pack(side=tk.LEFT, padx=6)
    ttk.Button(frm, text='Start', command=start).pack(side=tk.LEFT, padx=6)
    ttk.Button(frm, text='Stop', command=stop).pack(side=tk.LEFT)

    # when parameters change, reset the state so the effect is visible immediately
    def on_param_change(*args):
        reset()

    mass.trace_add('write', on_param_change)
    k.trace_add('write', on_param_change)
    x0.trace_add('write', on_param_change)
    gravity.trace_add('write', on_param_change)
    air.trace_add('write', on_param_change)
    b.trace_add('write', on_param_change)

    reset()
