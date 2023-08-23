import PySimpleGUI as gui
from followExcel import FollowExcel
from changeTemp import serialCom
import os
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import time
import threading
import socket

# delay program so everything loads properly on startup
time.sleep(2)

# change color theme
gui.theme("DarkBlue4")

# setup correct display type for 3.5 inch display
if os.environ.get('DISPLAY','') == '':
    print('no display found. Using :0.0')
    os.environ.__setitem__('DISPLAY', ':0.0')

# initialize variables    
startTime = time.time()
programTime = 0
temp = 48
killThread = False
width, height = gui.Window.get_screen_size()
allCoordinates = []
print(width, height)
# change font size before changing these
buttonWidth = int(width * 0.02) # change value until button takes up ~1/3 width of screen
buttonHeight = int(height * 0.012) # change value until button take up a little less than 1/2 height of screen
textWidth = int(width * 0.036)  # change value until button takes up ~1/3 width of screen
textHeight = int(height * 0.0010) # change value until everything fits on the main menu
pbHeight = int(height * 0.1) # change value until everything fits 
pbPadding = int(height * 0.25) # change value until everything fits 

# change font, if using a new resolution change font size first (effects button and text size)
font = ('Courier New', 16)
gui.set_options(font=font)

# serial connection varaibles, raspi port: /dev/ttyUSB0
baudRate = 115200
mySerialPort = "COM11"

# layout of the main menu
layoutGeneral = [
    [gui.Button('Close'), gui.Button('IP')],
    [gui.Text('Menu', size=(int(textWidth * 2/3), textHeight)), gui.Text('Time:', size=(int(textWidth * 2/3), textHeight), key='-TIME-'),
     gui.Text('Temp:', size=(int(textWidth * 2/3), textHeight), key='-TEMP-')],
    [gui.Button('Pork', size=(buttonWidth, buttonHeight)), gui.Button('Chicken', size=(buttonWidth, buttonHeight)), gui.Button('Beef', size=(buttonWidth, buttonHeight))],
    [gui.Button('Custom', size=(buttonWidth, buttonHeight)), gui.Button('Graph', size=(buttonWidth, buttonHeight)), gui.Button('Set Temp', size=(buttonWidth, buttonHeight))]
]

# Convert time in seconds into a string in the correct format (00:00:00)
def convert(seconds):
    seconds = seconds % (24 * 3600)
    hour = seconds // 3600
    seconds %= 3600
    minutes = seconds // 60
    seconds %= 60
    return "%d:%02d:%02d" % (hour, minutes, seconds)

# Convert farenheit ot a string in celcius
def F2C(farenheit):
    celcius = (farenheit - 32) * 5 / 9
    celcius = '%.2f'%celcius
    return str(celcius)

def getIP():
    testIP = "8.8.8.8"
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect((testIP, 0))
    ipaddr = s.getsockname()[0]
    return str(ipaddr)

def createIPWindow(name):
    layout = [[gui.Text("IP address: " + getIP(), font = ('Helvetica', 20), justification='center', expand_x=True, pad=(0,pbPadding))],
            [gui.Button('Back', size=(int(buttonWidth * 4), buttonHeight))]]
    return gui.Window(name, layout, modal=True, resizable = True).Finalize()

def detectIPWindow():
    global programTime
    while True:
        event, values = IPWindow.read(timeout = 0)
        if event == 'Back':
            print('Back')
            IPWindow.close()
            break
        programTime = time.time() - startTime # updates the overall time 

# layout for general cook windows (pork, chicken, beef)
def createCookWindow(name):
    matplotlib.use('Agg')
    global fig
    fig = matplotlib.figure.Figure(figsize=(9,2), dpi = 62)
    layout = [[gui.Text(name, size=(int(textWidth * 2/3), textHeight)), gui.Text('Time:', size=(int(textWidth * 2/3), textHeight), key='-TIME-'), 
                gui.Text('Temp:', size=(int(textWidth * 2/3), textHeight), key='-TEMP-')],
                [gui.Canvas(key='-CANVAS-')],
                [gui.ProgressBar(100, orientation='h', expand_x=True, size=(textWidth, pbHeight), key='-PBAR-'), gui.Text('0%', key='-PER-')],
                [gui.Button('Start', size=(textWidth, buttonHeight), key='-START-'), gui.Button('Back', size=(textWidth, buttonHeight))]]
    return gui.Window(name, layout, modal=True, resizable = True).Finalize() 
    # for some reason you need resizable = True and can not add no_titlebar for .maximize to work on a raspberry pi,
    # for laptop/pc you want to get rid of resizable and add no_titlebar = true for all createWindow functions

# functionality for the cook window
def detectCookWindow(file):
    global programTime
    pfe = FollowExcel(serialPort=mySerialPort, baud=baudRate, file=file) # initialize class with custom file
    startFlag = False # program has not yet started
    coords = [] # empty set of coordinates for the graph
    windowStartTime = 0
    while True:
        event, values = cookWindow.read(timeout=0)
        if event == 'Back':
            print('Back')
            pfe.stop() # stops follow excel method
            cookWindow.close()
            break
        elif event == '-START-': # this button will swap between 'Start' and 'Cancel' states
            if startFlag == False: 
                print('Start')
                cookWindow.perform_long_operation(lambda: pfe.start(), '-RETURN-') # starts follow excel method as a thread
                cookWindow['-START-'].update('Cancel')
                windowStartTime = time.time() # set initial time for counter
                startFlag = True
            else:
                print('Cancel')
                pfe.stop() # stops follow excel method
                cookWindow['-START-'].update('Start')
                startFlag = False
        elif event == '-RETURN-':
            cookWindow['-START-'].update('Start')
            coords = [] # reset graph numbers
            figPlot.clear() # reset graph image
            pfe = FollowExcel(serialPort=mySerialPort, baud=baudRate, file=file) # resets the temperature to 48
            if startFlag == True:
                pfe.time = pfe.maxTime # make progress bar show 100%
            elif startFlag == False:
                pfe.time = 0 # make progress bar show 0%
            startFlag = False
        if startFlag == True:
            windowTime = time.time() - windowStartTime # counter
            if windowTime > 1: # delay counter by 1 second so previous temperature does not get graphed
                coords.append((windowTime, pfe.temp)) # add temperature and time data to graph
            updateGraph(coords) # update graph image
        # update components
        cookWindow['-PBAR-'].update(round(100*pfe.time/pfe.maxTime))
        cookWindow['-PER-'].update(str(round(100 * pfe.time/pfe.maxTime)) + '%')
        cookWindow['-TIME-'].update("Time: " + convert(pfe.time))
        cookWindow['-TEMP-'].update("Temp: " + str(pfe.temp) + "F/ " + F2C(pfe.temp) + "C")
        global temp
        temp = pfe.temp # update global temperature so the main menu knows the temperature
        programTime = time.time() - startTime # updates the overall time 
        cookWindow.refresh() # refreshes window (I don't think this is needed)
    
# layout for the custom window
def createCustomWindow(name):
    matplotlib.use('Agg')
    global fig
    fig = matplotlib.figure.Figure(figsize=(9, 2), dpi = 62)
    layout = [[gui.Text(name, size=(int(textWidth * 2/3), textHeight)), gui.Text('time:', size=(int(textWidth * 2/3), textHeight), key='-TIME-'), 
               gui.Text('Temp:', size=(int(textWidth * 2/3), textHeight), key='-TEMP-')],
                [gui.Text('Selected file: '), gui.Text("", key="-FILE-", font = ("Arial", 12))],
                [gui.Canvas(key='-CANVAS-')],
                [gui.ProgressBar(100, orientation='h', expand_x=True, size=(textWidth, pbHeight), key='-PBAR-'), gui.Text('0%', key='-PER-')],
                [gui.Button('Start', size=(int(textWidth * 2 / 3), buttonHeight), key='-START-'),
                gui.Button('Customize File', size=(int(textWidth * 2 / 3), buttonHeight), key='-CUSTOM-'),
                gui.Button('Back', size=(int(textWidth * 2 / 3), buttonHeight))]]
    return gui.Window(name, layout, modal=True, resizable = True).Finalize()

# functionality for the custom window (similar to cookwindow)
def detectCustomWindow():
    global programTime
    # change file path when changing devices
    file_path = r'C:\Users\jqi\OneDrive - SharkNinja\Desktop\Python Scripts\Digital potentiometer\Test.csv'
    pfe = FollowExcel(serialPort=mySerialPort, baud=baudRate, file='Test.csv') # default file is test.csv
    customWindow["-FILE-"].update(file_path)
    startFlag = False
    coords = []
    windowStartTime = 0
    while True:
        event, values = customWindow.read(timeout=0)
        if event == 'Back':
            print('Back')
            pfe.stop()
            customWindow.close()
            break
        elif event == '-START-':
            if startFlag == False:
                print('Start')
                customWindow.perform_long_operation(lambda: pfe.start(), '-RETURN-')
                customWindow['-START-'].update('Cancel')
                customWindow['-CUSTOM-'].update('')
                windowStartTime = time.time()
                startFlag = True
            else:
                print('Cancel')
                pfe.stop() # stops follow excel method
                customWindow['-START-'].update('Start')
                startFlag = False
        elif event == '-CUSTOM-':
            if startFlag == False:
                print('Customize File')
                tempFile = file_path
                file_path = gui.popup_get_file("Select a file", title="File Explorer", file_types=(("ALL CSV Files", "*.csv"),)) # get a csv file from file explorer
                print(file_path)
                if file_path:
                    customWindow["-FILE-"].update(file_path) # change file_path in GUI
                    pfe = FollowExcel(serialPort=mySerialPort, baud=baudRate, file=file_path) # update based on new file_path
                else:
                    file_path = tempFile
        elif event == '-RETURN-':
            print('Return')
            customWindow['-START-'].update('Start')
            coords = []
            figPlot.clear() 
            pfe = FollowExcel(serialPort=mySerialPort, baud=baudRate, file=file_path) # reset temperature to 48
            customWindow['-CUSTOM-'].update('Customize File')
            if startFlag == True:
                pfe.time = pfe.maxTime # make progress bar show 100%
            elif startFlag == False:
                pfe.time = 0 # make progress bar show 0%
            startFlag = False
        if startFlag == True:
            windowTime = time.time() - windowStartTime
            if windowTime > 1:
                coords.append((windowTime, pfe.temp)) 
            updateGraph(coords)
        customWindow['-PBAR-'].update(round(100 * pfe.time/pfe.maxTime))
        customWindow['-PER-'].update(str(round(100 * pfe.time/pfe.maxTime)) + '%')
        customWindow['-TIME-'].update("Time: " + convert(pfe.time))
        customWindow['-TEMP-'].update("Temp: " + str(pfe.temp) + "F/ " + F2C(pfe.temp) + "C")
        global temp
        temp = pfe.temp
        programTime = time.time() - startTime
        customWindow.refresh()

# layout for the set temp window
def createSetTempWindow(name):
    layout = [[gui.Text(name, size=(textWidth, textHeight)), gui.Text('Temp:', size=(textWidth, textHeight), key='-TEMP-')],
                  [gui.Slider(range=(0,255), orientation='h', size=(textWidth * 2, pbHeight), default_value=0, pad=(0,pbPadding), enable_events=True, key='-SL-')],
                  [gui.Button('Back', size=(textWidth * 2, buttonHeight))]]
    return gui.Window(name, layout, modal=True, resizable = True).Finalize()

# functionality for the set temp window
def detectSetTempWindow():
    global programTime
    sc = serialCom(serialPort = mySerialPort, baud = baudRate)
    sc.changeStep(255) # default set temperature to 48
    while True:
        event, values = setTempWindow.read(timeout=0)
        if event == 'Back':
            print('Back')
            setTempWindow.close()
            break
        if event == '-SL-':
            sc.changeStep(int(values['-SL-'])) # change temp to reflect slider step
        setTempWindow['-TEMP-'].update("Temp: " + str(sc.temp) + "F/ " + F2C(sc.temp) + "C")
        global temp
        temp = sc.temp
        programTime = time.time() - startTime # change counter time

# layout for the graph window
def createGraphWindow(name):
    matplotlib.use('Agg')
    global fig
    fig = matplotlib.figure.Figure(figsize=(6, 2), dpi = 100)
    layout = [[gui.Canvas(key='-CANVAS-')],
            [gui.Button('Back', size=(int(buttonWidth * 4), buttonHeight))]]
    return gui.Window(name, layout, modal=True, resizable = True).Finalize()

# functionality for the graph window
def detectGraphWindow():
    global programTime
    while True:                             # Event Loop
        event, values = graphWindow.read(timeout=0)
        if event in (None, 'Back'):
            break
        updateGraph(allCoordinates) 
        programTime = time.time() - startTime # change counter time
    graphWindow.close()

# updates the graph based on given coordinates
def updateGraph(customCoordinates):
    figPlot.clear() # clear graph
    if customCoordinates:
        x, y = zip(*customCoordinates) # x is all x points, y is all y points
        figPlot.plot(x, y, color='blue')
    canvas.draw() # draw new graph

# Repeatably does a function with a delay between cycles
def every(delay, task):
  global killThread
  next_time = time.time() + delay
  while True:
    time.sleep(max(0, next_time - time.time()))
    task()
    next_time += (time.time() - next_time) // delay * delay + delay
    if killThread == True:
        break

# updates the coordinates for the graph window
def updateCoords():
    allCoordinates.append((round(programTime - 1), temp))

# start the main menu window
window = gui.Window('DigipotGUI', layoutGeneral, resizable = True).Finalize()
window.maximize()
# creates a thread which updates the coordinates every 1 second
threading.Thread(target=lambda: every(1, updateCoords)).start()
#functionality for the main menu window
while True:
    event, values = window.read(timeout=0)

    if event in (gui.WIN_CLOSED, 'Close'):
        break
    if event == 'IP':
        print('IP')
        IPWindow = createIPWindow('IP')
        IPWindow.maximize()
        IPWindow = detectIPWindow()
    elif event == 'Pork':
        print('Pork')
        cookWindow = createCookWindow('Pork')
        figPlot = fig.add_subplot(111)
        canvas_elem = cookWindow['-CANVAS-']
        canvas = FigureCanvasTkAgg(fig, canvas_elem.Widget)
        canvas.get_tk_widget().pack(fill='both', expand=1)
        cookWindow.maximize()
        detectCookWindow('PorkAvg.csv')
    
    elif event == 'Chicken':
        print('Chicken')
        cookWindow = createCookWindow('Chicken')
        figPlot = fig.add_subplot(111)
        canvas_elem = cookWindow['-CANVAS-']
        canvas = FigureCanvasTkAgg(fig, canvas_elem.Widget)
        canvas.get_tk_widget().pack(fill='both', expand=1)
        cookWindow.maximize()
        detectCookWindow('ChickenAvg.csv')
    elif event == 'Beef':
        print('beef')
        cookWindow = createCookWindow('Beef')
        figPlot = fig.add_subplot(111)
        canvas_elem = cookWindow['-CANVAS-']
        canvas = FigureCanvasTkAgg(fig, canvas_elem.Widget)
        canvas.get_tk_widget().pack(fill='both', expand=1)
        cookWindow.maximize()
        detectCookWindow('BeefAvg.csv')
    elif event == 'Custom':
        print('Custom')
        customWindow = createCustomWindow('Custom')
        figPlot = fig.add_subplot(111)
        canvas_elem = customWindow['-CANVAS-']
        canvas = FigureCanvasTkAgg(fig, canvas_elem.Widget)
        canvas.get_tk_widget().pack(fill='both', expand=1)
        customWindow.maximize()
        detectCustomWindow()
    elif event == 'Graph':
        print('Graph')
        graphWindow = createGraphWindow('Graph')
        figPlot = fig.add_subplot(111)
        canvas_elem = graphWindow['-CANVAS-']
        canvas = FigureCanvasTkAgg(fig, canvas_elem.Widget)
        canvas.get_tk_widget().pack(fill='both', expand=1)
        graphWindow.maximize()
        graphWindow = detectGraphWindow()
    elif event == 'Set Temp':
        print('Set Temp')
        setTempWindow = createSetTempWindow('Set Temp')
        setTempWindow.maximize()
        setTempWindow = detectSetTempWindow()
    
    # update the time and temp so they can be displayed
    window['-TIME-'].update("Time: " + convert(round(programTime - 1)))
    window['-TEMP-'].update("Temp: " + str(temp) + "F/ " + F2C(temp) + "C")
    programTime = time.time() - startTime

# close program
killThread = True
window.close()