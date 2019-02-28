import subprocess
import time
import os
import pickle

import errorcheck
import utilities

import sg
import sg_filesystem
import sg_result



def SwiftCompDehomogenizationInput(arg):
    '''Create dehomogenization input file'''

    ExtAPI, macro_displacement, macro_rotation, method, macro_strain_stress = arg[0], arg[1], arg[2], arg[3], arg[4]

    SGFileSystem = sg_filesystem.SGFileSystem(ExtAPI)

    SGResult = sg_result.SGResult()
    with open(SGFileSystem.user_dir + 'SGResult.pickle', 'rb') as f:
        SGResult = pickle.load(f)

    # Check whether there is *.sc file or not. If not, raise an error
    if errorcheck.noSCFile(ExtAPI) or errorcheck.noKFile(ExtAPI):
        return False

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
        if method == 'Generalized Strain':
            utilities.writeFormat(f, 'd', [1])
        else: 
            utilities.writeFormat(f, 'd', [0])
        f.write('\n')

        # ----- Write macrogeneralized strains --------------------
        if SGResult.BeamModel:
            if SGResult.BeamModel.submodel == 0:    
                utilities.writeFormat(f, 'E' * 4, macro_strain_stress)
            elif SGResult.BeamModel.submodel == 1:    
                utilities.writeFormat(f, 'E' * 6, macro_strain_stress)
        elif SGResult.PlateModel:
            if SGResult.PlateModel.submodel == 0:   
                utilities.writeFormat(f, 'E' * 6, macro_strain_stress)
            else:
                utilities.writeFormat(f, 'E' * 8, macro_strain_stress)
        elif SGResult.SolidModel:
            utilities.writeFormat(f, 'E' * 6, macro_strain_stress)
        f.write('\n')

    ExtAPI.Log.WriteMessage("Creating dehomogenization input file finished.")

    return True


def SwiftCompDehomogenizationRun(arg):
    '''Run dehomogenization'''

    ExtAPI = arg

    SGFileSystem = sg_filesystem.SGFileSystem(ExtAPI)

    SGResult = sg_result.SGResult()
    with open(SGFileSystem.user_dir + 'SGResult.pickle', 'rb') as f:
        SGResult = pickle.load(f)

    SG = sg.StructureGenome()
    with open(SGFileSystem.user_dir + 'SG.pickle', 'rb') as f:
        SG = pickle.load(f)

    # Obtain SwiftComp excution command

    # ================================================================
    # arg1: The complete input file name (including the extension)
    # ================================================================
    arg1 = SGFileSystem.file_name_sc

    # ================================================================
    # arg2: The macroscopic model to be constructed
    # ----------------------------------------------------------------
    # 1D for a beam model
    # 2D for a plate/shell model
    # 3D for a 3D model
    # ================================================================
    if SG.BeamModel:
        arg2 = '1D'
    elif SG.PlateModel:
        arg2 = '2D'
    elif SG.SolidModel:
        arg2 = '3D'

    # ================================================================
    # arg3: homogenization, dehomogenization, or failure analysis
    # ----------------------------------------------------------------
    # H for homogenization
    # L for dehomogenization
    # HA for homogenization of aperiodic structures
    # LA for dehomogenization of aperiodic structures
    # F for initial failure strength analysis
    # FI for initial failure indexes and strength ratios
    # FE for initial failure envelope
    # ================================================================
    if not SG.aperiodic:
        arg3 = 'L'
    else:
        arg3 = 'LA'

    # ================================================================
    # arg4: The version of SwiftComp is running:
    # ----------------------------------------------------------------
    # B for standard version
    # P for professional version
    # No arguments for parallel version
    # ================================================================
    arg4 = ''

    dehom_time_start = time.clock()

    # Run dehomogenization! save stdout to a file named temp
    command = ['SwiftComp', arg1, arg2, arg3, arg4, '>', SGFileSystem.user_dir+'temp']
    exitCode = subprocess.call(command, cwd=SGFileSystem.user_dir, shell=True)
    if exitCode != 0:
        return False

    dehom_time_end = time.clock()

    # Dehomogenization time
    SGResult.dehomTime = dehom_time_end - dehom_time_start

    # Get standard output
    with open(SGFileSystem.user_dir + 'temp') as f:
        SGResult.dehommStdout = f.read()
    os.remove(SGFileSystem.user_dir + 'temp')

    # Check whether the dehomogenization is successful or not.
    if errorcheck.dehomNotSuccessful(ExtAPI, SGResult.dehommStdout):
        return False

    # write solve.out file
    with open('solve.out', 'w') as f:
        f.write(SGResult.dehommStdout)

    try:
        # set displayment
        SGResult.setDisplacement(SGFileSystem)

        # set stress
        SGResult.setStress(SGFileSystem)

        # set strain
        SGResult.setStrain(SGFileSystem)

    except:
        ExtAPI.Log.WriteMessage("set displacement/stress/strain false")
        return False

    # save updated SGResult
    with open(SGFileSystem.user_dir + 'SGResult.pickle', 'wb') as f:
        pickle.dump(SGResult, f)


    if SG.nSG == 1:
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
            f.write('$EndNodes' + '\n')

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

        # use Gmsh to visualize the result
        if utilities.is_os_64bit():  # 64 bit OS
            command = [Gmsh_dir + 'gmsh64.exe', SGFileSystem.file_name_geo]
        else:  # 32 bit OS
            command = [Gmsh_dir + 'gmsh32.exe', SGFileSystem.file_name_geo]

        subprocess.Popen(command, cwd=SGFileSystem.user_dir, shell=True)


    ExtAPI.Log.WriteMessage("Dehomogenization finished.")
    ExtAPI.Log.WriteMessage("Dehomogenization time: " + str(SGResult.dehomTime))

    return True


def updateBeamModelDehomogenizationSetting(load, currentExtractResult):

    load.Properties["Macro Displacements/v1"].Value = currentExtractResult.macro_displacement[0]
    load.Properties["Macro Displacements/v2"].Value = currentExtractResult.macro_displacement[1]
    load.Properties["Macro Displacements/v3"].Value = currentExtractResult.macro_displacement[2]

    load.Properties["Macro Rotations/C11"].Value = currentExtractResult.macro_rotation[0][0]
    load.Properties["Macro Rotations/C12"].Value = currentExtractResult.macro_rotation[0][1]
    load.Properties["Macro Rotations/C13"].Value = currentExtractResult.macro_rotation[0][2]
    load.Properties["Macro Rotations/C21"].Value = currentExtractResult.macro_rotation[1][0]
    load.Properties["Macro Rotations/C22"].Value = currentExtractResult.macro_rotation[1][1]
    load.Properties["Macro Rotations/C23"].Value = currentExtractResult.macro_rotation[1][2]
    load.Properties["Macro Rotations/C31"].Value = currentExtractResult.macro_rotation[2][0]
    load.Properties["Macro Rotations/C32"].Value = currentExtractResult.macro_rotation[2][1]
    load.Properties["Macro Rotations/C33"].Value = currentExtractResult.macro_rotation[2][2]

    load.Properties["Macro Generalized StrainStress/Macro Model/Method1/epsilon11"].Value = currentExtractResult.macro_strain[0]
    load.Properties["Macro Generalized StrainStress/Macro Model/Method1/kappa11"].Value   = currentExtractResult.macro_strain[3]
    load.Properties["Macro Generalized StrainStress/Macro Model/Method1/kappa12"].Value   = currentExtractResult.macro_strain[4]
    load.Properties["Macro Generalized StrainStress/Macro Model/Method1/kappa13"].Value   = currentExtractResult.macro_strain[5]

    load.Properties["Macro Generalized StrainStress/Macro Model/Method1/F1"].Value = currentExtractResult.macro_stress[0]
    load.Properties["Macro Generalized StrainStress/Macro Model/Method1/M1"].Value = currentExtractResult.macro_stress[3]
    load.Properties["Macro Generalized StrainStress/Macro Model/Method1/M2"].Value = currentExtractResult.macro_stress[4]
    load.Properties["Macro Generalized StrainStress/Macro Model/Method1/M3"].Value = currentExtractResult.macro_stress[5] 

    load.Properties["Macro Generalized StrainStress/Macro Model/Method2/epsilon11"].Value = currentExtractResult.macro_strain[0]
    load.Properties["Macro Generalized StrainStress/Macro Model/Method2/gamma12"].Value   = currentExtractResult.macro_strain[1]
    load.Properties["Macro Generalized StrainStress/Macro Model/Method2/gamma13"].Value   = currentExtractResult.macro_strain[2]
    load.Properties["Macro Generalized StrainStress/Macro Model/Method2/kappa11"].Value   = currentExtractResult.macro_strain[3]
    load.Properties["Macro Generalized StrainStress/Macro Model/Method2/kappa12"].Value   = currentExtractResult.macro_strain[4]
    load.Properties["Macro Generalized StrainStress/Macro Model/Method2/kappa13"].Value   = currentExtractResult.macro_strain[5]

    load.Properties["Macro Generalized StrainStress/Macro Model/Method2/F1"].Value = currentExtractResult.macro_stress[0]
    load.Properties["Macro Generalized StrainStress/Macro Model/Method2/F2"].Value = currentExtractResult.macro_stress[1]
    load.Properties["Macro Generalized StrainStress/Macro Model/Method2/F3"].Value = currentExtractResult.macro_stress[2]
    load.Properties["Macro Generalized StrainStress/Macro Model/Method2/M1"].Value = currentExtractResult.macro_stress[3]
    load.Properties["Macro Generalized StrainStress/Macro Model/Method2/M2"].Value = currentExtractResult.macro_stress[4]
    load.Properties["Macro Generalized StrainStress/Macro Model/Method2/M3"].Value = currentExtractResult.macro_stress[5] 


def updatePlateModelDehomogenizationSetting(load, currentExtractResult):

    load.Properties["Macro Displacements/v1"].Value = currentExtractResult.macro_displacement[0]
    load.Properties["Macro Displacements/v2"].Value = currentExtractResult.macro_displacement[1]
    load.Properties["Macro Displacements/v3"].Value = currentExtractResult.macro_displacement[2]

    load.Properties["Macro Rotations/C11"].Value = currentExtractResult.macro_rotation[0][0]
    load.Properties["Macro Rotations/C12"].Value = currentExtractResult.macro_rotation[0][1]
    load.Properties["Macro Rotations/C13"].Value = currentExtractResult.macro_rotation[0][2]
    load.Properties["Macro Rotations/C21"].Value = currentExtractResult.macro_rotation[1][0]
    load.Properties["Macro Rotations/C22"].Value = currentExtractResult.macro_rotation[1][1]
    load.Properties["Macro Rotations/C23"].Value = currentExtractResult.macro_rotation[1][2]
    load.Properties["Macro Rotations/C31"].Value = currentExtractResult.macro_rotation[2][0]
    load.Properties["Macro Rotations/C32"].Value = currentExtractResult.macro_rotation[2][1]
    load.Properties["Macro Rotations/C33"].Value = currentExtractResult.macro_rotation[2][2]

    load.Properties["Macro Generalized StrainStress/Macro Model/Method1/epsilon11"].Value  = currentExtractResult.macro_strain[0]
    load.Properties["Macro Generalized StrainStress/Macro Model/Method1/epsilon22"].Value  = currentExtractResult.macro_strain[1]
    load.Properties["Macro Generalized StrainStress/Macro Model/Method1/2epsilon12"].Value = currentExtractResult.macro_strain[2]
    load.Properties["Macro Generalized StrainStress/Macro Model/Method1/kappa11"].Value    = currentExtractResult.macro_strain[3]
    load.Properties["Macro Generalized StrainStress/Macro Model/Method1/kappa22"].Value    = currentExtractResult.macro_strain[4]
    load.Properties["Macro Generalized StrainStress/Macro Model/Method1/2kappa12"].Value   = currentExtractResult.macro_strain[5]

    load.Properties["Macro Generalized StrainStress/Macro Model/Method1/N11"].Value = currentExtractResult.macro_stress[0]
    load.Properties["Macro Generalized StrainStress/Macro Model/Method1/N22"].Value = currentExtractResult.macro_stress[1]
    load.Properties["Macro Generalized StrainStress/Macro Model/Method1/N12"].Value = currentExtractResult.macro_stress[2]
    load.Properties["Macro Generalized StrainStress/Macro Model/Method1/M11"].Value = currentExtractResult.macro_stress[3]
    load.Properties["Macro Generalized StrainStress/Macro Model/Method1/M22"].Value = currentExtractResult.macro_stress[4]
    load.Properties["Macro Generalized StrainStress/Macro Model/Method1/M12"].Value = currentExtractResult.macro_stress[5] 

    load.Properties["Macro Generalized StrainStress/Macro Model/Method2/epsilon11"].Value  = currentExtractResult.macro_strain[0]
    load.Properties["Macro Generalized StrainStress/Macro Model/Method2/epsilon22"].Value  = currentExtractResult.macro_strain[1]
    load.Properties["Macro Generalized StrainStress/Macro Model/Method2/2epsilon12"].Value = currentExtractResult.macro_strain[2]
    load.Properties["Macro Generalized StrainStress/Macro Model/Method2/kappa11"].Value    = currentExtractResult.macro_strain[3]
    load.Properties["Macro Generalized StrainStress/Macro Model/Method2/kappa22"].Value    = currentExtractResult.macro_strain[4]
    load.Properties["Macro Generalized StrainStress/Macro Model/Method2/2kappa12"].Value   = currentExtractResult.macro_strain[5]
    load.Properties["Macro Generalized StrainStress/Macro Model/Method2/gamma13"].Value    = currentExtractResult.macro_strain[6]
    load.Properties["Macro Generalized StrainStress/Macro Model/Method2/gamma23"].Value    = currentExtractResult.macro_strain[7]

    load.Properties["Macro Generalized StrainStress/Macro Model/Method2/N11"].Value = currentExtractResult.macro_stress[0]
    load.Properties["Macro Generalized StrainStress/Macro Model/Method2/N22"].Value = currentExtractResult.macro_stress[1]
    load.Properties["Macro Generalized StrainStress/Macro Model/Method2/N12"].Value = currentExtractResult.macro_stress[2]
    load.Properties["Macro Generalized StrainStress/Macro Model/Method2/M11"].Value = currentExtractResult.macro_stress[3]
    load.Properties["Macro Generalized StrainStress/Macro Model/Method2/M22"].Value = currentExtractResult.macro_stress[4]
    load.Properties["Macro Generalized StrainStress/Macro Model/Method2/M12"].Value = currentExtractResult.macro_stress[5] 
    load.Properties["Macro Generalized StrainStress/Macro Model/Method2/N13"].Value = currentExtractResult.macro_stress[6] 
    load.Properties["Macro Generalized StrainStress/Macro Model/Method2/N23"].Value = currentExtractResult.macro_stress[7] 


def updateSolidModelDehomogenizationSetting(load, currentExtractResult):

    load.Properties["Macro Displacements/v1"].Value = currentExtractResult.macro_displacement[0]
    load.Properties["Macro Displacements/v2"].Value = currentExtractResult.macro_displacement[1]
    load.Properties["Macro Displacements/v3"].Value = currentExtractResult.macro_displacement[2]

    load.Properties["Macro Rotations/C11"].Value = currentExtractResult.macro_rotation[0][0]
    load.Properties["Macro Rotations/C12"].Value = currentExtractResult.macro_rotation[0][1]
    load.Properties["Macro Rotations/C13"].Value = currentExtractResult.macro_rotation[0][2]
    load.Properties["Macro Rotations/C21"].Value = currentExtractResult.macro_rotation[1][0]
    load.Properties["Macro Rotations/C22"].Value = currentExtractResult.macro_rotation[1][1]
    load.Properties["Macro Rotations/C23"].Value = currentExtractResult.macro_rotation[1][2]
    load.Properties["Macro Rotations/C31"].Value = currentExtractResult.macro_rotation[2][0]
    load.Properties["Macro Rotations/C32"].Value = currentExtractResult.macro_rotation[2][1]
    load.Properties["Macro Rotations/C33"].Value = currentExtractResult.macro_rotation[2][2]

    load.Properties["Macro Generalized StrainStress/Method/epsilon11"].Value  = currentExtractResult.macro_strain[0]
    load.Properties["Macro Generalized StrainStress/Method/epsilon22"].Value  = currentExtractResult.macro_strain[1]
    load.Properties["Macro Generalized StrainStress/Method/epsilon33"].Value  = currentExtractResult.macro_strain[2]
    load.Properties["Macro Generalized StrainStress/Method/2epsilon23"].Value = currentExtractResult.macro_strain[3]
    load.Properties["Macro Generalized StrainStress/Method/2epsilon13"].Value = currentExtractResult.macro_strain[4]
    load.Properties["Macro Generalized StrainStress/Method/2epsilon12"].Value = currentExtractResult.macro_strain[5]

    load.Properties["Macro Generalized StrainStress/Method/sigma11"].Value    = currentExtractResult.macro_stress[0]
    load.Properties["Macro Generalized StrainStress/Method/sigma22"].Value    = currentExtractResult.macro_stress[1]
    load.Properties["Macro Generalized StrainStress/Method/sigma33"].Value    = currentExtractResult.macro_stress[2]
    load.Properties["Macro Generalized StrainStress/Method/sigma23"].Value    = currentExtractResult.macro_stress[3]
    load.Properties["Macro Generalized StrainStress/Method/sigma13"].Value    = currentExtractResult.macro_stress[4]
    load.Properties["Macro Generalized StrainStress/Method/sigma12"].Value    = currentExtractResult.macro_stress[5] 