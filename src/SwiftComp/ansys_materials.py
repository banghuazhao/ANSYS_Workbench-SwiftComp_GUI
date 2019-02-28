"""
Basic functionalities to access material data.

Example:

import materials
body = ExtAPI.DataModel.GeoData.Assemblies[0].Parts[0].Bodies[0]
mat = body.Material
prop = materials.GetMaterialPropertyByName(mat,"Elasticity")
val = materials.InterpolateData(prop["Temperature"][1:],prop["Young's Modulus"][1:],10.)
val = materials.InterpolateData(prop["Temperature"][1:],prop["Young's Modulus"][1:],20.)
"""

import System
import clr

def GetListMaterialProperties(mat):
    """
    Return the list of material property names for the given material.
    """
    list = []
    for prop in mat.MaterialProperties:
        list.Add(prop.TypeName)
    return list

def GetMaterialPropertyByName(mat,name):
    """
    Return the material property by its name for the given material.
    """
    prop = mat.GetPropertyByType(name)
    if prop == None: return
    data = prop.GetMaterialPropertyDataByType(name,None,None)
    if data is None: return
    table = {}
    for v in data.Variables:
        values = []
        values.Add(v.Unit)
        num = v.Count()
        for i in range(num):
            values.Add(v.GetAsDouble(i))
        table.Add(v.TypeName,values)
    return table

def GetMaterialPropertyDataTypes(mat, name):
    prop = mat.GetPropertyByType(name)
    if prop == None: return
    list = []
    for d in prop.MaterialPropertyDatas:
        list.Add(d.Name)
    return list

def GetMaterialPropertyByNameAndDataType(mat,name, dataName):
    """
    Return the material property by its name and its data type for the given material.
    """
    prop = mat.GetPropertyByType(name)
    if prop == None: return
    data = prop.GetMaterialPropertyDataByType(dataName,None,None)
    if data is None: return
    table = {}
    for v in data.Variables:
        values = []
        values.Add(v.Unit)
        num = v.Count()
        for i in range(num):
            values.Add(v.GetAsDouble(i))
        table.Add(v.TypeName,values)
    return table

def InterpolateData(vx,vy,vin):
    """
    Find the value associated to vin by interpolating the table (vx,vy).
    """
    if vx.Count != vy.Count:
        return None
    n = vx.Count
    tab = {}
    for i in range(n):
        tab.Add(i,vx[i])
    perm = sorted(tab,key=tab.get)
    if vin <= vx[perm[0]]: return vy[perm[0]]
    if vin >= vx[perm[n-1]]: return vy[perm[n-1]]
    i = 1
    while vin > vx[perm[i]]:
        i += 1
    t = (vin-vx[perm[i-1]])/(vx[perm[i]]-vx[perm[i-1]])
    return t*vy[perm[i]]+(1.-t)*vy[perm[i-1]]
