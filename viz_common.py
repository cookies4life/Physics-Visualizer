"""Shared drawing and UI helpers used across the physics visualizer's demos.

Keeping this in one place is what lets the different demo windows (Newton's
incline/flat force demos, the spring-mass energy demo, projectile
kinematics, ...) share one consistent look and one consistent way of
presenting the equations being demonstrated.
"""

import math
import tkinter as tk
from tkinter import ttk


def create_equations_panel(win, title, width=340, height=480):
    """Create a small companion window beside `win` that shows live equations.

    Returns an `update(lines)` callable — pass it a list of strings (one per
    line) each time the simulation state changes, and it replaces the
    panel's text. Text is explicitly black-on-light so it stays readable
    regardless of the platform's default Text widget colors.
    """
    win.update_idletasks()
    eq_win = tk.Toplevel(win)
    eq_win.title(f"{title} — Equations")
    x = win.winfo_x() + win.winfo_width() + 14
    y = win.winfo_y()
    eq_win.geometry(f"{width}x{height}+{x}+{y}")
    eq_win.resizable(False, False)

    frame = ttk.Frame(eq_win, padding=10)
    frame.pack(fill=tk.BOTH, expand=True)
    ttk.Label(frame, text="Equations Being Demonstrated", font=(None, 12, 'bold'), wraplength=width - 30).pack(anchor='w')
    text = tk.Text(
        frame, width=max(20, width // 9), height=max(10, height // 17), font=('Courier', 10),
        bg='#f7f6f2', fg='black', insertbackground='black', relief=tk.FLAT, wrap='word')
    text.pack(fill=tk.BOTH, expand=True, pady=(8, 0))
    text.config(state='disabled')

    def update(lines):
        text.config(state='normal')
        text.delete('1.0', tk.END)
        text.insert('1.0', "\n".join(lines))
        text.config(state='disabled')

    return eq_win, update


def draw_sky(canvas, canvas_w, canvas_h, horizon_y):
    """Draw a soft sky gradient from the top of the canvas down to horizon_y."""
    sky_top = (0xea, 0xf6, 0xff)
    sky_bottom = (0xff, 0xff, 0xff)
    bands = 8
    band_h = max(1, horizon_y // bands)
    for i in range(bands):
        t = i / (bands - 1)
        r = round(sky_top[0] + (sky_bottom[0] - sky_top[0]) * t)
        g = round(sky_top[1] + (sky_bottom[1] - sky_top[1]) * t)
        b = round(sky_top[2] + (sky_bottom[2] - sky_top[2]) * t)
        canvas.create_rectangle(0, i * band_h, canvas_w, (i + 1) * band_h + 1, fill=f'#{r:02x}{g:02x}{b:02x}', outline='')


def draw_backdrop(canvas, canvas_w, canvas_h, ground_y):
    """Draw a soft sky gradient above ground_y and a grassy strip below it."""
    draw_sky(canvas, canvas_w, canvas_h, ground_y)
    canvas.create_rectangle(0, ground_y, canvas_w, canvas_h, fill='#8fbf6b', outline='')
    canvas.create_line(0, ground_y, canvas_w, ground_y, fill='#5f8f45', width=2)
    for gx in range(0, canvas_w, 18):
        canvas.create_line(gx, ground_y, gx + 6, ground_y + 10, fill='#5f8f45', width=1)


def draw_road(canvas, canvas_w, canvas_h, road_y):
    """Draw a sky gradient above road_y and an asphalt road (with lane dashes)
    spanning the full canvas width below it."""
    draw_sky(canvas, canvas_w, canvas_h, road_y)
    canvas.create_rectangle(0, road_y, canvas_w, canvas_h, fill='#4a4a4d', outline='')
    canvas.create_line(0, road_y, canvas_w, road_y, fill='#2e2e30', width=3)
    canvas.create_line(0, canvas_h - 1, canvas_w, canvas_h - 1, fill='#2e2e30', width=3)
    dash_w, gap_w = 26, 18
    dash_y = road_y + (canvas_h - road_y) / 2
    x = 0
    while x < canvas_w:
        canvas.create_line(x, dash_y, x + dash_w, dash_y, fill='#f2d24b', width=3)
        x += dash_w + gap_w


def draw_football_field(canvas, canvas_w, canvas_h, ground_y):
    """Draw a sky gradient above ground_y and a football field (end zones, yard
    lines, hash marks) spanning the full canvas width below it."""
    draw_sky(canvas, canvas_w, canvas_h, ground_y)
    canvas.create_rectangle(0, ground_y, canvas_w, canvas_h, fill='#2e7d32', outline='')
    canvas.create_line(0, ground_y, canvas_w, ground_y, fill='#ffffff', width=2)

    endzone_w = min(50, canvas_w * 0.06)
    canvas.create_rectangle(0, ground_y, endzone_w, canvas_h, fill='#1b4d20', outline='')
    canvas.create_rectangle(canvas_w - endzone_w, ground_y, canvas_w, canvas_h, fill='#1b4d20', outline='')
    canvas.create_line(endzone_w, ground_y, endzone_w, canvas_h, fill='white', width=2)
    canvas.create_line(canvas_w - endzone_w, ground_y, canvas_w - endzone_w, canvas_h, fill='white', width=2)

    field_h = canvas_h - ground_y
    spacing = 40
    x = endzone_w
    while x < canvas_w - endzone_w:
        canvas.create_line(x, ground_y, x, canvas_h, fill='white', width=1)
        canvas.create_line(x, ground_y + field_h * 0.3, x + 8, ground_y + field_h * 0.3, fill='white', width=1)
        canvas.create_line(x, ground_y + field_h * 0.7, x + 8, ground_y + field_h * 0.7, fill='white', width=1)
        x += spacing


def draw_football(canvas, cx, cy, length, width, angle_rad, color='#7b4019'):
    """Draw a football centered at (cx, cy), oriented along angle_rad.

    angle_rad is a canvas-space angle (0 = pointing along +x; since canvas y
    grows downward, positive angles rotate the nose toward the bottom of the
    screen) — pass atan2(-vy, vx) for a ball flying with world-space velocity
    (vx, vy) where vy is up-positive.
    """
    n = 20
    pts = []
    for i in range(n):
        t = i / n * 2 * math.pi
        lx = (length / 2) * math.cos(t)
        taper = 1 - 0.55 * (abs(math.cos(t)) ** 3)
        ly = (width / 2) * math.sin(t) * taper
        pts.append((lx, ly))
    cos_a, sin_a = math.cos(angle_rad), math.sin(angle_rad)
    screen_pts = []
    for lx, ly in pts:
        rx = lx * cos_a - ly * sin_a
        ry = lx * sin_a + ly * cos_a
        screen_pts.append((cx + rx, cy + ry))
    canvas.create_polygon(*[c for p in screen_pts for c in p], fill=color, outline='#3d2008', width=2, smooth=True)

    p1x, p1y = cx - (length * 0.32) * cos_a, cy - (length * 0.32) * sin_a
    p2x, p2y = cx + (length * 0.32) * cos_a, cy + (length * 0.32) * sin_a
    canvas.create_line(p1x, p1y, p2x, p2y, fill='white', width=1)

    perp_x, perp_y = -sin_a, cos_a
    lace_half = max(2.0, width * 0.18)
    for f in (-0.12, 0.0, 0.12):
        px, py = cx + f * length * cos_a, cy + f * length * sin_a
        canvas.create_line(px - perp_x * lace_half, py - perp_y * lace_half, px + perp_x * lace_half, py + perp_y * lace_half, fill='white', width=2)


def draw_car(canvas, x_left, x_right, road_y, height, body_color, cabin_color, label_text):
    """Draw a simple car silhouette (body, cabin, wheels) sitting on a road at road_y."""
    w = max(1.0, x_right - x_left)
    wheel_r = max(6.0, height * 0.18)
    body_bottom = road_y - wheel_r * 0.9
    body_top = body_bottom - height * 0.55
    cabin_top = body_top - height * 0.35
    cabin_left = x_left + w * 0.24
    cabin_right = x_left + w * 0.76

    canvas.create_oval(x_left + w * 0.06, road_y - wheel_r * 0.3, x_right - w * 0.06, road_y + wheel_r * 0.9, fill='#3a3a3a', outline='')

    canvas.create_polygon(
        x_left, body_bottom,
        x_left, body_top + height * 0.12,
        x_left + w * 0.08, body_top,
        x_right - w * 0.08, body_top,
        x_right, body_top + height * 0.12,
        x_right, body_bottom,
        smooth=True, fill=body_color, outline='#1c1c1c', width=2)

    canvas.create_polygon(
        cabin_left, body_top,
        cabin_left + w * 0.06, cabin_top,
        cabin_right - w * 0.06, cabin_top,
        cabin_right, body_top,
        smooth=True, fill=cabin_color, outline='#1c1c1c', width=1)

    for wx in (x_left + w * 0.22, x_right - w * 0.22):
        canvas.create_oval(wx - wheel_r, road_y - wheel_r * 1.6, wx + wheel_r, road_y + wheel_r * 0.4, fill='#1c1c1c', outline='#000000')
        canvas.create_oval(wx - wheel_r * 0.4, road_y - wheel_r * 1.2, wx + wheel_r * 0.4, road_y - wheel_r * 0.4, fill='#cfcfcf', outline='')

    canvas.create_text((x_left + x_right) / 2, body_top + height * 0.28, text=label_text, fill='white', font=('Arial', 9, 'bold'))


def draw_hanging_block(canvas, x0, y0, x1, y1, mass_val):
    """Draw a bevelled block for objects suspended in mid-air (no ground shadow)."""
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    canvas.create_rectangle(x0, y0, x1, y1, fill='#3a56b0', outline='#1c2b57', width=2)
    canvas.create_line(x0, y0 + 3, x1, y0 + 3, fill='#7c94e0', width=3)
    canvas.create_text(cx, cy, text=f"m={mass_val:.2f} kg", fill='white', font=('Arial', 9, 'bold'))


def draw_legend(canvas, items, canvas_w, top=16):
    """Draw a small legend box in the canvas's top-right corner.

    `items` is a list of (label, color) tuples.
    """
    lx, ly = canvas_w - 190, top
    canvas.create_rectangle(lx - 10, ly - 10, canvas_w - 10, ly + 20 * len(items), fill='#ffffff', outline='#cccccc')
    for i, (label, color) in enumerate(items):
        y = ly + i * 20
        canvas.create_line(lx, y, lx + 22, y, fill=color, width=3)
        canvas.create_text(lx + 30, y, text=label, anchor='w', font=('Arial', 8))


def draw_readout(canvas, text, top=10):
    """Draw a small readable text readout in the canvas's top-left corner."""
    canvas.create_rectangle(10, top, 18 + 7 * len(text), top + 24, fill='#ffffff', outline='#cccccc')
    canvas.create_text(18, top + 12, anchor='w', text=text, font=('Courier', 10))


def draw_arrow(canvas, x0, y0, x1, y1, color, width, text=None):
    """Draw a force-vector-style arrow, optionally labelled at its tip."""
    canvas.create_line(x0, y0, x1, y1, arrow='last', arrowshape=(10, 12, 4), fill=color, width=width, capstyle='round')
    if text:
        canvas.create_text(x1 + 8, y1, text=text, fill=color, font=('Arial', 9, 'bold'), anchor='w')


def draw_tilted_block(canvas, corners, box_cx, box_cy, mass_val):
    """Draw a bevelled block whose corners are already rotated to an incline."""
    contact_x = (corners[0][0] + corners[1][0]) / 2
    contact_y = (corners[0][1] + corners[1][1]) / 2
    canvas.create_oval(contact_x - 34, contact_y - 9, contact_x + 34, contact_y + 9, fill='#7a4a22', outline='')
    canvas.create_polygon(*[c for corner in corners for c in corner], fill='#3a56b0', outline='#1c2b57', width=2)
    ul, ur = corners[3], corners[2]
    canvas.create_line(ul[0], ul[1], ur[0], ur[1], fill='#7c94e0', width=3)
    canvas.create_text(box_cx, box_cy, text=f"m={mass_val:.2f} kg", fill='white', font=('Arial', 9, 'bold'))


def draw_flat_block(canvas, x0, y0, x1, y1, mass_val):
    """Draw a bevelled, axis-aligned block for horizontal-motion demos."""
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    canvas.create_oval(x0 + 5, y1 - 6, x1 - 5, y1 + 10, fill='#7a4a22', outline='')
    canvas.create_rectangle(x0, y0, x1, y1, fill='#3a56b0', outline='#1c2b57', width=2)
    canvas.create_line(x0, y0 + 3, x1, y0 + 3, fill='#7c94e0', width=3)
    canvas.create_text(cx, cy, text=f"m={mass_val:.2f} kg", fill='white', font=('Arial', 9, 'bold'))


# --- Small topic icons, used by the main menu tiles ---

def draw_wood_crate(canvas, cx, cy, size, label='m'):
    """Draw a wooden crate with a mass label on it (Newton's Laws icon)."""
    half = size / 2
    x0, y0, x1, y1 = cx - half, cy - half, cx + half, cy + half
    canvas.create_rectangle(x0, y0, x1, y1, fill='#c98a4b', outline='#6b4423', width=3)
    for frac in (0.33, 0.66):
        canvas.create_line(x0, y0 + size * frac, x1, y0 + size * frac, fill='#a9713f', width=1)
    corner = size * 0.28
    for x, y, dx, dy in ((x0, y0, 1, 1), (x1, y0, -1, 1), (x0, y1, 1, -1), (x1, y1, -1, -1)):
        canvas.create_line(x, y, x + dx * corner, y + dy * corner, fill='#6b4423', width=2)
    canvas.create_text(cx, cy, text=label, font=('Arial', max(10, int(size * 0.34)), 'bold'), fill='#3d2a12')


def draw_spring_icon(canvas, cx, top_y, bottom_y, mass_size):
    """Draw a small hanging spring-mass system (Work, Energy & Power icon)."""
    canvas.create_rectangle(cx - mass_size * 0.7, top_y - 6, cx + mass_size * 0.7, top_y, fill='#6b4423', outline='#4a2d15', width=1)
    coil_top = top_y
    coil_bottom = bottom_y - mass_size / 2
    coils = 5
    amp = mass_size * 0.28
    pts = []
    for i in range(coils + 1):
        t = i / coils
        y = coil_top + t * (coil_bottom - coil_top)
        x = cx + (amp if i % 2 == 0 else -amp)
        pts.append((x, y))
    canvas.create_line(cx, coil_top, pts[0][0], pts[0][1], fill='#5a5a5a', width=2)
    for i in range(len(pts) - 1):
        canvas.create_line(pts[i][0], pts[i][1], pts[i + 1][0], pts[i + 1][1], fill='#5a5a5a', width=2)
    canvas.create_line(pts[-1][0], pts[-1][1], cx, coil_bottom, fill='#5a5a5a', width=2)
    bx0, by0, bx1, by1 = cx - mass_size / 2, bottom_y - mass_size, cx + mass_size / 2, bottom_y
    canvas.create_rectangle(bx0, by0, bx1, by1, fill='#3a56b0', outline='#1c2b57', width=2)
    canvas.create_line(bx0, by0 + 3, bx1, by0 + 3, fill='#7c94e0', width=3)
    canvas.create_text((bx0 + bx1) / 2, (by0 + by1) / 2, text='m', font=('Arial', max(10, int(mass_size * 0.4)), 'bold'), fill='white')


def draw_rotation_icon(canvas, cx, cy, r, color='#5a5f68'):
    """Draw a spinning wheel with a curved motion arrow (Rotational Motion icon)."""
    canvas.create_oval(cx - r, cy - r, cx + r, cy + r, fill='#c7ccd4', outline=color, width=3)
    canvas.create_oval(cx - r * 0.14, cy - r * 0.14, cx + r * 0.14, cy + r * 0.14, fill=color, outline='')
    for ang in (0, 60, 120):
        rad = math.radians(ang)
        dx, dy = math.cos(rad), math.sin(rad)
        canvas.create_line(cx + dx * r * 0.14, cy + dy * r * 0.14, cx + dx * r * 0.92, cy + dy * r * 0.92, fill=color, width=3)
        canvas.create_line(cx - dx * r * 0.14, cy - dy * r * 0.14, cx - dx * r * 0.92, cy - dy * r * 0.92, fill=color, width=3)
    canvas.create_arc(cx - r * 1.4, cy - r * 1.4, cx + r * 1.4, cy + r * 1.4, start=20, extent=130, style='arc', outline='#1d4fd8', width=3)
    tip_rad = math.radians(20)
    tip_x, tip_y = cx + r * 1.4 * math.cos(tip_rad), cy - r * 1.4 * math.sin(tip_rad)
    canvas.create_line(tip_x - 8, tip_y - 3, tip_x, tip_y, tip_x - 3, tip_y + 8, fill='#1d4fd8', width=3, capstyle='round', joinstyle='round')


def draw_water_drop(canvas, cx, cy, size, color='#2ea3f2'):
    """Draw a water droplet (Fluids & Statics icon)."""
    norm_pts = [
        (0.0, -1.0), (0.55, -0.35), (0.85, 0.25), (0.55, 0.85),
        (0.0, 1.0), (-0.55, 0.85), (-0.85, 0.25), (-0.55, -0.35),
    ]
    r = size / 2
    pts = [(cx + nx * r, cy + ny * r) for nx, ny in norm_pts]
    canvas.create_polygon(*[c for p in pts for c in p], fill=color, outline='#1b6ca8', width=2, smooth=True)
    canvas.create_oval(cx - r * 0.35, cy - r * 0.05, cx + r * 0.05, cy + r * 0.45, fill='#bfe6ff', outline='')


def _rotated_ellipse_points(cx, cy, rx, ry, angle_rad, n=24):
    pts = []
    for i in range(n):
        t = i / n * 2 * math.pi
        lx, ly = rx * math.cos(t), ry * math.sin(t)
        rx_p = lx * math.cos(angle_rad) - ly * math.sin(angle_rad)
        ry_p = lx * math.sin(angle_rad) + ly * math.cos(angle_rad)
        pts.append((cx + rx_p, cy + ry_p))
    return pts


def draw_atom_icon(canvas, cx, cy, r, color='#7c4fd6'):
    """Draw a simple atom with three orbital rings (Quantum Mechanics icon)."""
    for angle_deg in (0, 60, 120):
        pts = _rotated_ellipse_points(cx, cy, r * 0.95, r * 0.4, math.radians(angle_deg))
        canvas.create_polygon(*[c for p in pts for c in p], fill='', outline=color, width=2, smooth=True)
    for angle_deg, t in ((30, 0.2), (150, 0.55), (270, 0.8)):
        pts = _rotated_ellipse_points(cx, cy, r * 0.95, r * 0.4, math.radians(angle_deg))
        ex, ey = pts[int(t * len(pts))]
        canvas.create_oval(ex - 4, ey - 4, ex + 4, ey + 4, fill='#d9740c', outline='')
    canvas.create_oval(cx - r * 0.16, cy - r * 0.16, cx + r * 0.16, cy + r * 0.16, fill=color, outline='')


def draw_pencil(canvas, cx, cy, length, width, angle_rad=math.radians(-40)):
    """Draw a simple wooden pencil (eraser, ferrule, wood body, sharpened graphite tip)
    centered at (cx, cy), pointing at angle_rad. Used as the app's logo."""
    cos_a, sin_a = math.cos(angle_rad), math.sin(angle_rad)

    def rot(lx, ly):
        return (cx + lx * cos_a - ly * sin_a, cy + lx * sin_a + ly * cos_a)

    def quad(x0, x1, half_w, **kwargs):
        pts = [rot(x0, -half_w), rot(x1, -half_w), rot(x1, half_w), rot(x0, half_w)]
        canvas.create_polygon(*[c for p in pts for c in p], **kwargs)

    half_w = width / 2
    tip_len = length * 0.16
    ferrule_len = length * 0.08
    eraser_len = length * 0.10
    x0 = -length / 2
    x1 = x0 + eraser_len
    x2 = x1 + ferrule_len
    x3 = length / 2 - tip_len
    x4 = x3 + tip_len * 0.5
    x5 = length / 2

    quad(x0, x1, half_w, fill='#e0708a', outline='#8a3d52', width=1)
    quad(x1, x2, half_w, fill='#c7ccd4', outline='#5a5f68', width=1)
    quad(x2, x3, half_w, fill='#e8b84b', outline='#8a6b1f', width=1)
    canvas.create_line(*rot(x2, 0), *rot(x3, 0), fill='#c99a2e', width=1)
    canvas.create_polygon(*[c for p in (rot(x3, -half_w), rot(x4, 0), rot(x3, half_w)) for c in p],
                           fill='#f0d9a6', outline='#8a6b1f', width=1)
    canvas.create_polygon(*[c for p in (rot(x4, -half_w * 0.35), rot(x5, 0), rot(x4, half_w * 0.35)) for c in p],
                           fill='#2b2015', outline='')
