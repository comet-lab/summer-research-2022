#Author Mollie Goldblatt mgoldbl1@umbc.edu 8/25/2022

import numpy as np
import math
import theta_solver as ts
import matplotlib.pyplot as plt


# equation 1 in N. Pacheco 2021

def T_uncut(c):
    identity_matrix = np.identity(3)
    bottom_row = np.zeros(3)
    array1 = np.row_stack((identity_matrix, bottom_row))
    transformation = np.array([[0, 0, c, 1]]).T
    array2 = np.column_stack((array1, transformation))
    return array2


# equation 2 in N. Pacheco 2021
def T_notch(theta, kappa):
    
    T = np.zeros((4, 4))
    
    T[0][0] = np.cos(theta)
    T[0][2] = np.sin(theta)
    if kappa != 0:
        T[0][3] = (1-np.cos(theta))/kappa
            
    T[1][1] = 1
    
    T[2][0] = -1 * np.sin(theta)
    T[2][2] = np.cos(theta)
    if kappa != 0:
        T[2][3] = np.sin(theta)/kappa

    T[3][3] = 1

    return T


#(forces, deflections, kappas) = ts.find_forces_thetas_kappas(n, max_force, r_outer, r_inner, g_array, h_array, mu, E_linear, E_super, epsilon_low)

# takes the forces and deflections for ts.find_forces_thetas_kappas and finds the force where the wrist won't bend anymore

def force_at_max_theta(forces, deflections):
    previous_theta = 1
    for index in range(1, len(forces)):
        if np.array_equal(deflections[index-1], deflections[index]):
            return forces[index-1]

    return forces[-1]


# takes the forces and deflections from ts.find_forces_thetas_kappas and picks out several forces for the wrist shape graph. 
def modify_arrays(forces, deflections, kappas):
    new_forces = np.array([])
    
    force_at_max = force_at_max_theta(forces, deflections)
    last_index = forces.tolist().index(force_at_max)
    skip = max(1, last_index//8)
    
    for num in range(last_index, 0, -skip):
        new_forces = np.append(new_forces, forces[num]) 

    new_deflections = np.zeros([len(new_forces), len(deflections[0])])
    new_kappas = np.zeros([len(new_forces), len(kappas[0])])

    index2 = 0
    for num in range(last_index, 0, -skip):
        new_deflections[index2] = deflections[num]
        new_kappas[index2] = kappas[num]
        index2 += 1

    return (new_forces, new_deflections, new_kappas)



# equation 1 in N. Pacheco 2021

def find_positions(c_array, n, kappas, deflections):
    zeros = np.array([0, 0, 0, 1])
    position_array = np.zeros((2*n+1, 4))
    position_index = 0
    position_array[position_index] = zeros
    position_index +=1
    T = np.identity(4)
    for notch_index in range(0, n):
        T = np.matmul(T, T_notch(deflections[notch_index], kappas[notch_index]))
        position = np.matmul(T,zeros)
        position_array[position_index] = position
        position_index += 1
        T = np.matmul(T, T_uncut(c_array[notch_index]))
        position = np.matmul(T, zeros)
        position_array[position_index] = position
        position_index +=1
    return position_array


# calls find_positions for multiple forces and deflections. 
def find_x_and_z_coordinates(forces, c_array, n, kappas, deflections):
    new_forces, new_deflections, new_kappas = modify_arrays(forces, deflections, kappas)
    x_array = np.zeros((len(new_forces), 2*n +1))
    z_array = np.zeros((len(new_forces), 2*n +1))
    
    for index in range(0, len(new_forces)):
        force = new_forces[index]
        deflections = new_deflections[index]
        kappas = new_kappas[index]
        position_array = find_positions(c_array, n, kappas, deflections)
        transposed = position_array.transpose()
        xs = 1000*transposed[0]
        zs = 1000*transposed[2]
        x_array[index] = xs
        z_array[index] = zs

    return (new_forces, x_array, z_array)

# calls find_positions for one force for 3d wrist graph.
def find_x_and_z_coordinates_for_one_force(force, c_array, n, kappas, deflections):
    x_array = np.zeros((2*n +1))
    z_array = np.zeros((2*n +1))
    position_array = find_positions(c_array, n, kappas, deflections)
    transposed = position_array.transpose()
    xs = 1000*transposed[0]
    zs = 1000*transposed[2]
    x_array = xs
    z_array = zs
    return (force, x_array, z_array)
    

#returns matplotlib figure of the wrist shapes.     
def graph_wrist_shape(new_forces, x_array, z_array, fignum):
    fig = plt.figure(num=fignum)
    fig.set_figheight(8.5)
    fig.set_figwidth(10.5)
    colors = ['#0000FF', '#6082B6', '#5D3FD3', '#1F51FF', '#CCCCFF', '#4169E1', '#87CEEB', '#4682B4', '#A7C7E7', '#89CFF0', '#0096FF', '#0047AB', '#6495ED', '#1434A4', '#7DF9FF']
    
    plt.title('Wrist Shape')
    plt.xlabel('X axis (mm)')
    plt.ylabel('Z axis (mm)')
    for k in range(0, len(new_forces)):
        plt.plot(x_array[k], z_array[k], color=colors[k], marker=".", markersize=7, label = '{} N'.format(round(new_forces[k], 4)))
        plt.legend(title="Forces", loc='upper right')
    return fig


#force, deflections, final_kappas = find_thetas_kappas_for_one_force(n, force, r_outer, r_inner, g_array, h_array, mu, E_linear, E_super, epsilon_low)

#force, x_array, z_array = find_x_and_z_coordinates_for_one_force(force, c_array, n)    
