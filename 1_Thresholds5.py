



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
score_list = []
now = datetime.datetime.now()
current_time = now.strftime("%Y_%m_%d_%H_%M_%S")
startTempTSP = 45 # for TSP
startTempCPM = 45 # for CPM
CPMVal =[]
TSPVal =[]
folder = 'Thresholds'

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
        status_label.config(text="Connected to " + port)
        connect_button.config(state="disabled")
        disconnect_button.config(state="normal")
        send_buttonTSP.config(state="normal")
        send_buttonCPM.config(state="normal")
        famiC_button.config(state="normal")
        famiH_button.config(state="normal")
        save_buttonTSP.config(state="normal")
        save_buttonTSPT1.config(state="normal")
        save_buttonTSPT2.config(state="normal")
        save_buttonCPM.config(state="normal")
        save_buttonCPMT1.config(state="normal")
        save_buttonCPMT2.config(state="normal")
        temps_message.config(text="Next step: TSP Threshold 1")
        send_data('F') # stimulation time = 500ms
        time.sleep(0.05)
        send_data('F') # stimulation time = 500ms
        time.sleep(0.005)
        send_data('D000500') # stimulation time = 500ms
        time.sleep(0.005)
        send_data('C0450')
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
            countdown_label.config(text='Wait:{:.1f} s'.format(remaining_time))
            countdown_label.after(1000, countdown)

def reset_countdown():
    global start_time
    start_time = None
    countdown_label.config(text='')
    

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
        with open(( folder +sep+ user_id +'_' + current_time +'.csv'), mode='a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["participant_id", "TrialType", "Temp","datetime"])  
            
def save_results(data1,concept):
    global folder
    user_id = id_entry.get()
    with open((folder +sep+ user_id +'_' + current_time +'.csv'), mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([user_id, concept, data1, datetime.datetime.now().time()])     

def send_tempsFC():
    global ser
    global start_time
    dataS = famiC_var.get()
    if int(dataS)<10:
        dataS = '0' + dataS
    data = 'C0' +dataS+ '0'
    send_data(data)   
    time.sleep(0.1)
    send_data('D005000') # stimulation time = 10s
    time.sleep(0.1)
    send_data('L')
    famiC_button.config(state="disabled")  # disable the button
    start_time = time.time() + 5
    countdown()
    famiC_button.after(4000, lambda: famiC_button.config(state="normal"))  # enable the button after 500 ms

def send_tempsFH():
    global ser
    global start_time
    dataS = famiH_var.get()
    if int(dataS)<10:
        dataS = '0' + dataS
    data = 'C0' +dataS+ '0'
    send_data(data)   
    time.sleep(0.1)
    send_data('D005000') # stimulation time = 5s
    time.sleep(0.1)
    send_data('L')
    start_time = time.time() + 5
    countdown()
    famiH_button.config(state="disabled")  # disable the button
    famiH_button.after(4000, lambda: famiH_button.config(state="normal"))


    
def send_tempsTSP():
    global ser
    dataS = send_varTSP.get()
    if int(dataS)<10:
        dataS = '0' + dataS
    data = 'C0' +dataS+ '0'
    send_data(data)   
    time.sleep(0.01)
    send_data('D000500') # stimulation time = 5s
    time.sleep(0.01)
    send_data('L')
    save_tempTSP()
    send_buttonTSP.config(state="disabled")
    save_buttonTSP.config(state="normal")  # disable the button
    send_buttonTSP.after(500, lambda: send_buttonTSP.config(state="normal"))  # enable the button after 500 ms
    

def send_tempsCPM():
    global ser
    dataS = send_varCPM.get()
    if int(dataS)<10:
        dataS = '0' + dataS
    data = 'C0' +dataS+ '0'
    send_data(data)   
    time.sleep(0.01)
    send_data('D010000') # stimulation time = 5s
    time.sleep(0.01)
    send_data('L')
    save_tempCPM()
    send_buttonCPM.config(state="disabled")
    save_buttonCPM.config(state="normal")  # disable the button
    send_buttonCPM.after(9000, lambda: send_buttonCPM.config(state="normal"))  # enable the button after 500 ms
    


def save_tempTSP():
    global start_time
    if test_user():
        save_results(send_varTSP.get(),'tempTSP')
        start_time = time.time() + 5
        countdown()
def save_tempCPM():
    global start_time
    if test_user():
        save_results(send_varCPM.get(),'tempCPM')
        start_time = time.time() + 10
        countdown()
        
        
def save_scoreTSP():
    global startTempTSP
    if test_user():
        save_results(score_scaleTSP.get(),'vasTSP')
        send_labelTSP.config(text='Previous Temp:'+ str(send_varTSP.get())+ 'C;    Next:')
        save_buttonTSP.config(state="disabled")  # disable the button
        #save_button0.after(200, lambda: save_button0.config(state="normal"))  # enable the button after 500 ms
        if score_scaleTSP.get()<5: 
            startTempTSP= int(send_varTSP.get())+1
        elif score_scaleTSP.get()>5: 
            startTempTSP= int(send_varTSP.get())-1   
        send_varTSP.set(valuesTSP[startTempTSP-5])
           
    
def save_scoreTSPT1():
    global start_time
    if test_user():
        save_buttonTSPT1.config(state="disabled")
        temps_labelTSPT1.config(text='TSP T1: '+ send_varTSP.get()+ ' C')
        save_results(send_varTSP.get(),'TSP_threshold1')
        temps_message.config(text="Next Step: CPM Threshold 1") 
        TSPVal.append(int(send_varTSP.get()))
        startTempTSP =45 #reset temp
        send_varTSP.set(valuesTSP[startTempTSP-5])
        start_time = time.time() + 90
        countdown()
        
def save_scoreTSPT2():
    global start_time
    if test_user():
        save_buttonTSPT2.config(state="disabled")
        temps_labelTSPT2.config(text='TSP T2: ' + send_varTSP.get() +' C')
        save_results(send_varTSP.get(),'TSP_threshold2')
        temps_message.config(text="Next Step: CPM Threshold 2") 
        TSPVal.append(int(send_varTSP.get()))
        m1 = sum(TSPVal)/2
        temps_labelmeanTSP.config(text='Mean TSP: ' + str(m1) +' C')
        start_time = time.time() + 90
        countdown()
        

def save_scoreCPM():
    global startTempCPM
    if test_user():
        save_results(score_scaleCPM.get(),'vasCPM')
        send_labelCPM.config(text='Previous Temp:'+ str(send_varCPM.get())+ 'C;    Next:')
        save_buttonCPM.config(state="disabled")  # disable the button
        #save_button0.after(200, lambda: save_button0.config(state="normal"))  # enable the button after 500 ms
        if score_scaleCPM.get()<5: 
            startTempCPM = int(send_varCPM.get())+1
        elif score_scaleCPM.get()>5: 
            startTempCPM = int(send_varCPM.get())-1   
        send_varCPM.set(valuesCPM[startTempCPM-5])
        
def save_scoreCPMT1():
    global start_time
    if test_user():
        save_buttonCPMT1.config(state="disabled")
        temps_labelCPMT1.config(text='CPM T1: '+ send_varCPM.get()+ ' C')
        save_results(send_varCPM.get(),'CPM_threshold1')
        temps_message.config(text="Next Step: TSP Threshold 2") 
        CPMVal.append(int(send_varCPM.get()))
        startTempCPM =45 #reset temp
        send_varCPM.set(valuesCPM[startTempCPM-5])
        start_time = time.time() + 90
        countdown()
def save_scoreCPMT2():
    if test_user():
        save_buttonCPMT2.config(state="disabled")
        temps_labelCPMT2.config(text='CPM T2: ' + send_varCPM.get() +' C')
        save_results(send_varCPM.get(),'CPM_threshold2')
        CPMVal.append(int(send_varCPM.get()))
        m2 = sum(CPMVal)/2
        temps_labelmeanCPM.config(text='Mean CPM: ' + str(m2) +' C')
        temps_message.config(text="Finish!") 

        
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
    ax.set_ylim([0, 60])

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



root = tk.Tk()
root.title("Pain5 Thresholds")
root.iconbitmap('painlessLogo.ico')


container = tk.Frame(root, borderwidth=1, relief=tk.SOLID)
container.pack(fill=tk.BOTH, expand=True, padx=10, pady=1)

id_label = tk.Label(container, text="Participant ID:")
id_label.grid(row=0, column=0, padx=5, pady=5)

id_entry = tk.Entry(container)
id_entry.grid(row=0, column=1, padx=5, pady=5)

port_label = tk.Label(container, text="Select TCS Port:")
port_label.grid(row=0, column=2, padx=5, pady=5)

port_listbox = tk.Listbox(container, width=30, height=4, exportselection=False)
port_listbox.grid(row=0, column=3, columnspan=2, padx=5, pady=5)

port_scrollbar = tk.Scrollbar(container, orient=tk.VERTICAL)
port_scrollbar.grid(row=0, column=5, padx=5, pady=5, sticky=tk.NS)

port_listbox.config(yscrollcommand=port_scrollbar.set)
port_scrollbar.config(command=port_listbox.yview)

status_label = tk.Label(container, text="Not connected", bd=1, relief=tk.SUNKEN, anchor=tk.W)
status_label.grid(row=1, column=2, columnspan=3, padx=5, pady=1, sticky=tk.W+tk.E)

connect_button = tk.Button(container, text="Connect", command=connect)
connect_button.grid(row=2, column=2, padx=5, pady=1, sticky=tk.W)

disconnect_button = tk.Button(container, text="Disconnect", command=disconnect, state="disabled")
disconnect_button.grid(row=2, column=3, padx=5, pady=1, sticky=tk.W)

refresh_button = tk.Button(container, text="Refresh list", command=refresh)
refresh_button.grid(row=2, column=4, padx=5, pady=1, sticky=tk.E)







# familiarization
fami_label_frame = tk.LabelFrame(root, bd=1,text="Familiarization", font=('calibri', 18), relief=tk.SOLID)
fami_frame = tk.Frame(fami_label_frame)

famiC_label = tk.Label(fami_frame, text="Cold:", width=5, pady=1)
famiC_label.pack(side=tk.LEFT)
valuesFC = list(range(0, 20))
famiC_var = tk.StringVar()
famiC_var.set(valuesFC[0])  
famiC_entry = tk.Spinbox(fami_frame, from_=0, to=20, increment=1, textvariable=famiC_var, width=3)
famiC_entry.pack(side=tk.LEFT)
famiC_button = tk.Button(fami_frame, text="Stimulate!", command=send_tempsFC, state="disabled")
famiC_button.pack(side=tk.LEFT)

famiH_label = tk.Label(fami_frame, text="Heat:", width=5)
famiH_label.pack(side=tk.LEFT, padx=(40, 0))
valuesFH = list(range(40, 50))
famiH_var = tk.StringVar()
famiH_var.set(valuesFH[5])  
famiH_entry = tk.Spinbox(fami_frame, from_=40, to=50, increment=1, textvariable=famiH_var, width=3)
famiH_entry.pack(side=tk.LEFT)
famiH_button = tk.Button(fami_frame, text="Stimulate!", command=send_tempsFH, state="disabled")
famiH_button.pack(side=tk.LEFT)
fami_frame.pack()
fami_label_frame.pack(padx=10, pady=3)




## threshold 5 TSP
t5TSP_label_frame = tk.LabelFrame(root, bd=1,text="T5 TSP",font=('calibri', 18), relief=tk.SOLID)
t5TSP_frame = tk.Frame(t5TSP_label_frame)


send_labelTSP = tk.Label(t5TSP_frame, text="Next Temperature:", width=22)
send_labelTSP.grid(row=0, column=0,columnspan=1)
valuesTSP = list(range(5, 60))
send_varTSP = tk.StringVar()
send_varTSP.set(valuesTSP[startTempTSP-5])  # set initial value to first item in list

send_entryTSP = tk.Spinbox(t5TSP_frame, from_=5, to=60, increment=1, textvariable=send_varTSP, width=3)
send_entryTSP.grid(row=0, column=1)
send_buttonTSP = tk.Button(t5TSP_frame, text="Stimulate!", command=send_tempsTSP, state="disabled", font=('calibri', 12))
send_buttonTSP.grid(row=0, column=2)

score_labelTSP = tk.Label(t5TSP_frame, text="Pain Score:")
score_labelTSP.grid(row=1, column=0)
score_scaleTSP = tk.Scale(t5TSP_frame, from_=0, to=10, length=300, orient=tk.HORIZONTAL)
score_scaleTSP.grid(row=1, column=1,columnspan=3)
save_buttonTSP = tk.Button(t5TSP_frame, text="Save Pain Score", command=save_scoreTSP, state="disabled")
save_buttonTSP.grid(row=1, column=4)
save_buttonTSPT1 = tk.Button(t5TSP_frame, text="Save Thres 1", command=save_scoreTSPT1, state="disabled")
save_buttonTSPT1.grid(row=0, column=5, padx=(20,0))
temps_labelTSPT1 = tk.Label(t5TSP_frame,text="", font=('calibri', 12),width=12)
temps_labelTSPT1.grid(row=0, column=6)
save_buttonTSPT2 = tk.Button(t5TSP_frame, text="Save Thres 2", command=save_scoreTSPT2, state="disabled")
save_buttonTSPT2.grid(row=1, column=5, padx=(20,0))
temps_labelTSPT2 = tk.Label(t5TSP_frame,font=('calibri', 12),width=12)
temps_labelTSPT2.grid(row=1, column=6)
temps_labelmeanTSP = tk.Label(t5TSP_frame,font=('calibri', 12),width=18)
temps_labelmeanTSP.grid(row=1, column=7)
t5TSP_frame.pack()
t5TSP_label_frame.pack(padx=10)




## threshold 5 CPM
t5CPM_label_frame = tk.LabelFrame(root, bd=1,text="T5 CPM and OA", font=('calibri', 18), relief=tk.SOLID)
t5CPM_frame = tk.Frame(t5CPM_label_frame)
send_labelCPM = tk.Label(t5CPM_frame, text="Next Temperature:", width=22)
send_labelCPM.grid(row=0, column=0,columnspan=1)
valuesCPM = list(range(5, 60))
send_varCPM = tk.StringVar()
send_varCPM.set(valuesCPM[startTempCPM-5])  # set initial value to first item in list
send_entryCPM = tk.Spinbox(t5CPM_frame, from_=5, to=60, increment=1, textvariable=send_varCPM, width=3)
send_entryCPM.grid(row=0, column=1)
send_buttonCPM = tk.Button(t5CPM_frame, text="Stimulate!", command=send_tempsCPM, state="disabled", font=('calibri', 12))
send_buttonCPM.grid(row=0, column=2)
score_labelCPM = tk.Label(t5CPM_frame, text="Pain Score:")
score_labelCPM.grid(row=1, column=0)
score_scaleCPM = tk.Scale(t5CPM_frame, from_=0, to=10, length=300, orient=tk.HORIZONTAL)
score_scaleCPM.grid(row=1, column=1,columnspan=3)
save_buttonCPM = tk.Button(t5CPM_frame, text="Save Pain Score", command=save_scoreCPM, state="disabled")
save_buttonCPM.grid(row=1, column=4)
save_buttonCPMT1 = tk.Button(t5CPM_frame, text="Save Thres 1", command=save_scoreCPMT1, state="disabled")
save_buttonCPMT1.grid(row=0, column=5, padx=(20,0))
save_buttonCPMT2 = tk.Button(t5CPM_frame, text="Save Thres 2", command=save_scoreCPMT2, state="disabled")
save_buttonCPMT2.grid(row=1, column=5, padx=(20,0))
temps_labelCPMT1 = tk.Label(t5CPM_frame,font=('calibri', 12),width=12)
temps_labelCPMT1.grid(row=0, column=6)
temps_labelCPMT2 = tk.Label(t5CPM_frame,font=('calibri', 12),width=12)
temps_labelCPMT2.grid(row=1, column=6)
temps_labelmeanCPM = tk.Label(t5CPM_frame,font=('calibri', 12),width=18)
temps_labelmeanCPM.grid(row=1, column=7)
t5CPM_frame.pack()
t5CPM_label_frame.pack(padx=10)


save_frame = tk.Frame(root, width=500, height=100)
save_frame.pack( padx=10, pady=5)


temps_message = tk.Label(save_frame, text = ('Next Step: Enter participantID and connect TCS'), font=('calibri', 16))
#temps_message.pack(side=tk.LEFT)
temps_message.grid(row=0, column=0, padx=(0,35), pady=5, sticky='w')
countdown_label = tk.Label(save_frame, text='', font=('calibri', 16))
#countdown_label.pack(side=tk.RIGHT)
countdown_label.grid(row=0, column=1, padx=(100,0), pady=5, sticky='e')

temps_frame = tk.Frame(root)
temps_frame.pack()







plot_button = tk.Button(temps_frame, text="Show Temps Plot", command=toggle_plot, state="normal")
plot_button.grid(row=0, column=0, padx=10)
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




