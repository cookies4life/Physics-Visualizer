"""
Physics Visualizer
------------------
Entry point. Shows the main menu and routes the user's choice
to the right category module.
"""

import tkinter as tk
from tkinter import messagebox, ttk

import classical_mechanics
import quantum_mechanics
import relativistic_mechanics
import statistical_mechanics


def launch_action(action):
    try:
        action()
    except Exception as exc:
        messagebox.showerror("Error", f"Failed to launch simulation:\n{exc}")


def clear_frame(frame):
    for widget in frame.winfo_children():
        widget.destroy()


def show_category(frame, title, actions):
    clear_frame(frame)

    title_label = ttk.Label(frame, text=title, style="Title.TLabel")
    title_label.pack(pady=(12, 6))

    instructions = ttk.Label(
        frame,
        text="Click a simulation to open a plot window. Close the plot to return.",
        style="Info.TLabel",
        wraplength=360,
        justify="center",
    )
    instructions.pack(padx=10, pady=(0, 16))

    for action_name, action in actions:
        button = ttk.Button(
            frame,
            text=action_name,
            command=lambda action=action: launch_action(action),
            width=30,
        )
        button.pack(pady=4)

    ttk.Separator(frame, orient="horizontal").pack(fill="x", pady=12)
    back_button = ttk.Button(frame, text="Back to main menu", command=lambda: show_main_menu(frame))
    back_button.pack(pady=(0, 8))


def show_main_menu(frame):
    clear_frame(frame)

    title_label = ttk.Label(frame, text="Physics Visualizer", style="Title.TLabel")
    title_label.pack(pady=(16, 8))

    description = ttk.Label(
        frame,
        text="Choose a physics category below to open an interactive visualization.",
        style="Info.TLabel",
        wraplength=360,
        justify="center",
    )
    description.pack(padx=10, pady=(0, 18))

    categories = [
        ("Classical Mechanics", lambda: show_category(
            frame,
            "Classical Mechanics",
            [
                ("Projectile Motion", classical_mechanics.projectile_motion),
                ("Pendulum", classical_mechanics.pendulum),
                ("Collision", classical_mechanics.collision),
            ],
        )),
        ("Quantum Mechanics", lambda: show_category(
            frame,
            "Quantum Mechanics",
            [
                ("Wave Function", quantum_mechanics.wave_function),
                ("Double Slit", quantum_mechanics.double_slit),
                ("Particle Probability", quantum_mechanics.particle_probability),
            ],
        )),
        ("Relativistic Mechanics", lambda: show_category(
            frame,
            "Relativistic Mechanics",
            [
                ("Time Dilation", relativistic_mechanics.time_dilation),
                ("Length Contraction", relativistic_mechanics.length_contraction),
                ("Spacetime Diagram", relativistic_mechanics.spacetime_diagram),
            ],
        )),
        ("Statistical Relationships", lambda: show_category(
            frame,
            "Statistical Relationships",
            [
                ("Gas Simulation", statistical_mechanics.gas_simulation),
                ("Maxwell-Boltzmann", statistical_mechanics.distribution),
                ("Entropy Mixing", statistical_mechanics.entropy),
            ],
        )),
    ]

    for name, callback in categories:
        button = ttk.Button(frame, text=name, command=callback, width=30)
        button.pack(pady=6)

    ttk.Separator(frame, orient="horizontal").pack(fill="x", pady=16)
    ttk.Button(frame, text="Quit", command=frame.master.destroy, width=30).pack(pady=(0, 8))


def main():
    root = tk.Tk()
    root.title("Physics Visualizer")
    root.geometry("420x420")
    root.resizable(False, False)

    style = ttk.Style(root)
    style.configure("TButton", font=("Segoe UI", 11), padding=8)
    style.configure("Title.TLabel", font=("Segoe UI", 18, "bold"))
    style.configure("Info.TLabel", font=("Segoe UI", 10))

    content_frame = ttk.Frame(root, padding=16)
    content_frame.pack(fill="both", expand=True)

    show_main_menu(content_frame)
    root.mainloop()


if __name__ == "__main__":
    main()