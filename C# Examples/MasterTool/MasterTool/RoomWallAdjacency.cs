#region Header
/*
 * Author: Jon Logsdon
*/
#endregion

#region Namespaces
using System;
using System.Reflection;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Windows.Forms;
using System.Windows.Media.Imaging;
using Autodesk.Revit.UI;
using Autodesk.Revit.UI.Selection;
using Autodesk.Revit.Attributes;
using Autodesk.Revit.DB;
using Autodesk.Revit.DB.Architecture;
#endregion

namespace MasterTool
{
    [Autodesk.Revit.Attributes.Transaction(Autodesk.Revit.Attributes.TransactionMode.Manual)]
    class RoomWallAdjacency : Autodesk.Revit.UI.IExternalCommand
    {
        public Dictionary<List<Wall>, List<Element>> GetRoomWallAdjacency(Document document, Room room)
        {
            //Establish list and dictionary variables
            List<Wall> roomWalls = new List<Wall>();
            List<Element> adjacencies = new List<Element>();
            Dictionary<List<Wall>, List<Element>> data = new Dictionary<List<Wall>, List<Element>>();
            IList<IList<Autodesk.Revit.DB.BoundarySegment>> segments = room.GetBoundarySegments(new SpatialElementBoundaryOptions());

            //Make sure the room is bound
            if(null != segments)
            {
                //Iterate through all segments
                foreach(IList<Autodesk.Revit.DB.BoundarySegment> segmentList in segments)
                {
                    foreach(Autodesk.Revit.DB.BoundarySegment boundarySegment in segmentList)
                    {
                        //Get the neighbor element from the document
                        Element neighbor = document.GetElement(boundarySegment.ElementId);
                        //Get boundary curve
                        Curve curve = boundarySegment.GetCurve();
                        //Get curve length
                        double length = curve.Length;

                        //Check if the neighbor element is a wall
                        if(neighbor is Wall)
                        {
                            //Initiate wall variable
                            Wall wall = neighbor as Wall;
                            //Get the host area parameter
                            Parameter p = wall.get_Parameter(
                                BuiltInParameter.HOST_AREA_COMPUTED);
                            //Convert area to double
                            double area = p.AsDouble();
                            //Get location curve
                            LocationCurve lc = wall.Location as LocationCurve;
                            //Get wall length
                            double wallLength = lc.Curve.Length;

                            //Populate lists
                            roomWalls.Add(wall);
                            adjacencies.Add(neighbor);
                        }
                    }
                }
                //Populate final dictionary
                data.Add(roomWalls, adjacencies);
            }

            return data;
        }

        public Autodesk.Revit.UI.Result Execute(ExternalCommandData commandData, ref string message, ElementSet elements)
        {
            //Establish typical apps and docs for Revit
            UIApplication uiapp = commandData.Application;
            UIDocument uidoc = uiapp.ActiveUIDocument;
            Document doc = uidoc.Document;
            Dictionary<List<Wall>, List<Element>> roomInfo = null;

            //Iterate elements in the project
            foreach(Element e in elements)
            {
                //Check if the element is a room
                if(e is Room)
                {
                    //Initiate room variable and get the room info
                    Room room = e as Room;
                    roomInfo = GetRoomWallAdjacency(doc, room);
                }
            }

            return Autodesk.Revit.UI.Result.Succeeded;
        }
    }
}
