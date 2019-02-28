import structural_func
import utilities

import sg
import sg_result
import sg_filesystem
import sg_homogenization_result_list



def importHomogenizationResultInformationSourceOnActivate(object, prop):

    bodyType =  str(ExtAPI.DataModel.GeoData.Assemblies[0].Parts[0].Bodies[0].BodyType)

    from System.Collections.Generic import List

    SGFileSystem = sg_filesystem.SGFileSystem(ExtAPI)

    user_dir_files = os.listdir(SGFileSystem.user_dir)

    if bodyType == 'GeoBodyWire': # beam model
        object.Properties["BeamTimoshenkoStiffness"].Value = True
        object.Properties["PlateReissnerStiffness"].Value  = False
        object.Properties["SolidStiffness"].Value          = False
        object.Properties["Model Information/Macro Model"].Value = "Beam Model"    
    elif bodyType == 'GeoBodySheet':  # plate model
        object.Properties["BeamTimoshenkoStiffness"].Value = False
        object.Properties["PlateReissnerStiffness"].Value  = True
        object.Properties["SolidStiffness"].Value          = False
        object.Properties["Model Information/Macro Model"].Value = "Plate Model"
    elif bodyType == 'GeoBodySolid':  # solid model
        object.Properties["BeamTimoshenkoStiffness"].Value = False
        object.Properties["PlateReissnerStiffness"].Value  = False
        object.Properties["SolidStiffness"].Value          = True
        object.Properties["Model Information/Macro Model"].Value = "Solid Model"

    SGHomogenizationResultList = sg_homogenization_result_list.SGHomogenizationResultList()

    if 'SGHomogenizationResultList.pickle' in user_dir_files:
        with open(SGFileSystem.user_dir + 'SGHomogenizationResultList.pickle', 'rb') as f:
            SGHomogenizationResultList = pickle.load(f)
       
        # extract name list from SGHomogenizationResultList
        resulNameList = []
        if bodyType == 'GeoBodyWire': # beam model
            [resulNameList.append(x.result_name) for x in SGHomogenizationResultList.ResultList if x.BeamModel]
        elif bodyType == 'GeoBodySheet':  # plate model
            [resulNameList.append(x.result_name) for x in SGHomogenizationResultList.ResultList if x.PlateModel]
        elif bodyType == 'GeoBodySolid':  # solid model
            [resulNameList.append(x.result_name) for x in SGHomogenizationResultList.ResultList if x.SolidModel]

        if resulNameList:
            prop.Options = List[str](resulNameList)

            selectedResultName = object.Properties["Information Source/Select/Homogenization Result Name"].Value

            if selectedResultName:  # there is extraction name
                selectedHomogenizationResult =  [x for x in SGHomogenizationResultList.ResultList if x.result_name == selectedResultName]
                structural_func.updateHomogenizationResultNameSelection(object, selectedHomogenizationResult[0])
            elif resulNameList:  # there is no extraction name and there is resulNameList
                object.Properties["Information Source/Select/Homogenization Result Name"].Value = resulNameList[0]
                structural_func.updateHomogenizationResultNameSelection(object, SGHomogenizationResultList.ResultList[0])
            else:  # there is no extraction name and there is no resulNameList
                object.Properties["Information Source/Select/Homogenization Result Name"].Value = "No homogenization results available"
        else:
             object.Properties["Information Source/Select/Homogenization Result Name"].Value = "No homogenization results available"
    else: 
        object.Properties["Information Source/Select/Homogenization Result Name"].Value = "No homogenization results available"


def importHomogenizationResultGetPreCommandsAtTree(object, stream):

    selectedIDs = object.Properties["Body Selection/Select Body(s)"].Value.Ids

    element_ids = []

    for id in selectedIDs:
        element_ids.extend(ExtAPI.DataModel.Project.Model.Analyses[0].MeshData.MeshRegionById(id).ElementIds)

    stream.Write("/COM, Script for importing homogenization result\n\n")

    density =  object.Properties["Density/Effective Density"].Value

    # get largest material number 
    stream.Write("*GET, maxMaterialNumber, MAT, , NUM, MAX\n")
    stream.Write("*set, newMaterialNumber, maxMaterialNumber + 1000\n")

    # write density
    stream.Write("MP,dens, newMaterialNumber, " + str(density) + "\n")


    bodyType =  str(ExtAPI.DataModel.GeoData.Assemblies[0].Parts[0].Bodies[0].BodyType)


    if bodyType == 'GeoBodyWire':  # beam Model

        # get largest composite beam section number 
        stream.Write("*GET, maxBeamSectionNumber, CMPB, , NUM, MAX\n")
        stream.Write("*set, newBeamSectionNumber, maxBeamSectionNumber + 1000\n")

        C11 = object.Properties["BeamTimoshenkoStiffness/C11"].Value
        C12 = object.Properties["BeamTimoshenkoStiffness/C12"].Value
        C13 = object.Properties["BeamTimoshenkoStiffness/C13"].Value
        C14 = object.Properties["BeamTimoshenkoStiffness/C14"].Value
        C15 = object.Properties["BeamTimoshenkoStiffness/C15"].Value
        C16 = object.Properties["BeamTimoshenkoStiffness/C16"].Value
        C22 = object.Properties["BeamTimoshenkoStiffness/C22"].Value
        C23 = object.Properties["BeamTimoshenkoStiffness/C23"].Value
        C24 = object.Properties["BeamTimoshenkoStiffness/C24"].Value
        C25 = object.Properties["BeamTimoshenkoStiffness/C25"].Value
        C26 = object.Properties["BeamTimoshenkoStiffness/C26"].Value
        C33 = object.Properties["BeamTimoshenkoStiffness/C33"].Value
        C34 = object.Properties["BeamTimoshenkoStiffness/C34"].Value
        C35 = object.Properties["BeamTimoshenkoStiffness/C35"].Value
        C36 = object.Properties["BeamTimoshenkoStiffness/C36"].Value
        C44 = object.Properties["BeamTimoshenkoStiffness/C44"].Value
        C45 = object.Properties["BeamTimoshenkoStiffness/C45"].Value
        C46 = object.Properties["BeamTimoshenkoStiffness/C46"].Value
        C55 = object.Properties["BeamTimoshenkoStiffness/C55"].Value
        C56 = object.Properties["BeamTimoshenkoStiffness/C56"].Value
        C66 = object.Properties["BeamTimoshenkoStiffness/C66"].Value

        # SwiftComp convention: e11, g12, g13, k11, k12, k13
        C = [[C11, C12, C13, C14, C15, C16], [C12, C22, C23, C24, C25, C26], [C13, C23, C33, C34, C35, C36],
             [C14, C24, C34, C44, C45, C46], [C15, C25, C35, C45, C55, C56], [C16, C26, C36, C46, C56, C66],]

        # ANSYS convention: e11, k12, k13, k11, g12, g13
        S = C

        S[1], S[4] = S[4], S[1]
        S[2], S[5] = S[5], S[2]
        S = utilities.transpose(S)
        S[1], S[4] = S[4], S[1]
        S[2], S[5] = S[5], S[2]
        S = utilities.transpose(S)

        stream.Write("sectype, newBeamSectionNumber, COMB, MATRIX\n") 
        stream.Write("cbmx,  1, " + str(S[0][0]) + ", " + str(S[0][1]) + ", " + str(S[0][2]) + ", " + str(S[0][3]) + ", " + str(S[0][4]) + ", " + str(S[0][5]) + "\n") 
        stream.Write("cbmx,  2, " + str(S[1][1]) + ", " + str(S[1][2]) + ", " + str(S[1][3]) + ", " + str(S[1][4]) + ", " + str(S[1][5]) + "\n")
        stream.Write("cbmx,  3, " + str(S[2][2]) + ", " + str(S[2][3]) + ", " + str(S[2][4]) + ", " + str(S[2][5]) + "\n") 
        stream.Write("cbmx,  4, " + str(S[3][3]) + ", " + str(S[3][4]) + ", " + str(S[3][5]) + "\n") 
        stream.Write("cbmx,  5, " + str(S[4][4]) + ", " + str(S[4][5]) + "\n") 
        stream.Write("cbmx,  6, " + str(S[5][5]) + "\n") 

        # change the material and beam section of selected element
        for element in element_ids:
            stream.Write("EMODIF, " + str(element) + ", MAT, newMaterialNumber\n") 
            stream.Write("EMODIF, " + str(element) + ", SECNUM, newBeamSectionNumber\n") 

    elif bodyType == 'GeoBodySheet':  # plate Model
        # get largest general shell section number 
        stream.Write("*GET, maxShellSectionNumber, GENS, , NUM, MAX\n")
        stream.Write("*set, newShellSectionNumber, maxShellSectionNumber + 1000\n")

        A11 = object.Properties["PlateReissnerStiffness/A11"].Value
        A12 = object.Properties["PlateReissnerStiffness/A12"].Value
        A16 = object.Properties["PlateReissnerStiffness/A16"].Value
        A22 = object.Properties["PlateReissnerStiffness/A22"].Value
        A26 = object.Properties["PlateReissnerStiffness/A26"].Value
        A66 = object.Properties["PlateReissnerStiffness/A66"].Value
        B11 = object.Properties["PlateReissnerStiffness/B11"].Value
        B12 = object.Properties["PlateReissnerStiffness/B12"].Value
        B16 = object.Properties["PlateReissnerStiffness/B16"].Value
        B22 = object.Properties["PlateReissnerStiffness/B22"].Value
        B26 = object.Properties["PlateReissnerStiffness/B26"].Value
        B66 = object.Properties["PlateReissnerStiffness/B66"].Value
        D11 = object.Properties["PlateReissnerStiffness/D11"].Value
        D12 = object.Properties["PlateReissnerStiffness/D12"].Value
        D16 = object.Properties["PlateReissnerStiffness/D16"].Value
        D22 = object.Properties["PlateReissnerStiffness/D22"].Value
        D26 = object.Properties["PlateReissnerStiffness/D26"].Value
        D66 = object.Properties["PlateReissnerStiffness/D66"].Value
        C11 = object.Properties["PlateReissnerStiffness/C11"].Value
        C12 = object.Properties["PlateReissnerStiffness/C12"].Value
        C22 = object.Properties["PlateReissnerStiffness/C22"].Value

        stream.Write("sectype, newShellSectionNumber, gens\n") 
        stream.Write("sspa, " + str(A11) + ", " + str(A12) + ", " + str(A16) + ", " + str(A22) + ", " + str(A26) + ", " + str(A66) + "\n") 
        stream.Write("sspb, " + str(B11) + ", " + str(B12) + ", " + str(B16) + ", " + str(B22) + ", " + str(B26) + ", " + str(B66) + "\n")
        stream.Write("sspd, " + str(D11) + ", " + str(D12) + ", " + str(D16) + ", " + str(D22) + ", " + str(D26) + ", " + str(D66) + "\n") 
        stream.Write("sspe, " + str(C11) + ", " + str(C12) + ", " + str(C22) + "\n") 

        # change the material and beam section of selected element
        for element in element_ids:
            stream.Write("EMODIF, " + str(element) + ", MAT, newMaterialNumber\n") 
            stream.Write("EMODIF, " + str(element) + ", SECNUM, newShellSectionNumber\n") 

    elif bodyType == 'GeoBodySolid':  # Solid Model


        C11 = object.Properties["SolidStiffness/C11"].Value
        C12 = object.Properties["SolidStiffness/C12"].Value
        C13 = object.Properties["SolidStiffness/C13"].Value
        C14 = object.Properties["SolidStiffness/C14"].Value
        C15 = object.Properties["SolidStiffness/C15"].Value
        C16 = object.Properties["SolidStiffness/C16"].Value
        C22 = object.Properties["SolidStiffness/C22"].Value
        C23 = object.Properties["SolidStiffness/C23"].Value
        C24 = object.Properties["SolidStiffness/C24"].Value
        C25 = object.Properties["SolidStiffness/C25"].Value
        C26 = object.Properties["SolidStiffness/C26"].Value
        C33 = object.Properties["SolidStiffness/C33"].Value
        C34 = object.Properties["SolidStiffness/C34"].Value
        C35 = object.Properties["SolidStiffness/C35"].Value
        C36 = object.Properties["SolidStiffness/C36"].Value
        C44 = object.Properties["SolidStiffness/C44"].Value
        C45 = object.Properties["SolidStiffness/C45"].Value
        C46 = object.Properties["SolidStiffness/C46"].Value
        C55 = object.Properties["SolidStiffness/C55"].Value
        C56 = object.Properties["SolidStiffness/C56"].Value
        C66 = object.Properties["SolidStiffness/C66"].Value
        
        # SwiftComp convention: 11, 22, 33, 23, 13, 12
        C = [[C11, C12, C13, C14, C15, C16], [C12, C22, C23, C24, C25, C26], [C13, C23, C33, C34, C35, C36],
             [C14, C24, C34, C44, C45, C46], [C15, C25, C35, C45, C55, C56], [C16, C26, C36, C46, C56, C66],]

        # ANSYS convention: 11, 22, 33, 12, 23, 13
        D = C

        D[4], D[5] = D[5], D[4]
        D[3], D[4] = D[4], D[3]
        D = utilities.transpose(D)
        D[4], D[5] = D[5], D[4]
        D[3], D[4] = D[4], D[3]
        D = utilities.transpose(D)

        # write anisotropic material properteis
        stream.Write("TB, ANEL, newMaterialNumber\n") 
        stream.Write("TBDATA,  1, " + str(D[0][0]) + ", " + str(D[1][0]) + ", " + str(D[2][0]) + ", " + str(D[3][0]) + ", " + str(D[4][0]) + ", " + str(D[5][0]) + "\n") 
        stream.Write("TBDATA,  7, " + str(D[1][1]) + ", " + str(D[2][1]) + ", " + str(D[3][1]) + ", " + str(D[4][1]) + ", " + str(D[5][1]) + ", " + str(D[2][2]) + "\n") 
        stream.Write("TBDATA, 13, " + str(D[3][2]) + ", " + str(D[4][2]) + ", " + str(D[5][2]) + ", " + str(D[3][3]) + ", " + str(D[4][3]) + ", " + str(D[5][3]) + "\n") 
        stream.Write("TBDATA, 19, " + str(D[4][4]) + ", " + str(D[5][4]) + ", " + str(D[5][5]) + "\n") 

        # change the material of selected element
        for element in element_ids:
            stream.Write("EMODIF, " + str(element) + ", MAT, newMaterialNumber\n") 



def beamTimoshenkoStiffnessVisible(entity, p):
    return p.Value

def plateReissnerStiffnessVisible(entity, p):
    return p.Value

def solidStiffnessVisible(entity, p):
    return p.Value



def extractResultCanAddAtTree(currentAnalysis, string):
    '''extract result can be added at tree or not'''
    return currentAnalysis.SolverName == 'ANSYS'


def extractResultOnInitAtTree(result):

    SGFileSystem = sg_filesystem.SGFileSystem(ExtAPI)

    bodyType =  str(ExtAPI.DataModel.GeoData.Assemblies[0].Parts[0].Bodies[0].BodyType)

    if bodyType == 'GeoBodyWire': # beam model
        result.Properties["Extraction Information/Macro Model"].Value = "Beam Model"
    elif bodyType == 'GeoBodySheet':  # plate model
        result.Properties["Extraction Information/Macro Model"].Value = "Plate/Shell Model"
    elif bodyType == 'GeoBodySolid':  # solid model
        result.Properties["Extraction Information/Macro Model"].Value = "Solid Model"

    # create a dummy script and then delete. 
    # by this way, the solve could be triggered so that we can extract beam/plate strain/stress results
    add_dummy_script = True

    # get the content of ds.dat file
    try:
        with open(SGFileSystem.work_dir + 'ds.dat', 'r') as f:
            ds_content = f.read()
    except:
        ds_content = ''

    if "Script for extraction" in ds_content:
        add_dummy_script = False

    if add_dummy_script:
        dummy_script = ExtAPI.DataModel.Project.Model.Analyses[0].AddCommandSnippet()
        dummy_script.Name = "dummy_script"
        dummy_script.Input = "/COM, This is just a dummy script to update solve.\n It will be deleted once after creation\n"
        dummy_script.Delete()


def extractResultGetSolveCommandsAtTree(load, stream):
    stream.Write("/COM, Script for enabling beam/plate stress/strain data\n\n")
    stream.Write("outres, MISC, all\n")


def extractResultGetPostCommandsAtTree(load, stream):

    SGFileSystem = sg_filesystem.SGFileSystem(ExtAPI)

    bodyType =  str(ExtAPI.DataModel.GeoData.Assemblies[0].Parts[0].Bodies[0].BodyType)
    nelem  = ExtAPI.DataModel.Project.Model.Analyses[0].MeshData.Elements.Count
    nnode  = ExtAPI.DataModel.Project.Model.Analyses[0].MeshData.Nodes.Count

    stream.Write("/COM, Script for extraction\n\n")
    stream.Write("SET, LAST\n\n")

    # write displacement 
    stream.Write("*CFOPEN, " +  SGFileSystem.dir_file_name + "_macro_displacement" + ", txt\n")
    stream.Write("*DO, i, 1, " + str(nnode) + "\n")
    stream.Write("*GET,x1,NODE,i,U,X\n")
    stream.Write("*GET,x2,NODE,i,U,Y\n")
    stream.Write("*GET,x3,NODE,i,U,Z\n")
    stream.Write("*VWRITE, x1, x2, x3\n")
    stream.Write("(E20.13, 3X, E20.13, 3X, E20.13)\n")
    stream.Write("*ENDDO\n")
    stream.Write("*CFCLOS\n\n")

    if bodyType == 'GeoBodyWire': # beam model
        # write macro strain
        stream.Write("*CFOPEN, " +  SGFileSystem.dir_file_name + "_macro_strain" + ", txt\n")
        stream.Write("*DO, i, 1, " + str(nelem) + "\n")
        # extract macro strain at node i
        stream.Write("*GET,e11_i,ELEM,i,smisc,7\n")
        stream.Write("*GET,g12_i,ELEM,i,smisc,12\n")
        stream.Write("*GET,g13_i,ELEM,i,smisc,11\n")
        stream.Write("*GET,k11_i,ELEM,i,smisc,10\n")
        stream.Write("*GET,k12_i,ELEM,i,smisc,8\n")
        stream.Write("*GET,k13_i,ELEM,i,smisc,9\n")
        # extract macro strain at node j
        stream.Write("*GET,e11_j,ELEM,i,smisc,20\n")
        stream.Write("*GET,g12_j,ELEM,i,smisc,25\n")
        stream.Write("*GET,g13_j,ELEM,i,smisc,24\n")
        stream.Write("*GET,k11_j,ELEM,i,smisc,23\n")
        stream.Write("*GET,k12_j,ELEM,i,smisc,21\n")
        stream.Write("*GET,k13_j,ELEM,i,smisc,22\n")
        # calculate the macro strain
        stream.Write("*SET, e11, (e11_i + e11_j)/2\n")
        stream.Write("*SET, g12, (g12_i + g12_j)/2\n")
        stream.Write("*SET, g13, (g13_i + g13_j)/2\n")
        stream.Write("*SET, k11, (k11_i + k11_j)/2\n")
        stream.Write("*SET, k12, (k12_i + k12_j)/2\n")
        stream.Write("*SET, k13, (k13_i + k13_j)/2\n")
        stream.Write("*VWRITE, e11, g12, g13, k11, k12, k13\n")
        stream.Write("(E20.13, 3X, E20.13, 3X, E20.13, 3X, E20.13, 3X, E20.13, 3X, E20.13)\n")
        stream.Write("*ENDDO\n")
        stream.Write("*CFCLOS\n\n")

        # write macro stress
        stream.Write("*CFOPEN, " +  SGFileSystem.dir_file_name + "_macro_stress" + ", txt\n")
        stream.Write("*DO, i, 1, " + str(nelem) + "\n")
        # extract macro stress at node i
        stream.Write("*GET,F1_i,ELEM,i,smisc,1\n")
        stream.Write("*GET,F2_i,ELEM,i,smisc,6\n")
        stream.Write("*GET,F3_i,ELEM,i,smisc,5\n")
        stream.Write("*GET,M1_i,ELEM,i,smisc,4\n")
        stream.Write("*GET,M2_i,ELEM,i,smisc,2\n")
        stream.Write("*GET,M3_i,ELEM,i,smisc,3\n")
        # extract macro stress at node j
        stream.Write("*GET,F1_j,ELEM,i,smisc,14\n")
        stream.Write("*GET,F2_j,ELEM,i,smisc,19\n")
        stream.Write("*GET,F3_j,ELEM,i,smisc,18\n")
        stream.Write("*GET,M1_j,ELEM,i,smisc,17\n")
        stream.Write("*GET,M2_j,ELEM,i,smisc,15\n")
        stream.Write("*GET,M3_j,ELEM,i,smisc,16\n")
        # calculate the macro stress
        stream.Write("F1 = (F1_i + F1_j)/2\n")
        stream.Write("F2 = (F2_i + F2_j)/2\n")
        stream.Write("F3 = (F3_i + F3_j)/2\n")
        stream.Write("M1 = (M1_i + M1_j)/2\n")
        stream.Write("M2 = (M2_i + M2_j)/2\n")
        stream.Write("M3 = (M3_i + M3_j)/2\n")
        stream.Write("*VWRITE, F1, F2, F3, M1, M2, M3\n")
        stream.Write("(E20.13, 3X, E20.13, 3X, E20.13, 3X, E20.13, 3X, E20.13, 3X, E20.13)\n")
        stream.Write("*ENDDO\n")
        stream.Write("*CFCLOS\n\n")

    elif bodyType == 'GeoBodySheet':  # plate model
        # write macro strain
        stream.Write("*CFOPEN, " +  SGFileSystem.dir_file_name + "_macro_strain" + ", txt\n")
        stream.Write("*DO, i, 1, " + str(nelem) + "\n")
        # extract macro strain 
        stream.Write("*GET,e11,ELEM,i,smisc,9\n")
        stream.Write("*GET,e22,ELEM,i,smisc,10\n")
        stream.Write("*GET,e12,ELEM,i,smisc,11\n")
        stream.Write("*GET,k11,ELEM,i,smisc,12\n")
        stream.Write("*GET,k22,ELEM,i,smisc,13\n")
        stream.Write("*GET,k12,ELEM,i,smisc,14\n")
        stream.Write("*GET,g13,ELEM,i,smisc,15\n")
        stream.Write("*GET,g23,ELEM,i,smisc,16\n")
        stream.Write("*SET,e12, e12 * 2\n")
        stream.Write("*SET,K12, K12 * 2\n")
        stream.Write("*VWRITE, e11, e22, e12, k11, k22, k12, g13, g23\n")
        stream.Write("(E20.13, 3X, E20.13, 3X, E20.13, 3X, E20.13, 3X, E20.13, 3X, E20.13, 3X, E20.13, 3X, E20.13)\n")
        stream.Write("*ENDDO\n")
        stream.Write("*CFCLOS\n\n")

        # write macro stress
        stream.Write("*CFOPEN, " +  SGFileSystem.dir_file_name + "_macro_stress" + ", txt\n")
        stream.Write("*DO, i, 1, " + str(nelem) + "\n")
        # extract macro stress
        stream.Write("*GET,N11,ELEM,i,smisc,1\n")
        stream.Write("*GET,N22,ELEM,i,smisc,2\n")
        stream.Write("*GET,N12,ELEM,i,smisc,3\n")
        stream.Write("*GET,M11,ELEM,i,smisc,4\n")
        stream.Write("*GET,M22,ELEM,i,smisc,5\n")
        stream.Write("*GET,M12,ELEM,i,smisc,6\n")
        stream.Write("*GET,N13,ELEM,i,smisc,7\n")
        stream.Write("*GET,N23,ELEM,i,smisc,8\n")
        stream.Write("*VWRITE, N11, N22, N12, M11, M22, M12, N13, N23\n")
        stream.Write("(E20.13, 3X, E20.13, 3X, E20.13, 3X, E20.13, 3X, E20.13, 3X, E20.13, 3X, E20.13, 3X, E20.13)\n")
        stream.Write("*ENDDO\n")
        stream.Write("*CFCLOS\n\n")


def extractResultOnGenerateAtTree(result, fct):
    '''when extract result is on generated at tree'''

    dehom_flag = result.Properties["Dehomogenization Information/Dehomogenization at the same time"].Value

    ids = result.Properties["Element Selection/Select Element(s)"].Value

    elem_ids = [int(i) for i in ids]

    arguments = [ExtAPI, result, elem_ids]

    extractResult = ExtAPI.Application.InvokeUIThread(structural_func.extractResult, arguments)

    [macro_model, macro_displacement, macro_rotation, macro_strain, macro_stress] = extractResult

    result.Properties["Macro Displacements"].Value = True
    result.Properties["Macro Displacements/v1"].Value = '0'
    result.Properties["Macro Displacements/v1"].Value = str(macro_displacement[0])
    result.Properties["Macro Displacements/v2"].Value = str(macro_displacement[1])
    result.Properties["Macro Displacements/v3"].Value = str(macro_displacement[2])

    result.Properties["Macro Rotations"].Value = True
    result.Properties["Macro Rotations/C11"].Value = str(macro_rotation[0][0])
    result.Properties["Macro Rotations/C12"].Value = str(macro_rotation[0][1])
    result.Properties["Macro Rotations/C13"].Value = str(macro_rotation[0][2])
    result.Properties["Macro Rotations/C21"].Value = str(macro_rotation[1][0])
    result.Properties["Macro Rotations/C22"].Value = str(macro_rotation[1][1])
    result.Properties["Macro Rotations/C23"].Value = str(macro_rotation[1][2])
    result.Properties["Macro Rotations/C31"].Value = str(macro_rotation[2][0])
    result.Properties["Macro Rotations/C32"].Value = str(macro_rotation[2][1])
    result.Properties["Macro Rotations/C33"].Value = str(macro_rotation[2][2])

    if macro_model == 1:
        if len(elem_ids) == 1:
            name = result.Caption + ": Beam element no " + str(elem_ids[0])
        else:
            name = result.Caption + ": " + str(len(elem_ids)) + " beam elements"
        result.Properties["Extraction Information/Extraction Name"].Value = name
        result.Properties["Macro Generalized Strains for Beam Model"].Value = True
        result.Properties["Macro Generalized Stresses for Beam Model"].Value = True
        result.Properties["Macro Generalized Strains for Plate Model"].Value = False
        result.Properties["Macro Generalized Stresses for Plate Model"].Value = False
        result.Properties["Macro Generalized Strains for Solid Model"].Value = False
        result.Properties["Macro Generalized Stresses for Solid Model"].Value = False
        result.Properties["Macro Generalized Strains for Beam Model/epsilon11"].Value = str(macro_strain[0])
        result.Properties["Macro Generalized Strains for Beam Model/gamma12"].Value   = str(macro_strain[1])
        result.Properties["Macro Generalized Strains for Beam Model/gamma13"].Value   = str(macro_strain[2])
        result.Properties["Macro Generalized Strains for Beam Model/kappa11"].Value   = str(macro_strain[3])
        result.Properties["Macro Generalized Strains for Beam Model/kappa12"].Value   = str(macro_strain[4])
        result.Properties["Macro Generalized Strains for Beam Model/kappa13"].Value   = str(macro_strain[5])
        result.Properties["Macro Generalized Stresses for Beam Model/F1"].Value   = str(macro_stress[0])
        result.Properties["Macro Generalized Stresses for Beam Model/F2"].Value   = str(macro_stress[1])
        result.Properties["Macro Generalized Stresses for Beam Model/F3"].Value   = str(macro_stress[2])
        result.Properties["Macro Generalized Stresses for Beam Model/M1"].Value   = str(macro_stress[3])
        result.Properties["Macro Generalized Stresses for Beam Model/M2"].Value   = str(macro_stress[4])
        result.Properties["Macro Generalized Stresses for Beam Model/M3"].Value   = str(macro_stress[5])

    elif macro_model == 2:
        if len(elem_ids) == 1:
            name = result.Caption + ": Shell element no " + str(elem_ids[0])
        else:
            name = result.Caption + ": " + str(len(elem_ids)) + " shell elements"
        result.Properties["Extraction Information/Extraction Name"].Value = name
        result.Properties["Macro Generalized Strains for Beam Model"].Value = False
        result.Properties["Macro Generalized Stresses for Beam Model"].Value = False
        result.Properties["Macro Generalized Strains for Plate Model"].Value = True
        result.Properties["Macro Generalized Stresses for Plate Model"].Value = True
        result.Properties["Macro Generalized Strains for Solid Model"].Value = False
        result.Properties["Macro Generalized Stresses for Solid Model"].Value = False
        result.Properties["Macro Generalized Strains for Plate Model/epsilon11"].Value  = str(macro_strain[0])
        result.Properties["Macro Generalized Strains for Plate Model/epsilon22"].Value  = str(macro_strain[1])
        result.Properties["Macro Generalized Strains for Plate Model/2epsilon12"].Value = str(macro_strain[2])
        result.Properties["Macro Generalized Strains for Plate Model/kappa11"].Value    = str(macro_strain[3])
        result.Properties["Macro Generalized Strains for Plate Model/kappa22"].Value    = str(macro_strain[4])
        result.Properties["Macro Generalized Strains for Plate Model/2kappa12"].Value   = str(macro_strain[5])
        result.Properties["Macro Generalized Strains for Plate Model/gamma13"].Value    = str(macro_strain[6])
        result.Properties["Macro Generalized Strains for Plate Model/gamma23"].Value    = str(macro_strain[7])
        result.Properties["Macro Generalized Stresses for Plate Model/N11"].Value   = str(macro_stress[0])
        result.Properties["Macro Generalized Stresses for Plate Model/N22"].Value   = str(macro_stress[1])
        result.Properties["Macro Generalized Stresses for Plate Model/N12"].Value   = str(macro_stress[2])
        result.Properties["Macro Generalized Stresses for Plate Model/M11"].Value   = str(macro_stress[3])
        result.Properties["Macro Generalized Stresses for Plate Model/M22"].Value   = str(macro_stress[4])
        result.Properties["Macro Generalized Stresses for Plate Model/M12"].Value   = str(macro_stress[5])
        result.Properties["Macro Generalized Stresses for Plate Model/N13"].Value   = str(macro_stress[6])
        result.Properties["Macro Generalized Stresses for Plate Model/N23"].Value   = str(macro_stress[7])

    elif macro_model == 3:
        if len(elem_ids) == 1:
            name = result.Caption + ": Solid element no " + str(elem_ids[0])
        else:
            name = result.Caption + ": " + str(len(elem_ids)) + " solid elements"
        result.Properties["Extraction Information/Extraction Name"].Value = name
        result.Properties["Macro Generalized Strains for Beam Model"].Value = False
        result.Properties["Macro Generalized Stresses for Beam Model"].Value = False
        result.Properties["Macro Generalized Strains for Plate Model"].Value = False
        result.Properties["Macro Generalized Stresses for Plate Model"].Value = False
        result.Properties["Macro Generalized Strains for Solid Model"].Value = True
        result.Properties["Macro Generalized Stresses for Solid Model"].Value = True
        result.Properties["Macro Generalized Strains for Solid Model/epsilon11"].Value  = str(macro_strain[0])
        result.Properties["Macro Generalized Strains for Solid Model/epsilon22"].Value  = str(macro_strain[1])
        result.Properties["Macro Generalized Strains for Solid Model/epsilon33"].Value  = str(macro_strain[2])
        result.Properties["Macro Generalized Strains for Solid Model/2epsilon23"].Value = str(macro_strain[3])
        result.Properties["Macro Generalized Strains for Solid Model/2epsilon13"].Value = str(macro_strain[4])
        result.Properties["Macro Generalized Strains for Solid Model/2epsilon12"].Value = str(macro_strain[5])
        result.Properties["Macro Generalized Stresses for Solid Model/sigma11"].Value  = str(macro_stress[0])
        result.Properties["Macro Generalized Stresses for Solid Model/sigma22"].Value  = str(macro_stress[1])
        result.Properties["Macro Generalized Stresses for Solid Model/sigma33"].Value  = str(macro_stress[2])
        result.Properties["Macro Generalized Stresses for Solid Model/sigma23"].Value  = str(macro_stress[3])
        result.Properties["Macro Generalized Stresses for Solid Model/sigma13"].Value  = str(macro_stress[4])
        result.Properties["Macro Generalized Stresses for Solid Model/sigma12"].Value  = str(macro_stress[5])

    arguments2 = [ExtAPI, name, macro_model, macro_displacement, macro_rotation, macro_strain, macro_stress]

    ExtAPI.Application.InvokeUIThread(structural_func.updateSGStructuralResultListObject, arguments2)

    if dehom_flag == "Yes":
        return ExtAPI.Application.InvokeUIThread(structural_func.dehomogenizationFromStructuralAnalysis, arguments2)

    return True


def displacementExtractResultVisible(entity, p):
    return p.Value


def rotationExtractResultVisible(entity, p):
    return p.Value


def beamStrainExtractResultVisible(entity, p):
    return p.Value


def beamStressExtractResultVisible(entity, p):
    return p.Value


def plateStrainExtractResultVisible(entity, p):
    return p.Value


def plateStressExtractResultVisible(entity, p):
    return p.Value


def solidStrainExtractResultVisible(entity, p):
    return p.Value


def solidStressExtractResultVisible(entity, p):
    return p.Value


def extractResulOnRemovetAtTree(result):
    '''when extract result is on remove at tree'''

    name = result.Properties["Extraction Information/Extraction Name"].Value

    arguments = [ExtAPI, name]

    ExtAPI.Application.InvokeUIThread(structural_func.updateSGStructuralResultListObjectWhenRemove, arguments)