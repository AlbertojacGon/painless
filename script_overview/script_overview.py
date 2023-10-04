# This Python file uses the following encoding: utf-8
import sys
import ctypes
import socket
import glob
import os
import os.path
import subprocess

from PySide6.QtWidgets import QApplication, QWidget, QPushButton
from PySide6.QtCore import QSignalMapper
from PySide6.QtGui import QColor, QPalette, QIcon

from ui_form import Ui_Widget

VERSION = "1.0"

def retrieve_current_version():
    # TODO add logic to fetch a version string from a server
    return "1.0"

class Widget(QWidget):

    _info_text = "Update available"

    def __init__(self, parent=None):
        """Initialises the widget by searching for executables in the painless subfolder and dynamically creating a button for each executable found.
        """
        super().__init__(parent)

        self.ui = Ui_Widget()
        self.ui.setupUi(self)

        self.window_icon_pth = os.path.join(".", "icon.ico")
        self.setWindowTitle("Painless script overview")
        self.setWindowIcon(QIcon(self.window_icon_pth))

        red_palette = QPalette()
        red_palette.setColor(QPalette.WindowText, QColor(0.8 * 255, 0, 0, 0.8 * 255))
        self.ui.infoText.setPalette(red_palette)
        self.check_for_updates()

        self.script_folder = os.path.join('.', 'painless')
        if not os.path.isdir(self.script_folder):
            print(f"Could not find the folder {self.script_folder}, exiting...")
            sys.exit()
        print(f"Looking for executables in {self.script_folder}...")
        external_scripts_exe = glob.glob(os.path.join(self.script_folder, '*.exe'))

        signalMapper = QSignalMapper(self)

        self.ui.buttons = []

        index = 0
        for script in external_scripts_exe:
            script_name = os.path.basename(script).split(".")[0]
            print(f"{index+1}:\t\t{script_name}")
            self.ui.buttons.append(QPushButton())
            self.ui.buttons[index].setObjectName(f"button_{index}")
            self.ui.buttons[index].setText(script_name)
            self.ui.verticalLayout.addWidget(self.ui.buttons[index])
            self.ui.buttons[index].show()
            self.ui.buttons[index].clicked.connect(signalMapper.map)
            signalMapper.setMapping(self.ui.buttons[index], script)
            index += 1
        print(f"Found {index} executables.")

        signalMapper.mappedString.connect(self.launch_script_string)


    def launch_script_string(self, string):
        """Launches the executable specified by string in a detached process.
        """
        subprocess.Popen(string, start_new_session=True, cwd=self.script_folder, creationflags=subprocess.CREATE_NEW_CONSOLE)
        # sys.exit()  # uncomment this to exit the overview after a button is clicked

    def check_for_updates(self):
        """Checks for updates and adjusts the info text above the buttons accordingly.
        """
        # TODO: change this to check for updates online here - preferably in second thread
        updates_available = False
        latest_version = retrieve_current_version()
        if latest_version != VERSION:
            updates_available = True
        if updates_available:
            self.ui.infoText.setText(self._info_text)
        else:
            self.ui.infoText.setText("")
        self.ui.infoText.show()

if __name__ == "__main__":
    # Bind to a socket to avoid overview to be run twice
    try:
        DEFINED_PORT = 6454
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind(('localhost', DEFINED_PORT))
    except OSError:
        print('Process is already running, exiting')
        sys.exit()

    appID = u'mentalab.painless_script_overview.v1'
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(appID)
    app = QApplication(sys.argv)
    widget = Widget()
    widget.show()
    sys.exit(app.exec())
