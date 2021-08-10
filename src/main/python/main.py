"""Main file."""
from fbs_runtime.application_context.PyQt5 import ApplicationContext
from PyQt5.QtWidgets import (QDialog, QGridLayout, QGroupBox, QLabel,
                             QPushButton, QLineEdit, QListWidget, QMessageBox,
                             QProgressBar, QComboBox)
from PyQt5.QtGui import QPixmap
import utils
import pymysql
import sys


class Gui(QDialog):
    """Perform Gui Functions."""

    def __init__(self, parent=None):
        """Initialize Gui."""
        super(Gui, self).__init__(parent)
        self.Env = utils.getEnv(envPath)
        mainLayout = QGridLayout()

        self.createLeftGroup()
        self.createRightGroup()

        mainLayout.addWidget(self.LeftGroup, 0, 0)
        mainLayout.addWidget(self.RightGroup, 0, 1)
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
        layout.addWidget(self.Image, 0, 0, 8, 8)
        layout.addWidget(self.SkipButton, 9, 6, 1, 2)
        layout.addWidget(self.SettingsButton, 9, 0, 1, 2)
        self.LeftGroup.setLayout(layout)

        self.SettingsButton.clicked.connect(self.on_settings_clicked)

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

    def PopulateAddressList(self):
        """Download MSTR_CUSTLIST and populate addresses."""
        # create a dictionary that maps addresses to custListObjects
        self.DatabaseBox.clear()
        connection = pymysql.connect(host=self.Env['HOST'],
                                     user=self.Env['USERNAME'],
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
                       "`Bill City`, `Bill Zip`, `Account Number` from " +
                       "`MSTR CUSTLIST`")
                cursor.execute(sql)
                accounts = cursor.fetchall()
                print(accounts[0])
                # add accounts to list as BillAddress BillCity BillState BillZi

                dict = {a['Bill Address'] + ' ' + a['Bill City'] + ' ' +
                        a['Bill State'] + ' ' + a['Bill Zip']: a for a in
                        accounts if a['Bill Address'] != ''}
                self.AddressDict = dict
                self.AddressList.addItems(self.AddressDict.keys)

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
        self.Username.setText(self.Env['USERNAME'])

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
        self.Env = env

    def on_cancelButton_clicked(self):
        """Reset fields if cancel button is pressed."""
        self.Host.setText(self.Env['HOST'])
        self.Username.setText(self.Env['USERNAME'])
        self.Password.setText(self.Env['PASSWORD'])
        self.PhotosFolder.setText(self.Env['PHOTOSFOLDER'])
        self.OutputPath.setText(self.Env['OUTPUTPATH'])
        self.isSaved = True
        self.reject()


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
