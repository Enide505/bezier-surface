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


def rotate_x(point, angle):
    cos_theta = math.cos(angle)
    sin_theta = math.sin(angle)
    x, y, z = point
    return np.array([x, y * cos_theta - z * sin_theta, y * sin_theta + z * cos_theta])


def rotate_y(point, angle):
    cos_theta = math.cos(angle)
    sin_theta = math.sin(angle)
    x, y, z = point
    return np.array([x * cos_theta + z * sin_theta, y, -x * sin_theta + z * cos_theta])


def apply_rotation(control_points, angle_x, angle_y):
    rotated_points = np.array([
        [rotate_y(rotate_x(point, angle_x), angle_y) for point in row]
        for row in control_points
    ])
    return rotated_points


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

    rotated_points = apply_rotation(control_points, np.radians(rotation_x), np.radians(rotation_y))

    if show_surface.get():
        surface = bezier_surface(rotated_points)
        ax.plot_surface(surface[:, :, 0], surface[:, :, 1], surface[:, :, 2], cmap='viridis', alpha=0.6)

    if show_lines.get():
        for row in rotated_points:
            ax.plot(row[:, 0], row[:, 1], row[:, 2], 'ro-', markersize=5)
        for col in rotated_points.transpose(1, 0, 2):
            ax.plot(col[:, 0], col[:, 1], col[:, 2], 'ro-', markersize=5)

    label_counter = 0
    for i, row in enumerate(rotated_points):
        for j, point in enumerate(row):
            label = chr(65 + label_counter)
            ax.text(point[0], point[1], point[2], label, color='black', fontsize=10)
            label_counter += 1

    ax.quiver(0, 0, 0, 1.5, 0, 0, color='red', arrow_length_ratio=0.1)
    ax.quiver(0, 0, 0, 0, 1.5, 0, color='green', arrow_length_ratio=0.1)
    ax.quiver(0, 0, 0, 0, 0, 1.5, color='blue', arrow_length_ratio=0.1)
    ax.text(1.5, 0, 0, 'X', color='red')
    ax.text(0, 1.5, 0, 'Y', color='green')
    ax.text(0, 0, 1.5, 'Z', color='blue')

    set_fixed_axis_limits()
    canvas.draw()


def add_point():
    global control_points
    dx, dy, dz = 1, 1, 0.5
    last_point = control_points[-1, -1]

    new_col = np.array([
        last_point + np.array([dx * i, dy * j, dz])
        for i in range(control_points.shape[0])
        for j in range(1)
    ]).reshape(-1, 1, 3)

    control_points = np.hstack((control_points, new_col))

    refresh_sliders()
    update_plot(0, 0)


def remove_last_point():
    global control_points
    if control_points.shape[1] > 1:
        control_points = control_points[:, :-1, :]
        refresh_sliders()
        update_plot(0, 0)
    else:
        print("Невозможно удалить точку: должна остаться хотя бы одна точка.")


def update_point(i, j, axis, value):
    control_points[i, j, axis] = value
    update_plot(0, 0)


def refresh_sliders():
    for widget in frame_points.winfo_children():
        widget.destroy()

    for i, row in enumerate(control_points):
        for j, point in enumerate(row):
            for k, coord in enumerate(point):
                label = tk.Label(frame_points, text=f"{chr(65 + i * control_points.shape[1] + j)}[{k}]:")
                label.grid(row=i * control_points.shape[1] + j, column=k * 2)
                slider = ttk.Scale(
                    frame_points, from_=-10, to=10, orient=tk.HORIZONTAL,
                    command=lambda val, i=i, j=j, k=k: update_point(i, j, k, float(val))
                )
                slider.set(coord)
                slider.grid(row=i * control_points.shape[1] + j, column=k * 2 + 1)


root = tk.Tk()
root.title("Безье Поверхность")

root.protocol("WM_DELETE_WINDOW", root.quit)

frame_controls = tk.Frame(root)
frame_controls.pack(side=tk.LEFT, fill=tk.BOTH)

rotation_x_label = tk.Label(frame_controls, text="Поворот вокруг X:")
rotation_x_label.pack()
slider_x = ttk.Scale(frame_controls, from_=-180, to=180, orient=tk.HORIZONTAL,
                     command=lambda val: update_plot(float(val), float(slider_y.get())))
slider_x.pack()

rotation_y_label = tk.Label(frame_controls, text="Поворот вокруг Y:")
rotation_y_label.pack()
slider_y = ttk.Scale(frame_controls, from_=-180, to=180, orient=tk.HORIZONTAL,
                     command=lambda val: update_plot(float(slider_x.get()), float(val)))
slider_y.pack()

show_surface = tk.BooleanVar(value=True)
show_surface_check = tk.Checkbutton(frame_controls, text="Показать поверхность", variable=show_surface,
                                    command=lambda: update_plot(float(slider_x.get()), float(slider_y.get())))
show_surface_check.pack()

show_lines = tk.BooleanVar(value=True)
show_lines_check = tk.Checkbutton(frame_controls, text="Показать линии", variable=show_lines,
                                  command=lambda: update_plot(float(slider_x.get()), float(slider_y.get())))
show_lines_check.pack()

button_add_point = tk.Button(frame_controls, text="Добавить точку", command=add_point)
button_add_point.pack()

button_remove_point = tk.Button(frame_controls, text="Удалить точку", command=remove_last_point)
button_remove_point.pack()

frame_points = tk.Frame(root)
frame_points.pack(side=tk.RIGHT, fill=tk.BOTH)

control_points = np.array([
    [[-1, -1, 0], [0, -1, 1], [1, -1, 0]],
    [[-1, 0, 1], [0, 0, 2], [1, 0, 1]],
    [[-1, 1, 0], [0, 1, 1], [1, 1, 0]]
])

refresh_sliders()

fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')
canvas = FigureCanvasTkAgg(fig, master=root)
canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)

update_plot(0, 0)

root.mainloop()
