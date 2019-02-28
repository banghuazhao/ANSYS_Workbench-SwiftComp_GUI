import subprocess
import time
import os

import errorcheck
import utilities

import sg
import sg_filesystem
import sg_result
import sg_homogenization_result_list

import pickle


def SwiftCompHomogenizationInput(arg):
    '''Creating homogenization input file'''

    ExtAPI, fct = arg[0]

    # check SwiftComp executable
    if errorcheck.noSwiftCompExe(ExtAPI):
        return False

    fct(0,"Begin generating homogenization input file")

    # Start Creating homogenization input file
    hom_input_time_start = time.clock()

    # create structuregenome instance SG
    SG = sg.StructureGenome()
    SGResult = sg_result.SGResult()

    # set macroModel
    SG.setMacroModel(arg[2])
    SGResult.result_name = arg[1]
    SGResult.setMacroModel(arg[2])

    # set extra inputs, common_flag, aperiodic_flag
    if SG.BeamModel:  # beam model
        SG.setBeamModelControlParameters(arg[3], arg[4], arg[5], arg[6], arg[7])
    elif SG.PlateModel:  # plate/shell model
        SG.setPlateModelControlParameters(arg[3], arg[4], arg[5], arg[6])
    elif SG.SolidModel:  # solid model
        SG.setSolidModelControlParameters(arg[3], arg[4])
    
    # check if it is 1D SG (check for 'Import Plies')
    if any([x.Name == 'Imported Plies' for x in ExtAPI.DataModel.Project.Model.Children]):
        if SG.BeamModel:
            utilities.No1DSGForBeamModel()
            return False
        else:
            try:
                SG.set1DSG(ExtAPI)
            except Exception as e:
                utilities.set1DSGWrongMessage(e)
                return False

    else:  # not 1D SG
        # set Material library
        try:
            SG.setMaterial(ExtAPI)
        except Exception as e:
            utilities.setMaterialWrongMessage(e)
            return False

        # set nSG, nnode, nelem, nmate, nslave, nlayer
        SG.setMeshControlParameters(ExtAPI)

        # set node coordinates
        try:
            fct(10,"Extract node coordinate information...")
            SG.setNodaCoordinate(ExtAPI)
        except Exception as e:
            utilities.setNodeWrongMessage(e)
            return False

        # set element connectivity
        try:
            fct(20,"Extract element connectivity information...")
            SG.setElementConnectivity(ExtAPI)
        except Exception as e:
            utilities.setElementWrongMessage(e)
            return False

        # set omega
        SG.setOmega(ExtAPI)

    # get SG directory and files
    SGFileSystem = sg_filesystem.SGFileSystem(ExtAPI)

    # Generate SwiftComp homogenization input file *.sc
    with open(SGFileSystem.dir_file_name_sc, 'w') as f:

        fct(30,"Begin writting input file...")

        # ----- Write extra inputs for dimensionally reducible structures -------
        if SG.BeamModel:
            utilities.writeFormat(f, 'd', [SG.BeamModel.submodel])
            f.write('\n')
            utilities.writeFormat(f, 'EEE', SG.BeamModel.beam_ini_curvatures)
            f.write('\n')
            utilities.writeFormat(f, 'EE', SG.BeamModel.beam_ini_oblique)
            f.write('\n')
        elif SG.PlateModel:
            utilities.writeFormat(f, 'd', [SG.PlateModel.submodel])
            f.write('\n')
            utilities.writeFormat(f, 'EE', SG.PlateModel.plate_ini_curvatures)
            f.write('\n')

        # ----- Write problem control parameters --------------------
        utilities.writeFormat(f, 'd' * 4, [SG.analysis, SG.elem_flag, SG.trans_flag, SG.temp_flag])
        f.write('\n')

        # ----- Write aperiodic control parameters --------------------
        if SG.aperiodic:
            utilities.writeFormat(f, 'd' * 3, [SG.py1, SG.py2, SG.py3])
            f.write('\n')

        # ----- Write mesh control parameters --------------------
        utilities.writeFormat(f, 'd' * 6, [SG.nSG, SG.nnode, SG.nelem, SG.nmate, SG.nslave, SG.nlayer])
        f.write('\n')

        # ----- Write nodal coordinates ------------------------------
        fct(40,"Begin writting nodal coordinates...")
        if SG.nSG == 1:
            for i in range(SG.nnode):
                utilities.writeFormat(f, 'dE', [i+1, SG.Node[i].coordinate[2]])
        elif SG.nSG == 2:
            for i in range(SG.nnode):
                utilities.writeFormat(f, 'dEE', [i+1, SG.Node[i].coordinate[1], SG.Node[i].coordinate[2]])
        elif SG.nSG == 3:
            for i in range(SG.nnode):
                utilities.writeFormat(f, 'dEEE', [i+1, SG.Node[i].coordinate[0], SG.Node[i].coordinate[1], SG.Node[i].coordinate[2]])
        f.write('\n')

        # ----- Write element connectivities -------------------------
        fct(70,"Begin writting element connectivities...")
        if SG.nlayer == 0:
            if SG.nSG == 2:
                for i in range(SG.nelem):
                    utilities.writeFormat(f, 'd' * 11, [i+1] + [SG.Element[i].material_id] + SG.Element[i].connectivity)
            elif SG.nSG == 3:
                for i in range(SG.nelem):
                    utilities.writeFormat(f, 'd' * 22, [i+1] + [SG.Element[i].material_id] + SG.Element[i].connectivity)
        else:
            if SG.nSG == 1:
                for i in range(SG.nelem):
                    utilities.writeFormat(f, 'd' * 7, [i+1] + [SG.Element[i].layer_id] + SG.Element[i].connectivity)
            elif SG.nSG == 2:
                for i in range(SG.nelem):
                    utilities.writeFormat(f, 'd' * 11, [i+1] + [SG.Element[i].layer_id] + SG.Element[i].connectivity)
            elif SG.nSG == 3:
                for i in range(SG.nelem):
                    utilities.writeFormat(f, 'd' * 22, [i+1] + [SG.Element[i].layer_id] + SG.Element[i].connectivity)
        f.write('\n')

        # ----- Write layer block -------------------------
        if SG.nlayer > 0:
            for i in range(SG.nlayer):
                utilities.writeFormat(f, 'ddE', [i+1] + [SG.Layer[i].material_id] + [SG.Layer[i].angle])
        f.write('\n')
        
        # ----- Write nmate material block --------------------------------------
        fct(90,"Begin writting material block...")
        for i in range(SG.nmate):

            # ----- Write material control parameters -------------------------
            utilities.writeFormat(f, 'ddd', [i+1, SG.Material[i].isotropy, SG.Material[i].ntemp])

            for j in range(SG.Material[i].ntemp):
                # ----- Write material properties -------------------------
                utilities.writeFormat(f, 'EE', [SG.Material[i].MaterialProperty[j].T, SG.Material[i].MaterialProperty[j].density])
                if SG.Material[i].isotropy == 0:
                    utilities.writeFormat(f, 'EE', [SG.Material[i].MaterialProperty[j].isotropic['E'], SG.Material[i].MaterialProperty[j].isotropic['nu']])
                elif SG.Material[i].isotropy == 1:
                    utilities.writeFormat(f, 'EEE', [SG.Material[i].MaterialProperty[j].orthotropic['E1'], SG.Material[i].MaterialProperty[j].orthotropic['E2'], SG.Material[i].MaterialProperty[j].orthotropic['E3']])
                    utilities.writeFormat(f, 'EEE', [SG.Material[i].MaterialProperty[j].orthotropic['G12'], SG.Material[i].MaterialProperty[j].orthotropic['G13'], SG.Material[i].MaterialProperty[j].orthotropic['G23']])
                    utilities.writeFormat(f, 'EEE', [SG.Material[i].MaterialProperty[j].orthotropic['nu12'], SG.Material[i].MaterialProperty[j].orthotropic['nu13'], SG.Material[i].MaterialProperty[j].orthotropic['nu23']])
                elif SG.Material[i].isotropy == 2:
                    utilities.writeFormat(f, 'E' * 6, SG.Material[i].MaterialProperty[j].anisotropic[0][0:])
                    utilities.writeFormat(f, 'E' * 5, SG.Material[i].MaterialProperty[j].anisotropic[1][1:])
                    utilities.writeFormat(f, 'E' * 4, SG.Material[i].MaterialProperty[j].anisotropic[2][2:])
                    utilities.writeFormat(f, 'E' * 3, SG.Material[i].MaterialProperty[j].anisotropic[3][3:])
                    utilities.writeFormat(f, 'E' * 2, SG.Material[i].MaterialProperty[j].anisotropic[4][4:])
                    utilities.writeFormat(f, 'E' * 1, SG.Material[i].MaterialProperty[j].anisotropic[5][5:])
                f.write('\n')
                
            f.write('\n')

        f.write('\n')

        # ----- Write homogenized SG volume --------------------------------------
        utilities.writeFormat(f, 'E', [SG.omega])
        f.write('\n')

    hom_input_time_end = time.clock()

    SGResult.homInputTime = hom_input_time_end - hom_input_time_start

    # save SG instance to file so that we can use it later
    with open(SGFileSystem.user_dir + 'SG.pickle', 'wb') as f:
        pickle.dump(SG, f)

    # save SGResult instance to file so that we can use it later
    with open(SGFileSystem.user_dir + 'SGResult.pickle', 'wb') as f:
        pickle.dump(SGResult, f)

    fct(100,"Finish generating homogenization input file...")

    ExtAPI.Log.WriteMessage("Creating homogenization input file finished.")
    ExtAPI.Log.WriteMessage("Creating Homogenization input file time: " + str(SGResult.homInputTime))

    return True



def SwiftCompHomogenizationRun(arg):
    ''' Run SwiftComp homogenization'''

    ExtAPI, fct = arg

    fct(0,"Begin homogenization...")

    SGFileSystem = sg_filesystem.SGFileSystem(ExtAPI)

    # Check SwiftComp temp files (SCInt, SCReal, SCTemp, SCWork). If exist, delete them
    user_dir_files = os.listdir(SGFileSystem.user_dir)
    if 'SCInt' in user_dir_files or 'SCReal' in user_dir_files or 'SCTemp' in user_dir_files or 'SCWork' in user_dir_files:
        os.remove(SGFileSystem.user_dir + 'SCInt')
        os.remove(SGFileSystem.user_dir + 'SCReal')
        os.remove(SGFileSystem.user_dir + 'SCTemp')
        os.remove(SGFileSystem.user_dir + 'SCWork')

    SG = sg.StructureGenome()
    with open(SGFileSystem.user_dir + 'SG.pickle', 'rb') as f:
        SG = pickle.load(f)

    SGResult = sg_result.SGResult()
    with open(SGFileSystem.user_dir + 'SGResult.pickle', 'rb') as f:
        SGResult = pickle.load(f)
    
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
        arg3 = 'H'
    else:
        arg3 = 'HA'

    # ================================================================
    # arg4: The version of SwiftComp is running:
    # ----------------------------------------------------------------
    # B for standard version
    # P for professional version
    # No arguments for parallel version
    # ================================================================
    arg4 = ''

    hom_time_start = time.clock()

    # Run homogenization! save stdout to a file named temp
    command = ['SwiftComp', arg1, arg2, arg3, arg4, '>', SGFileSystem.user_dir+'temp']
    exitCode = subprocess.call(command, cwd=SGFileSystem.user_dir, shell=True)
    if exitCode != 0:
        return False

    hom_time_end = time.clock()

    # Homogenization time
    SGResult.homTime = hom_time_end - hom_time_start

    fct(95,"Finish homogenization...")

    # Get standard output
    with open(SGFileSystem.user_dir + 'temp', 'r') as f:
        SGResult.hommStdout = f.read()
    os.remove(SGFileSystem.user_dir + 'temp')

    # Check whether the homogenization is successful or not.
    if errorcheck.homNotSuccessful(ExtAPI, SGResult.hommStdout):
        return False

    # Display the result file *.sc.k
    os.startfile(SGFileSystem.dir_file_name_sc_k)

    # write solve.out file
    with open('solve.out', 'w') as f:
        f.write(SGResult.hommStdout)

    # Set Beam/Plate/Solid model result
    if SGResult.BeamModel:
        SGResult.setBeamModelResult(SGFileSystem)
    elif SGResult.PlateModel:
        SGResult.setPlateModelResult(SGFileSystem)
    elif SGResult.SolidModel:
        SGResult.setSolidModelResult(SGFileSystem)

    # save updated SGResult
    with open(SGFileSystem.user_dir + 'SGResult.pickle', 'wb') as f:
        pickle.dump(SGResult, f)

    ExtAPI.Log.WriteMessage("Homogenization finished.")
    ExtAPI.Log.WriteMessage("Homogenization time: " + str(SGResult.homTime))

    # update SGHomogenizationResultList

    SGHomogenizationResultList = sg_homogenization_result_list.SGHomogenizationResultList()

    SGHomogenizationResult = sg_homogenization_result_list.SGHomogenizationResult()

    SGHomogenizationResult.result_name = SGResult.result_name

    if SGResult.BeamModel:
        SGHomogenizationResult.BeamModel = SGResult.BeamModel
    elif SGResult.PlateModel:
        SGHomogenizationResult.PlateModel = SGResult.PlateModel
    elif SGResult.SolidModel:
        SGHomogenizationResult.SolidModel = SGResult.SolidModel

    SGHomogenizationResult.density = SGResult.density

    if "SGHomogenizationResultList.pickle" in user_dir_files:
        with open(SGFileSystem.user_dir + 'SGHomogenizationResultList.pickle', 'rb') as f:
            SGHomogenizationResultList = pickle.load(f)
    
    SGHomogenizationResultList.setHomogenizationResult(SGHomogenizationResult)

    # save updated SGStructuralResultList
    with open(SGFileSystem.user_dir + 'SGHomogenizationResultList.pickle', 'wb') as f:
        pickle.dump(SGHomogenizationResultList, f)

    fct(100,"Stored homogenization Result...")
    return True


def homogenizationResult(ExtAPI):
    '''fetch SGResult instance'''

    SGFileSystem = sg_filesystem.SGFileSystem(ExtAPI)

    SGResult = sg_result.SGResult()
    with open(SGFileSystem.user_dir + 'SGResult.pickle', 'rb') as f:
        SGResult = pickle.load(f)

    return SGResult


def updateSGHomogenizationResultListObjectWhenRemove(arg):

    ExtAPI, result_name = arg[:]

    SGFileSystem = sg_filesystem.SGFileSystem(ExtAPI)

    user_dir_files = os.listdir(SGFileSystem.user_dir)

    SGHomogenizationResultList = sg_homogenization_result_list.SGHomogenizationResultList()

    if "SGHomogenizationResultList.pickle" in user_dir_files:
        with open(SGFileSystem.user_dir + "SGHomogenizationResultList.pickle", 'rb') as f:
            SGHomogenizationResultList = pickle.load(f)

        # remove the SGHomogennizationResult in the list
        for i in range(len(SGHomogenizationResultList.ResultList)):
            if result_name == SGHomogenizationResultList.ResultList[i].result_name:
                del SGHomogenizationResultList.ResultList[i]
                break

        # save updated SGHomogenizationResultList
        with open(SGFileSystem.user_dir + "SGHomogenizationResultList.pickle", 'wb') as f:
            pickle.dump(SGHomogenizationResultList, f)
