import os
import platform

# add this block for message box
import clr
clr.AddReference("Ans.UI.Toolkit")
clr.AddReference("Ans.UI.Toolkit.Base")
import Ansys.UI.Toolkit


def writeFormat(file, format, content, delimiter=''):
    # delimiter = '' space, default
    #           = ','

    string_fmt = ''
    for i, t in enumerate(format):
        if t == 'd':
            string_fmt += '{0[' + str(i) + ']:10d}'
        elif t == 'e' or t == 'E':
            string_fmt += '{0[' + str(i) + ']:16.6' + t + '}'
        if delimiter != '':
            string_fmt += delimiter

    if delimiter != '':
        string_fmt = string_fmt.rstrip(delimiter)
    string_fmt += '\n'

    # print string_fmt
    file.write(string_fmt.format(content))
    return


def transpose(matrix):
    return  [list(x) for x in zip(*matrix)]


def is_os_64bit():
    return platform.machine().endswith('64')


def No1DSGForBeamModel():
    message = "\n".join([
        "1D SG can not be used for Beam Model!",
        "Please define 2D SG or 3D SG for Beam Model."])
    Ansys.UI.Toolkit.MessageBox.Show(message)


def set1DSGWrongMessage(e):
    message = "\n".join([
        "Something is wrong when reading ACP data",
        "Please double check ACP models",
        "The error are:",
        e])
    Ansys.UI.Toolkit.MessageBox.Show(message)

def setMaterialWrongMessage(e):
    message = "\n".join([
        "Something is wrong when reading material data",
        "Please double check material models",
        "The error are:",
        e])
    Ansys.UI.Toolkit.MessageBox.Show(message)

def setNodeWrongMessage(e):
    message = "\n".join([
        "Something is wrong when reading nodal coordinates data",
        "Please double check nodes of the model",
        "The error are:",
        e])
    Ansys.UI.Toolkit.MessageBox.Show(message)

def setElementWrongMessage(e):
    message = "\n".join([
        "Something is wrong when reading element connectivity data",
        "Please double check elements of the model",
        "The error are:",
        e])
    Ansys.UI.Toolkit.MessageBox.Show(message)

def element2DTypeWrongMessage():
    message = "\n".join([
        "Unspported 2D element type!",
        "Please use the following 2D element type:",
        "Linear triangular element: kTri3",
        "Quadratic triangular element: kTri6",
        "Linear quadrilateral element: kQuad4",
        "Quadratic quadrilateral element: kQuad8"])
    Ansys.UI.Toolkit.MessageBox.Show(message)

def element3DTypeWrongMessage():
    message = "\n".join([
        "Unspported 3D element type!",
        "Please use the following 3D element type:",
        "Linear tetrahedral element: kTet4",
        "Quadratic tetrahedral element: kTet10",
        "Linear brick element: kHex8",
        "Quadratic brick element: kHex20"])
    Ansys.UI.Toolkit.MessageBox.Show(message)

# Get Failure Analysis type. If Failure strength, Failure Index, and Faliure Envelope, 1,2,3, respectiviely.
# Use: getFailuretype(user_dir, file_name_sc)
# Return: aperiodic
def getFailuretype(workfiletest):
        with open(workfiletest, 'r') as sc:
            line = sc.readline()
            line = line.split()
            return (line)
        return 1  # error
