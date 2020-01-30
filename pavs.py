from PyQt5.QtWidgets import QMainWindow, QApplication, QPushButton, QLineEdit, QComboBox, QFileDialog, QStyleFactory, QHBoxLayout, QLabel, QSizePolicy, QSlider, QStyle, QVBoxLayout, QWidget, QStatusBar, QTableWidget, QVBoxLayout, QTableWidgetItem, QHBoxLayout, QSplitter, QGroupBox, QFormLayout, QAction, QGridLayout, QShortcut
from PyQt5.QtMultimedia import QMediaContent, QMediaPlayer
from PyQt5.QtMultimediaWidgets import QVideoWidget
from PyQt5 import QtCore, Qt, QtGui
from PyQt5.QtCore import QRect, QSize, Qt, QUrl, QDir, QTime, pyqtSlot
from PyQt5.QtGui import QFont, QPixmap, QImage, QColor, QPainter, QPen, QKeySequence, QStandardItemModel
import os
import csv
import sys
import numpy as np

audio_extensions = [".wav", ".mp3"]
video_extensions = [".avi", ".mp4", ".mkv"]

class Window(QMainWindow):

    def __init__(self):
        super().__init__()

        self.title = "Python Annotator for VideoS"
        # self.top = 100
        # self.left = 100
        # self.width = 300
        # self.height = 400
        # self.setWindowState = "Qt.WindowMaximized"
        iconName = "home.png"
        self.InitWindow()

    def InitWindow(self):
        self.setWindowTitle(self.title)
        # self.setWindowIcon(QtGui.QIcon(iconName))
        self.setWindowState(QtCore.Qt.WindowMaximized)

        self.UiComponents()

        self.show()

    def UiComponents(self):

        self.rowNo = 1
        self.colNo = 0
        self.fName = ""
        self.fName2 = ""
        self.fileNameExist = ""
        self.dropDownName = ""

        self.model = QStandardItemModel()

        self.mediaPlayer = QMediaPlayer(None, QMediaPlayer.VideoSurface)
        self.tableWidget = QTableWidget()
        self.tableWidget.cellClicked.connect(self.checkTableFrame)

        self.videoWidget = QVideoWidget()
        self.frameID=0


        self.insertBaseRow()

        openButton = QPushButton("Open...")
        openButton.clicked.connect(self.openFile)

        self.playButton = QPushButton()
        self.playButton.setEnabled(False)
        self.playButton.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))
        self.playButton.clicked.connect(self.play)

        self.lbl = QLabel('00:00:00')
        self.lbl.setFixedWidth(60)
        self.lbl.setUpdatesEnabled(True)
        # self.lbl.setStyleSheet(stylesheet(self))

        self.elbl = QLabel('00:00:00')
        self.elbl.setFixedWidth(60)
        self.elbl.setUpdatesEnabled(True)
        # self.elbl.setStyleSheet(stylesheet(self))


        self.nextButton = QPushButton("-->")
        self.nextButton.clicked.connect(self.next)

        self.delButton = QPushButton("Delete")
        self.delButton.clicked.connect(self.delete)

        self.exportButton = QPushButton("Export")
        self.exportButton.clicked.connect(self.export)

        self.importButton = QPushButton("Import")
        self.importButton.clicked.connect(self.importCSV)

        # self.ctr = QLineEdit()
        # self.ctr.setPlaceholderText("Extra")

        self.startTime = QLineEdit()
        self.startTime.setPlaceholderText("Select Start Time")

        self.endTime = QLineEdit()
        self.endTime.setPlaceholderText("Select End Time")

        self.iLabel = QComboBox(self)
        self.iLabel.addItem("1. Eye Contact")
        self.iLabel.addItem("2. Pointing")
        self.iLabel.addItem("3. Response to Names")
        self.iLabel.addItem("4. Following Pointing")
        self.iLabel.addItem("5. Babbling")
        self.iLabel.addItem("6. Question-Answering")
        self.iLabel.addItem("7. Showing")
        self.iLabel.addItem("8. Following Instructions")
        self.iLabel.activated[str].connect(self.style_choice)

        # self.iLabel = QLineEdit()
        # self.iLabel.setPlaceholderText("Label")

        self.positionSlider = QSlider(Qt.Horizontal)
        self.positionSlider.setRange(0, 100)
        self.positionSlider.sliderMoved.connect(self.setPosition)
        self.positionSlider.sliderMoved.connect(self.handleLabel)
        self.positionSlider.setSingleStep(2)
        self.positionSlider.setPageStep(20)
        self.positionSlider.setAttribute(Qt.WA_TranslucentBackground, True)

        self.errorLabel = QLabel()
        self.errorLabel.setSizePolicy(QSizePolicy.Preferred,
                QSizePolicy.Maximum)

        # Main plotBox
        plotBox = QHBoxLayout()

        controlLayout = QHBoxLayout()
        # controlLayout.setContentsMargins(0, 0, 0, 0)
        controlLayout.addWidget(openButton)
        controlLayout.addWidget(self.playButton)
        controlLayout.addWidget(self.lbl)
        controlLayout.addWidget(self.positionSlider)
        controlLayout.addWidget(self.elbl)

        wid = QWidget(self)
        self.setCentralWidget(wid)

        # Left Layout{
        # layout.addWidget(self.videoWidget)

        layout = QVBoxLayout()
        layout.addWidget(self.videoWidget, 3)
        # layout.addLayout(self.grid_root)
        layout.addLayout(controlLayout)
        layout.addWidget(self.errorLabel)

        plotBox.addLayout(layout, 3)
        # }

        # Right Layout {
        inputFields = QHBoxLayout()
        inputFields.addWidget(self.startTime)
        inputFields.addWidget(self.endTime)
        inputFields.addWidget(self.iLabel)
        # inputFields.addWidget(self.ctr)

        feats = QHBoxLayout()
        feats.addWidget(self.nextButton)
        feats.addWidget(self.delButton)
        feats.addWidget(self.exportButton)
        feats.addWidget(self.importButton)

        layout2 = QVBoxLayout()
        layout2.addWidget(self.tableWidget)
        layout2.addLayout(inputFields, 1)
        layout2.addLayout(feats, 2)
        # layout2.addWidget(self.nextButton)
        # }

        plotBox.addLayout(layout2, 1)

        # self.setLayout(layout)
        wid.setLayout(plotBox)

        self.shortcut = QShortcut(QKeySequence("["), self)
        self.shortcut.activated.connect(self.addStartTime)
        self.shortcut = QShortcut(QKeySequence("]"), self)
        self.shortcut.activated.connect(self.addEndTime)
        self.shortcut = QShortcut(QKeySequence("L"), self)
        self.shortcut.activated.connect(self.openFile)
        self.shortcut = QShortcut(QKeySequence("C"), self)
        self.shortcut.activated.connect(self.clearTable)

        self.shortcut = QShortcut(QKeySequence(Qt.Key_Right), self)
        self.shortcut.activated.connect(self.forwardSlider)
        self.shortcut = QShortcut(QKeySequence(Qt.Key_Left), self)
        self.shortcut.activated.connect(self.backSlider)
        self.shortcut = QShortcut(QKeySequence(Qt.Key_Up), self)
        self.shortcut.activated.connect(self.volumeUp)
        self.shortcut = QShortcut(QKeySequence(Qt.Key_Down), self)
        self.shortcut.activated.connect(self.volumeDown)
        self.shortcut = QShortcut(QKeySequence(Qt.ShiftModifier +  Qt.Key_Right) , self)
        self.shortcut.activated.connect(self.forwardSlider10)
        self.shortcut = QShortcut(QKeySequence(Qt.ShiftModifier +  Qt.Key_Left) , self)
        self.shortcut.activated.connect(self.backSlider10)

        self.mediaPlayer.setVideoOutput(self.videoWidget)
        self.mediaPlayer.stateChanged.connect(self.mediaStateChanged)
        self.mediaPlayer.positionChanged.connect(self.positionChanged)
        self.mediaPlayer.positionChanged.connect(self.handleLabel)
        self.mediaPlayer.durationChanged.connect(self.durationChanged)
        self.mediaPlayer.error.connect(self.handleError)

    def openFile(self):
        fileName, _ = QFileDialog.getOpenFileName(self, "Open Movie",
                QDir.homePath())

        if fileName != '':
            self.fileNameExist = fileName
            self.mediaPlayer.setMedia(
                    QMediaContent(QUrl.fromLocalFile(fileName)))
            self.playButton.setEnabled(True)
        self.videopath = QUrl.fromLocalFile(fileName)
        self.errorLabel.setText(fileName)
        self.errorLabel.setStyleSheet('color: black')

    def play(self):
        # self.is_playing_video = not self.is_playing_video
        if self.mediaPlayer.state() == QMediaPlayer.PlayingState:
            self.mediaPlayer.pause()
        else:
            self.mediaPlayer.play()
            # self._play_video()
            # self.errorLabel.setText("Start: " + " -- " + " End:")

    def _play_video(self):
        if self.is_playing_video and self.video_fps:
            frame_idx = min(self.render_frame_idx+1, self.frame_count)
            print(frame_idx)

            if frame_idx == self.frame_count:
                self.on_play_video_clicked()
            else:
                self.target_frame_idx = frame_idx

    def style_choice(self, text):
        self.dropDownName = text
        QApplication.setStyle(QStyleFactory.create(text))


    def addStartTime(self):
        self.startTime.setText(self.lbl.text())

    def addEndTime(self):
        self.endTime.setText(self.lbl.text())

    def next(self):
        self.tableWidget.setItem(self.rowNo, self.colNo, QTableWidgetItem(self.startTime.text()))
        self.colNo += 1
        self.tableWidget.setItem(self.rowNo, self.colNo, QTableWidgetItem(self.endTime.text()))
        self.colNo += 1
        self.tableWidget.setItem(self.rowNo, self.colNo, QTableWidgetItem(str(self.iLabel.currentIndex()+1)))
        self.colNo += 1
        self.tableWidget.setItem(self.rowNo, self.colNo, QTableWidgetItem(self.iLabel.currentText().split(' ')[1]))
        self.colNo = 0
        self.rowNo += 1
        # print(self.ctr.text(), self.startTime.text(), self.iLabel.text(), self.rowNo, self.colNo)
        # print(self.iLabel.currentIndex())

    def delete(self):
        # print("delete")
        index_list = []
        for model_index in self.tableWidget.selectionModel().selectedRows():
            index = QtCore.QPersistentModelIndex(model_index)
            index_list.append(index)

        self.rowNo = self.rowNo - len(index_list)

        for index in index_list:
            self.tableWidget.removeRow(index.row())

    def clearTable(self):
        while self.tableWidget.rowCount() > 0:
            self.tableWidget.removeRow(0)
        self.insertBaseRow()
        print("Clearing")

    def export(self):
        self.fName = ((self.fileNameExist.rsplit('/', 1)[1]).rsplit('.',1))[0]
        path, _ = QFileDialog.getSaveFileName(self, 'Save File', QDir.homePath() + "/"+self.fName+".csv", "CSV Files(*.csv *.txt)")
        if path:
            with open(path, 'w') as stream:
                print("saving", path)
                writer = csv.writer(stream)
                # writer = csv.writer(stream, delimiter=self.delimit)
                for row in range(self.tableWidget.rowCount()):
                    rowdata = []
                    for column in range(self.tableWidget.columnCount()):
                        item = self.tableWidget.item(row, column)
                        if item is not None and item is not "":
                            rowdata.append(item.text())
                        else:
                            break
                    writer.writerow(rowdata)
        # self.isChanged = False
        # self.setCurrentFile(path)

    def importCSV(self):
        # if fName2 != "":
            # self.fName2 = ((self.fileNameExist.rsplit('/', 1)[1]).rsplit('.',1))[0]
            # path, _ = QFileDialog.getSaveFileName(self, 'Save File', QDir.homePath() + "/"+self.fName2+".csv", "CSV Files(*.csv *.txt)")
        # else:
        self.clearTable()
        path, _ = QFileDialog.getOpenFileName(self, 'Save File', QDir.homePath() , "CSV Files(*.csv *.txt)")
        print(path)
        if path:
            with open(path, 'r') as stream:
                print("loading", path)
                reader = csv.reader(stream)
                # reader = csv.reader(stream, delimiter=';', quoting=csv.QUOTE_ALL)
                # reader = csv.reader(stream, delimiter=';', quoting=csv.QUOTE_ALL)
                # for row in reader:
                for i, row in enumerate(reader):
                    if i == 0:
                        continue
                    else:
                        if(len(row) == 4):
                            st, et, li, ln = row
                            self.tableWidget.setItem(self.rowNo, self.colNo, QTableWidgetItem(st))
                            self.colNo += 1
                            self.tableWidget.setItem(self.rowNo, self.colNo, QTableWidgetItem(et))
                            self.colNo += 1
                            self.tableWidget.setItem(self.rowNo, self.colNo, QTableWidgetItem(str(li)))
                            self.colNo += 1
                            self.tableWidget.setItem(self.rowNo, self.colNo, QTableWidgetItem(ln))
                            self.rowNo += 1
                            self.colNo = 0

    def insertBaseRow(self):
        self.tableWidget.setColumnCount(4) #, Start Time, End Time, TimeStamp
        self.tableWidget.setRowCount(50)
        self.rowNo = 1
        self.colNo = 0
        self.tableWidget.setItem(0, 0, QTableWidgetItem("Start Time"))
        self.tableWidget.setItem(0, 1, QTableWidgetItem("End Time"))
        self.tableWidget.setItem(0, 2, QTableWidgetItem("Label Index"))
        self.tableWidget.setItem(0, 3, QTableWidgetItem("Label Name"))

    def checkTableFrame(self, row, column):
        if ((row > 0) and (column < 2)):
            # print("Row %d and Column %d was clicked" % (row, column))
            item = self.tableWidget.item(row, column)
            if (item != (None and "")):
                try:
                    itemFrame = item.text()
                    itemFrame = itemFrame.split(":")
                    frameTime = int(itemFrame[2]) + int(itemFrame[1])*60 + int(itemFrame[0])*3600
                    elblFrames = self.elbl.text().split(":")
                    elblFrameTime = int(elblFrames[2]) + int(elblFrames[1])*60 + int(elblFrames[0])*3600
                    # print("Elbl FT ", str(elblFrameTime))
                    # print("FT ", str(frameTime))
                    # print(frameTime)
                    self.mediaPlayer.setPosition(frameTime*1000+1*60)
                except:
                    self.errorLabel.setText("Some Video Error - Please Recheck Video Imported!")
                    self.errorLabel.setStyleSheet('color: red')

    def mediaStateChanged(self, state):
        if self.mediaPlayer.state() == QMediaPlayer.PlayingState:
            self.playButton.setIcon(
                    self.style().standardIcon(QStyle.SP_MediaPause))
        else:
            self.playButton.setIcon(
                    self.style().standardIcon(QStyle.SP_MediaPlay))

    def positionChanged(self, position):
        self.positionSlider.setValue(position)

    def durationChanged(self, duration):
        self.positionSlider.setRange(0, duration)
        mtime = QTime(0,0,0,0)
        mtime = mtime.addMSecs(self.mediaPlayer.duration())
        self.elbl.setText(mtime.toString())

    def setPosition(self, position):
        self.mediaPlayer.setPosition(position)

    def handleError(self):
        self.playButton.setEnabled(False)
        self.errorLabel.setText("Error: " + self.mediaPlayer.errorString())
        self.errorLabel.setStyleSheet('color: red')

    def forwardSlider(self):
        self.mediaPlayer.setPosition(self.mediaPlayer.position() + 1*60)

    def forwardSlider10(self):
            self.mediaPlayer.setPosition(self.mediaPlayer.position() + 1000*60)

    def backSlider(self):
        self.mediaPlayer.setPosition(self.mediaPlayer.position() - 1*60)

    def backSlider10(self):
        self.mediaPlayer.setPosition(self.mediaPlayer.position() - 1000*60)

    def volumeUp(self):
        self.mediaPlayer.setVolume(self.mediaPlayer.volume() + 10)
        print("Volume: " + str(self.mediaPlayer.volume()))

    def volumeDown(self):
        self.mediaPlayer.setVolume(self.mediaPlayer.volume() - 10)
        print("Volume: " + str(self.mediaPlayer.volume()))

    # def mouseMoveEvent(self, event):
        # if event.buttons() == Qt.LeftButton:
        #     self.move(event.globalPos() \- QPoint(self.frameGeometry().width() / 2, \
        #                 self.frameGeometry().height() / 2))
        #     event.accept()

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.accept()
        else:
            event.ignore()

    ##################### update Label ##################################
    def handleLabel(self):
        self.lbl.clear()
        mtime = QTime(0,0,0,0)
        self.time = mtime.addMSecs(self.mediaPlayer.position())
        self.lbl.setText(self.time.toString())

    def dropEvent(self, event):
        f = str(event.mimeData().urls()[0].toLocalFile())
        self.loadFilm(f)

    def clickFile(self):
        print("File Clicked")

    def clickExit(self):
        sys.exit()

App = QApplication(sys.argv)
window = Window()
sys.exit(App.exec())
