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

		ttk.Label(outer, text="Physics Visualizer", font=(None, 26, 'bold'), background=BG).pack(pady=(0, 2))
		ttk.Label(outer, text="Pick a topic to explore", font=(None, 12), background=BG, foreground='#5a5f68').pack(pady=(0, 22))

		grid = tk.Frame(outer, bg=BG)
		grid.pack(expand=True)

		topics = [
			("Kinematics", self._icon_football, self.open_kinematics, '#eaf6ff'),
			("Newton's Laws", self._icon_newton, self.open_newton, '#fdf1e0'),
			("Work, Energy\n& Power", self._icon_energy, self.open_energy, '#f3e9ff'),
			("Momentum &\nCollisions", self._icon_momentum, self.open_momentum, '#eef2f7'),
			("Rotational\nMotion", self._icon_rotation, self.open_rotation, '#fff4e0'),
			("Fluids &\nStatics", self._icon_fluids, self.open_fluids, '#e6f6fb'),
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

	def run(self):
		"""Start the Tkinter main event loop."""
		self.root.mainloop()
