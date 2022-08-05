import PySimpleGUI as sg
import theta_solver as ts
import wrist_shape as ws
import numpy as np
import matplotlib as mpl

mpl.use('TkAgg')
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt
import math

#d1 = np.array([1.674, 0, 3.86])
#d2 = np.array([2.517, 0, 4.72])
#r = 0.81

def cylinder(r_outer, axis_point1, axis_point2):
    b = np.array([0, 1, 0])
    if axis_point1[-1] == axis_point2[-1]:
        a = np.array([1, 0, 0])
    else:
        m = (axis_point2[2] - axis_point1[2])/(axis_point2[0] - axis_point1[0])
        a = np.array([m/math.sqrt(m**2 +1), 0, -1/math.sqrt(m**2 +1)])

    t = np.linspace(0, 1, 10)
        
    theta = np.linspace(0, 2*math.pi, 20)

    ts, thetas = np.meshgrid(t, theta)

    centers_x = (1-ts)*axis_point1[0] + ts*axis_point2[0]
    centers_y = (1-ts)*axis_point1[1] + ts*axis_point2[1]
    centers_z = (1-ts)*axis_point1[2] + ts*axis_point2[2]

    xs = centers_x + np.cos(thetas)*r_outer*a[0] + np.sin(thetas)*r_outer*b[0]
    ys = centers_y + np.cos(thetas)*r_outer*a[1] + np.sin(thetas)*r_outer*b[1]
    zs = centers_z + np.cos(thetas)*r_outer*a[2] + np.sin(thetas)*r_outer*b[2]

    return xs, ys, zs


def plot_cylinders(r_outer, x_array, z_array, n, fignum):
    fig3d = plt.figure(num=fignum)
    ax3d = plt.axes(projection ='3d')
    #ax3d = fig3d.add_subplot(1, 1, 1, projection='3d')
    fig3d.set_figheight(8.5)
    fig3d.set_figwidth(10.5)

    for index in range(0, 2*n+1):
        if index % 2 != 0:
            d1 = np.array([x_array[index], 0, z_array[index]])
            d2 = np.array([x_array[index+1], 0, z_array[index+1]])
            xs, ys, zs = cylinder(r_outer, d1, d2)
            right = min(min(xs.flatten()), min(ys.flatten()), min(zs.flatten()))
            left = max(max(xs.flatten()), max(ys.flatten()), max(zs.flatten()))
            ax3d.plot_surface(xs, ys, zs, color='orange')
        
            if index == 1:
                final_right = right
                final_left = left
            else:
                final_right = min(right, final_right)
                final_left = max(left, final_left)

        

    ax3d.set_xlim(final_right, final_left)
    ax3d.set_ylim(final_right, final_left)
    ax3d.set_zlim(final_right, final_left)

    ax3d.set_xlabel('X axis')
    ax3d.set_ylabel('Y axis')
    ax3d.set_zlabel('Z axis')

    ax3d.view_init(0, -90)

    return fig3d
