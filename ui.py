
import PySimpleGUI as sg
import requests
import os
from api import get_nums

# iterate and read starter code from api.py
def get_starter_code():
    starter = ''
    try:
        with open(os.path.join(os.path.dirname(__file__), 'api.py'), 'r', encoding='utf-8') as f:
            lines = f.readlines()
        in_block = False
        for line in lines:
            if 'starter_example = """' in line:
                in_block = True
                continue
            if in_block:
                if '"""' in line:
                    break
                starter += line
    except Exception:
        starter = ''
    return starter

# layout
layout = [
    [sg.Text('aStarSearch Code:', justification='center', font=('Any', 14), expand_x=True)],
    [sg.Multiline(default_text=get_starter_code(), size=(80, 20), key='-CODE-', expand_x=True, expand_y=True)],
    [
        sg.Text('NUM_OF_ITERATIONS:'), sg.Input(default_text='3', size=(5,1), key='-ITER-'),
        sg.Text('NUM_BEST:'), sg.Input(default_text='10', size=(5,1), key='-BEST-'),
        sg.Text('MAX_NUM:'), sg.Input(default_text='100', size=(5,1), key='-MAX-'),
    ],
    [sg.Button('Start/Send', key='-SEND-')],
    [sg.Text('', key='-STATUS-', size=(60,1))]
]

# initialize window
window = sg.Window('A* Search Evolution UI', layout, resizable=True, size=(800, 600))


# instance loop
while True:
    event, values = window.read()
    if event == sg.WINDOW_CLOSED:
        break
    if event == '-SEND-':
        code = values['-CODE-']
        try:
            num_iter = int(values['-ITER-'])
            num_best = int(values['-BEST-'])
            max_num = int(values['-MAX-'])
            get_nums(num_iter, num_best)
        except ValueError:
            window['-STATUS-'].update('ERROR: Enter valid integers for all variables!')
            continue

        #send data here to the API
        window['-STATUS-'].update('NOTICE: Sent to API! Processing...')

window.close()
