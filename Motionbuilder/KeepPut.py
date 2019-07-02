from pyfbsdk import *
from pyfbsdk_additions import *
import time

class KeepPut():
    def __init__(self):

        global startRegion, editStart, buttonStart, stopRegion, editStop, buttonStop, buttonAction, userPoseRegion, editUserPose, lSystem, lPlayer, lEndTime, lEndFrame, lStartTime, lStartFrame
        
        startRegion = FBLabel()
        editStart = FBEditNumber()
        buttonStart = FBButton()
        stopRegion = FBLabel()
        editStop = FBEditNumber()
        buttonStop = FBButton()
        userPoseRegion = FBLabel()
        editUserPose = FBEditNumber()
        buttonAction = FBButton()

        lSystem = FBSystem()
        lPlayer = FBPlayerControl()
        lEndTime = lSystem.CurrentTake.LocalTimeSpan.GetStop()
        lEndFrame = lSystem.CurrentTake.LocalTimeSpan.GetStop().GetFrame(True)
        lStartTime = lSystem.CurrentTake.LocalTimeSpan.GetStart()
        lStartFrame = lSystem.CurrentTake.LocalTimeSpan.GetStart().GetFrame(True)
        

    def keepPutUI(self, t):
        currentTime = lSystem.LocalTime.GetFrame()
    #Start Text
        x = FBAddRegionParam(15,FBAttachType.kFBAttachNone,"")
        y = FBAddRegionParam(15,FBAttachType.kFBAttachNone,"")
        w = FBAddRegionParam(80,FBAttachType.kFBAttachNone,"")
        h = FBAddRegionParam(25,FBAttachType.kFBAttachNone,"")
        t.AddRegion("startRegion","startRegion", x, y, w, h)

        t.SetControl("startRegion", startRegion)
        startRegion.Visible = True
        startRegion.ReadOnly = False
        startRegion.Enabled = True
        startRegion.Hint = ""
        startRegion.Caption = "Start"
        startRegion.Style = FBTextStyle.kFBTextStyleNone
        startRegion.Justify = FBTextJustify.kFBTextJustifyLeft
        startRegion.WordWrap = True

    #Start Value Field    
        x = FBAddRegionParam(70,FBAttachType.kFBAttachNone,"")
        y = FBAddRegionParam(15,FBAttachType.kFBAttachNone,"")
        w = FBAddRegionParam(80,FBAttachType.kFBAttachNone,"")
        h = FBAddRegionParam(25,FBAttachType.kFBAttachNone,"")
        t.AddRegion("editStart","editStart", x, y, w, h)

        t.SetControl("editStart", editStart)
        editStart.Value = lStartFrame
        editStart.Min = lStartFrame
        editStart.Max = lEndFrame
        editStart.Precision = 0.000000
        editStart.LargeStep = 5.000000
        editStart.SmallStep = 1.000000

    #Start Assign Button
        x = FBAddRegionParam(160,FBAttachType.kFBAttachNone,"")
        y = FBAddRegionParam(15,FBAttachType.kFBAttachNone,"")
        w = FBAddRegionParam(80,FBAttachType.kFBAttachNone,"")
        h = FBAddRegionParam(25,FBAttachType.kFBAttachNone,"")
        t.AddRegion("buttonStart","buttonStart", x, y, w, h)

        t.SetControl("buttonStart", buttonStart)
        buttonStart.Visible = True
        buttonStart.ReadOnly = False
        buttonStart.Enabled = True
        buttonStart.Hint = ""
        buttonStart.Caption = "Use Current"
        buttonStart.State = 0
        buttonStart.Style = FBButtonStyle.kFBPushButton
        buttonStart.Justify = FBTextJustify.kFBTextJustifyCenter
        buttonStart.Look = FBButtonLook.kFBLookNormal
        buttonStart.OnClick.Add(self.startButtonEvent)

    #Stop Text
        x = FBAddRegionParam(15,FBAttachType.kFBAttachNone,"")
        y = FBAddRegionParam(45,FBAttachType.kFBAttachNone,"")
        w = FBAddRegionParam(80,FBAttachType.kFBAttachNone,"")
        h = FBAddRegionParam(25,FBAttachType.kFBAttachNone,"")
        t.AddRegion("stopRegion","stopRegion", x, y, w, h)

        t.SetControl("stopRegion", stopRegion)
        stopRegion.Visible = True
        stopRegion.ReadOnly = False
        stopRegion.Enabled = True
        stopRegion.Hint = ""
        stopRegion.Caption = "Stop"
        stopRegion.Style = FBTextStyle.kFBTextStyleNone
        stopRegion.Justify = FBTextJustify.kFBTextJustifyLeft
        stopRegion.WordWrap = True

    #Stop Value Field
        x = FBAddRegionParam(70,FBAttachType.kFBAttachNone,"")
        y = FBAddRegionParam(45,FBAttachType.kFBAttachNone,"")
        w = FBAddRegionParam(80,FBAttachType.kFBAttachNone,"")
        h = FBAddRegionParam(25,FBAttachType.kFBAttachNone,"")
        t.AddRegion("editStop","editStop", x, y, w, h)

        t.SetControl("editStop", editStop)
        editStop.Value = lEndFrame
        editStop.Min = lStartFrame
        editStop.Max = lEndFrame
        editStop.Precision = 0.000000
        editStop.LargeStep = 5.000000
        editStop.SmallStep = 1.000000

    #Stop Assign Button
        x = FBAddRegionParam(160,FBAttachType.kFBAttachNone,"")
        y = FBAddRegionParam(45,FBAttachType.kFBAttachNone,"")
        w = FBAddRegionParam(80,FBAttachType.kFBAttachNone,"")
        h = FBAddRegionParam(25,FBAttachType.kFBAttachNone,"")
        t.AddRegion("buttonStop","buttonStop", x, y, w, h)

        t.SetControl("buttonStop", buttonStop)
        buttonStop.Visible = True
        buttonStop.ReadOnly = False
        buttonStop.Enabled = True
        buttonStop.Hint = ""
        buttonStop.Caption = "Use Current"
        buttonStop.State = 0
        buttonStop.Style = FBButtonStyle.kFBPushButton
        buttonStop.Justify = FBTextJustify.kFBTextJustifyCenter
        buttonStop.Look = FBButtonLook.kFBLookNormal
        buttonStop.OnClick.Add(self.stopButtonEvent)

    #User Pose Text
        x = FBAddRegionParam(15,FBAttachType.kFBAttachNone,"")
        y = FBAddRegionParam(90,FBAttachType.kFBAttachNone,"")
        w = FBAddRegionParam(80,FBAttachType.kFBAttachNone,"")
        h = FBAddRegionParam(25,FBAttachType.kFBAttachNone,"")
        t.AddRegion("userPoseRegion","userPoseRegion", x, y, w, h)

        t.SetControl("userPoseRegion", userPoseRegion)
        userPoseRegion.Visible = True
        userPoseRegion.ReadOnly = False
        userPoseRegion.Enabled = True
        userPoseRegion.Hint = ""
        userPoseRegion.Caption = "Desired Pose"
        userPoseRegion.Style = FBTextStyle.kFBTextStyleNone
        userPoseRegion.Justify = FBTextJustify.kFBTextJustifyLeft
        userPoseRegion.WordWrap = True

    #User Pose Value Field
        x = FBAddRegionParam(100,FBAttachType.kFBAttachNone,"")
        y = FBAddRegionParam(85,FBAttachType.kFBAttachNone,"")
        w = FBAddRegionParam(80,FBAttachType.kFBAttachNone,"")
        h = FBAddRegionParam(25,FBAttachType.kFBAttachNone,"")
        t.AddRegion("editUserPose","editUserPose", x, y, w, h)

        t.SetControl("editUserPose", editUserPose)
        editUserPose.Value = currentTime
        editUserPose.Min = lStartFrame
        editUserPose.Max = lEndFrame
        editUserPose.Precision = 0.000000
        editUserPose.LargeStep = 5.000000
        editUserPose.SmallStep = 1.000000

    #Run Button
        x = FBAddRegionParam(15,FBAttachType.kFBAttachNone,"")
        y = FBAddRegionParam(155,FBAttachType.kFBAttachNone,"")
        w = FBAddRegionParam(110,FBAttachType.kFBAttachNone,"")
        h = FBAddRegionParam(30,FBAttachType.kFBAttachNone,"")
        t.AddRegion("buttonAction","buttonAction", x, y, w, h)

        t.SetControl("buttonAction", buttonAction)
        buttonAction.Visible = True
        buttonAction.ReadOnly = False
        buttonAction.Enabled = True
        buttonAction.Hint = ""
        buttonAction.Caption = "Keep Put!"
        buttonAction.State = 0
        buttonAction.Style = FBButtonStyle.kFBPushButton
        buttonAction.Justify = FBTextJustify.kFBTextJustifyCenter
        buttonAction.Look = FBButtonLook.kFBLookNormal
        buttonAction.OnClick.Add(self.actionButtonEvent)

        
    def startButtonEvent(self, control, event):
        time = FBSystem().LocalTime
        frame = time.GetFrame(True)
        editStart.Value = frame


    def stopButtonEvent(self, control, event):
        time = FBSystem().LocalTime
        frame = time.GetFrame(True)
        editStop.Value = frame
        
        
    def checkTimespan(self, timespan, time):
        if (time > timespan.GetStart() and time < timespan.GetStop() ):
            return True
        
        return False


    def runFCurveAlter(self, curve, currentTime, startTime, stopTime):
        '''if editUserPose.Value == lStartFrame:
            value = curve.Evaluate(currentTime)

        else:
            value = editUserPose.Value'''
        
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
        currentTime = FBSystem().LocalTime
        startTime = FBTime(0,0,0, int(editStart.Value) )
        stopTime = FBTime(0,0,0, int(editStop.Value) )
        
        models = FBModelList()
        FBGetSelectedModels(models)
        
        for model in models:
            animNode = model.Translation.GetAnimationNode()
            for node in animNode.Nodes:
                if node.FCurve:
                    self.runFCurveAlter(node.FCurve, currentTime, startTime, stopTime)
        
    def main(self):
        t = FBCreateUniqueTool("KeepPut v 1.0.0")
        t.StartSizeX = 275
        t.StartSizeY = 250
        self.keepPutUI(t)
        ShowTool(t)


KeepPut().main()
