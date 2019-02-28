# import visual

import subprocess
import os

import shutil
import scdehomfun
import errorcheck
import utilities


##############################################################################
# # visualization
##############################################################################
#
# def Visualization(currentAnalysis):
#     ExtAPI.Log.WriteMessage("Creating Visualization in tree...")
#     currentAnalysis.CreateResultObject("Visualization")
#
#
# def visualizationLocation(result, step, collector):
#
#     status = visual.visualizationTemp(ExtAPI, result, step, collector)
#
#     if status == 0:
#         return True
#     else:
#         return False


def visualizationTemp(ExtAPI, result, step, collector):
    arg = [ExtAPI, result, step, collector]
    status = ExtAPI.Application.InvokeUIThread(visualMain, arg)
    return status


def visualMain(arg):
    ExtAPI, result, stepInfo, collector = arg[0], arg[1], arg[2], arg[3]

    elem_ids = collector.Ids

    analysis = result.Analysis
    reader = analysis.GetResultsData()
    mesh = analysis.MeshData

    deformation = reader.GetResult("U")
    strain = reader.GetResult("EPEL")

    temp = [0] * 6

    for i in elem_ids:
        tensor = strain.GetElementValues(i)
        elem_node = mesh.ElementById(i).CornerNodeCount
        for j in range(6):
            for k in range(elem_node):
                temp[j] += tensor[j + k * 6]

    temp_strain = [x / len(elem_ids) for x in temp]
    # 11 22 33 12 23 13
    # 11 22 33 23 13 12
    solid_strain = [temp_strain[0], temp_strain[1], temp_strain[2], temp_strain[4], temp_strain[5], temp_strain[3]]

    ##################################################################
    # Creating dehomogenization input file
    ##################################################################

    # macro displacement
    mac_dis = [0.] * 3

    # macro rotation
    mac_rot = [1., 0., 0., 0., 1., 0., 0., 0., 1.]

    # Get various directory
    [work_dir, user_dir] = utilities.getDirectory(ExtAPI)

    # Get various filename
    [file_name, file_name_sc, file_name_sc_k, file_name_sc_glb, file_name_sc_u, file_name_sc_sn] = utilities.getFileName(user_dir)

    # Check whether there is *.sc file or not. If not, raise an error
    status = errorcheck.checkSCFile(ExtAPI)
    if status != 0:
        return status

    # Get macro_model
    macro_model = dehomfun.getMacroModel(user_dir, file_name_sc)

    # Generate SwiftComp dehomogenization input file *.sc.glb
    with open(user_dir + file_name_sc_glb, 'w') as sc_target:

        # ----- Write macro displacements --------------------
        utilities.writeFormat(sc_target, 'EEE', mac_dis)
        sc_target.write('\n')

        # ----- Write macro rotations --------------------
        utilities.writeFormat(sc_target, 'EEE', mac_rot[0:3])
        sc_target.write('\n')
        utilities.writeFormat(sc_target, 'EEE', mac_rot[3:6])
        sc_target.write('\n')
        utilities.writeFormat(sc_target, 'EEE', mac_rot[6:9])
        sc_target.write('\n')

        # ----- Write macrogeneralized strains --------------------
        if macro_model == 0:
            utilities.writeFormat(sc_target, 'E' * 4, beam_strain)
        elif macro_model == 1:
            utilities.writeFormat(sc_target, 'E' * 6, plate_strain)
        elif macro_model == 2:
            utilities.writeFormat(sc_target, 'E' * 6, solid_strain)

        sc_target.write('\n')

    ##################################################################
    # Run dehomogenization
    ##################################################################

    # Obtain SwiftComp excution command

    # ================================================================
    # arg1: The complete input file name (including the extension)
    # ================================================================
    arg1 = file_name_sc

    # ================================================================
    # arg2: The macroscopic model to be constructed
    # ----------------------------------------------------------------
    # 1D for a beam model
    # 2D for a plate/shell model
    # 3D for a 3D model
    # ================================================================
    if macro_model == 0:
        arg2 = '1D'
    elif macro_model == 1:
        arg2 = '2D'
    elif macro_model == 2:
        arg2 = '3D'

    # ================================================================
    # arg3: homogenization, dehomogenization, or failure analysis
    # ----------------------------------------------------------------
    # H for homogenization
    # L for dehomogenization
    # F for failure analysis
    # FA for failure analysis with average field
    # HA for homogenization of aperiodic structures
    # LA for dehomogenization of aperiodic structures
    # ================================================================
    # Get aperiodic. If aperiodic == 0, no. If aperiodic != 1, yes
    # Use: getAperiodic(ExtAPI)
    # Return: aperiodic
    aperiodic = dehomfun.getAperiodic(user_dir, file_name_sc)
    if aperiodic == 0:
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

    # Run Dehomogenization!
    sc_dehom = subprocess.Popen(['powershell', 'SwiftComp', arg1, arg2, arg3, arg4,
                                 '|', 'tee', 'temp'], cwd=user_dir)
    sc_dehom.wait()

    # Get standard output
    f = open(user_dir + 'temp')
    sc_dehom_stdout = f.read()
    f.close()
    os.remove(user_dir + 'temp')

    ##################################################################
    # Read *.sc, *.u, *.sn file
    ##################################################################
    # use *.sc.ech file for find macro_model and aperiodic
    file_name_sc_ech = file_name_sc + '.ech'
    with open(user_dir + file_name_sc_ech, 'r') as f:
        several_lines = f.read(1000)
        if 'Beam' in several_lines:
            macro_model = 0
        elif 'Plate' in several_lines:
            macro_model = 1
        else:
            macro_model = 2

        if 'Aperiodic' in several_lines:
            aperiodic = 1
        else:
            aperiodic = 0

    # read *.sc file
    with open(user_dir + file_name_sc, 'r') as f:
        # ----- read extra inputs for dimensionally reducible structures -------
        if macro_model == 0:
            line = f.readline().split()
            submodel = int(line[0])
            f.readline()

            line = f.readline().split()
            beam_ini_cur = map(float, [line[0], line[1], line[2]])
            f.readline()

            line = f.readline().split()
            beam_obli = map(float, [line[0], line[1]])
            f.readline()

        elif macro_model == 1:
            line = f.readline().split()
            submodel = int(line[0])
            f.readline()

            line = f.readline().split()
            plate_ini_cur = map(float, [line[0], line[1]])
            f.readline()

        elif macro_model == 2:
            pass

        # ----- Read problem control parameters --------------------
        line = f.readline().split()
        [analysis, elem_flag, trans_flag, temp_flag] = map(int, [line[0], line[1], line[2], line[3]])
        f.readline()

        # ----- Read aperiodic control parameters --------------------
        if aperiodic == 1:
            line = f.readline().split()
            [py1, py2, py3] = map(int, [line[0], line[1], line[2]])
            f.readline()

        # ----- Read mesh control parameters --------------------
        line = f.readline().split()
        [nSG, nnode, nelem, nmate, nslave, nlayer] = map(int, [line[0], line[1], line[2], line[3], line[4], line[5]])
        f.readline()

        # ----- Read nodal coordinates ------------------------------
        n_coord = []
        if nSG == 1:
            for i in range(nnode):
                line = f.readline().split()
                n_coord += [[int(line[0]), 0., 0., float(line[1])]]
        elif nSG == 2:
            for i in range(nnode):
                line = f.readline().split()
                n_coord += [[int(line[0]), 0., float(line[1]), float(line[2])]]
        elif nSG == 3:
            for i in range(nnode):
                line = f.readline().split()
                n_coord += [[int(line[0]), float(line[1]), float(line[2]), float(line[3])]]
        f.readline()

        # ----- Read element connectivities -------------------------
        e_connt = []
        # define a new list e_node to store the number of node for each element
        e_node = [0] * nelem
        if nSG == 1:
            for i in range(nelem):
                line = f.readline().split()
                e_connt += [map(int, line)]
                e_node[i] = sum(x > 0 for x in e_connt[i]) - 2
        elif nSG == 2:
            for i in range(nelem):
                line = f.readline().split()
                e_connt += [map(int, line)]
                e_node[i] = sum(x > 0 for x in e_connt[i]) - 2
        elif nSG == 3:
            for i in range(nelem):
                line = f.readline().split()
                e_connt += [map(int, line)]
                e_node[i] = sum(x > 0 for x in e_connt[i]) - 2
        f.readline()

        # ----- Read nmate material block --------------------------------------
        mat_lib = {}
        for i in range(nmate):

            # ----- Read material control parameters -------------------------
            line = f.readline().split()
            mat_id, isotropy, ntemp = map(int, line)

            # ----- Read material properties -------------------------
            elastic = []
            if isotropy == 0:
                for j in range(ntemp):
                    line = f.readline().split()
                    T_i, density_i = map(float, line)

                    line = f.readline().split()
                    const1_i, const2_i = map(float, line)

                    elastic += [[T_i, density_i, const1_i, const2_i]]

                    f.readline()

            elif isotropy == 1:
                for j in range(ntemp):
                    line = f.readline().split()
                    T_i, density_i = map(float, line)

                    line = f.readline().split()
                    [const1_i, const2_i, const3_i] = map(float, line)

                    line = f.readline().split()
                    [const4_i, const5_i, const6_i] = map(float, line)

                    line = f.readline().split()
                    [const7_i, const8_i, const9_i] = map(float, line)

                    elastic += [[T_i, density_i, const1_i, const2_i, const3_i, const4_i, const5_i, const6_i, const7_i, const8_i, const9_i]]

                    f.readline()

            elif isotropy == 2:
                for j in range(ntemp):
                    line = f.readline().split()
                    T_i, density_i = map(float, line)

                    C = [[0.] * 6] * 6

                    line = f.readline().split()
                    [C[0][0], C[0][1], C[0][2], C[0][3], C[0][4], C[0][5]] = map(float, line)

                    line = f.readline().split()
                    [C[1][1], C[1][2], C[1][3], C[1][4], C[1][5]] = map(float, line)

                    line = f.readline().split()
                    [C[2][2], C[2][3], C[2][4], C[2][5]] = map(float, line)

                    line = f.readline().split()
                    [C[3][3], C[3][4], C[3][5]] = map(float, line)

                    line = f.readline().split()
                    [C[4][4], C[4][5]] = map(float, line)

                    line = f.readline().split()
                    [C[5][5]] = map(float, line)

                    elastic += [[T_i, density_i,
                                 C[0][0], C[0][1], C[0][2], C[0][3], C[0][4], C[0][5],
                                 C[1][1], C[1][2], C[1][3], C[1][4], C[1][5],
                                 C[2][2], C[2][3], C[2][4], C[2][5],
                                 C[3][3], C[3][4], C[3][5],
                                 C[4][4], C[4][5],
                                 C[5][5]]]

                    f.readline()

            f.readline()

            mat_lib[mat_id] = {'isotropy': isotropy, 'ntemp': ntemp, 'elastic': elastic}

        f.readline()

        # ----- Read homogenized SG volume --------------------------------------
        line = f.readline().split()
        w = float(line[0])

    # read *.u file
    with open(user_dir + file_name_sc_u, 'r') as f:
        # nodal displacement value
        # n_dis = [
        #     [node_no1, ux1, uy1, uz1],
        #     [node_no2, ux2, uy2, uz2],
        #     ...
        # ]
        n_dis = []
        for i in range(nnode):
            line = f.readline().split()
            n_dis += [[int(line[0]), float(line[1]), float(line[2]), float(line[3])]]

    # read *.sn file
    with open(user_dir + file_name_sc_sn, 'r') as f:
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
        if nSG == 1:
            for i in range(nelem):
                strain = []
                stress = []
                for j in range(e_node[i]):
                    line = f.readline().split()
                    strain += [map(float, line[1:7])]
                    stress += [map(float, line[7:13])]
                e_strain[i + 1] = strain
                e_stress[i + 1] = stress
        elif nSG == 2:
            for i in range(nelem):
                strain = []
                stress = []
                for j in range(e_node[i]):
                    line = f.readline().split()
                    strain += [map(float, line[2:8])]
                    stress += [map(float, line[8:14])]
                e_strain[i + 1] = strain
                e_stress[i + 1] = stress
        elif nSG == 3:
            for i in range(nelem):
                strain = []
                stress = []
                for j in range(e_node[i]):
                    line = f.readline().split()
                    strain += [map(float, line[3:9])]
                    stress += [map(float, line[9:15])]
                e_strain[i + 1] = strain
                e_stress[i + 1] = stress

    ##################################################################
    # Write Gmsh format
    ##################################################################
    # element type in Gmsh
    # e_type is a list
    # type definition nSG node
    # 2 3-node triangle. 2 3
    # 3 4-node quadrangle. 2 4
    # 4 4-node tetrahedron. 3 4
    # 5 8-node hexahedron. 3 8
    # 9 6-node second order triangle (3 nodes associated with the vertices and 3 with the edges). 2 6
    # 11 10-node second order tetrahedron (4 nodes associated with the vertices and 6 with the edges). 3 10
    # 16 8-node second order quadrangle (4 nodes associated with the vertices and 4 with the edges). 2 8
    # 17 20-node second order hexahedron (8 nodes associated with the vertices and 12 with the edges). 3 20

    e_type = [0] * nelem
    if nSG == 2:
        for i in range(nelem):
            if e_node[i] == 3:
                e_type[i] = 2
            elif e_node[i] == 4:
                e_type[i] = 3
            elif e_node[i] == 6:
                e_type[i] = 9
            elif e_node[i] == 8:
                e_type[i] = 16
    elif nSG == 3:
        for i in range(nelem):
            if e_node[i] == 4:
                e_type[i] = 4
            elif e_node[i] == 8:
                e_type[i] = 5
            elif e_node[i] == 10:
                e_type[i] = 11
            elif e_node[i] == 20:
                e_type[i] = 17

    # Generate Gmsh input file *.msh
    file_name_msh = file_name + '.msh'
    with open(user_dir + file_name_msh, 'w') as f:

        # ----- MeshFormat --------------------
        f.write('$MeshFormat\n')
        f.write('2.2 0 8\n')
        f.write('$EndMeshFormat\n')

        # ----- Nodes ---------------------
        f.write('$Nodes\n')
        f.write(str(nnode) + '\n')
        for n in n_coord:
            list = str(n[0]) + ''.join([' %.5e' % x for x in n[1:4]])
            f.write(list + '\n')
        f.write('$EndNodes' + '\n')

        # ----- Elements ---------------------
        f.write('$Elements' + '\n')
        f.write(str(nelem) + '\n')
        for i in range(nelem):
            temp = e_connt[i]
            e = [x for x in temp if x > 0]
            e.insert(1, e_type[i])
            e.insert(2, nmate)
            e.insert(4, 10 + e[3])
            f.write(str(e).replace(',', '').replace('[', '').replace(']', '') + '\n')
        f.write('$EndElements' + '\n')

        # ----- Node Data ---------------------
        f.write('$NodeData' + '\n')
        f.write('1\n')
        f.write('"U-Magnitude"\n')
        f.write('1\n0\n3\n0\n1\n')
        f.write(str(nnode) + '\n')
        u_mag = [0] * nnode
        for i in range(nnode):
            u_mag[i] = (n_dis[i][1]**2 + n_dis[i][2]**2 + n_dis[i][3]**2)**(1 / 2.0)
            list = [i + 1, u_mag[i]]
            list = str(list[0]) + ''.join([' %.5e' % list[1]])
            f.write(list + '\n')
        f.write('$EndNodeData' + '\n')

        f.write('$NodeData' + '\n')
        f.write('1\n')
        f.write('"U1"\n')
        f.write('1\n0\n3\n0\n1\n')
        f.write(str(nnode) + '\n')
        for i in range(nnode):
            list = [i + 1, n_dis[i][1]]
            list = str(list[0]) + ''.join([' %.5e' % list[1]])
            f.write(list + '\n')
        f.write('$EndNodeData' + '\n')

        f.write('$NodeData' + '\n')
        f.write('1\n')
        f.write('"U2"\n')
        f.write('1\n0\n3\n0\n1\n')
        f.write(str(nnode) + '\n')
        for i in range(nnode):
            list = [i + 1, n_dis[i][2]]
            list = str(list[0]) + ''.join([' %.5e' % list[1]])
            f.write(list + '\n')
        f.write('$EndNodeData' + '\n')

        f.write('$NodeData' + '\n')
        f.write('1\n')
        f.write('"U3"\n')
        f.write('1\n0\n3\n0\n1\n')
        f.write(str(nnode) + '\n')
        for i in range(nnode):
            list = [i + 1, n_dis[i][3]]
            list = str(list[0]) + ''.join([' %.5e' % list[1]])
            f.write(list + '\n')
        f.write('$EndNodeData' + '\n')

        # ----- Element Data ---------------------
        f.write('$ElementNodeData' + '\n')
        f.write('1\n')
        f.write('"E11"\n')
        f.write('1\n0\n3\n0\n1\n')
        f.write(str(nelem) + '\n')
        for i in range(nelem):
            list = [i + 1, e_node[i]]
            for j in range(e_node[i]):
                list.append(e_strain[i + 1][j][0])
            temp = str(list[0]) + ' ' + str(list[1]) + ''.join([' %.5e' % x for x in list[2:2 + e_node[i]]])
            f.write(temp + '\n')
        f.write('$EndElementNodeData' + '\n')

        f.write('$ElementNodeData' + '\n')
        f.write('1\n')
        f.write('"E22"\n')
        f.write('1\n0\n3\n0\n1\n')
        f.write(str(nelem) + '\n')
        for i in range(nelem):
            list = [i + 1, e_node[i]]
            for j in range(e_node[i]):
                list.append(e_strain[i + 1][j][1])
            temp = str(list[0]) + ' ' + str(list[1]) + ''.join([' %.5e' % x for x in list[2:2 + e_node[i]]])
            f.write(temp + '\n')
        f.write('$EndElementNodeData' + '\n')

        f.write('$ElementNodeData' + '\n')
        f.write('1\n')
        f.write('"E33"\n')
        f.write('1\n0\n3\n0\n1\n')
        f.write(str(nelem) + '\n')
        for i in range(nelem):
            list = [i + 1, e_node[i]]
            for j in range(e_node[i]):
                list.append(e_strain[i + 1][j][2])
            temp = str(list[0]) + ' ' + str(list[1]) + ''.join([' %.5e' % x for x in list[2:2 + e_node[i]]])
            f.write(temp + '\n')
        f.write('$EndElementNodeData' + '\n')

        f.write('$ElementNodeData' + '\n')
        f.write('1\n')
        f.write('"E23"\n')
        f.write('1\n0\n3\n0\n1\n')
        f.write(str(nelem) + '\n')
        for i in range(nelem):
            list = [i + 1, e_node[i]]
            for j in range(e_node[i]):
                list.append(e_strain[i + 1][j][3])
            temp = str(list[0]) + ' ' + str(list[1]) + ''.join([' %.5e' % x for x in list[2:2 + e_node[i]]])
            f.write(temp + '\n')
        f.write('$EndElementNodeData' + '\n')

        f.write('$ElementNodeData' + '\n')
        f.write('1\n')
        f.write('"E13"\n')
        f.write('1\n0\n3\n0\n1\n')
        f.write(str(nelem) + '\n')
        for i in range(nelem):
            list = [i + 1, e_node[i]]
            for j in range(e_node[i]):
                list.append(e_strain[i + 1][j][4])
            temp = str(list[0]) + ' ' + str(list[1]) + ''.join([' %.5e' % x for x in list[2:2 + e_node[i]]])
            f.write(temp + '\n')
        f.write('$EndElementNodeData' + '\n')

        f.write('$ElementNodeData' + '\n')
        f.write('1\n')
        f.write('"E12"\n')
        f.write('1\n0\n3\n0\n1\n')
        f.write(str(nelem) + '\n')
        for i in range(nelem):
            list = [i + 1, e_node[i]]
            for j in range(e_node[i]):
                list.append(e_strain[i + 1][j][5])
            temp = str(list[0]) + ' ' + str(list[1]) + ''.join([' %.5e' % x for x in list[2:2 + e_node[i]]])
            f.write(temp + '\n')
        f.write('$EndElementNodeData' + '\n')

        f.write('$ElementNodeData' + '\n')
        f.write('1\n')
        f.write('"S11"\n')
        f.write('1\n0\n3\n0\n1\n')
        f.write(str(nelem) + '\n')
        for i in range(nelem):
            list = [i + 1, e_node[i]]
            for j in range(e_node[i]):
                list.append(e_stress[i + 1][j][0])
            temp = str(list[0]) + ' ' + str(list[1]) + ''.join([' %.5e' % x for x in list[2:2 + e_node[i]]])
            f.write(temp + '\n')
        f.write('$EndElementNodeData' + '\n')

        f.write('$ElementNodeData' + '\n')
        f.write('1\n')
        f.write('"S22"\n')
        f.write('1\n0\n3\n0\n1\n')
        f.write(str(nelem) + '\n')
        for i in range(nelem):
            list = [i + 1, e_node[i]]
            for j in range(e_node[i]):
                list.append(e_stress[i + 1][j][1])
            temp = str(list[0]) + ' ' + str(list[1]) + ''.join([' %.5e' % x for x in list[2:2 + e_node[i]]])
            f.write(temp + '\n')
        f.write('$EndElementNodeData' + '\n')

        f.write('$ElementNodeData' + '\n')
        f.write('1\n')
        f.write('"S33"\n')
        f.write('1\n0\n3\n0\n1\n')
        f.write(str(nelem) + '\n')
        for i in range(nelem):
            list = [i + 1, e_node[i]]
            for j in range(e_node[i]):
                list.append(e_stress[i + 1][j][2])
            temp = str(list[0]) + ' ' + str(list[1]) + ''.join([' %.5e' % x for x in list[2:2 + e_node[i]]])
            f.write(temp + '\n')
        f.write('$EndElementNodeData' + '\n')

        f.write('$ElementNodeData' + '\n')
        f.write('1\n')
        f.write('"S23"\n')
        f.write('1\n0\n3\n0\n1\n')
        f.write(str(nelem) + '\n')
        for i in range(nelem):
            list = [i + 1, e_node[i]]
            for j in range(e_node[i]):
                list.append(e_stress[i + 1][j][3])
            temp = str(list[0]) + ' ' + str(list[1]) + ''.join([' %.5e' % x for x in list[2:2 + e_node[i]]])
            f.write(temp + '\n')
        f.write('$EndElementNodeData' + '\n')

        f.write('$ElementNodeData' + '\n')
        f.write('1\n')
        f.write('"S13"\n')
        f.write('1\n0\n3\n0\n1\n')
        f.write(str(nelem) + '\n')
        for i in range(nelem):
            list = [i + 1, e_node[i]]
            for j in range(e_node[i]):
                list.append(e_stress[i + 1][j][4])
            temp = str(list[0]) + ' ' + str(list[1]) + ''.join([' %.5e' % x for x in list[2:2 + e_node[i]]])
            f.write(temp + '\n')
        f.write('$EndElementNodeData' + '\n')

        f.write('$ElementNodeData' + '\n')
        f.write('1\n')
        f.write('"S12"\n')
        f.write('1\n0\n3\n0\n1\n')
        f.write(str(nelem) + '\n')
        for i in range(nelem):
            list = [i + 1, e_node[i]]
            for j in range(e_node[i]):
                list.append(e_stress[i + 1][j][5])
            temp = str(list[0]) + ' ' + str(list[1]) + ''.join([' %.5e' % x for x in list[2:2 + e_node[i]]])
            f.write(temp + '\n')
        f.write('$EndElementNodeData' + '\n')

    # Create .geo file for Gmsh
    file_name_geo = file_name + '.geo'
    with open(user_dir + file_name_geo, 'w') as f:
        f.write('Merge "' + file_name_msh + '";\n')
        f.write("""
Mesh.SurfaceFaces=0;
Mesh.Points=0;
Mesh.SurfaceEdges=0;
Mesh.VolumeEdges = 0;

General.GraphicsHeight = 500;
General.GraphicsWidth = 600;
General.GraphicsPositionX = 800;
General.GraphicsPositionY = 500;

General.TrackballQuaternion0 = 0.5;
General.TrackballQuaternion1 = 0.5;
General.TrackballQuaternion2 = 0.5;
General.TrackballQuaternion3 = 0.5;

General.RotationX = 270;
General.RotationY = 0;
General.RotationZ = 270;

 View[0].Visible=1;
 View[1].Visible=0;
 View[2].Visible=0;
 View[3].Visible=0;
 View[4].Visible=0;
 View[5].Visible=0;
 View[6].Visible=0;
 View[7].Visible=0;
 View[8].Visible=0;
 View[9].Visible=0;
View[10].Visible=0;
View[11].Visible=0;
View[12].Visible=0;
View[13].Visible=0;
View[14].Visible=0;
View[15].Visible=0;

 View[0].TransformXX=3.5;
 View[1].TransformXX=3.5;
 View[2].TransformXX=3.5;
 View[3].TransformXX=3.5;
 View[4].TransformXX=3.5;
 View[5].TransformXX=3.5;
 View[6].TransformXX=3.5;
 View[7].TransformXX=3.5;
 View[8].TransformXX=3.5;
 View[9].TransformXX=3.5;
View[10].TransformXX=3.5;
View[11].TransformXX=3.5;
View[12].TransformXX=3.5;
View[13].TransformXX=3.5;
View[14].TransformXX=3.5;
View[15].TransformXX=3.5;

 View[0].TransformYY=3.5;
 View[1].TransformYY=3.5;
 View[2].TransformYY=3.5;
 View[3].TransformYY=3.5;
 View[4].TransformYY=3.5;
 View[5].TransformYY=3.5;
 View[6].TransformYY=3.5;
 View[7].TransformYY=3.5;
 View[8].TransformYY=3.5;
 View[9].TransformYY=3.5;
View[10].TransformYY=3.5;
View[11].TransformYY=3.5;
View[12].TransformYY=3.5;
View[13].TransformYY=3.5;
View[14].TransformYY=3.5;
View[15].TransformYY=3.5;

 View[0].TransformZZ=3.5;
 View[1].TransformZZ=3.5;
 View[2].TransformZZ=3.5;
 View[3].TransformZZ=3.5;
 View[4].TransformZZ=3.5;
 View[5].TransformZZ=3.5;
 View[6].TransformZZ=3.5;
 View[7].TransformZZ=3.5;
 View[8].TransformZZ=3.5;
 View[9].TransformZZ=3.5;
View[10].TransformZZ=3.5;
View[11].TransformZZ=3.5;
View[12].TransformZZ=3.5;
View[13].TransformZZ=3.5;
View[14].TransformZZ=3.5;
View[15].TransformZZ=3.5;

 View[0].ShowElement=1;
 View[1].ShowElement=1;
 View[2].ShowElement=1;
 View[3].ShowElement=1;
 View[4].ShowElement=1;
 View[5].ShowElement=1;
 View[6].ShowElement=1;
 View[7].ShowElement=1;
 View[8].ShowElement=1;
 View[9].ShowElement=1;
View[10].ShowElement=1;
View[11].ShowElement=1;
View[12].ShowElement=1;
View[13].ShowElement=1;
View[14].ShowElement=1;
View[15].ShowElement=1;
                """)

    install_dir = ExtAPI.ExtensionManager.CurrentExtension.InstallDir
    if not os.path.isfile(user_dir + 'gmsh.exe'):
        shutil.copyfile(install_dir + '\\bin\\gmsh.exe', user_dir + 'gmsh.exe')

    sc_dehom = subprocess.Popen([user_dir + 'gmsh', file_name_geo], cwd=user_dir)

    # dir = ExtAPI.ExtensionManager.CurrentExtension.InstallDir
    # gmsh_dir = dir + '/bin'
    # run_gmsh = gmsh_dir + '/gmsh'
    return 0
