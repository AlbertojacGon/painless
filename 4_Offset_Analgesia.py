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
incomingVAS = ''
score_list = []
now = datetime.datetime.now()
current_time = now.strftime("%Y_%m_%d_%H_%M_%S")
start_time = time.time()
folder = 'OffsetAnalgesia'

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
        if ser is not None and serVAS is not None:
            fam_button.config(state="normal")
            control_button.config(state="normal")
            offset_button.config(state="normal")
        temps_message.config(text="Connect eVAS")
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
        
        
def connectVAS():
    global start_time
    global ser
    global serVAS
    portVAS_idx = portVAS_listbox.curselection()[0] # Obtiene el índice de la selección actual
    portVAS = portVAS_listbox.get(portVAS_idx) # Obtiene el puerto seleccionado en el índice
    baud_rate = 115200
    try:
        serVAS = serial.Serial(portVAS, baud_rate, timeout=0)
        statusVAS_label.config(text="eVAS Connected to " + portVAS)
        connectVAS_button.config(state="disabled")
        disconnectVAS_button.config(state="normal")  
        if ser is not None and serVAS is not None:
            fam_button.config(state="normal")
            control_button.config(state="normal")
            offset_button.config(state="normal")
        time.sleep(0.005)
        if ser.inWaiting():
            while ser.inWaiting():
                serVAS.read()
        start_time = time.time()
        temps_message.config(text="Select the correct OA Pain5 temp and start familiarization")
        
    except serial.SerialException:
        statusVAS_label.config(text="Error: Could not connect to " + portVAS)

def disconnectVAS():
    global serVAS
    if serVAS is not None and serVAS.isOpen():
        serVAS.close()
        statusVAS_label.config(text="Disconnected from " + serVAS.port)
        connectVAS_button.config(state="normal")
        disconnectVAS_button.config(state="disabled")
        serVAS = None

def refreshVAS():
    portsVAS = serial.tools.list_ports.comports()
    portVAS_listbox.delete(0, tk.END)
    for portVAS, desc, hwid in sorted(portsVAS):
        portVAS_listbox.insert(tk.END, portVAS)
        
def on_close():
    if ser:
        ser.close()
    if serVAS:
        serVAS.close()
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
    

def update_temps():
    global incoming
    if ser is not None and ser.isOpen():
        try:
            ser.write('E'.encode())
            time.sleep(.02)
            incoming = ser.read(1000)   
            
            temps_read = [float(x)/10 for x in incoming.decode().split('+')]
            temps_read = temps_read[1:6]
            if len(temps_read)==5:       
                return(temps_read)
            else:
                return([0,0,0,0,0])
        except: return([0,0,0,0,0])
    
    
def update_VAS():
    global incomingVAS
    if serVAS is not None and serVAS.isOpen():
        incomingVAS = serVAS.readline().decode()
        if incomingVAS:
            valVas = incomingVAS.strip()
            if valVas=='L' or valVas=='C' or valVas=='R':
                valVas=''
            if valVas:
                valVas = int(valVas)
                save_results('','VAS',time.time()-start_time,valVas)
                if valVas!=999:
                    tempCP_message.config(text = ("VAS Value: " + str(valVas)))
    root.after(1, update_VAS)
    
    
def test_user():
    user_id = id_entry.get()
    if user_id == '':
        tk.messagebox.showerror("Error", "Please enter an ID and then connect")
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
        with open((folder +sep+ user_id +'_' + current_time +'.csv'), mode='a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["participant_id", "TrialType", "Temp", "VAS", "Time"])  
            
def save_results(temp,concept,time,vas):
    global folder
    user_id = id_entry.get()
    with open((folder +sep+ user_id +'_' + current_time +'.csv'), mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([user_id, concept, temp, vas, time])     



    
def stimFami():
    global ser
    global start_time    
    fam_button.config(state="disabled")
    control_button.config(state="disabled")
    offset_button.config(state="disabled")
    dataS = float(temp_spinbox.get())

    dataS = dataS-2
    datstr = str(dataS).replace('.','')
    data = 'C0' +datstr
    send_data(data)   
    time.sleep(0.003)
    send_data('D010000') # stimulation time = 10s
    time.sleep(0.003)
    send_data('L')
    #save_tempTSP()
    StartOAtime = time.time()
    start_time = time.time()
    save_results(dataS,'Familiarization',time.time()-start_time,'')
    temps_message.config(text=("Familiarization. Rate pain continuously. Temp:" + str(dataS)+ "C")) 
    cont = 0
    tWait = 10 
    while cont<=tWait:
        if (time.time()- StartOAtime)>cont:
            countdown_label.config(text=str(tWait-cont))
            cont+=1
            countdown_label.update_idletasks()
        root.update()
    info_fam_label.config(text="Done")
    fam_button.config(state="normal")
    control_button.config(state="normal")
    offset_button.config(state="normal")
    
def stimControl():
    global ser
    global start_time    
    fam_button.config(state="disabled")
    control_button.config(state="disabled")
    offset_button.config(state="disabled")
    dataS = float(temp_spinbox.get())
    datstr = str(dataS).replace('.','')
    data = 'C0' +datstr
    send_data(data)   
    time.sleep(0.003)
    send_data('D030000') # stimulation time = 30s
    time.sleep(0.003)
    send_data('L')
    #save_tempTSP()
    StartOAtime = time.time()
    start_time = time.time()
    save_results(dataS,'Control',time.time()-start_time,'')
    temps_message.config(text=("Control. Rate pain continuously. Temp:" + str(dataS)+ "C")) 
    cont = 0
    tWait = 30 
    while cont<=tWait:
        if (time.time()- StartOAtime)>cont:
            countdown_label.config(text=str(tWait-cont))
            cont+=1
            countdown_label.update_idletasks()
        root.update()
    info_ctr_label.config(text="Done")
    fam_button.config(state="normal")
    control_button.config(state="normal")
    offset_button.config(state="normal")
    

def stimOA():
    global ser
    global start_time    
    fam_button.config(state="disabled")
    control_button.config(state="disabled")
    offset_button.config(state="disabled")
    dataS = float(temp_spinbox.get())
    datstr = str(dataS).replace('.','')
    data = 'C0' +datstr
    send_data(data)   
    time.sleep(0.003)
    send_data('D020500') # stimulation time = 5s, here will be controlled by tWait
    time.sleep(0.003)
    send_data('L')

    StartOAtime = time.time()
    start_time = time.time()
    save_results(dataS,'OA_Pre',time.time()-start_time,'')
    temps_message.config(text="OA. Rate pain continuously. Temp: " + str(dataS)+ "C") 
    cont = 0
    tWait = 5 
    while cont<=tWait:
        if (time.time()- StartOAtime+.4)>cont:
            countdown_label.config(text=str(tWait-cont))
            cont+=1
            countdown_label.update_idletasks()
        root.update()
        
    dataS = dataS+1
    datstr = str(dataS).replace('.','')
    data = 'C0' +datstr
    send_data(data)   
    time.sleep(0.003)
    while (time.time()- StartOAtime+.01)<tWait:
        root.update()
        
    send_data('L')
    save_results(dataS,'OA+1',time.time()-start_time,'')
    temps_message.config(text="OA+1C. Rate pain continuously. Temp: " + str(dataS)+ "C") 
    cont = 5
    tWait = 10
    while cont<=tWait:
        if (time.time()- StartOAtime+.2)>cont:
            countdown_label.config(text=str(tWait-cont))
            cont+=1
            countdown_label.update_idletasks()
        root.update()
    
    dataS = dataS-1
    datstr = str(dataS).replace('.','')
    data = 'C0' +datstr
    send_data(data)   
    time.sleep(0.003)
    while (time.time()- StartOAtime+.01)<tWait:
        root.update()
    send_data('L')
    save_results(dataS,'OA_Post',time.time()-start_time,'')
    temps_message.config(text="OA. Rate pain continuously. Temp: " + str(dataS)+ "C") 
    cont = 10
    tWait = 30 
    while cont<=tWait:
        if (time.time()- StartOAtime+.2)>cont:
            countdown_label.config(text=str(tWait-cont))
            cont+=1
            countdown_label.update_idletasks()
        root.update()
    send_data('C0320')   
    time.sleep(0.003)
    while (time.time()- StartOAtime+.01)<tWait:
        root.update()
    send_data('L')
    save_results(dataS,'OA_END',time.time()-start_time,'')
    info_oa_label.config(text="Done")
    temps_message.config(text="OA Finished") 
    fam_button.config(state="normal")
    control_button.config(state="normal")
    offset_button.config(state="normal")



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
serVAS = None


root = tk.Tk()
root.title("Offset Analgesia")

# logo
# icono = tk.PhotoImage(file='painlessLogo.png')
# root.iconphoto(False, icono)
root.iconbitmap('painlessLogo.ico')



id_frame = tk.Frame(root, borderwidth=1, relief=tk.SOLID,pady=10, padx=10)
id_frame.pack(pady=10)

id_label = tk.Label(id_frame, text="Participant ID:")
id_label.grid(row=0,column=0)
id_entry = tk.Entry(id_frame)
id_entry.grid(row=0,column=1)





port_var = tk.StringVar()

ports_frame = tk.Frame(root)
ports_frame.pack()
port_frame =tk.LabelFrame(ports_frame, bd=1,text="TCS connection",font=('calibri', 16), relief=tk.SOLID,pady=10, padx=10)
port_frame.grid(row=0, column = 0, rowspan=4, columnspan=4, padx=5)

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


# connect to EVAS

portVAS_var = tk.StringVar()


portVAS_frame = tk.LabelFrame(ports_frame, bd=1,text="eVAS connection",font=('calibri', 16), relief=tk.SOLID,pady=10, padx=10)
portVAS_frame.grid(row=0, column = 4, rowspan=4, columnspan=4, padx=5)


portVAS_label = tk.Label(portVAS_frame, text="Select eVAS Port:")
portVAS_label.grid(row=0, column = 0)

portVAS_listbox = tk.Listbox(portVAS_frame, width=30, height=3, exportselection=False, relief=tk.RIDGE)
portVAS_listbox.grid(row=0, column = 2)

portVAS_scrollbar = tk.Scrollbar(portVAS_frame, orient=tk.VERTICAL)
portVAS_scrollbar.grid(row=0, column = 3)

portVAS_listbox.config(yscrollcommand=portVAS_scrollbar.set)
portVAS_scrollbar.config(command=portVAS_listbox.yview)

statusVAS_label = tk.Label(portVAS_frame , text="eVAS Not connected", bd=1, relief=tk.SUNKEN, anchor=tk.W)
statusVAS_label.grid(row=1, column = 0,  columnspan=3)


buttonVAS_frame = tk.Frame(portVAS_frame)
buttonVAS_frame.grid(row=2, column = 0, columnspan=3)

connectVAS_button = tk.Button(buttonVAS_frame, text="Connect", command=connectVAS)
connectVAS_button.grid(row=2, column = 1)

disconnectVAS_button = tk.Button(buttonVAS_frame, text="Disconnect", command=disconnectVAS, state="disabled")
disconnectVAS_button.grid(row=2, column = 2)

refreshVAS_button = tk.Button(buttonVAS_frame, text="Refresh list", command=refreshVAS)
refreshVAS_button.grid(row=2, column = 3)



container = tk.Frame(root, borderwidth=1, relief=tk.SOLID)
container.pack(fill=tk.BOTH, expand=True, padx=15, pady=5)


temp_label = tk.Label(container, text="Select the OA temp",font=('calibri', 12))
info_label = tk.Label(container, text="Note: For Familiarization the temp will be automatically reduced 2C")
info_fam_label = tk.Label(container,font=('calibri', 12))
info_oa_label = tk.Label(container,font=('calibri', 12))
info_ctr_label = tk.Label(container,font=('calibri', 12))
t_var= tk.StringVar(container)
t_var.set("45.0")
temp_spinbox = tk.Spinbox(container, from_=30, to=65, increment=0.5, width=4, textvariable= t_var)

fam_button = tk.Button(container, text="Start Familiarization", command=stimFami, state="disabled",width=18)
control_button = tk.Button(container, text="Start Control", command=stimControl, state="disabled",width=18)
offset_button = tk.Button(container, text="Start Offset Analgesia" , command=stimOA, state="disabled",width=18)

# Add labels and widgets to grid
temp_label.grid(row=0, column=0)
temp_spinbox.grid(row=0, column=1)
info_label.grid(row=0, column=2,columnspan=3)
fam_button.grid(row=1, column=0,padx=10, pady=(15,5))
info_fam_label.grid(row=2, column=0)
control_button.grid(row=1, column=1,padx=10, pady=(15,5))
info_ctr_label.grid(row=2, column=1)
offset_button.grid(row=1, column=2,padx=10, pady=(15,5))
info_oa_label.grid(row=2, column=2)


save_frame = tk.Frame(root)
save_frame.pack( padx=10, pady=2)


temps_message = tk.Label(save_frame, text = ('Write Participant ID and Connect TCS'), font=('calibri', 16),  width = 60)
temps_message.grid(row=0, column=0, columnspan=3, padx=(0,35), pady=5, sticky='w')
countdown_label = tk.Label(save_frame, text='', font=('calibri', 16),  width = 6)
countdown_label.grid(row=0, column=3, padx=(100,0), pady=5, sticky='e')


temps_frame = tk.Frame(root)
temps_frame.pack()

tempCP_message = tk.Label(temps_frame, text = ('VAS Value:'), font=('calibri', 14),  width = 14)
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
refresh()
refreshVAS()
update_VAS()
root.protocol("WM_DELETE_WINDOW", on_close)
root.mainloop()

