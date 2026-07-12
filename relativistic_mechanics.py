"""
Relativistic Mechanics module.
Contains: time dilation, length contraction, spacetime visualization.
"""

import numpy as np
import matplotlib.pyplot as plt

C = 3e8  # speed of light (m/s)


def start():
    while True:
        print("\n--- Relativistic Mechanics ---")
        print("1. Time Dilation")
        print("2. Length Contraction")
        print("3. Spacetime Diagram")
        print("0. Back to main menu")

        choice = input("Choose an option: ").strip()

        if choice == "1":
            time_dilation()
        elif choice == "2":
            length_contraction()
        elif choice == "3":
            spacetime_diagram()
        elif choice == "0":
            break
        else:
            print("Invalid choice, try again.")


def _gamma(v_fraction_of_c):
    beta = v_fraction_of_c
    return 1 / np.sqrt(1 - beta**2)


def time_dilation():
    """Plots the Lorentz factor (and dilated time) vs velocity."""
    beta = np.linspace(0, 0.999, 500)
    gamma = _gamma(beta)

    fig, ax = plt.subplots()
    ax.plot(beta, gamma, "b-")
    ax.set_title("Time Dilation: γ vs v/c")
    ax.set_xlabel("v / c")
    ax.set_ylabel("γ (time dilation factor)")
    ax.grid(True)

    proper_time = 1.0  # 1 second in the moving frame
    dilated = proper_time * gamma
    print(f"\nExample: 1 second in the moving frame at v = 0.9c "
          f"appears as {proper_time * _gamma(0.9):.2f} s to a stationary observer.")

    plt.show()


def length_contraction():
    """Plots contracted length vs velocity for a rest-length rod."""
    L0 = 10.0  # rest length (meters)
    beta = np.linspace(0, 0.999, 500)
    L = L0 * np.sqrt(1 - beta**2)

    fig, ax = plt.subplots()
    ax.plot(beta, L, "r-")
    ax.set_title(f"Length Contraction (rest length = {L0} m)")
    ax.set_xlabel("v / c")
    ax.set_ylabel("Observed length (m)")
    ax.grid(True)
    plt.show()


def spacetime_diagram():
    """Draws a simple Minkowski spacetime diagram with light cones."""
    fig, ax = plt.subplots()
    t = np.linspace(-10, 10, 100)

    ax.plot(t, t, "y--", label="Light cone (future)")
    ax.plot(t, -t, "y--", label="Light cone (past)")

    # A worldline for an object moving at v = 0.5c
    v_over_c = 0.5
    ax.plot(v_over_c * t, t, "b-", label="Worldline (v = 0.5c)")

    ax.axhline(0, color="gray", lw=0.5)
    ax.axvline(0, color="gray", lw=0.5)
    ax.set_xlim(-10, 10)
    ax.set_ylim(-10, 10)
    ax.set_xlabel("x (space)")
    ax.set_ylabel("ct (time)")
    ax.set_title("Spacetime Diagram")
    ax.legend()
    ax.set_aspect("equal")
    plt.show()