import System
import clr
import sys
import os
from WorksheetBase import *
from GridEditor import *
from Ansys.ACT.Interfaces.UserObject import *

class PGEditor(WSBase):
    def __init__(self,api,load,prop):
        WSBase.__init__(self,api,load,prop)
        self.WithAddLine = True
        self.WithDeleteLine = True
        
    def CreateUI(self):
        WSBase.CreateUI(self)
    
        self.ui = GridEditor(self.api,self.prop.Caption,self)
        self.ui.WithAddLine = self.WithAddLine
        self.ui.WithDeleteLine = self.WithDeleteLine
        self.ui.CreateUI()

        self.ui.Grid.BeginUpdate()
        self.InitColumns()
        self.InitLines()
        self.ui.Grid.EndUpdate()
        
    def InitLines(self):
        for irow in range(self.prop.RowCount):
            self.AddLine(irow)
            
    def InitColumns(self):
        icol = 0        
        cols = []
        for prop in self.prop.AllDescendants:
            if prop.IsGroup and prop.Display!=PropertyDisplayEnum.Property:
                continue
            col = ColumnGridEditor(self.ui,icol)
            col.Tag = prop
            col.HeaderText = prop.Caption
            #col.Visible = prop.Visible
            cols.Add(col)
            icol += 1

        self.ui.AddColumns(cols)

    def GetValues(self):
        v = []
        icol = 0
        for prop in self.prop.AllDescendants:
            if prop.IsGroup and prop.Display!=PropertyDisplayEnum.Property:
                continue
            for i in range(self.ui.Grid.Rows.Count):
                val = self.ui.GetCellValue(i,icol)
                v.Add(val)
            icol += 1
        return v

    def onapply(self,load,prop):
        icol = 0
        nr = self.ui.Grid.Rows.Count
        if nr>prop.RowCount:
            diff = nr - prop.RowCount
            for i in range(diff):
                prop.AddRow()
        elif nr<prop.RowCount:
            diff = prop.RowCount - nr
            for i in range(diff):
                prop.DeleteRow(nr+diff-i-1)
        for i in range(self.ui.Grid.Rows.Count):
            prop.ActiveRow = i
            for j in range(self.ui.Grid.Columns.Count):
                val = self.ui.GetCellValue(i,j)
                self.ui.Grid.Cells[i,j].Tag.Tag.Value = val
            prop.SaveActiveRow()
        WSBase.onapply(self,load,prop)
        
    def value2string(self,load,prop,val):
        txt = "Tabular Data"
        return txt

    def AddLine(self,irow):
        row = RowGridEditor(self.ui,irow)
        row.Visible = True
        self.ui.AddRows([row])
        icol = 0
        if irow>=self.prop.RowCount:
            self.prop.ActiveRow = -1
        else:
            self.prop.ActiveRow = irow
        for prop in self.prop.AllDescendants:
            if prop.IsGroup and prop.Display!=PropertyDisplayEnum.Property:
                continue
            value = prop.InternalValue
            cell = CellGridEditor(self.ui,irow,icol)
            cell.Tag = prop
            cell.Control = prop.Control
            cell.OnActivate = DefaultCellOnActivate
            cell.OnValidate = DefaultCellOnValidate
            if cell.Control=="select":
                cell.OnValidate = CellSelectOnValidate
                cell.OnActivate = CellSelectOnActivate
                cell.Options = []
                n = prop.NumOptions
                for iop in range(n):
                    cell.Options.Add(prop.GetOptionString(iop))
            elif cell.Control=="applycancel":
                cell.OnValidate = CellApplyCancelOnValidate
            cell.String2Value = DefaultPGString2Value
            cell.Value2String = DefaultPGValue2String            
            cell.Value = value
            self.ui.SetCell(irow,icol,cell)
            icol += 1   
        self.RefreshLine(irow)
            
    def RefreshLine(self,irow):
        for icol in range(self.ui.Grid.Columns.Count):
            cell = self.ui.Grid.Cells[irow,icol]
            cellDef = cell.Tag
            prop = cellDef.Tag
            prop.Value = cellDef.Value
        for icol in range(self.ui.Grid.Columns.Count):
            cell = self.ui.Grid.Cells[irow,icol]
            cellDef = cell.Tag
            prop = cellDef.Tag
            prop.InternalValue = cellDef.Value
            cellDef.ReadOnly = False
            if prop.ReadOnly:
                cellDef.Status = CellStatusEnum.ReadOnly
                cellDef.ReadOnly = True
            elif not prop.Visible:
                cellDef.Status = CellStatusEnum.Disabled
                cellDef.ReadOnly = True
            elif not prop.IsValid:
                cellDef.Status = CellStatusEnum.Invalid
            else:
                cellDef.Status = CellStatusEnum.Editable
            if prop.UnitString!="":
                cellDef.UnitString = prop.UnitString
            if cellDef.Value!=None:
                strval = DefaultPGValue2String(cellDef,cellDef.Value)
                cellDef.ValueString = strval
            self.ui.RefreshCell(cell)

    def PasteLine(self,irow,icol,vals):
        if irow==self.ui.Grid.RowCount:
            self.AddLine(irow)
        for ic in range(self.ui.Grid.Columns.Count):
            cell = self.ui.Grid.Cells[irow,ic]
            cellDef = cell.Tag
            prop = cellDef.Tag
            prop.Value = cellDef.Value
        
        ic = icol
        for val in vals:
            cell = self.ui.Grid.Cells[irow,ic]
            cellDef = cell.Tag
            prop = cellDef.Tag
            value = val
            #if cellDef.OnActivate!=None:
            #    cellDef.OnActivate(cell,cellDef)
            #if cellDef.Control=="select":
            #    if not cellDef.Options.Contains(val):
            #        continue
            val = cellDef.String2Value(cellDef,value)
            if val==None:
                continue
            cellDef.Value = val
            if cellDef.UnitString==None:
                cellDef.ValueString = cellDef.Value2String(cellDef,val)
            else:
                cellDef.ValueString = val.ToString() + " [" + cellDef.UnitString + "]"
            ic += 1

        self.RefreshLine(irow)

                 

def DefaultPGString2Value(cell,str):
    return cell.Tag.String2Value(str)

def DefaultPGValue2String(cell,val):
    return cell.Tag.Value2String(val)

def DefaultCellOnValidate(cell,cellDef):
    cellDef.Tag.InternalValue = cellDef.Value
    cellDef.Tag.Validate()
    irow = cellDef.iRow
    for icol in range(cellDef.GridEditor.Grid.Columns.Count):
        cellCur = cellDef.GridEditor.Grid.Cells[irow,icol]
        cellDefCur = cellCur.Tag
        prop = cellDefCur.Tag
        if prop.IsGroup and prop.Display!=PropertyDisplayEnum.Property:
            continue
        value = prop.InternalValue
        cellDefCur.Value = value

def DefaultCellOnActivate(cell,cellDef):
    cellDef.Tag.InternalValue = cellDef.Value
    ret = cellDef.Tag.OnActivateProperty(True,cell.ExpansionBoxBounds.X,cell.ExpansionBoxBounds.Y,cell.ExpansionBoxBounds.Width,cell.ExpansionBoxBounds.Height)
    if ret==2:
        cellDef.Value = cellDef.Tag.InternalValue
        cellDef.GridEditor.Tag.RefreshLine(cell.StartRowIndex)
        return

def CellApplyCancelOnValidate(cell,cellDef):
    cellDef.Tag.OnButtonClick("Apply")
    cellDef.Value = cellDef.Tag.InternalValue
    cellDef.GridEditor.Tag.RefreshLine(cell.StartRowIndex)
    return cellDef.Value

def CellSelectOnActivate(cell,cellDef):
    cellDef.Tag.OnActivateProperty(True,cell.ExpansionBoxBounds.X,cell.ExpansionBoxBounds.Y,cell.ExpansionBoxBounds.Width,cell.ExpansionBoxBounds.Height)
    n = cellDef.Tag.NumOptions
    if n>0:
        cellDef.Options = []
        for i in range(n):
            cellDef.Options.Add(cellDef.Tag.GetOptionString(i))

def CellSelectOnValidate(cell,cellDef):
    if cellDef.Control=="select":
        value = cellDef.Tag.GetOption(cell.DropDownControl.SelectedIndices[0])
    return value
