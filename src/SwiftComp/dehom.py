import dehom_func

import errorcheck
import utilities
import pickle

import sg
import sg_filesystem
import sg_result
import sg_structural_result_list

# add this block for message box
import clr
clr.AddReference("Ans.UI.Toolkit")
clr.AddReference("Ans.UI.Toolkit.Base")
import Ansys.UI.Toolkit


def beamDehomogenizationCanAddAtTree(currentAnalysis, load):
    if currentAnalysis.Children.Count == 2 and currentAnalysis.SolverName == 'SwiftCompDehom@SwiftComp':
        SGFileSystem = sg_filesystem.SGFileSystem(ExtAPI)
        SGResult = sg_result.SGResult()
        with open(SGFileSystem.user_dir + 'SGResult.pickle', 'rb') as f:
            SGResult = pickle.load(f)
        return SGResult.BeamModel
    return False


def beamDehomogenizationOnInitAtTree(load):
    SGFileSystem = sg_filesystem.SGFileSystem(ExtAPI)
    SGResult = sg_result.SGResult()
    with open(SGFileSystem.user_dir + 'SGResult.pickle', 'rb') as f:
        SGResult = pickle.load(f)
    if SGResult.BeamModel.submodel == 0:
        load.Properties["Macro Generalized StrainStress/Macro Model"].Value = "Euler-Bernoulli Beam Model"
    elif SGResult.BeamModel.submodel == 1:
        load.Properties["Macro Generalized StrainStress/Macro Model"].Value = "Timoshenko Beam Model"


def extractionNameBeamModelOnActivate(load, prop):
    # works for 19.2
    # from System.Collections.Generic import List
    # test = ["test3","test4"]
    # prop.Options = List[str](test)

    # For 19.2, get warning Obsolete method 'AddOption': Use the Options field instead.
    # prop.ClearOptions()
    # prop.AddOption("X")
    # prop.AddOption("Y")
    # prop.AddOption("Z")

    from System.Collections.Generic import List

    SGFileSystem = sg_filesystem.SGFileSystem(ExtAPI)

    user_dir_files = os.listdir(SGFileSystem.user_dir)

    SGStructuralResultList = sg_structural_result_list.SGStructuralResultList()

    if 'SGStructuralResultList.pickle' in user_dir_files:
        with open(SGFileSystem.user_dir + 'SGStructuralResultList.pickle', 'rb') as f:
            SGStructuralResultList = pickle.load(f)
       
        resulNameList = []
        for i in range(len(SGStructuralResultList.ResultList)):
            if SGStructuralResultList.ResultList[i].macro_model == 1:
                resulNameList.append(SGStructuralResultList.ResultList[i].name)

        prop.Options = List[str](resulNameList)

        extractionName = load.Properties["Information Source/Select/Extraction Name"].Value
        if extractionName:  # there is extraction name
            for i in range(len(SGStructuralResultList.ResultList)):
                if SGStructuralResultList.ResultList[i].name == extractionName:
                    dehom_func.updateBeamModelDehomogenizationSetting(load, SGStructuralResultList.ResultList[i])
                    return
        elif resulNameList:  # there is no extraction name and there is resulNameList
            load.Properties["Information Source/Select/Extraction Name"].Value = resulNameList[0]
            dehom_func.updateBeamModelDehomogenizationSetting(load, SGStructuralResultList.ResultList[0])
        else:  # there is no extraction name and there is no resulNameList
            load.Properties["Information Source/Select/Extraction Name"].Value = "No structural analysis results available"
    else: 
        load.Properties["Information Source/Select/Extraction Name"].Value = "No structural analysis results available"


def beamDehomogenizationAtTree(load, fct):

    v1 = load.Properties["Macro Displacements/v1"].Value
    v2 = load.Properties["Macro Displacements/v2"].Value
    v3 = load.Properties["Macro Displacements/v3"].Value
    macro_displacement = [v1, v2, v3]

    C11 = load.Properties["Macro Rotations/C11"].Value
    C12 = load.Properties["Macro Rotations/C12"].Value
    C13 = load.Properties["Macro Rotations/C13"].Value
    C21 = load.Properties["Macro Rotations/C21"].Value
    C22 = load.Properties["Macro Rotations/C22"].Value
    C23 = load.Properties["Macro Rotations/C23"].Value
    C31 = load.Properties["Macro Rotations/C31"].Value
    C32 = load.Properties["Macro Rotations/C32"].Value
    C33 = load.Properties["Macro Rotations/C33"].Value
    macro_rotation = [[C11, C12, C13], [C21, C22, C23], [C31, C32, C33]]

    if load.Properties["Macro Generalized StrainStress/Macro Model"].Value == "Euler-Bernoulli Beam Model":
        method = load.Properties["Macro Generalized StrainStress/Macro Model/Method1"].Value
        if method == 'Generalized Strain':
            e11 = load.Properties["Macro Generalized StrainStress/Macro Model/Method1/epsilon11"].Value
            k11 = load.Properties["Macro Generalized StrainStress/Macro Model/Method1/kappa11"].Value
            k12 = load.Properties["Macro Generalized StrainStress/Macro Model/Method1/kappa12"].Value
            k13 = load.Properties["Macro Generalized StrainStress/Macro Model/Method1/kappa13"].Value
            macro_strain_stress = [e11, k11, k12, k13]
        else:
            F1 = load.Properties["Macro Generalized StrainStress/Macro Model/Method1/F1"].Value
            M1 = load.Properties["Macro Generalized StrainStress/Macro Model/Method1/M1"].Value
            M2 = load.Properties["Macro Generalized StrainStress/Macro Model/Method1/M2"].Value
            M3 = load.Properties["Macro Generalized StrainStress/Macro Model/Method1/M3"].Value
            macro_strain_stress = [F1, M1, M2, M3]

    elif load.Properties["Macro Generalized StrainStress/Macro Model"].Value == "Timoshenko Beam Model":
        method = load.Properties["Macro Generalized StrainStress/Macro Model/Method2"].Value 
        if method == 'Generalized Strain':
            e11 = load.Properties["Macro Generalized StrainStress/Macro Model/Method2/epsilon11"].Value
            g12 = load.Properties["Macro Generalized StrainStress/Macro Model/Method2/gamma12"].Value
            g13 = load.Properties["Macro Generalized StrainStress/Macro Model/Method2/gamma13"].Value
            k11 = load.Properties["Macro Generalized StrainStress/Macro Model/Method2/kappa11"].Value
            k12 = load.Properties["Macro Generalized StrainStress/Macro Model/Method2/kappa12"].Value
            k13 = load.Properties["Macro Generalized StrainStress/Macro Model/Method2/kappa13"].Value
            macro_strain_stress = [e11, g12, g13, k11, k12, k13]
        else:
            F1 = load.Properties["Macro Generalized StrainStress/Macro Model/Method2/F1"].Value
            F2 = load.Properties["Macro Generalized StrainStress/Macro Model/Method2/F2"].Value
            F3 = load.Properties["Macro Generalized StrainStress/Macro Model/Method2/F3"].Value
            M1 = load.Properties["Macro Generalized StrainStress/Macro Model/Method2/M1"].Value
            M2 = load.Properties["Macro Generalized StrainStress/Macro Model/Method2/M2"].Value
            M3 = load.Properties["Macro Generalized StrainStress/Macro Model/Method2/M3"].Value
            macro_strain_stress = [F1, F2, F3, M1, M2, M3]

    parameters = [ExtAPI, macro_displacement, macro_rotation, method, macro_strain_stress]

    return ExtAPI.Application.InvokeUIThread(dehom_func.SwiftCompDehomogenizationInput, parameters)


def plateDehomogenizationCanAddAtTree(currentAnalysis, load):
    if currentAnalysis.Children.Count == 2 and currentAnalysis.SolverName == 'SwiftCompDehom@SwiftComp':
        SGFileSystem = sg_filesystem.SGFileSystem(ExtAPI)
        SGResult = sg_result.SGResult()
        with open(SGFileSystem.user_dir + 'SGResult.pickle', 'rb') as f:
            SGResult = pickle.load(f)
        return SGResult.PlateModel
    return False


def plateDehomogenizationOnInitAtTree(load):
    SGFileSystem = sg_filesystem.SGFileSystem(ExtAPI)
    SGResult = sg_result.SGResult()
    with open(SGFileSystem.user_dir + 'SGResult.pickle', 'rb') as f:
        SGResult = pickle.load(f)
    if SGResult.PlateModel.submodel == 0:
        load.Properties["Macro Generalized StrainStress/Macro Model"].Value = "Kirchhoff-Love Model"
    elif SGResult.PlateModel.submodel == 1:
        load.Properties["Macro Generalized StrainStress/Macro Model"].Value = "Reissner-Mindlin Model"


def extractionNamePlateModelOnActivate(load, prop):
    # works for 19.2
    # from System.Collections.Generic import List
    # test = ["test3","test4"]
    # prop.Options = List[str](test)

    # For 19.2, get warning Obsolete method 'AddOption': Use the Options field instead.
    # prop.ClearOptions()
    # prop.AddOption("X")
    # prop.AddOption("Y")
    # prop.AddOption("Z")

    from System.Collections.Generic import List

    SGFileSystem = sg_filesystem.SGFileSystem(ExtAPI)

    user_dir_files = os.listdir(SGFileSystem.user_dir)

    SGStructuralResultList = sg_structural_result_list.SGStructuralResultList()

    if 'SGStructuralResultList.pickle' in user_dir_files:
        with open(SGFileSystem.user_dir + 'SGStructuralResultList.pickle', 'rb') as f:
            SGStructuralResultList = pickle.load(f)
       
        resulNameList = []
        for i in range(len(SGStructuralResultList.ResultList)):
            if SGStructuralResultList.ResultList[i].macro_model == 2:
                resulNameList.append(SGStructuralResultList.ResultList[i].name)

        prop.Options = List[str](resulNameList)

        extractionName = load.Properties["Information Source/Select/Extraction Name"].Value
        if extractionName:  # there is extraction name
            for i in range(len(SGStructuralResultList.ResultList)):
                if SGStructuralResultList.ResultList[i].name == extractionName:
                    dehom_func.updatePlateModelDehomogenizationSetting(load, SGStructuralResultList.ResultList[i])
                    return
        elif resulNameList:  # there is no extraction name and there is resulNameList
            load.Properties["Information Source/Select/Extraction Name"].Value = resulNameList[0]
            dehom_func.updatePlateModelDehomogenizationSetting(load, SGStructuralResultList.ResultList[0])
        else:  # there is no extraction name and there is no resulNameList
            load.Properties["Information Source/Select/Extraction Name"].Value = "No structural analysis results available"
    else: 
        load.Properties["Information Source/Select/Extraction Name"].Value = "No structural analysis results available"


def plateDehomogenizationAtTree(load, fct):

    v1 = load.Properties["Macro Displacements/v1"].Value
    v2 = load.Properties["Macro Displacements/v2"].Value
    v3 = load.Properties["Macro Displacements/v3"].Value
    macro_displacement = [v1, v2, v3]

    C11 = load.Properties["Macro Rotations/C11"].Value
    C12 = load.Properties["Macro Rotations/C12"].Value
    C13 = load.Properties["Macro Rotations/C13"].Value
    C21 = load.Properties["Macro Rotations/C21"].Value
    C22 = load.Properties["Macro Rotations/C22"].Value
    C23 = load.Properties["Macro Rotations/C23"].Value
    C31 = load.Properties["Macro Rotations/C31"].Value
    C32 = load.Properties["Macro Rotations/C32"].Value
    C33 = load.Properties["Macro Rotations/C33"].Value
    macro_rotation = [[C11, C12, C13], [C21, C22, C23], [C31, C32, C33]]


    if load.Properties["Macro Generalized StrainStress/Macro Model"].Value == "Kirchhoff-Love Model":
        method = load.Properties["Macro Generalized StrainStress/Macro Model/Method1"].Value
        if method == 'Generalized Strain':
            e11 = load.Properties["Macro Generalized StrainStress/Macro Model/Method1/epsilon11"].Value
            e22 = load.Properties["Macro Generalized StrainStress/Macro Model/Method1/epsilon22"].Value
            e12 = load.Properties["Macro Generalized StrainStress/Macro Model/Method1/2epsilon12"].Value
            k11 = load.Properties["Macro Generalized StrainStress/Macro Model/Method1/kappa11"].Value
            k22 = load.Properties["Macro Generalized StrainStress/Macro Model/Method1/kappa22"].Value
            k12 = load.Properties["Macro Generalized StrainStress/Macro Model/Method1/2kappa12"].Value
            macro_strain_stress = [e11, e22, e12, k11, k22, k12]
        else:
            N11 = load.Properties["Macro Generalized StrainStress/Macro Model/Method1/N11"].Value
            N22 = load.Properties["Macro Generalized StrainStress/Macro Model/Method1/N22"].Value
            N12 = load.Properties["Macro Generalized StrainStress/Macro Model/Method1/N12"].Value
            M11 = load.Properties["Macro Generalized StrainStress/Macro Model/Method1/M11"].Value
            M22 = load.Properties["Macro Generalized StrainStress/Macro Model/Method1/M22"].Value
            M12 = load.Properties["Macro Generalized StrainStress/Macro Model/Method1/M12"].Value
            macro_strain_stress = [N11, N22, N12, M11, M22, M12]

    elif load.Properties["Macro Generalized StrainStress/Macro Model"].Value == "Reissner-Mindlin Model":
        method = load.Properties["Macro Generalized StrainStress/Macro Model/Method2"].Value 
        if method == 'Generalized Strain':
            e11 = load.Properties["Macro Generalized StrainStress/Macro Model/Method2/epsilon11"].Value
            e22 = load.Properties["Macro Generalized StrainStress/Macro Model/Method2/epsilon22"].Value
            e12 = load.Properties["Macro Generalized StrainStress/Macro Model/Method2/2epsilon12"].Value
            k11 = load.Properties["Macro Generalized StrainStress/Macro Model/Method2/kappa11"].Value
            k22 = load.Properties["Macro Generalized StrainStress/Macro Model/Method2/kappa22"].Value
            k12 = load.Properties["Macro Generalized StrainStress/Macro Model/Method2/2kappa12"].Value
            g13 = load.Properties["Macro Generalized StrainStress/Macro Model/Method2/gamma13"].Value
            g23 = load.Properties["Macro Generalized StrainStress/Macro Model/Method2/gamma23"].Value
            macro_strain_stress = [e11, e22, e12, k11, k22, k12, g13, g23]
        else:
            N11 = load.Properties["Macro Generalized StrainStress/Macro Model/Method2/N11"].Value
            N22 = load.Properties["Macro Generalized StrainStress/Macro Model/Method2/N22"].Value
            N12 = load.Properties["Macro Generalized StrainStress/Macro Model/Method2/N12"].Value
            M11 = load.Properties["Macro Generalized StrainStress/Macro Model/Method2/M11"].Value
            M22 = load.Properties["Macro Generalized StrainStress/Macro Model/Method2/M22"].Value
            M12 = load.Properties["Macro Generalized StrainStress/Macro Model/Method2/M12"].Value
            N13 = load.Properties["Macro Generalized StrainStress/Macro Model/Method2/N13"].Value
            N23 = load.Properties["Macro Generalized StrainStress/Macro Model/Method2/N23"].Value
            macro_strain_stress = [N11, N22, N12, M11, M22, M12, N13, N23]

    parameters = [ExtAPI, macro_displacement, macro_rotation, method, macro_strain_stress]

    return ExtAPI.Application.InvokeUIThread(dehom_func.SwiftCompDehomogenizationInput, parameters)




def solidDehomogenizationCanAddAtTree(currentAnalysis, load):
    if currentAnalysis.Children.Count == 2 and currentAnalysis.SolverName == 'SwiftCompDehom@SwiftComp':
        SGFileSystem = sg_filesystem.SGFileSystem(ExtAPI)
        SGResult = sg_result.SGResult()
        with open(SGFileSystem.user_dir + 'SGResult.pickle', 'rb') as f:
            SGResult = pickle.load(f)
        return SGResult.SolidModel
    return False

def extractionNameSolidModelOnActivate(load, prop):
    # works for 19.2
    # from System.Collections.Generic import List
    # test = ["test3","test4"]
    # prop.Options = List[str](test)

    # For 19.2, get warning Obsolete method 'AddOption': Use the Options field instead.
    # prop.ClearOptions()
    # prop.AddOption("X")
    # prop.AddOption("Y")
    # prop.AddOption("Z")

    from System.Collections.Generic import List

    SGFileSystem = sg_filesystem.SGFileSystem(ExtAPI)

    user_dir_files = os.listdir(SGFileSystem.user_dir)

    SGStructuralResultList = sg_structural_result_list.SGStructuralResultList()

    if 'SGStructuralResultList.pickle' in user_dir_files:
        with open(SGFileSystem.user_dir + 'SGStructuralResultList.pickle', 'rb') as f:
            SGStructuralResultList = pickle.load(f)
       
        resulNameList = []
        for i in range(len(SGStructuralResultList.ResultList)):
            if SGStructuralResultList.ResultList[i].macro_model == 3:
                resulNameList.append(SGStructuralResultList.ResultList[i].name)

        prop.Options = List[str](resulNameList)

        extractionName = load.Properties["Information Source/Select/Extraction Name"].Value
        if extractionName:  # there is extraction name
            for i in range(len(SGStructuralResultList.ResultList)):
                if SGStructuralResultList.ResultList[i].name == extractionName:
                    dehom_func.updateSolidModelDehomogenizationSetting(load, SGStructuralResultList.ResultList[i])
                    return
        elif resulNameList:  # there is no extraction name and there is resulNameList
            load.Properties["Information Source/Select/Extraction Name"].Value = resulNameList[0]
            dehom_func.updateSolidModelDehomogenizationSetting(load, SGStructuralResultList.ResultList[0])
        else:  # there is no extraction name and there is no resulNameList
            load.Properties["Information Source/Select/Extraction Name"].Value = "No structural analysis results available"
    else: 
        load.Properties["Information Source/Select/Extraction Name"].Value = "No structural analysis results available"


def solidDehomogenizationAtTree(load, fct):

    v1 = load.Properties["Macro Displacements/v1"].Value
    v2 = load.Properties["Macro Displacements/v2"].Value
    v3 = load.Properties["Macro Displacements/v3"].Value
    macro_displacement = [v1, v2, v3]

    C11 = load.Properties["Macro Rotations/C11"].Value
    C12 = load.Properties["Macro Rotations/C12"].Value
    C13 = load.Properties["Macro Rotations/C13"].Value
    C21 = load.Properties["Macro Rotations/C21"].Value
    C22 = load.Properties["Macro Rotations/C22"].Value
    C23 = load.Properties["Macro Rotations/C23"].Value
    C31 = load.Properties["Macro Rotations/C31"].Value
    C32 = load.Properties["Macro Rotations/C32"].Value
    C33 = load.Properties["Macro Rotations/C33"].Value
    macro_rotation = [[C11, C12, C13], [C21, C22, C23], [C31, C32, C33]]

    method = load.Properties["Macro Generalized StrainStress/Method"].Value 
    if method == 'Generalized Strain':
        e11 = load.Properties["Macro Generalized StrainStress/Method/epsilon11"].Value
        e22 = load.Properties["Macro Generalized StrainStress/Method/epsilon22"].Value
        e33 = load.Properties["Macro Generalized StrainStress/Method/epsilon33"].Value
        e23 = load.Properties["Macro Generalized StrainStress/Method/2epsilon23"].Value
        e13 = load.Properties["Macro Generalized StrainStress/Method/2epsilon13"].Value
        e12 = load.Properties["Macro Generalized StrainStress/Method/2epsilon12"].Value
        macro_strain_stress = [e11, e22, e33, e23, e13, e12]
    else:
        s11 = load.Properties["Macro Generalized StrainStress/Method/sigma11"].Value
        s22 = load.Properties["Macro Generalized StrainStress/Method/sigma22"].Value
        s33 = load.Properties["Macro Generalized StrainStress/Method/sigma33"].Value
        s23 = load.Properties["Macro Generalized StrainStress/Method/sigma23"].Value
        s13 = load.Properties["Macro Generalized StrainStress/Method/sigma13"].Value
        s12 = load.Properties["Macro Generalized StrainStress/Method/sigma12"].Value
        macro_strain_stress = [s11, s22, s33, s23, s13, s12]

    parameters = [ExtAPI, macro_displacement, macro_rotation, method, macro_strain_stress]

    return ExtAPI.Application.InvokeUIThread(dehom_func.SwiftCompDehomogenizationInput, parameters)



def SwiftCompDehom(s, fct):
    '''SwiftComp solve'''
    return ExtAPI.Application.InvokeUIThread(dehom_func.SwiftCompDehomogenizationRun, ExtAPI)


def GetReader(solver):
    SGFileSystem = sg_filesystem.SGFileSystem(ExtAPI)
    SG = sg.StructureGenome()
    with open(SGFileSystem.user_dir + 'SG.pickle', 'rb') as f:
        SG = pickle.load(f)
    if SG.nSG != 1:
        return ["SwiftCompDehomSolverReader"]
    else:
        return None


class SwiftCompDehomSolverReader(Ansys.ACT.Interfaces.Post.ICustomResultReader):
    def __init__(self, infos):
        steps = 1
        self.infos = infos

    def GetResultNames(self):
        return ["U", "S", "EPEL"]

    def GetResultLocation(self, resultName):
        if resultName == "U":
            return ResultLocationEnum.Node
        elif resultName == "S" or resultName == "EPEL":
            return ResultLocationEnum.ElementNode
        else:
            return ResultLocationEnum.Element

    def GetResultType(self, resultName):
        if resultName == "U":
            return ResultTypeEnum.Vector
        elif resultName == "S" or resultName == "EPEL":
            return ResultTypeEnum.Tensor
        else:
            return ResultTypeEnum.Scalar

    def GetComponentNames(self, resultName):
        if resultName == "U":
            return ["X", "Y", "Z"]
        elif resultName == "S" or resultName == "EPEL":
            return ["X", "Y", "Z", "XY", "YZ", "XZ"]
        else:
            return ["value"]

    def GetComponentUnit(self, resultName, componentName):
        if resultName == "U":
            return "Length"
        elif resultName == "S":
            return "Stress"
        elif resultName == "EPEL":
            return "Strain"
        else:
            return "value unit"

    def GetValues(self, resultName, collector):
        arguments = [ExtAPI, resultName, collector]

        return ExtAPI.Application.InvokeUIThread(GetValueTrue, arguments)


def GetValueTrue(arg):
    ExtAPI, resultName, collector = arg[0], arg[1],  arg[2]

    SGFileSystem = sg_filesystem.SGFileSystem(ExtAPI)

    SGResult = sg_result.SGResult()
    with open(SGFileSystem.user_dir + 'SGResult.pickle', 'rb') as f:
        SGResult = pickle.load(f)

    try:
        # Displayment
        if resultName == "U":
            for node in collector.Ids:
                collector.SetValues(node, SGResult.Displacement.Node[node-1].displacement)

        # Stress
        elif resultName == "S":
            for element in collector.Ids:
                collector.SetValues(element, SGResult.Stress.Element[element-1].stress_corner)

        # Strain
        elif resultName == "EPEL":
            for element in collector.Ids:
                collector.SetValues(element, SGResult.Strain.Element[element-1].strain_corner)
    except:
        return False

    return True
