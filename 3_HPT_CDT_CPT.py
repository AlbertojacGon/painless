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
from numpy import mean
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

incoming = ''

score_list = []
now = datetime.datetime.now()
current_time = now.strftime("%Y_%m_%d_%H_%M_%S")
folder = 'HPT_CDT_CPT'

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
        ser = serial.Serial(port, baud_rate, timeout=0)
        status_label.config(text="TCS Connected to " + port)
        connect_button.config(state="disabled")
        disconnect_button.config(state="normal")
        start_save()
        temps_message.config(text="HPT1")
        send_data('F') # stimulation time = 500ms
        time.sleep(0.05)
        send_data('F') # stimulation time = 500ms
        time.sleep(0.05)
        send_data('N320')
        time.sleep(0.05)

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
        user_id = id_entry.get()
        if not os.path.exists(folder):
            os.makedirs(folder)
        with open((folder +sep+ user_id +'_' + current_time +'HPT_CDT_CPT.csv'), mode='a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["participant_id", "TrialType", "meanTemp","ReactionTime","AllTemps", "datetime"])

def save_results(mTemp,RT,temps,concept):
    global folder
    user_id = id_entry.get()
    with open((folder +sep+ user_id +'_' + current_time +'HPT_CDT_CPT.csv'), mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([user_id, concept, mTemp,RT,temps, datetime.datetime.now().time()])



def CDT(trialN):
    global start_time
    send_data('D099990')
    time.sleep(0.003)
    send_data('V00010')
    time.sleep(0.003)
    send_data('C0000')
    time.sleep(0.005)
    send_data('R00080')
    time.sleep(0.005)
    send_data('L')
    time.sleep(0.005)
    T0 = time.time()
    cont = 1
    while True:
        send_data('K')
        time.sleep(0.003)
        pushbutton = read_data()
        T1 = time.time()-T0
        if pushbutton:
            pushbutton = int(pushbutton)
            if pushbutton == 1:
                curr_temps = update_temps()
                send_data('C0320')
                time.sleep(0.003)
                send_data('D000900')
                time.sleep(0.003)
                send_data('V01700')
                time.sleep(0.003)
                send_data('C0320')
                if trialN==1:
                    save_results(round(mean(curr_temps),2),T1, curr_temps, 'CDT1')
                    CDT1_label.config(text=("Temp: {:.1f}C".format(mean(curr_temps))))
                    start_time = time.time() + 5
                    countdown()
                elif trialN==2:
                    save_results(round(mean(curr_temps),2),T1, curr_temps, 'CDT2')
                    CDT2_label.config(text=("Temp: {:.1f}C".format(mean(curr_temps))))
                    start_time = time.time() + 5
                    countdown()
                elif trialN==3:
                    save_results(round(mean(curr_temps),2),T1, curr_temps, 'CDT3')
                    CDT3_label.config(text=("Temp: {:.1f}C".format(mean(curr_temps))))
                    start_time = time.time() + 5
                    countdown()
                tempCP_message.config(text=("Temp:"))
                break
        if T1>cont:
            curr_temps = update_temps()
            tempCP_message.config(text=("Temp: {:.1f}C".format(mean(curr_temps))))
            cont+=1
        root.update()


def CPT(trialN):
    global start_time
    send_data('D099990')
    time.sleep(0.003)
    send_data('V00010')
    time.sleep(0.003)
    send_data('C0000')
    time.sleep(0.005)
    send_data('R00080')
    time.sleep(0.005)
    send_data('L')
    time.sleep(0.005)
    T0 = time.time()
    cont = 1
    while True:
        send_data('K')
        time.sleep(0.003)
        pushbutton = read_data()
        T1 = time.time()-T0
        if pushbutton:
            pushbutton = int(pushbutton)
            if pushbutton == 1:
                curr_temps = update_temps()
                send_data('D009000')
                time.sleep(0.003)
                send_data('C0320')
                time.sleep(0.003)
                send_data('V00080')
                time.sleep(0.003)
                if trialN==1:
                    save_results(round(mean(curr_temps),2),T1, curr_temps, 'CPT1')
                    CPT1_label.config(text=("Temp: {:.1f}C".format(mean(curr_temps))))
                    start_time = time.time() + 5 + int((32-mean(curr_temps))/8)
                    countdown()
                elif trialN==2:
                    save_results(round(mean(curr_temps),2),T1, curr_temps, 'CPT2')
                    CPT2_label.config(text=("Temp: {:.1f}C".format(mean(curr_temps))))
                    start_time = time.time() + 5 + int((32-mean(curr_temps))/8)
                    countdown()
                elif trialN==3:
                    save_results(round(mean(curr_temps),2),T1, curr_temps, 'CPT3')
                    CPT3_label.config(text=("Temp: {:.1f}C".format(mean(curr_temps))))
                    temps_message.config(text="Done!")
                tempCP_message.config(text=("Temp:"))

                break
        if T1>cont:
            curr_temps = update_temps()
            tempCP_message.config(text=("Temp: {:.1f}C".format(mean(curr_temps))))
            cont+=1
        root.update()


def HPT(trialN):
    global start_time
    send_data('D099990')
    time.sleep(0.003)
    send_data('V00010')
    time.sleep(0.003)
    send_data('C0600')
    time.sleep(0.005)
    send_data('R00080')
    time.sleep(0.005)
    send_data('L')
    time.sleep(0.005)
    T0 = time.time()
    cont = 1
    while True:
        send_data('K')
        time.sleep(0.003)
        pushbutton = read_data()
        T1 = time.time()-T0
        if pushbutton:
            pushbutton = int(pushbutton)
            if pushbutton == 1:
                curr_temps = update_temps()
                send_data('D009000')
                time.sleep(0.003)
                send_data('C0320')
                time.sleep(0.003)
                send_data('V00080')
                time.sleep(0.003)
                if trialN==1:
                    save_results(round(mean(curr_temps),2),T1, curr_temps, 'HPT1')
                    HPT1_label.config(text=("Temp: {:.1f}C".format(mean(curr_temps))))
                    temps_message.config(text="Wait:")
                    start_time = time.time() + 5+ int((mean(curr_temps)-32)/8)
                    countdown()
                elif trialN==2:
                    save_results(round(mean(curr_temps),2),T1, curr_temps, 'HPT2')
                    HPT2_label.config(text=("Temp: {:.1f}C".format(mean(curr_temps))))
                    start_time = time.time() + 5+ int((mean(curr_temps)-32)/8)
                    countdown()
                elif trialN==3:
                    save_results(round(mean(curr_temps),2),T1, curr_temps, 'HPT3')
                    HPT3_label.config(text=("Temp: {:.1f}C".format(mean(curr_temps))))
                    start_time = time.time() + 120
                    countdown()
                tempCP_message.config(text=("Temp:"))
                break
        if T1>cont:
            curr_temps = update_temps()
            tempCP_message.config(text=("Temp: {:.1f}C".format(mean(curr_temps))))
            cont+=1
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
    ax.set_ylim([-1, 60])

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
root.minsize(width=750, height=250)
root.title("Heat Pain Threshold (HPT), Cold Detection Threshold (CDT) and Cold Pain Threshold (CPT)")

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
port_frame =tk.LabelFrame(ports_frame, bd=1,text="TCS connection",font=('calibri', 16), relief=tk.SOLID,pady=5, padx=10)
port_frame.grid(row=0, column = 2, rowspan=4, columnspan=4, padx=5)

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


R1_frame = tk.Frame(root)
R1_frame.pack(pady=(20,0))
# Heat Pain Threshold
HPT_label_frame = tk.LabelFrame(R1_frame, bd=1,text="1 Heat Pain Threshold",font=('calibri', 18), relief=tk.SOLID)
HPT_label_frame.grid(row=0, column = 0, rowspan=2, columnspan=3, padx=5)


send_buttonHPT1 = tk.Button(HPT_label_frame, text="Start Trial 1", command=lambda: HPT(1), state="normal")
send_buttonHPT1.grid(row=0, column = 0, padx=10)
send_buttonHPT2 = tk.Button(HPT_label_frame, text="Start Trial 2", command=lambda: HPT(2), state="normal")
send_buttonHPT2.grid(row=0, column = 1, padx=10)
send_buttonHPT3 = tk.Button(HPT_label_frame, text="Start Trial 3", command=lambda: HPT(3), state="normal")
send_buttonHPT3.grid(row=0, column = 2, padx=10)
HPT1_label = tk.Label(HPT_label_frame, font=('calibri', 12))
HPT1_label.grid(row=1, column = 0)
HPT2_label = tk.Label(HPT_label_frame, font=('calibri', 12))
HPT2_label.grid(row=1, column = 1)
HPT3_label = tk.Label(HPT_label_frame, font=('calibri', 12))
HPT3_label.grid(row=1, column = 2)





# Cold Detection Threshold
CDT_label_frame = tk.LabelFrame(R1_frame, bd=1,text="2 Cold Detection Threshold",font=('calibri', 18), relief=tk.SOLID)
CDT_label_frame.grid(row=0, column = 3, rowspan=2, columnspan=3, padx=5)

send_buttonCDT1 = tk.Button(CDT_label_frame, text="Start Trial 1", command=lambda: CDT(1), state="normal")
send_buttonCDT1.grid(row=0, column = 0, padx=10)
send_buttonCDT2 = tk.Button(CDT_label_frame, text="Start Trial 2", command=lambda: CDT(2), state="normal")
send_buttonCDT2.grid(row=0, column = 1, padx=10)
send_buttonCDT3 = tk.Button(CDT_label_frame, text="Start Trial 3", command=lambda: CDT(3), state="normal")
send_buttonCDT3.grid(row=0, column = 2, padx=10)
CDT1_label = tk.Label(CDT_label_frame, font=('calibri', 12))
CDT1_label.grid(row=1, column = 0)
CDT2_label = tk.Label(CDT_label_frame, font=('calibri', 12))
CDT2_label.grid(row=1, column = 1)
CDT3_label = tk.Label(CDT_label_frame, font=('calibri', 12))
CDT3_label.grid(row=1, column = 2)





# Cold Pain Threshold
CPT_label_frame = tk.LabelFrame(root, bd=1,text="3 Cold Pain Threshold",font=('calibri', 18), relief=tk.SOLID)
CPT_frame = tk.Frame(CPT_label_frame)

send_frameCPT = tk.Frame(CPT_frame)
send_frameCPT.pack()

send_buttonCPT1 = tk.Button(send_frameCPT, text="Start Trial 1", command=lambda: CPT(1), state="normal")
send_buttonCPT1.grid(row=0, column = 0, padx=10)
send_buttonCPT2 = tk.Button(send_frameCPT, text="Start Trial 2", command=lambda: CPT(2), state="normal")
send_buttonCPT2.grid(row=0, column = 1, padx=10)
send_buttonCPT3 = tk.Button(send_frameCPT, text="Start Trial 3", command=lambda: CPT(3), state="normal")
send_buttonCPT3.grid(row=0, column = 2, padx=10)
CPT1_label = tk.Label(send_frameCPT, font=('calibri', 12))
CPT1_label.grid(row=1, column = 0)
CPT2_label = tk.Label(send_frameCPT, font=('calibri', 12))
CPT2_label.grid(row=1, column = 1)
CPT3_label = tk.Label(send_frameCPT, font=('calibri', 12))
CPT3_label.grid(row=1, column = 2)

CPT_frame.pack()
CPT_label_frame.pack(padx=10, pady=1)

save_frame = tk.Frame(root, width=500, height=100)
save_frame.pack( padx=10, pady=1)

temps_message = tk.Label(save_frame, text = ('Write Participant ID and Connect TCS (pushbutton should be connected to the TCS)'), font=('calibri', 14))
#temps_message.pack(side=tk.LEFT)
temps_message.grid(row=0, column=0, padx=(0,35), pady=5, sticky='w')
countdown_label = tk.Label(save_frame, text='', font=('calibri', 16))
#countdown_label.pack(side=tk.RIGHT)
countdown_label.grid(row=0, column=1, padx=(100,0), pady=1, sticky='e')

temps_frame = tk.Frame(root)
temps_frame.pack()


tempCP_message = tk.Label(temps_frame, text = ('Temp:'), font=('calibri', 16))
#temps_message.pack(side=tk.LEFT)
tempCP_message.grid(row=0, column=0, padx=(0,35), pady=1, sticky='w')
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
root.protocol("WM_DELETE_WINDOW", on_close)
root.mainloop()
