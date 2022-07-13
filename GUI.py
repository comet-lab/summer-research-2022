import PySimpleGUI as sg
import theta_solver as ts
import numpy as np
import matplotlib as mpl
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
mpl.use('TkAgg')

max_n = 8
background_clr = '#4a4ca3'
theme = 'DarkBlue4'
font_name = 'Courier New'

def is_int(string):
    try:
        number = int(string)
    except ValueError:
        return False
    return True

def valid_n(n, max_n):
    n = int(n)
    if n <=0 or n>max_n:
        return False
    else:
        return True

def keys_to_check(n):
    list_of_keys = ['r_inner','r_outer', 'epsilon_low', 'E_super', 'E_linear', 'mu', 'max_force']
    for num in range(0, n):
        list_of_keys.append('g{}'.format(num+1))
        list_of_keys.append('h{}'.format(num+1))
    return list_of_keys

def is_float2(dict1, window, n):
    list_of_keys = keys_to_check(n)
    for key in list_of_keys:
        try:
            number = float(dict1[key])
        except ValueError:
            window['-OUTPUT2-'].update("{} is not a float".format(key), visible = True)
            return False
    return True

def check_parameters(dict1, window, n):
    dict2 = dict1.copy()
    list_of_keys = keys_to_check(n)
        
    r_outer= float(dict2['r_outer'])
    r_inner = float(dict2['r_inner'])
    if r_inner <= 0:
        window['-OUTPUT2-'].update("Inner radius must be greater than 0.", visible = True)
        return False
    
    elif r_outer < r_inner or r_outer <=0:
        window['-OUTPUT2-'].update("Outer radius must be greater than 0 and greater than the inner radius.", visible = True)
        return False
    
    else:
        for key in list_of_keys:
            if key == 'mu':
                dict2[key] = float(dict2[key])
                if dict2[key] <0:
                    window['-OUTPUT2-'].update("coefficient of friction must be equal to or greater than 0.", visible = True)
                    return False

            elif key == 'E_linear':
               E_linear = float(dict2[key])
               E_super = float(dict2['E_super'])
               if E_super <= 0:
                  window['-OUTPUT2-'].update("The slope of the stress-strain curve in the superelastic region must be greater than 0.", visible = True)
                  return False
                
               elif E_linear < E_super or E_linear<=0:
                   window['-OUTPUT2-'].update("Linear Young's Modulus must be greater than the slope of the stress-strain curve in the superelastic region, and Linear Young's Modulus must be greater than 0.", visible = True)
                   return False
            
            elif key.startswith('g'):
                dict2[key] = float(dict2[key])
                if not valid_g(dict2[key], dict2['r_outer']) or dict2[key]<=0:
                    window['-OUTPUT2-'].update("2*outer radius must be greater than the depth of the notch. Depths of notches must be greater than zero.", visible = True)
                    return False

            elif key.startswith('h'):
                dict2[key] = float(dict2[key])
                if not valid_h(dict2[key]) or dict2[key]<=0:
                    window['-OUTPUT2-'].update("Heights of the notches must be greater than zero.", visible = True)
                    return False
            
            elif key == 'epsilon_low':
                 epsilon_low = float(dict2[key])
                 if epsilon_low <=0:
                    window['-OUTPUT2-'].update("Strain where the superelastic region starts must be greater than 0", visible = True)
                    return False

            elif key == 'max_force':
                 max_force = float(dict2[key])
                 if max_force <=0:
                    window['-OUTPUT2-'].update("Maximum force must be greater than 0", visible = True)
                    return False

    return True



def valid_h(h):
    h = float(h)
    if h <= 0:
        return False
    return True

def valid_g(g, r_outer):
    g = float(g)
    if g <= 0 or 2*float(r_outer) < g:
        return False
    return True

def make_visible(n, g_list, h_list):
    for num in range(0, n):
        g_layout = g_list[num]
        text1 = g_layout[1]
        text1.update(visible = True)
        input1 = g_layout[2]
        input1.update(visible = True)
        
        h_layout = h_list[num]
        text2 = h_layout[1]
        text2.update(visible = True)
        input2 = h_layout[2]
        input2.update(visible = True)
        
def make_invisible(max_n, g_list, h_list):
     for num in range(0, max_n):
        g_layout = g_list[num]
        text1 = g_layout[1]
        text1.update(visible = False)
        input1 = g_layout[2]
        input1.update(visible = False)
        
        h_layout = h_list[num]
        text2 = h_layout[1]
        text2.update(visible = False)
        input2 = h_layout[2]
        input2.update(visible = False)
          
def create_g_array(n, dict1):
    g_array = np.zeros(n)

    list_of_keys = []
    for key in dict1.keys():
        list_of_keys.append(str(key))
    
    for key in list_of_keys:
        if key.startswith('g') and dict1[key] != '':
            g = dict1[key]
            index = int(key[1])-1
            g_array[index] = float(g)/1000.0
            
    return g_array
            
def create_h_array(n, dict1):
    h_array = np.zeros(n)

    list_of_keys = []
    for key in dict1.keys():
        list_of_keys.append(str(key))
    
    for key in list_of_keys:
        if key.startswith('h') and dict1[key] != '':
            h = dict1[key]
            index = int(key[1])-1
            h_array[index] = float(h)/1000.0
            
    return h_array
    
    
def create_final_dict(n, dict1):
    dict2 = dict1.copy()
    final_parameters = dict()
    final_parameters['r_inner'] = float(dict2['r_inner'])/1000.0
    final_parameters['r_outer'] = float(dict2['r_outer'])/1000.0
    final_parameters['n'] = n
    final_parameters['max_force'] = float(dict2['max_force'])
    final_parameters['epsilon_low'] = float(dict2['epsilon_low'])
    final_parameters['mu'] = float(dict2['mu'])
    final_parameters['E_linear'] = float(dict2['E_linear']) *1e+9
    final_parameters['E_super'] = float(dict2['E_super']) *1e+9
    return final_parameters
    
def draw_figure(canvas, figure):
    figure_canvas_agg = FigureCanvasTkAgg(figure, canvas)
    figure_canvas_agg.draw()
    figure_canvas_agg.get_tk_widget().pack(side='top', fill='both', expand=1)
    return figure_canvas_agg

def unpack_canvas(canvas):    
    canvas.get_tk_widget().pack_forget()
                     

def erase_graph(canvas):
    for item in canvas.get_tk_widget().find_all():
       canvas.get_tk_widget().delete(item)

#n = 4
#g_layout_list = []

#for num in range(0, n):
#   g_layout = [sg.Push(), sg.Text("Notch {}".format(num+1)), sg.Input(key = "g{}".format(num))]
#  g_layout_list.append(g_layout)


#h_layout_list = []
#for num2 in range(0, n):
#    h_layout = [sg.Push(), sg.Text("Notch {}".format(num2+1)), sg.Input(key = "g{}".format(num2))]
#    h_layout_list.append(h_layout)
    


font = (font_name, 15)
sg.theme(theme)
sg.set_options(font=font)


g_layout_list = []
for num in range(0, max_n):
    g_layout = [sg.Push(), sg.Text("Notch {}".format(num+1), background_color = background_clr, key='g{}_text'.format(num+1), visible=False), sg.Input(key = "g{}".format(num+1), visible=False)]
    g_layout_list.append(g_layout)


h_layout_list = []
for num in range(0, max_n):
    h_layout = [sg.Push(), sg.Text("Notch {}".format(num+1), background_color = background_clr, key='h{}_text'.format(num+1), visible=False), sg.Input(key = "h{}".format(num+1), visible=False)]
    h_layout_list.append(h_layout)


    



#define layout

layout1 = [[sg.Text("How many notches", background_color = background_clr)],
           [sg.Input(key='n', do_not_clear = True, enable_events=True)],
           [sg.Text(size=(100,1), background_color = background_clr, key='-OUTPUT1-', visible = False)],
           [sg.Text('Outer radius of the wrist (mm):', background_color = background_clr), sg.Input(key = 'r_outer')],
           [sg.Text('Inner radius of the wrist (mm):', background_color = background_clr), sg.Input(key = 'r_inner')],
           [sg.Text("Depth of cut for each notch (mm):", background_color = background_clr)],
           *g_layout_list,            
           [sg.Text("height of each notch(mm):", background_color = background_clr)],
           *h_layout_list
           ]

layout2 = [
    [sg.Text('Coefficient of friction (mu):', background_color = background_clr), sg.Input(key = 'mu')],
    [sg.Text("Linear Young's Modulus (GPa):", background_color = background_clr), sg.Input(key = 'E_linear')],
    [sg.Text('Strain where superelastic region starts:', background_color = background_clr), sg.Input(key = 'epsilon_low')],
    [sg.Text('Slope of the stress-strain curve in the superelastic region (GPa) :', background_color = background_clr), sg.Input(key = 'E_super')]
    ]

layout3 = [[sg.Text('Maximum force (Newtons):', background_color = background_clr), sg.Input(key = 'max_force')],
           [sg.Button("plot force model")],
           [sg.Text(size=(100,3), key='-OUTPUT2-', visible=False)],
           [sg.Text(size=(90,2), key='-OUTPUT3-', visible=False)],
           [sg.Canvas(key='-CANVAS-')]]


#Define Layout with Tabs         


tabgrp = [[sg.TabGroup([[sg.Tab('Wrist Dimensions', layout1, title_color='White',border_width =10, background_color = background_clr, element_justification= 'center'),
                         
                    sg.Tab('Material Properties', layout2,title_color='White',background_color=background_clr, element_justification= 'right'),
                         
                    sg.Tab('Graphs', layout3,title_color='White',background_color= background_clr, element_justification= 'center')]],

                       tab_location='centertop',
                       title_color='Yellow', tab_background_color='Purple',selected_title_color='White', selected_background_color=background_clr ,
                       border_width=5), sg.Button('Close')]]  
        







window = sg.Window("Force Model",tabgrp)
n = 0
fig_canvas_agg = None

while True:
    event, values = window.read()
    if event == sg.WIN_CLOSED:
        break
    if event == 'Close':
        break
    
    if values['n']:
        window['-OUTPUT1-'].update(visible = False)
        if not is_int(values['n']):
            window['-OUTPUT1-'].update("please make sure the number of notches is an integer", visible = True)
        elif not valid_n(values['n'], max_n):
            window['-OUTPUT1-'].update("please make sure the number of notches is greater than 0 and smaller than {}".format(max_n+1), visible = True)
                    
        else:
            n = int(values['n'])
            make_invisible(max_n, g_layout_list, h_layout_list)
            make_visible(n, g_layout_list, h_layout_list)

    if event == "plot force model":
        window['-OUTPUT2-'].update(visible = False)
        dict_of_parameters = values.copy()
        if not is_float2(dict_of_parameters, window, n):
            window['-OUTPUT3-'].update("Please find and correct the values that are not floats.", visible=True)
        elif not check_parameters(dict_of_parameters, window, n):
            window['-OUTPUT3-'].update("Please find and correct the values.", visible=True)
        else:
            window['-OUTPUT2-'].update(visible = False)
            window['-OUTPUT3-'].update("All values you entered are acceptable. Please wait a moment for the graph to load.", visible=True)
            window.refresh()
            g_array = create_g_array(n, dict_of_parameters)
            h_array = create_h_array(n, dict_of_parameters)
            final_dict = create_final_dict(n, dict_of_parameters)

            if fig_canvas_agg is not None:
                unpack_canvas(fig_canvas_agg)
                
            fig = ts.graph_force_model(final_dict['n'], final_dict['max_force'], final_dict['r_outer'], final_dict['r_inner'], g_array, h_array, final_dict['mu'], final_dict['E_linear'], final_dict['E_super'], final_dict['epsilon_low'])
            fig_canvas_agg = draw_figure(window['-CANVAS-'].TKCanvas, fig)
            window.refresh()
            
            
        
        
        
        
window.close() 
