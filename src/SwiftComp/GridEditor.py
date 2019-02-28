import System
import clr
import sys
import os
clr.AddReference("Ans.Utilities")
clr.AddReference("Ans.UI.Toolkit")
clr.AddReference("Ans.UI.Toolkit.Base")
from Ansys.Utilities import *
from Ansys.UI.Toolkit import *
from Ansys.UI.Toolkit.Drawing import *

class CellStatusEnum:
    Editable = 0
    ReadOnly = 1
    Invalid = 2
    Edited = 3
    Disabled = 4

def createColor(r,g,b):
    c = Color()
    c.Red = r
    c.Green = g
    c.Blue = b
    return c

class CellGridEditor:
    def __init__(self,gridEditor,row,col):
        self.GridEditor = gridEditor
        self.Tag = None
        self.iRow = row
        self.iCol = col
        self.Control = "text"
        self.ReadOnly = False
        self.Status = CellStatusEnum.Editable
        self.Value = None
        self.UnitString = None
        self.ValueString = ""
        self.OnValidate = None
        self.OnActivate = None
        self.IsValid = DefaultCellIsValid
        self.Value2String = DefaultCellValue2String
        self.String2Value = DefaultCellString2Value
        self.Options = []

    def SetBackColor(self,cell):
        if self.Status==CellStatusEnum.Editable:
            cell.BackColor = self.GridEditor.EditableColor
        elif self.Status==CellStatusEnum.ReadOnly:
            cell.BackColor = self.GridEditor.ReadOnlyColor
        elif self.Status==CellStatusEnum.Invalid:
            cell.BackColor = self.GridEditor.InvalidColor
        elif self.Status==CellStatusEnum.Edited:
            cell.BackColor = self.GridEditor.EditedColor
        elif self.Status==CellStatusEnum.Disabled:
            cell.BackColor = self.GridEditor.DisabledColor  
        else:
            cell.BackColor = self.GridEditor.DefaultColor 

def DefaultCellValue2String(cell,val):
    return val.ToString()

def DefaultCellString2Value(cell,val):
    try:
        if cell.Control=="integer":
            return System.Int32.Parse(val)
        elif cell.Control=="float":
            return System.Double.Parse(val)
    except:
        return None
    return val

def DefaultCellIsValid(cell):
    if cell.ValueString==None or cell.ValueString=="":
        return False
    return True


class ColumnGridEditor:
    def __init__(self,gridEditor,col):
        self.GridEditor = gridEditor
        self.Tag = None
        self.iCol = col
        self.Width = 60
        self.Visible = True
        self.HeaderText = ""

class RowGridEditor:
    def __init__(self,gridEditor,row):
        self.GridEditor = gridEditor
        self.Tag = None
        self.iRow = row
        self.Visible = True
        self.HeaderText = ""

class GEGridViewButtonCell(GridViewButtonCell):
    def __init__(self,text,btn):
        GridViewButtonCell.__init__(self,text,btn)
        self.Up = True

    def OnMouseDown(self,event):
        GridViewButtonCell.OnMouseDown(self,event)
        if self.Tag.ReadOnly:
            return
        if not self.Buttons[0].Visible:
            cellDef = self.Tag
            if cellDef.OnActivate!=None:
                cellDef.OnActivate(self,cellDef)
            if cellDef.Control=="custom":
                return
            self.Buttons[0].Visible = True
            self.Buttons[0].Enabled = True
            self.Up = False

    def OnMouseUp(self,event):
        if self.Up:
            GridViewButtonCell.OnMouseUp(self,event)
        self.Up = True

    def OnLostFocus(self, event):
        self.Buttons[0].Enabled = False
        self.Buttons[0].Visible = False
        GridViewButtonCell.OnLostFocus(self,event)

class GEGridViewDropDownCell(GridViewDropDownCell):
    def __init__(self):
        GridViewDropDownCell.__init__(self)

    def OnBeforeDropDownShown(self):
        self.Select()
        cellDef = self.Tag
        if cellDef.OnActivate!=None:
            cellDef.OnActivate(self,cellDef)
        if cellDef.Control=="select":
            n = cellDef.Options.Count
            if n > 0:
                strs = System.Array.CreateInstance(GridViewDropDownCell.GridViewDropDownItem,n)
                for i in range(n):
                    strs[i] = GridViewDropDownCell.GridViewDropDownItem(cellDef.Options[i])
                self.ItemList = strs
        GridViewDropDownCell.OnBeforeDropDownShown(self)

class GridEditor(Window):
    def __init__(self,api,title,tag):
        self.ImgLib = ImageLibrary()
        self.ImgLib.AddImagesFromDirectory(os.path.dirname(__file__))
        self.ExtAPI = api
        self.Tag = tag
        self.Title = title
        self.Grid = None
        self.WithAddLine = False
        self.WithDeleteLine = False
        self.AllowClose = False

        self.DefaultColor = createColor(255,255,255)
        self.EditableColor = createColor(255,255,255)
        self.ReadOnlyColor = createColor(192,192,192)
        self.InvalidColor = createColor(255,240,0)
        self.EditedColor = createColor(255,255,255)
        self.DisabledColor = createColor(160,160,160)

    def AddColumns(self,cols):
        for col in cols:
            column = self.Grid.Columns.Add()
            column.AutoSizeMode = GridViewAutoSizeMode.Fill
            column.Text = col.HeaderText
            column.Width = col.Width
            column.Tag = col
            column.Visible = col.Visible

    def AddRows(self,rows):
        for row in rows:
            r = self.Grid.Rows.Add()
            r.Text = row.HeaderText
            r.Tag = row
            r.Visible = row.Visible

    def SetCell(self,irow,icol,cellDef):
        cell = None
        if cellDef.Control=="select":
            cell = GEGridViewDropDownCell()
            cell.ReadOnly = cellDef.ReadOnly
            n = cellDef.Options.Count
            strs = System.Array.CreateInstance(GridViewDropDownCell.GridViewDropDownItem, n)
            for i in range(n):
                strs[i] = GridViewDropDownCell.GridViewDropDownItem(cellDef.Options[i])
            cell.ItemList = strs
        elif cellDef.Control=="applycancel":
            cell = GEGridViewButtonCell(cellDef.ValueString,"Apply")
            cell.ReadOnly = True
            cell.Buttons[0].Enabled = False
            cell.Buttons[0].Visible = False
            cell.Buttons[0].Click += DefaultOnClickButtonCell 
        elif cellDef.Control=="custom":
            cell = GEGridViewButtonCell(cellDef.ValueString,"Apply")
            cell.ReadOnly = True
            cell.Buttons[0].Enabled = False
            cell.Buttons[0].Visible = False
        else:
            cell = GridViewTextCell(cellDef.ValueString)
            cell.ReadOnly = cellDef.ReadOnly
            if cellDef.Value!=None:
                cell.EditText = GetEditableValue(cellDef.ValueString) #cellDef.Value.ToString()
            else:
                cell.EditText = ""
        cell.Tag = cellDef
        if cellDef.Status==CellStatusEnum.Disabled:
            cell.Text = ""
        else:
            cell.Text = cellDef.ValueString
        cellDef.SetBackColor(cell)                        
        self.Grid.Cells.SetCell(irow, icol, cell)

    def RefreshCell(self,cell):
        if cell.Tag.Control != "applycancel" and cell.Tag.Control != "custom":
            cell.ReadOnly = cell.Tag.ReadOnly
        if cell.Tag.Status == CellStatusEnum.Disabled:
            cell.Text = ""
        else:
            cell.Text = cell.Tag.ValueString
        if cell.Tag.Control == "select":
            n = cell.Tag.Options.Count
            strs = System.Array.CreateInstance(GridViewDropDownCell.GridViewDropDownItem,n)
            for i in range(n):
                strs[i] = GridViewDropDownCell.GridViewDropDownItem(cell.Tag.Options[i])
            cell.ItemList = strs
        else:
            if cell.Tag.Value!=None:
                cell.EditText = GetEditableValue(cell.Tag.ValueString) #cell.Tag.Value.ToString()
            else:
                cell.EditText = ""
        cell.Tag.SetBackColor(cell)

    def AddImageDir(self,dir):
        self.ImgLib.AddImagesFromDirectory(dir)

    def AddTool(self,imgName,cb):
        img = self.ImgLib[imgName]
        button = ToolBarButton(img)
        button.ToolBarButtonClick += cb
        self.ToolBars[0].Items.Add(button)

    def CreateUI(self):
        self.CreateToolBar()
        self.StatusBar.Hide()
        self.ExtAPI.UserInterface.SetParent(self.Handle, self.ExtAPI.UserInterface.MainHandle);
        self.Text = self.Title
        
        if self.WithAddLine and self.Tag.AddLine!=None:
            self.AddTool("addrow", self.OnAddLine)

        self.Style = DialogStyle.SizableToolWindow
        #self.Height = 200
        #self.Width = 50

        self.Grid = GridView()
        self.Grid.ColumnHeadersVisible = True

        self.Add(self.Grid) 

        self.BeforeClose += self.OnBeforeClose
        self.Grid.BeforeCellEdit += self.OnBeforeCellEdit
        self.Grid.AfterCellEdit += self.OnAfterCellEdit
        self.Grid.BeforeShowContextMenu += self.OnBeforeShowContextMenu

        self.TopMost = True


    def OnBeforeShowContextMenu(self,sender,args):
        menu = ContextMenu()

        clip = Clipboard.GetDataObject()
        if clip.ContainsText():
            item = menu.AddMenuItem("Paste")
            item.Tag = args
            item.Clicked += self.OnPaste
        
            if self.WithDeleteLine:
                menu.AddMenuSeparator()
        
        if self.WithDeleteLine:
            item = menu.AddMenuItem("Delete selected row(s)")
            item.Tag = args
            img = self.ImgLib["deleterow"]
            item.Image = img
            item.Clicked += self.OnDelClicked

        menu.Show(args.GlobalX,args.GlobalY)

    def OnPaste(self,sender,args):
        clip = Clipboard.GetDataObject()
        txt = clip.GetText()
        lines = txt.splitlines()
        cells = sender.Tag.SelectedCells
        refCell = None
        refEndCell = None
        for cell in cells:
            if refCell==None:
                refCell = cell
                refEndCell = cell
            else:
                if cell.StartRowIndex<refCell.StartRowIndex or cell.StartColumnIndex<refCell.StartColumnIndex:
                    refCell = cell
                if cell.EndRowIndex>refEndCell.EndRowIndex or cell.EndColumnIndex>refEndCell.EndColumnIndex:
                    refEndCell = cell
        if cells.Count==1:
            refEndCell = None
        irow = 0
        if refCell!=None:
            irow = refCell.StartRowIndex

        self.Grid.BeginUpdate()
        for line in lines:
            if refEndCell!=None and irow>refEndCell.EndRowIndex:
                break
            if not self.WithAddLine and irow>=self.Grid.RowCount:
                break
            vals = line.split("\t")
            icol = 0
            if refCell!=None:
                icol = refCell.StartColumnIndex
            self.Tag.PasteLine(irow,icol,vals)
            irow += 1
        self.Grid.EndUpdate()

    def OnDelClicked(self,sender,args):
        cells = sender.Tag.SelectedCells
        rows = []
        for cell in cells:
            idx = cell.StartRowIndex
            if not rows.Contains(idx):
                rows.Add(idx)
        rows.sort()
        rows.reverse()
        for row in rows:
            self.Grid.Rows.RemoveAt(row)
        return

    def OnBeforeClose(self,args):
        if not self.AllowClose:
            args.InterruptClose = True

    def OnBeforeCellEdit(self,sender,args):
        cellDef = args.Cell.Tag

        if cellDef.OnActivate != None:
            value = cellDef.OnActivate(args.Cell,cellDef)

        if cellDef.ReadOnly:
            args.CancelEdit = True

    def OnAfterCellEdit(self,sender,args):
        if args.Value==None:
            return

        value = args.Value
        cellDef = args.Cell.Tag

        if cellDef.Control=="select":
            if args.Cell.DropDownControl.SelectedIndices.Count>0 and cellDef.Options.Count>args.Cell.DropDownControl.SelectedIndices[0]:
                value = cellDef.Tag.Options[args.Cell.DropDownControl.SelectedIndices[0]]

        if cellDef.Control=="applycancel":
            if cellDef.OnValidate!=None:
                value = cellDef.OnValidate(args.Cell, cellDef)
            return

        if cellDef.Control=="custom":
            if cellDef.OnValidate!=None:
                value = cellDef.OnValidate(args.Cell, cellDef)
            return

        if value == None:
            return
        val = cellDef.String2Value(cellDef,value)
        if val != None:
            cellDef.Value = val
        if cellDef.UnitString == None:
            cellDef.ValueString = cellDef.Value2String(cellDef,val)
        elif cellDef.Value != None:
            cellDef.ValueString = cellDef.Value.ToString() + " [" + cellDef.UnitString + "]"
        else:
            cellDef.ValueString = ""

        if self.Tag:
            self.Tag.RefreshLine(args.Cell.StartRowIndex)
        else:
            args.Cell.Text = cellDef.ValueString

        if cellDef.OnValidate != None:
            value = cellDef.OnValidate(args.Cell,cellDef)
            if self.Tag:
                self.Tag.RefreshLine(args.Cell.StartRowIndex)

        args.CancelEdit = True

    def GetDialogSize(self):
        return [self.Width,self.Height]

    def GetDialogLocation(self):
        return [self.Location.X,self.Location.Y]

    def GetCellValue(self,irow,icol):
        cell = self.Grid.Cells[irow,icol]
        return cell.Tag.Value

    def ComputeSize(self):
        width = 2
        for col in self.Grid.Columns:
            width += col.Tag.Width
        self.Width = width
        dw = width - self.ClientSize.Width
        self.Width += dw

    def ShowGridEditor(self,corner,x,y,size=None):
        if size==None:
            self.ComputeSize()
        else:
            self.Width = size[0]
            self.Height = size[1]
        if corner=="bl":
            if Application.IsUsingQt:
                self.Location = Point(x,y-self.Height)
            else:
                self.Location = self.PointToClient(Point(x,y-self.Height))
        elif x!=None and y!=None:
            if Application.IsUsingQt:
                self.Location = Point(x,y)
            else:
                self.Location = self.PointToClient(Point(x,y))
        self.Show()
        
    def HideGridEditor(self):
        self.Hide()

    def OnAddLine(self,sender,args):
        irow = self.Grid.RowCount
        self.Tag.AddLine(irow)

def GetEditableValue(displayValue):
    """Extract the numerical value if the displayValue contains an unit."""
    unitPos = displayValue.find("[")
    if(unitPos > 0):
        return displayValue[0:unitPos]
    return displayValue


def DefaultOnClickButtonCell(sender,args):
    sender.Enabled = False
    sender.Visible = False

    if sender.ParentGridViewCell.Tag.OnValidate!=None:
        sender.ParentGridViewCell.Tag.OnValidate(sender.ParentGridViewCell, sender.ParentGridViewCell.Tag)

