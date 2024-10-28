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


def set_fixed_axis_limits():
    control_points_np = np.array(control_points)
    x_min, x_max = control_points_np[:, :, 0].min(), control_points_np[:, :, 0].max()
    y_min, y_max = control_points_np[:, :, 1].min(), control_points_np[:, :, 1].max()
    z_min, z_max = control_points_np[:, :, 2].min(), control_points_np[:, :, 2].max()

    ax.set_xlim(x_min, x_max)
    ax.set_ylim(y_min, y_max)
    ax.set_zlim(z_min, z_max)


def update_plot(rotation_x, rotation_y):
    ax.clear()

    if show_surface.get():
        surface = bezier_surface(np.array(control_points))
        ax.plot_surface(surface[:, :, 0], surface[:, :, 1], surface[:, :, 2], cmap='viridis', alpha=0.6)

    control_points_np = np.array(control_points)
    if show_lines.get():
        for row in control_points_np:
            ax.plot(row[:, 0], row[:, 1], row[:, 2], 'ro-', markersize=5)
        for col in control_points_np.transpose(1, 0, 2):
            ax.plot(col[:, 0], col[:, 1], col[:, 2], 'ro-', markersize=5)

    ax.quiver(0, 0, 0, 1.5, 0, 0, color='red', arrow_length_ratio=0.1)
    ax.quiver(0, 0, 0, 0, 1.5, 0, color='green', arrow_length_ratio=0.1)
    ax.quiver(0, 0, 0, 0, 0, 1.5, color='blue', arrow_length_ratio=0.1)
    ax.text(1.5, 0, 0, 'X', color='red')
    ax.text(0, 1.5, 0, 'Y', color='green')
    ax.text(0, 0, 1.5, 'Z', color='blue')

    ax.view_init(rotation_x, rotation_y)
    set_fixed_axis_limits()
    canvas.draw()


def add_point():
    for row in control_points:
        row.append([row[-1][0] + 1, row[-1][1], row[-1][2]])
    update_plot(float(slider_x.get()), float(slider_y.get()))


def remove_point():
    if all(len(row) > 1 for row in control_points):
        for row in control_points:
            row.pop()
        update_plot(float(slider_x.get()), float(slider_y.get()))


root = tk.Tk()
root.title("Поверхность Безье")

control_points = [[[0, 0, 0], [1, 0, 1], [2, 0, 0]],
                  [[0, 1, 1], [1, 1, 2], [2, 1, 1]],
                  [[0, 2, 0], [1, 2, 1], [2, 2, 0]]]

fig = plt.figure(figsize=(8, 6))
ax = fig.add_subplot(111, projection='3d')
canvas = FigureCanvasTkAgg(fig, master=root)
canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

show_surface = tk.BooleanVar(value=True)
show_lines = tk.BooleanVar(value=True)

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

button_add_point = tk.Button(frame_controls, text="Добавить точку", command=add_point)
button_add_point.pack(side=tk.LEFT)

button_remove_point = tk.Button(frame_controls, text="Удалить точку", command=remove_point)
button_remove_point.pack(side=tk.LEFT)

check_surface = tk.Checkbutton(frame_controls, text="Отображение поверхности", variable=show_surface,
                               command=lambda: update_plot(float(slider_x.get()), float(slider_y.get())))
check_surface.pack(side=tk.LEFT)

check_lines = tk.Checkbutton(frame_controls, text="Отображение прямых", variable=show_lines,
                             command=lambda: update_plot(float(slider_x.get()), float(slider_y.get())))
check_lines.pack(side=tk.LEFT)

root.mainloop()
