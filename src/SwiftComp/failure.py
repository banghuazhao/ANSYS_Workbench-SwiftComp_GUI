import failure_func

import sg
import sg_filesystem


def failureStregnthCanAddAtTree(currentAnalysis, load):
    return currentAnalysis.Children.Count == 2 and currentAnalysis.SolverName == 'SwiftCompFailure@SwiftComp'


def failureStregnthOnGenerateAtTree(load, fct):

    arguments = [ExtAPI, load, 'F']

    return ExtAPI.Application.InvokeUIThread(failure_func.SwiftCompFailureInput, arguments)


def failureEnvelopeCanAddAtTree(currentAnalysis, load):
    return currentAnalysis.Children.Count == 2 and currentAnalysis.SolverName == 'SwiftCompFailure@SwiftComp'


def failureEnvelopeOnGenerateAtTree(load, fct):

    arguments = [ExtAPI, load, 'FE']

    return ExtAPI.Application.InvokeUIThread(failure_func.SwiftCompFailureInput, arguments)

def failureIndexCanAddAtTree(currentAnalysis, load):
    return currentAnalysis.Children.Count == 2 and currentAnalysis.SolverName == 'SwiftCompFailure@SwiftComp'


def failureIndexGeneralizedStressStrainOnActivate(load, prop):
    SGFileSystem = sg_filesystem.SGFileSystem(ExtAPI)

    SG = sg.StructureGenome()
    with open(SGFileSystem.user_dir + 'SG.pickle', 'rb') as f:
        SG = pickle.load(f)

    if load.Properties["Additional Information/Generalized StressStrain"].Value == 'Stress':
        id1 = 0
    else:
        id1 = 1

    load.Properties["Additional Information/Generalized StressStrain/Euler-Bernoulli Beam Stress"].Value   = False
    load.Properties["Additional Information/Generalized StressStrain/Euler-Bernoulli Beam Strain"].Value   = False
    load.Properties["Additional Information/Generalized StressStrain/Timoshenko Beam Stress"].Value        = False
    load.Properties["Additional Information/Generalized StressStrain/Timoshenko Beam Strain"].Value        = False
    load.Properties["Additional Information/Generalized StressStrain/Kirchhoff-Love Plate Stress"].Value   = False
    load.Properties["Additional Information/Generalized StressStrain/Kirchhoff-Love Plate Strain"].Value   = False
    load.Properties["Additional Information/Generalized StressStrain/Reissner-Mindlin Plate Stress"].Value = False
    load.Properties["Additional Information/Generalized StressStrain/Reissner-Mindlin Plate Strain"].Value = False
    load.Properties["Additional Information/Generalized StressStrain/Solid Stress"].Value                  = False
    load.Properties["Additional Information/Generalized StressStrain/Solid Strain"].Value                  = False
    if SG.BeamModel:
        if SG.BeamModel.submodel == 0:
            if id1 == 0:
                load.Properties["Additional Information/Generalized StressStrain/Euler-Bernoulli Beam Stress"].Value = True
            else:
                load.Properties["Additional Information/Generalized StressStrain/Euler-Bernoulli Beam Strain"].Value = True
        elif SG.BeamModel.submodel == 1:
            if id1 == 0:
                load.Properties["Additional Information/Generalized StressStrain/Timoshenko Beam Stress"].Value = True
            else:
                load.Properties["Additional Information/Generalized StressStrain/Timoshenko Beam Strain"].Value = True
    elif SG.PlateModel:
        if SG.PlateModel.submodel == 0:
            if id1 == 0:
                load.Properties["Additional Information/Generalized StressStrain/Kirchhoff-Love Plate Stress"].Value = True
            else:
                load.Properties["Additional Information/Generalized StressStrain/Kirchhoff-Love Plate Strain"].Value = True
        elif SG.PlateModel.submodel == 1:
            if id1 == 0:
                load.Properties["Additional Information/Generalized StressStrain/Reissner-Mindlin Plate Stress"].Value = True
            else:
                load.Properties["Additional Information/Generalized StressStrain/Reissner-Mindlin Plate Strain"].Value = True
    elif SG.SolidModel:
        if id1 == 0:
            load.Properties["Additional Information/Generalized StressStrain/Solid Stress"].Value = True
        else:
            load.Properties["Additional Information/Generalized StressStrain/Solid Strain"].Value = True

def failureIndexOnGenerateAtTree(load, fct):

    arguments = [ExtAPI, load, 'FI']

    return ExtAPI.Application.InvokeUIThread(failure_func.SwiftCompFailureInput, arguments)


def EulerBernoulliBeamStressVisible(entity, p):
    return p.Value


def EulerBernoulliBeamStrainVisible(entity, p):
    return p.Value


def TimoshenkoBeamStressVisible(entity, p):
    return p.Value 


def TimoshenkoBeamStrainVisible(entity, p):
    return p.Value


def KirchhoffLovePlateStressVisible(entity, p):
    return p.Value


def KirchhoffLovePlateStrainVisible(entity, p):
    return p.Value


def ReissnerMindlinPlateStressVisible(entity, p):
    return p.Value


def ReissnerMindlinPlateStrainVisible(entity, p):
    return p.Value


def solidStressVisible(entity, p):
    return p.Value


def solidStrainVisible(entity, p):
    return p.Value


def SwiftCompFailure(s, fct):
    arguments = [ExtAPI, fct]
    return ExtAPI.Application.InvokeUIThread(failure_func.SwiftCompFailureRun, arguments)