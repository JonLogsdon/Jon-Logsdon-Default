"""
Creates a constraint system based on the selection.
"""
import pyfbsdk
import vmobu



class One_Point_Constraint( object ):
	"""
	Creates a constraint system based on selection order.
	"""
	def __init__( self ):
		# check the selection
		self.selection = vmobu.core.get_selection_order( )
		if self.selection and len( self.selection ) > 1:
			result = self.main( )
			if result:
				pyfbsdk.FBMessageBox( 'One Point Constraint', 'Success! Be sure to resolve this constraint before exporting etc as to not break our hierarchy!', 'OK' )
		else:
			vmobu.core.confirm_dialog( title = 'One Point Constraint Error', message = 'Please selection two objects to constrain together.', button_one_label = 'OK')

	def main( self ):
		# Unpack the selection
		child = self.selection[ 0 ]
		parent  = self.selection[ 1 ]

		# Check to see if a OPC constraint is already controlling this obj.
		existing_constraint = vmobu.core.get_object_by_name( 'OPC_{0}'.format( child.LongName ), use_namespace=True, case_sensitive=False, models_only=False, single_only=True )
		if existing_constraint:
			pyfbsdk.FBMessageBox( 'One Point Constraint Error', 'There is already a one point constraint applied to {0}. \n Resolve this constraint before continuing!'.format( child.LongName ), 'OK' )
			return False

		# Create the null
		null = self.create_null( child )
		# Constrain the null to the parent in the selection
		vmobu.core.create_constraint_parent( null, parent, name = 'OPC_{0}'.format( child.LongName ), snap = True )
		vmobu.core.unselect_all_components( )

		# Parent the child to the null
		child.Parent = null

		return True

	# Utility methods
	@staticmethod
	def create_null( obj ):
		null = pyfbsdk.FBModelNull( 'OPC_Null_{0}'.format( obj.Name ) )
		vmobu.core.align_objects( null, obj, pivot = False )
		obj_parent = obj.Parent
		if obj_parent:
			obj_parent_name = obj_parent.LongName
		else:
			obj_parent_name = 'None'
		vmobu.core.add_property_obj( null, 'OPC_Parent', prop_value =  obj_parent_name )

		vmobu.core.evaluate( )

		return null


def run( ):
	One_Point_Constraint( )