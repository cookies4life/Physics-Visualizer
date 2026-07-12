"""
Classical Mechanics module.
Contains: projectile motion, pendulum, collisions.
Each simulation opens a matplotlib window.
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation


def start():
    while True:
        print("\n--- Classical Mechanics ---")
        print("1. Projectile Motion")
        print("2. Pendulum")
        print("3. Collision")
        print("0. Back to main menu")

        choice = input("Choose an option: ").strip()

        if choice == "1":
            projectile_motion()
        elif choice == "2":
            pendulum()
        elif choice == "3":
            collision()
        elif choice == "0":
            break
        else:
            print("Invalid choice, try again.")


def projectile_motion(v0=40, angle_deg=45, g=9.81):
    """Animates a projectile's trajectory."""
    angle = np.radians(angle_deg)
    vx, vy = v0 * np.cos(angle), v0 * np.sin(angle)

    t_flight = 2 * vy / g
    t = np.linspace(0, t_flight, 200)
    x = vx * t
    y = vy * t - 0.5 * g * t**2

    fig, ax = plt.subplots()
    ax.set_xlim(0, x.max() * 1.1)
    ax.set_ylim(0, y.max() * 1.2)
    ax.set_title("Projectile Motion")
    ax.set_xlabel("Distance (m)")
    ax.set_ylabel("Height (m)")

    trail, = ax.plot([], [], "b-", lw=1)
    point, = ax.plot([], [], "ro", markersize=8)

    def update(frame):
        trail.set_data(x[:frame], y[:frame])
        point.set_data([x[frame]], [y[frame]])
        return trail, point

    ani = FuncAnimation(fig, update, frames=len(t), interval=15, blit=True, repeat=False)
    plt.show()


def pendulum(length=2.0, theta0_deg=30, g=9.81, duration=10):
    """Animates a simple pendulum (small-angle approximation)."""
    theta0 = np.radians(theta0_deg)
    omega = np.sqrt(g / length)

    t = np.linspace(0, duration, 500)
    theta = theta0 * np.cos(omega * t)

    x = length * np.sin(theta)
    y = -length * np.cos(theta)

    fig, ax = plt.subplots()
    ax.set_xlim(-length * 1.2, length * 1.2)
    ax.set_ylim(-length * 1.2, length * 0.2)
    ax.set_aspect("equal")
    ax.set_title("Pendulum")

    rod, = ax.plot([], [], "k-", lw=2)
    bob, = ax.plot([], [], "bo", markersize=14)

    def update(frame):
        rod.set_data([0, x[frame]], [0, y[frame]])
        bob.set_data([x[frame]], [y[frame]])
        return rod, bob

    ani = FuncAnimation(fig, update, frames=len(t), interval=20, blit=True, repeat=True)
    plt.show()


def collision(m1=2.0, m2=1.0, v1=3.0, v2=-2.0, duration=6):
    """Animates a 1D elastic collision between two masses."""
    # Elastic collision result (used after they meet)
    v1f = ((m1 - m2) * v1 + 2 * m2 * v2) / (m1 + m2)
    v2f = ((m2 - m1) * v2 + 2 * m1 * v1) / (m1 + m2)

    x1_start, x2_start = -5.0, 5.0
    r1, r2 = 0.3 * m1**0.5, 0.3 * m2**0.5

    t = np.linspace(0, duration, 400)
    dt = t[1] - t[0]

    x1 = np.zeros_like(t)
    x2 = np.zeros_like(t)
    x1[0], x2[0] = x1_start, x2_start
    collided = False

    for i in range(1, len(t)):
        if not collided:
            x1[i] = x1[i - 1] + v1 * dt
            x2[i] = x2[i - 1] + v2 * dt
            if x2[i] - x1[i] <= (r1 + r2):
                collided = True
                v1, v2 = v1f, v2f
        else:
            x1[i] = x1[i - 1] + v1 * dt
            x2[i] = x2[i - 1] + v2 * dt

    fig, ax = plt.subplots()
    ax.set_xlim(x1_start - 2, x2_start + 2)
    ax.set_ylim(-1, 1)
    ax.set_title("1D Elastic Collision")
    ax.axhline(0, color="gray", lw=0.5)

    ball1, = ax.plot([], [], "ro", markersize=20 * r1)
    ball2, = ax.plot([], [], "bo", markersize=20 * r2)

    def update(frame):
        ball1.set_data([x1[frame]], [0])
        ball2.set_data([x2[frame]], [0])
        return ball1, ball2

    ani = FuncAnimation(fig, update, frames=len(t), interval=15, blit=True, repeat=False)
    plt.show()