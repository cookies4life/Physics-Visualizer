"""Main menu for launching the different physics visualizations."""

import tkinter as tk
from tkinter import ttk
import kinematics_vis
import newton_vis
import energy_vis
import momentum_vis
import rotation_vis
import fluids_vis
import quantum_vis



class MainMenu:
	"""Create the main window and connect each button to a topic-specific demo."""

	def __init__(self):
		"""Initialize the application window and build the menu UI."""
		self.root = tk.Tk()
		self.root.title("Physics Visualizer")
		self.root.geometry("800x600")
		self._build()

	def _build(self):
		"""Create the buttons and labels that let the user choose a physics topic."""
		frm = ttk.Frame(self.root, padding=20)
		frm.pack(fill=tk.BOTH, expand=True)

		title = ttk.Label(frm, text="Physics Visualizer", font=(None, 24))
		title.pack(pady=(0, 20))

		# Kinematics button
		btn_kin = ttk.Button(frm, text="Kinematics", command=self.open_kinematics)
		btn_kin.pack(fill=tk.BOTH, expand=True, pady=5)

		# Topic buttons
		ttk.Button(frm, text="Newton's Laws", command=self.open_newton).pack(fill=tk.BOTH, expand=True, pady=5)
		ttk.Button(frm, text="Work, Energy & Power", command=self.open_energy).pack(fill=tk.BOTH, expand=True, pady=5)
		ttk.Button(frm, text="Momentum & Collisions", command=self.open_momentum).pack(fill=tk.BOTH, expand=True, pady=5)
		ttk.Button(frm, text="Rotational Motion", command=self.open_rotation).pack(fill=tk.BOTH, expand=True, pady=5)
		ttk.Button(frm, text="Fluids & Statics", command=self.open_fluids).pack(fill=tk.BOTH, expand=True, pady=5)
		ttk.Button(frm, text="Quantum Mechanics", command=self.open_quantum).pack(fill=tk.BOTH, expand=True, pady=5)


		# Quit
		ttk.Button(frm, text="Quit", command=self.root.destroy).pack(side=tk.BOTTOM, pady=10)

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
