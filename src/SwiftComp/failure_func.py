import utilities
import pickle
import time
import subprocess
import os

import errorcheck
import sg
import sg_result
import sg_filesystem

def SwiftCompFailureInput(arg):

    ExtAPI, load, F_type = arg

    SGFileSystem = sg_filesystem.SGFileSystem(ExtAPI)

    SG = sg.StructureGenome()
    with open(SGFileSystem.user_dir + 'SG.pickle', 'rb') as f:
        SG = pickle.load(f)

    table = load.Properties["Strength Parameters/Failure Criterion"]

    FC = []
    num_of_constants = []
    constants = []
    for i in range(SG.nmate):
        table.ActiveRow = i
        material_name = table.Properties["Material Name"]
        material_type = table.Properties["Material Type"]
        if material_type.Value == 'Isotropic':
            failure_criterion = material_type.Properties["FC (isotropic)"]
            FC.append(failure_criterion.Value)
            if failure_criterion.Value == 'Max Principal Stress':
                num_of_constants.append(2)
                X_t = abs(failure_criterion.Properties["X_t"].Value)
                X_c = abs(failure_criterion.Properties["X_c"].Value)
                constants.append({'X_t':X_t, 'Y_t':None, 'Z_t':None, 'X_c':X_c, 'Y_c':None, 'Z_c':None, 'R':None, 'T':None, 'S':None, 
                                    'Xe_t':None, 'Ye_t':None, 'Ze_t':None, 'Xe_c':None, 'Ye_c':None, 'Ze_c':None, 'Re':None, 'Te':None, 'Se':None})
            elif failure_criterion.Value == 'Max Principal Strain':
                num_of_constants.append(2)
                Xe_t = abs(failure_criterion.Properties["Xe_t"].Value)
                Xe_c = abs(failure_criterion.Properties["Xe_c"].Value)
                constants.append({'X_t':None, 'Y_t':None, 'Z_t':None, 'X_c':None, 'Y_c':None, 'Z_c':None, 'R':None, 'T':None, 'S':None, 
                                    'Xe_t':Xe_t, 'Ye_t':None, 'Ze_t':None, 'Xe_c':Xe_c, 'Ye_c':None, 'Ze_c':None, 'Re':None, 'Te':None, 'Se':None})
            elif failure_criterion.Value == 'Max Shear Stress':
                num_of_constants.append(1)
                S = abs(failure_criterion.Properties["S"].Value)
                constants.append({'X_t':None, 'Y_t':None, 'Z_t':None, 'X_c':None, 'Y_c':None, 'Z_c':None, 'R':None, 'T':None, 'S':S, 
                                    'Xe_t':None, 'Ye_t':None, 'Ze_t':None, 'Xe_c':None, 'Ye_c':None, 'Ze_c':None, 'Re':None, 'Te':None, 'Se':None})
            elif failure_criterion.Value == 'Max Shear Strain':
                num_of_constants.append(1)
                Se = abs(failure_criterion.Properties["Se"].Value)
                constants.append({'X_t':None, 'Y_t':None, 'Z_t':None, 'X_c':None, 'Y_c':None, 'Z_c':None, 'R':None, 'T':None, 'S':None, 
                                    'Xe_t':None, 'Ye_t':None, 'Ze_t':None, 'Xe_c':None, 'Ye_c':None, 'Ze_c':None, 'Re':None, 'Te':None, 'Se':Se})
            elif failure_criterion.Value == 'Mises Criterion':
                num_of_constants.append(1)
                X_t = abs(failure_criterion.Properties["X_t"].Value)
                constants.append({'X_t':X_t, 'Y_t':None, 'Z_t':None, 'X_c':None, 'Y_c':None, 'Z_c':None, 'R':None, 'T':None, 'S':None, 
                                    'Xe_t':None, 'Ye_t':None, 'Ze_t':None, 'Xe_c':None, 'Ye_c':None, 'Ze_c':None, 'Re':None, 'Te':None, 'Se':None})
        else:
            failure_criterion = material_type.Properties["FC (not isotropic)"]
            FC.append(failure_criterion.Value)
            if failure_criterion.Value == 'Max Stress':
                num_of_constants.append(9)
                X_t = abs(failure_criterion.Properties["X_t"].Value)
                Y_t = abs(failure_criterion.Properties["Y_t"].Value)
                Z_t = abs(failure_criterion.Properties["Z_t"].Value)
                X_c = abs(failure_criterion.Properties["X_c"].Value)
                Y_c = abs(failure_criterion.Properties["Y_c"].Value)
                Z_c = abs(failure_criterion.Properties["Z_c"].Value)
                R   = abs(failure_criterion.Properties["R"].Value)
                T   = abs(failure_criterion.Properties["T"].Value)
                S   = abs(failure_criterion.Properties["S"].Value)
                constants.append({'X_t':X_t, 'Y_t':Y_t, 'Z_t':Z_t, 'X_c':X_c, 'Y_c':Y_c, 'Z_c':Z_c, 'R':R, 'T':T, 'S':S, 
                                    'Xe_t':None, 'Ye_t':None, 'Ze_t':None, 'Xe_c':None, 'Ye_c':None, 'Ze_c':None, 'Re':None, 'Te':None, 'Se':None})
            elif failure_criterion.Value == 'Max Strain':
                num_of_constants.append(9)
                Xe_t = abs(failure_criterion.Properties["Xe_t"].Value)
                Ye_t = abs(failure_criterion.Properties["Ye_t"].Value)
                Ze_t = abs(failure_criterion.Properties["Ze_t"].Value)
                Xe_c = abs(failure_criterion.Properties["Xe_c"].Value)
                Ye_c = abs(failure_criterion.Properties["Ye_c"].Value)
                Ze_c = abs(failure_criterion.Properties["Ze_c"].Value)
                Re   = abs(failure_criterion.Properties["Re"].Value)
                Te   = abs(failure_criterion.Properties["Te"].Value)
                Se   = abs(failure_criterion.Properties["Se"].Value)
                constants.append({'X_t':None, 'Y_t':None, 'Z_t':None, 'X_c':None, 'Y_c':None, 'Z_c':None, 'R':None, 'T':None, 'S':None, 
                                    'Xe_t':Xe_t, 'Ye_t':Ye_t, 'Ze_t':Ze_t, 'Xe_c':Xe_c, 'Ye_c':Ye_c, 'Ze_c':Ze_c, 'Re':Re, 'Te':Te, 'Se':Se})
            elif failure_criterion.Value == 'Tsai-Hill':
                num_of_constants.append(6)
                X_t = abs(failure_criterion.Properties["X_t"].Value)
                Y_t = abs(failure_criterion.Properties["Y_t"].Value)
                Z_t = abs(failure_criterion.Properties["Z_t"].Value)
                R   = abs(failure_criterion.Properties["R"].Value)
                T   = abs(failure_criterion.Properties["T"].Value)
                S   = abs(failure_criterion.Properties["S"].Value)
                constants.append({'X_t':X_t, 'Y_t':Y_t, 'Z_t':Z_t, 'X_c':None, 'Y_c':None, 'Z_c':None, 'R':R, 'T':T, 'S':S, 
                                    'Xe_t':None, 'Ye_t':None, 'Ze_t':None, 'Xe_c':None, 'Ye_c':None, 'Ze_c':None, 'Re':None, 'Te':None, 'Se':None})
            elif failure_criterion.Value == 'Tsai-Wu':
                num_of_constants.append(9)
                X_t = abs(failure_criterion.Properties["X_t"].Value)
                Y_t = abs(failure_criterion.Properties["Y_t"].Value)
                Z_t = abs(failure_criterion.Properties["Z_t"].Value)
                X_c = abs(failure_criterion.Properties["X_c"].Value)
                Y_c = abs(failure_criterion.Properties["Y_c"].Value)
                Z_c = abs(failure_criterion.Properties["Z_c"].Value)
                R   = abs(failure_criterion.Properties["R"].Value)
                T   = abs(failure_criterion.Properties["T"].Value)
                S   = abs(failure_criterion.Properties["S"].Value)
                constants.append({'X_t':X_t, 'Y_t':Y_t, 'Z_t':Z_t, 'X_c':X_c, 'Y_c':Y_c, 'Z_c':Z_c, 'R':R, 'T':T, 'S':S, 
                                    'Xe_t':None, 'Ye_t':None, 'Ze_t':None, 'Xe_c':None, 'Ye_c':None, 'Ze_c':None, 'Re':None, 'Te':None, 'Se':None})
            elif failure_criterion.Value == 'Hashin':
                num_of_constants.append(6)
                X_t = abs(failure_criterion.Properties["X_t"].Value)
                Y_t = abs(failure_criterion.Properties["Y_t"].Value)
                X_c = abs(failure_criterion.Properties["X_c"].Value)
                Y_c = abs(failure_criterion.Properties["Y_c"].Value)
                R   = abs(failure_criterion.Properties["R"].Value)
                T   = abs(failure_criterion.Properties["T"].Value)
                constants.append({'X_t':X_t, 'Y_t':Y_t, 'Z_t':None, 'X_c':X_c, 'Y_c':Y_c, 'Z_c':None, 'R':R, 'T':T, 'S':None, 
                                    'Xe_t':None, 'Ye_t':None, 'Ze_t':None, 'Xe_c':None, 'Ye_c':None, 'Ze_c':None, 'Re':None, 'Te':None, 'Se':None})

    Char_length = load.Properties["Strength Parameters/Characteristic Length"].Value
    if load.Properties["Additional Information/Generalized StressStrain"].Value == 'Stress':
        id1 = 0
    else:
        id1 = 1

    if F_type == 'FE':  # failure envelope analysis
        if id1 == 0:
            axis1 = load.Properties["Additional Information/Generalized StressStrain/Failure Envelope x Axis Component (Stress)"].Value
            axis2 = load.Properties["Additional Information/Generalized StressStrain/Failure Envelope y Axis Component (Stress)"].Value
        else:
            axis1 = load.Properties["Additional Information/Generalized StressStrain/Failure Envelope x Axis Component (Strain)"].Value
            axis2 = load.Properties["Additional Information/Generalized StressStrain/Failure Envelope y Axis Component (Strain)"].Value

        if axis1 == 'sigma11' or axis1 == 'epsilon11':
            istr1 = 1
        elif axis1 == 'sigma22' or axis1 == 'epsilon22':
            istr1 = 2
        elif axis1 == 'sigma33' or axis1 == 'epsilon33':
            istr1 = 3
        elif axis1 == 'sigma23' or axis1 == 'epsilon23':
            istr1 = 4
        elif axis1 == 'sigma13' or axis1 == 'epsilon13':
            istr1 = 5
        elif axis1 == 'sigma12' or axis1 == 'epsilon12':
            istr1 = 6

        if axis2 == 'sigma11' or axis2 == 'epsilon11':
            istr2 = 1
        elif axis2 == 'sigma22' or axis2 == 'epsilon22':
            istr2 = 2
        elif axis2 == 'sigma33' or axis2 == 'epsilon33':
            istr2 = 3
        elif axis2 == 'sigma23' or axis2 == 'epsilon23':
            istr2 = 4
        elif axis2 == 'sigma13' or axis2 == 'epsilon13':
            istr2 = 5
        elif axis2 == 'sigma12' or axis2 == 'epsilon12':
            istr2 = 6

        idiv = int(load.Properties["Additional Information/Number of divisions along one direction"].Value)

    elif F_type == 'FI':  # failure index analysis
        if SG.BeamModel:
            if SG.BeamModel.submodel == 0:
                if id1 == 0:
                    F1 = load.Properties["Additional Information/Generalized StressStrain/Euler-Bernoulli Beam Stress/F1"].Value
                    M1 = load.Properties["Additional Information/Generalized StressStrain/Euler-Bernoulli Beam Stress/M1"].Value
                    M2 = load.Properties["Additional Information/Generalized StressStrain/Euler-Bernoulli Beam Stress/M2"].Value
                    M3 = load.Properties["Additional Information/Generalized StressStrain/Euler-Bernoulli Beam Stress/M3"].Value
                else:
                    e11 = load.Properties["Additional Information/Generalized StressStrain/Euler-Bernoulli Beam Strain/epsilon11"].Value
                    k11 = load.Properties["Additional Information/Generalized StressStrain/Euler-Bernoulli Beam Strain/kappa11"].Value
                    k12 = load.Properties["Additional Information/Generalized StressStrain/Euler-Bernoulli Beam Strain/kappa12"].Value
                    k13 = load.Properties["Additional Information/Generalized StressStrain/Euler-Bernoulli Beam Strain/kappa13"].Value
            elif SG.BeamModel.submodel == 1:
                if id1 == 0:
                    F1 = load.Properties["Additional Information/Generalized StressStrain/Timoshenko Beam Stress/F1"].Value
                    F2 = load.Properties["Additional Information/Generalized StressStrain/Timoshenko Beam Stress/F2"].Value
                    F3 = load.Properties["Additional Information/Generalized StressStrain/Timoshenko Beam Stress/F3"].Value
                    M1 = load.Properties["Additional Information/Generalized StressStrain/Timoshenko Beam Stress/M1"].Value
                    M2 = load.Properties["Additional Information/Generalized StressStrain/Timoshenko Beam Stress/M2"].Value
                    M3 = load.Properties["Additional Information/Generalized StressStrain/Timoshenko Beam Stress/M3"].Value
                else:
                    e11 = load.Properties["Additional Information/Generalized StressStrain/Timoshenko Beam Strain/epsilon11"].Value
                    g12 = load.Properties["Additional Information/Generalized StressStrain/Timoshenko Beam Strain/gamma12"].Value
                    g13 = load.Properties["Additional Information/Generalized StressStrain/Timoshenko Beam Strain/gamma13"].Value
                    k11 = load.Properties["Additional Information/Generalized StressStrain/Timoshenko Beam Strain/kappa11"].Value
                    k12 = load.Properties["Additional Information/Generalized StressStrain/Timoshenko Beam Strain/kappa12"].Value
                    k13 = load.Properties["Additional Information/Generalized StressStrain/Timoshenko Beam Strain/kappa13"].Value
        elif SG.PlateModel:
            if SG.PlateModel.submodel == 0:
                if id1 == 0:
                    N11 = load.Properties["Additional Information/Generalized StressStrain/Kirchhoff-Love Plate Stress/N11"].Value
                    N22 = load.Properties["Additional Information/Generalized StressStrain/Kirchhoff-Love Plate Stress/N22"].Value
                    N12 = load.Properties["Additional Information/Generalized StressStrain/Kirchhoff-Love Plate Stress/N12"].Value
                    M11 = load.Properties["Additional Information/Generalized StressStrain/Kirchhoff-Love Plate Stress/M11"].Value
                    M22 = load.Properties["Additional Information/Generalized StressStrain/Kirchhoff-Love Plate Stress/M22"].Value
                    M12 = load.Properties["Additional Information/Generalized StressStrain/Kirchhoff-Love Plate Stress/M12"].Value
                else:
                    e11 = load.Properties["Additional Information/Generalized StressStrain/Kirchhoff-Love Plate Strain/epsilon11"].Value
                    e22 = load.Properties["Additional Information/Generalized StressStrain/Kirchhoff-Love Plate Strain/epsilon22"].Value
                    e12 = load.Properties["Additional Information/Generalized StressStrain/Kirchhoff-Love Plate Strain/2epsilon12"].Value
                    k11 = load.Properties["Additional Information/Generalized StressStrain/Kirchhoff-Love Plate Strain/kappa11"].Value
                    k22 = load.Properties["Additional Information/Generalized StressStrain/Kirchhoff-Love Plate Strain/kappa22"].Value
                    k12 = load.Properties["Additional Information/Generalized StressStrain/Kirchhoff-Love Plate Strain/2kappa12"].Value
            elif SG.PlateModel.submodel == 1:
                if id1 == 0:
                    N11 = load.Properties["Additional Information/Generalized StressStrain/Reissner-Mindlin Plate Stress/N11"].Value
                    N22 = load.Properties["Additional Information/Generalized StressStrain/Reissner-Mindlin Plate Stress/N22"].Value
                    N12 = load.Properties["Additional Information/Generalized StressStrain/Reissner-Mindlin Plate Stress/N12"].Value
                    M11 = load.Properties["Additional Information/Generalized StressStrain/Reissner-Mindlin Plate Stress/M11"].Value
                    M22 = load.Properties["Additional Information/Generalized StressStrain/Reissner-Mindlin Plate Stress/M22"].Value
                    M12 = load.Properties["Additional Information/Generalized StressStrain/Reissner-Mindlin Plate Stress/M12"].Value
                    N13 = load.Properties["Additional Information/Generalized StressStrain/Reissner-Mindlin Plate Stress/N13"].Value
                    N23 = load.Properties["Additional Information/Generalized StressStrain/Reissner-Mindlin Plate Stress/N23"].Value
                else:
                    e11 = load.Properties["Additional Information/Generalized StressStrain/Reissner-Mindlin Plate Strain/epsilon11"].Value
                    e22 = load.Properties["Additional Information/Generalized StressStrain/Reissner-Mindlin Plate Strain/epsilon22"].Value
                    e12 = load.Properties["Additional Information/Generalized StressStrain/Reissner-Mindlin Plate Strain/2epsilon12"].Value
                    k11 = load.Properties["Additional Information/Generalized StressStrain/Reissner-Mindlin Plate Strain/kappa11"].Value
                    k22 = load.Properties["Additional Information/Generalized StressStrain/Reissner-Mindlin Plate Strain/kappa22"].Value
                    k12 = load.Properties["Additional Information/Generalized StressStrain/Reissner-Mindlin Plate Strain/2kappa12"].Value
                    g13 = load.Properties["Additional Information/Generalized StressStrain/Reissner-Mindlin Plate Strain/gamma13"].Value
                    g23 = load.Properties["Additional Information/Generalized StressStrain/Reissner-Mindlin Plate Strain/gamma23"].Value
        elif SG.SolidModel:
            if id1 == 0:
                s11 = load.Properties["Additional Information/Generalized StressStrain/Solid Stress/sigma11"].Value
                s22 = load.Properties["Additional Information/Generalized StressStrain/Solid Stress/sigma22"].Value
                s33 = load.Properties["Additional Information/Generalized StressStrain/Solid Stress/sigma33"].Value
                s23 = load.Properties["Additional Information/Generalized StressStrain/Solid Stress/sigma23"].Value
                s13 = load.Properties["Additional Information/Generalized StressStrain/Solid Stress/sigma13"].Value
                s12 = load.Properties["Additional Information/Generalized StressStrain/Solid Stress/sigma12"].Value
            else:
                e11 = load.Properties["Additional Information/Generalized StressStrain/Solid Strain/epsilon11"].Value
                e22 = load.Properties["Additional Information/Generalized StressStrain/Solid Strain/epsilon22"].Value
                e33 = load.Properties["Additional Information/Generalized StressStrain/Solid Strain/epsilon33"].Value
                e23 = load.Properties["Additional Information/Generalized StressStrain/Solid Strain/epsilon23"].Value
                e13 = load.Properties["Additional Information/Generalized StressStrain/Solid Strain/epsilon13"].Value
                e12 = load.Properties["Additional Information/Generalized StressStrain/Solid Strain/epsilon12"].Value

    with open(SGFileSystem.dir_file_name_sc_glb, 'w') as f:

        for i in range(SG.nmate):

            # ----- Write failure analysis parameters -------------------------

            for j in range(SG.Material[i].ntemp):

                if  FC[i] == 'Max Principal Stress':
                    utilities.writeFormat(f, 'dd', [1, num_of_constants[i]])
                    utilities.writeFormat(f, 'E', [Char_length])
                    utilities.writeFormat(f, 'EE', [constants[i]['X_t'], constants[i]['X_c']])
                elif FC[i] == 'Max Principal Strain':
                    utilities.writeFormat(f, 'dd', [2, num_of_constants[i]])
                    utilities.writeFormat(f, 'E', [Char_length])
                    utilities.writeFormat(f, 'EE', [constants[i]['Xe_t'], constants[i]['Xe_c']])
                elif FC[i] == 'Max Shear Stress':
                    utilities.writeFormat(f, 'dd', [3, num_of_constants[i]])
                    utilities.writeFormat(f, 'E', [Char_length])
                    utilities.writeFormat(f, 'E', [constants[i]['S']])
                elif FC[i] == 'Max Shear Strain':
                    utilities.writeFormat(f, 'dd', [4, num_of_constants[i]])
                    utilities.writeFormat(f, 'E', [Char_length])
                    utilities.writeFormat(f, 'E', [constants[i]['Se']])
                elif FC[i] == 'Mises Criterion':
                    utilities.writeFormat(f, 'dd', [5, num_of_constants[i]])
                    utilities.writeFormat(f, 'E', [Char_length])
                    utilities.writeFormat(f, 'E', [constants[i]['X_t']])
                elif FC[i] == 'Max Stress':
                    utilities.writeFormat(f, 'dd', [1, num_of_constants[i]])
                    utilities.writeFormat(f, 'E', [Char_length])
                    utilities.writeFormat(f, 'E'*9, [constants[i]['X_t'], constants[i]['Y_t'], constants[i]['Z_t'],
                                                        constants[i]['X_c'], constants[i]['Y_c'], constants[i]['Z_c'],
                                                        constants[i]['R'],   constants[i]['T'],   constants[i]['S']])
                elif FC[i] == 'Max Strain':
                    utilities.writeFormat(f, 'dd', [2, num_of_constants[i]])
                    utilities.writeFormat(f, 'E', [Char_length])
                    utilities.writeFormat(f, 'E'*9, [constants[i]['Xe_t'], constants[i]['Ye_t'], constants[i]['Ze_t'],
                                                        constants[i]['Xe_c'], constants[i]['Ye_c'], constants[i]['Ze_c'],
                                                        constants[i]['Re'],   constants[i]['Te'],   constants[i]['Se']])
                elif FC[i] == 'Tsai-Hill':
                    utilities.writeFormat(f, 'dd', [3, num_of_constants[i]])
                    utilities.writeFormat(f, 'E', [Char_length])
                    utilities.writeFormat(f, 'E'*6, [constants[i]['X_t'], constants[i]['Y_t'], constants[i]['Z_t'],
                                                        constants[i]['R'],   constants[i]['T'],   constants[i]['S']])
                elif FC[i] == 'Tsai-Wu':
                    utilities.writeFormat(f, 'dd', [4, num_of_constants[i]])
                    utilities.writeFormat(f, 'E', [Char_length])
                    utilities.writeFormat(f, 'E'*9, [constants[i]['X_t'], constants[i]['Y_t'], constants[i]['Z_t'],
                                                    constants[i]['X_c'], constants[i]['Y_c'], constants[i]['Z_c'],
                                                    constants[i]['R'],   constants[i]['T'],   constants[i]['S']])
                elif FC[i] == 'Hashin':
                    utilities.writeFormat(f, 'dd', [5, num_of_constants[i]])
                    utilities.writeFormat(f, 'E', [Char_length])
                    utilities.writeFormat(f, 'E'*6, [constants[i]['X_t'], constants[i]['Y_t'], constants[i]['X_c'],
                                                        constants[i]['Y_c'], constants[i]['R'],   constants[i]['T']])

            f.write('\n')

        utilities.writeFormat(f, 'd', [id1])
        f.write('\n')

        if F_type == 'FE':
            utilities.writeFormat(f, 'ddd', [istr1, istr2, idiv])
            f.write('\n')
        elif F_type == 'FI':
            if SG.BeamModel:
                if SG.BeamModel.submodel == 0:
                    if id1 == 0:
                        utilities.writeFormat(f, 'EEEE', [F1, M1, M2, M3])
                    else:
                        utilities.writeFormat(f, 'EEEE', [e11, k11, k12, k13])
                elif SG.BeamModel.submodel == 1:
                    if id1 == 0:
                        utilities.writeFormat(f, 'EEEEEE', [F1, F2, F3, M1, M2, M3])
                    else:
                        utilities.writeFormat(f, 'EEEEEE', [e11, g12, g13, k11, k12, k13])
            elif SG.PlateModel:
                if SG.PlateModel.submodel == 0:
                    if id1 == 0:
                        utilities.writeFormat(f, 'EEEEEE', [N11, N22, N12, M11, M22, M12])
                    else: 
                        utilities.writeFormat(f, 'EEEEEE', [e11, e22, e12, k11, k22, k12])
                elif SG.PlateModel.submodel == 1:
                    if id1 == 0:
                        utilities.writeFormat(f, 'EEEEEEEE', [N11, N22, N12, M11, M22, M12, N13, N23])
                    else: 
                        utilities.writeFormat(f, 'EEEEEEEE', [e11, e22, e12, k11, k22, k12, g13, g23])
            elif SG.SolidModel:
                if id1 == 0:
                    utilities.writeFormat(f, 'EEEEEE', [s11, s22, s33, s23, s13, s12])
                else: 
                    utilities.writeFormat(f, 'EEEEEE', [e11, e22, e33, e23, e13, e12])
            f.write('\n')

    SGResult = sg_result.SGResult()
    with open(SGFileSystem.user_dir + 'SGResult.pickle', 'rb') as f:
        SGResult = pickle.load(f)

    SGResult.failureType = F_type

    # save SGResult instance to file so that we can use it later
    with open(SGFileSystem.user_dir + 'SGResult.pickle', 'wb') as f:
        pickle.dump(SGResult, f)

    ExtAPI.Log.WriteMessage("Creating Failure Analysis input file finished.")

    return True


def SwiftCompFailureRun(arg):
    ''' Run SwiftComp failure analysis'''

    ExtAPI, fct = arg

    fct(0,"Begin failure analysis...")

    SGFileSystem = sg_filesystem.SGFileSystem(ExtAPI)

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
    arg3 = SGResult.failureType

    # ================================================================
    # arg4: The version of SwiftComp is running:
    # ----------------------------------------------------------------
    # B for standard version
    # P for professional version
    # No arguments for parallel version
    # ================================================================
    arg4 = ''

    failure_time_start = time.clock()

    # Run failure analysis! save stdout to a file named temp
    command = ['SwiftComp', arg1, arg2, arg3, arg4, '>', SGFileSystem.user_dir+'temp']
    exitCode = subprocess.call(command, cwd=SGFileSystem.user_dir, shell=True)
    if exitCode != 0:
        return False

    failure_time_end = time.clock()

    # failure analysis time
    SGResult.failureTime = failure_time_end - failure_time_start

    fct(95,"Finish failure analysis...")

    # Get standard output
    with open(SGFileSystem.user_dir + 'temp', 'r') as f:
        SGResult.failureStdout = f.read()
    os.remove(SGFileSystem.user_dir + 'temp')

    # Check whether the homogenization is successful or not.
    if errorcheck.failureNotSuccessful(ExtAPI, SGResult.failureStdout):
        return False

    # Display the result file *.sc.fi
    os.startfile(SGFileSystem.dir_file_name_sc_fi)

    # write solve.out file
    with open('solve.out', 'w') as f:
        f.write(SGResult.failureStdout)

    # save updated SGResult
    with open(SGFileSystem.user_dir + 'SGResult.pickle', 'wb') as f:
        pickle.dump(SGResult, f)

    fct(100,"Stored failure analysis Result...")

    return True
