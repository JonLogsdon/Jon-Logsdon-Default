from pyfbsdk import *
import xml.etree.cElementTree

class Pinning_Groups:
	def __init__( self ):
		self.curr_char = FBApplication( ).CurrentCharacter
		
	def get_rig_pinning( self ):
		for char in FBSystem( ).Scene.Characters:
			if char.LongName == self.curr_char.LongName:
				for comp in FBSystem( ).Scene.Components:
					if comp.ClassName( ) == 'FBControlSet':
						for prop in comp.PropertyList:
							if prop.Name.endswith( 'TPin' or 'RPin' ):
								self.write_xml_with_properties( )
								
	def load_pinning_groups( self, pkey ):
		for char in FBSystem( ).Scene.Characters:
			if char.LongName == self.curr_char.LongName:
				for comp in FBSystem( ).Scene.Components:
					if comp.ClassName( ) == 'FBControlSet':
						for prop in comp.PropertyList:
							if prop.Name.endswith( 'TPin' ):
								if prop.Name == pkey[ 0 ]:
									pin_value = pkey[ 1 ]
									if pin_value == 'False':
										prop.Data = False
									else:
										prop.Data = bool( pin_value )
										
							if prop.Name.endswith( 'RPin' ):
								if prop.Name == pkey[ 0 ]:
									pin_value = pkey[ 1 ]
									if pin_value == 'False':
										prop.Data = False
									else:
										prop.Data = bool( pin_value )								
								
	def load_pinning_xml( self ):
		tree = xml.etree.cElementTree.parse( r"C:\Users\jon.logsdon\Desktop\test_pin.xml" )
		root = tree.getroot( )
		for child in root:
			global pin_name
			for pin_name in child:
				global pkey
				for pkey in pin_name.items( ):
					self.load_pinning_groups( pkey )
								
	def write_xml_with_properties( self ):
		property_name = [ ]
		property_data = [ ]
		
		root = xml.etree.cElementTree.Element( "root" )
		doc = xml.etree.cElementTree.SubElement( root, "doc" )
		
		for comp in FBSystem( ).Scene.Components:
			if comp.ClassName( ) == 'FBControlSet':
				for prop in comp.PropertyList:
					if prop.Name.endswith( 'TPin' ):
						field1 = xml.etree.cElementTree.SubElement( doc, "field1" )
						field1.set( prop.Name, str( prop.Data ) )			
					if prop.Name.endswith( 'RPin' ):
						field1 = xml.etree.cElementTree.SubElement( doc, "field1" )
						field1.set( prop.Name, str( prop.Data ) )							
	
		tree = xml.etree.cElementTree.ElementTree( root )
		tree.write( r"C:\Users\jon.logsdon\Desktop\test_pin.xml" )

#Pinning_Groups( ).load_pinning_xml( )
Pinning_Groups( ).get_rig_pinning( )