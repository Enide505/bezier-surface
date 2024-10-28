import numpy as np
import math
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import tkinter as tk
from tkinter import ttk


def bernstein_poly(i, n, t):
    return math.comb(n, i) * (t ** i) * ((1 - t) ** (n - i))


def bezier_surface(control_points, resolution=20):
    u = np.linspace(0, 1, resolution)
    v = np.linspace(0, 1, resolution)
    U, V = np.meshgrid(u, v)
    n, m = control_points.shape[:2]
    surface = np.zeros((resolution, resolution, 3))

    for i in range(n):
        for j in range(m):
            B_ij = bernstein_poly(i, n - 1, U) * bernstein_poly(j, m - 1, V)
            surface[:, :, 0] += B_ij * control_points[i, j, 0]
            surface[:, :, 1] += B_ij * control_points[i, j, 1]
            surface[:, :, 2] += B_ij * control_points[i, j, 2]

    return surface


def update_plot(rotation_x, rotation_y):
    ax.clear()
    surface = bezier_surface(control_points)
    ax.plot_surface(surface[:, :, 0], surface[:, :, 1], surface[:, :, 2], cmap='viridis')

    ax.quiver(0, 0, 0, 1.5, 0, 0, color='red', arrow_length_ratio=0.1)  # Ось X
    ax.quiver(0, 0, 0, 0, 1.5, 0, color='green', arrow_length_ratio=0.1)  # Ось Y
    ax.quiver(0, 0, 0, 0, 0, 1.5, color='blue', arrow_length_ratio=0.1)  # Ось Z

    ax.text(1.5, 0, 0, 'X', color='red')
    ax.text(0, 1.5, 0, 'Y', color='green')
    ax.text(0, 0, 1.5, 'Z', color='blue')

    ax.view_init(rotation_x, rotation_y)
    canvas.draw()


root = tk.Tk()
root.title("Поверхность Безье")

control_points = np.array([[[0, 0, 0], [1, 0, 1], [2, 0, 0]],
                           [[0, 1, 1], [1, 1, 2], [2, 1, 1]],
                           [[0, 2, 0], [1, 2, 1], [2, 2, 0]]])

fig = plt.figure(figsize=(8, 6))
ax = fig.add_subplot(111, projection='3d')
canvas = FigureCanvasTkAgg(fig, master=root)
canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

update_plot(30, 30)

frame_controls = ttk.Frame(root)
frame_controls.pack(side=tk.BOTTOM, fill=tk.X)

tk.Label(frame_controls, text="Поворот по оси X:").pack(side=tk.LEFT)
slider_x = ttk.Scale(frame_controls, from_=0, to=360, orient=tk.HORIZONTAL,
                     command=lambda x: update_plot(float(slider_x.get()), float(slider_y.get())))
slider_x.set(30)
slider_x.pack(side=tk.LEFT, fill=tk.X, expand=1)

tk.Label(frame_controls, text="Поворот по оси Y:").pack(side=tk.LEFT)
slider_y = ttk.Scale(frame_controls, from_=0, to=360, orient=tk.HORIZONTAL,
                     command=lambda y: update_plot(float(slider_x.get()), float(slider_y.get())))
slider_y.set(30)
slider_y.pack(side=tk.LEFT, fill=tk.X, expand=1)

root.mainloop()
