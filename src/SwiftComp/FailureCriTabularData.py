import System
import clr
import sys
import subprocess
import os
import sg
import sg_filesystem
from PropertyGroupEditorAA import *
from Ansys.ACT.Interfaces.UserObject import *

class FCTabularData(PGEditor):
    def __init__(self,api,load,prop):
        PGEditor.__init__(self,api,load,prop)
        self.steps = []
        self.WithAddLine = False
        self.WithDeleteLine = False
        
    def CreateUI(self):
        PGEditor.CreateUI(self)
    
    def InitLines(self):
        SGFileSystem = sg_filesystem.SGFileSystem(ExtAPI)
        SG = sg.StructureGenome()
        with open(SGFileSystem.user_dir + 'SG.pickle', 'rb') as f:
            SG = pickle.load(f)

        self.steps = [x for x in range(1,SG.nmate + 1)] 
        irow = 0
        for step in self.steps:
            Material = SG.Material[irow]

            tensileUltimateStrength = None
            if Material.MaterialProperty[0].tensileUltimateStrength:
                tensileUltimateStrength = Material.MaterialProperty[0].tensileUltimateStrength

            compressiveUltimateStrength = None
            if Material.MaterialProperty[0].compressiveUltimateStrength:
                compressiveUltimateStrength = Material.MaterialProperty[0].compressiveUltimateStrength

            orthotropicStressLimits = None
            if Material.MaterialProperty[0].orthotropicStressLimits:
                orthotropicStressLimits = Material.MaterialProperty[0].orthotropicStressLimits

            orthotropicStrainLimits = None
            if Material.MaterialProperty[0].orthotropicStrainLimits:
                orthotropicStrainLimits = Material.MaterialProperty[0].orthotropicStrainLimits

            self.AddLine(irow)
            icol = 0
            for p in self.prop.AllDescendants:

                if p.IsGroup and p.Display!=PropertyDisplayEnum.Property:
                    continue

                if p.Name=="Material Name":
                    cell = self.ui.Grid.Cells[irow,icol]
                    cellDef = cell.Tag
                    cellDef.Value = Material.name
                elif p.Name=="Material Type":
                    cell = self.ui.Grid.Cells[irow,icol]
                    cellDef = cell.Tag
                    if Material.isotropy == 0:
                        cellDef.Value = 'Isotropic'
                    elif Material.isotropy == 1:
                        cellDef.Value = 'Orthotropic'
                    elif Material.isotropy == 2:
                        cellDef.Value = 'Anisotropic'
                
                if tensileUltimateStrength:
                    if p.Name=="X_t":
                        cell = self.ui.Grid.Cells[irow,icol]
                        cellDef = cell.Tag
                        cellDef.Value = tensileUltimateStrength
                    elif p.Name=="X":
                        cell = self.ui.Grid.Cells[irow,icol]
                        cellDef = cell.Tag
                        cellDef.Value = tensileUltimateStrength

                if tensileUltimateStrength:
                    if p.Name=="X_c":
                        cell = self.ui.Grid.Cells[irow,icol]
                        cellDef = cell.Tag
                        cellDef.Value = tensileUltimateStrength

                if orthotropicStressLimits:
                    if p.Name=="X_t":
                        cell = self.ui.Grid.Cells[irow,icol]
                        cellDef = cell.Tag
                        cellDef.Value = orthotropicStressLimits['X_t']
                    elif p.Name=="Y_t":
                        cell = self.ui.Grid.Cells[irow,icol]
                        cellDef = cell.Tag
                        cellDef.Value = orthotropicStressLimits['Y_t']
                    elif p.Name=="Z_t":
                        cell = self.ui.Grid.Cells[irow,icol]
                        cellDef = cell.Tag
                        cellDef.Value = orthotropicStressLimits['Z_t']
                    elif p.Name=="X_c":
                        cell = self.ui.Grid.Cells[irow,icol]
                        cellDef = cell.Tag
                        cellDef.Value = orthotropicStressLimits['X_c']
                    elif p.Name=="Y_c":
                        cell = self.ui.Grid.Cells[irow,icol]
                        cellDef = cell.Tag
                        cellDef.Value = orthotropicStressLimits['Y_c']
                    elif p.Name=="Z_c":
                        cell = self.ui.Grid.Cells[irow,icol]
                        cellDef = cell.Tag
                        cellDef.Value = orthotropicStressLimits['Z_c']
                    elif p.Name=="R":
                        cell = self.ui.Grid.Cells[irow,icol]
                        cellDef = cell.Tag
                        cellDef.Value = orthotropicStressLimits['R']
                    elif p.Name=="T":
                        cell = self.ui.Grid.Cells[irow,icol]
                        cellDef = cell.Tag
                        cellDef.Value = orthotropicStressLimits['T']
                    elif p.Name=="S":
                        cell = self.ui.Grid.Cells[irow,icol]
                        cellDef = cell.Tag
                        cellDef.Value = orthotropicStressLimits['S']
                    elif p.Name=="X":
                        cell = self.ui.Grid.Cells[irow,icol]
                        cellDef = cell.Tag
                        cellDef.Value = orthotropicStressLimits['X_t']
                    elif p.Name=="Y":
                        cell = self.ui.Grid.Cells[irow,icol]
                        cellDef = cell.Tag
                        cellDef.Value = orthotropicStressLimits['Y_t']
                    elif p.Name=="Z":
                        cell = self.ui.Grid.Cells[irow,icol]
                        cellDef = cell.Tag
                        cellDef.Value = orthotropicStressLimits['Z_t']

                if orthotropicStrainLimits:
                    if p.Name=="Xe_t":
                        cell = self.ui.Grid.Cells[irow,icol]
                        cellDef = cell.Tag
                        cellDef.Value = orthotropicStrainLimits['Xe_t']
                    elif p.Name=="Ye_t":
                        cell = self.ui.Grid.Cells[irow,icol]
                        cellDef = cell.Tag
                        cellDef.Value = orthotropicStrainLimits['Ye_t']
                    elif p.Name=="Ze_t":
                        cell = self.ui.Grid.Cells[irow,icol]
                        cellDef = cell.Tag
                        cellDef.Value = orthotropicStrainLimits['Ze_t']
                    elif p.Name=="Xe_c":
                        cell = self.ui.Grid.Cells[irow,icol]
                        cellDef = cell.Tag
                        cellDef.Value = orthotropicStrainLimits['Xe_c']
                    elif p.Name=="Ye_c":
                        cell = self.ui.Grid.Cells[irow,icol]
                        cellDef = cell.Tag
                        cellDef.Value = orthotropicStrainLimits['Ye_c']
                    elif p.Name=="Ze_c":
                        cell = self.ui.Grid.Cells[irow,icol]
                        cellDef = cell.Tag
                        cellDef.Value = orthotropicStrainLimits['Ze_c']
                    elif p.Name=="Re":
                        cell = self.ui.Grid.Cells[irow,icol]
                        cellDef = cell.Tag
                        cellDef.Value = orthotropicStrainLimits['Re']
                    elif p.Name=="Te":
                        cell = self.ui.Grid.Cells[irow,icol]
                        cellDef = cell.Tag
                        cellDef.Value = orthotropicStrainLimits['Te']
                    elif p.Name=="Se":
                        cell = self.ui.Grid.Cells[irow,icol]
                        cellDef = cell.Tag
                        cellDef.Value = orthotropicStrainLimits['Se']

                icol += 1

            self.RefreshLine(irow)
            irow += 1

    #def isvalid(self,load,prop):
    #    SG = structuregenome.StructureGenome
   #     [status, SG.mat_libf, SG.bodyid_matid, mat_count1] = hom_main_fun.materialLibraryFailureConstants(ExtAPI)
    #    self.steps = [x for x in range(1,mat_count1)]
    #    #self.steps = self.load.dataMATID #FailureAnalysisParameters.nMate ##self.load.Analysis.StepsEndTime
    #    while prop.RowCount>self.steps.Count:
    #         prop.DeleteRow(prop.RowCount-1)
    #    if prop.RowCount!=self.steps.Count:
    #        return False
   #     if prop.ValidState==ValidStateEnum.StateUnknown:
    #        isv = True
    #        for i in range(prop.RowCount):
    #            prop.ActiveRow = i
    #            for p in prop.Properties.AllDescendants:
    #                if p.Visible:
    #                    if p.IsGroup:
    #                        if p.Display==PropertyDisplayEnum.Property:
    #                            isv &= p.IsValid;
     #                   else:
    #                        isv &= p.IsValid;
    #        return isv
    #    else:
    #        if prop.ValidState==ValidStateEnum.StateValid:
    #            return True
    #        return False