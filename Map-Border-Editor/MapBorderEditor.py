from PyQt6 import QtGui, QtWidgets
import sys
import webbrowser


version = "Version 1"

aboutMsg = "Koopatlas Map Border Editor | " + version + "\nCoded by LiQ - GNU GPLv3 License"

result = []

listData = []


class Widgets(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.newFileWIP = False
        # widgets
        self.worldListLabel = QtWidgets.QLabel()
        self.worldList = QtWidgets.QListWidget()
        self.borderLabel = QtWidgets.QLabel()
        self.coordinateL = QtWidgets.QSpinBox()
        self.coordinateR = QtWidgets.QSpinBox()
        self.coordinateT = QtWidgets.QSpinBox()
        self.coordinateB = QtWidgets.QSpinBox()
        self.addButton = QtWidgets.QPushButton()
        self.removeButton = QtWidgets.QPushButton()

        self.coordinateL.setMinimum(0)
        self.coordinateL.setMaximum(65535)  # u16
        self.coordinateR.setMinimum(0)
        self.coordinateR.setMaximum(65535)  # u16
        self.coordinateT.setMinimum(0)
        self.coordinateT.setMaximum(65535)  # u16
        self.coordinateB.setMinimum(0)
        self.coordinateB.setMaximum(65535)  # u16

        self.worldListLabel.setText("Worlds")
        self.borderLabel.setText("Border")
        self.addButton.setText("Add")
        self.removeButton.setText("Remove")

        self.worldList.itemSelectionChanged.connect(self.updateValues)
        self.addButton.pressed.connect(self.addB)
        self.removeButton.pressed.connect(self.removeB)
        self.coordinateL.valueChanged.connect(self.coordinateLChanged)
        self.coordinateR.valueChanged.connect(self.coordinateRChanged)
        self.coordinateT.valueChanged.connect(self.coordinateTChanged)
        self.coordinateB.valueChanged.connect(self.coordinateBChanged)

        # init layout
        self.layout = QtWidgets.QFormLayout()

        # add rows
        self.layout.addRow(self.worldListLabel)
        self.layout.addRow(self.worldList)
        self.layout.addRow(self.addButton, self.removeButton)
        self.layout.addRow('Left Border (X):', self.coordinateL)
        self.layout.addRow('Right Border (X):', self.coordinateR)
        self.layout.addRow('Top Border (Y):', self.coordinateT)
        self.layout.addRow('Bottom Border (Y):', self.coordinateB)

        # set the layout
        self.setLayout(self.layout)

    def updateValues(self):
        index = self.worldList.currentRow()
        self.coordinateL.setValue(listData[index][0])
        self.coordinateR.setValue(listData[index][1])
        self.coordinateT.setValue(listData[index][2])
        self.coordinateB.setValue(listData[index][3])

    def addB(self):
        if self.worldList.count() == 255: return
        self.worldList.addItem("World " + str(self.worldList.count() + 1))
        listData.append([0, 0, 0, 0])

    def removeB(self):
        try:
            selected = self.worldList.selectedIndexes()[0]
            if selected:
                self.worldList.takeItem(selected.row())
        finally:
            return

    def coordinateLChanged(self):
        if self.newFileWIP: return
        index = self.worldList.currentRow()
        listData[index][0] = self.coordinateL.value()
    def coordinateRChanged(self):
        if self.newFileWIP: return
        index = self.worldList.currentRow()
        listData[index][1] = self.coordinateR.value()
    def coordinateTChanged(self):
        if self.newFileWIP: return
        index = self.worldList.currentRow()
        listData[index][2] = self.coordinateT.value()
    def coordinateBChanged(self):
        if self.newFileWIP: return
        index = self.worldList.currentRow()
        listData[index][3] = self.coordinateB.value()

    def addItemFromExtern(self, coordinates):
        self.worldList.addItem("World " + str(self.worldList.count() + 1))
        listData.append(coordinates)


class MainForm(QtWidgets.QMainWindow):
    def __init__(self):
        QtWidgets.QMainWindow.__init__(self)

        # basic things
        self.setWindowTitle("Koopatlas Map Border Editor")
        self.setWindowIcon(QtGui.QIcon("icon.ico"))

        self.createMenuStrip()

        self.widget = Widgets()
        self.setCentralWidget(self.widget)

        self.msg = None

        #Vars
        self.path = None
        self.starcoins = 0

        self.show()

    def createMenuStrip(self):
        menub = self.menuBar()

        menub.setNativeMenuBar(False)

        # File Menu
        file = menub.addMenu("File")

        newfile = file.addAction("New")
        newfile.triggered.connect(self.newFile)

        openFile = file.addAction("Open File...")
        openFile.triggered.connect(self.openFile)

        self.saveFileB = file.addAction("Save File")
        self.saveFileB.triggered.connect(self.saveFile)
        self.saveFileB.setEnabled(False)

        saveFileAs = file.addAction("Save File As...")
        saveFileAs.triggered.connect(self.saveFileAs)

        # Help Menu
        help = menub.addMenu("Info")
        about = help.addAction("About")
        about.triggered.connect(self.aboutPressed)

        website = help.addAction("Documentation")
        website.triggered.connect(self.websitePressed)

    def aboutPressed(self):
        msg = QtWidgets.QMessageBox()
        msg.setText(aboutMsg)
        msg.setWindowTitle("About")
        msg.setStandardButtons(QtWidgets.QMessageBox.StandardButton.Ok)
        msg.exec()

    def websitePressed(self):
        webbrowser.open("https://nikolasthurm.de/viewmapfeature.html", new=2)

    def openFile(self):
        fresult = QtWidgets.QFileDialog.getOpenFileName(self, "Open File", "", "Map Border Binary (*.bin)")

        if fresult[0] == "":
            return

        #clear everything
        self.newFile()

        # get only the path
        self.path = fresult[0]

        # Open the file
        file = open(self.path, 'rb')
        data = file.read()
        file.close()

        if data[0] != ord('K'):
           self.errorWhileOpening()#
           return
        if data[1] != ord('M'):
            self.errorWhileOpening()
            return
        if data[2] != ord('B'):
            self.errorWhileOpening()
            return
        if data[3] != ord('B'):
            self.errorWhileOpening()
            return

        #Clear list
        listData = []

        try:
            numberOfWorlds = data[4]
            index = 6
            for w in range(numberOfWorlds):
                coordinates = []
                for i in range(4):
                    offset = (data[index] << 8) | (data[index + 1])
                    coordinates.append(offset)
                    index += 2
                self.widget.addItemFromExtern(coordinates)
            self.saveFileB.setEnabled(True)
        except:
            self.errorWhileOpening()
        finally:
            pass


    def saveFile(self):
        if self.path is None:
            return

        self.saveProcess()

    def saveFileAs(self):
        fresult = QtWidgets.QFileDialog.getSaveFileName(self, "Save File", "", "Map Border Binary (*.bin)")

        if fresult[0] == "":
            return

        self.path = fresult[0]

        self.saveProcess()



    def newFile(self):
        self.widget.worldList.clear()
        listData.clear()
        self.widget.newFileWIP = True
        self.widget.coordinateL.setValue(0)
        self.widget.coordinateR.setValue(0)
        self.widget.coordinateT.setValue(0)
        self.widget.coordinateB.setValue(0)
        self.widget.newFileWIP = False
        self.saveFileB.setEnabled(False)
        self.path = None

    def errorWhileOpening(self):
        msg = QtWidgets.QMessageBox()
        msg.setText("Error while reading!\nYour file may be corrupted.\nContact: LiQ#7253 on Discord")
        msg.setWindowTitle("About")
        msg.setStandardButtons(QtWidgets.QMessageBox.StandardButton.Ok)
        msg.exec()

    def saveProcess(self):
        # Save the data in result
        result.append(ord('K'))
        result.append(ord('M'))
        result.append(ord('B'))
        result.append(ord('B'))
        result.append(len(listData))
        result.append(0x00)
        for world in listData:
            result.append((world[0] >> 8) & 0xff)
            result.append(world[0] & 0xff)
            result.append((world[1] >> 8) & 0xff)
            result.append(world[1] & 0xff)
            result.append((world[2] >> 8) & 0xff)
            result.append(world[2] & 0xff)
            result.append((world[3] >> 8) & 0xff)
            result.append(world[3] & 0xff)

        # Open the file
        file = open(self.path, 'wb')
        file.write(bytes(result))
        file.close()

app = QtWidgets.QApplication(sys.argv)

window = MainForm()

app.exec()
