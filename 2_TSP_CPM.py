#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Feb 16 10:38:45 2023

@author: albertogonzalezv
"""




import serial
import csv, time, os
import tkinter as tk
import serial.tools.list_ports
import datetime
from os import sep
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

incoming = ''
incomingCPM = ''
score_list = []
now = datetime.datetime.now()
current_time = now.strftime("%Y_%m_%d_%H_%M_%S")
startTempTSP = 45 # for TSP
startTempCPM = 45 # for CPM
folder = 'TSP_CPM'

def send_data(data_out): # send by serial
    if ser!=False:
        for i in data_out:
            ser.write(i.encode())
            time.sleep(0.002)
def read_data(): # read serial
    if ser!=False:
        incoming=''
        while ser.inWaiting():
            incoming = incoming + ser.read().decode()
        return(incoming)


def connect():
    global ser
    port_idx = port_listbox.curselection()[0] # Obtiene el índice de la selección actual
    port = port_listbox.get(port_idx) # Obtiene el puerto seleccionado en el índice
    baud_rate = 115200
    try:
        start_save()
        ser = serial.Serial(port, baud_rate, timeout=0)
        status_label.config(text="TCS Connected to " + port)
        connect_button.config(state="disabled")
        disconnect_button.config(state="normal")
        send_buttonTSP.config(state="normal")
        save_buttonTSP.config(state="normal")

        temps_message.config(text="Select the correct TSP Pain5 temp and press Stim 1")
        send_data('F') # stimulation time = 500ms
        time.sleep(0.005)
        send_data('D000500') # stimulation time = 500ms
        time.sleep(0.005)
        send_data('N320')
        time.sleep(0.005)
        send_data('V01700')
        time.sleep(0.005)
        send_data('R01700')
        time.sleep(0.005)
    except serial.SerialException:
        status_label.config(text="Error: Could not connect to " + port)

def disconnect():
    global ser
    if ser is not None and ser.isOpen():
        ser.close()
        status_label.config(text="Disconnected from " + ser.port)
        connect_button.config(state="normal")
        disconnect_button.config(state="disabled")
        ser = None

def refresh():
    ports = serial.tools.list_ports.comports()
    port_listbox.delete(0, tk.END)
    for port, desc, hwid in sorted(ports):
        port_listbox.insert(tk.END, port)

def on_close():
    if ser:
        ser.close()
    if serCPM:
        serCPM.close()
    root.destroy()

# countdown

def countdown():
    global start_time
    if start_time is not None:
        remaining_time = start_time - time.time()
        if remaining_time <= 0:
            countdown_label.config(text='0.0 s')
            return
        else:
            countdown_label.config(text='{:.1f} s'.format(remaining_time))
            countdown_label.after(1000, countdown)

def reset_countdown():
    global start_time
    start_time = None
    countdown_label.config(text='')

def countdown2():
    global start_time
    if start_time is not None:
        remaining_time = start_time - time.time()
        if remaining_time <= 0 and temps_message.cget('text') == "Rate pain cold plate in:":
            save_buttonCP.config(state="normal")
            temps_message.config(text="Test Stim Post in:")
            start_time = time.time() + 10  # start countdown again with 10 seconds
            countdown2()  # start the countdown again
        elif remaining_time <= 0 and temps_message.cget('text') == "Test Stim Post in:":
            temps_message.config(text="Rate Pain Test Stim Post in:")
            send_data('L')
            start_time = time.time() + 10  # start countdown again with 10 seconds
            countdown2()  # start the countdown again
        elif remaining_time <= 0:
            countdown_label.config(text='0.0 s')
            save_buttonCPM2.config(state="normal")
            temps_message.config(text="Save Pain Test Stim Post")
            return
        else:
            countdown_label.config(text='{:.1f} s'.format(remaining_time))
            countdown_label.after(1000, countdown2)

def count20():
    global start_time
    start_time = time.time() + 20
    temps_message.config(text="Rate pain cold plate in:")
    countdown2()




def update_temps():
    global incoming
    if ser is not None and ser.isOpen():
        try:
            incoming = ser.read(1000)
            ser.write('E'.encode())
            temps_read = [float(x)/10 for x in incoming.decode().split('+')]
            temps_read = temps_read[1:6]
            if len(temps_read)==5:

                return(temps_read)
            else:
                return([0,0,0,0,0])
        except: return([0,0,0,0,0])

def test_user():
    user_id = id_entry.get()
    if user_id == '':
        tk.messagebox.showerror("Error", "Please enter a participant ID and then connect")
        return False
    else:
        return True

def start_save():
    global folder
    user= test_user()
    if user:
        if not os.path.exists(folder):
            os.makedirs(folder)
        user_id = id_entry.get()
        with open((folder +sep+ user_id +'_' + current_time +'TSP_CPM.csv'), mode='a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["participant_id", "TrialType", "Temp","datetime"])

def save_results(data1,concept):
    global folder
    user_id = id_entry.get()
    with open((folder +sep+ user_id +'_' + current_time +'TSP_CPM.csv'), mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([user_id, concept, data1, datetime.datetime.now().time()])




def stimTSP1():
    global ser
    global start_time
    dataS = float(send_varTSP.get())
    datstr = str(dataS).replace('.','')
    if dataS<10:
        datstr= '0' + datstr
    data = 'C0' +datstr
    send_data(data)
    time.sleep(0.003)
    send_data('D000500') # stimulation time = 5s
    time.sleep(0.003)
    send_data('L')
    save_tempTSP()
    send_buttonTSP.config(state="disabled")
    save_buttonTSP.config(state="normal")  # disable the button
    send_buttonTSP.after(500, lambda: send_buttonTSP.config(state="normal"))  # enable the button after 500 ms
    start_time = time.time() + 11
    temps_message.config(text="Save now TSP Stim1 Pain")
    countdown()

def stimTSP10():
    global ser

    StartTSPtime = time.time()
    cont=0
    temps_message.config(text="Next Step: Save TSP Stim10 Pain")
    while cont<10:
        if  (time.time()- StartTSPtime)>cont:
            cont+=1
            send_data('L')
            countdown_label.config(text=str(10-cont))
            countdown_label.update_idletasks()

        root.update()
    save_buttonTSP10.config(state="normal")


def save_tempTSP():
    global start_time
    if test_user():
        save_results(send_varTSP.get(),'tempTSP')
        start_time = time.time() + 5
        countdown()


def save_scoreTSP():
    if test_user():
        save_results(score_scaleTSP.get(),'vasTSP1')
        temps_message.config(text="Press Stim10 when time=0")
        send_buttonTSP10.config(state="normal")
        send_buttonTSP.config(state="disabled")
        save_buttonTSP.config(state="disabled")  # disable the button
        save_buttonTSP.after(200, lambda: save_buttonTSP.config(state="normal"))  # enable the button after 500 ms
        info_TSP_label.config(text="Done: " + str(score_scaleTSP.get()))

def save_scoreTSP10():
    if test_user():
        global start_time
        start_time = time.time() + 60
        save_results(score_scaleTSP10.get(),'vasTSP10')
        temps_message.config(text="Next Step: Connect Cold Plate")
        send_buttonTSP.config(state="normal")
        send_buttonTSP10.config(state="disabled")
        save_buttonTSP10.config(state="disabled")  # disable the button
        save_buttonTSP10.after(200, lambda: save_buttonTSP10.config(state="normal"))  # enable the button after 500 ms
        info_TSP10_label.config(text="Done: " + str(score_scaleTSP10.get()))
        countdown()



def send_tempsCPM():
    global ser
    dataS = float(send_varCPM.get())
    datstr = str(dataS).replace('.','')

    if dataS<10:
        datstr= '0' + datstr
    data = 'C0' +datstr
    print(data)
    send_data(data)
    time.sleep(0.1)
    send_data('D010000') # stimulation time = 10
    time.sleep(0.1)
    send_data('L')
    save_tempCPM()
    send_buttonCPM.config(state="disabled")
    temps_message.config(text="Next Step: Save Pain Test Stim Pre")
    save_buttonCPM.config(state="normal")
    send_buttonCPM.after(9000, lambda: send_buttonCPM.config(state="normal"))  # enable the button after 500 ms



def save_tempCPM():
    global start_time
    if test_user():
        save_results(send_varCPM.get(),'tempCPM')
        start_time = time.time() + 10
        countdown()


def save_scoreCPM():
    if test_user():
        save_results(score_scaleCPM.get(),'vasCPMTestPre')
        save_buttonCPM.config(state="disabled")  # disable the button
        button20CPM.config(state="normal")
        temps_message.config(text="Next Step: Palm of non-dominant hand in cold for 40s")
        info_CPM_label.config(text=("Done: " + str(score_scaleCPM.get())))


def save_scoreCP():
    global startTempCPM
    if test_user():
        save_results(score_scaleCP.get(),'vasCPMCold')
        save_buttonCP.config(state="disabled")  # disable the button
        info_CP_label.config(text=("Done: " + str(score_scaleCP.get())))
        #temps_message.config(text="Next Step: Save Test Post Pain")

def save_scoreCPM2():
    if test_user():
        save_results(score_scaleCPM2.get(),'vasCPMTestPost')
        save_buttonCPM2.config(state="disabled")  # disable the button
        temps_message.config(text="Finished!")
        info_CPM2_label.config(text=("Done: " + str(score_scaleCPM2.get())))


def send_dataCPM(data_out): # send by serial
    if serCPM!=False:
        for i in data_out:
            serCPM.write(i.encode())
            time.sleep(0.002)


def update_tempsCPM():
    global incomingCPM
    if serCPM is not None and serCPM.isOpen():
        serCPM.write('E'.encode())
        time.sleep(0.01)
        if serCPM.inWaiting():
            incomingCPM = ''
            while serCPM.inWaiting():
                incomingCPM = incomingCPM + serCPM.read().decode()
            temps_read = incomingCPM.split()
            temp = (float(temps_read[0])/10)
        tempCP_message.config(text=('Cold Plate Temp:'+ str(temp) + 'C'))
    temps_label.after(1000, update_tempsCPM)



def connectCPM():
    global serCPM
    portCPM_idx = portCPM_listbox.curselection()[0] # Obtiene el índice de la selección actual
    portCPM = portCPM_listbox.get(portCPM_idx) # Obtiene el puerto seleccionado en el índice
    baud_rate = 115200
    try:
        serCPM = serial.Serial(portCPM, baud_rate)
        statusCPM_label.config(text="Cold Plate Connected to " + portCPM)
        connectCPM_button.config(state="disabled")
        disconnectCPM_button.config(state="normal")
        send_buttonCPM.config(state="normal")
        send_dataCPM('C100') # temp to 10.0
        time.sleep(0.005)
        temps_message.config(text="Select CPM Pain5 temp and wait for the Cold Plate to reach 10C")


    except serial.SerialException:
        statusCPM_label.config(text="Error: Could not connect to " + portCPM)

def disconnectCPM():
    global serCPM
    if serCPM is not None and serCPM.isOpen():
        serCPM.close()
        statusCPM_label.config(text="Disconnected from " + serCPM.port)
        connectCPM_button.config(state="normal")
        disconnectCPM_button.config(state="disabled")
        serCPM = None

def refreshCPM():
    portsCPM = serial.tools.list_ports.comports()
    portCPM_listbox.delete(0, tk.END)
    for portCPM, desc, hwid in sorted(portsCPM):
        portCPM_listbox.insert(tk.END, portCPM)



datax = [0]
y1 = [0]
y2 = [0]
y3 = [0]
y4 = [0]
y5 = [0]

def update_plot():
    global datax, y1, y2, y3, y4, y5, plot_button, plot_callback

    # Generate new data points
    x = datax[-1] + .13
    y = update_temps()
    y1.append(y[0])
    y2.append(y[1])
    y3.append(y[2])
    y4.append(y[3])
    y5.append(y[4])
    datax.append(x)
    y1 = y1[-100:]
    y2 = y2[-100:]
    y3 = y3[-100:]
    y4 = y4[-100:]
    y5 = y5[-100:]
    datax = datax[-100:]

    # Plot the last 100 data points with different colors for each line
    ax.clear()
    ax.plot(datax, y1, color='b')
    ax.plot(datax, y2, color='r')
    ax.plot(datax, y3, color='g')
    ax.plot(datax, y4, color='c')
    ax.plot(datax, y5, color='m')

    # Set the Y axis limits to [0, 60] for both lines
    ax.set_ylim([20, 60])

    # Redraw the canvas
    canvas.draw()

    # Schedule the next update, if the callback is defined
    if plot_callback is not None:
        root.after(100, plot_callback)

def toggle_plot():
    global plot_callback

    if plot_callback is None:
        # If the callback is not defined, define it and start updating the plot
        plot_callback = update_plot
        plot_button.config(text="Hide Temps Plot")
        update_plot()
    else:
        # If the callback is defined, stop updating the plot
        plot_callback = None
        plot_button.config(text="Show Temps Plot")




ser = None
serCPM = None


root = tk.Tk()
root.title("TSP and CPM")

# logo
# icono = tk.PhotoImage(file='painlessLogo.png')
# root.iconphoto(False, icono)
root.iconbitmap('painlessLogo.ico')










port_var = tk.StringVar()

ports_frame = tk.Frame(root)
ports_frame.pack()

id_frame =tk.LabelFrame(ports_frame, bd=1,text="Participant ID",font=('calibri', 16), relief=tk.SOLID,pady=10, padx=10)
id_frame.grid(row=0, column = 0, rowspan=4, columnspan=2, padx=5)
id_label = tk.Label(id_frame, text="Participant ID:")
id_label.grid(row=0,column=0)
id_entry = tk.Entry(id_frame)
id_entry.grid(row=0,column=1)

port_frame =tk.LabelFrame(ports_frame, bd=1,text="TCS connection",font=('calibri', 16), relief=tk.SOLID,pady=10, padx=10)
port_frame.grid(row=0, column = 2, rowspan=4, columnspan=4, padx=5)

# port_message = tk.Label(port_frame, text = ('Select de TCS port'), font=('calibri', 12))
# port_message.pack()

port_label = tk.Label(port_frame, text="Select TCS Port:")
port_label.grid(row=0, column = 0)

#port_listbox = tk.Listbox(port_frame, width=10, height=5)
port_listbox = tk.Listbox(port_frame, width=30, height=3, exportselection=False, relief=tk.RIDGE)
port_listbox.grid(row=0, column = 1)

port_scrollbar = tk.Scrollbar(port_frame, orient=tk.VERTICAL)
port_scrollbar.grid(row=0, column = 2)

port_listbox.config(yscrollcommand=port_scrollbar.set)
port_scrollbar.config(command=port_listbox.yview)

status_label = tk.Label(port_frame, text="TCS not connected", bd=1, relief=tk.SUNKEN, anchor=tk.W)
status_label.grid(row=1, column = 0, columnspan=3)


button_frame = tk.Frame(port_frame)
button_frame.grid(row=2, column = 0, columnspan=3)

connect_button = tk.Button(button_frame, text="Connect", command=connect)
connect_button.grid(row=2, column = 1)

disconnect_button = tk.Button(button_frame, text="Disconnect", command=disconnect, state="disabled")
disconnect_button.grid(row=2, column = 2)

refresh_button = tk.Button(button_frame, text="Refresh list", command=refresh)
refresh_button.grid(row=2, column = 3)


# connect to Cold plate

portCPM_var = tk.StringVar()


portCPM_frame = tk.LabelFrame(ports_frame, bd=1,text="Cold Plate connection",font=('calibri', 16), relief=tk.SOLID,pady=10, padx=10)
portCPM_frame.grid(row=0, column =7 , rowspan=4, columnspan=4, padx=5)

# port_message = tk.Label(port_frame, text = ('Select de TCS port'), font=('calibri', 12))
# port_message.pack()

portCPM_label = tk.Label(portCPM_frame, text="Select Cold Plate Port:")
portCPM_label.grid(row=0, column = 0)

#port_listbox = tk.Listbox(port_frame, width=10, height=5)
portCPM_listbox = tk.Listbox(portCPM_frame, width=30, height=3, exportselection=False, relief=tk.RIDGE)
portCPM_listbox.grid(row=0, column = 2)

portCPM_scrollbar = tk.Scrollbar(portCPM_frame, orient=tk.VERTICAL)
portCPM_scrollbar.grid(row=0, column = 3)

portCPM_listbox.config(yscrollcommand=portCPM_scrollbar.set)
portCPM_scrollbar.config(command=portCPM_listbox.yview)

statusCPM_label = tk.Label(portCPM_frame , text="Cold Plate Not connected", bd=1, relief=tk.SUNKEN, anchor=tk.W)
statusCPM_label.grid(row=1, column = 0,  columnspan=3)


buttonCPM_frame = tk.Frame(portCPM_frame)
buttonCPM_frame.grid(row=2, column = 0, columnspan=3)

connectCPM_button = tk.Button(buttonCPM_frame, text="Connect", command=connectCPM)
connectCPM_button.grid(row=2, column = 1)

disconnectCPM_button = tk.Button(buttonCPM_frame, text="Disconnect", command=disconnectCPM, state="disabled")
disconnectCPM_button.grid(row=2, column = 2)

refreshCPM_button = tk.Button(buttonCPM_frame, text="Refresh list", command=refreshCPM)
refreshCPM_button.grid(row=2, column = 3)



## Temporal Summation of Pain"
t5TSP_label_frame = tk.LabelFrame(root, bd=1,text="Temporal Summation of Pain",font=('calibri', 18), relief=tk.SOLID)
t5TSP_frame = tk.Frame(t5TSP_label_frame)

send_frameTSP = tk.Frame(t5TSP_frame)
send_frameTSP.pack()
send_labelTSP = tk.Label(send_frameTSP, text="Pain5 Temp:", width=12)
send_labelTSP.pack(side=tk.LEFT)
valuesTSP = list(range(5, 60))
send_varTSP = tk.StringVar()
send_varTSP.set(valuesTSP[startTempTSP-5])  # set initial value to first item in list

send_entryTSP = tk.Spinbox(send_frameTSP, from_=5, to=60, increment=0.5, textvariable=send_varTSP, width=4)
send_entryTSP.pack(side=tk.LEFT)
send_buttonTSP = tk.Button(send_frameTSP, text="Stim 1", command=stimTSP1, state="disabled")
send_buttonTSP.pack(side=tk.LEFT)

send_buttonTSP10 = tk.Button(send_frameTSP, text="Stim 10", command=stimTSP10, state="disabled")
send_buttonTSP10.pack(side=tk.LEFT)

score_frameTSP = tk.Frame(t5TSP_frame)
score_frameTSP.pack()

# Primera fila
score_labelTSP = tk.Label(score_frameTSP, text="Stim1 Pain :")
score_labelTSP.pack(side=tk.LEFT)
score_scaleTSP = tk.Scale(score_frameTSP, from_=0, to=10, length=300, orient=tk.HORIZONTAL)
score_scaleTSP.pack(side=tk.LEFT)
save_buttonTSP = tk.Button(score_frameTSP, text="Save Stim1 Pain", command=save_scoreTSP, state="disabled")
save_buttonTSP.pack(side=tk.LEFT, pady=(15,15))
info_TSP_label = tk.Label(score_frameTSP,text="",font=('calibri', 12),widt=8)
info_TSP_label.pack(side=tk.LEFT)

# Segunda fila
score_frameTSP10 = tk.Frame(t5TSP_frame)
score_frameTSP10.pack()

score_labelTSP10 = tk.Label(score_frameTSP10, text="Stim10 Pain :")
score_labelTSP10.pack(side=tk.LEFT)
score_scaleTSP10 = tk.Scale(score_frameTSP10, from_=0, to=10, length=300, orient=tk.HORIZONTAL)
score_scaleTSP10.pack(side=tk.LEFT)
save_buttonTSP10 = tk.Button(score_frameTSP10, text="Save Stim10 Pain", command=save_scoreTSP10, state="disabled")
save_buttonTSP10.pack(side=tk.LEFT)
info_TSP10_label = tk.Label(score_frameTSP10,text="",font=('calibri', 12),widt=8)
info_TSP10_label.pack(side=tk.LEFT)


t5TSP_frame.pack()
t5TSP_label_frame.pack(padx=10, pady=10)




# Conditioned Pain Modulation
t5CPM_label_frame = tk.LabelFrame(root, bd=1,text="Conditioned Pain Modulation", font=('calibri', 18), relief=tk.SOLID)
t5CPM_frame = tk.Frame(t5CPM_label_frame)




send_frameCPM = tk.Frame(t5CPM_frame)
send_frameCPM.pack()
send_labelCPM = tk.Label(send_frameCPM, text="CPM Pain5 temp:", width=12)
send_labelCPM.pack(side=tk.LEFT)
valuesCPM = list(range(5, 60))
send_varCPM = tk.StringVar()
send_varCPM.set(valuesCPM[startTempCPM-5])  # set initial value to first item in list

send_entryCPM = tk.Spinbox(send_frameCPM, from_=5, to=60, increment=0.5, textvariable=send_varCPM, width=4)
send_entryCPM.pack(side=tk.LEFT)
send_buttonCPM = tk.Button(send_frameCPM, text="Test Stim Pre", command=send_tempsCPM, state="disabled")
send_buttonCPM.pack(side=tk.LEFT)

button20CPM = tk.Button(send_frameCPM, text="Start 40s Cold Plate", command=count20, state="disabled")
button20CPM.pack(side=tk.LEFT)



score_frameCPM = tk.Frame(t5CPM_frame)
score_frameCPM.pack()

score_labelCPM = tk.Label(score_frameCPM, text="Pain Test Stim Pre:")
score_labelCPM.pack(side=tk.LEFT,)
score_scaleCPM = tk.Scale(score_frameCPM, from_=0, to=10, length=300, orient=tk.HORIZONTAL)
score_scaleCPM.pack(side=tk.LEFT)
save_buttonCPM = tk.Button(score_frameCPM, text="Save Pain Pre", command=save_scoreCPM, state="disabled")
save_buttonCPM.pack(side=tk.LEFT)
info_CPM_label = tk.Label(score_frameCPM,text="",font=('calibri', 12),widt=8)
info_CPM_label.pack(side=tk.LEFT)

score_frameCP = tk.Frame(t5CPM_frame)
score_frameCP.pack()
score_labelCP = tk.Label(score_frameCP, text="      Pain Cold Plate:")
score_labelCP.pack(side=tk.LEFT,)
score_scaleCP = tk.Scale(score_frameCP, from_=0, to=10, length=300, orient=tk.HORIZONTAL)
score_scaleCP.pack(side=tk.LEFT)
save_buttonCP = tk.Button(score_frameCP, text="Save Pain Cold", command=save_scoreCP, state="disabled")
save_buttonCP.pack(side=tk.LEFT)
info_CP_label = tk.Label(score_frameCP,text="",font=('calibri', 12),widt=8)
info_CP_label.pack(side=tk.LEFT)

score_frameCPM2 = tk.Frame(t5CPM_frame)
score_frameCPM2.pack()
score_labelCPM2 = tk.Label(score_frameCPM2, text="Pain Test Stim Post:")
score_labelCPM2.pack(side=tk.LEFT,)
score_scaleCPM2 = tk.Scale(score_frameCPM2, from_=0, to=10, length=300, orient=tk.HORIZONTAL)
score_scaleCPM2.pack(side=tk.LEFT)
save_buttonCPM2 = tk.Button(score_frameCPM2, text="Save Pain Post", command=save_scoreCPM2, state="disabled")
save_buttonCPM2.pack(side=tk.LEFT)
info_CPM2_label = tk.Label(score_frameCPM2,text="",font=('calibri', 12),widt=8)
info_CPM2_label.pack(side=tk.LEFT)




t5CPM_frame.pack()
t5CPM_label_frame.pack(padx=10)




save_frame = tk.Frame(root, width=500, height=100)
save_frame.pack( padx=10, pady=10)


temps_message = tk.Label(save_frame, text = ('Write Participant ID and Connect TCS'), font=('calibri', 16))
#temps_message.pack(side=tk.LEFT)
temps_message.grid(row=0, column=0, padx=(0,35), pady=5, sticky='w')
countdown_label = tk.Label(save_frame, text='', font=('calibri', 16))
#countdown_label.pack(side=tk.RIGHT)
countdown_label.grid(row=0, column=1, padx=(100,0), pady=5, sticky='e')

temps_frame = tk.Frame(root)
temps_frame.pack()


tempCP_message = tk.Label(temps_frame, text = ('Cold Plate Temp:'), font=('calibri', 14))
#temps_message.pack(side=tk.LEFT)
tempCP_message.grid(row=0, column=0, padx=(0,35), sticky='w')
plot_button = tk.Button(temps_frame, text="Show Temps Plot", command=toggle_plot, state="normal")
plot_button.grid(row=0, column=1, padx=10)
# Define the plot callback as initially None
plot_callback = None

temps_label = tk.Label(root, font=('calibri', 12))
temps_label.pack()



# create a matplotlib figure
fig = plt.Figure()
ax = fig.add_subplot(111)

# create a tkinter canvas for the figure
canvas = FigureCanvasTkAgg(fig, master=root)
canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)



update_temps()
update_tempsCPM()
refresh()
refreshCPM()
root.protocol("WM_DELETE_WINDOW", on_close)
root.mainloop()


########################## TCS conection
#time.sleep(1)
#print(read_data())
#time.sleep(.5)
#send_data('S10001') # activar todas as superficies
#time.sleep(.1)
#send_data('C0090') #Setting the temperature setpoint
#time.sleep(.1)
#send_data('G') #authomatic calibration
#time.sleep(5)
#send_data('N420') #Setting resting temp N230
#time.sleep(.1)
#send_data('D001000') #Setting the stimulation time (Ds00200 = 200ms)
#time.sleep(.1)
#send_data('T255010') #Set trigger and duration
#time.sleep(.1)
#send_data('P') # ask for parameter
#time.sleep(.1)
#print(read_data())
#send_data('E') # ask for temperatures
#time.sleep(.1)
