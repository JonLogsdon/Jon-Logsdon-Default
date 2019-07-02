from pyfbsdk import *

import vmobu
import core

curr_char = FBApplication( ).CurrentCharacter

#Male_v1
for prop in curr_char.PropertyList:
	if prop.Name == "FootInToAnkle":
		prop.Data = prop.Data - 1.5
	if prop.Name == "FootOutToAnkle":
		prop.Data = prop.Data - 2
	if prop.Name == "FootBackToAnkle":
		prop.Data = prop.Data - 2
		

