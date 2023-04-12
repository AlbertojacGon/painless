#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Feb 15 22:31:21 2023

@author: albertogonzalezv
"""

import explorepy
import serial
import csv,os,time
import tkinter as tk
from datetime import datetime
from os import sep
import serial.tools.list_ports
from explorepy.tools import get_local_time
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

eeg_trials = 25
dev_name = "Explore_8532"
folder = "EEG_Cheps"

now = datetime.now()
current_time = now.strftime("%Y_%m_%d_%H_%M_%S")
explore = None
ser = None

time_cont = 0
trial_cont = 0
STOP =0
dataS= 60
# connect
def connect_explore(dev_name):
    
    global explore
    explore = explorepy.Explore()
    explorepy.set_bt_interface('sdk')
    explore.connect(device_name=dev_name_entry.get())
    
    eeg_dev = True
    if eeg_dev:
        connectEEG_button.config(state=tk.DISABLED)
        start_button.config(state="normal")

def on_close():
    global explore
    if explore:
        explore.disconnect()
    if ser:
        ser.close()
    root.destroy()
    
def start_rec():
    global folder, STOP, time_cont, trial_cont, dataS
    if test_user():
        user_id = id_entry.get()
        explore.record_data(file_name=(folder + sep + user_id + current_time+'_' + str(trial_cont)), file_type='csv')
        stop_button.config(state="normal")
        start_button.config(state="disabled")
        STOP = False
        while trial_cont<eeg_trials:
            t0=time.time()
            time_cont=0
            if not STOP:
                while time.time()-t0<9.9:               
                    if not STOP:
                        if (time.time()-t0)>time_cont:
                            
                            tempTCS_message2.config(text=('Wait for:'+str(10-time_cont)))
                            tempTCS_message2.update_idletasks()
                            time_cont+=1
                        root.update()
                        time.sleep(.001)
                    else:break
                if not STOP:
                    send_data('L')
                    save_other('TRIGGER', dataS)
                    trial_cont+=1
                    crono.config(text = ("Trials: " +str(trial_cont) +'/'+str(eeg_trials)))
            else: break
        if trial_cont>=eeg_trials:
            crono.config(text ="Finished. Stop and Save Pain") 
        

def stop_rec():
    global STOP
    explore.stop_recording()
    STOP = True
    start_button.config(state="normal")
    stop_button.config(state="disabled")

def test_user():
    user_id = id_entry.get()
    if user_id == '':
        tk.messagebox.showerror("Error", "Please enter an ID")
        return False
    else:
        return True
def start_save():
    global folder
    if not os.path.exists(folder):
       os.makedirs(folder)
def save_comments():
    global folder
    if test_user():
        if not os.path.exists(folder):
            os.makedirs(folder)
        user_id = id_entry.get()
        notes = notes_entry.get()
        with open((folder +sep+ user_id +'_' + current_time +'NOTES.csv'), mode='a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([user_id, 'COMMENT', notes,get_local_time()])
        notes_save_button.config(state="disabled")  # disable the button
        notes_save_button.after(100, lambda: notes_save_button.config(state="normal"))
        notes_entry.delete(0, tk.END)
        
        

def save_pain():
    global folder
    user_id = id_entry.get()
    with open((folder +sep+ user_id +'_' + current_time +'NOTES.csv'), mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([user_id, 'FinalPain',pain_scale.get(), get_local_time()])
    pain_saved_label.config(text='Done')
        
        
def save_other(data1, data2):
    global folder
    user_id = id_entry.get()
    with open((folder +sep+ user_id +'_' + current_time +'NOTES.csv'), mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([user_id, data1, data2, get_local_time()])

    
def stream():
    #explore.acquire()
    explore.visualize( bp_freq=(1, 30), notch_freq=50)
    
def impeds(): 
    explore.measure_imp()



  
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
    if test_user():
        port_idx = port_listbox.curselection()[0] # Obtiene el índice de la selección actual
        port = port_listbox.get(port_idx) # Obtiene el puerto seleccionado en el índice
        baud_rate = 115200
        
        try:
            ser = serial.Serial(port, baud_rate, timeout=0)
            status_label.config(text="TCS Connected to " + port)
            connect_button.config(state="disabled")
            disconnect_button.config(state="normal")
            notes_save_button.config(state="normal")  
            pain_save_button.config(state="normal")  
            SetTCSButt.config(state="normal")  
            plot_button.config(state="normal") 
            start_save()
            send_data('F') # stimulation time = 500ms
            time.sleep(0.05)
            send_data('F') # stimulation time = 500ms
            time.sleep(0.05)
            send_data('N320')
            time.sleep(0.05)
            send_data('D000300') # stimulation time = 10sç
            time.sleep(0.005)
            send_data('V01700')
            time.sleep(0.005)
            send_data('R01700')
            time.sleep(0.005)
            send_data('T255100')
            time.sleep(0.005)
            send_data('C0600')
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
    


def sendtemp():
    global dataS
    dataS = send_entryTCS.get()
    print(dataS)
    data = 'C0' +dataS+ '0'
    send_data(data)
    save_other('ChepsTemp',dataS)
    tempTCS_message.config(text = ('Current Temp: '+dataS+ 'C'))
    
def coldTest():
    global start_time
    cont = 0
    tWait = 30 
    start_time = time.time()
    while cont<=tWait:
        if (time.time()-start_time)>cont:
            tempTCS_message2.config(text=('Wait for:'+str(tWait-cont)))
            cont+=1
            tempTCS_message2.update_idletasks()
        root.update()
    

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
    ax.set_ylim([25, 61])

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
        
        
root = tk.Tk()
root.title("CHEPS EEG")
root.iconbitmap('painlessLogo.ico')


connect_frame = tk.Frame(root)
connect_frame.pack(padx=0, pady=1)
portEXP_frame = tk.LabelFrame(connect_frame, bd=1,text="Explorepy Connect",font=('calibri', 16), relief=tk.SOLID,pady=10, padx=10)
portEXP_frame.grid(row=1, column =0 , rowspan=3, columnspan=2, padx=5)
dev_label = tk.Label(portEXP_frame, text="EEG device:")
dev_label.grid(row=0, column =0, padx=5)
dev_name_entry = tk.Entry(portEXP_frame)
dev_name_entry.insert(0, dev_name)
dev_name_entry.grid(row=0, column =1, columnspan=2, padx=5)

connectEEG_button = tk.Button(portEXP_frame, text="Connect", command=lambda: connect_explore(dev_name_entry.get()))
connectEEG_button.grid(row=1, column =1, columnspan=2, padx=5)

id_frame = tk.LabelFrame(connect_frame, bd=1,text="Participant ID",font=('calibri', 16), relief=tk.SOLID,pady=5, padx=10)
id_frame.grid(row=0, column =0 , rowspan=1, columnspan=2, padx=5)

id_label = tk.Label(id_frame, text="Participant ID:")
id_label.grid(row=0, column =0, padx=1)
id_entry = tk.Entry(id_frame)
id_entry.grid(row=0, column =1, padx=1)


port_frame = tk.LabelFrame(connect_frame, bd=1,text="TCS connection",font=('calibri', 16), relief=tk.SOLID,pady=10, padx=10)
port_frame.grid(row=0, column =3 , rowspan=4, columnspan=4, padx=5)

# port_message = tk.Label(port_frame, text = ('Select de TCS port'), font=('calibri', 12))
# port_message.pack()

port_label = tk.Label(port_frame, text="Select TCS Port:")
port_label.grid(row=0, column = 0)

#port_listbox = tk.Listbox(port_frame, width=10, height=5)
port_listbox = tk.Listbox(port_frame, width=30, height=3, exportselection=False, relief=tk.RIDGE)
port_listbox.grid(row=0, column = 2)

port_scrollbar = tk.Scrollbar(port_frame, orient=tk.VERTICAL)
port_scrollbar.grid(row=0, column = 3)

port_listbox.config(yscrollcommand=port_scrollbar.set)
port_scrollbar.config(command=port_listbox.yview)

status_label = tk.Label(port_frame , text="TCS Not connected", bd=1, relief=tk.SUNKEN, anchor=tk.W)
status_label.grid(row=1, column = 0,  columnspan=3)


button_frame = tk.Frame(port_frame)
button_frame.grid(row=2, column = 0, columnspan=3)

connect_button = tk.Button(button_frame, text="Connect", command=connect)
connect_button.grid(row=2, column = 1)

disconnect_button = tk.Button(button_frame, text="Disconnect", command=disconnect, state="disabled")
disconnect_button.grid(row=2, column = 2)

refresh_button = tk.Button(button_frame, text="Refresh list", command=refresh)
refresh_button.grid(row=2, column = 3)


temps_frame = tk.LabelFrame(root, bd=1,text="CHEPs temperature",font=('calibri', 16), relief=tk.SOLID,pady=10, padx=10)
temps_frame.pack(padx=10)

tempTCS_m1 = tk.Label(temps_frame, text = ('New Temp:'), font=('calibri', 14))
tempTCS_m1.grid(row=0, column=0, padx=(5,0))
valuesTCS = list(range(55, 61))
send_varTCS = tk.StringVar()
send_varTCS.set(valuesTCS[5])  # set initial value to first item in list
send_entryTCS = tk.Spinbox(temps_frame, from_=55, to=60, increment=1, textvariable=send_varTCS, width=3)
send_entryTCS.grid(row=0, column=1, padx=(0,0))
SetTCSButt = tk.Button(temps_frame, text="Set New Temp", command=sendtemp,state="disabled")
SetTCSButt.grid(row=0, column=2, padx=(0,0))
tempTCS_message = tk.Label(temps_frame, text = ('Current Temp: 60C'), font=('calibri', 14))
tempTCS_message.grid(row=0, column=4, padx=(0,25))
tempTCS_message2 = tk.Label(temps_frame, text = ('Wait for:'), font=('calibri', 14), width=12)
tempTCS_message2.grid(row=0, column=5, padx=(25,5))
tempTCS_m2 = tk.Label(temps_frame, text = (u'If the stimulus is very painful, TCS-II temperature should be reduced by -1C.\n This process could be repeated until 55C is reached.'), font=('calibri', 12))
tempTCS_m2.grid(row=1, column=0, columnspan=5)


notes_frame = tk.LabelFrame(root, bd=1,text="Annotations",font=('calibri', 16), relief=tk.SOLID,pady=10, padx=10)
notes_frame.pack(padx=10, pady=10, fill=tk.X)
notes_label = tk.Label(notes_frame, text="Comments:", font=("Helvetica", 12))
notes_label.grid(row=0, column=0, padx=(0,5))
notes_entry = tk.Entry(notes_frame, width=70)
notes_entry.grid(row=0, column=1, columnspan=3, padx=(0,5))
notes_save_button = tk.Button(notes_frame, text="Save comments", command=save_comments,state="disabled")
notes_save_button.grid(row=0, column=4, padx=(0,5))
hand_m1 = tk.Label(notes_frame, text = "At the end of the test, the participant will rate (NRS) how painful the stimuli sequence was on average.", font=('calibri', 12))
hand_m1.grid(row=1, column=0, columnspan =4)
score_label = tk.Label(notes_frame, text="Pain level:", font=("Helvetica", 12))
score_label.grid(row=2, column=0, padx=(0,5))
pain_scale = tk.Scale(notes_frame, from_=0, to=10, length=300, orient=tk.HORIZONTAL, font=("Helvetica", 12))
pain_scale.grid(row=2, column=1,columnspan=2, padx=(0,5))
pain_save_button = tk.Button(notes_frame, text="Save Pain", command=save_pain,state="disabled")
pain_save_button.grid(row=2, column=3, padx=(0,5))
pain_saved_label = tk.Label(notes_frame, text="    ", font=("Helvetica", 12))
pain_saved_label.grid(row=2, column=4, padx=(0,5))

cronoFrame = tk.Frame(root)
cronoFrame.pack(padx=10, pady =10)
start_button = tk.Button(cronoFrame , text="Start", font=("Helvetica", 18),state=tk.DISABLED, command=start_rec)
start_button.grid(row=0, column=0, padx=(10,25), pady=5)

stop_button = tk.Button(cronoFrame , text="Stop", font=("Helvetica", 18), state=tk.DISABLED, command=stop_rec)
stop_button.grid(row=0, column=1, padx=(25,25), pady=5)

crono = tk.Label(cronoFrame, text=("Trials 0/" + str(eeg_trials)), font=("Helvetica", 18), width=30)
crono.grid(row=0, column=2, padx=(0,5), columnspan=2, sticky="e")

temps_frame = tk.Frame(root)
temps_frame.pack()
plot_button = tk.Button(temps_frame, text="Show Temps Plot", command=toggle_plot, state="disabled")
plot_button.grid(row=0, column=0, padx=(5,0))
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

refresh()

root.protocol("WM_DELETE_WINDOW", on_close)
root.mainloop()

    