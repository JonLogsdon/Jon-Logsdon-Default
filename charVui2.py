#!/usr/bin/env python

# =============================================================================
# IMPORTS
# =============================================================================

# Non-R&H imports
import sys
from PyQt4.QtGui import *
from PyQt4.QtCore import *

# R&H imports
import rh.plugin


# =============================================================================
# CLASSES
# =============================================================================
class Window(QWidget):
    def __init__(self, parent=None):
        super(Window, self).__init__(parent)

        grid = QGridLayout()
        grid.addWidget(self.createFirstExclusiveGroup(), 0, 0)
        grid.addWidget(self.createSecondExclusiveGroup(), 1, 0)
	grid.addWidget(self.createThirdExclusiveGroup(), 2, 0)
	grid.addWidget(self.createPushButtonGroup(), 3, 0)
        self.setLayout(grid)

        self.setWindowTitle("Char Vui #2")
        self.resize(420, 800)

    def createFirstExclusiveGroup(self):
        headerGroupBox = QGroupBox("Character Select")
	
	self.currentStageDropDown = QToolButton(self)
	self.currentStageDropDown.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
	self.currentStageDropDown.setPopupMode(QToolButton.MenuButtonPopup)
	self.currentStageDropDown.setMenu(QMenu(self.currentStageDropDown))
	self.currentStageTextBox = QTextBrowser(self)
	self.currentStageAction1 = QWidgetAction(self.currentStageDropDown)
	self.currentStageAction1.setDefaultWidget(self.currentStageTextBox)
	self.currentStageDropDown.menu().addAction(self.currentStageAction1)
	self.currentStageDropDown.setText("CharacterA")
	self.currentStageDropDown.setIcon(QIcon("/home/jlogsdon/Icons/person_charVui2.png"))
	self.currentStageDropDown.setMinimumSize(300, 40)
	
#	self.info.setStyleSheet("background-color: #FFFFFF;color: #000")
	
	self.lockButton = QPushButton()
	self.lockButton.setGeometry(QRect(12, 10, 20, 30))
	self.lockButton.setIcon(QIcon("/home/jlogsdon/Icons/padlock_charVui2.jpg"))
	self.retimeButton = QPushButton()
	self.retimeButton.setGeometry(QRect(12, 10, 20, 30))
	self.retimeButton.setIcon(QIcon("/home/jlogsdon/Icons/clock_charVui2.png"))
	self.refreshButton = QPushButton()
	self.refreshButton.setGeometry(QRect(12, 10, 20, 30))
	self.refreshButton.setIcon(QIcon("/home/jlogsdon/Icons/refresh_charVui2.png"))
	
	self.hbox = QHBoxLayout()
#	self.hbox.addStretch(1)
	
#	self.vbox = QVBoxLayout()
#	self.vbox.addStretch(1)
#	self.vbox.addLayout(self.hbox)
	
	self.hbox.addWidget(self.currentStageDropDown)
	self.hbox.addWidget(self.lockButton)
	self.hbox.addWidget(self.retimeButton)
	self.hbox.addWidget(self.refreshButton)
	
#	self.centralWidget = QWidget()
#       self.centralWidget.setLayout(self.vbox)
#	self.setCentralWidget(self.centralWidget)

#        radio1.setChecked(True)

#        vbox = QtGui.QVBoxLayout()
#        vbox.addWidget(radio1)
#        vbox.addWidget(radio2)
#        vbox.addWidget(radio3)
#        vbox.addStretch(1)
        headerGroupBox.setLayout(self.hbox)

        return headerGroupBox

    def createSecondExclusiveGroup(self):
        mainGroupBox = QGroupBox("Hierarchy")
	outerGroupBox = QGroupBox()
	innerGroupBox = QGroupBox()
	scrollTabWidget = QTabWidget()
	scrollTab1 = QWidget()
	scrollTab2 = QWidget()
	scrollTab3 = QWidget()
	scrollTab4 = QWidget()
	scrollTab5 = QWidget()
	
#	self.info.setStyleSheet("background-color: #FFFFFF;color: #000")
	
	self.applyChangesButton = QPushButton()
	self.cancelButton = QPushButton()
	
	self.hierarchyContainer = QTextBrowser()
	
#	self.scrollLayout = QGridLayout()
#	self.scrollWidget = QWidget()
#	self.scrollWidget.resize(200, 600)
 #       self.scrollWidget.setLayout(self.scrollLayout)
	self.scrollAreaOuter = QScrollArea(outerGroupBox)
        self.scrollAreaOuter.setWidgetResizable(True)
        self.scrollAreaOuter.setWidget(scrollTabWidget)
	
	self.scrollAreaInner = QScrollArea(innerGroupBox)
        self.scrollAreaInner.setWidgetResizable(True)
        self.scrollAreaInner.setWidget(self.hierarchyContainer)
	
	self.scrollAreaInnerWidgetContents = QWidget(self.scrollAreaInner)
	self.scrollAreaInnerWidgetContents.setGeometry(QRect(0, 0, 701, 292))
#	self.scrollAreaInnerWidgetContents.setObjectName(_fromUtf8("scrollAreaInnerWidgetContents"))
	self.dockWidget = QDockWidget(scrollTabWidget)
	self.verticalLayout = QVBoxLayout(self.scrollAreaInnerWidgetContents)
	
	self.hbox = QHBoxLayout(scrollTab1)
	self.innerBox = QHBoxLayout(self.scrollAreaInner)
#	self.hbox.addStretch(1)
	
	self.vbox = QVBoxLayout(scrollTab1)
#	self.vbox.addStretch(1)
	self.vbox.addLayout(self.hbox)
	
	scrollTabWidget.addTab(scrollTab1, "On")
	scrollTabWidget.addTab(scrollTab2, "Controls")
	scrollTabWidget.addTab(scrollTab3, "PDS")
	scrollTabWidget.addTab(scrollTab4, "Snap")
	scrollTabWidget.addTab(scrollTab5, "Rig Tools")
	self.vbox.addWidget(self.scrollAreaOuter)
	self.verticalLayout.addWidget(self.dockWidget)
	
#	self.centralWidget = QWidget()
#       self.centralWidget.setLayout(self.vbox)
#	self.setCentralWidget(self.centralWidget)

#        radio1.setChecked(True)

#        vbox = QtGui.QVBoxLayout()
#        vbox.addWidget(radio1)
#        vbox.addWidget(radio2)
#        vbox.addWidget(radio3)
#        vbox.addStretch(1)
        mainGroupBox.setLayout(self.vbox)

        return mainGroupBox

    def createThirdExclusiveGroup(self):
        settingPresetGroupBox = QGroupBox("Setting Presets")
	
	self.settingPresetDropDown = QToolButton(self)
	self.settingPresetDropDown.setPopupMode(QToolButton.MenuButtonPopup)
	self.settingPresetDropDown.setMenu(QMenu(self.settingPresetDropDown))
	self.settingPresetTextBox = QTextBrowser(self)
	self.settingPresetAction1 = QWidgetAction(self.settingPresetDropDown)
	self.settingPresetAction1.setDefaultWidget(self.settingPresetTextBox)
	self.settingPresetDropDown.menu().addAction(self.settingPresetAction1)
	self.settingPresetDropDown.setText("Shoot")
	self.settingPresetDropDown.setMinimumSize(300, 20)
	
#	self.info.setStyleSheet("background-color: #FFFFFF;color: #000")
	
	self.saveButton = QPushButton()
	self.saveButton.setGeometry(QRect(12, 10, 20, 30))
	self.saveButton.setIcon(QIcon("/home/jlogsdon/Icons/floppyDiskIcon_charVui2.jpg"))
	self.trashButton = QPushButton()
	self.trashButton.setGeometry(QRect(12, 20, 20, 31))
	self.trashButton.setIcon(QIcon("/home/jlogsdon/Icons/trashIcon_charVui2.png"))
	
	
	self.hbox = QHBoxLayout()
#	self.hbox.addStretch(1)
	
	self.hbox.addWidget(self.settingPresetDropDown)
	self.hbox.addWidget(self.saveButton)
	self.hbox.addWidget(self.trashButton)

        settingPresetGroupBox.setLayout(self.hbox)

        return settingPresetGroupBox

    def createPushButtonGroup(self):
        buttonGroupBox = QGroupBox()
        buttonGroupBox.setCheckable(False)
        buttonGroupBox.setChecked(False)

        applyChangesButton = QPushButton("Apply Changes")
	applyChangesButton.setGeometry(QRect(12, 10, 20, 100))
	applyChangesButton.setMinimumSize(10, 40)
	
	cancelButton = QPushButton("Cancel")
	cancelButton.setGeometry(QRect(12, 10, 20, 100))
	cancelButton.setMinimumSize(10, 40)

        hbox = QHBoxLayout()
        hbox.addWidget(applyChangesButton)
	hbox.addWidget(cancelButton)
#        vbox.addStretch(1)
        buttonGroupBox.setLayout(hbox)

        return buttonGroupBox


if __name__ == '__main__':

    import sys

    app = QApplication(sys.argv)
    clock = Window()
    clock.show()
    sys.exit(app.exec_())
    