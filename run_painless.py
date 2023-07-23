#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Jul 22 20:24:25 2023

@author: albertogonzalezv
"""
import tkinter as tk
import os

def run_script(script_name):
    os.system('python ' + script_name)

def change_button_color(button):
    button.config(fg='green')

def create_window():
    window = tk.Tk()
    window.title("Painless Task Launcher")
    window.iconbitmap('painlessLogo.ico')
    window.geometry("400x300")

    button1 = tk.Button(window, text="1 Thresholds 5", command=lambda: [run_script(os.getcwd()+os.sep+ "1_Thresholds5.py"), change_button_color(button1)])
    button1.pack(pady=10)

    button2 = tk.Button(window, text="2 TSP CPM", command=lambda: [run_script(os.getcwd()+os.sep+"2_TSP_CPM.py"), change_button_color(button2)])
    button2.pack(pady=10)

    button3 = tk.Button(window, text="3 HPT CDT CPT", command=lambda: [run_script(os.getcwd()+os.sep+"3_HPT_CDT_CPT.py"), change_button_color(button3)])
    button3.pack(pady=10)

    button4 = tk.Button(window, text="4 Offset Analgesia", command=lambda: [run_script(os.getcwd()+os.sep+"4_Offset_Analgesia.py"), change_button_color(button4)])
    button4.pack(pady=10)

    button5 = tk.Button(window, text="5 Resting EEG COLD", command=lambda: [run_script(os.getcwd()+os.sep+"5_resting_EEG_COLD.py"), change_button_color(button5)])
    button5.pack(pady=10)

    button6 = tk.Button(window, text="6 CHEPS EEG", command=lambda: [run_script(os.getcwd()+os.sep+"6_Cheps_EEG.py"), change_button_color(button6)])
    button6.pack(pady=10)

    window.mainloop()

create_window()
