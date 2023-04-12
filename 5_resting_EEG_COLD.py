#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Feb 15 22:31:21 2023

@author: albertogonzalezv
"""

import explorepy
import serial
import csv,os, time
import tkinter as tk
from datetime import datetime
from os import sep
import serial.tools.list_ports
from explorepy.tools import get_local_time


eeg_duration = 300
dev_name = "Explore_8532"
folder = "Resting_EEG_Cold"

now = datetime.now()
current_time = now.strftime("%Y_%m_%d_%H_%M_%S")
explore = None
serCPM = None

time_cont = 0
STOP =0
incomingCPM = []
# connect
def connect_explore(dev_name):
    
    global explore
    explore = explorepy.Explore()
    explorepy.set_bt_interface('sdk')
    explore.connect(device_name=dev_name_entry.get())
    
    eeg_dev = True
    if eeg_dev:
        connect_button.config(state=tk.DISABLED)
        start_button.config(state="normal")

def on_close():
    global explore
    if explore:
        explore.disconnect()
    if serCPM:
        serCPM.close()
    root.destroy()
    
def start_rec():
    global folder, STOP, time_cont
    if test_user():
        user_id = id_entry.get()
        explore.record_data(file_name=(folder + sep + user_id + current_time+'_' + str(time_cont)), duration=eeg_duration, file_type='csv')
        stop_button.config(state="normal")
        start_button.config(state="disabled")
        STOP = False
        while time_cont<eeg_duration:
            t0=time.time()
            if not STOP:
                while time.time()-t0<0.995:
                    root.update()
                    time.sleep(.001)
                time_cont+=1
                crono.config(text = ("Seconds " +str(time_cont) +'/'+str(eeg_duration)))
            else: break
            time.sleep(.001)
        

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
        
def save_handUp():
    global folder
    user_id = id_entry.get()
    with open((folder +sep+ user_id +'_' + current_time +'NOTES.csv'), mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([user_id, 'HAND UP', ' ',get_local_time()])
        handdwButt.config(state="normal")
        handupButt.config(state="disabled")
        

def save_handDw():
    global folder
    user_id = id_entry.get()
    with open((folder +sep+ user_id +'_' + current_time +'NOTES.csv'), mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([user_id, 'HAND DOWN',' ', get_local_time()])
        handdwButt.config(state="disabled")
        handupButt.config(state="normal")

def save_pain():
    global folder
    user_id = id_entry.get()
    with open((folder +sep+ user_id +'_' + current_time +'NOTES.csv'), mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([user_id, 'FinalPain', pain_scale.get() ,get_local_time()])
        pain_saved_label.config(text='Done')
        
def save_other(data1, data2):
    global folder
    user_id = id_entry.get()
    with open((folder +sep+ user_id +'_' + current_time +'NOTES.csv'), mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([user_id, data1, data2, get_local_time()])
        handdwButt.config(state="disabled")
        handupButt.config(state="normal")
    
def stream():
    #explore.acquire()
    explore.visualize( bp_freq=(1, 30), notch_freq=50)
    
def impeds(): 
    explore.measure_imp()



  
    
def send_dataCPM(data_out): # send by serial
    if serCPM!=False:
        for i in data_out:
            serCPM.write(i.encode())
            time.sleep(0.002)
    

def connectCPM():
    global serCPM
    if test_user():
        portCPM_idx = portCPM_listbox.curselection()[0] # Obtiene el índice de la selección actual
        portCPM = portCPM_listbox.get(portCPM_idx) # Obtiene el puerto seleccionado en el índice
        baud_rate = 115200
        try:
            serCPM = serial.Serial(portCPM, baud_rate)
            statusCPM_label.config(text="Cold Plate Connected to " + portCPM)
            connectCPM_button.config(state="disabled")
            disconnectCPM_button.config(state="normal")  
            SetCPButt.config(state="normal")  
            CPButt.config(state="normal")  
            handupButt.config(state="normal")  
            notes_save_button.config(state="normal")  
            pain_save_button.config(state="normal")  
            start_save()
            #send_buttonCPM.config(state="normal")
            send_dataCPM('C200') # temp to 20.0
            time.sleep(0.005)
            #temps_message.config(text="Select CPM Pain5 temp and wait for the Cold Plate to reach 10C") 
            
    
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
        
def update_tempsCPM():
    global incomingCPM, serCPM
    if serCPM is not None and serCPM.isOpen():
        serCPM.write('E'.encode())
        time.sleep(0.005)
        if serCPM.inWaiting():
            incomingCPM = ''
            while serCPM.inWaiting():
                incomingCPM = incomingCPM + serCPM.read().decode()
            temps_read = incomingCPM.split()
            temp = (float(temps_read[0])/10)
            tempCP_message.config(text=('Current Cold Plate Temp:'+ str(temp) + 'C'))
    root.after(1000, update_tempsCPM)
    
def change_tempsCPM(newtemp):
    send_dataCPM(('C'+str(newtemp)+'0')) # temp to 10.0
    time.sleep(0.005)

def sendCPtemp():
    dataS = send_entryCP.get()
    if int(dataS)<10:
        dataS = '0' + dataS
    data = 'C' +dataS+ '0'
    send_dataCPM(data)
    save_other('ColdPlateTemp',dataS)
    
def coldTest():
    global start_time
    cont = 0
    tWait = 30 
    start_time = time.time()
    while cont<=tWait:
        if (time.time()-start_time)>cont:
            tempCP_message2.config(text=('Wait for:'+str(tWait-cont)))
            cont+=1
            tempCP_message2.update_idletasks()
        root.update()
    

root = tk.Tk()
root.title("Resting EEG during Cold Pain")
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

connect_button = tk.Button(portEXP_frame, text="Connect", command=lambda: connect_explore(dev_name_entry.get()))
connect_button.grid(row=1, column =1, columnspan=2, padx=5)

id_frame = tk.LabelFrame(connect_frame, bd=1,text="Participant ID",font=('calibri', 16), relief=tk.SOLID,pady=5, padx=10)
id_frame.grid(row=0, column =0 , rowspan=1, columnspan=2, padx=5)

id_label = tk.Label(id_frame, text="Participant ID:")
id_label.grid(row=0, column =0, padx=1)
id_entry = tk.Entry(id_frame)
id_entry.grid(row=0, column =1, padx=1)


portCPM_frame = tk.LabelFrame(connect_frame, bd=1,text="Cold Plate connection",font=('calibri', 16), relief=tk.SOLID,pady=10, padx=10)
portCPM_frame.grid(row=0, column =3 , rowspan=4, columnspan=4, padx=5)

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


temps_frame = tk.LabelFrame(root, bd=1,text="Cold Plate temperature setting",font=('calibri', 16), relief=tk.SOLID,pady=10, padx=10)
temps_frame.pack(padx=10)

tempCP_m1 = tk.Label(temps_frame, text = ('Desired Cold Plate Temp:'), font=('calibri', 14))
tempCP_m1.grid(row=0, column=0, padx=(0,5))
valuesCP = list(range(2, 36))
send_varCP = tk.StringVar()
send_varCP.set(valuesCP[18])  # set initial value to first item in list
send_entryCP = tk.Spinbox(temps_frame, from_=2, to=36, increment=2, textvariable=send_varCP, width=3)
send_entryCP.grid(row=0, column=1, padx=(0,5))
SetCPButt = tk.Button(temps_frame, text="Set Temp", command=sendCPtemp,state="disabled")
SetCPButt.grid(row=0, column=2, padx=(0,5))
tempCP_message = tk.Label(temps_frame, text = ('Current Cold Plate Temp:'), font=('calibri', 14))
tempCP_message.grid(row=0, column=3, padx=(0,25))
CPButt = tk.Button(temps_frame, text="Start Cold Test", command=coldTest,state="disabled")
CPButt.grid(row=0, column=4, padx=(0,5))
tempCP_message2 = tk.Label(temps_frame, text = ('Wait for:'), font=('calibri', 14), width=12)
tempCP_message2.grid(row=0, column=5, padx=(25,5))
tempCP_m2 = tk.Label(temps_frame, text = ('If the pain intensity rating is higher than 5/10, increase the cold plate temperature by 2C (more warm). \nConversely, if the pain intensity rating is lower than 3/10, decrease the cold plate temperature by 2C (more cold). \nRepeat this process until the pain intensity is between 3/10 and 5/10'), font=('calibri', 12))
tempCP_m2.grid(row=1, column=0, columnspan=5)


notes_frame = tk.LabelFrame(root, bd=1,text="Annotations",font=('calibri', 16), relief=tk.SOLID,pady=10, padx=10)
notes_frame.pack(padx=10, pady=10, fill=tk.X)
notes_label = tk.Label(notes_frame, text="Comments:")
notes_label.grid(row=0, column=0, padx=(0,5))
notes_entry = tk.Entry(notes_frame)
notes_entry.grid(row=0, column=1, padx=(0,5))
notes_save_button = tk.Button(notes_frame, text="Save comments", command=save_comments,state="disabled")
notes_save_button.grid(row=0, column=2, padx=(0,5))
handupButt = tk.Button(notes_frame, text="Hand is Up!!", command=save_handUp,state="disabled")
handupButt.grid(row=0, column=3, padx=(0,5))
handdwButt = tk.Button(notes_frame, text="Hand is Down", command=save_handDw,state="disabled")
handdwButt.grid(row=0, column=4, padx=(0,5))
hand_m1 = tk.Label(notes_frame, text = "Pain intensity ratings should be stored with 'Save Comments'\n as soon as the participant lift the hand from the plate and when it is placed back on the cold plate", font=('calibri', 12))
hand_m1.grid(row=1, column=0, columnspan =5)
score_label = tk.Label(notes_frame, text="Final Pain level:", font=("Helvetica", 14))
score_label.grid(row=2, column=0, padx=(0,5))
pain_scale = tk.Scale(notes_frame, from_=0, to=10, length=300, orient=tk.HORIZONTAL, font=("Helvetica", 12))
pain_scale.grid(row=2, column=1,columnspan=2, padx=(0,5))
pain_save_button = tk.Button(notes_frame, text="Save Final Pain", command=save_pain,state="disabled", font=("Helvetica", 12))
pain_save_button.grid(row=2, column=3, padx=(0,5))
pain_saved_label = tk.Label(notes_frame, text="    ", font=("Helvetica", 12))
pain_saved_label.grid(row=2, column=4, padx=(0,5))

cronoFrame = tk.Frame(root)
cronoFrame.pack()
crono = tk.Label(cronoFrame, text=("Seconds 0/" + str(eeg_duration)), font=("Helvetica", 20))
crono.pack(pady=10)

start_button = tk.Button(cronoFrame , text="Start", font=("Helvetica", 18),state=tk.DISABLED, command=start_rec)
start_button.pack(side=tk.LEFT, padx=10, pady=(0,20))

stop_button = tk.Button(cronoFrame , text="Stop", font=("Helvetica", 18), state=tk.DISABLED, command=stop_rec)
stop_button.pack(side=tk.LEFT, padx=10, pady=(0,20))
refreshCPM()
update_tempsCPM()

root.protocol("WM_DELETE_WINDOW", on_close)
root.mainloop()

    