import System
import clr
import sys

class WSBase:
    """ 
    Base object for all worksheet associated to an applycancel property
    """

    def __init__(self,api,load,prop):
        self.api = api
        self.load = load
        self.prop = prop
        self.ui = None
        self.size = None
        
    def CreateUI(self):
        self.ui = None
        
    def Show(self):
        rect = self.prop.DisplayRect
        if self.ui!=None:
            self.ui.ShowGridEditor("bl",rect[0]+rect[2],rect[1]+rect[3],self.size)
        
    def Hide(self):
        if self.ui!=None:
            self.size = self.ui.GetDialogSize()
            self.ui.HideGridEditor()
        
    def Reset(self):
        self.Hide()
        self.CreateUI()
        self.Show()
        
    def GetValues(self):
        return None
        
    def onapply(self,load,prop):
        prop.Value = "Tabular Data"
        self.Hide()
    
    def oncancel(self,load,prop):
        self.Hide()

    def onactivate(self,load,prop):
        self.Reset()
        
    def value2string(self,load,prop,val):
        if val==None:
            return ""
        return val.ToString()
