from pyfbsdk import *
import vmobu

class One_Point_Weapon_Constraint:
    def get_selection_order( self ):
        selected_models = FBModelList( )
        pParent = None
        pSelected = True
        pSortSelectedOrder = True
        FBGetSelectedModels( selected_models, pParent, pSelected, pSortSelectedOrder )
        if not selected_models:
            return None
        else:
            return selected_models
        
    def create_aux_effector( self ):
        selected = One_Point_Weapon_Constraint( ).get_selection_order( )
        for char in FBSystem( ).Scene.Characters:
            control_set = char.GetCurrentControlSet( )
            
            for i in range( len( selected ) ):
                selected[ i ].Selected = False
                if i == 0:
                    effector_dst = control_set.PropertyList.Find( selected[ i ].Name )
                    effector = control_set.GetIKEffectorModel( FBEffectorId.kFBLeftWristEffectorId, 0 )
                    
                    aux = FBModelMarker( effector.Name + "Aux" )
                    aux.Show = True
                    aux.Type = FBMarkerType.kFBMarkerTypeIKEffector
                    
                    matrix = FBMatrix( )
                    effector.GetMatrix( matrix )
                    aux.SetMatrix( matrix )
                    aux.ConnectDst( effector_dst )
                    
                    selected[ i ].Selected = False
                    effector.Selected = True
                else:
                    selected[ i ].Selected = True
        
    def create_null_object( self ):
        #self.create_aux_effector( )
        constrain_null = FBModelNull( "test" )
        selected = One_Point_Weapon_Constraint( ).get_selection_order( )
        for i in range( len( selected ) ):
            if i == 1:
                second_selection = selected[ i ].LongName
                second_selection_obj = vmobu.core.get_object_by_name( second_selection, use_namespace=True, models_only=False )
                
            if i == 0:
                parent = selected[ i ].Parents
                parent.Parent = constrain_null
        
def run( ):
    One_Point_Weapon_Constraint( ).create_null_object( )
    selected = One_Point_Weapon_Constraint( ).get_selection_order( )
    constraint_pc = FBConstraintManager( ).TypeCreateConstraint( 3 )
    constraint_pc.Name = "OnePointWeaponConst"
    for i in range( len( selected ) ):
        #ref = vmobu.core.get_object_by_name( selected[ i ].LongName, use_namespace=True, models_only=False )
        if i == 0:
            constraint_pc.ReferenceAdd( 1, selected[ i ] )
        else:
            constraint_pc.ReferenceAdd( 0, selected[ i ] )
            
        constraint_pc.Active = False
        constraint_pc.Snap( )
run( )