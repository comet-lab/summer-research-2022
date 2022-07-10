import PySimpleGUI as sg
import theta_solver as ts
import numpy as np
import matplotlib.pyplot as plt

def is_int(string):
    try:
        number = int(string)
    except ValueError:
        return False
    return True

def is_float(dict1):
        for value in dict1.values():
            try:
                number = float(value)
            except ValueError:
                return False
        return True

def valid(num):
    num = int(num)
    if num <=0 or num>8:
        return False
    else:
        return True

def check_parameters(dict1):
    dict2 = dict1.copy()
    for key in dict2.keys():
        if key == 'mu':
            dict2[key] = float(dict2[key])
            if dict2[key] <0:
                return False
        elif key == 'r_outer':
            dict2[key] = float(dict2[key])
            dict2['r_inner'] = float(dict2['r_inner'])
            if dict2[key] < dict2['r_inner'] or dict2[key]<=0:
                return False

        elif key == 'E_linear':
           dict2[key] = float(dict2[key])
           dict2['E_super'] = float(dict2['E_super'])
           if dict2[key] < dict2['E_super'] or dict2[key]<=0:
               return False
            
        else:
            dict2[key] = float(dict2[key])
            if dict2[key] <= 0:
                return False
    return True

def valid_hs(dict1):
    dict2 = dict1.copy()
    for key in dict2.keys():
        dict2[key] = float(dict2[key])
        if dict2[key] <= 0:
            return False
    return True

def valid_gs(dict1, r_outer):
    dict2 = dict1.copy()
    for key in dict2.keys():
        dict2[key] = float(dict2[key])
        if dict2[key] <= 0 or 2*float(r_outer) < dict2[key]:
            return False
    return True


font = ('Courier New', 15)
sg.theme('DarkBlue4')
sg.set_options(font=font)



layout = [[sg.Text("How many notches")],
       [sg.Input(key='n', do_not_clear = False)],
       [sg.Text(size=(80,1), key='-OUTPUT-')],
       [sg.Button('OK')]]


window1 = sg.Window('number of notches', layout, finalize = True)
window1.BringToFront()
valid_n = False
positive_n = False

while True:
    (event, values1) = window1.read()
    if event == "OK":
        while not valid_n or not positive_n:
            if is_int(values1['n']) and valid(values1['n']):
                n = int(values1['n'])
                valid_n = True
                positive_n = True

            elif is_int(values1['n']) and not valid(values1['n']):
                window1['-OUTPUT-'].update("please make sure the value is greater than 0 and equal to or less than 8")
                (event, values1) = window1.read()
                positive_n = False                

            elif not is_int(values1['n']):
                window1['-OUTPUT-'].update("please make sure the value is an integer")
                (event, values1) = window1.read()
                valid_n = False
        break
        
   
    
window1.close()


font = ('Courier New', 15)
sg.theme('BluePurple')
sg.set_options(font=font)


layout4 = [ [sg.Text('Outer radius of the wrist (mm):'), sg.Input(key = 'r_outer')],
            [sg.Text('Inner radius of the wrist (mm):'), sg.Input(key = 'r_inner')],
            [sg.Text('Maximum force (Newtons):'), sg.Input(key = 'max_force')],
            [sg.Text('Coefficient of friction (mu):'), sg.Input(key = 'mu')],
            [sg.Text("Linear Young's Modulus (GPa):"), sg.Input(key = 'E_linear')],
            [sg.Text('Strain where superelastic region starts:'), sg.Input(key = 'epsilon_low')],
            [sg.Text('Slope of the stress-strain curve in the superelastic region (GPa) :'), sg.Input(key = 'E_super')],
            [sg.Text(size=(90,3), key='-OUTPUT-')],
            [sg.Button('OK')]
                  ]

window4 = sg.Window('other parameters', layout4, finalize = True, element_justification='r')
window4.BringToFront()

valid_answer = False
valid_parameters = False
while True:
    event, values4 = window4.read()
    if event == 'OK':
        while not valid_answer or not valid_parameters:
            if is_float(values4) and check_parameters(values4):
                valid_answer = True
                valid_parameters = True               
            
            elif not is_float(values4):
                window4['-OUTPUT-'].update("Please make sure that all answers are floats.")
                (event, values4) = window4.read()
                valid_answer = False

            elif is_float(values4) and not check_parameters(values4):
                window4['-OUTPUT-'].update("Please check the values. All values should be greater than 0 except for the coefficient of friction which can equal 0. outer radius > inner radius. Linear Young's Modulus > the slope of the stress-strain curve in the superelastic region")
                (event, values4) = window4.read()
                valid_parameters = False
            
        break     

window4.close()

r_outer_mm = values4['r_outer']
r_outer = float(values4['r_outer'])/1000.0

r_inner_mm = values4['r_inner']
r_inner = float(values4['r_inner'])/1000.0

max_force = float(values4['max_force'])

mu = float(values4['mu'])

E_linear_gpa = values4['E_linear']
E_linear = float(values4['E_linear']) *1e+9

epsilon_low = float(values4['epsilon_low'])

E_super_gpa = values4['E_super']
E_super = float(values4['E_super']) *1e+9


g_layout_list = []

for num in range(0, n):
    g_layout = [sg.Push(), sg.Text("Notch {}".format(num+1)), sg.Input(key = "g{}".format(num))]
    g_layout_list.append(g_layout)


font = ('Courier New', 15)
sg.theme('BluePurple')
sg.set_options(font=font)

layout2 = [
    [sg.Text("Depth of cut for each notch (mm):")],
    [g_layout_list],
    [sg.Text(size=(80,3), key='-OUTPUT-')],
    [sg.Button('OK')]
    ]

window2 = sg.Window('Depth of notches', layout2, finalize = True)
window2.BringToFront()

valid_g = False
positive_g = False

while True:
    event, values2 = window2.read()
    if event == "OK":
        while not valid_g or not positive_g:
            if is_float(values2) and valid_gs(values2, r_outer_mm):
                valid_g = True
                positive_g = True
            elif is_float(values2) and not valid_gs(values2, r_outer_mm):
                window2['-OUTPUT-'].update("Please check the values. All values must be greater than 0. 2*outer radius must be greater than the depth of the notch.")
                (event, values2) = window2.read()
                positive_g = False   
            elif not is_float(values2):
                window2['-OUTPUT-'].update("Please make sure that all answers are floats.")
                (event, values2) = window2.read()
                valid_g = False      
        break


window2.close()
   
g_array = np.zeros(n)
g_array_mm = np.zeros(n)

for item in values2.items():
    g = item[0]
    index = int(g[1])
    g_array[index] = float(item[1])/1000.0
    g_array_mm[index] = float(item[1])



h_layout_list = []
for num2 in range(0, n):
    h_layout = [sg.Push(), sg.Text("Notch {}".format(num2+1)), sg.Input(key = "g{}".format(num2))]
    h_layout_list.append(h_layout)
                 

font = ('Courier New', 15)
sg.theme('BluePurple')
sg.set_options(font=font)



layout3 = [
    [sg.Text("height of each notch(mm):")],
    [h_layout_list],
    [sg.Text(size=(60,1), key='-OUTPUT-')],
    [sg.Button('OK')]
    ]

window3 = sg.Window('Height of notches', layout3, finalize = True)
window3.BringToFront()

valid_h = False
positive_h = False

while True:
    event, values3 = window3.read()
    if event == "OK":
        while not valid_h and not positive_h:
            if is_float(values3) and valid_hs(values3):
                valid_h = True
                positive_h = True

            elif is_float(values3) and not valid_hs(values3):
                window3['-OUTPUT-'].update("Please make sure that all values are greater than 0.")
                (event, values3) = window3.read()
                positive_h = False 
                
            elif not is_float(values3):
                window3['-OUTPUT-'].update("Please make sure that all answers are floats.")
                (event, values3) = window3.read()
                valid_h = False      
        break


window3.close()

   
h_array = np.zeros(n)
h_array_mm = np.zeros(n)

for item in values3.items():
    h = item[0]
    index = int(h[1])
    h_array[index] = float(item[1])/1000.0
    h_array_mm[index] = float(item[1])
    
#print(h_array)


depth_of_notches = []

for num in range(0, n):
    depth_of_notches.append([sg.Text('Depth of cut of notch {}: {}'.format(num, g_array_mm[num]))])
    
height_of_notches = []

for num in range(0, n):
    height_of_notches.append([sg.Text('height of notch {}: {}'.format(num, h_array_mm[num]))])    
    

number_of_notches_text =  [sg.Text('Number of notches: {}'.format(n))]   
outer_radius_text = [sg.Text('outer radius of the wrist: {}'.format(r_outer_mm))]
inner_radius_text = [sg.Text('inner radius of the wrist: {}'.format(r_inner_mm))]
mu_text = [sg.Text('coefficient of friction: {}'.format(mu)) ]
maximum_force_text = [sg.Text('maximum force in the plot: {}'.format(max_force)) ]


col1 = sg.Column([
    # Notches sg.Frame
    [sg.Frame('',[ number_of_notches_text ] ) ],
    # Depth of Notches sg.Frame
        [sg.Frame('',   depth_of_notches )],
        [sg.Frame('', [outer_radius_text, inner_radius_text])],
        [sg.Frame('', [ mu_text] )],
        [sg.Frame('', [  maximum_force_text ])]
    
                ])



E_linear_text =  [sg.Text("linear Young's Modulus: {}".format(E_linear_gpa))]
E_super_text = [sg.Text("slope of the stress-strain curve in the superelastic region: {}".format(E_super_gpa))]
epsilon_low_text = [sg.Text("Strain where the superelastic region starts: {}".format(epsilon_low))]

col2 = sg.Column([
        # Height of Notches sg.Frame
        [sg.Frame('',  height_of_notches )],
        [sg.Frame('',[ E_linear_text, E_super_text, epsilon_low_text])]
                ])
                 
font = ('Courier New', 15)
sg.theme('BluePurple')
sg.set_options(font=font)
    



layout_summary = [[col1, col2], [sg.Button("plot force model")]]

window5 = sg.Window('Summary and Graph', layout_summary, finalize = True)
window5.BringToFront()

while True:
    event, values = window5.read()
    if event == sg.WIN_CLOSED:
        break
    elif event == 'plot force model':
        ts.graph_force_model(n, max_force, r_outer, r_inner, g_array, h_array, mu, E_linear, E_super, epsilon_low)
    
window5.close()

