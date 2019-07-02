from pyfbsdk import *
from pyfbsdk_additions import *

class Constraint_System:
	def __init__( self ):
		self.const_manager = FBConstraintManager( )
		
	def populate_layout( self, mainLyt ):
		x = FBAddRegionParam( 5, FBAttachType.kFBAttachLeft, "" )
		y = FBAddRegionParam( 5, FBAttachType.kFBAttachTop, "" )
		w = FBAddRegionParam( -5, FBAttachType.kFBAttachRight, "" )
		h = FBAddRegionParam( -5, FBAttachType.kFBAttachBottom, "" )
		mainLyt.AddRegion( "main", "main", x,y,w,h )
		
		grid = FBGridLayout( )
		mainLyt.SetControl( "main", grid )
		
		v_box_layout = FBVBoxLayout( )
		const_list_widget = FBList( )
		const_list_widget.OnChange.Add( )
		const_list_widget.Style = FBListStyle.kFBVerticalList
		const_list_widget.MultiSelect = True
		v_box_layout.Add( const_list_widget, 141 )
		
def run( ):
	t = FBCreateUniqueTool( "Constraint System" )
	t.StartSizeX = 200
	t.StartSizeY = 150
	t.MinSizeY = 150
	t.MaxSizeY = 200
	
	const_sys = Constraint_System( )
	
	const_sys.populate_layout( t )
	ShowTool( t )