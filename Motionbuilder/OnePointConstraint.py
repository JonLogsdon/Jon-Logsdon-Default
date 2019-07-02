"""
Creates a constraint system based on selection for a character limb to follow another, or for holding items.

*Examples:* ::

	>>>import One_Point_Constaint_System
	>>>One_Point_Constaint_System.One_Point_Constraint().run()

*Author:*
	* Jon Logsdon, jon.logsdon@volition-inc.com, 5/22/2014 1:35:21 PM
"""


# Motionbuilder lib
import pyfbsdk

#vmobu
import vmobu

class One_Point_Constraint:
	"""
	Creates a constraint system based on selection order.
	
	*Author:*
		* Jon Logsdon, jon.logsdon@volition-inc.com, 5/22/2014 1:39:38 PM
	"""
	
	def __init__( self ):
		self.aux_vector = pyfbsdk.FBVector3d( )
		self.pos_null_vector = pyfbsdk.FBVector3d( )
		
	def create_null_object( self ):
		"""
		Creates a null object to accept the constraint of the system.
		
		*Arguments:*
			* ``None``
		
		*Keyword Arguments:*
			* ``None``
		
		*Returns:*
			* ``None`` 
		
		*Author:*
			* Jon Logsdon, jon.logsdon@volition-inc.com, 5/22/2014 1:48:10 PM
		"""
		
		global constrain_null, child_obj, parent_obj
		constrain_null = pyfbsdk.FBModelNull( "OnePointConst_UserNode" )
		selected = vmobu.core.get_selection_order( )
		for i in range( len( selected ) ):
			if i == 0:
				child_obj = selected[ i ]
			if i == 1:
				parent_obj = selected[ i ]
		
		constrain_null_vector = pyfbsdk.FBVector3d( )
		constrain_null.GetVector( constrain_null_vector, pyfbsdk.FBModelTransformationType.kModelTranslation )
		constrain_null.GetVector( constrain_null_vector, pyfbsdk.FBModelTransformationType.kModelRotation )
		
		pyfbsdk.FBSystem( ).Scene.Evaluate( )
		
		constrain_null.SetVector( pyfbsdk.FBVector3d( self.pos_null_vector ), pyfbsdk.FBModelTransformationType.kModelTranslation )
		constrain_null.SetVector( pyfbsdk.FBVector3d( self.pos_null_vector ), pyfbsdk.FBModelTransformationType.kModelRotation )
		
		for comp in pyfbsdk.FBSystem( ).Scene.Components:
			comp.Selected = False
		
def run( ):
	One_Point_Constraint( ).create_null_object( )
	
	null_vector = pyfbsdk.FBVector3d( )
	constrain_null.GetVector( null_vector, pyfbsdk.FBModelTransformationType.kModelTranslation )
	constrain_null.GetVector( null_vector, pyfbsdk.FBModelTransformationType.kModelRotation )
	
	child_obj.Parent = constrain_null
	
	selected = vmobu.core.get_selection_order( )
	constraint_pc = pyfbsdk.FBConstraintManager( ).TypeCreateConstraint( 3 )
	constraint_pc.Name = "OnePointConst"
	
	constraint_pc.ReferenceAdd( 1, parent_obj )
	constraint_pc.ReferenceAdd( 0, constrain_null )
			
	constraint_pc.Snap( )
run( )