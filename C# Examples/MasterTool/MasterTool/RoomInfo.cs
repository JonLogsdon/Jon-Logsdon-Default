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
    class RoomInfo : Autodesk.Revit.UI.IExternalCommand
    {
        public Dictionary<Room, List<string>> GetRoomInfo(Document document, UIDocument uidoc)
        {
            using (Transaction t = new Transaction(document, "Turn on volume calculation"))
            {
                t.Start();
                AreaVolumeSettings settings = AreaVolumeSettings.GetAreaVolumeSettings(document);
                settings.ComputeVolumes = true;
                t.Commit();
            }

                Dictionary<Room, List<string>> dimensions = new Dictionary<Room, List<string>>();
            List<string> info = new List<string>();
            RoomFilter filter = new RoomFilter();
            FilteredElementCollector collector = new FilteredElementCollector(document);
            collector.WherePasses(filter);

            FilteredElementIdIterator roomIdItr = collector.GetElementIdIterator();
            roomIdItr.Reset();
            while (roomIdItr.MoveNext())
            {
                ElementId roomId = roomIdItr.Current;
                Room room = document.GetElement(roomId) as Room;

                //Make sure room is valid
                if (room != null)
                {
                    //Wall wall = document.GetReference(room) as Wall;

                    //Fill out dictionary with room attributes
                    info.Add(room.Name);
                    info.Add(room.Volume.ToString());
                    info.Add(room.Area.ToString());
                    info.Add(room.Perimeter.ToString());
                    info.Add(room.UnboundedHeight.ToString());

                    dimensions.Add(room, info);
                }
            }

            return dimensions;
        }

        public string FindDoorsInWallWithReferenceIntersector(Document doc, UIDocument uidoc)
        {
            Wall wall = doc.GetElement(uidoc.Selection.PickObject(ObjectType.Element)) as Wall;
            LocationCurve locCurve = wall.Location as LocationCurve;
            Curve curve = locCurve.Curve;

            XYZ curveTangent = curve.ComputeDerivatives(0.5, true).BasisX;
            XYZ wallEnd = curve.GetEndPoint(0);

            ElementCategoryFilter filter = new ElementCategoryFilter(BuiltInCategory.OST_Doors);
            ReferenceIntersector intersector = new ReferenceIntersector(filter, FindReferenceTarget.Element, (View3D)doc.ActiveView);
            string doorDistanceInfo = "";

            foreach(ReferenceWithContext refWithContext in intersector.Find(wallEnd,curveTangent))
            {
                double proximity = refWithContext.Proximity;
                FamilyInstance door = doc.GetElement(refWithContext.GetReference()) as FamilyInstance;

                doorDistanceInfo += String.Format("{0} - {1} = {2}\n", door.Symbol.Family.Name, door.Name, proximity);
            }

            return doorDistanceInfo;
        }

        public Autodesk.Revit.UI.Result Execute(ExternalCommandData commandData, ref string message, ElementSet elements)
        {
            //Establish typical apps and docs for Revit
            Document document = commandData.Application.ActiveUIDocument.Document;
            UIDocument uidoc = commandData.Application.ActiveUIDocument;
            string fullInfo = "";

            List<string> data = new List<string>();
            Dictionary<Room, List<string>> roomInfo = GetRoomInfo(document, uidoc);

            string distanceInfo = FindDoorsInWallWithReferenceIntersector(document, uidoc);

            if (distanceInfo != "")
            {
                TaskDialog.Show("Distance Info", distanceInfo);
            }
            else
            {
                TaskDialog.Show("ERROR", "The distance info was empty");
            }

            foreach (KeyValuePair<Room, List<string>> entry in roomInfo)
            {
                Room room = entry.Key;

                foreach (var infoAsset in entry.Value)
                {
                    data.Add(infoAsset);
                }
            }

            foreach (var item in data)
            {
                fullInfo += String.Format("{0}\n", item);
            }

            TaskDialog.Show("Info", fullInfo);

            return Autodesk.Revit.UI.Result.Succeeded;
        }
    }
}
