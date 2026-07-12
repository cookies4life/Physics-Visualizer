"""
Statistical Relationships module.
Contains: gas simulation, distributions, entropy.
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation


def start():
    while True:
        print("\n--- Statistical Relationships ---")
        print("1. Gas Simulation")
        print("2. Maxwell-Boltzmann Distribution")
        print("3. Entropy (Two-Gas Mixing)")
        print("0. Back to main menu")

        choice = input("Choose an option: ").strip()

        if choice == "1":
            gas_simulation()
        elif choice == "2":
            distribution()
        elif choice == "3":
            entropy()
        elif choice == "0":
            break
        else:
            print("Invalid choice, try again.")


def gas_simulation(n_particles=40, box_size=10, speed=0.15):
    """Animates particles bouncing around a 2D box (ideal gas model)."""
    rng = np.random.default_rng(42)
    pos = rng.uniform(0.5, box_size - 0.5, size=(n_particles, 2))
    angles = rng.uniform(0, 2 * np.pi, size=n_particles)
    vel = speed * np.column_stack([np.cos(angles), np.sin(angles)])

    fig, ax = plt.subplots()
    ax.set_xlim(0, box_size)
    ax.set_ylim(0, box_size)
    ax.set_aspect("equal")
    ax.set_title("Ideal Gas Simulation")

    scatter = ax.scatter(pos[:, 0], pos[:, 1], s=40, c="royalblue")

    def update(frame):
        nonlocal pos, vel
        pos = pos + vel
        # bounce off walls
        for dim in (0, 1):
            hit_low = pos[:, dim] < 0
            hit_high = pos[:, dim] > box_size
            vel[hit_low | hit_high, dim] *= -1
            pos[:, dim] = np.clip(pos[:, dim], 0, box_size)
        scatter.set_offsets(pos)
        return scatter,

    ani = FuncAnimation(fig, update, frames=400, interval=20, blit=True, repeat=True)
    plt.show()


def distribution(temperature=300, mass=4.65e-26):
    """Plots the Maxwell-Boltzmann speed distribution at a given temperature (K)."""
    k_b = 1.380649e-23  # Boltzmann constant

    v = np.linspace(0, 2000, 500)
    f = (
        4 * np.pi * v**2
        * (mass / (2 * np.pi * k_b * temperature)) ** 1.5
        * np.exp(-mass * v**2 / (2 * k_b * temperature))
    )

    fig, ax = plt.subplots()
    ax.plot(v, f, "g-")
    ax.set_title(f"Maxwell-Boltzmann Speed Distribution (T = {temperature} K)")
    ax.set_xlabel("Speed (m/s)")
    ax.set_ylabel("Probability Density")
    plt.show()


def entropy(n=50):
    """Visualizes entropy increase as two gases mix over time."""
    rng = np.random.default_rng(1)
    # Particle types: 0 = gas A (starts left half), 1 = gas B (starts right half)
    pos = rng.uniform(0, 10, size=(2 * n, 2))
    pos[:n, 0] = rng.uniform(0, 5, size=n)      # gas A on the left
    pos[n:, 0] = rng.uniform(5, 10, size=n)     # gas B on the right

    angles = rng.uniform(0, 2 * np.pi, size=2 * n)
    vel = 0.12 * np.column_stack([np.cos(angles), np.sin(angles)])
    colors = ["crimson"] * n + ["royalblue"] * n

    fig, ax = plt.subplots()
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 10)
    ax.set_aspect("equal")
    ax.set_title("Entropy: Two Gases Mixing Over Time")
    ax.axvline(5, color="gray", lw=0.5, ls="--")

    scatter = ax.scatter(pos[:, 0], pos[:, 1], s=25, c=colors)

    def update(frame):
        nonlocal pos, vel
        pos = pos + vel
        for dim in (0, 1):
            hit_low = pos[:, dim] < 0
            hit_high = pos[:, dim] > 10
            vel[hit_low | hit_high, dim] *= -1
            pos[:, dim] = np.clip(pos[:, dim], 0, 10)
        scatter.set_offsets(pos)
        return scatter,

    ani = FuncAnimation(fig, update, frames=500, interval=20, blit=True, repeat=True)
    plt.show()