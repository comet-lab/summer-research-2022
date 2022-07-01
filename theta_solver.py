import numpy as np
import scipy.optimize as sp
import math
import matplotlib.pyplot as plt


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
        epsilon = (kappa_array[j]*(r_outer - y_bar_array[j]))/(1 + (y_bar_array[j]*kappa_array[j]))
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

# equation A.7 Masters Thesis
def find_phi(n, g_array, r_outer):
    phi_array = np.array([])
    for j in range(0, n):
        phi = 2*np.arccos((g_array[j]-r_outer)/r_outer)
        phi_array = np.append(phi_array, phi)
    return phi_array

# equation A.7 Masters Thesis
def find_A_outers(n, r_outer, phi_array):
    A_outer_array = np.array([])
    for j in range(0, n):
        A_outer = r_outer**2 * (phi_array[j]/2)
        A_outer_array = np.append(A_outer_array, A_outer)
    return A_outer_array

# equation A.7 Masters Thesis
def find_A_inners(n, r_inner, phi_array):
    A_inner_array = np.array([])
    for j in range(0, n):
        A_inner = r_inner**2 * (phi_array[j]/2)
        A_inner_array = np.append(A_inner_array, A_inner)
    return A_inner_array

# equation A.7 Masters Thesis 
def find_y_bar_os(n, r_outer, phi_array):
    y_bar_o_array = np.array([])
    for j in range(0, n):
        y_bar_o = (2*r_outer*math.sin(phi_array[j]/2))/(3*phi_array[j]/2)
        y_bar_o_array = np.append(y_bar_o_array, y_bar_o)
    return y_bar_o_array

# equation A.7 Masters Thesis 
def find_y_bar_is(n, r_inner, phi_array):
    y_bar_i_array = np.array([])
    for j in range(0, n):
        y_bar_i = (2*r_inner*math.sin(phi_array[j]/2))/(3*phi_array[j]/2)
        y_bar_i_array = np.append(y_bar_i_array, y_bar_i)
    return y_bar_i_array


# equation 1 in Swaney & York 2016
def find_y_bars(n, r_outer, r_inner, g_array):
    phi_array = find_phi(n, g_array, r_outer)
    y_bar_o_array = find_y_bar_os(n, r_outer, phi_array)
    y_bar_i_array = find_y_bar_is(n, r_inner, phi_array)
    A_outer_array = find_A_outers(n, r_outer, phi_array)
    A_inner_array = find_A_inners(n, r_inner, phi_array)
    
    y_bar_array = np.array([])
    for j in range(0, n):
        y_bar = (y_bar_o_array[j]*A_outer_array[j] - y_bar_i_array[j]*A_inner_array[j])/(A_outer_array[j] - A_inner_array[j])
        y_bar_array = np.append(y_bar_array, y_bar)
    return y_bar_array

# https://www.efunda.com/math/areas/CircularSection.cfm
# https://www.efunda.com/math/areas/ParallelAxisTheorem.cfm
def find_Is(n, r_outer, r_inner, g_array, y_bar_array):
    phi_array = find_phi(n, g_array, r_outer)
    A_outer_array = find_A_outers(n, r_outer, phi_array)
    A_inner_array = find_A_inners(n, r_inner, phi_array)
    I_array = np.array([])
    for j in range(0, n):
        I = (((phi_array[j]/2) + .5*math.sin(phi_array[j])) * (((r_outer **4) /4 )- ((r_inner **4) /4 ))
               - y_bar_array[j]**2 * (A_outer_array[j] - A_inner_array[j]))
        I_array = np.append(I_array, I)
    return I_array

# equation 8 York & Swaney 2015
def find_theta_max(n, h_array, r_outer, y_bar_array):
    theta_max_array = np.array([])
    for j in range(0, n):
        theta_max = h_array[j]/(r_outer + y_bar_array[j])
        theta_max_array = np.append(theta_max_array, theta_max)
    return theta_max_array

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
def find_thetas(n, y_bar_array, h_array, E_array, I_array, mu, r_inner, Fp, theta_max_array):
    theta_array = np.array([])
    for j in range(0, n):
       D = (((r_inner + y_bar_array[j])* h_array[j]*Fp)/(E_array[j]*I_array[j]) )* math.exp(-mu * theta_array.sum())
       theta = sp.newton(key_function, initial_value, fprime=key_function_prime, args=(D, mu))
       if theta > theta_max_array[j]:
           theta = theta_max_array[j]
       theta_array = np.append(theta_array, theta)
    return theta_array

#iterative process from section 3.3 in N. Pacheco 2021
def solve_for_thetas(n, y_bar_array, h_array, I_array, theta_max_array, mu, r_inner, r_outer, Fp, eta, E_linear, E_super, epsilon_low, sigma_low):
    E_array = E_linear * np.ones(n)
    #print('initial E_array', E_array)
    theta_array = find_thetas(n, y_bar_array, h_array, E_array, I_array, mu, r_inner, Fp, theta_max_array)
    previous_E_array = E_array
    E_array = update_Es(n, eta, previous_E_array, theta_array, h_array, y_bar_array, r_outer, E_linear, E_super, epsilon_low, sigma_low)

    
    while np.max(np.absolute(E_array - previous_E_array)) >= 1e-4:
        theta_array = find_thetas(n, y_bar_array, h_array, E_array, I_array, mu, r_inner, Fp, theta_max_array)
        previous_E_array = E_array
        E_array = update_Es(n, eta, previous_E_array, theta_array, h_array, y_bar_array, r_outer, E_linear, E_super, epsilon_low, sigma_low)
    #print('final E_array', E_array)
    return theta_array




#test values for wrist A 
n = 5 # number of notches
mu = 0.13 # coefficient of friction
eta = 0.2 # gradient descent rate (guess)
E_super = 3e9 # Pascals table 3 (given in giga Pascals)
epsilon_low = 0.028 # table 3
E_linear = 1e10  # table 3
sigma_low = E_linear*epsilon_low 
r_outer = 0.00081 #millimeters (table 2)
r_inner = 0.0007 # millimeters (table 2)
h_array = np.array([0.0008, 0.0008, 0.0008, 0.0008, 0.0008]) # table 2
g_array = np.array([0.0014, 0.0014, 0.0014, 0.0014, 0.0014]) #table 2
y_bar_array = find_y_bars(n, r_outer, r_inner, g_array) 
I_array = find_Is(n, r_outer, r_inner, g_array, y_bar_array)
theta_max_array = find_theta_max(n, h_array, r_outer, y_bar_array)
Fp = 1.5 #Newtons (figure 9)

#print('y_bar_array', y_bar_array)
#print('final theta_array', solve_for_thetas(n, y_bar_array, h_array, I_array, mu, r_inner, r_outer, Fp, eta, E_linear, E_super, epsilon_low, sigma_low))


# test results:
#y_bar_array [0.00068653 0.00068653 0.00068653 0.00068653 0.00068653]
#initial E_array [1.e+10 1.e+10 1.e+10 1.e+10 1.e+10]
#final E_array [6.66350434e+09 7.02278977e+09 7.40211304e+09 7.80254663e+09 8.22522662e+09]
#final theta_array [0.34665659 0.31569582 0.2884928  0.26443844 0.24304743]








forces = np.arange(0, 2.6, 0.05)
deflections = np.ones((52, 5))


for k in range(0, len(forces)):
    theta_array = solve_for_thetas(n, y_bar_array, h_array, I_array, theta_max_array, mu, r_inner, r_outer, forces[k], eta, E_linear, E_super, epsilon_low, sigma_low)
    deflections[k] = theta_array
        
#print(deflections)

#print(deflections.shape)

figure, axis = plt.subplots(1, 3)
axis[0].set_title('Force Model - Wrist A')
axis[0].set_xlabel('Force')
axis[0].set_ylabel('Deflection')


colors = ['orange', 'green', 'blue', 'red', 'aqua']

deflections = deflections.transpose()

#print(deflections)



for k in range(0, len(deflections)):
    axis[0].plot(forces, deflections[k]*(180/math.pi), color=colors[k])





#test values for wrist B 
n = 5 # number of notches
mu = 0.13 # coefficient of friction
eta = 0.2 # gradient descent rate (guess)
E_super = 3e9 # Pascals table 3 (given in giga Pascals)
epsilon_low = 0.028 # table 3
E_linear = 1e10  # table 3
sigma_low = E_linear*epsilon_low 
r_outer = 0.00081 #millimeters (table 2)
r_inner = 0.0007 # millimeters (table 2)
h_array = np.array([0.0005, 0.0005, 0.0005, 0.0005, 0.0005]) # table 2
g_array = np.array([0.0014, 0.0014, 0.0014, 0.0014, 0.0014]) #table 2
y_bar_array = find_y_bars(n, r_outer, r_inner, g_array) 
I_array = find_Is(n, r_outer, r_inner, g_array, y_bar_array)
theta_max_array = find_theta_max(n, h_array, r_outer, y_bar_array)
Fp = 1.5 #Newtons (figure 9)



forces = np.arange(0, 2.6, 0.05)
deflections = np.ones((52, n))


for k in range(0, len(forces)):
    theta_array = solve_for_thetas(n, y_bar_array, h_array, I_array, theta_max_array, mu, r_inner, r_outer, forces[k], eta, E_linear, E_super, epsilon_low, sigma_low)
    deflections[k] = theta_array
        
#print(deflections)

#print(deflections.shape)



axis[1].set_title('Force Model - Wrist B')
axis[1].set_xlabel('Force')
axis[1].set_ylabel('Deflection')


colors = ['orange', 'green', 'blue', 'red', 'aqua']

deflections = deflections.transpose()

#print(deflections)



for k in range(0, len(deflections)):
    axis[1].plot(forces, deflections[k]*(180/math.pi), color=colors[k])



#test values for wrist C
n = 4 # number of notches
mu = 0.13 # coefficient of friction
eta = 0.2 # gradient descent rate (guess)
E_super = 3e9 # Pascals table 3 (given in giga Pascals)
epsilon_low = 0.028 # table 3
E_linear = 1e10  # table 3
sigma_low = E_linear*epsilon_low 
r_outer = 0.00081 #millimeters (table 2)
r_inner = 0.0007 # millimeters (table 2)
h_array = np.array([0.001, 0.001, 0.001, 0.001]) # table 2
g_array = np.array([0.00136, 0.00139, 0.00142, 0.00145]) #table 2
y_bar_array = find_y_bars(n, r_outer, r_inner, g_array) 
I_array = find_Is(n, r_outer, r_inner, g_array, y_bar_array)
theta_max_array = find_theta_max(n, h_array, r_outer, y_bar_array)
Fp = 1.5 #Newtons (figure 9)


forces = np.arange(0, 2.6, 0.05)
deflections = np.ones((52, 4))


for k in range(0, len(forces)):
    theta_array = solve_for_thetas(n, y_bar_array, h_array, I_array, theta_max_array, mu, r_inner, r_outer, forces[k], eta, E_linear, E_super, epsilon_low, sigma_low)
    deflections[k] = theta_array
        
#print(deflections)

#print(deflections.shape)

axis[2].set_title('Force Model - Wrist C')
axis[2].set_xlabel('Force')
axis[2].set_ylabel('Deflection')


colors = ['orange', 'green', 'blue', 'red']

deflections = deflections.transpose()

#print(deflections)



for k in range(0, len(deflections)):
    axis[2].plot(forces, deflections[k]*(180/math.pi), color=colors[k])
    
plt.show()
 

