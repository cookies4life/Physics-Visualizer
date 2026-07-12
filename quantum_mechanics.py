"""
Quantum Mechanics module.
Contains: wave function, double-slit experiment, particle probability.
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation


def start():
    while True:
        print("\n--- Quantum Mechanics ---")
        print("1. Wave Function")
        print("2. Double Slit Experiment")
        print("3. Particle Probability Density")
        print("0. Back to main menu")

        choice = input("Choose an option: ").strip()

        if choice == "1":
            wave_function()
        elif choice == "2":
            double_slit()
        elif choice == "3":
            particle_probability()
        elif choice == "0":
            break
        else:
            print("Invalid choice, try again.")


def wave_function():
    """Animates a traveling Gaussian wave packet (real part + envelope)."""
    x = np.linspace(-10, 10, 800)
    k0 = 3.0     # central wave number
    sigma = 1.5  # packet width

    fig, ax = plt.subplots()
    ax.set_xlim(-10, 10)
    ax.set_ylim(-1.2, 1.2)
    ax.set_title("Wave Function (Gaussian Wave Packet)")

    envelope_top, = ax.plot([], [], "r--", lw=1)
    envelope_bot, = ax.plot([], [], "r--", lw=1)
    wave_line, = ax.plot([], [], "b-", lw=1.5)

    def update(frame):
        t = frame * 0.05
        x0 = -6 + t * 2
        envelope = np.exp(-((x - x0) ** 2) / (2 * sigma**2))
        psi_real = envelope * np.cos(k0 * x - t * 2)

        envelope_top.set_data(x, envelope)
        envelope_bot.set_data(x, -envelope)
        wave_line.set_data(x, psi_real)
        return envelope_top, envelope_bot, wave_line

    ani = FuncAnimation(fig, update, frames=150, interval=30, blit=True, repeat=True)
    plt.show()


def double_slit():
    """Plots the classic double-slit interference intensity pattern."""
    screen_x = np.linspace(-0.02, 0.02, 2000)  # meters, position on screen
    wavelength = 500e-9   # green light
    d = 0.0005            # slit separation
    L = 1.0               # screen distance

    theta = np.arctan(screen_x / L)
    beta = (np.pi * d * np.sin(theta)) / wavelength
    intensity = np.cos(beta) ** 2

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(7, 6))
    ax1.plot(screen_x * 1000, intensity, "b-")
    ax1.set_title("Double Slit Interference Pattern")
    ax1.set_xlabel("Screen position (mm)")
    ax1.set_ylabel("Relative Intensity")

    # Visual "fringes" as an image band
    fringe_img = np.tile(intensity, (100, 1))
    ax2.imshow(fringe_img, cmap="inferno", aspect="auto",
               extent=[screen_x[0] * 1000, screen_x[-1] * 1000, 0, 1])
    ax2.set_yticks([])
    ax2.set_xlabel("Screen position (mm)")
    ax2.set_title("Fringe Pattern")

    plt.tight_layout()
    plt.show()


def particle_probability():
    """Plots |psi|^2 for a particle in an infinite square well (n=1..3)."""
    x = np.linspace(0, 1, 500)
    fig, ax = plt.subplots()

    for n in [1, 2, 3]:
        psi = np.sqrt(2) * np.sin(n * np.pi * x)
        prob = psi**2
        ax.plot(x, prob, label=f"n = {n}")

    ax.set_title("Particle in a Box: Probability Density |ψ|²")
    ax.set_xlabel("Position (x / L)")
    ax.set_ylabel("Probability Density")
    ax.legend()
    plt.show()