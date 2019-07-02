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
    [Autodesk.Revit.Attributes.Regeneration(Autodesk.Revit.Attributes.RegenerationOption.Manual)]
    class Dimensions : Autodesk.Revit.UI.IExternalCommand
    {
        const double _eps = 1.0e-9;

        public void DuplicateDimension(Document doc, Dimension dimension)
        {
            Line line = dimension.Curve as Line;
            if(null != line)
            {
                Autodesk.Revit.DB.View view = dimension.View;
                ReferenceArray references = dimension.References;
                Dimension newDimension = doc.Create.NewDimension(
                                                                    view,
                                                                    line,
                                                                    references);
            }
        }

        public Dimension CreateLinearDimension(Document doc)
        {
            Autodesk.Revit.ApplicationServices.Application app = doc.Application;
            XYZ pt1 = new XYZ(5, 5, 0);
            XYZ pt2 = new XYZ(5, 10, 0);
            Line line = Line.CreateUnbound(pt1, pt2);
            Plane plane = Plane.CreateByNormalAndOrigin(pt1.CrossProduct(pt2), pt2);
            SketchPlane skPlane = SketchPlane.Create(doc, plane);
            ModelCurve modelCurveA = doc.FamilyCreate.NewModelCurve(line, skPlane);

            pt1 = new XYZ(10, 5, 0);
            pt2 = new XYZ(10, 10, 0);
            line = Line.CreateUnbound(pt1, pt2);
            plane = Plane.CreateByNormalAndOrigin(pt1.CrossProduct(pt2), pt2);
            skPlane = SketchPlane.Create(doc, plane);
            ModelCurve modelCurveB = doc.FamilyCreate.NewModelCurve(line, skPlane);

            ReferenceArray refArr = new ReferenceArray();
            refArr.Append(modelCurveA.GeometryCurve.Reference);
            refArr.Append(modelCurveB.GeometryCurve.Reference);

            pt1 = new XYZ(5, 10, 0);
            pt2 = new XYZ(10, 10, 0);
            line = Line.CreateUnbound(pt1, pt2);
            Dimension dim = doc.FamilyCreate.NewLinearDimension(doc.ActiveView, line, refArr);
            FamilyParameter param = doc.FamilyManager.AddParameter("width",
                                                                    BuiltInParameterGroup.PG_CONSTRAINTS,
                                                                    ParameterType.Length,
                                                                    false);

            dim.FamilyLabel = param;
            return dim;
        }

        static public bool IsEqual(double a, double b)
        {
            return Math.Abs(a - b) < _eps;
        }

        static public bool IsParallel(XYZ a, XYZ b)
        {
            double angle = a.AngleTo(b);
            return _eps > angle || IsEqual(angle, Math.PI);
        }

        static XYZ Midpoint(XYZ p, XYZ q)
        {
            return p + 0.5 * (q - p);
        }

        static XYZ Midpoint(Line line)
        {
            return Midpoint(line.GetEndPoint(0), line.GetEndPoint(1));
        }

        static XYZ Normal(Line line)
        {
            XYZ p = line.GetEndPoint(0);
            XYZ q = line.GetEndPoint(1);
            XYZ v = q - p;

            return v.CrossProduct(XYZ.BasisZ).Normalize();
        }

        static Face GetClosestFace(Element e, XYZ p, XYZ normal, Options opt)
        {
            Face face = null;
            double minDistance = double.MaxValue;
            GeometryElement geo = e.get_Geometry(opt);
            foreach (GeometryObject obj in geo)
            {
                Solid solid = obj as Solid;
                if(solid != null)
                {
                    FaceArray fa = solid.Faces;
                    foreach(Face f in fa)
                    {
                        PlanarFace pf = f as PlanarFace;
                        if(null != pf && IsParallel(normal, pf.FaceNormal))
                        {
                            XYZ v = p - pf.Origin;
                            double d = v.DotProduct(-pf.FaceNormal);
                            if(d < minDistance)
                            {
                                face = f;
                                minDistance = d;
                            }
                        }
                    }
                }
            }

            return face;
        }

        public static void CreateDimensionElement(
                                                    Document doc,
                                                    Autodesk.Revit.ApplicationServices.Application app,
                                                    Autodesk.Revit.DB.View view,
                                                    XYZ p1,
                                                    Reference r1,
                                                    XYZ p2,
                                                    Reference r2)
        {
            Autodesk.Revit.Creation.Application creApp = app.Create;
            Autodesk.Revit.Creation.Document creDoc = doc.Create;
            ReferenceArray refArr = new ReferenceArray();

            refArr.Append(r1);
            refArr.Append(r2);

            Line line = Line.CreateBound(p1, p2);
            Transaction t = new Transaction(doc, "Dimension Two Walls");

            t.Start();

            Dimension dim = creDoc.NewDimension(doc.ActiveView, line, refArr);
            t.Commit();
        }

        public Autodesk.Revit.UI.Result Execute(ExternalCommandData commandData, ref string message, ElementSet elements)
        {
            const string _prompt = "Please select two parallel opposing walls.";

            UIApplication uiapp = commandData.Application;
            UIDocument uidoc = uiapp.ActiveUIDocument;
            Autodesk.Revit.ApplicationServices.Application app = uiapp.Application;
            Document doc = uidoc.Document;
            Selection sel = uidoc.Selection;
            List<Wall> walls = new List<Wall>(2);
            ICollection<ElementId> selectionIds = uidoc.Selection.GetElementIds();

            if (selectionIds.Count > 0)
            {
                foreach (ElementId id in selectionIds)
                {
                    Element elem = doc.GetElement(id);
                    if (elem is Wall)
                    {
                        walls.Add(elem as Wall);
                    }
                }

                if (2 != walls.Count)
                {
                    message = _prompt;
                    return Result.Failed;
                }
            }

            List<Line> lines = new List<Line>(2);
            List<XYZ> midpoints = new List<XYZ>(2);
            XYZ normal = null;

            foreach(Wall wall in walls)
            {
                LocationCurve locCur = wall.Location as LocationCurve;
                Curve curve = locCur.Curve;

                if(!(curve is Line))
                {
                    message = _prompt;
                    return Result.Failed;
                }

                Line l = curve as Line;
                lines.Add(l);
                midpoints.Add(Midpoint(l));

                if (null == normal)
                {
                    normal = Normal(l);
                }
                else
                {
                    if(!IsParallel(normal, Normal(l)))
                    {
                        message = _prompt;
                        return Result.Failed;
                    }
                }
            }

            Options opt = app.Create.NewGeometryOptions();
            opt.ComputeReferences = true;
            List<Face> faces = new List<Face>(2);

            faces.Add(GetClosestFace(walls[0], midpoints[1], normal, opt));
            faces.Add(GetClosestFace(walls[1], midpoints[0], normal, opt));

            CreateDimensionElement(doc, app, doc.ActiveView, midpoints[0], faces[0].Reference, midpoints[1], faces[1].Reference);

            return Result.Succeeded;
        }
    }
}
