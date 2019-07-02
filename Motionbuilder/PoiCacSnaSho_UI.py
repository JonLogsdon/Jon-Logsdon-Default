import PySide.QtCore
import PySide.QtGui
import PySide.QtUiTools

class PointCacheSnapshotUI(PySide.QtGui.QMainWindow):
	def __init__(self, parent=None):
		super(PointCacheSnapshotUI, self).__init__()	
		
		#Load ui file
		loader = PySide.QtUiTools.QUiLoader()
		self.myWidget = loader.load(r'C:\Users\jon.logsdon\Scripts\Mobu\PointCacheUI.ui')
		layout = PySide.QtGui.QVBoxLayout()
		layout.addWidget(self.myWidget)
		
		#Initialize ui components
		
		#--Widgets--
		self.cacheSnapshotTabWidget      = self.myWidget.cacheSnapshotTabWidget
		self.pointCacheWidget            = self.myWidget.pointCacheWidget
		self.pointCacheTabWidget         = self.myWidget.pointCacheTabWidget
		self.snapshotWidget             = self.myWidget.snapshotWidget
		
		#--Buttons--
		self.popInBut                  = self.myWidget.popInBut
		self.popOutBut                 = self.myWidget.popOutBut
		self.popIn2But                 = self.myWidget.popIn2But
		self.popOut2But                = self.myWidget.popOut2But		
		self.browsePathBut              = self.myWidget.browsePathBut
		self.charRefreshBut             = self.myWidget.charRefreshBut
		self.storyTracksRefreshBut        = self.myWidget.storyTracksRefreshBut
		self.processBut                = self.myWidget.processBut
		self.viewCacheBut              = self.myWidget.viewCacheBut
		self.viewDeformBut              = self.myWidget.viewDeformBut	
		self.allDeformModsBut           = self.myWidget.allDeformModsBut
		self.allStaticModsBut            = self.myWidget.allStaticModsBut
		self.cancelSnapshotBut          = self.myWidget.cancelSnapshotBut
		self.cacheCloneBut             = self.myWidget.cacheCloneBut
		self.copyCloneBut              = self.myWidget.copyCloneBut
		self.meshCloneBut              = self.myWidget.meshCloneBut
		self.rangeBut                  = self.myWidget.rangeBut
		self.runSnapshotBut             = self.myWidget.runSnapshotBut
		self.singleBut                  = self.myWidget.singleBut
		self.snapshotRefreshBut          = self.myWidget.snapshotRefreshBut
		self.deactiveEvalCheckBox        = self.myWidget.deactiveEvalCheckBox
		self.dupModCheckBox           = self.myWidget.dupModCheckBox
		
		#--Value Edits--
		self.cacheEndEdit              = self.myWidget.cacheEndEdit
		self.cacheFilePath              = self.myWidget.cacheFilePath
		self.cacheFilePathEdit           = self.myWidget.cacheFilePathEdit
		self.copiesValue               = self.myWidget.copiesValue
		self.maxCloneValue             = self.myWidget.maxCloneValue
		self.minCloneValue             = self.myWidget.minCloneValue
		
		#--Lists--
		self.currCharsList              = self.myWidget.currCharsList
		self.storyTracksList             = self.myWidget.storyTracksList
		self.currModsList               = self.myWidget.currModsList	

		self.loadUI()
		
	def addTab(self, widget):
		if self.cacheSnapshotTabWidget.indexOf(widget) == -1:
			widget.setWindowFlags(PySide.QtCore.Qt.Widget)
			self.cacheSnapshotTabWidget.addTab(widget, widget.windowTitle())
			
	def removeTab(self, widget):
		index = self.cacheSnapshotTabWidget.indexOf(widget)
		if index != -1:
			self.cacheSnapshotTabWidget.removeTab(index)
			widget.setWindowFlags(PySide.QtCore.Qt.Window)
			widget.show()	
			
	        
	def loadUI(self):
		self.myWidget.show()
		self.myWidget.raise_()
		
MainWindow = PointCacheSnapshotUI()