"""Main menu for launching the different physics visualizations."""

import math
import tkinter as tk
from tkinter import ttk

import viz_common
import kinematics_vis
import newton_vis
import energy_vis
import momentum_vis
import rotation_vis
import fluids_vis
import quantum_vis
import whiteboard_tutor
import waves_vis


TILE_SIZE = 112
BG = '#f5f7fa'


class MainMenu:
	"""Create the main window and connect each icon tile to a topic-specific demo."""

	def __init__(self):
		"""Initialize the application window and build the menu UI."""
		self.root = tk.Tk()
		self.root.title("Physics Visualizer")
		self.root.geometry("900x640")
		self.root.configure(bg=BG)
		self._build()

	def _build(self):
		"""Create the icon tiles that let the user choose a physics topic."""
		outer = tk.Frame(self.root, bg=BG, padx=28, pady=24)
		outer.pack(fill=tk.BOTH, expand=True)

		title_row = tk.Frame(outer, bg=BG)
		title_row.pack(pady=(0, 2))
		logo_canvas = tk.Canvas(title_row, width=60, height=48, bg=BG, highlightthickness=0)
		logo_canvas.pack(side=tk.LEFT, padx=(0, 10))
		viz_common.draw_pencil(logo_canvas, 30, 24, 54, 10)
		tk.Label(title_row, text="Physics Visualizer", font=(None, 26, 'bold'), bg=BG, fg='black').pack(side=tk.LEFT)
		tk.Label(outer, text="Pick a topic to explore", font=(None, 12), bg=BG, fg='#5a5f68').pack(pady=(0, 16))

		hero = self._make_hero_tile(
			outer, "Whiteboard Tutor", "Draw a free-body diagram or write out your question — an AI physics tutor checks your work and chats with you live.",
			self._icon_whiteboard_tutor, self.open_whiteboard_tutor, '#fff6e0')
		hero.pack(fill=tk.X, pady=(0, 20))

		grid = tk.Frame(outer, bg=BG)
		grid.pack(expand=True)

		topics = [
			("Kinematics", self._icon_football, self.open_kinematics, '#eaf6ff'),
			("Newton's Laws", self._icon_newton, self.open_newton, '#fdf1e0'),
			("Work, Energy\n& Power", self._icon_energy, self.open_energy, '#f3e9ff'),
			("Momentum &\nCollisions", self._icon_momentum, self.open_momentum, '#eef2f7'),
			("Rotational\nMotion", self._icon_rotation, self.open_rotation, '#fff4e0'),
			("Fluids &\nStatics", self._icon_fluids, self.open_fluids, '#e6f6fb'),
			("Waves &\nDiffraction", self._icon_waves, self.open_waves, '#e0f2fe'),
			("Quantum\nMechanics", self._icon_quantum, self.open_quantum, '#f0e9ff'),
		]

		cols = 4
		for i, (name, icon_fn, command, bg) in enumerate(topics):
			row, col = divmod(i, cols)
			tile = self._make_tile(grid, name, icon_fn, command, bg)
			tile.grid(row=row, column=col, padx=14, pady=14, sticky='n')
		for c in range(cols):
			grid.columnconfigure(c, weight=1)

		ttk.Button(outer, text="Quit", command=self.root.destroy).pack(side=tk.BOTTOM, pady=(20, 0))

	def _make_tile(self, parent, title, icon_fn, command, bg):
		"""Build one clickable icon tile: a square icon canvas with its name below."""
		tile = tk.Frame(parent, bg=bg, highlightbackground='#d8d8d8', highlightcolor='#4c6ef5', highlightthickness=2, bd=0)

		icon_canvas = tk.Canvas(tile, width=TILE_SIZE, height=TILE_SIZE, bg=bg, highlightthickness=0)
		icon_canvas.pack(padx=10, pady=(12, 6))
		icon_fn(icon_canvas)

		label = tk.Label(tile, text=title, bg=bg, font=(None, 11, 'bold'), fg='#22252a', justify='center')
		label.pack(pady=(0, 14), padx=10)

		def on_click(_event=None):
			command()

		def on_enter(_event=None):
			tile.config(highlightbackground='#4c6ef5')

		def on_leave(_event=None):
			tile.config(highlightbackground='#d8d8d8')

		for widget in (tile, icon_canvas, label):
			widget.bind('<Button-1>', on_click)
			widget.bind('<Enter>', on_enter)
			widget.bind('<Leave>', on_leave)
			widget.config(cursor='hand2')

		return tile

	def _make_hero_tile(self, parent, title, subtitle, icon_fn, command, bg):
		"""Build the big, prominent Whiteboard Tutor tile — same click/hover behavior as a
		regular tile, but wider and rectangular so it stands out above the topic grid."""
		tile = tk.Frame(parent, bg=bg, highlightbackground='#e0b84a', highlightcolor='#4c6ef5', highlightthickness=3, bd=0)
		inner = tk.Frame(tile, bg=bg)
		inner.pack(fill=tk.X, padx=18, pady=14)

		icon_w, icon_h = 200, 130
		icon_canvas = tk.Canvas(inner, width=icon_w, height=icon_h, bg=bg, highlightthickness=0)
		icon_canvas.pack(side=tk.LEFT, padx=(0, 20))
		icon_fn(icon_canvas, icon_w, icon_h)

		text_frame = tk.Frame(inner, bg=bg)
		text_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
		tk.Label(text_frame, text=title, bg=bg, font=(None, 20, 'bold'), fg='#22252a', anchor='w').pack(fill=tk.X, pady=(10, 4))
		tk.Label(text_frame, text=subtitle, bg=bg, font=(None, 12), fg='#5a5f68', anchor='w', justify='left', wraplength=520).pack(fill=tk.X)
		tk.Label(text_frame, text="Click to open ->", bg=bg, font=(None, 11, 'italic'), fg='#8a5a2b', anchor='w').pack(fill=tk.X, pady=(8, 0))

		def on_click(_event=None):
			command()

		def on_enter(_event=None):
			tile.config(highlightbackground='#4c6ef5')

		def on_leave(_event=None):
			tile.config(highlightbackground='#e0b84a')

		clickable = [tile, inner, icon_canvas, text_frame] + list(text_frame.winfo_children())
		for widget in clickable:
			widget.bind('<Button-1>', on_click)
			widget.bind('<Enter>', on_enter)
			widget.bind('<Leave>', on_leave)
			widget.config(cursor='hand2')

		return tile

	def _icon_whiteboard_tutor(self, canvas, w, h):
		"""Draw an easel-mounted whiteboard with a physics equation and markers in a tray."""
		board_w, board_h = w * 0.82, h * 0.62
		bx0, by0 = (w - board_w) / 2, h * 0.06
		bx1, by1 = bx0 + board_w, by0 + board_h
		canvas.create_rectangle(bx0 - 6, by0 - 6, bx1 + 6, by1 + 6, fill='#c7ccd4', outline='#5a5f68', width=2)
		canvas.create_rectangle(bx0, by0, bx1, by1, fill='white', outline='#8a8f98', width=1)
		canvas.create_text((bx0 + bx1) / 2, (by0 + by1) / 2, text='F = ma', font=('Arial', int(h * 0.16), 'bold'), fill='#1d4fd8')

		canvas.create_line(bx0 + board_w * 0.15, by1 + 6, bx0 - board_w * 0.05, h * 0.97, fill='#5a5f68', width=3)
		canvas.create_line(bx1 - board_w * 0.15, by1 + 6, bx1 + board_w * 0.05, h * 0.97, fill='#5a5f68', width=3)
		canvas.create_line(bx0 + board_w * 0.5, by1 + 6, bx0 + board_w * 0.5, h * 0.85, fill='#5a5f68', width=3)

		tray_y = by1 + 2
		for i, mc in enumerate(('#c1440e', '#1f8a3b', '#7c4fd6')):
			mx = bx0 + board_w * 0.26 + i * board_w * 0.18
			canvas.create_rectangle(mx, tray_y - 4, mx + board_w * 0.11, tray_y + 4, fill=mc, outline='#333333')

	# --- Icon drawers, one per topic ---

	def _icon_football(self, canvas):
		mid = TILE_SIZE / 2
		viz_common.draw_football(canvas, mid, mid, TILE_SIZE * 0.62, TILE_SIZE * 0.34, math.radians(-25))

	def _icon_newton(self, canvas):
		mid = TILE_SIZE / 2
		viz_common.draw_wood_crate(canvas, mid, mid, TILE_SIZE * 0.72, label='m')

	def _icon_energy(self, canvas):
		mid = TILE_SIZE / 2
		viz_common.draw_spring_icon(canvas, mid, TILE_SIZE * 0.14, TILE_SIZE * 0.92, TILE_SIZE * 0.34)

	def _icon_momentum(self, canvas):
		road_y = TILE_SIZE * 0.86
		canvas.create_rectangle(0, road_y, TILE_SIZE, TILE_SIZE, fill='#4a4a4d', outline='')
		canvas.create_line(0, road_y, TILE_SIZE, road_y, fill='#2e2e30', width=2)
		viz_common.draw_car(canvas, TILE_SIZE * 0.14, TILE_SIZE * 0.86, road_y, TILE_SIZE * 0.5, '#3a56b0', '#7c94e0', '')

	def _icon_rotation(self, canvas):
		mid = TILE_SIZE / 2
		viz_common.draw_rotation_icon(canvas, mid, mid, TILE_SIZE * 0.32)

	def _icon_fluids(self, canvas):
		mid = TILE_SIZE / 2
		viz_common.draw_water_drop(canvas, mid, mid, TILE_SIZE * 0.66)

	def _icon_quantum(self, canvas):
		mid = TILE_SIZE / 2
		viz_common.draw_atom_icon(canvas, mid, mid, TILE_SIZE * 0.36)

	def _icon_waves(self, canvas):
		w = h = TILE_SIZE
		viz_common.draw_sky(canvas, w, h, int(h * 0.42))
		barrier_y = h * 0.42
		canvas.create_rectangle(0, h * 0.42, w, h, fill='#2ea3f2', outline='')
		for row, amp, color in ((0.58, 4, '#bfe6ff'), (0.74, 5, '#e3f6ff'), (0.9, 4, '#bfe6ff')):
			pts = []
			for i in range(0, int(w) + 1, 4):
				pts.append((i, h * row + amp * math.sin(i * 0.5)))
			canvas.create_line(*[c for p in pts for c in p], fill=color, width=2, smooth=True)
		gap_l, gap_r = w * 0.44, w * 0.56
		canvas.create_rectangle(0, barrier_y - 4, gap_l, barrier_y + 4, fill='#5a5f68', outline='#333333')
		canvas.create_rectangle(gap_r, barrier_y - 4, w, barrier_y + 4, fill='#5a5f68', outline='#333333')

	def open_kinematics(self):
		"""Open the kinematics projectile demo."""
		kinematics_vis.open_kinematics_window(self.root)

	def open_newton(self):
		"""Open the Newton's laws force demo."""
		newton_vis.open_newton_window(self.root)

	def open_energy(self):
		"""Open the work, energy, and power demo."""
		energy_vis.open_energy_window(self.root)

	def open_momentum(self):
		"""Open the momentum and collision demo."""
		momentum_vis.open_momentum_window(self.root)

	def open_rotation(self):
		"""Open the rotational motion demo."""
		rotation_vis.open_rotation_window(self.root)

	def open_fluids(self):
		"""Open the fluids and buoyancy demo."""
		fluids_vis.open_fluids_window(self.root)

	def open_quantum(self):
		"""Open the quantum mechanics demo."""
		quantum_vis.open_quantum_window(self.root)

	def open_waves(self):
		"""Open the water wave / diffraction ripple-tank demo."""
		waves_vis.open_waves_window(self.root)

	def open_whiteboard_tutor(self):
		"""Open the AI whiteboard tutor (drawing board + live chat)."""
		whiteboard_tutor.open_whiteboard_tutor(self.root)

	def run(self):
		"""Start the Tkinter main event loop."""
		self.root.mainloop()
