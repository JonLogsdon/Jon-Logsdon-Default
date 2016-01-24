"""
This is the main Animation Exporter from Motionbuilder.

*Examples:* ::

	>>> import anim_exporter
	>>> MainWindow = Anim_Exporter()
"""

# Python std lib
import re
import os
import sys

# PySide
import PySide.QtCore
import PySide.QtGui
import PySide.QtUiTools
import pysideuic

# Common tools API
import core
import file_io.v_path
import diagnostics.dcc_logger

# Motionbuilder lib
from pyfbsdk import *
from pyfbsdk_additions import *
import mbdebugger

import vmobu


UI_FILE_PATH = os.path.join(r'D:\projects\ctg\main\ctg\src\tools\Python\packages\vlib\dcc\ui\anim_exporter.ui')
ICON_PATH = os.path.join(r'D:\projects\ctg\main\ctg\src\tools\Python\packages\vlib\dcc\icons\anim_exporter')
VERSION = 3.0
STATUS_TIMEOUT = 3000
DEBUG = False

class Anim_Exporter(PySide.QtGui.QMainWindow):
  def __init__(self, parent=None):
    #Call .ui file for anim_exporter, and load it into MB space
    global anim_names, aeWidget, uiFile, project_dir, scene
    sys = FBSystem()
    scene = sys.Scene
    
    super(Anim_Exporter, self).__init__(parent)
    
    loader = PySide.QtUiTools.QUiLoader()  
    aeWidget = loader.load(UI_FILE_PATH)
    
    self.setAttribute( PySide.QtCore.Qt.WA_DeleteOnClose )
    
    export_path = None
    
    #Instance variables
    self.anim_node = None
    self.anim_controller = None
    self.master = None
    self.time_call_back_id = None
    self.after_new_call_back_id = None
    self.after_open_call_back_id = None
    self.after_import_call_back_id = None
    self.anim_nodes = None
    self.anim_node_exporter = None
    
    self.stored_anim_dir = None
    self.stored_anim_data = None
    self.stored_weightList = None
    
    self.bone_list = None
    self.prop_list = None

    
    #Get project directory
    project_dir = core.const.workspace_dir
    batch_dir = project_dir  
    
    self.auto_fix = False
    self.quiet = False
    
    #Connect with UI classes
    self.tabWidget = aeWidget.tabWidget
    self.projectLineEdit = aeWidget.projectLineEdit
    self.characterComboUI = aeWidget.characterComboUI
    self.exportGroupBoxUI = aeWidget.exportGroupBox
    self.updateButtonUI = aeWidget.updateButtonUI
    self.animxExportSelUI = aeWidget.animxExportSelUI
    self.addAnimationButtonUI = aeWidget.addAnimationButtonUI
    self.deleteAnimationButtonUI = aeWidget.deleteAnimationButtonUI
    self.animxCopyUI = aeWidget.animxCopyUI
    self.animxPasteUI = aeWidget.animxPasteUI
    self.animListUI = aeWidget.animListUI   
    self.exportDirUI = aeWidget.exportDirUI
    self.batchDir = aeWidget.batchDir
    self.animxBrowseUI = aeWidget.animxBrowseUI
    self.boneGroupTableUI = aeWidget.boneGroupTableUI
    self.setTimerangeButtonUI = aeWidget.setTimerangeButtonUI
    self.batchButton = aeWidget.batchButton
    self.browseButton = aeWidget.browseButton
    
    self.endTime = FBSystem().CurrentTake.LocalTimeSpan.GetStop()
    self.endFrame = FBSystem().CurrentTake.LocalTimeSpan.GetStop().GetFrame()
    self.startTime = FBSystem().CurrentTake.LocalTimeSpan.GetStart()
    self.startFrame = FBSystem().CurrentTake.LocalTimeSpan.GetStart().GetFrame()    
    
    self.animListUI.setColumnWidth(0, 200)
    for i in range(1, 5):
      self.animListUI.setColumnWidth(i, 60)
      
    self.boneGroupTableUI.setColumnWidth(1, 70)
    
    self.addAnimationButtonUI.clicked.connect(self.add_animation)
    self.setTimerangeButtonUI.clicked.connect(self.setCurrentTableTimerange)
    self.batchButton.clicked.connect(self.batch_process)
    self.animxExportSelUI.clicked.connect(self.animExportSel)
    self.animxBrowseUI.clicked.connect(self.browseExportDirs)
    self.updateButtonUI.clicked.connect(self.refresh_anim_node)
    self.browseButton.clicked.connect(self.browseBatchDirs)
    
    
    self.exportDirUI.setText('')
  
    #Call the loading of the widget function
    self.loadCustomWidget()
    
  def add_animation(self):
    self.add_anim_row()
    
  def add_anim_row(self):
    self.refresh_anim_node()
    
    self.animListUI.insertRow(0)
    item = PySide.QtGui.QTableWidgetItem()
    self.animListUI.setItem(0, 0, item)
    
    self.setTakeProperties()
    self.storeAnimTakes()
    
  def setTakeProperties(self, row=None):
    global startFrameText, startFrameWidgetItem, startFrameItem
    FBSystem().Scene.Evaluate()
    if row is None:
      row = 0
      col = 0
    else:
      row = self.animListUI.currentRow()
      col = self.animListUI.currentColumn()
      
    currTake = vmobu.core.get_current_take()
    
    takeNameWidgetItem = PySide.QtGui.QTableWidgetItem()
    takeNameItem = self.animListUI.setItem(0, 0, takeNameWidgetItem)    
    takeNameWidgetItem.setText(currTake.Name)
    
    currSel = FBModelList()
    FBGetSelectedModels(currSel)
    for sel in currSel:
      if sel.PropertyList.Find('p_export_rampin') != "":
        rigRampIn = sel.PropertyList.Find('p_export_rampin')
        rigRampOut = sel.PropertyList.Find('p_export_rampout')
        rigFrameRate = sel.PropertyList.Find('p_export_framerate')
      else:  
        print "There is no Master control to selection."
      
    rampInWidgetItem = PySide.QtGui.QTableWidgetItem()
    rampInItem = self.animListUI.setItem(row, 3, rampInWidgetItem)
    rampInWidgetItem.setText(str(rigRampIn))
    
    rampOutWidgetItem = PySide.QtGui.QTableWidgetItem()
    rampOutItem = self.animListUI.setItem(row, 4, rampOutWidgetItem)
    rampOutWidgetItem.setText(str(rigRampOut))    
    
    framerateWidgetItem = PySide.QtGui.QTableWidgetItem()
    framerateItem = self.animListUI.setItem(row, 5, framerateWidgetItem)
    framerateWidgetItem.setText(str(rigFrameRate))
    
    start = FBSystem().CurrentTake.LocalTimeSpan.GetStart().GetFrame() 
    end = FBSystem().CurrentTake.LocalTimeSpan.GetStop().GetFrame()      
    
    startFrameWidgetItem = PySide.QtGui.QTableWidgetItem()
    startFrameItem = self.animListUI.setItem(row, 1, startFrameWidgetItem)
    startFrameText = startFrameWidgetItem.setText(str(start))
        
    endFrameWidgetItem = PySide.QtGui.QTableWidgetItem()
    endFrameItem = self.animListUI.setItem(row, 2, endFrameWidgetItem)
    endFrameWidgetItem.setText(str(end))    
    
  def setCurrentTableTimerange(self, row=None):
    FBSystem().Scene.Evaluate()
    if row is None:
      row = self.animListUI.currentRow()
      col = self.animListUI.currentColumn()
    else:
      col = 0
      
    if col == 0:
      start = self.startFrame
      end = self.endFrame
      
    start = self.startFrame
    end = self.endFrame    

    #self.cellWidgetStart = self.animListUI.cellWidget(row, 1)
    #self.cellWidgetEnd = self.animListUI.cellWidget(row, 2)
    
    startFrameWidgetItem = PySide.QtGui.QTableWidgetItem()
    startFrameItem = self.animListUI.setItem(0, 1, startFrameWidgetItem)
    startFrameText = startFrameWidgetItem.setText(str(start))
    
    endFrameWidgetItem = PySide.QtGui.QTableWidgetItem()
    endFrameItem = self.animListUI.setItem(0, 2, endFrameWidgetItem)
    endFrameWidgetItem.setText(str(end))
    
  @PySide.QtCore.Slot( )
  
  def batch_process(self):
    currTake = vmobu.core.get_current_take()
    lOptions = FBFbxOptions(True)
    setBatchPath = self.batchDir.text()
    lApp = FBApplication()
    currSel = FBModelList()
    FBGetSelectedModels(currSel)
    for sel in currSel:
      selBatchExport = lApp.FileExportBatch((setBatchPath + "test.fbx"), currTake, lOptions, sel)
      
    FBMessageBox("Batch Export Status", "Batch animation exported!\n", "OK")
      
  def animExportSel(self):
    lOptions = FBBatchOptions()
    setExportPath = self.exportDirUI.text()
    lApp = FBApplication()
    currSel = FBModelList()
    FBGetSelectedModels(currSel)
    for sel in currSel:
      selExport = lApp.FileExport((str(setExportPath)) + "test.fbx")
      
    FBMessageBox("Export Status", "Animation exported!\n", "OK")
    
  def browseExportDirs(self):
    browseDialog = PySide.QtGui.QFileDialog()
    browseDialog.setFileMode(PySide.QtGui.QFileDialog.Directory)
    dialogOptions = browseDialog.setOption(PySide.QtGui.QFileDialog.ShowDirsOnly)
    
    export_path = browseDialog.getExistingDirectory(None, '')
    export_path = export_path + "\\"
    self.exportDirUI.setText(export_path)
    
  def browseBatchDirs(self):
    browseDialog = PySide.QtGui.QFileDialog()
    browseDialog.setFileMode(PySide.QtGui.QFileDialog.Directory)
    dialogOptions = browseDialog.setOption(PySide.QtGui.QFileDialog.ShowDirsOnly)
    
    export_path = browseDialog.getExistingDirectory(None, '')
    export_path = export_path + "\\"
    self.batchDir.setText(export_path)
    
  def refresh_anim_node(self):
    project_dir = file_io.v_path.Path( core.const.workspace_dir.replace( '\\', '/' )[ :-1 ] ).splitdrive( )[
          1 ].replace( '/projects/', '' ) 
    
    self.projectLineEdit.setText(str(project_dir))
    if type(self.characterComboUI) == PySide.QtGui.QComboBox:
      try:
        for i in range(0, self.characterComboUI.count() ):
          self.characterComboUI.removeItem(i)
          
        self.anim_nodes = FBSystem().Scene.Notes
        if len(self.anim_nodes) > 0:
          self.anim_node = self.anim_nodes[0]
          
        self.tabWidget.setEnabled(True)
        if not self.anim_nodes:
          self.tabWidget.setEnabled(False)
          
        self.characterComboUI.addItems([an.LongName for an in self.anim_nodes])
      except RuntimeError, e:
        self.closeEvent(None) 
        
    self.updateAnimProperties()
    
  def createNote(self):
    for char in FBSystem().Scene.Characters:
      self.objNote = FBNote(char.LongName+':anim_node')
      self.objNote.Attach(char)
      
      self.applyCustProps()
      
  def storeAnimTakes(self, processCol=0, row=None):
    global noteAnimProperty
    if row is None:
      row = 0
      col = 0
    else:
      row = self.animListUI.currentRow()
      col = self.animListUI.currentColumn()
        
    for objNote in FBSystem().Scene.Notes:
      objNoteParent = objNote.Parents.Name
      take = vmobu.core.get_current_take()
      noteAnimProperty = self.objNote.PropertyCreate(take.Name, FBPropertyType.kFBPT_enum, "Enum", False, True, None)
      #for row in xrange(self.animListUI.rowCount()):
      currTakeItem = "Take:" + take.Name
      startFrameItem = self.animListUI.item(row, 1)
      endFrameItem = self.animListUI.item(row, 2)
      rampInItem = self.animListUI.item(row, 3)
      rampOutItem = self.animListUI.item(row, 4)
      framerateItem = self.animListUI.item(row, 5)
         
      startFrameText = "startFrame:" + str(startFrameItem.text())
      endFrameText = "endFrame:" + str(endFrameItem.text())
      rampInText = "rampIn:" + str(rampInItem.text())
      rampOutText = "rampOut:" + str(rampOutItem.text())
      framerateText = "frameRate:" + str(framerateItem.text())
          
      noteAnimPropEnumList = noteAnimProperty.GetEnumStringList(True)
      noteAnimPropEnumList.Add(currTakeItem)
      noteAnimPropEnumList.Add(startFrameText)
      noteAnimPropEnumList.Add(endFrameText)
      noteAnimPropEnumList.Add(rampInText)
      noteAnimPropEnumList.Add(rampOutText)
      noteAnimPropEnumList.Add(framerateText)
          
      noteAnimProperty.NotifyEnumStringListChanged()
        
  def updateAnimProperties(self):
    currTake = vmobu.core.get_current_take()
    for row in xrange(self.animListUI.rowCount()):
      animNameItem = self.animListUI.item(0, 0)
      startFrameItem = self.animListUI.item(0, 1)
      endFrameItem = self.animListUI.item(0, 2)
      rampInItem = self.animListUI.item(0, 3)
      rampOutItem = self.animListUI.item(0, 4)
      framerateItem = self.animListUI.item(0, 5)
      
      if animNameItem.text() != noteAnimProperty.Name:
        noteAnimProperty.Name = str(animNameItem.text())
        currTake.Name = noteAnimProperty.Name
      else:
        pass
        
  def applyCustProps(self):
    for objNote in FBSystem().Scene.Notes:
      for parent in objNote.Parents:
        objNoteParent = parent.LongName
      parentObjProperty = self.objNote.PropertyCreate("Parent", FBPropertyType.kFBPT_charptr, "String", False, True, None)
      parentObjProperty.Data = objNoteParent
    models = FBModelList()
    FBGetSelectedModels(models)   
    for m in models:
      for p in m.PropertyList:
        if p.Name.startswith("p_"): 
          if p.GetPropertyType() == FBPropertyType.kFBPT_int:
            objProperty = self.objNote.PropertyCreate(p.Name, FBPropertyType.kFBPT_int, "Int", False, True, None)
          if p.GetPropertyType() == FBPropertyType.kFBPT_bool:
            objProperty = self.objNote.PropertyCreate(p.Name, FBPropertyType.kFBPT_bool, "Bool", False, True, None)
          if p.GetPropertyType() == FBPropertyType.kFBPT_float:
            objProperty = self.objNote.PropertyCreate(p.Name, FBPropertyType.kFBPT_float, "Float", False, True, None)
          if p.GetPropertyType() == FBPropertyType.kFBPT_double:
            objProperty = self.objNote.PropertyCreate(p.Name, FBPropertyType.kFBPT_double, "Double", False, True, None)
          if p.GetPropertyType() == FBPropertyType.kFBPT_charptr:
            objProperty = self.objNote.PropertyCreate(p.Name, FBPropertyType.kFBPT_charptr, "String", False, True, None)
          if p.GetPropertyType() == FBPropertyType.kFBPT_stringlist:
            objProperty = self.objNote.PropertyCreate(p.Name, FBPropertyType.kFBPT_stringlist, "String", False, True, None)
          if p.GetPropertyType() == FBPropertyType.kFBPT_event:
            objProperty = self.objNote.PropertyCreate(p.Name, FBPropertyType.kFBPT_event, "Event", False, True, None)
          if p.GetPropertyType() == FBPropertyType.kFBPT_enum:
            objProperty = self.objNote.PropertyCreate(p.Name, FBPropertyType.kFBPT_enum, "Enum", False, True, None)
          if p.GetPropertyType() == FBPropertyType.kFBPT_kReference:
            objProperty = self.objNote.PropertyCreate(p.Name, FBPropertyType.kFBPT_kReference, "kReference", False, True, None)
          if p.GetPropertyType() == FBPropertyType.kFBPT_Reference:
            objProperty = self.objNote.PropertyCreate(p.Name, FBPropertyType.kFBPT_Reference, "Reference", False, True, None)
          if p.GetPropertyType() == FBPropertyType.kFBPT_object:
            objProperty = self.objNote.PropertyCreate(p.Name, FBPropertyType.kFBPT_object, "Object", False, True, None)   
          if p.GetPropertyType() == FBPropertyType.kFBPT_Action:
            objProperty = self.objNote.PropertyCreate(p.Name, FBPropertyType.kFBPT_Action, "Action", False, True, None)  
          objProperty.Data = p.Data  
    
    
  def loadCustomWidget(self):
    #Call and show the widget of the UI
    
    #Set layout of UI
    layout = PySide.QtGui.QVBoxLayout()
    layout.addWidget(aeWidget)
    self.setLayout(layout) 
    
    project_dir = file_io.v_path.Path( core.const.workspace_dir.replace( '\\', '/' )[ :-1 ] ).splitdrive( )[
          1 ].replace( '/projects/', '' ) 
    
    self.projectLineEdit.setText(str(project_dir))
    
    #Check for "Notes" in scene and apply to characterCombo field
    if len(FBSystem().Scene.Notes) < 1:
      self.anim_node = "No anim node"
      characterComboUIText = self.characterComboUI.addItem(self.anim_node)
      
    for n in FBSystem().Scene.Notes:
      if n.Name.endswith("anim_node"):
        self.anim_node = n.LongName
      else:
        self.anim_node = None
        
      if n == "":
        characterComboUIText = self.characterComboUI.addItem("No anim node")
        if not anim_node:
          print "WARNING: No anim node is present."
      else:
        if self.anim_node != None:
          characterComboUIText = self.characterComboUI.addItem(self.anim_node)
    
    self.createNote()    
        
    print "Anim Exporter Loaded!"
    
    aeWidget.show()
    aeWidget.raise_()
    
    
MainWindow = Anim_Exporter()