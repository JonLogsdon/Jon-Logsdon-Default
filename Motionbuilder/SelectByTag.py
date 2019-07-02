"""
***************************************************************************************
_mobu.tools.common.tech.selectByTag.selectByTag.py

Desc: This script allows the user to find, and select, an object in Motionbuilder 
        by a "tag" of the name of the object they are searching for.
            
Lang: Python
Comments: All objects in the scene that have a tag matching what is entered 
                will be selected.
Author: Jonathan Logsdon 2013 jlogsdon@playstation.sony.com
***************************************************************************************
"""


from pyfbsdk import *
from _pythonidelib import *
from pyfbsdk_additions import *

import _mobu.lib.selection.selection as selection
reload(selection)


class SelectByTag():
    def __init__(self):
        self.SEL=selection.Selection()
        self.groups = FBSystem().Scene.Groups
        
    def selectModels(self, pRoot, pPattern):
        """Selects objects based on the user input."""
        
        if pRoot and pPattern:        
            pPattern = pPattern.lower()
            for lChild in pRoot.Children:
                lChildName = lChild.LongName.lower()            
                if lChildName.find(pPattern) != -1:
                    lChild.Selected = True
                    print "Object Name = %s" % lChild.LongName
                
                # Recurse.
                self.selectModels(lChild, pPattern)
                
            for group in self.groups:
                groupName = group.Name            
                if groupName.find(pPattern) != -1:
                    group.Selected = True
                    print "Object Name = %s" % group.Name
    
    def userInput(self):
        """Message box prompting user to input a tag for the desired object(s) the 
        user is searching for."""
        
        (lRes, lPattern) = FBMessageBoxGetUserValue( 
            "Select by Name", 
            "Select All Objects by Name(s) Containing:\n- search is not case sensitive -",
             "", 
             FBPopupInputType.kFBPopupString, 
             "OK", 
             "Cancel" )
        
        if lPattern and lRes == 1:
            lScene = FBSystem().Scene
            self.SEL.unSelectAll()
            self.selectModels(lScene.RootModel, lPattern)
            print lPattern
            
            del(lScene)
        
    def main(self):
        """Runs the tool."""
        
        self.userInput()
SelectByTag().main()
         