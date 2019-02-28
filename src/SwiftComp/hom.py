import hom_func

import sg_result
import sg_filesystem


def beamHomogenizationCanAddAtTree(currentAnalysis, load):
    return currentAnalysis.Children.Count == 2 and currentAnalysis.SolverName == 'SwiftCompHom@SwiftComp'


def beamHomogenizationOnInitAtTree(load):
    SGFileSystem = sg_filesystem.SGFileSystem(ExtAPI)
    load.Properties["Homogenization Result Name/Name"].Value = 'Beam_Model_' + SGFileSystem.file_name


def beamHomogenizationAtTree(load, fct):
    macro_model = "Beam Model"

    result_name = load.Properties["Homogenization Result Name/Name"].Value

    submodel = load.Properties["Submodel/Type of Beam Model"].Value

    k11 = load.Properties["Beam Initial Curvature/k11"].Value
    k12 = load.Properties["Beam Initial Curvature/k12"].Value
    k13 = load.Properties["Beam Initial Curvature/k13"].Value

    cos_y1x1 = load.Properties["Beam Obliqueness/cos(y1,x1)"].Value
    cos_y2x1 = load.Properties["Beam Obliqueness/cos(y2,x1)"].Value

    analysis = load.Properties["Problem Control Parameters/Analysis Type"].Value
    elem_flag = load.Properties["Problem Control Parameters/Element Type"].Value
    trans_flag = load.Properties["Problem Control Parameters/Element Orientation"].Value

    if analysis in ['Elastic', 'Conduction', 'Piezoelectric/Piezomagnetic', 'Piezoeletromagnetic']:
        temp_flag = load.Properties["Problem Control Parameters/Analysis Type/Temperature Distribution Uniform"].Value
    else:
        temp_flag = load.Properties["Problem Control Parameters/Analysis Type/Temperature Distribution"].Value

    py1 = load.Properties["Aperiodic Control Parameters/Aperiodic Along y1"].Value

    arguments = [[ExtAPI, fct], result_name, macro_model, submodel, [k11, k12, k13], [cos_y1x1, cos_y2x1], 
                 [analysis, elem_flag, trans_flag, temp_flag], [py1]]

    return ExtAPI.Application.InvokeUIThread(hom_func.SwiftCompHomogenizationInput, arguments)


def plateHomogenizationCanAddAtTree(currentAnalysis, load):
    return currentAnalysis.Children.Count == 2 and currentAnalysis.SolverName == 'SwiftCompHom@SwiftComp'


def plateHomogenizationOnInitAtTree(load):
    SGFileSystem = sg_filesystem.SGFileSystem(ExtAPI)
    load.Properties["Homogenization Result Name/Name"].Value = 'Plate_Model_' + SGFileSystem.file_name


def plateHomogenizationAtTree(load, fct):
    macro_model = "Plate Model"

    result_name = load.Properties["Homogenization Result Name/Name"].Value

    submodel = load.Properties["Submodel/Type of Plate Model"].Value

    k12 = load.Properties["Plate Initial Curvature/k12"].Value
    k21 = load.Properties["Plate Initial Curvature/k21"].Value

    analysis = load.Properties["Problem Control Parameters/Analysis Type"].Value
    elem_flag = load.Properties["Problem Control Parameters/Element Type"].Value
    trans_flag = load.Properties["Problem Control Parameters/Element Orientation"].Value

    if analysis in ['Elastic', 'Conduction', 'Piezoelectric/Piezomagnetic', 'Piezoeletromagnetic']:
        temp_flag = load.Properties["Problem Control Parameters/Analysis Type/Temperature Distribution Uniform"].Value
    else:
        temp_flag = load.Properties["Problem Control Parameters/Analysis Type/Temperature Distribution"].Value

    py1 = load.Properties["Aperiodic Control Parameters/Aperiodic Along y1"].Value
    py2 = load.Properties["Aperiodic Control Parameters/Aperiodic Along y2"].Value

    arguments = [[ExtAPI, fct], result_name, macro_model, submodel, [k12, k21],
                 [analysis, elem_flag, trans_flag, temp_flag], [py1, py2]]

    return ExtAPI.Application.InvokeUIThread(hom_func.SwiftCompHomogenizationInput, arguments)


def solidHomogenizationCanAddAtTree(currentAnalysis, load):
    return currentAnalysis.Children.Count == 2 and currentAnalysis.SolverName == 'SwiftCompHom@SwiftComp'


def solidHomogenizationOnInitAtTree(load):
    SGFileSystem = sg_filesystem.SGFileSystem(ExtAPI)
    load.Properties["Homogenization Result Name/Name"].Value = 'Solid_Model_' + SGFileSystem.file_name


def solidHomogenizationAtTree(load, fct):
    macro_model = "Solid Model"

    result_name = load.Properties["Homogenization Result Name/Name"].Value

    analysis = load.Properties["Problem Control Parameters/Analysis Type"].Value
    elem_flag = load.Properties["Problem Control Parameters/Element Type"].Value
    trans_flag = load.Properties["Problem Control Parameters/Element Orientation"].Value

    if analysis in ['Elastic', 'Conduction', 'Piezoelectric/Piezomagnetic', 'Piezoeletromagnetic']:
        temp_flag = load.Properties["Problem Control Parameters/Analysis Type/Temperature Distribution Uniform"].Value
    else:
        temp_flag = load.Properties["Problem Control Parameters/Analysis Type/Temperature Distribution"].Value

    py1 = load.Properties["Aperiodic Control Parameters/Aperiodic Along y1"].Value
    py2 = load.Properties["Aperiodic Control Parameters/Aperiodic Along y2"].Value
    py3 = load.Properties["Aperiodic Control Parameters/Aperiodic Along y3"].Value

    arguments = [[ExtAPI, fct], result_name, macro_model,
                 [analysis, elem_flag, trans_flag, temp_flag], [py1, py2, py3]]

    return ExtAPI.Application.InvokeUIThread(hom_func.SwiftCompHomogenizationInput, arguments)


def HomogenizationSettingOnRemovetAtTree(load):
    '''when homogenization is on remove at tree'''

    result_name = load.Properties["Homogenization Result Name/Name"].Value

    arguments = [ExtAPI, result_name]

    ExtAPI.Application.InvokeUIThread(hom_func.updateSGHomogenizationResultListObjectWhenRemove, arguments)


def SwiftCompHom(s, fct):
    arguments = [ExtAPI,fct]
    return ExtAPI.Application.InvokeUIThread(hom_func.SwiftCompHomogenizationRun, arguments)


def homogenizationResultCanAddAtTree(currentAnalysis, extraction):
    return currentAnalysis.SolverName == 'SwiftCompHom@SwiftComp'


def homogenizationResultAtTree(result, fct):

    SGResult = sg_result.SGResult()

    SGResult = ExtAPI.Application.InvokeUIThread(hom_func.homogenizationResult, ExtAPI)

    result.Properties["Calculation Information/Homogenization Time"].Value = SGResult.homTime

    result.Properties["BeamStiffness"].Value = False
    result.Properties["BeamCompliance"].Value = False
    result.Properties["BeamTimoshenkoStiffness"].Value = False
    result.Properties["BeamTimoshenkoCompliance"].Value = False
    result.Properties["BeamShearCenter"].Value = False
    result.Properties["PlateStiffness"].Value = False
    result.Properties["PlateCompliance"].Value = False
    result.Properties["PlateInPlane"].Value = False
    result.Properties["PlateFlexural"].Value = False
    result.Properties["SolidStiffness"].Value = False
    result.Properties["SolidCompliance"].Value = False
    result.Properties["EngineeringConstant"].Value = False

    if SGResult.BeamModel:
        result.Properties["Model Information/Macro Model"].Value = "Beam Model"
        if SGResult.BeamModel.submodel == 0:
            result.Properties["BeamStiffness"].Value = True
            result.Properties["BeamStiffness/C11"].Value = SGResult.BeamModel.stiffness[0][0]
            result.Properties["BeamStiffness/C12"].Value = SGResult.BeamModel.stiffness[0][1]
            result.Properties["BeamStiffness/C13"].Value = SGResult.BeamModel.stiffness[0][2]
            result.Properties["BeamStiffness/C14"].Value = SGResult.BeamModel.stiffness[0][3]
            result.Properties["BeamStiffness/C22"].Value = SGResult.BeamModel.stiffness[1][1]
            result.Properties["BeamStiffness/C23"].Value = SGResult.BeamModel.stiffness[1][2]
            result.Properties["BeamStiffness/C24"].Value = SGResult.BeamModel.stiffness[1][3]
            result.Properties["BeamStiffness/C33"].Value = SGResult.BeamModel.stiffness[2][2]
            result.Properties["BeamStiffness/C34"].Value = SGResult.BeamModel.stiffness[2][3]
            result.Properties["BeamStiffness/C44"].Value = SGResult.BeamModel.stiffness[3][3]
            result.Properties["BeamCompliance"].Value = True
            result.Properties["BeamCompliance/S11"].Value = SGResult.BeamModel.compliance[0][0]
            result.Properties["BeamCompliance/S12"].Value = SGResult.BeamModel.compliance[0][1]
            result.Properties["BeamCompliance/S13"].Value = SGResult.BeamModel.compliance[0][2]
            result.Properties["BeamCompliance/S14"].Value = SGResult.BeamModel.compliance[0][3]
            result.Properties["BeamCompliance/S22"].Value = SGResult.BeamModel.compliance[1][1]
            result.Properties["BeamCompliance/S23"].Value = SGResult.BeamModel.compliance[1][2]
            result.Properties["BeamCompliance/S24"].Value = SGResult.BeamModel.compliance[1][3]
            result.Properties["BeamCompliance/S33"].Value = SGResult.BeamModel.compliance[2][2]
            result.Properties["BeamCompliance/S34"].Value = SGResult.BeamModel.compliance[2][3]
            result.Properties["BeamCompliance/S44"].Value = SGResult.BeamModel.compliance[3][3]
        elif SGResult.BeamModel.submodel == 1:
            result.Properties["BeamTimoshenkoStiffness"].Value = True
            result.Properties["BeamTimoshenkoStiffness/C11"].Value = SGResult.BeamModel.TimoshenkoStiffness[0][0]
            result.Properties["BeamTimoshenkoStiffness/C12"].Value = SGResult.BeamModel.TimoshenkoStiffness[0][1]
            result.Properties["BeamTimoshenkoStiffness/C13"].Value = SGResult.BeamModel.TimoshenkoStiffness[0][2]
            result.Properties["BeamTimoshenkoStiffness/C14"].Value = SGResult.BeamModel.TimoshenkoStiffness[0][3]
            result.Properties["BeamTimoshenkoStiffness/C15"].Value = SGResult.BeamModel.TimoshenkoStiffness[0][4]
            result.Properties["BeamTimoshenkoStiffness/C16"].Value = SGResult.BeamModel.TimoshenkoStiffness[0][5]
            result.Properties["BeamTimoshenkoStiffness/C22"].Value = SGResult.BeamModel.TimoshenkoStiffness[1][1]
            result.Properties["BeamTimoshenkoStiffness/C23"].Value = SGResult.BeamModel.TimoshenkoStiffness[1][2]
            result.Properties["BeamTimoshenkoStiffness/C24"].Value = SGResult.BeamModel.TimoshenkoStiffness[1][3]
            result.Properties["BeamTimoshenkoStiffness/C25"].Value = SGResult.BeamModel.TimoshenkoStiffness[1][4]
            result.Properties["BeamTimoshenkoStiffness/C26"].Value = SGResult.BeamModel.TimoshenkoStiffness[1][5]
            result.Properties["BeamTimoshenkoStiffness/C33"].Value = SGResult.BeamModel.TimoshenkoStiffness[2][2]
            result.Properties["BeamTimoshenkoStiffness/C34"].Value = SGResult.BeamModel.TimoshenkoStiffness[2][3]
            result.Properties["BeamTimoshenkoStiffness/C35"].Value = SGResult.BeamModel.TimoshenkoStiffness[2][4]
            result.Properties["BeamTimoshenkoStiffness/C36"].Value = SGResult.BeamModel.TimoshenkoStiffness[2][5]
            result.Properties["BeamTimoshenkoStiffness/C44"].Value = SGResult.BeamModel.TimoshenkoStiffness[3][3]
            result.Properties["BeamTimoshenkoStiffness/C45"].Value = SGResult.BeamModel.TimoshenkoStiffness[3][4]
            result.Properties["BeamTimoshenkoStiffness/C46"].Value = SGResult.BeamModel.TimoshenkoStiffness[3][5]
            result.Properties["BeamTimoshenkoStiffness/C55"].Value = SGResult.BeamModel.TimoshenkoStiffness[4][4]
            result.Properties["BeamTimoshenkoStiffness/C56"].Value = SGResult.BeamModel.TimoshenkoStiffness[4][5]
            result.Properties["BeamTimoshenkoStiffness/C66"].Value = SGResult.BeamModel.TimoshenkoStiffness[5][5]
            result.Properties["BeamTimoshenkoCompliance"].Value = True
            result.Properties["BeamTimoshenkoCompliance/S11"].Value = SGResult.BeamModel.TimoshenkoCompliance[0][0]
            result.Properties["BeamTimoshenkoCompliance/S12"].Value = SGResult.BeamModel.TimoshenkoCompliance[0][1]
            result.Properties["BeamTimoshenkoCompliance/S13"].Value = SGResult.BeamModel.TimoshenkoCompliance[0][2]
            result.Properties["BeamTimoshenkoCompliance/S14"].Value = SGResult.BeamModel.TimoshenkoCompliance[0][3]
            result.Properties["BeamTimoshenkoCompliance/S15"].Value = SGResult.BeamModel.TimoshenkoCompliance[0][4]
            result.Properties["BeamTimoshenkoCompliance/S16"].Value = SGResult.BeamModel.TimoshenkoCompliance[0][5]
            result.Properties["BeamTimoshenkoCompliance/S22"].Value = SGResult.BeamModel.TimoshenkoCompliance[1][1]
            result.Properties["BeamTimoshenkoCompliance/S23"].Value = SGResult.BeamModel.TimoshenkoCompliance[1][2]
            result.Properties["BeamTimoshenkoCompliance/S24"].Value = SGResult.BeamModel.TimoshenkoCompliance[1][3]
            result.Properties["BeamTimoshenkoCompliance/S25"].Value = SGResult.BeamModel.TimoshenkoCompliance[1][4]
            result.Properties["BeamTimoshenkoCompliance/S26"].Value = SGResult.BeamModel.TimoshenkoCompliance[1][5]
            result.Properties["BeamTimoshenkoCompliance/S33"].Value = SGResult.BeamModel.TimoshenkoCompliance[2][2]
            result.Properties["BeamTimoshenkoCompliance/S34"].Value = SGResult.BeamModel.TimoshenkoCompliance[2][3]
            result.Properties["BeamTimoshenkoCompliance/S35"].Value = SGResult.BeamModel.TimoshenkoCompliance[2][4]
            result.Properties["BeamTimoshenkoCompliance/S36"].Value = SGResult.BeamModel.TimoshenkoCompliance[2][5]
            result.Properties["BeamTimoshenkoCompliance/S44"].Value = SGResult.BeamModel.TimoshenkoCompliance[3][3]
            result.Properties["BeamTimoshenkoCompliance/S45"].Value = SGResult.BeamModel.TimoshenkoCompliance[3][4]
            result.Properties["BeamTimoshenkoCompliance/S46"].Value = SGResult.BeamModel.TimoshenkoCompliance[3][5]
            result.Properties["BeamTimoshenkoCompliance/S55"].Value = SGResult.BeamModel.TimoshenkoCompliance[4][4]
            result.Properties["BeamTimoshenkoCompliance/S56"].Value = SGResult.BeamModel.TimoshenkoCompliance[4][5]
            result.Properties["BeamTimoshenkoCompliance/S66"].Value = SGResult.BeamModel.TimoshenkoCompliance[5][5]
            result.Properties["BeamShearCenter"].Value = True
            result.Properties["BeamShearCenter/y1"].Value = SGResult.BeamModel.shearCenter[0]
            result.Properties["BeamShearCenter/y2"].Value = SGResult.BeamModel.shearCenter[1]

    elif SGResult.PlateModel:
        result.Properties["Model Information/Macro Model"].Value = "Plate/Shell Model"
        if SGResult.PlateModel.submodel == 0:
            result.Properties["PlateStiffness"].Value = True
            result.Properties["PlateStiffness/A11"].Value = SGResult.PlateModel.stiffness[0][0]
            result.Properties["PlateStiffness/A12"].Value = SGResult.PlateModel.stiffness[0][1]
            result.Properties["PlateStiffness/A16"].Value = SGResult.PlateModel.stiffness[0][2]
            result.Properties["PlateStiffness/A22"].Value = SGResult.PlateModel.stiffness[1][1]
            result.Properties["PlateStiffness/A26"].Value = SGResult.PlateModel.stiffness[1][2]
            result.Properties["PlateStiffness/A66"].Value = SGResult.PlateModel.stiffness[2][2]
            result.Properties["PlateStiffness/B11"].Value = SGResult.PlateModel.stiffness[0][3]
            result.Properties["PlateStiffness/B12"].Value = SGResult.PlateModel.stiffness[0][4]
            result.Properties["PlateStiffness/B16"].Value = SGResult.PlateModel.stiffness[0][5]
            result.Properties["PlateStiffness/B22"].Value = SGResult.PlateModel.stiffness[1][4]
            result.Properties["PlateStiffness/B26"].Value = SGResult.PlateModel.stiffness[1][5]
            result.Properties["PlateStiffness/B66"].Value = SGResult.PlateModel.stiffness[2][5]
            result.Properties["PlateStiffness/D11"].Value = SGResult.PlateModel.stiffness[3][3]
            result.Properties["PlateStiffness/D12"].Value = SGResult.PlateModel.stiffness[3][4]
            result.Properties["PlateStiffness/D16"].Value = SGResult.PlateModel.stiffness[3][5]
            result.Properties["PlateStiffness/D22"].Value = SGResult.PlateModel.stiffness[4][4]
            result.Properties["PlateStiffness/D26"].Value = SGResult.PlateModel.stiffness[4][5]
            result.Properties["PlateStiffness/D66"].Value = SGResult.PlateModel.stiffness[5][5]
            result.Properties["PlateCompliance"].Value = True
            result.Properties["PlateCompliance/S11"].Value = SGResult.PlateModel.compliance[0][0]
            result.Properties["PlateCompliance/S12"].Value = SGResult.PlateModel.compliance[0][1]
            result.Properties["PlateCompliance/S13"].Value = SGResult.PlateModel.compliance[0][2]
            result.Properties["PlateCompliance/S14"].Value = SGResult.PlateModel.compliance[0][3]
            result.Properties["PlateCompliance/S15"].Value = SGResult.PlateModel.compliance[0][4]
            result.Properties["PlateCompliance/S16"].Value = SGResult.PlateModel.compliance[0][5]
            result.Properties["PlateCompliance/S22"].Value = SGResult.PlateModel.compliance[1][1]
            result.Properties["PlateCompliance/S23"].Value = SGResult.PlateModel.compliance[1][2]
            result.Properties["PlateCompliance/S24"].Value = SGResult.PlateModel.compliance[1][3]
            result.Properties["PlateCompliance/S25"].Value = SGResult.PlateModel.compliance[1][4]
            result.Properties["PlateCompliance/S26"].Value = SGResult.PlateModel.compliance[1][5]
            result.Properties["PlateCompliance/S33"].Value = SGResult.PlateModel.compliance[2][2]
            result.Properties["PlateCompliance/S34"].Value = SGResult.PlateModel.compliance[2][3]
            result.Properties["PlateCompliance/S35"].Value = SGResult.PlateModel.compliance[2][4]
            result.Properties["PlateCompliance/S36"].Value = SGResult.PlateModel.compliance[2][5]
            result.Properties["PlateCompliance/S44"].Value = SGResult.PlateModel.compliance[3][3]
            result.Properties["PlateCompliance/S45"].Value = SGResult.PlateModel.compliance[3][4]
            result.Properties["PlateCompliance/S46"].Value = SGResult.PlateModel.compliance[3][5]
            result.Properties["PlateCompliance/S55"].Value = SGResult.PlateModel.compliance[4][4]
            result.Properties["PlateCompliance/S56"].Value = SGResult.PlateModel.compliance[4][5]
            result.Properties["PlateCompliance/S66"].Value = SGResult.PlateModel.compliance[5][5]
        elif SGResult.PlateModel.submodel == 1:
            pass
        if SGResult.PlateModel.inPlane:
            result.Properties["PlateInPlane"].Value = True
            result.Properties["PlateInPlane/E1"].Value     = SGResult.PlateModel.inPlane['E1']    
            result.Properties["PlateInPlane/E2"].Value     = SGResult.PlateModel.inPlane['E2']    
            result.Properties["PlateInPlane/G12"].Value    = SGResult.PlateModel.inPlane['G12']   
            result.Properties["PlateInPlane/nu12"].Value   = SGResult.PlateModel.inPlane['nu12']  
            result.Properties["PlateInPlane/eta121"].Value = SGResult.PlateModel.inPlane['eta121']
            result.Properties["PlateInPlane/eta122"].Value = SGResult.PlateModel.inPlane['eta122']
        if SGResult.PlateModel.flexural:
            result.Properties["PlateFlexural"].Value = True
            result.Properties["PlateFlexural/E1"].Value     = SGResult.PlateModel.flexural['E1']    
            result.Properties["PlateFlexural/E2"].Value     = SGResult.PlateModel.flexural['E2']    
            result.Properties["PlateFlexural/G12"].Value    = SGResult.PlateModel.flexural['G12']   
            result.Properties["PlateFlexural/nu12"].Value   = SGResult.PlateModel.flexural['nu12']  
            result.Properties["PlateFlexural/eta121"].Value = SGResult.PlateModel.flexural['eta121']
            result.Properties["PlateFlexural/eta122"].Value = SGResult.PlateModel.flexural['eta122']

    elif SGResult.SolidModel:
        result.Properties["Model Information/Macro Model"].Value = "Solid Model"
        result.Properties["SolidStiffness"].Value = True
        result.Properties["SolidStiffness/C11"].Value = SGResult.SolidModel.stiffness[0][0]
        result.Properties["SolidStiffness/C12"].Value = SGResult.SolidModel.stiffness[0][1]
        result.Properties["SolidStiffness/C13"].Value = SGResult.SolidModel.stiffness[0][2]
        result.Properties["SolidStiffness/C14"].Value = SGResult.SolidModel.stiffness[0][3]
        result.Properties["SolidStiffness/C15"].Value = SGResult.SolidModel.stiffness[0][4]
        result.Properties["SolidStiffness/C16"].Value = SGResult.SolidModel.stiffness[0][5]
        result.Properties["SolidStiffness/C22"].Value = SGResult.SolidModel.stiffness[1][1]
        result.Properties["SolidStiffness/C23"].Value = SGResult.SolidModel.stiffness[1][2]
        result.Properties["SolidStiffness/C24"].Value = SGResult.SolidModel.stiffness[1][3]
        result.Properties["SolidStiffness/C25"].Value = SGResult.SolidModel.stiffness[1][4]
        result.Properties["SolidStiffness/C26"].Value = SGResult.SolidModel.stiffness[1][5]
        result.Properties["SolidStiffness/C33"].Value = SGResult.SolidModel.stiffness[2][2]
        result.Properties["SolidStiffness/C34"].Value = SGResult.SolidModel.stiffness[2][3]
        result.Properties["SolidStiffness/C35"].Value = SGResult.SolidModel.stiffness[2][4]
        result.Properties["SolidStiffness/C36"].Value = SGResult.SolidModel.stiffness[2][5]
        result.Properties["SolidStiffness/C44"].Value = SGResult.SolidModel.stiffness[3][3]
        result.Properties["SolidStiffness/C45"].Value = SGResult.SolidModel.stiffness[3][4]
        result.Properties["SolidStiffness/C46"].Value = SGResult.SolidModel.stiffness[3][5]
        result.Properties["SolidStiffness/C55"].Value = SGResult.SolidModel.stiffness[4][4]
        result.Properties["SolidStiffness/C56"].Value = SGResult.SolidModel.stiffness[4][5]
        result.Properties["SolidStiffness/C66"].Value = SGResult.SolidModel.stiffness[5][5]
        result.Properties["SolidCompliance"].Value = True
        result.Properties["SolidCompliance/S11"].Value = SGResult.SolidModel.compliance[0][0]
        result.Properties["SolidCompliance/S12"].Value = SGResult.SolidModel.compliance[0][1]
        result.Properties["SolidCompliance/S13"].Value = SGResult.SolidModel.compliance[0][2]
        result.Properties["SolidCompliance/S14"].Value = SGResult.SolidModel.compliance[0][3]
        result.Properties["SolidCompliance/S15"].Value = SGResult.SolidModel.compliance[0][4]
        result.Properties["SolidCompliance/S16"].Value = SGResult.SolidModel.compliance[0][5]
        result.Properties["SolidCompliance/S22"].Value = SGResult.SolidModel.compliance[1][1]
        result.Properties["SolidCompliance/S23"].Value = SGResult.SolidModel.compliance[1][2]
        result.Properties["SolidCompliance/S24"].Value = SGResult.SolidModel.compliance[1][3]
        result.Properties["SolidCompliance/S25"].Value = SGResult.SolidModel.compliance[1][4]
        result.Properties["SolidCompliance/S26"].Value = SGResult.SolidModel.compliance[1][5]
        result.Properties["SolidCompliance/S33"].Value = SGResult.SolidModel.compliance[2][2]
        result.Properties["SolidCompliance/S34"].Value = SGResult.SolidModel.compliance[2][3]
        result.Properties["SolidCompliance/S35"].Value = SGResult.SolidModel.compliance[2][4]
        result.Properties["SolidCompliance/S36"].Value = SGResult.SolidModel.compliance[2][5]
        result.Properties["SolidCompliance/S44"].Value = SGResult.SolidModel.compliance[3][3]
        result.Properties["SolidCompliance/S45"].Value = SGResult.SolidModel.compliance[3][4]
        result.Properties["SolidCompliance/S46"].Value = SGResult.SolidModel.compliance[3][5]
        result.Properties["SolidCompliance/S55"].Value = SGResult.SolidModel.compliance[4][4]
        result.Properties["SolidCompliance/S56"].Value = SGResult.SolidModel.compliance[4][5]
        result.Properties["SolidCompliance/S66"].Value = SGResult.SolidModel.compliance[5][5]
        if SGResult.SolidModel.engineering:
            result.Properties["EngineeringConstant"].Value = True
            result.Properties["EngineeringConstant/E1"].Value   = SGResult.SolidModel.engineering['E1']
            result.Properties["EngineeringConstant/E2"].Value   = SGResult.SolidModel.engineering['E2']  
            result.Properties["EngineeringConstant/E3"].Value   = SGResult.SolidModel.engineering['E3']  
            result.Properties["EngineeringConstant/G12"].Value  = SGResult.SolidModel.engineering['G12'] 
            result.Properties["EngineeringConstant/G13"].Value  = SGResult.SolidModel.engineering['G13'] 
            result.Properties["EngineeringConstant/G23"].Value  = SGResult.SolidModel.engineering['G23'] 
            result.Properties["EngineeringConstant/nu12"].Value = SGResult.SolidModel.engineering['nu12']
            result.Properties["EngineeringConstant/nu13"].Value = SGResult.SolidModel.engineering['nu13']
            result.Properties["EngineeringConstant/nu23"].Value = SGResult.SolidModel.engineering['nu23']

    result.Properties["Density"].Value = True
    result.Properties["Density/Effective Density"].Value = SGResult.density

    return True


def beamStiffnessVisible(entity, p):
    return p.Value


def beamComplianceVisible(entity, p):
    return p.Value


def beamTimoshenkoStiffnessVisible(entity, p):
    return p.Value 


def beamTimoshenkoComplianceVisible(entity, p):
    return p.Value


def beamShearCenterVisible(entity, p):
    return p.Value


def plateStiffnessVisible(entity, p):
    return p.Value


def plateComplianceVisible(entity, p):
    return p.Value


def plateInPlaneVisible(entity, p):
    return p.Value


def plateFlexuralVisible(entity, p):
    return p.Value


def solidStiffnessVisible(entity, p):
    return p.Value


def solidComplianceVisible(entity, p):
    return p.Value


def engineeringConstantVisible(entity, p):
    return p.Value


def densityVisible(entity, p):
    return p.Value
