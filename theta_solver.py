import numpy as np
import scipy.optimize as sp
import math


#equation 15 in N. Pacheco 2021
def find_kappas(n, theta_array, h_array, y_bar_array):
    kappa_array = np.array([])
    for j in range(0, n):
        kappa = theta_array[j]/(h_array[j] - (y_bar_array[j]*theta_array[j]))
        kappa_array = np.append(kappa_array, kappa)
    return kappa_array

#equation 16 in N. Pacheco 2021
def find_epsilons(n, kappa_array, r_outer, y_bar_array):
    epsilon_array = np.array([])
    for j in range(0, n):
        epsilon = (kappa_array[j]*(r_outer - y_bar_array[j]))/(1 + (y_bar_array[j]*kappa_array[j])                )
        epsilon_array = np.append(epsilon_array, epsilon)
    return epsilon_array

#equation 13 in N. Pacheco 2021
def find_sigmas(n, epsilon_array, E_linear, E_super, epsilon_low, sigma_low):
    sigma_array = np.array([])
    for j in range(0, n):
        if epsilon_array[j] <= epsilon_low:
            sigma = epsilon_array[j]*E_linear
        else:
            sigma = sigma_low + (epsilon_array[j] - epsilon_low)*E_super
        sigma_array = np.append(sigma_array, sigma)
    return sigma_array

#equation 14 in N. Pacheco 2021
def update_Es(n, eta, previous_E_array, theta_array, h_array, y_bar_array, r_outer, E_linear, E_super, epsilon_low, sigma_low):

    kappa_array = find_kappas(n, theta_array, h_array, y_bar_array)
    epsilon_array = find_epsilons(n, kappa_array, r_outer, y_bar_array)
    sigma_array = find_sigmas(n, epsilon_array, E_linear, E_super, epsilon_low, sigma_low)
        
    E_array = np.array([])
    
    for j in range(0, n):        
        if epsilon_array[j] == 0:
            E = previous_E_array[j] - eta*(previous_E_array[j] - E_linear)
        else:
            E = previous_E_array[j] - eta*(previous_E_array[j] - (sigma_array[j]/epsilon_array[j]))
            
        E_array = np.append(E_array, E)
    return E_array

# equation 2 in Swaney & York 2016
def find_phi_outers(n, g_array, r_outer):
    phi_outer_array = np.array([])
    for j in range(0, n):
        phi_outer  = 2*np.arccos((g_array[j]-r_outer)/r_outer)
        phi_outer_array = np.append(phi_outer_array, phi_outer)
    return phi_outer_array

# equation 2 in Swaney & York 2016       
def find_phi_inners(n, g_array, r_outer, r_inner):
    phi_inner_array = np.array([])
    for j in range(0, n):
        phi_inner  = 2*np.arccos((g_array[j]-r_outer)/r_inner)
        phi_inner_array = np.append(phi_inner_array, phi_inner)
    return phi_inner_array

# equation 2 in Swaney & York 2016
def find_A_outers(n, r_outer, phi_outer_array):
    A_outer_array = np.array([])
    for j in range(0, n):
        A_outer = r_outer**2 * ((phi_outer_array[j] - np.sin(phi_outer_array[j]))/2)
        A_outer_array = np.append(A_outer_array, A_outer)
    return A_outer_array

# equation 2 in Swaney & York 2016
def find_A_inners(n, r_inner, phi_inner_array):
    A_inner_array = np.array([])
    for j in range(0, n):
        A_inner = r_inner**2 * ((phi_inner_array[j] - np.sin(phi_inner_array[j]))/2)
        A_inner_array = np.append(A_inner_array, A_inner)
    return A_inner_array

# equation 2 in Swaney & York 2016
def find_y_bar_os(n, r_outer, phi_outer_array):
    y_bar_o_array = np.array([])
    for j in range(0, n):
        y_bar_o = (4*r_outer*(np.sin(.5*phi_outer_array[j])**3))/(3*(phi_outer_array[j]-np.sin(phi_outer_array[j])))
        y_bar_o_array = np.append(y_bar_o_array, y_bar_o)
    return y_bar_o_array

# equation 2 in Swaney & York 2016
def find_y_bar_is(n, r_inner, phi_inner_array):
    y_bar_i_array = np.array([])
    for j in range(0, n):
        y_bar_i = (4*r_inner*(np.sin(.5*phi_inner_array[j])**3))/(3*(phi_inner_array[j]-np.sin(phi_inner_array[j])))
        y_bar_i_array = np.append(y_bar_i_array, y_bar_i)
    return y_bar_i_array


# equation 1 in Swaney & York 2016
def find_y_bars(n, r_outer, r_inner, g_array):
    phi_outer_array = find_phi_outers(n, g_array, r_outer)
    phi_inner_array = find_phi_inners(n, g_array, r_outer, r_inner)
    y_bar_o_array = find_y_bar_os(n, r_outer, phi_outer_array)
    y_bar_i_array = find_y_bar_is(n, r_inner, phi_inner_array)
    A_outer_array = find_A_outers(n, r_outer, phi_outer_array)
    A_inner_array = find_A_inners(n, r_inner, phi_inner_array)
    
    y_bar_array = np.array([])
    for j in range(0, n):
        y_bar = (y_bar_o_array[j]*A_outer_array[j] - y_bar_i_array[j]*A_inner_array[j])/(A_outer_array[j] - A_inner_array[j])
        y_bar_array = np.append(y_bar_array, y_bar)
    return y_bar_array

# 1/5 the second moment of the area for an annulus (https://en.wikipedia.org/wiki/Second_moment_of_area)
def find_Is(n, r_outer, r_inner):
    I_array = np.array([])
    for j in range(0, n):
        I = (math.pi/10)*(r_outer**4 - r_inner**4)
        I_array = np.append(I_array, I)
    return I_array


# f(theta) = theta - D*exp(-mu*theta)
def key_function(x, D, mu):
    y = x - D*math.exp(-mu*x)
    return y

#derivative of f(theta)
def key_function_prime(x, D, mu):
    y_prime = 1 + mu*D*math.exp(-mu*x)
    return y_prime

#used Newton's method to solve equation 12 in N. Pacheco 2021
initial_value = 0.0
def find_thetas(n, y_bar_array, h_array, E_array, I_array, mu, r_inner, Fp):
    theta_array = np.array([])
    for j in range(0, n):
       D = (((r_inner + y_bar_array[j])* h_array[j]*Fp)/(E_array[j]*I_array[j]) )* math.exp(-mu * theta_array.sum())
       theta = sp.newton(key_function, initial_value, fprime=key_function_prime, args=(D, mu))
       theta_array = np.append(theta_array, theta)
    return theta_array


#iterative process from section 3.3 in N. Pacheco 2021
def solve_for_thetas(n, y_bar_array, h_array, I_array, mu, r_inner, r_outer, Fp, eta, E_linear, E_super, epsilon_low, sigma_low):
    E_array = E_linear * np.ones(n)
    print('initial E_array', E_array)
    theta_array = find_thetas(n, y_bar_array, h_array, E_array, I_array, mu, r_inner, Fp)
    previous_E_array = E_array
    E_array = update_Es(n, eta, previous_E_array, theta_array, h_array, y_bar_array, r_outer, E_linear, E_super, epsilon_low, sigma_low)
    
    while np.min(np.absolute(E_array - previous_E_array)) >= 10**-4:
        theta_array = find_thetas(n, y_bar_array, h_array, E_array, I_array, mu, r_inner, Fp)
        previous_E_array = E_array
        E_array = update_Es(n, eta, previous_E_array, theta_array, h_array, y_bar_array, r_outer, E_linear, E_super, epsilon_low, sigma_low)

    print('final E_array', E_array)
    return theta_array

#test values
n = 5 # number of notches
mu = 0.13 # coefficient of friction
eta = 0.05 # gradient descent rate (guess)
E_super = 3e9 # Pascals table 3 (given in giga Pascals)
epsilon_low = 0.028 # table 3
sigma_low = 5e8 # figure 6
E_linear = sigma_low/epsilon_low # to be consistent with epsilon_low and sigma_low
r_outer = 0.0009 #millimeters (guess)
r_inner = 0.0007 # millimeters (guess)
h_array = np.array([0.0008, 0.0008, 0.0008, 0.0008, 0.0008]) # table 2
g_array = np.array([0.0014, 0.0014, 0.0014, 0.0014, 0.0014]) #table 2
y_bar_array = find_y_bars(n, r_outer, r_inner, g_array) 
I_array = find_Is(n, r_outer, r_inner) # 1/5 of the second moment of area for an annulus 
Fp = 500 #Newtons (guess)


print('final theta_array', solve_for_thetas(n, y_bar_array, h_array, I_array, mu, r_inner, r_outer, Fp, eta, E_linear, E_super, epsilon_low, sigma_low))


# test result: theta_array = [0.73846696 0.63541634 0.55247992 0.48449348 0.42790712]
# final E_array values = [5.28022990e+09 5.65003325e+09 6.04784730e+09 6.47553580e+09 6.93514007e+09]
