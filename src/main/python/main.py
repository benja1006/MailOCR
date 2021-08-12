"""Main file."""
from fbs_runtime.application_context.PyQt5 import ApplicationContext
from PyQt5.QtWidgets import (QDialog, QGridLayout, QGroupBox, QLabel,
                             QPushButton, QLineEdit, QListWidget, QMessageBox,
                             QProgressBar, QComboBox)
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import pyqtSignal
import utils
import pymysql
import sys
import os


class Gui(QDialog):
    """Perform Gui Functions."""

    def __init__(self, parent=None):
        """Initialize Gui."""
        super(Gui, self).__init__(parent)
        self.Env = utils.getEnv(envPath)
        self.SettingsGui = SettingsGui(self.Env, self)
        mainLayout = QGridLayout()

        self.createPhotoArray()

        self.createLeftGroup()
        self.createRightGroup()

        mainLayout.addWidget(self.LeftGroup, 0, 0)
        mainLayout.addWidget(self.RightGroup, 0, 1)
        self.setLayout(mainLayout)
        self.SettingsGui.doneEditing.connect(self.on_updateSettings)

    def show(self):
        """Override the show function to show settings afterwards."""
        # print(type(Gui))
        super().show()
        updateSettings = False
        for value in self.Env.values():
            if value == '':
                updateSettings = True
        if(not utils.checkDbLoginInfo(self.Env) or updateSettings):
            self.SettingsGui.show()
            utils.throwError('Make sure all settings are correct and ' +
                             'filled in.')

    def createLeftGroup(self):
        """Create left group containing image and skip button."""
        self.LeftGroup = QGroupBox()

        self.Image = QLabel()

        pixmap = QPixmap(self.getNextImage())
        self.Image.setPixmap(pixmap)

        self.SkipButton = QPushButton('Skip')
        self.SettingsButton = QPushButton('Settings')

        layout = QGridLayout()
        layout.addWidget(self.Image, 0, 0, 8, 8)
        layout.addWidget(self.SkipButton, 9, 6, 1, 2)
        layout.addWidget(self.SettingsButton, 9, 0, 1, 2)
        self.LeftGroup.setLayout(layout)

        self.SettingsButton.clicked.connect(self.on_settings_clicked)
        self.SkipButton.clicked.connect(self.on_skipButton_clicked)

    def createRightGroup(self):
        """Create right group containing list of addresses and search bar."""
        self.RightGroup = QGroupBox()

        self.SearchBar = QLineEdit()
        self.AddressList = QListWidget()
        self.DatabaseBox = QComboBox()
        self.DatabaseBox.addItems(['SFNY', 'Solar Landscape'])

        layout = QGridLayout()
        layout.addWidget(self.SearchBar, 0, 0, 1, 4)
        layout.addWidget(self.AddressList, 1, 0, 8, 4)
        layout.addWidget(self.DatabaseBox, 9, 0, 1, 2)
        self.RightGroup.setLayout(layout)
        self.ActiveDatabase = 'sfny_production'
        self.PopulateAddressList()

        self.DatabaseBox.currentIndexChanged.connect(self.on_database_edit)
        self.SearchBar.textEdited.connect(self.search)
        self.AddressList.itemDoubleClicked.connect(self.on_item_select)
        self.SearchBar.returnPressed.connect(self.on_enter_pressed)

    def PopulateAddressList(self):
        """Download MSTR_CUSTLIST and populate addresses."""
        # create a dictionary that maps addresses to custListObjects
        if(not utils.checkDbLoginInfo(self.Env)):
            self.AddressDict = {}
            self.AddressList.clear()
            return
        self.SearchBar.setText('')
        self.AddressList.clear()
        connection = pymysql.connect(host=self.Env['HOST'],
                                     user=self.Env['USER'],
                                     password=self.Env['PASSWORD'],
                                     database=self.ActiveDatabase,
                                     local_infile=1,
                                     ssl={'key': 'whatever'},
                                     cursorclass=pymysql.cursors.DictCursor
                                     )
        with connection:
            with connection.cursor() as cursor:
                sql = ("SELECT `FNAME`, `LNAME`, `Service Address`, " +
                       "`Service City`, `Service Zip`, `Bill Address`, " +
                       "`Bill City`, `Bill State`, `Bill Zip`, " +
                       "`Account Number` from `MSTR CUSTLIST`")
                cursor.execute(sql)
                accounts = cursor.fetchall()
                # print(accounts[0])
                # add accounts to list as BillAddress BillCity BillState BillZi

                dict = {a['Bill Address'] + ' ' + a['Bill City'] + ' ' +
                        a['Bill State'] + ' ' + a['Bill Zip']: a for a in
                        accounts if a['Bill Address'] != ''}
                self.AddressDict = dict
                self.AddressList.addItems(self.AddressDict.keys())

    def on_settings_clicked(self):
        """Create a popup settings box with save/cancel buttons."""
        self.SettingsGui.show()

    def on_database_edit(self):
        """Update the database when it is edited."""
        databases = {
            'SFNY': 'sfny_production',
            'Solar Landscape': 'solar_landscape_prod'
        }
        self.ActiveDatabase = databases[self.DatabaseBox.currentText()]
        self.PopulateAddressList()

    def search(self):
        """Search through keys."""
        searchTerm = self.SearchBar.text()
        # oldSet = set(self.currAddresses)
        newSet = set([a for a in self.AddressDict.keys() if searchTerm in a])
        self.AddressList.clear()
        self.AddressList.addItems(newSet)
        self.AddressList.setCurrentRow(0)

    def getNextImage(self):
        """Return the path to the next Image."""
        if len(self.PhotoArray):
            return self.PhotoArray[0][0]
        else:
            return None

    def createPhotoArray(self):
        """Create self.PhotoArray with a path to all photos."""
        photoFolder = self.Env['PHOTOSFOLDER']
        if(not os.path.isdir(photoFolder)):
            photos = ['']
        else:
            photos = [(os.path.join(photoFolder, f), f) for f in
                      os.listdir(photoFolder) if not f.startswith('.')]
        self.PhotoArray = photos

    def on_skipButton_clicked(self):
        """Move the first image to the end and show new image."""
        self.PhotoArray.append(self.PhotoArray.pop(0))
        pixmap = QPixmap(self.getNextImage())
        self.Image.setPixmap(pixmap)

    def on_updateSettings(self, env):
        """Reset the app when settings are updated."""
        self.Env = env
        self.createPhotoArray()
        pixmap = QPixmap(self.getNextImage())
        self.Image.setPixmap(pixmap)
        self.PopulateAddressList()

    def on_item_select(self, item):
        """Pass item to pairItems."""
        self.pairItems(item)

    def on_enter_pressed(self):
        """Pass current item to pairItems."""
        self.pairItems(self.AddressList.currentItem())

    def pairItems(self, item):
        """Pair item and image and output to file."""
        if(not os.path.isdir(self.Env['OUTPUTPATH'])):
            return utils.throwError('Please enter a valid output folder.')
        filePath = os.path.join(self.Env['OUTPUTPATH'], 'output.txt')
        accountNumber = self.AddressDict[item.text()]['Account Number']
        with open(filePath, 'a') as file:
            file.write('%s:%s \n' % (self.PhotoArray.pop(0)[1], accountNumber))
        pixmap = QPixmap(self.getNextImage())
        print(self.getNextImage())
        self.Image.setPixmap(pixmap)


class SettingsGui(QDialog):
    """Edits the settings for the app."""

    doneEditing = pyqtSignal(dict)

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
        self.PhotosFolder.setText(self.Env['PHOTOSFOLDER'])

        label2 = QLabel('Output Folder')
        self.OutputPath = QLineEdit()
        self.OutputPath.setText(self.Env['OUTPUTPATH'])

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
        self.Host.setText(self.Env['HOST'])

        label2 = QLabel('Username')
        self.Username = QLineEdit()
        self.Username.setText(self.Env['USER'])

        label3 = QLabel('Password')
        self.Password = QLineEdit()
        self.Password.setText(self.Env['PASSWORD'])

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
        self.SaveProgressBar.setValue(1)

        layout = QGridLayout()
        layout.addWidget(self.SaveButton, 0, 2, 1, 2)
        layout.addWidget(self.CancelButton, 0, 0, 1, 2)
        layout.addWidget(self.SaveProgressBar, 1, 0, 1, 4)

        self.Buttons.setLayout(layout)

        self.SaveButton.clicked.connect(self.on_saveButton_clicked)
        self.CancelButton.clicked.connect(self.on_cancelButton_clicked)

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
            return
        else:
            self.doneEditing.emit(self.Env)
            super(SettingsGui, self).reject()

    def on_Field_edit(self):
        """Reset progress bar and isSaved flag."""
        self.SaveProgressBar.setValue(0)
        self.isSaved = False

    def on_saveButton_clicked(self):
        """Save the env."""
        env = {
            "HOST": self.Host.text(),
            "USER": self.Username.text(),
            "PASSWORD": self.Password.text(),
            "PHOTOSFOLDER": self.PhotosFolder.text(),
            "OUTPUTPATH": self.OutputPath.text()
        }
        utils.updateEnv(env, envPath)
        self.SaveProgressBar.setValue(1)
        self.isSaved = True
        self.Env = env
        if(not os.path.isdir(env['OUTPUTPATH'])):
            return utils.throwError('Please set a valid output path.')
        self.reject()

    def on_cancelButton_clicked(self):
        """Reset fields if cancel button is pressed."""
        self.Host.setText(self.Env['HOST'])
        self.Username.setText(self.Env['USER'])
        self.Password.setText(self.Env['PASSWORD'])
        self.PhotosFolder.setText(self.Env['PHOTOSFOLDER'])
        self.OutputPath.setText(self.Env['OUTPUTPATH'])
        self.isSaved = True
        self.reject()


if __name__ == '__main__':
    appctxt = ApplicationContext()
    envPath = appctxt.get_resource('.env')
    if(not utils.isAdmin()):
        utils.throwError('Please run as administrator')
    Gui = Gui()
    Gui.show()
    exit_code = appctxt.app.exec_()
    sys.exit(exit_code)
