"""
Plant keys for jittering mocap animation, such as for the feet or hands.

*Commands:* ::
    >>> KeyTools().main()
    
*Author:*
    * Jonathan Logsdon, jon.logsdon@dsvolition.com, Feb. 24, 2014, 9:40 AM

"""

# Python std lib
import time
import os

# PySide
import PySide.QtCore
import PySide.QtGui
import PySide.QtUiTools

# Motionbuilder lib
from pyfbsdk import *
from pyfbsdk_additions import *

lApplication = FBApplication()
lCharacter = lApplication.CurrentCharacter        
lSystem = FBSystem()
lOriginalTake = lSystem.CurrentTake.Name
lPlayer = FBPlayerControl()
lEndTime = lSystem.CurrentTake.LocalTimeSpan.GetStop()
lEndFrame = lEndTime.GetFrame()
lStartTime = lSystem.CurrentTake.LocalTimeSpan.GetStart()
lStartFrame = lStartTime.GetFrame()

UI_FILE_PATH = os.path.join(r'C:\Users\jon.logsdon\Scripts\Mobu\KeyingToolsUI.ui')

loader = PySide.QtUiTools.QUiLoader() 
keyToolsWidget = loader.load(UI_FILE_PATH)

class KeyToolsUI(PySide.QtGui.QMainWindow):
    def __init__(self, parent=None):
        super(KeyToolsUI, self).__init__(parent)

        layout = PySide.QtGui.QVBoxLayout()
        layout.addWidget(keyToolsWidget)
        self.setLayout(layout) 
        
        plantKeys = PlantKeys()
        slidingKeys = SlidingKeys()
        freeKeys = FreeKeys()
        
        keyToolsWidget.show()
        keyToolsWidget.raise_()
        
class PlantKeys(PySide.QtGui.QMainWindow):
    def __init__(self, parent=None):
        super(PlantKeys, self).__init__(parent)
        
        self.plantKeysTab = keyToolsWidget.plantKeysTab
        self.plantDesiredPoseEdit = keyToolsWidget.plantDesiredPoseEdit
        self.plantEndCurrentBut = keyToolsWidget.plantEndCurrentBut
        self.plantEndFrameEdit = keyToolsWidget.plantEndFrameEdit
        self.plantRunBut = keyToolsWidget.plantRunBut
        self.plantStartCurrentBut = keyToolsWidget.plantStartCurrentBut
        self.plantStartFrameEdit = keyToolsWidget.plantStartFrameEdit
        
        self.plantEndCurrentBut.clicked.connect(self.stopButtonEvent)
        self.plantRunBut.clicked.connect(self.actionButtonEvent)
        self.plantStartCurrentBut.clicked.connect(self.startButtonEvent)
        
        self.plantDesiredPoseEdit.setAlignment(PySide.QtCore.Qt.AlignCenter)
        self.plantDesiredPoseEdit.setText(str(lStartFrame))
        
        self.plantEndFrameEdit.setAlignment(PySide.QtCore.Qt.AlignCenter)
        self.plantEndFrameEdit.setText(str(lEndFrame))
        
        self.plantStartFrameEdit.setAlignment(PySide.QtCore.Qt.AlignCenter)
        self.plantStartFrameEdit.setText(str(lStartFrame))
        FBSystem().Scene.Evaluate()
        
    def startButtonEvent(self):
        #Set time and get start frame
        time = FBSystem().LocalTime
        frame = time.GetFrame()
        self.plantStartFrameEdit.setText(str(frame))
        FBSystem().Scene.Evaluate()


    def stopButtonEvent(self, control, event):
        #Set time and get end frame
        time = FBSystem().LocalTime
        frame = time.GetFrame()
        self.plantEndFrameEdit.setText(str(frame))
        
        
    def checkTimespan(self, timespan, time):
        #Check the timespan between start and stop frame
        if (time > timespan.GetStart() and time < timespan.GetStop() ):
            return True
        
        return False


    def runFCurveAlter(self, curve, currentTime, startTime, stopTime):
        #Smooth curve(s) of selected objects according to desired pose
        value = curve.Evaluate(currentTime)           
        count = len(curve.Keys)
        
        startKeyAdd = curve.KeyAdd(startTime, value)
        stopKeyAdd = curve.KeyAdd(stopTime, value)
        
        if startKeyAdd >= 0: 
            curve.Keys[startKeyAdd].TangentMode = FBTangentMode.kFBTangentModeUser
            curve.Keys[startKeyAdd].LeftDerivative = 0.0
            curve.Keys[startKeyAdd].RightDerivative = 0.0

        if stopKeyAdd >= 0: 
            curve.Keys[stopKeyAdd].TangentMode = FBTangentMode.kFBTangentModeUser   
            curve.Keys[stopKeyAdd].LeftDerivative = 0.0
            curve.Keys[stopKeyAdd].RightDerivative = 0.0
        
    def actionButtonEvent(self, control, event):
        #Runs tool based on user inputs of start and end frame, and frame of desired pose
        currentTime = FBSystem().LocalTime
        startTime = FBTime(0,0,0, int(self.editStart.Value) )
        stopTime = FBTime(0,0,0, int(self.editStop.Value) )
        
        models = FBModelList()
        FBGetSelectedModels(models)
        
        for model in models:
            animNode = model.Translation.GetAnimationNode()
            for node in animNode.Nodes:
                if node.FCurve:
                    self.runFCurveAlter(node.FCurve, currentTime, startTime, stopTime)
                    
    
class SlidingKeys:
    def __init__(self):
        self.slideKeysTab = keyToolsWidget.slideKeysTab
        self.slideDesiredPoseEdit = keyToolsWidget.slideDesiredPoseEdit
        self.slideEndCurrentBut = keyToolsWidget.slideEndCurrentBut
        self.slideEndFrameEdit = keyToolsWidget.slideEndFrameEdit
        self.slideRunBut = keyToolsWidget.slideRunBut
        self.slideStartCurrentBut = keyToolsWidget.slideStartCurrentBut
        self.slideStartFrameEdit = keyToolsWidget.slideStartFrameEdit
        
        self.slideEndCurrentBut.clicked.connect(self.stopButtonEvent)
        self.slideRunBut.clicked.connect(self.actionButtonEvent)
        self.slideStartCurrentBut.clicked.connect(self.startButtonEvent)
        
        self.slideDesiredPoseEdit.setAlignment(PySide.QtCore.Qt.AlignCenter)
        self.slideDesiredPoseEdit.setText(str(lStartFrame))
        
        self.slideEndFrameEdit.setAlignment(PySide.QtCore.Qt.AlignCenter)
        self.slideEndFrameEdit.setText(str(lEndFrame))
        
        self.slideStartFrameEdit.setAlignment(PySide.QtCore.Qt.AlignCenter)
        self.slideStartFrameEdit.setText(str(lStartFrame))
        FBSystem().Scene.Evaluate()
        
    def startButtonEvent(self, control, event):
        #Set time and get start frame
        time = FBSystem().LocalTime
        frame = time.GetFrame()
        self.editStart.Value = frame


    def stopButtonEvent(self, control, event):
        #Set time and get end frame
        time = FBSystem().LocalTime
        frame = time.GetFrame()
        self.editStop.Value = frame
        
        
    def checkTimespan(self, timespan, time):
        #Check the timespan between start and stop frame
        if (time > timespan.GetStart() and time < timespan.GetStop() ):
            return True
        
        return False


    def runFCurveAlter(self, curve, currentTime, startTime, stopTime):
        #Smooth curve(s) of selected objects according to desired pose
        value = curve.Evaluate(currentTime)           
        count = len(curve.Keys)
        
        startKeyAdd = curve.KeyAdd(startTime, value)
        stopKeyAdd = curve.KeyAdd(stopTime, value)
        
        if startKeyAdd >= 0: 
            curve.Keys[startKeyAdd].TangentMode = FBTangentMode.kFBTangentModeUser
            curve.Keys[startKeyAdd].LeftDerivative = 0.0
            curve.Keys[startKeyAdd].RightDerivative = 0.0

        if stopKeyAdd >= 0: 
            curve.Keys[stopKeyAdd].TangentMode = FBTangentMode.kFBTangentModeUser   
            curve.Keys[stopKeyAdd].LeftDerivative = 0.0
            curve.Keys[stopKeyAdd].RightDerivative = 0.0
        
    def actionButtonEvent(self, control, event):
        #Runs tool based on user inputs of start and end frame, and frame of desired pose
        currentTime = FBSystem().LocalTime
        startTime = FBTime(0,0,0, int(self.editStart.Value) )
        stopTime = FBTime(0,0,0, int(self.editStop.Value) )
        
        models = FBModelList()
        FBGetSelectedModels(models)
        
        for model in models:
            animNode = model.Translation.GetAnimationNode()
            for node in animNode.Nodes:
                if node.FCurve:
                    self.runFCurveAlter(node.FCurve, currentTime, startTime, stopTime)
                    
                    
class FreeKeys:
    def __init_(self):
        self.freeKeysTab = keyToolsWidget.freeKeysTab
        self.freeDesiredPoseEdit = keyToolsWidget.freeDesiredPoseEdit
        self.freeEndCurrentBut = keyToolsWidget.freeEndCurrentBut
        self.freeEndCurrentEdit = keyToolsWidget.freeEndCurrentEdit
        self.freeRunBut = keyToolsWidget.freeRunBut
        self.freeStartCurrentBut = keyToolsWidget.freeStartCurrentBut
        self.freeStartFrameEdit = keyToolsWidget.freeStartFrameEdit
        
        
    def startButtonEvent(self, control, event):
        #Set time and get start frame
        time = FBSystem().LocalTime
        frame = time.GetFrame()
        self.editStart.Value = frame


    def stopButtonEvent(self, control, event):
        #Set time and get end frame
        time = FBSystem().LocalTime
        frame = time.GetFrame()
        self.editStop.Value = frame
        
        
    def checkTimespan(self, timespan, time):
        #Check the timespan between start and stop frame
        if (time > timespan.GetStart() and time < timespan.GetStop() ):
            return True
        
        return False


    def runFCurveAlter(self, curve, currentTime, startTime, stopTime):
        #Smooth curve(s) of selected objects according to desired pose
        value = curve.Evaluate(currentTime)           
        count = len(curve.Keys)
        
        startKeyAdd = curve.KeyAdd(startTime, value)
        stopKeyAdd = curve.KeyAdd(stopTime, value)
        
        if startKeyAdd >= 0: 
            curve.Keys[startKeyAdd].TangentMode = FBTangentMode.kFBTangentModeUser
            curve.Keys[startKeyAdd].LeftDerivative = 0.0
            curve.Keys[startKeyAdd].RightDerivative = 0.0

        if stopKeyAdd >= 0: 
            curve.Keys[stopKeyAdd].TangentMode = FBTangentMode.kFBTangentModeUser   
            curve.Keys[stopKeyAdd].LeftDerivative = 0.0
            curve.Keys[stopKeyAdd].RightDerivative = 0.0
        
    def actionButtonEvent(self, control, event):
        #Runs tool based on user inputs of start and end frame, and frame of desired pose
        currentTime = FBSystem().LocalTime
        startTime = FBTime(0,0,0, int(self.editStart.Value) )
        stopTime = FBTime(0,0,0, int(self.editStop.Value) )
        
        models = FBModelList()
        FBGetSelectedModels(models)
        
        for model in models:
            animNode = model.Translation.GetAnimationNode()
            for node in animNode.Nodes:
                if node.FCurve:
                    self.runFCurveAlter(node.FCurve, currentTime, startTime, stopTime)
        
        
MainWindow = KeyToolsUI()
