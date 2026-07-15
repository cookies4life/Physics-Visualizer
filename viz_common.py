"""Shared drawing and UI helpers used across the physics visualizer's demos.

Keeping this in one place is what lets the different demo windows (Newton's
incline/flat force demos, the spring-mass energy demo, projectile
kinematics, ...) share one consistent look and one consistent way of
presenting the equations being demonstrated.
"""

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


def draw_backdrop(canvas, canvas_w, canvas_h, ground_y):
    """Draw a soft sky gradient above ground_y and a grassy strip below it."""
    sky_top = (0xea, 0xf6, 0xff)
    sky_bottom = (0xff, 0xff, 0xff)
    bands = 8
    band_h = max(1, ground_y // bands)
    for i in range(bands):
        t = i / (bands - 1)
        r = round(sky_top[0] + (sky_bottom[0] - sky_top[0]) * t)
        g = round(sky_top[1] + (sky_bottom[1] - sky_top[1]) * t)
        b = round(sky_top[2] + (sky_bottom[2] - sky_top[2]) * t)
        canvas.create_rectangle(0, i * band_h, canvas_w, (i + 1) * band_h + 1, fill=f'#{r:02x}{g:02x}{b:02x}', outline='')
    canvas.create_rectangle(0, ground_y, canvas_w, canvas_h, fill='#8fbf6b', outline='')
    canvas.create_line(0, ground_y, canvas_w, ground_y, fill='#5f8f45', width=2)
    for gx in range(0, canvas_w, 18):
        canvas.create_line(gx, ground_y, gx + 6, ground_y + 10, fill='#5f8f45', width=1)


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
