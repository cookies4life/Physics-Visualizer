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
	def __init__(self):
		self.root = tk.Tk()
		self.root.title("Physics Visualizer")
		self.root.geometry("800x600")
		self._build()

	def _build(self):
		frm = ttk.Frame(self.root, padding=20)
		frm.pack(fill=tk.BOTH, expand=True)

		title = ttk.Label(frm, text="Physics Visualizer", font=(None, 24))
		title.pack(pady=(0, 20))

		# Kinematics button
		btn_kin = ttk.Button(frm, text="Kinematics", command=self.open_kinematics)
		btn_kin.pack(fill=tk.X, pady=5)

		# Topic buttons
		ttk.Button(frm, text="Newton's Laws", command=self.open_newton).pack(fill=tk.X, pady=5)
		ttk.Button(frm, text="Work, Energy & Power", command=self.open_energy).pack(fill=tk.X, pady=5)
		ttk.Button(frm, text="Momentum & Collisions", command=self.open_momentum).pack(fill=tk.X, pady=5)
		ttk.Button(frm, text="Rotational Motion", command=self.open_rotation).pack(fill=tk.X, pady=5)
		ttk.Button(frm, text="Fluids & Statics", command=self.open_fluids).pack(fill=tk.X, pady=5)
		ttk.Button(frm, text="Quantum Mechanics", command=self.open_quantum).pack(fill=tk.X, pady=5)

		# Quit
		ttk.Button(frm, text="Quit", command=self.root.destroy).pack(side=tk.BOTTOM, pady=10)

	def open_kinematics(self):
		kinematics_vis.open_kinematics_window(self.root)

	def open_newton(self):
		newton_vis.open_newton_window(self.root)

	def open_energy(self):
		energy_vis.open_energy_window(self.root)

	def open_momentum(self):
		momentum_vis.open_momentum_window(self.root)

	def open_rotation(self):
		rotation_vis.open_rotation_window(self.root)

	def open_fluids(self):
		fluids_vis.open_fluids_window(self.root)

	def open_quantum(self):
		quantum_vis.open_quantum_window(self.root)

	def run(self):
		self.root.mainloop()
