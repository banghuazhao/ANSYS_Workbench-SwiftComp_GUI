import os
import pickle
import subprocess
import time
import os

import utilities
import errorcheck

import sg
import sg_result
import sg_filesystem
import sg_structural_result_list


def extractResult(arg):
    '''
    Calcluate extracted results for dehomogenization: 
    macro_displacement = [v1, v2, v3]
    macro_rotation = [[C11, C12, C13], [C21, C22, C23], [C31, C32, c33]]
    macro_strain:
    BeamModel: [epsilon11 kappa11 kappa12 kappa13]
    PlateModel: [epsilon11 2epsilon12 epsilon22 kappa11 kappa12+kappa21 kappa22]
    SolidModel: [epsilon11 epsilon22 epsilon33 2epsilon23 2epsilon13 2epsilon12]
    '''

    ExtAPI, result, elem_ids = arg[0], arg[1], arg[2]

    reader = result.Analysis.GetResultsData()
    mesh = result.Analysis.MeshData

    macro_model = ExtAPI.DataModel.Project.Model.Analyses[0].MeshData.ElementById(elem_ids[0]).Dimension

    SGFileSystem = sg_filesystem.SGFileSystem(ExtAPI)

    # Get node ids in the selection
    node_ids = []
    for i in elem_ids:
        elem_node = mesh.ElementById(i).CornerNodeIds
        node_ids += elem_node
    node_ids = list(set(node_ids))

    # Get displacement vector
    macro_displacement_all = []
    with open(SGFileSystem.dir_file_name + "_macro_displacement.txt",'r') as f:
        macro_displacement_all = f.readlines()

    macro_displacement = [0] * 3
    for i in node_ids:
        temp_displacement = [float(component) for component in macro_displacement_all[i-1].split()]
        macro_displacement = [x + y for x, y in zip(macro_displacement, temp_displacement)]

    macro_displacement = [component / len(node_ids) for component in macro_displacement]

    # Get macro rotation
    macro_rotation = [[1., 0., 0.], [0., 1., 0.], [0., 0., 1.]]
 
    if macro_model==1:  # Get macro strain and stress tensor for beam model
        # strain
        macro_strain_all = []
        with open(SGFileSystem.dir_file_name + "_macro_strain.txt",'r') as f:
            macro_strain_all = f.readlines()

        macro_strain = [0] * 6
        for i in elem_ids:
            temp_strain = [float(component) for component in macro_strain_all[i-1].split()]
            macro_strain = [x + y for x, y in zip(macro_strain, temp_strain)]

        macro_strain = [component / len(elem_ids) for component in macro_strain]

        # stress
        macro_stress_all = []
        with open(SGFileSystem.dir_file_name + "_macro_stress.txt",'r') as f:
            macro_stress_all = f.readlines()

        macro_stress = [0] * 6
        for i in elem_ids:
            temp_stress = [float(component) for component in macro_stress_all[i-1].split()]
            macro_stress = [x + y for x, y in zip(macro_stress, temp_stress)]

        macro_stress = [component / len(elem_ids) for component in macro_stress]

    elif macro_model==2:  # Get macro strain and stress tensor for plate model
        # strain
        macro_strain_all = []
        with open(SGFileSystem.dir_file_name + "_macro_strain.txt",'r') as f:
            macro_strain_all = f.readlines()

        macro_strain = [0] * 8
        for i in elem_ids:
            temp_strain = [float(component) for component in macro_strain_all[i-1].split()]
            macro_strain = [x + y for x, y in zip(macro_strain, temp_strain)]

        macro_strain = [component / len(elem_ids) for component in macro_strain]

        # stress
        macro_stress_all = []
        with open(SGFileSystem.dir_file_name + "_macro_stress.txt",'r') as f:
            macro_stress_all = f.readlines()

        macro_stress = [0] * 8
        for i in elem_ids:
            temp_stress = [float(component) for component in macro_stress_all[i-1].split()]
            macro_stress = [x + y for x, y in zip(macro_stress, temp_stress)]

        macro_stress = [component / len(elem_ids) for component in macro_stress]

    elif macro_model==3:  # Get macro strain and stress tensor for solid model

        # strain
        strain = reader.GetResult("EPEL")
        strain_sum = [0] * 6
        for i in elem_ids:
            elem_node = mesh.ElementById(i).CornerNodeCount
            strain_tensor = strain.GetElementValues(i)
            for j in range(6):
                for k in range(elem_node):
                    strain_sum[j] += strain_tensor[j + k * 6]

        # 11 22 33 12 23 13
        temp_strain = [x / len(elem_ids) for x in strain_sum]
        # 11 22 33 23 13 12
        macro_strain = [temp_strain[0], temp_strain[1], temp_strain[2], 2*temp_strain[4], 2*temp_strain[5], 2*temp_strain[3]]

        # stress
        stress = reader.GetResult("S")
        stress_sum = [0] * 6
        for i in elem_ids:
            elem_node = mesh.ElementById(i).CornerNodeCount
            stress_tensor = stress.GetElementValues(i)
            for j in range(6):
                for k in range(elem_node):
                    stress_sum[j] += stress_tensor[j + k * 6]

        # 11 22 33 12 23 13
        temp_stress = [x / len(elem_ids) for x in stress_sum]
        # 11 22 33 23 13 12
        macro_stress = [temp_stress[0], temp_stress[1], temp_stress[2], temp_stress[4], temp_stress[5], temp_stress[3]]

    reader.Dispose()

    extractResult = [macro_model, macro_displacement, macro_rotation, macro_strain, macro_stress]

    return extractResult


def updateSGStructuralResultListObject(arg):

    ExtAPI = arg[0]

    name, macro_model, macro_displacement, macro_rotation, macro_strain, macro_stress = arg[1:]

    SGFileSystem = sg_filesystem.SGFileSystem(ExtAPI)

    user_dir_files = os.listdir(SGFileSystem.user_dir)

    SGStructuralResultList = sg_structural_result_list.SGStructuralResultList()

    if "SGStructuralResultList.pickle" in user_dir_files:
        with open(SGFileSystem.user_dir + 'SGStructuralResultList.pickle', 'rb') as f:
            SGStructuralResultList = pickle.load(f)

    SGStructuralResultList.setStructuralResult(name, macro_model, macro_displacement, macro_rotation, macro_strain, macro_stress)

    # save updated SGStructuralResultList
    with open(SGFileSystem.user_dir + 'SGStructuralResultList.pickle', 'wb') as f:
        pickle.dump(SGStructuralResultList, f)


def updateSGStructuralResultListObjectWhenRemove(arg):

    ExtAPI, name = arg[:]

    SGFileSystem = sg_filesystem.SGFileSystem(ExtAPI)

    user_dir_files = os.listdir(SGFileSystem.user_dir)

    SGStructuralResultList = sg_structural_result_list.SGStructuralResultList()

    if "SGStructuralResultList.pickle" in user_dir_files:
        with open(SGFileSystem.user_dir + "SGStructuralResultList.pickle", 'rb') as f:
            SGStructuralResultList = pickle.load(f)

        # remove the SGStructuralResult in the list
        for i in range(len(SGStructuralResultList.ResultList)):
            if name == SGStructuralResultList.ResultList[i].name:
                del SGStructuralResultList.ResultList[i]
                break

        # save updated SGStructuralResultList
        with open(SGFileSystem.user_dir + "SGStructuralResultList.pickle", 'wb') as f:
            pickle.dump(SGStructuralResultList, f)


def updateHomogenizationResultNameSelection(object, SGHomogenizatoinResult):

    object.Properties["Density/Effective Density"].Value = SGHomogenizatoinResult.density

    if SGHomogenizatoinResult.BeamModel:
        if SGHomogenizatoinResult.BeamModel.submodel == 0:
            object.Properties["Model Information/Macro Model"].Value = "Euler-Bernoulli Beam Model"
            object.Properties["BeamTimoshenkoStiffness/C11"].Value = SGHomogenizatoinResult.BeamModel.stiffness[0][0]
            object.Properties["BeamTimoshenkoStiffness/C12"].Value = 0
            object.Properties["BeamTimoshenkoStiffness/C13"].Value = 0
            object.Properties["BeamTimoshenkoStiffness/C14"].Value = SGHomogenizatoinResult.BeamModel.stiffness[0][1]
            object.Properties["BeamTimoshenkoStiffness/C15"].Value = SGHomogenizatoinResult.BeamModel.stiffness[0][2]
            object.Properties["BeamTimoshenkoStiffness/C16"].Value = SGHomogenizatoinResult.BeamModel.stiffness[0][3]
            object.Properties["BeamTimoshenkoStiffness/C22"].Value = 1
            object.Properties["BeamTimoshenkoStiffness/C23"].Value = 0
            object.Properties["BeamTimoshenkoStiffness/C24"].Value = 0
            object.Properties["BeamTimoshenkoStiffness/C25"].Value = 0
            object.Properties["BeamTimoshenkoStiffness/C26"].Value = 0
            object.Properties["BeamTimoshenkoStiffness/C33"].Value = 1
            object.Properties["BeamTimoshenkoStiffness/C34"].Value = 0
            object.Properties["BeamTimoshenkoStiffness/C35"].Value = 0
            object.Properties["BeamTimoshenkoStiffness/C36"].Value = 0
            object.Properties["BeamTimoshenkoStiffness/C44"].Value = SGHomogenizatoinResult.BeamModel.stiffness[1][1]
            object.Properties["BeamTimoshenkoStiffness/C45"].Value = SGHomogenizatoinResult.BeamModel.stiffness[1][2]
            object.Properties["BeamTimoshenkoStiffness/C46"].Value = SGHomogenizatoinResult.BeamModel.stiffness[1][3]
            object.Properties["BeamTimoshenkoStiffness/C55"].Value = SGHomogenizatoinResult.BeamModel.stiffness[2][2]
            object.Properties["BeamTimoshenkoStiffness/C56"].Value = SGHomogenizatoinResult.BeamModel.stiffness[2][3]
            object.Properties["BeamTimoshenkoStiffness/C66"].Value = SGHomogenizatoinResult.BeamModel.stiffness[3][3]
        elif SGHomogenizatoinResult.BeamModel.submodel == 1:
            object.Properties["Model Information/Macro Model"].Value = "Timoshenko Beam Model"
            object.Properties["BeamTimoshenkoStiffness/C11"].Value = SGHomogenizatoinResult.BeamModel.TimoshenkoStiffness[0][0]
            object.Properties["BeamTimoshenkoStiffness/C12"].Value = SGHomogenizatoinResult.BeamModel.TimoshenkoStiffness[0][1]
            object.Properties["BeamTimoshenkoStiffness/C13"].Value = SGHomogenizatoinResult.BeamModel.TimoshenkoStiffness[0][2]
            object.Properties["BeamTimoshenkoStiffness/C14"].Value = SGHomogenizatoinResult.BeamModel.TimoshenkoStiffness[0][3]
            object.Properties["BeamTimoshenkoStiffness/C15"].Value = SGHomogenizatoinResult.BeamModel.TimoshenkoStiffness[0][4]
            object.Properties["BeamTimoshenkoStiffness/C16"].Value = SGHomogenizatoinResult.BeamModel.TimoshenkoStiffness[0][5]
            object.Properties["BeamTimoshenkoStiffness/C22"].Value = SGHomogenizatoinResult.BeamModel.TimoshenkoStiffness[1][1]
            object.Properties["BeamTimoshenkoStiffness/C23"].Value = SGHomogenizatoinResult.BeamModel.TimoshenkoStiffness[1][2]
            object.Properties["BeamTimoshenkoStiffness/C24"].Value = SGHomogenizatoinResult.BeamModel.TimoshenkoStiffness[1][3]
            object.Properties["BeamTimoshenkoStiffness/C25"].Value = SGHomogenizatoinResult.BeamModel.TimoshenkoStiffness[1][4]
            object.Properties["BeamTimoshenkoStiffness/C26"].Value = SGHomogenizatoinResult.BeamModel.TimoshenkoStiffness[1][5]
            object.Properties["BeamTimoshenkoStiffness/C33"].Value = SGHomogenizatoinResult.BeamModel.TimoshenkoStiffness[2][2]
            object.Properties["BeamTimoshenkoStiffness/C34"].Value = SGHomogenizatoinResult.BeamModel.TimoshenkoStiffness[2][3]
            object.Properties["BeamTimoshenkoStiffness/C35"].Value = SGHomogenizatoinResult.BeamModel.TimoshenkoStiffness[2][4]
            object.Properties["BeamTimoshenkoStiffness/C36"].Value = SGHomogenizatoinResult.BeamModel.TimoshenkoStiffness[2][5]
            object.Properties["BeamTimoshenkoStiffness/C44"].Value = SGHomogenizatoinResult.BeamModel.TimoshenkoStiffness[3][3]
            object.Properties["BeamTimoshenkoStiffness/C45"].Value = SGHomogenizatoinResult.BeamModel.TimoshenkoStiffness[3][4]
            object.Properties["BeamTimoshenkoStiffness/C46"].Value = SGHomogenizatoinResult.BeamModel.TimoshenkoStiffness[3][5]
            object.Properties["BeamTimoshenkoStiffness/C55"].Value = SGHomogenizatoinResult.BeamModel.TimoshenkoStiffness[4][4]
            object.Properties["BeamTimoshenkoStiffness/C56"].Value = SGHomogenizatoinResult.BeamModel.TimoshenkoStiffness[4][5]
            object.Properties["BeamTimoshenkoStiffness/C66"].Value = SGHomogenizatoinResult.BeamModel.TimoshenkoStiffness[5][5]
    elif SGHomogenizatoinResult.PlateModel:
        if SGHomogenizatoinResult.PlateModel.submodel == 0:
            object.Properties["Model Information/Macro Model"].Value = "Kirchhoff-Love Model"
            object.Properties["PlateReissnerStiffness/A11"].Value = SGHomogenizatoinResult.PlateModel.stiffness[0][0]
            object.Properties["PlateReissnerStiffness/A12"].Value = SGHomogenizatoinResult.PlateModel.stiffness[0][1]
            object.Properties["PlateReissnerStiffness/A16"].Value = SGHomogenizatoinResult.PlateModel.stiffness[0][2]
            object.Properties["PlateReissnerStiffness/A22"].Value = SGHomogenizatoinResult.PlateModel.stiffness[1][1]
            object.Properties["PlateReissnerStiffness/A26"].Value = SGHomogenizatoinResult.PlateModel.stiffness[1][2]
            object.Properties["PlateReissnerStiffness/A66"].Value = SGHomogenizatoinResult.PlateModel.stiffness[2][2]
            object.Properties["PlateReissnerStiffness/B11"].Value = SGHomogenizatoinResult.PlateModel.stiffness[0][3]
            object.Properties["PlateReissnerStiffness/B12"].Value = SGHomogenizatoinResult.PlateModel.stiffness[0][4]
            object.Properties["PlateReissnerStiffness/B16"].Value = SGHomogenizatoinResult.PlateModel.stiffness[0][5]
            object.Properties["PlateReissnerStiffness/B22"].Value = SGHomogenizatoinResult.PlateModel.stiffness[1][4]
            object.Properties["PlateReissnerStiffness/B26"].Value = SGHomogenizatoinResult.PlateModel.stiffness[1][5]
            object.Properties["PlateReissnerStiffness/B66"].Value = SGHomogenizatoinResult.PlateModel.stiffness[2][5]
            object.Properties["PlateReissnerStiffness/D11"].Value = SGHomogenizatoinResult.PlateModel.stiffness[3][3]
            object.Properties["PlateReissnerStiffness/D12"].Value = SGHomogenizatoinResult.PlateModel.stiffness[3][4]
            object.Properties["PlateReissnerStiffness/D16"].Value = SGHomogenizatoinResult.PlateModel.stiffness[3][5]
            object.Properties["PlateReissnerStiffness/D22"].Value = SGHomogenizatoinResult.PlateModel.stiffness[4][4]
            object.Properties["PlateReissnerStiffness/D26"].Value = SGHomogenizatoinResult.PlateModel.stiffness[4][5]
            object.Properties["PlateReissnerStiffness/D66"].Value = SGHomogenizatoinResult.PlateModel.stiffness[5][5]
            object.Properties["PlateReissnerStiffness/C11"].Value = 1.0
            object.Properties["PlateReissnerStiffness/C12"].Value = 0.0
            object.Properties["PlateReissnerStiffness/C22"].Value = 1.0
    elif SGHomogenizatoinResult.SolidModel:
        object.Properties["Model Information/Macro Model"].Value = "Solid Model"
        object.Properties["SolidStiffness/C11"].Value = SGHomogenizatoinResult.SolidModel.stiffness[0][0]
        object.Properties["SolidStiffness/C12"].Value = SGHomogenizatoinResult.SolidModel.stiffness[0][1]
        object.Properties["SolidStiffness/C13"].Value = SGHomogenizatoinResult.SolidModel.stiffness[0][2]
        object.Properties["SolidStiffness/C14"].Value = SGHomogenizatoinResult.SolidModel.stiffness[0][3]
        object.Properties["SolidStiffness/C15"].Value = SGHomogenizatoinResult.SolidModel.stiffness[0][4]
        object.Properties["SolidStiffness/C16"].Value = SGHomogenizatoinResult.SolidModel.stiffness[0][5]
        object.Properties["SolidStiffness/C22"].Value = SGHomogenizatoinResult.SolidModel.stiffness[1][1]
        object.Properties["SolidStiffness/C23"].Value = SGHomogenizatoinResult.SolidModel.stiffness[1][2]
        object.Properties["SolidStiffness/C24"].Value = SGHomogenizatoinResult.SolidModel.stiffness[1][3]
        object.Properties["SolidStiffness/C25"].Value = SGHomogenizatoinResult.SolidModel.stiffness[1][4]
        object.Properties["SolidStiffness/C26"].Value = SGHomogenizatoinResult.SolidModel.stiffness[1][5]
        object.Properties["SolidStiffness/C33"].Value = SGHomogenizatoinResult.SolidModel.stiffness[2][2]
        object.Properties["SolidStiffness/C34"].Value = SGHomogenizatoinResult.SolidModel.stiffness[2][3]
        object.Properties["SolidStiffness/C35"].Value = SGHomogenizatoinResult.SolidModel.stiffness[2][4]
        object.Properties["SolidStiffness/C36"].Value = SGHomogenizatoinResult.SolidModel.stiffness[2][5]
        object.Properties["SolidStiffness/C44"].Value = SGHomogenizatoinResult.SolidModel.stiffness[3][3]
        object.Properties["SolidStiffness/C45"].Value = SGHomogenizatoinResult.SolidModel.stiffness[3][4]
        object.Properties["SolidStiffness/C46"].Value = SGHomogenizatoinResult.SolidModel.stiffness[3][5]
        object.Properties["SolidStiffness/C55"].Value = SGHomogenizatoinResult.SolidModel.stiffness[4][4]
        object.Properties["SolidStiffness/C56"].Value = SGHomogenizatoinResult.SolidModel.stiffness[4][5]
        object.Properties["SolidStiffness/C66"].Value = SGHomogenizatoinResult.SolidModel.stiffness[5][5]



def dehomogenizationFromStructuralAnalysis(arg):

    ExtAPI = arg[0]

    name, macro_model, macro_displacement, macro_rotation, macro_strain, macro_stress = arg[1:]

    SGFileSystem = sg_filesystem.SGFileSystem(ExtAPI)

    SG = sg.StructureGenome()
    with open(SGFileSystem.user_dir + 'SG.pickle', 'rb') as f:
        SG = pickle.load(f)

    # Generate SwiftComp dehomogenization input file *.sc.glb
    with open(SGFileSystem.dir_file_name_sc_glb, 'w') as f:

        # ----- Write macro displacements --------------------
        utilities.writeFormat(f, 'EEE', macro_displacement)
        f.write('\n')

        # ----- Write macro rotations --------------------
        utilities.writeFormat(f, 'EEE', macro_rotation[0])
        f.write('\n')
        utilities.writeFormat(f, 'EEE', macro_rotation[1])
        f.write('\n')
        utilities.writeFormat(f, 'EEE', macro_rotation[2])
        f.write('\n')

        # ----- Write id --------------------
        utilities.writeFormat(f, 'd', [1])


        # ----- Write macrogeneralized strains --------------------
        if SG.BeamModel:
            if SG.BeamModel.submodel == 0:    
                utilities.writeFormat(f, 'E' * 4, macro_strain[0:4])
            elif SG.BeamModel.submodel == 1:    
                utilities.writeFormat(f, 'E' * 6, macro_strain[0:6])
        elif SG.PlateModel:
            if SG.PlateModel.submodel == 0:   
                utilities.writeFormat(f, 'E' * 6, macro_strain[0:6])
            else:
                utilities.writeFormat(f, 'E' * 8, macro_strain[0:8])
        elif SG.SolidModel:
            utilities.writeFormat(f, 'E' * 6, macro_strain[0:6])
        f.write('\n')


    # create dehomogenization command
    arg1 = SGFileSystem.file_name_sc

    if SG.BeamModel:
        arg2 = '1D'
    elif SG.PlateModel:
        arg2 = '2D'
    elif SG.SolidModel:
        arg2 = '3D'

    if not SG.aperiodic:
        arg3 = 'L'
    else:
        arg3 = 'LA'

    arg4 = ''

    # Run dehomogenization! save stdout to a file named temp
    command = ['SwiftComp', arg1, arg2, arg3, arg4, '>', SGFileSystem.user_dir+'temp']
    exitCode = subprocess.call(command, cwd=SGFileSystem.user_dir, shell=True)
    if exitCode != 0:
        return False

    # Get standard output
    with open(SGFileSystem.user_dir + 'temp') as f:
        dehommStdout = f.read()
    os.remove(SGFileSystem.user_dir + 'temp')

    # Check whether the dehomogenization is successful or not.
    if errorcheck.dehomNotSuccessful(ExtAPI, dehommStdout):
        return False

    # obtain dehomogenization data

    # read *.u file
    with open(SGFileSystem.dir_file_name_sc_u, 'r') as f:
        # nodal displacement value
        # n_dis = [
        #     [node_no1, ux1, uy1, uz1],
        #     [node_no2, ux2, uy2, uz2],
        #     ...
        # ]
        n_dis = []
        for i in range(SG.nnode):
            line = f.readline().split()
            n_dis += [[int(line[0]), float(line[1]), float(line[2]), float(line[3])]]

    # read *.sn file
    with open(SGFileSystem.dir_file_name_sc_sn, 'r') as f:
        # stress and strain result at elemental Gaussian points
        #
        # e_stress = {
        #    elem_no1: [
        #        [node_no1, s11, s22, s33, s23, s13, s23],
        #        [node_no2, s11, s22, s33, s23, s13, s23],
        #         ...
        #        ],
        #    ...
        #    }
        #
        # e_strain = {
        #    elem_no1: [
        #        [node_no1, e11, e22, e33, 2e23, 2e13, 2e23],
        #        [node_no2, e11, e22, e33, 2e23, 2e13, 2e23],
        #         ...
        #        ],
        #    ...
        #    }
        e_strain = {}
        e_stress = {}
        if SG.nSG == 1:
            for i in range(SG.nelem):
                strain = []
                stress = []
                for j in range(SG.Element[i].total_node):
                    line = f.readline().split()
                    strain += [map(float, line[1:7])]
                    stress += [map(float, line[7:13])]
                e_strain[i + 1] = strain
                e_stress[i + 1] = stress
        elif SG.nSG == 2:
            for i in range(SG.nelem):
                strain = []
                stress = []
                for j in range(SG.Element[i].total_node):
                    line = f.readline().split()
                    strain += [map(float, line[2:8])]
                    stress += [map(float, line[8:14])]
                e_strain[i + 1] = strain
                e_stress[i + 1] = stress
        elif SG.nSG == 3:
            for i in range(SG.nelem):
                strain = []
                stress = []
                for j in range(SG.Element[i].total_node):
                    line = f.readline().split()
                    strain += [map(float, line[3:9])]
                    stress += [map(float, line[9:15])]
                e_strain[i + 1] = strain
                e_stress[i + 1] = stress

    # Generate Gmsh input file *.msh
    with open(SGFileSystem.dir_file_name_msh, 'w') as f:

        # ----- MeshFormat --------------------
        f.write('$MeshFormat\n')
        f.write('2.2 0 8\n')
        f.write('$EndMeshFormat\n')

        # ----- Nodes ---------------------
        # node_id x y z
        f.write('$Nodes\n')
        if SG.nSG == 1 and SG.PlateModel:  # 1D SG for plate model
            f.write(str(SG.nnode*2) + '\n')
            total_thickness = SG.Node[-1].coordinate[2] - SG.Node[0].coordinate[2]
            for i in range(SG.nnode):
                y1, y2, y3 = SG.Node[i].coordinate
                line = str(i+1) + ''.join([' %.5e' % x for x in [y1, y2, y3]])
                f.write(line + '\n')
            for i in range(SG.nnode):
                y1, y2, y3 = SG.Node[i].coordinate
                line = str(SG.nnode+i+1) + ''.join([' %.5e' % x for x in [y1, y2+5*total_thickness, y3]])
                f.write(line + '\n')
        if SG.nSG == 1 and SG.SolidModel:  # 1D SG for solid model
            f.write(str(SG.nnode*4) + '\n')
            total_thickness = SG.Node[-1].coordinate[2] - SG.Node[0].coordinate[2]
            for i in range(SG.nnode):
                y1, y2, y3 = SG.Node[i].coordinate
                line = str(i+1) + ''.join([' %.5e' % x for x in [y1, y2, y3]])
                f.write(line + '\n')
            for i in range(SG.nnode):
                y1, y2, y3 = SG.Node[i].coordinate
                line = str(SG.nnode+i+1) + ''.join([' %.5e' % x for x in [y1, y2+total_thickness, y3]])
                f.write(line + '\n')
            for i in range(SG.nnode):
                y1, y2, y3 = SG.Node[i].coordinate
                line = str(2*SG.nnode+i+1) + ''.join([' %.5e' % x for x in [y1-total_thickness, y2+total_thickness, y3]])
                f.write(line + '\n')
            for i in range(SG.nnode):
                y1, y2, y3 = SG.Node[i].coordinate
                line = str(3*SG.nnode+i+1) + ''.join([' %.5e' % x for x in [y1-total_thickness, y2, y3]])
                f.write(line + '\n')
        else:  # 2D or 3D SG
            f.write(str(SG.nnode) + '\n')
            for i in range(SG.nnode):
                line = str(i+1) + ''.join([' %.5e' % x for x in SG.Node[i].coordinate])
                f.write(line + '\n')
        f.write('$EndNodes' + '\n')

        # ----- Elements ---------------------
        # elem_id elem_type number_of_tages (default2) physical_entity geometrical_entity node-number-list
        # element type in Gmsh
        # 2 3-node triangle
        # 3 4-node quadrangle
        # 4 4-node tetrahedron.
        # 5 8-node hexahedron
        # 9 6-node second order triangle (3 nodes associated with the vertices and 3 with the edges)
        # 11 10-node second order tetrahedron (4 nodes associated with the vertices and 6 with the edges)
        # 16 8-node second order quadrangle (4 nodes associated with the vertices and 4 with the edges)
        # 17 20-node second order hexahedron (8 nodes associated with the vertices and 12 with the edges)
        if SG.nSG != 1:
            for i in range(SG.nelem):
                if SG.Element[i].elementType == 'kTri3':
                    SG.Element[i].Gmsh_elementType = 2
                elif SG.Element[i].elementType == 'kQuad4':
                    SG.Element[i].Gmsh_elementType = 3
                elif SG.Element[i].elementType == 'kTri6':
                    SG.Element[i].Gmsh_elementType = 9
                elif SG.Element[i].elementType == 'kQuad8':
                    SG.Element[i].Gmsh_elementType = 16
                elif SG.Element[i].elementType == 'kTet4':
                    SG.Element[i].Gmsh_elementType = 4
                elif SG.Element[i].elementType == 'kHex8':
                    SG.Element[i].Gmsh_elementType = 5
                elif SG.Element[i].elementType == 'kTet10':
                    SG.Element[i].Gmsh_elementType = 11
                elif SG.Element[i].elementType == 'kHex20':
                    SG.Element[i].Gmsh_elementType= 17

        f.write('$Elements' + '\n')
        if SG.nSG == 1 and SG.PlateModel:  # 1D SG for plate model
            f.write(str(SG.nnode-1) + '\n')
            for i in range(SG.nnode-1):
                line = [i+1, 3, 2, 99, 99]
                line.extend([i+1, i+SG.nnode+1, i+SG.nnode+2, i+2])
                f.write(str(line).replace(',', '').replace('[', '').replace(']', '') + '\n')
        elif SG.nSG == 1 and SG.SolidModel:  # 1D SG for solid model
            f.write(str(SG.nnode-1) + '\n')
            for i in range(SG.nnode-1):
                line = [i+1, 5, 2, 99, 99]
                line.extend([i+1, i+SG.nnode+1, i+2*SG.nnode+1, i+3*SG.nnode+1, i+2, i+SG.nnode+2, i+2*SG.nnode+2, i+3*SG.nnode+2])
                f.write(str(line).replace(',', '').replace('[', '').replace(']', '') + '\n')
        else:  # 2D or 3D SG
            f.write(str(SG.nelem) + '\n')
            for i in range(SG.nelem):
                line = [i+1, SG.Element[i].Gmsh_elementType, 2, SG.Element[i].material_id, SG.Element[i].material_id]
                line.extend([x for x in SG.Element[i].connectivity if x > 0])
                f.write(str(line).replace(',', '').replace('[', '').replace(']', '') + '\n')
        f.write('$EndElements' + '\n')

        # ----- Node Data ---------------------
        f.write('$NodeData' + '\n')
        f.write('1\n')
        f.write('"U-Magnitude"\n')
        f.write('1\n0\n3\n0\n1\n')
        if SG.nSG == 1 and SG.PlateModel:  # 1D SG for plate model
            f.write(str(SG.nnode*2) + '\n')
            for i in range(SG.nnode):
                u_mag = (n_dis[i][1]**2 + n_dis[i][2]**2 + n_dis[i][3]**2)**(1 / 2.0)
                line = str(i+1) + ''.join([' %.5e' % u_mag])
                f.write(line + '\n')
            for i in range(SG.nnode):
                u_mag = (n_dis[i][1]**2 + n_dis[i][2]**2 + n_dis[i][3]**2)**(1 / 2.0)
                line = str(SG.nnode+i+1) + ''.join([' %.5e' % u_mag])
                f.write(line + '\n')
        if SG.nSG == 1 and SG.SolidModel:  # 1D SG for solid model
            f.write(str(SG.nnode*4) + '\n')
            for i in range(SG.nnode):
                u_mag = (n_dis[i][1]**2 + n_dis[i][2]**2 + n_dis[i][3]**2)**(1 / 2.0)
                line = str(i+1) + ''.join([' %.5e' % u_mag])
                f.write(line + '\n')
            for i in range(SG.nnode):
                u_mag = (n_dis[i][1]**2 + n_dis[i][2]**2 + n_dis[i][3]**2)**(1 / 2.0)
                line = str(SG.nnode+i+1) + ''.join([' %.5e' % u_mag])
                f.write(line + '\n')
            for i in range(SG.nnode):
                u_mag = (n_dis[i][1]**2 + n_dis[i][2]**2 + n_dis[i][3]**2)**(1 / 2.0)
                line = str(2*SG.nnode+i+1) + ''.join([' %.5e' % u_mag])
                f.write(line + '\n')
            for i in range(SG.nnode):
                u_mag = (n_dis[i][1]**2 + n_dis[i][2]**2 + n_dis[i][3]**2)**(1 / 2.0)
                line = str(3*SG.nnode+i+1) + ''.join([' %.5e' % u_mag])
                f.write(line + '\n')
        else:  # 2D or 3D SG
            f.write(str(SG.nnode) + '\n')
            for i in range(SG.nnode):
                u_mag = (n_dis[i][1]**2 + n_dis[i][2]**2 + n_dis[i][3]**2)**(1 / 2.0)
                line = str(i+1) + ''.join([' %.5e' % u_mag])
                f.write(line + '\n')
        f.write('$EndNodeData' + '\n')

        for n in range(3):
            f.write('$NodeData' + '\n')
            f.write('1\n')
            f.write('"U' + str(n+1) + '"\n')
            f.write('1\n0\n3\n0\n1\n')
            if SG.nSG == 1 and SG.PlateModel:  # 1D SG for plate model
                f.write(str(SG.nnode*2) + '\n')
                for i in range(SG.nnode):
                    line = str(i+1) + ''.join([' %.5e' % n_dis[i][n+1]])
                    f.write(line + '\n')
                for i in range(SG.nnode):
                    line = str(SG.nnode+i+1) + ''.join([' %.5e' % n_dis[i][n+1]])
                    f.write(line + '\n')
            if SG.nSG == 1 and SG.SolidModel:  # 1D SG for solid model
                f.write(str(SG.nnode*4) + '\n')
                for i in range(SG.nnode):
                    line = str(i+1) + ''.join([' %.5e' % n_dis[i][n+1]])
                    f.write(line + '\n')
                for i in range(SG.nnode):
                    line = str(SG.nnode+i+1) + ''.join([' %.5e' % n_dis[i][n+1]])
                    f.write(line + '\n')
                for i in range(SG.nnode):
                    line = str(2*SG.nnode+i+1) + ''.join([' %.5e' % n_dis[i][n+1]])
                    f.write(line + '\n')
                for i in range(SG.nnode):
                    line = str(3*SG.nnode+i+1) + ''.join([' %.5e' % n_dis[i][n+1]])
                    f.write(line + '\n')
            else:  # 2D or 3D SG
                f.write(str(SG.nnode) + '\n')
                for i in range(SG.nnode):
                    line = str(i+1) + ''.join([' %.5e' % n_dis[i][n+1]])
                    f.write(line + '\n')
            f.write('$EndNodeData' + '\n')

        # ----- Element Data ---------------------

        notation_dictionary = {0:'11', 1:'22', 2:'33', 3:'23', 4:'13', 5:'12'}

        for n in range(6):
            f.write('$ElementNodeData' + '\n')
            f.write('1\n')
            f.write('"E' + notation_dictionary[n] + '"\n')
            f.write('1\n0\n3\n0\n1\n')
            if SG.nSG == 1 and SG.PlateModel:
                f.write(str(SG.nnode - 1) + '\n')
                for i in range(SG.nelem):
                    for j in range(4):
                        temp = i*4 + j + 1
                        bot = e_strain[i + 1][j][n]
                        top = e_strain[i + 1][j+1][n]
                        line = str(temp) + ' ' + str(4) + ''.join([' %.5e' % x for x in [bot, bot, top, top]])
                        f.write(line + '\n')
            elif SG.nSG == 1 and SG.SolidModel:
                f.write(str(SG.nnode - 1) + '\n')
                for i in range(SG.nelem):
                    for j in range(4):
                        temp = i*4 + j + 1
                        bot = e_strain[i + 1][j][n]
                        top = e_strain[i + 1][j+1][n]
                        line = str(temp) + ' ' + str(8) + ''.join([' %.5e' % x for x in [bot, bot, bot, bot, top, top, top, top]])
                        f.write(line + '\n')
            else:
                f.write(str(SG.nelem) + '\n')
                for i in range(SG.nelem):
                    strain = []
                    for j in range(SG.Element[i].total_node):
                        strain.append(e_strain[i + 1][j][n])
                    line = str(i+1) + ' ' + str(SG.Element[i].total_node) + ''.join([' %.5e' % x for x in strain])
                    f.write(line + '\n')
            f.write('$EndElementNodeData' + '\n')

        for n in range(6):
            f.write('$ElementNodeData' + '\n')
            f.write('1\n')
            f.write('"S' + notation_dictionary[n] + '"\n')
            f.write('1\n0\n3\n0\n1\n')
            if SG.nSG == 1 and SG.PlateModel:
                f.write(str(SG.nnode - 1) + '\n')
                for i in range(SG.nelem):
                    for j in range(4):
                        temp = i*4 + j + 1
                        bot = e_stress[i + 1][j][n]
                        top = e_stress[i + 1][j+1][n]
                        line = str(temp) + ' ' + str(4) + ''.join([' %.5e' % x for x in [bot, bot, top, top]])
                        f.write(line + '\n')
            elif SG.nSG == 1 and SG.SolidModel:
                f.write(str(SG.nnode - 1) + '\n')
                for i in range(SG.nelem):
                    for j in range(4):
                        temp = i*4 + j + 1
                        bot = e_stress[i + 1][j][n]
                        top = e_stress[i + 1][j+1][n]
                        line = str(temp) + ' ' + str(8) + ''.join([' %.5e' % x for x in [bot, bot, bot, bot, top, top, top, top]])
                        f.write(line + '\n')
            else:  # 2D or 3D SG
                f.write(str(SG.nelem) + '\n')
                for i in range(SG.nelem):
                    stress = []
                    for j in range(SG.Element[i].total_node):
                        stress.append(e_stress[i + 1][j][n])
                    line = str(i+1) + ' ' + str(SG.Element[i].total_node) + ''.join([' %.5e' % x for x in stress])
                    f.write(line + '\n')
            f.write('$EndElementNodeData' + '\n')

    # installation directary. Example:
    # 'C:\Program Files\ANSYS Inc\v192\Addins\ACT\extensions\SwiftComp'
    # 'C:\Users\banghua\AppData\Roaming\Ansys\v192\ACT\extensions\SwiftComp'
    install_dir = ExtAPI.ExtensionManager.CurrentExtension.InstallDir
    Gmsh_dir = install_dir + '\\gmsh\\'

    # Create .geo file for Gmsh
    with open(SGFileSystem.dir_file_name_geo, 'w') as f:
        f.write('Merge "' + SGFileSystem.file_name_msh + '";\n')
        if SG.nSG == 1 and SG.PlateModel:
            f_geo = open(Gmsh_dir + 'SG1DPlate.geo', 'r')
            f.write(f_geo.read())
            f_geo.close()
        elif SG.nSG == 1 and SG.SolidModel:
            f_geo = open(Gmsh_dir + 'SG1DSolid.geo', 'r')
            f.write(f_geo.read())
            f_geo.close()
        elif SG.nSG == 2:
            f_geo = open(Gmsh_dir + 'SG2D.geo', 'r')
            f.write(f_geo.read())
            f_geo.close()
        elif SG.nSG == 3:
            f_geo = open(Gmsh_dir + 'SG3D.geo', 'r')
            f.write(f_geo.read())
            f_geo.close()

    # use Gmsh to visualize the result
    if utilities.is_os_64bit():  # 64 bit OS
        command = [Gmsh_dir + 'gmsh64.exe', SGFileSystem.file_name_geo]
    else:  # 32 bit OS
        command = [Gmsh_dir + 'gmsh32.exe', SGFileSystem.file_name_geo]

    subprocess.Popen(command, cwd=SGFileSystem.user_dir, shell=True)

    return True