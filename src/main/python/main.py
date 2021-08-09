"""Main file."""
from fbs_runtime.application_context.PyQt5 import ApplicationContext
from PyQt5.QtWidgets import (QDialog, QGridLayout, QGroupBox, QLabel,
                             QPushButton, QLineEdit, QListWidget, QMessageBox,
                             QProgressBar)
from PyQt5.QtGui import QPixmap
import utils

import sys


class Gui(QDialog):
    """Perform Gui Functions."""

    def __init__(self, parent=None):
        """Initialize Gui."""
        super(Gui, self).__init__(parent)
        self.Env = utils.getEnv(envPath)
        mainLayout = QGridLayout()

        self.createLeftGroup()
        # self.createRightGroup()

        mainLayout.addWidget(self.LeftGroup, 0, 0)
        self.setLayout(mainLayout)
        self.SettingsGui = SettingsGui(self.Env)

    def createLeftGroup(self):
        """Create left group containing image and skip button."""
        self.LeftGroup = QGroupBox()

        self.Image = QLabel()
        pixmap = QPixmap(testImagePath)
        self.Image.setPixmap(pixmap)

        self.SkipButton = QPushButton('Skip')
        self.SettingsButton = QPushButton('Settings')

        layout = QGridLayout()
        layout.addWidget(self.Image, 0, 0,
                         pixmap.height() / 20, pixmap.width() / 20)
        layout.addWidget(self.SkipButton,
                         pixmap.height() / 20 + 1, pixmap.width() / 20 - 2,
                         1, 2)
        layout.addWidget(self.SettingsButton, pixmap.height() / 20 + 1, 0,
                         1, 2)
        self.LeftGroup.setLayout(layout)

        self.SettingsButton.clicked.connect(self.on_settings_clicked)

    def createRightGroup(self):
        """Create right group containing list of addresses and search bar."""
        self.RightGroup = QGroupBox()

        self.SearchBar = QLineEdit()
        self.AddressList = QListWidget()
        self.PopulateAddressList()

    def PopulateAddressList(self):
        """Download MSTR_CUSTLIST and populate addresses."""
        # create a dictionary that maps addresses to custListObjects

    def on_settings_clicked(self):
        """Create a popup settings box with save/cancel buttons."""
        self.SettingsGui.show()


class SettingsGui(QDialog):
    """Edits the settings for the app."""

    def __init__(self, env, parent=None):
        """Initialize Gui."""
        super(SettingsGui, self).__init__(parent)
        self.Env = env
        mainLayout = QGridLayout()
        self.createRightGroup()
        self.createLeftGroup()
        self.createButtons()
        mainLayout.addWidget(self.LeftGroup, 0, 0)
        mainLayout.addWidget(self.RightGroup, 0, 1)
        mainLayout.addWidget(self.Buttons, 1, 0, 1, 2)
        self.setLayout(mainLayout)
        self.isSaved = True

    def createRightGroup(self):
        """Create the settings fields."""
        self.RightGroup = QGroupBox('Settings')

        label1 = QLabel('Photos Folder')
        self.PhotosFolder = QLineEdit()

        label2 = QLabel('Output Folder')
        self.OutputPath = QLineEdit()

        layout = QGridLayout()
        layout.addWidget(label1, 0, 0)
        layout.addWidget(self.PhotosFolder, 1, 0)
        layout.addWidget(label2, 2, 0)
        layout.addWidget(self.OutputPath, 3, 0)
        self.RightGroup.setLayout(layout)

        self.PhotosFolder.textEdited.connect(self.on_Field_edit)
        self.OutputPath.textEdited.connect(self.on_Field_edit)

    def createLeftGroup(self):
        """Create group containing mysql sign-in info."""
        self.LeftGroup = QGroupBox('Mysql Login')

        label1 = QLabel('Host')
        self.Host = QLineEdit()

        label2 = QLabel('Username')
        self.Username = QLineEdit()

        label3 = QLabel('Password')
        self.Password = QLineEdit()

        layout = QGridLayout()
        layout.addWidget(label1)
        layout.addWidget(self.Host, 1, 0)
        layout.addWidget(label2, 2, 0)
        layout.addWidget(self.Username, 3, 0)
        layout.addWidget(label3, 4, 0)
        layout.addWidget(self.Password, 5, 0)
        self.LeftGroup.setLayout(layout)

        self.Host.textEdited.connect(self.on_Field_edit)
        self.Username.textEdited.connect(self.on_Field_edit)
        self.Password.textEdited.connect(self.on_Field_edit)

    def createButtons(self):
        """Create buttons."""
        self.Buttons = QGroupBox()
        self.SaveButton = QPushButton('Save')
        self.CancelButton = QPushButton('Cancel')
        self.SaveProgressBar = QProgressBar()
        self.SaveProgressBar.setRange(0, 1)

        layout = QGridLayout()
        layout.addWidget(self.SaveButton, 0, 2, 1, 2)
        layout.addWidget(self.CancelButton, 0, 0, 1, 2)
        layout.addWidget(self.SaveProgressBar, 1, 0, 1, 4)

        self.Buttons.setLayout(layout)

        self.SaveButton.clicked.connect(self.on_saveButton_clicked)

    def on_cancelButton_clicked(self):
        """Reset fields to env and close window."""

    def reject(self):
        """Override super reject."""
        if(not self.isSaved):
            alert = QMessageBox()
            alert.setText("The settings have been modified.")
            alert.setInformativeText("Would you like to save the them?")
            alert.setStandardButtons(QMessageBox.Cancel | QMessageBox.Save)
            ret = alert.exec()
            if(ret == QMessageBox.Save):
                self.on_saveButton_clicked()
                super(SettingsGui, self).reject()
            return
        else:
            super(SettingsGui, self).reject()

    def on_Field_edit(self):
        """Reset progress bar and isSaved flag."""
        self.SaveProgressBar.setValue(0)
        self.isSaved = False

    def on_saveButton_clicked(self):
        """Save the env."""
        env = {
            "HOST": self.Host.text(),
            "USERNAME": self.Username.text(),
            "PASSWORD": self.Password.text(),
            "PHOTOSFOLDER": self.PhotosFolder.text(),
            "OUTPUTPATH": self.OutputPath.text()
        }
        utils.updateEnv(env, envPath)
        self.SaveProgressBar.setValue(1)
        self.isSaved = True


if __name__ == '__main__':
    appctxt = ApplicationContext()
    envPath = appctxt.get_resource('.env')
    testImagePath = appctxt.get_resource('Image1.png')
    if(not utils.isAdmin()):
        utils.throwError('Please run as administrator')
    Gui = Gui()
    Gui.show()
    exit_code = appctxt.app.exec_()
    sys.exit(exit_code)
