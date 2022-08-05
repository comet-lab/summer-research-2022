import PySimpleGUI as sg
import theta_solver as ts
import wrist_shape as ws
import Three_D_Wrist as td
import numpy as np
import matplotlib as mpl

mpl.use('TkAgg')
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt
import math


max_n = 8
background_clr = '#4a4ca3'
theme = 'DarkBlue4'
font_name = 'Courier New'


#####################################################################

#functions used multiple times:
       
def make_invisible(max_n, g_list, h_list, c_list, values):
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

        c_layout = c_list[num]
        text3 = c_layout[1]
        text3.update(visible = False)
        input3 = c_layout[2]
        input3.update(visible = False)

def make_visible(n, g_list, h_list, c_list):
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

        c_layout = c_list[num]
        text3 = c_layout[1]
        text3.update(visible = True)
        input3 = c_layout[2]
        input3.update(visible = True)

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
    list_of_keys = ['r_inner','r_outer', 'epsilon_low', 'E_super', 'E_linear', 'mu']
    for num in range(0, n):
        list_of_keys.append('g{}'.format(num+1))
        list_of_keys.append('h{}'.format(num+1))
        list_of_keys.append('c{}'.format(num+1))
    return list_of_keys


def is_float(dict1, window, n, output):
    list_of_keys = keys_to_check(n)
    for key in list_of_keys:
        try:
            number = float(dict1[key])
        except ValueError:
            window[output].update("{}:{} is not a float".format(key, dict1[key]), visible = True)
            return False
    return True

#####################################################################        
# code for if values['n']

def process_n(window, values, max_n, g_layout_list, h_layout_list, c_layout_list):
    n = int(values['n'])
    make_invisible(max_n, g_layout_list, h_layout_list, c_layout_list, values)
    window.refresh()
    window['tab1_column'].contents_changed()
    make_visible(n, g_layout_list, h_layout_list, c_layout_list)
    window.refresh()
    window['tab1_column'].contents_changed()

#####################################################################
    
# code for event == "-INg-", "-INh-", OR "-INc-"

def populate_same_values(x, values, window):
    if values['{}1'.format(x)]:
        value_to_copy = values['{}1'.format(x)]
        for index in range(1, int(values['n'])):
            values['{}{}'.format(x, index+1)] = value_to_copy
            window['{}{}'.format(x, index+1)].update(value=value_to_copy)
            window.refresh()

#####################################################################

# code 1 for event == "Plot graphs"


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

def valid_c(c):
    c = float(c)
    if c<= 0:
        return False
    return True


def check_parameters(dict1, window, n, output):
    dict2 = dict1.copy()
    list_of_keys = keys_to_check(n)

    
    r_outer = float(dict2['r_outer'])
    r_inner = float(dict2['r_inner'])
    if r_inner <= 0:
        window[output].update("Inner radius must be greater than 0.", visible = True)
        return False
    
    elif r_outer < r_inner or r_outer <=0:
        window[output].update("Outer radius must be greater than 0 and greater than the inner radius.", visible = True)
        return False
    
    else:
        for key in list_of_keys:
            if key == 'mu':
                dict2[key] = float(dict2[key])
                if dict2[key] <0:
                    window[output].update("coefficient of friction must be equal to or greater than 0.", visible = True)
                    return False

            elif key == 'E_linear':
               E_linear = float(dict2[key])
               E_super = float(dict2['E_super'])
               if E_super <= 0:
                  window[output].update("The slope of the stress-strain curve in the superelastic region must be greater than 0.", visible = True)
                  return False
                
               elif E_linear < E_super or E_linear<=0:
                   window[output].update("Linear Young's Modulus must be greater than the slope of the stress-strain curve in the superelastic region, and Linear Young's Modulus must be greater than 0.", visible = True)
                   return False
            
            elif key.startswith('g'):
                dict2[key] = float(dict2[key])
                if not valid_g(dict2[key], dict2['r_outer']) or dict2[key]<=0:
                    window[output].update("2*outer radius must be greater than the depth of the notch. Depths of notches must be greater than zero.", visible = True)
                    return False

            elif key.startswith('h'):
                dict2[key] = float(dict2[key])
                if not valid_h(dict2[key]) or dict2[key]<=0:
                    window[output].update("Heights of the notches must be greater than zero.", visible = True)
                    return False

            elif key.startswith('c'):
                dict2[key] = float(dict2[key])
                if not valid_c(dict2[key]) or dict2[key]<0:
                    window[output].update("Lengths of the uncut sections must be greater than zero.", visible = True)
                    return False
            
            elif key == 'epsilon_low':
                 epsilon_low = float(dict2[key])
                 if epsilon_low <=0:
                    window[output].update("Strain where the superelastic region starts must be greater than 0", visible = True)
                    return False
    return True


def valid_force(force):
    try:
        force = float(force)
    except ValueError:
         return False
    if force <=0:
        return False
    return True


#####################################################################

# code 2 for event == "Plot graphs"

def create_g_array(n, dict1):
    g_array = np.zeros(n)

    list_of_keys = []
    for key in dict1.keys():
        list_of_keys.append(str(key))

    correct_gs = ['g{}'.format(i+1) for i in range(0,n)]
    
    for key in list_of_keys:
        if key in correct_gs:
            g = dict1[key]
            index = int(key[1])-1
            g_array[index] = float(g)/1000.0
            
    return g_array
            
def create_h_array(n, dict1):
    h_array = np.zeros(n)

    list_of_keys = []
    for key in dict1.keys():
        list_of_keys.append(str(key))

    correct_hs = ['h{}'.format(i+1) for i in range(0,n)]
    
    for key in list_of_keys:
        if key in correct_hs:
            h = dict1[key]
            index = int(key[1])-1
            h_array[index] = float(h)/1000.0
            
    return h_array

def create_c_array(n, dict1):
    c_array = np.zeros(n)

    list_of_keys = []
    for key in dict1.keys():
        list_of_keys.append(str(key))
        
    correct_cs = ['c{}'.format(i+1) for i in range(0,n)]
    
    for key in list_of_keys:
        if key in correct_cs:
            c = dict1[key]
            index = int(key[1])-1
            c_array[index] = float(c)/1000.0
            
    return c_array
    
def create_final_dict(n, dict1, plot_type):
    dict2 = dict1.copy()
    final_parameters = dict()
    final_parameters['r_inner'] = float(dict2['r_inner'])/1000.0
    final_parameters['r_outer'] = float(dict2['r_outer'])/1000.0
    final_parameters['n'] = n
    final_parameters['epsilon_low'] = float(dict2['epsilon_low'])
    final_parameters['mu'] = float(dict2['mu'])
    final_parameters['E_linear'] = float(dict2['E_linear']) *1e+9
    final_parameters['E_super'] = float(dict2['E_super']) *1e+9
    if plot_type == '2d':
        final_parameters['max_force'] = float(dict2['max_force'])
    elif plot_type == '3d':
        final_parameters['force_3d'] = float(dict2['force_3d'])
    return final_parameters


def draw_figure_w_toolbar(canvas, fig, canvas_toolbar):
    if canvas.children:
        for child in canvas.winfo_children():
            child.destroy()
    if canvas_toolbar.children:
        for child in canvas_toolbar.winfo_children():
            child.destroy()
    figure_canvas_agg = FigureCanvasTkAgg(fig, master=canvas)
    figure_canvas_agg.draw()
    toolbar = Toolbar(figure_canvas_agg, canvas_toolbar)
    toolbar.update()
    figure_canvas_agg.get_tk_widget().pack(side='right', fill='both', expand=1)


class Toolbar(NavigationToolbar2Tk):
    def __init__(self, *args, **kwargs):
        super(Toolbar, self).__init__(*args, **kwargs)

def plot_graphs(window, n, dict_of_parameters):
    window['-OUTPUT2-'].update(visible = False)
    window['-OUTPUT3-'].update("All values you entered are acceptable. Please wait a moment for the graphs to load.", visible=True)
    window.refresh()
    g_array = create_g_array(n, dict_of_parameters)
    h_array = create_h_array(n, dict_of_parameters)
    c_array = create_c_array(n, dict_of_parameters)
    final_dict = create_final_dict(n, dict_of_parameters, '2d')        
            
    (forces, deflections, kappas) = ts.find_forces_thetas_kappas(final_dict['n'], final_dict['max_force'], final_dict['r_outer'], final_dict['r_inner'], g_array, h_array,
                                                                 final_dict['mu'], final_dict['E_linear'], final_dict['E_super'], final_dict['epsilon_low'])
    fig1 = ts.graph_force_model(forces, deflections, final_dict['n'], 1)
        
    draw_figure_w_toolbar(window['-CANVAS1-'].TKCanvas, fig1, window['toolbar_canvas_1'].TKCanvas)
    
    window.refresh()
    window['tab3_column'].contents_changed()

    new_forces, x_array, z_array = ws.find_x_and_z_coordinates(forces, c_array, n, kappas, deflections)
    fig2 = ws.graph_wrist_shape(new_forces, x_array, z_array, 2)

    draw_figure_w_toolbar(window['-CANVAS2-'].TKCanvas, fig2, window['toolbar_canvas_2'].TKCanvas)

    window['fig1_save'].update(visible = True)
    window['fig2_save'].update(visible = True)
    
    window.refresh()
    window['tab3_column'].contents_changed()
    return fig1, fig2
    
#####################################################################

# code for event == "plot 3d graph"



def draw_3d_figure(canvas, figure):
    figure_canvas_agg = FigureCanvasTkAgg(figure, canvas)
    figure_canvas_agg.draw()
    figure_canvas_agg.get_tk_widget().pack(side='top', fill='both', expand=1)
    return figure_canvas_agg

def delete_3d_figure_agg(figure_agg):
    figure_agg.get_tk_widget().forget()
    plt.close('all')


def plot_3d(window, n, dict_of_parameters):
    window['-OUTPUT4-'].update(visible = False)
    window['-OUTPUT5-'].update("All values you entered are acceptable. Please wait a moment for the graph to load.", visible=True)
    window.refresh()
    g_array = create_g_array(n, dict_of_parameters)
    h_array = create_h_array(n, dict_of_parameters)
    c_array = create_c_array(n, dict_of_parameters)
    final_dict = create_final_dict(n, dict_of_parameters, '3d')
    force, deflections, final_kappas = ts.find_thetas_kappas_for_one_force(final_dict['n'], final_dict['force_3d'], final_dict['r_outer'], final_dict['r_inner'], g_array,
                                                                               h_array, final_dict['mu'], final_dict['E_linear'], final_dict['E_super'], final_dict['epsilon_low'])
    force, x_array, z_array = ws.find_x_and_z_coordinates_for_one_force(final_dict['force_3d'], c_array, final_dict['n'], final_kappas, deflections)

    r_mm = final_dict['r_outer']*1000.0
    fig3d = td.plot_cylinders(r_mm, x_array, z_array, final_dict['n'], 3)
    figure_agg_3d = draw_3d_figure(window['-CANVAS3-'].TKCanvas, fig3d)
               
    window.refresh()
    window['tab4_column'].contents_changed()

    return fig3d, figure_agg_3d


#####################################################################
#code for event == "Save Values"

def create_list_of_strings(dict1):
    value_list = []
    dict1 = dict1.copy()
    n = dict1['n']
    correct_gs = ['g{}'.format(i+1) for i in range(0,int(n))]
    correct_hs = ['h{}'.format(i+1) for i in range(0,int(n))]
    correct_cs = ['c{}'.format(i+1) for i in range(0,int(n))]

    n_entry = "Notches:{}\n".format(dict1['n'])
    value_list.append(n_entry)
    
    depths = "Depths: " + "[" + ", ".join(["{}".format(dict1[g_key]) for g_key in correct_gs]) + "]" + "\n"
    value_list.append(depths)
    heights = "Heights: " + "[" + ", ".join(["{}".format(dict1[h_key]) for h_key in correct_hs]) + "]" + "\n"
    value_list.append(heights)
    uncut = "Uncut: " + "[" + ", ".join(["{}".format(dict1[c_key]) for c_key in correct_cs]) + "]" + "\n"
    value_list.append(uncut)
    
    
    key_names = ['Outer_Radius', 'Inner_Radius', 'Coefficient_Friction', "Linear_Young's_Modulus", 'Superelastic_Modulus', 'Strain_Lower']
    list_of_keys = ['r_outer','r_inner', 'mu', 'E_linear', 'E_super', 'epsilon_low']
                                         
    for index in range(0, len(key_names)):
        entry = "{}: {}\n".format(key_names[index], dict1[list_of_keys[index]])
        value_list.append(entry)
    
    return value_list 


def export_values(dict1, file_path):
    value_list = create_list_of_strings(dict1)
    try:
        with open(file_path, "w") as file1:
            file1.writelines(["# lengths are in units of mm \n", "# Young's modulus is in units of GPa \n"])
            file1.writelines(value_list)
        return True
            
    except (IOError, OSError) as error:
        sg.popup("Problem saving file. Error is {}".format(error))
        return False

#####################################################################
# code 1 for event == 'Load Values'

def remove_figure_with_toolbar(canvas, canvas_toolbar):
    if canvas.children:
        for child in canvas.winfo_children():
            child.destroy()
    if canvas_toolbar.children:
        for child in canvas_toolbar.winfo_children():
            child.destroy()

def clear_values(dict1, n, window):
    keys = keys_to_check(n)
    window['n'].update(value=0)
    for key in keys:
        window[key].update(value='')
        dict1[key] = ''

def update_window_before_loading_values(window, values, n, max_n, g_layout_list, h_layout_list, c_layout_list):
     
    remove_figure_with_toolbar(window['-CANVAS1-'].TKCanvas, window['toolbar_canvas_1'].TKCanvas)
    remove_figure_with_toolbar(window['-CANVAS2-'].TKCanvas, window['toolbar_canvas_2'].TKCanvas)
       
    clear_values(values, n, window)
    make_invisible(max_n, g_layout_list, h_layout_list, c_layout_list, values)
    window['n'].update(value='')
    values['n'] = ''
    window['-OUTPUT3-'].update(visible=False)
    window['fig1_save'].update(visible = False)
    window['fig2_save'].update(visible = False)    
    window.refresh()
    window['tab1_column'].contents_changed()
    window['tab3_column'].contents_changed()
    
#####################################################################

#code 2 for event == 'Load Values'


def create_phrase_dict():
    phrase_dict = dict()
    phrases = ['Notches', 'Outer_Radius', 'Inner_Radius', 'Coefficient_Friction', "Linear_Young's_Modulus", 'Superelastic_Modulus', 'Strain_Lower']
    keys = ['n', 'r_outer','r_inner', 'mu', 'E_linear', 'E_super', 'epsilon_low']
    for index in range(len(keys)):
        phrase_dict[phrases[index].upper()] = keys[index]
    return phrase_dict  

def all_possible_keys(max_n):
    list_of_keys = ['n', 'r_inner','r_outer', 'epsilon_low', 'E_super', 'E_linear', 'mu', 'max_force']
    for num in range(0, max_n):
        list_of_keys.append('g{}'.format(num+1))
        list_of_keys.append('h{}'.format(num+1))
        list_of_keys.append('c{}'.format(num+1))
    return list_of_keys


def import_values(max_n, filename):
    phrase_dict = create_phrase_dict()
    
    imported_values = dict()
    keys = all_possible_keys(max_n)
    for key in keys:
        imported_values[key] = ''

    try:   
        with open(filename, "r") as file1:
            lines = file1.readlines()

            for line in lines:
                if line.startswith('#'):
                    continue
            
                else:
                    split_line = line.split(':')
                    phrase = split_line[0]
                    if phrase.upper() == 'DEPTHS':
                        depths1 = split_line[1]
                        depths1 = depths1.strip(' []\n')
                        depths = depths1.split(',')
                        for index in range(0, len(depths)):
                            imported_values['g{}'.format(index+1)] = depths[index].strip()
                
                    elif phrase.upper() == 'HEIGHTS':
                        heights1 = split_line[1]
                        heights1 = heights1.strip(' []\n')
                        heights = heights1.split(',')
                
                        for index in range(0, len(heights)):
                            imported_values['h{}'.format(index+1)] = heights[index].strip()                    
                
                    elif phrase.upper() == 'UNCUT':
                        uncuts1 = split_line[1]
                        uncuts1 = uncuts1.strip(' []\n')
                        uncuts = uncuts1.split(',')
                        for index in range(0, len(uncuts)):
                            imported_values['c{}'.format(index+1)] = uncuts[index].strip()

                    else:
                        key_name = phrase_dict.get(phrase.upper())
                        if key_name is not None:
                            imported_values[key_name] = split_line[1].strip(' \n')
                        
        return True, imported_values
    
    except (IOError, OSError) as error:
        sg.popup("Problem reading file. Error is {}".format(error))
        return False, imported_values


def populate_inputs(imported_values, values, n, window):
    keys = keys_to_check(n)
    window['n'].update(value=imported_values['n'])
    values['n'] = imported_values['n']
    for key in keys:
        window[key].update(value=imported_values[key])
        values[key] = imported_values[key]
    

def load_all_values(max_n, g_layout_list, h_layout_list, c_layout_list, window):
    filename = ''
    filename = sg.popup_get_file('Load values from a text file', save_as = False, no_window=True, file_types=(('TXT', '.txt'),))
    if filename != '':
        import_return_code, imported_values = import_values(max_n, filename)
        if import_return_code:
            if not is_int(imported_values['n']):
                sg.popup("please make sure the number of notches is an integer")
            elif not valid_n(imported_values['n'], max_n):
                sg.popup("please make sure the number of notches is greater than 0 and smaller than {}".format(max_n+1))
            else:
                n = int(imported_values['n'])
                make_visible(n, g_layout_list, h_layout_list, c_layout_list)
                populate_inputs(imported_values, values, n, window)

                window.refresh()
                window['tab1_column'].contents_changed()
                window['tab3_column'].contents_changed()




#####################################################################

#define layout

font = (font_name, 15)
sg.theme(theme)
sg.set_options(font=font)
sg.set_options(dpi_awareness = True)
file_types=(('PNG', '.png'), ('JPG', '.jpg'), ('EPS', '.eps'), ('JPEG', '.jpeg'), ('PDF', '.pdf'), ('TIF', '.tif'), ('TIFF', '.tiff'))

g_layout_list = []
for num in range(0, max_n):
    g_layout = [sg.Push(), sg.Text("Notch {}".format(num+1), background_color = background_clr, key='g{}_text'.format(num+1), visible=False), sg.Input(key = "g{}".format(num+1), visible=False, do_not_clear = True)]
    g_layout_list.append(g_layout)


h_layout_list = []
for num in range(0, max_n):
    h_layout = [sg.Push(), sg.Text("Notch {}".format(num+1), background_color = background_clr, key='h{}_text'.format(num+1), visible=False), sg.Input(key = "h{}".format(num+1), visible=False, do_not_clear = True)]
    h_layout_list.append(h_layout)

c_layout_list = []
for num in range(0, max_n):
    c_layout = [sg.Push(), sg.Text("Uncut {}".format(num+1), background_color = background_clr, key='c{}_text'.format(num+1), visible=False), sg.Input(key = "c{}".format(num+1), visible=False, do_not_clear = True)]
    c_layout_list.append(c_layout)


menu_def = [['File', ['Load Values', 'Save Values', 'Exit']]]

# code for Wrist Dimenstions:
column1 = [[sg.Text("How many notches", background_color = background_clr)],
           [sg.Input(key='n', do_not_clear = True, enable_events=True)],
           [sg.Text(size=(100,1), background_color = background_clr, key='-OUTPUT1-', visible = False)],
           [sg.Text('Outer radius of the wrist (mm):', background_color = background_clr), sg.Input(key = 'r_outer')],
           [sg.Text('Inner radius of the wrist (mm):', background_color = background_clr), sg.Input(key = 'r_inner')],
           [sg.Text("Depth of cut for each notch (mm):", background_color = background_clr), sg.Button(button_text = 'fill in all notches as notch 1', key="-INg-", enable_events=True, size = (12, 3), font= (font_name, 11))],
           *g_layout_list,            
           [sg.Text("height of each notch(mm):", background_color = background_clr), sg.Button(button_text = 'fill in all notches as notch 1', key="-INh-", enable_events=True, size = (12, 3), font= (font_name, 11))],
           *h_layout_list,
           [sg.Text("length of each uncut section (mm):", background_color=background_clr), sg.Button(button_text = 'fill in all sections as section 1', key="-INc-", enable_events=True, size = (12, 3), font= (font_name, 11))],
           *c_layout_list
           ]

tab1 = [[sg.Column(column1, background_color=background_clr, vertical_scroll_only = True, scrollable = True, sbar_width = 35,
        sbar_background_color = "#FFFF8F", sbar_arrow_width = 35, sbar_arrow_color = "purple", size =(1500, 900), key='tab1_column')]]

# code for material properties:
tab2 = [
    [sg.Text('Coefficient of friction (mu):', background_color = background_clr), sg.Input(key = 'mu')],
    [sg.Text("Linear Young's Modulus (GPa):", background_color = background_clr), sg.Input(key = 'E_linear')],
    [sg.Text('Strain where superelastic region starts:', background_color = background_clr), sg.Input(key = 'epsilon_low')],
    [sg.Text('Slope of the stress-strain curve in the superelastic region (GPa) :', background_color = background_clr), sg.Input(key = 'E_super')]
    ]


# code for graphs:        
column2 = [
    [sg.Text('Maximum force (Newtons):', background_color = background_clr), sg.Input(key = 'max_force')],
    [sg.Button("Plot graphs")],
    [sg.InputText(visible=False, enable_events=True, key='fig1_path'), sg.FileSaveAs(button_text='Save Force Model', visible=False, key='fig1_save', file_types=file_types)],
    [sg.InputText(visible=False, enable_events=True, key='fig2_path'), sg.FileSaveAs(button_text='Save Wrist Shape', visible=False, key='fig2_save', file_types=file_types)],
    [sg.Text(size=(100,3), key='-OUTPUT2-', visible=False)],
    [sg.Text(size=(90,2), key='-OUTPUT3-', visible=False)],
    [sg.Canvas(key = 'toolbar_canvas_1')],
    [sg.Canvas(key='-CANVAS1-')],
    [sg.Canvas(key = 'toolbar_canvas_2')],
    [sg.Canvas(key='-CANVAS2-')]
    ]


tab3 = [[sg.Column(column2, background_color=background_clr, vertical_scroll_only = True, scrollable = True,
                   sbar_width = 35, sbar_background_color = "#FFFF8F", sbar_arrow_width = 35, sbar_arrow_color = "purple", size =(1500, 900), key='tab3_column')]]


column3 = [
    [sg.Text('Force (Newtons):', background_color = background_clr), sg.Input(key = 'force_3d')],
    [sg.Button("Plot 3d graph")],
    [sg.InputText(visible=False, enable_events=True, key='fig3d_path'), sg.FileSaveAs(button_text='Save 3d wrist', visible=False, key='fig3d_save', file_types=file_types)],
    [sg.Text(size=(100,3), key='-OUTPUT4-', visible=False)],
    [sg.Text(size=(100,3), key='-OUTPUT5-', visible=False)],
    [sg.Canvas(key = 'toolbar_canvas_3')],
    [sg.Canvas(key='-CANVAS3-')],
    ]

tab4 = [[sg.Column(column3, background_color=background_clr, vertical_scroll_only = True, scrollable = True,
                   sbar_width = 35, sbar_background_color = "#FFFF8F", sbar_arrow_width = 35, sbar_arrow_color = "purple", size =(1500, 900), key='tab4_column')]]


#Layout with tabs:         

final_layout = [ [sg.Menu(menu_def, tearoff=True)],
    [sg.TabGroup([[sg.Tab('Wrist Dimensions', tab1, title_color='White',border_width =10, background_color = background_clr, element_justification= 'center'),
                   sg.Tab('Material Properties', tab2, title_color='White',background_color=background_clr, element_justification= 'right'),
                   sg.Tab('Graphs', tab3, title_color='White',background_color= background_clr, element_justification= 'center'),
                   sg.Tab('3D Wrist Graph', tab4, title_color='White',background_color= background_clr, element_justification= 'center')]],
                  tab_location='centertop',
                    title_color='Yellow', tab_background_color='Purple',selected_title_color='White', selected_background_color=background_clr ,
                       border_width=5),sg.Button('Close')]]



######################################################################################################

#code for event loop:

window = sg.Window("Force Model", layout = final_layout, finalize = True)

n = 0

figure_agg_3d = None

while True:
    event, values = window.read()
    if event == sg.WIN_CLOSED:
        break
    if event == 'Close':
        break
    if event == 'Exit':
        break
    
    if values['n']:
        window['-OUTPUT1-'].update(visible = False)
        if not is_int(values['n']):
            window['-OUTPUT1-'].update("please make sure the number of notches is an integer", visible = True)
            window['tab1_column'].contents_changed()
        elif not valid_n(values['n'], max_n):
            window['-OUTPUT1-'].update("please make sure the number of notches is greater than 0 and smaller than {}".format(max_n+1), visible = True)
            window['tab1_column'].contents_changed()
        else:
            process_n(window, values, max_n, g_layout_list, h_layout_list, c_layout_list)
        

    if event == "-INg-":
        populate_same_values('g', values, window)
            
    if event == "-INh-":
        populate_same_values('h', values, window)
            
    if event == "-INc-":
        populate_same_values('c', values, window)        
        

    if event == "Plot graphs":
        window['-OUTPUT2-'].update(visible = False)
        dict_of_parameters = values.copy()
        n = int(values['n'])
        if not is_float(dict_of_parameters, window, n, '-OUTPUT2-'):
            window['-OUTPUT3-'].update("Please find and correct the values that are not floats.", visible=True)
        elif not check_parameters(dict_of_parameters, window, n, '-OUTPUT2-'):
            window['-OUTPUT3-'].update("Please find and correct the values.", visible=True)
        elif not valid_force(dict_of_parameters['max_force']):
             window['-OUTPUT2-'].update("maximum force should be a float greater than 0.", visible=True)
             window['-OUTPUT3-'].update("Please find and correct the values.", visible=True)
                  
        else:
            fig1, fig2 = plot_graphs(window, n, dict_of_parameters)
            
           

    if (event == 'fig1_path') and (values['fig1_path'] != ''):
        try:
            fig1.savefig(values['fig1_path'])
        except (IOError, OSError) as error:
            sg.popup("Problem saving file. Error is {}".format(error))
        else:
            sg.popup("force model saved as {}".format(values['fig1_path']))

        
    if (event == 'fig2_path') and (values['fig2_path'] != ''):
        try:
            fig2.savefig(values['fig2_path'])
        except (IOError, OSError) as error:
            sg.popup("Problem saving file. Error is {}".format(error))
        else:
            sg.popup("wrist shape saved as {}".format(values['fig2_path']))

    if event == 'Plot 3d graph':
        if figure_agg_3d:
            delete_3d_figure_agg(figure_agg_3d)
            
        window['-OUTPUT4-'].update(visible = False)
        window['-OUTPUT5-'].update(visible = False)
        
        dict_of_parameters = values.copy()
        n = int(values['n'])
        if not is_float(dict_of_parameters, window, n, '-OUTPUT4-'):
            window['-OUTPUT5-'].update("Please find and correct the values that are not floats.", visible=True)
        elif not check_parameters(dict_of_parameters, window, n, '-OUTPUT2-'):
            window['-OUTPUT5-'].update("Please find and correct the values.", visible=True)
        elif not valid_force(dict_of_parameters['force_3d']):
             window['-OUTPUT4-'].update("force should be a float greater than 0.", visible=True)
             window['-OUTPUT5-'].update("Please find and correct the values.", visible=True)
             
        else:
             fig3d, figure_agg_3d = plot_3d(window, n, dict_of_parameters)
         
            
            
    if event == "Save Values":
        if values['n'] == '':
            sg.popup('Please fill in all the fields (except maximum force) before attempting to save.')
        else:
            filename = ''
            filename = sg.popup_get_file('Save the values in a text file', save_as = True, no_window=True, file_types=(('TXT', '.txt'),))
            if filename != '':
                if export_values(values, filename):
                    sg.popup("values were saved as {}".format(filename))
            
            

    if event == 'Load Values':
        update_window_before_loading_values(window, values, n, max_n, g_layout_list, h_layout_list, c_layout_list)
        load_all_values(max_n, g_layout_list, h_layout_list, c_layout_list, window)


window.close() 

#plt.gcf().canvas.get_supported_filetypes()

"""
example of the format of text file (.txt):

# lengths are in units of mm 
# Young's modulus is in units of GPa 
Notches: 5
Depths: [1.4, 1.4, 1.4, 1.4, 1.4]
Heights: [0.8, 0.8, 0.8, 0.8, 0.8]
Uncut: [1.2, 1.2, 1.2, 1.2, 1.2]
Outer_Radius: 0.81
Inner_Radius: 0.7
Coefficient_Friction: 0.13
Linear_Young's_Modulus: 10
Superelastic_Modulus: 3
Strain_Lower: 0.028
"""
