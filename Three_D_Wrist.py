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


# helper function for set_axes_equal
def _set_axes_radius(ax, origin, radius):
    x, y, z = origin
    ax.set_xlim3d([x - radius, x + radius])
    ax.set_ylim3d([y - radius, y + radius])
    ax.set_zlim3d([z - radius, z + radius])

# https://stackoverflow.com/questions/13685386/matplotlib-equal-unit-length-with-equal-aspect-ratio-z-axis-is-not-equal-to
# (answer by AndrewCox)
def set_axes_equal(ax):
    """Set 3D plot axes to equal scale.

    Make axes of 3D plot have equal scale so that spheres appear as
    spheres and cubes as cubes.  Required since `ax.axis('equal')`
    and `ax.set_aspect('equal')` don't work on 3D.
    """
    limits = np.array([
        ax.get_xlim3d(),
        ax.get_ylim3d(),
        ax.get_zlim3d(),
    ])
    origin = np.mean(limits, axis=1)
    radius = 0.5 * np.max(np.abs(limits[:, 1] - limits[:, 0]))
    _set_axes_radius(ax, origin, radius)

# returns x, y, and z coordinates for the uncut cylinder, so matplotlib can plot it with plotsurface.
# axis point 1 is the center of the tube at the bottom of the uncut cylinder
# axis point 2 is the center of the tube at the top of the uncut cylinder
def cylinder(r_outer, axis_point1, axis_point2):
    b = np.array([0, 1, 0])
    if axis_point1[-1] == axis_point2[-1]:
        a = np.array([1, 0, 0])
    else:
        m = (axis_point2[2] - axis_point1[2])/(axis_point2[0] - axis_point1[0])
        a = np.array([m/math.sqrt(m**2 +1), 0, -1/math.sqrt(m**2 +1)])

    t = np.linspace(0, 1, 10)
        
    omega = np.linspace(0, 2*math.pi, 20)

    ts, omegas = np.meshgrid(t, omega)

    centers_x = (1-ts)*axis_point1[0] + ts*axis_point2[0]
    centers_y = (1-ts)*axis_point1[1] + ts*axis_point2[1]
    centers_z = (1-ts)*axis_point1[2] + ts*axis_point2[2]

    xs = centers_x + np.cos(omegas)*r_outer*a[0] + np.sin(omegas)*r_outer*b[0]
    ys = centers_y + np.cos(omegas)*r_outer*a[1] + np.sin(omegas)*r_outer*b[1]
    zs = centers_z + np.cos(omegas)*r_outer*a[2] + np.sin(omegas)*r_outer*b[2]

    return xs, ys, zs

# plots the uncut section 
def plot_uncut(axis_point1, axis_point2, r_outer, ax):
    xs, ys, zs = cylinder(r_outer, axis_point1, axis_point2)
    ax.plot_surface(xs, ys, zs, color='orange')

# axis point 1 is the center of the tube at the bottom of the cut section.
# axis point 2 is the center of the tube at the top of the cut section.
# the bend center is the center of the circle that the cut section bends around.
# the distance from the bend center to axis point 1 is R = 1/kappa.
# the distance from the bend center to axis point 2 is R = 1/kappa.
# axis point 1, axis point 2, and the bend center are the corners of an isosceles triangle.
# the angles of the isosceles triangle are theta (bend center), beta (axis point 1), beta (axis point2).
# the angle alpha is the angle between the x axis and the line: axis point 1-axis point 2.
# the angle gamma is beta - alpha.
# gamma is the angle between the x axis and the line: axis point 1-bend center.


def find_gamma(axis_point1, axis_point2, theta):
    if axis_point1[0] == axis_point2[0] and axis_point1[2] < axis_point2[2]:
        return math.pi/2
    elif axis_point1[0] == axis_point2[0] and axis_point1[2] > axis_point2[2]:
        return -math.pi/2
    else:
        m = (axis_point2[2] - axis_point1[2])/(axis_point2[0] - axis_point1[0])
        beta = (math.pi-theta)/2
        alpha = math.atan(m)
        gamma = beta - alpha
        if axis_point1[0] < axis_point2[0]:
            return gamma
        else:
            return gamma - math.pi

# find the bend center from axis point 1, R = 1/kappa, and gamma
def find_bend_center(axis_point1, R, gamma):
    xbc = axis_point1[0]+R*math.cos(gamma)
    zbc = axis_point1[2] - R*math.sin(gamma)
    bend_center = np.array([xbc, 0, zbc])
    return bend_center

# plot a cut section of the tube from kappa, theta, axis point 1, and axis point 2.
# psi is an angle that gives points on the arc that connects axis point 1 and axis point 2.
# psi goes from 0 to theta.
# omega is an angle that gives points on the tube in part of a circle around a values of psi.
# omega goes from -phi/2 to phi/2
# phi is the angle of the sector from equation A.5 in masters thesis by N. Pacheco.
# unit vector [a0, a1, a2] points from the bend center to a point on the arc that connects axis point 1 and axis point 2. 

def plot_cut(kappa, theta, axis_point1, axis_point2, phi, r_outer, ax):
    
    R = 1/kappa
    gamma = find_gamma(axis_point1, axis_point2, theta)
    bend_center = find_bend_center(axis_point1, R, gamma)
    psi = np.linspace(0, theta, 8)
    omega = np.linspace(-phi/2, phi/2, 8)
    psis, omegas = np.meshgrid(psi, omega)

    x_centers = bend_center[0] - R*np.cos(gamma+psis)
    z_centers = bend_center[2] + R*np.sin(gamma+psis)
    y_centers = 0 * x_centers
     

    a0 = -np.cos(gamma+psis)
    a1 = 0
    a2 = np.sin(gamma+psis)
    
    b = np.array([0, 1, 0])
    
    xs = x_centers + r_outer * np.cos(omegas) * a0 + r_outer * np.sin(omegas) * b[0]
    ys = y_centers + r_outer * np.cos(omegas) * a1 + r_outer * np.sin(omegas) * b[1]
    zs = z_centers + r_outer * np.cos(omegas) * a2 + r_outer * np.sin(omegas) * b[2]

    ax.plot_surface(xs, ys, zs, color='#90ee90')
    
# plots the uncut and cut sections of the wrist  
def plot_3d_wrist(r_outer, x_array, z_array, n, fignum, kappa_array, theta_array, phi_array):
    kappa_array_mm = kappa_array/1000
    
    fig3d = plt.figure(num=fignum)
    ax3d = plt.axes(projection ='3d')
    fig3d.set_figheight(8.5)
    fig3d.set_figwidth(10.5)

    for index in range(0, 2*n+1):
        if index % 2 != 0:
            axis_point1 = np.array([x_array[index], 0, z_array[index]])
            axis_point2 = np.array([x_array[index + 1], 0, z_array[index + 1]])
            
            plot_uncut(axis_point1, axis_point2, r_outer, ax3d)
        elif index % 2 == 0 and index != 2*n:
            axis_point1 = np.array([x_array[index], 0, z_array[index]])
            axis_point2 = np.array([x_array[index + 1], 0, z_array[index + 1]])
            
            plot_cut(kappa_array_mm[index//2], theta_array[index//2], axis_point1, axis_point2, phi_array[index//2], r_outer, ax3d)          
            
             
            
    ax3d.set_box_aspect([1,1,1])
    set_axes_equal(ax3d)
    ax3d.set_xlabel('X axis')
    ax3d.set_ylabel('Y axis')
    ax3d.set_zlabel('Z axis')
   

    ax3d.view_init(0, -90)

    return fig3d
