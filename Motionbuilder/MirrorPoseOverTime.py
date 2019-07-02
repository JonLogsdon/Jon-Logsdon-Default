from pyfbsdk import *
import time


class MirrorPoseOT:
    def __init__(self):
        # find the current character
        lApplication = FBApplication()
        lCharacter = lApplication.CurrentCharacter
        
        # find the Current take 
        lSystem = FBSystem()
        lOriginalTake = lSystem.CurrentTake.Name
        
        # get the Player
        lPlayer = FBPlayerControl()
        
        # Set the endTime
        lEndTime = lSystem.CurrentTake.LocalTimeSpan.GetStop()
        lEndFrame = lSystem.CurrentTake.LocalTimeSpan.GetStop().GetFrame()
        lStartFrameTime = lSystem.CurrentTake.LocalTimeSpan.GetStart()
        lStartFrame = lSystem.CurrentTake.LocalTimeSpan.GetStart().GetFrame()
        
        
    def switchTake (self, pTakeName):
        destName= pTakeName
        for take in lSystem.Scene.Takes:
            if take.Name == destName:
                lSystem.CurrentTake = take

    def setPoseOpts(self):
        self.switchTake(pTakeName)
        # create a new take for new animation
        lAnimPoseTake = lOriginalTake + ' mirror ' + str( lSystem.SystemTime.GetTimeString() )
        lNewTake = FBTake(lAnimPoseTake)
        lNewTake = lNewTake.CopyTake(lAnimPoseTake)

        # set pose options 
        poseOptions = FBCharacterPoseOptions()
        poseOptions.mCharacterPoseKeyingMode = FBCharacterPoseKeyingMode.kFBCharacterPoseKeyingModeFullBody
        poseOptions.SetFlag(FBCharacterPoseFlag.kFBCharacterPoseMirror, True)
        
    def startPoseOverTime(self):
        # set the character keying mode
        lCharacter.KeyingMode=FBCharacterKeyingMode.kFBCharacterKeyingFullBody
        
        # start the pose over time sequence
        lScene = lSystem.Scene
        lStop = int(lEndFrame)
        lRange = int(lEndFrame)+1
        lTime = lStartFrameTime
        lStart = int(lStartFrame)
        lProgress = lRange - lStart
        FBKeyControl().AutoKey = True

        # Create a FBProgress object and set default values for the caption and text.
        lFbp = FBProgress()
        lFbp.Caption = "Mirroring "
        lFbp.Text = "over time ..."
        lCount = 0.0
    
for i in range(lRange):
    ##ENSURE THAT THE TIME IS CORRECT
    timeout = False
    lPlayer.Goto(lTime)
    while not lPlayer.Goto(lTime)or timeout:
        time.sleep(1)
        lSystem.Scene.Evaluate()
        if timeout>5:
            print "Unable to Go to time "+lTime.GetTimeString()
            break
        timeout+=1

    # copy pose    
    poseName = 'CharacterPose_'+str(i)
    targetPose = FBCharacterPose(poseName)

    lSystem.Scene.Evaluate() 
    targetPose.CopyPose(lCharacter)
    
    # Switch to target Take
    switchTake(lAnimPoseTake)
    lSystem.Scene.Evaluate()
    targetPose.PastePose(lCharacter, poseOptions )
    lSystem.Scene.Evaluate()
    lPlayer.Key()
    lSystem.Scene.Evaluate()
    # Switch to Original Take
    switchTake(lOriginalTake)

    #Delete the pose, 
    targetPose.FBDelete()

    #step forward one frame
    lTime.Set(lTime.Get() + FBTime(0,0,0,1).Get())

    lCount += 1
    lVal = lCount / lProgress * 100            
    lFbp.Percent = int(lVal)
    
lFbp.FBDelete()
switchTake(lAnimPoseTake)
lSetTimeSpan = FBTimeSpan(FBTime(0,0,0,lStart),FBTime(0,0,0,lStop) )
lSystem.CurrentTake.LocalTimeSpan = lSetTimeSpan

FBKeyControl().AutoKey = False
lPlayer.GotoStart()

