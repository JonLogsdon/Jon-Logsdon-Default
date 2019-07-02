import os

#MotionBuilder libs...
import pyfbsdk

#Volition MoBu libs...
import _base
import _scene
import vmobu.const

class Constraints( _base.Mobu_Base ):
	def __init__( self ):
		super( Constraints, self ).__init__( )
		
	def aim_constraint( self ):
		selected = vmobu.core.get_selection_order( )
		pconstraint = pyfbsdk.FBConstraintManager( ).TypeCreateConstraint( 0 )
		for i in range( len( selected ) ):
			if i == 0:
				pconstraint.ReferenceAdd( 1, selected[ i ] )
			else:
				pconstraint.ReferenceAdd( 0, selected[ i ] )
				
	def expression_constraint( self ):
		selected = vmobu.core.get_selection_order( )
		pconstraint = pyfbsdk.FBConstraintManager( ).TypeCreateConstraint( 1 )
		for i in range( len( selected ) ):
			if i == 0:
				pconstraint.ReferenceAdd( 1, selected[ i ] )
			else:
				pconstraint.ReferenceAdd( 0, selected[ i ] )
				
	def multi_ref_constraint( self ):
		selected = vmobu.core.get_selection_order( )
		pconstraint = pyfbsdk.FBConstraintManager( ).TypeCreateConstraint( 2 )
		for i in range( len( selected ) ):
			if i == 0:
				pconstraint.ReferenceAdd( 1, selected[ i ] )
			else:
				pconstraint.ReferenceAdd( 0, selected[ i ] )
		
	def parent_constraint( self ):
		selected = vmobu.core.get_selection_order( )
		pconstraint = pyfbsdk.FBConstraintManager( ).TypeCreateConstraint( 3 )
		for i in range( len( selected ) ):
			if i == 0:
				pconstraint.ReferenceAdd( 1, selected[ i ] )
			else:
				pconstraint.ReferenceAdd( 0, selected[ i ] )
				
	def path_constraint( self ):
		selected = vmobu.core.get_selection_order( )
		pconstraint = pyfbsdk.FBConstraintManager( ).TypeCreateConstraint( 4 )
		for i in range( len( selected ) ):
			if i == 0:
				pconstraint.ReferenceAdd( 1, selected[ i ] )
			else:
				pconstraint.ReferenceAdd( 0, selected[ i ] )
				
	def position_constraint( self ):
		selected = vmobu.core.get_selection_order( )
		pconstraint = pyfbsdk.FBConstraintManager( ).TypeCreateConstraint( 5 )
		for i in range( len( selected ) ):
			if i == 0:
				pconstraint.ReferenceAdd( 1, selected[ i ] )
			else:
				pconstraint.ReferenceAdd( 0, selected[ i ] )
				
	def range_constraint( self ):
		selected = vmobu.core.get_selection_order( )
		pconstraint = pyfbsdk.FBConstraintManager( ).TypeCreateConstraint( 6 )
		for i in range( len( selected ) ):
			if i == 0:
				pconstraint.ReferenceAdd( 1, selected[ i ] )
			else:
				pconstraint.ReferenceAdd( 0, selected[ i ] )
				
	def relation_constraint( self ):
		selected = vmobu.core.get_selection_order( )
		pconstraint = pyfbsdk.FBConstraintManager( ).TypeCreateConstraint( 7 )
		for i in range( len( selected ) ):
			if i == 0:
				pconstraint.ReferenceAdd( 1, selected[ i ] )
			else:
				pconstraint.ReferenceAdd( 0, selected[ i ] )
				
	def rigid_body_constraint( self ):
		selected = vmobu.core.get_selection_order( )
		pconstraint = pyfbsdk.FBConstraintManager( ).TypeCreateConstraint( 8 )
		for i in range( len( selected ) ):
			if i == 0:
				pconstraint.ReferenceAdd( 1, selected[ i ] )
			else:
				pconstraint.ReferenceAdd( 0, selected[ i ] )
				
	def three_point_constraint( self ):
		selected = vmobu.core.get_selection_order( )
		pconstraint = pyfbsdk.FBConstraintManager( ).TypeCreateConstraint( 9 )
		for i in range( len( selected ) ):
			if i == 0:
				pconstraint.ReferenceAdd( 1, selected[ i ] )
			else:
				pconstraint.ReferenceAdd( 0, selected[ i ] )
				
	def rotation_constraint( self ):
		selected = vmobu.core.get_selection_order( )
		pconstraint = pyfbsdk.FBConstraintManager( ).TypeCreateConstraint( 10 )
		for i in range( len( selected ) ):
			if i == 0:
				pconstraint.ReferenceAdd( 1, selected[ i ] )
			else:
				pconstraint.ReferenceAdd( 0, selected[ i ] )
				
	def scale_constraint( self ):
		selected = vmobu.core.get_selection_order( )
		pconstraint = pyfbsdk.FBConstraintManager( ).TypeCreateConstraint( 11 )
		for i in range( len( selected ) ):
			if i == 0:
				pconstraint.ReferenceAdd( 1, selected[ i ] )
			else:
				pconstraint.ReferenceAdd( 0, selected[ i ] )
				
	def map_constraint( self ):
		selected = vmobu.core.get_selection_order( )
		pconstraint = pyfbsdk.FBConstraintManager( ).TypeCreateConstraint( 12 )
		for i in range( len( selected ) ):
			if i == 0:
				pconstraint.ReferenceAdd( 1, selected[ i ] )
			else:
				pconstraint.ReferenceAdd( 0, selected[ i ] )
				
	def chain_ik_constraint( self ):
		selected = vmobu.core.get_selection_order( )
		pconstraint = pyfbsdk.FBConstraintManager( ).TypeCreateConstraint( 13 )
		for i in range( len( selected ) ):
			if i == 0:
				pconstraint.ReferenceAdd( 1, selected[ i ] )
			else:
				pconstraint.ReferenceAdd( 0, selected[ i ] )
				
class Mobu_Class_Constraints( Constraints ):
	def __init__( self ):
		Constraints.__init__( self )