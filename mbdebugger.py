# Copyright 2009 Autodesk, Inc.  All rights reserved.
# Use of this software is subject to the terms of the Autodesk license agreement 
# provided at the time of installation or download, or which otherwise accompanies
# this software in either electronic or hard copy form.
#
# Script description:
# Create a debugging tool to help investigate crash in MotionBuilder.
#

import os
import os.path

logfilename = None
currentFile = None
inFileToken = "In file: "

def WriteCallArg(f, frame):
    """ 
    Write all args of the function call.
    Args are extracted from the execution frame
    """
    f.write(" with args: ")
    nbarg = frame.f_code.co_argcount
    hasArg = False
    for i, argname in enumerate(frame.f_code.co_varnames[:nbarg]):
        if argname != "self":
            hasArg = True
            f.write(argname)
            f.write("=")
            value = frame.f_locals[argname]
            f.write(str(value))
            if i < nbarg - 1:
                f.write(",")
    if not hasArg:
        f.write("<no arg>")
    f.write("\n")

def GetModuleName(f):
    """
    Extract the module name from a filename (i.e. the name of file without path or extension)
    """
    import os.path
    moduledir, modulefile = os.path.split(f)
    modulename, moduleext = os.path.splitext(modulefile)
    return modulename

def Trace(frame, event, arg):
    """
    log the line or function or module that is executed
    """
    # if the last line of execution is from the debugging module 
    #(i.e. the current module): forfeit it
    if frame.f_code.co_filename == Trace.func_code.co_filename:
        return Trace
        
    f=open(logfilename, "a")
    global currentFile
    # Only log the name of the file executed if different from current file
    if currentFile != frame.f_code.co_filename:
        f.write(inFileToken)
        f.write(frame.f_code.co_filename)
        f.write("\n")
        currentFile = frame.f_code.co_filename

    # A function call or a module execution                              
    if event == "call":
        if frame.f_code.co_name == "<module>":            
            msg = "Module execution: %s at line: %d\n" %(GetModuleName(frame.f_code.co_filename), frame.f_lineno)
        else:
            msg = "    function call: %s at line: %d  " %(frame.f_code.co_name, frame.f_lineno)
            f.write(msg)
            WriteCallArg(f, frame)
            msg = ""
    # A line is executed
    elif event == "line":
        msg = "    line exec: %d \n" %(frame.f_lineno)
    # Module or function call returned.
    elif event == "return":
        if frame.f_code.co_name == "<module>":
            msg = "Module execution ended: %s at line: %d \n" %(GetModuleName(frame.f_code.co_filename), frame.f_lineno)
        else:
            msg = "function returned: %s with value: %s \n" %(frame.f_code.co_name, str(arg))
    # Anything else is logged
    else:
        msg = "event: %s with arg: %s \n" %(event, str(arg))
    f.write(msg)
    f.close()
    return Trace

class OutputLogWrapper:
    """
    This OutputWrapper will replace a standard output (stdout or stderr) and 
    will log to this ouput AND to a set of files.
    """
    def __init__(self, originaloutput, *files):
        self.originaloutput = originaloutput
        self.files = files
        
    def write(self, msg):
        self.originaloutput.write(msg)
        for filename in self.files:
            f = open(filename, "a")
            f.write(msg)
            f.close()
    
def LogFileExecution(f):
    """
    Main function that execute a script and installs in the python runtime all
    necessary function to trace each line that is executed.
    """
    try:
        # reset file and check if that file exist and can be created
        loggile=open(logfilename, "w")
        loggile.close()
    except:
        print "Log file cannot be created:", logfilename
        return
            
    import sys    
    # ensure that if the script to test prints something on stdout/stderr we will log it
    stdout, stderr = sys.stdout, sys.stderr
    sys.stdout, sys.stderr = OutputLogWrapper(stdout, logfilename), OutputLogWrapper(stderr, logfilename)
    
    # set our trace method which will be called each time a line of code is executed
    sys.settrace(Trace)
    # Execute the file to test. Specifying globals is important so the file to execute knows
    # about its execution context
    execfile(f, globals(), globals())
    
    # unset our trace method
    sys.settrace(None)
    # Restore normal output
    sys.stdout, sys.stderr = stdout, stderr
    
    
def PrintExecLog():
    """
    Print the whole Execution Log.
    """
    try:
        print "Printing log file:", logfilename, "\n"
        f=open(logfilename, "r")
        print f.read()
    except:
        print "There is no log file:", logfilename
    else:
        f.close()
    
def PrintLastExec():
    """
    Print the last few lines of Execution log as well as the file where
    this line was executed.
    """
    try:
        f=open(logfilename, "r")
        lines = f.readlines()
        lines.reverse()
        
        if lines:
            lastlineexec = lines[0]
            lastlineexec = lastlineexec.strip()
            lastfile = None
            for line in lines[1:]:
                if inFileToken in line:
                    lastfile = line
                    break
            print "Execution stopped"
            print lastfile, " with: ", lastlineexec
        else:
            print "Nothing in log file:", logfilename
    except:
        print "There is no log file:", logfilename
    else:
        f.close()
        
import pyfbsdk
import pyfbsdk_additions

filepopup = pyfbsdk.FBFilePopup()

class MbDebugger(pyfbsdk.FBTool):
    """
    Basic Debugger that currently allow logging of all executed lines in a script.
    Basic usage:
    If a script crashes MB, and you want to know which line of your script as caused the crash:
    
    1- Select the script you want to test. Press Debug Button. MB will crash.
    2- Restart MB. Pop the Debugger.
    3- Press Last Exec line. On the Python console, the number of the last executed line of your script
       will be printed. At least you will know which line has caused the crash and you can
       tweak the params to this function to prevent this crash.
    """
    def SetLogName(self, log):
        global logfilename
        logfilename = log
        self.debuglog.Text = log
        
    def SetScript(self, script):
        self.todebugedit.Text = script        
        
    def OnDebug(self, control, event):
        script = self.todebugedit.Text
        if os.path.isfile(script):
            self.SetScript(script)
            LogFileExecution(script)
        
    def Browse(self, edit, filefilter, caption):
        filepopup.Caption = caption
        filepopup.Style = pyfbsdk.FBFilePopupStyle.kFBFilePopupOpen
        filepopup.Filter = filefilter
        result = filepopup.Execute()
        if result:
            edit.Text = os.path.join(filepopup.Path,filepopup.FileName)
    
    def OnBrowseDebugScript(self, control, event):
        self.Browse(self.todebugedit, "*.py", "Select script to debug")
        
    def OnBrowseLog(self, control, event):
        self.Browse(self.debuglog, "*.log", "Select file to log")
    
    def OnPrintLastExec(self, control, event):
        PrintLastExec()
        
    def OnPrintExecLog(self, control, event):
        PrintExecLog()
    
    def __init__(self):
        from pyfbsdk import FBAddRegionParam
        from pyfbsdk import FBAttachType
                
        # Init base class
        name = "Python Logger"
        
        # Ensure only one debugger will exists
        pyfbsdk_additions.FBDestroyToolByName(name)
        
        # init base class
        pyfbsdk.FBTool.__init__(self,name)
        
        self.lyt = pyfbsdk_additions.FBGridLayout()
                
        x = FBAddRegionParam(5,FBAttachType.kFBAttachLeft,"")
        y = FBAddRegionParam(5,FBAttachType.kFBAttachTop,"")
        w = FBAddRegionParam(-5,FBAttachType.kFBAttachRight,"")
        h = FBAddRegionParam(-5,FBAttachType.kFBAttachBottom,"")
        self.AddRegion("main", "main", x,y,w,h)
        self.SetControl("main",self.lyt)
                
        self.StartSizeX = 500
        self.StartSizeY = 225
                
        # Debug        
        l = pyfbsdk.FBLabel()
        l.Caption = "Script to execute"
        self.lyt.Add(l, 0, 0)
        
        self.todebugedit = pyfbsdk.FBEdit()
        self.todebugedit.ReadOnly = True
        self.lyt.AddRange(self.todebugedit, 1, 1, 0, 2)
        
        b = pyfbsdk.FBButton()
        b.Caption = "Browse"
        b.OnClick.Add(self.OnBrowseDebugScript)
        self.lyt.Add(b, 1, 3, width = 50)
        
        b = pyfbsdk.FBButton()
        b.Caption = "Log Execution"
        b.OnClick.Add(self.OnDebug)
        self.lyt.Add(b, 2, 0, width = 150)
        
        
        # print buttons        
        l = pyfbsdk.FBLabel()
        l.Caption = "Execution log"
        self.lyt.Add(l, 3, 0)
        
        self.debuglog = pyfbsdk.FBEdit()
        self.debuglog.ReadOnly = True
        self.lyt.AddRange(self.debuglog, 4, 4, 0, 2)
        
        b = pyfbsdk.FBButton()
        b.Caption = "Browse"
        b.OnClick.Add(self.OnBrowseLog)
        self.lyt.Add(b, 4, 3, width = 50)
        
        b = pyfbsdk.FBButton()
        b.Caption = "Print last exec line"
        b.OnClick.Add(self.OnPrintLastExec)
        self.lyt.Add(b, 5, 0, width = 150)
        
        b = pyfbsdk.FBButton()
        b.Caption = "Print last exec log"
        b.OnClick.Add(self.OnPrintExecLog)
        self.lyt.Add(b, 5, 1, width = 150)
        
        
MbDebuggerInstance = None
def InitDebugger():
    """
        Method to init all the debugging environment.
    """    

    # init log file:
    d, f = os.path.split(InitDebugger.func_code.co_filename)
    logdir = os.path.join(d, "..", "..")
    logfile = os.path.join(logdir, "lastexec.log")
    logfile = os.path.abspath(logfile)
    filepopup.Path = os.path.abspath(logdir)

    # init debugger
    global MbDebuggerInstance    
    MbDebuggerInstance = MbDebugger()
    # Don't forget to add the debugger to the tool manaager list of tools
    pyfbsdk_additions.FBAddTool(MbDebuggerInstance)
    
    MbDebuggerInstance.SetLogName(logfile)
    
InitDebugger()