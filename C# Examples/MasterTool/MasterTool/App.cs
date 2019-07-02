#region Header
/*
 * Author: Jon Logsdon
*/
#endregion

#region Namespaces
using Autodesk.Revit.UI;
using Autodesk.Revit.UI.Selection;
using Autodesk.Revit.Attributes;
using Autodesk.Revit.DB;
using Autodesk.Revit.DB.Architecture;
using System;
using System.Collections.Generic;
using System.Reflection;
using System.Windows.Media.Imaging;
#endregion

namespace MasterTool
{
    class App : IExternalApplication
    {
        public Result OnStartup(UIControlledApplication a)
        {
            // Method to add Tab and Panel 
            RibbonPanel panel = ribbonPanel(a);
            // Reflection to look for this assembly path 
            string thisAssemblyPath = Assembly.GetExecutingAssembly().Location;
            // Add button to panel
            PushButton getParamsButton = panel.AddItem(new PushButtonData("GetParamsButton", "Get Parameters \nfrom Selection", thisAssemblyPath, "MasterTool.RoomInfo")) as PushButton;
            // Add tool tip 
            getParamsButton.ToolTip = "this is a sample";
            // Reflection of path to image 
            //var globePath = System.IO.Path.Combine(System.IO.Path.GetDirectoryName(System.Reflection.Assembly.GetExecutingAssembly().Location), "LACMA DOORS.png");
            var globePath = System.IO.Path.Combine(System.IO.Path.GetDirectoryName("C:\\Users\\Developer\\Pictures\\T_WaterfallCutout.jpg"), "T_WaterfallCutout.jpg");
            Uri uriImage = new Uri(globePath);
            // Apply image to bitmap
            BitmapImage largeImage = new BitmapImage(uriImage);
            // Apply image to button 
            getParamsButton.LargeImage = largeImage;

            a.ApplicationClosing += a_ApplicationClosing;

            //Set Application to Idling
            a.Idling += a_Idling;

            return Result.Succeeded;
        }

        //*****************************a_Idling()*****************************
        void a_Idling(object sender, Autodesk.Revit.UI.Events.IdlingEventArgs e)
        {

        }

        //*****************************a_ApplicationClosing()*****************************
        void a_ApplicationClosing(object sender, Autodesk.Revit.UI.Events.ApplicationClosingEventArgs e)
        {
            throw new NotImplementedException();
        }

        //*****************************ribbonPanel()*****************************
        public RibbonPanel ribbonPanel(UIControlledApplication a)
        {
            string tab = "Master Tool"; // Tab name
            // Empty ribbon panel 
            RibbonPanel ribbonPanel = null;
            // Try to create ribbon tab. 
            try
            {
                a.CreateRibbonTab(tab);
            }
            catch { }
            // Try to create ribbon panel.
            try
            {
                RibbonPanel panel = a.CreateRibbonPanel(tab, "HAL");
            }
            catch { }
            // Search existing tab for your panel.
            List<RibbonPanel> panels = a.GetRibbonPanels(tab);
            foreach (RibbonPanel p in panels)
            {
                if (p.Name == "HAL")
                {
                    ribbonPanel = p;
                }
            }
            //return panel 
            return ribbonPanel;
        }

        public Result OnShutdown(UIControlledApplication a)
        {
            return Result.Succeeded;
        }
    }
}