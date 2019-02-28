import pickle

import sg
import sg_node
import sg_element



class SGResult(object):
    '''SG Result class. Store homogenization and dehomogenization result'''

    def __init__(self):

        self.result_name = None

        self.BeamModel = None
        self.PlateModel = None
        self.SolidModel = None
        self.density = None

        self.homInputTime = 0.0
        self.homTime = 0.0
        self.hommStdout = ''

        self.dehomTime = 0.0
        self.dehommStdout = ''

        self.Displacement = None
        self.Strain = None
        self.Stress = None

        self.failureType = None
        self.failureTime = 0.0
        self.failureStdout = ''

    def setMacroModel(self, macroModel):
        if macroModel == "Beam Model":
            self.BeamModel = BeamModel()
        elif macroModel == "Plate Model":
            self.PlateModel = PlateModel()
        elif macroModel == "Solid Model":
            self.SolidModel = SolidModel()


    def setBeamModelResult(self, SGFileSystem):
        with open(SGFileSystem.dir_file_name_sc_k, 'r') as f:
            content = f.read().split('\n')
            content = [x.strip() for x in content]

        # stiffness
        index =  [i for i, s in enumerate(content) if 'Stiffness' in s]
        if index:
            self.BeamModel.submodel = 0
            self.BeamModel.stiffness = [[0.0] * 4] * 4
            for i in range(4):
                self.BeamModel.stiffness[i] = map(float, content[index[0] + i + 2].split())

        # compliance
        index =  [i for i, s in enumerate(content) if 'Compliance' in s]
        if index:
            self.BeamModel.compliance = [[0.0] * 4] * 4
            for i in range(4):
                self.BeamModel.compliance[i] = map(float, content[index[0] + i + 2].split())

        # Timoshenko Stiffness
        index =  [i for i, s in enumerate(content) if 'Timoshenko Stiffness' in s]
        if index:
            self.BeamModel.submodel = 1
            self.BeamModel.TimoshenkoStiffness = [[0.0] * 6] * 6
            for i in range(6):
                self.BeamModel.TimoshenkoStiffness[i] = map(float, content[index[0] + i + 2].split())

        # Timoshenko Compliance
        index =  [i for i, s in enumerate(content) if 'Timoshenko Compliance' in s]
        if index:
            self.BeamModel.TimoshenkoCompliance = [[0.0] * 6] * 6
            for i in range(6):
                self.BeamModel.TimoshenkoCompliance[i] = map(float, content[index[0] + i + 2].split())

        # shear center
        index =  [i for i, s in enumerate(content) if 'Shear Center' in s]
        if index:
            self.BeamModel.shearCenter = [0.0] * 2
            self.BeamModel.shearCenter = map(float, content[index[0] + 2].split())

        # density
        index =  [i for i, s in enumerate(content) if 'Density' in s]
        if index:
            self.density = float(content[index[0]].split()[-1])


    def setPlateModelResult(self, SGFileSystem):
        with open(SGFileSystem.dir_file_name_sc_k, 'r') as f:
            content = f.read().split('\n')
            content = [x.strip() for x in content]

        # stiffness
        index =  [i for i, s in enumerate(content) if 'Stiffness' in s]
        if index:
            self.PlateModel.submodel = 0
            self.PlateModel.stiffness = [[0.0] * 6] * 6
            for i in range(6):
                self.PlateModel.stiffness[i] = map(float, content[index[0] + i + 2].split())

        # compliance
        index =  [i for i, s in enumerate(content) if 'Compliance' in s]
        if index:
            self.PlateModel.compliance = [[0.0] * 6] * 6
            for i in range(6):
                self.PlateModel.compliance[i] = map(float, content[index[0] + i + 2].split())

        # in-place properties
        index =  [i for i, s in enumerate(content) if 'In-Plane' in s]
        if index:
            self.PlateModel.inPlane = {}
            self.PlateModel.inPlane['E1']      = float(content[index[0]+2].split()[-1])
            self.PlateModel.inPlane['E2']      = float(content[index[0]+3].split()[-1])
            self.PlateModel.inPlane['G12']     = float(content[index[0]+4].split()[-1])
            self.PlateModel.inPlane['nu12']    = float(content[index[0]+5].split()[-1])
            self.PlateModel.inPlane['eta121']  = float(content[index[0]+6].split()[-1])
            self.PlateModel.inPlane['eta122']  = float(content[index[0]+7].split()[-1])

        # flexural properties
        index =  [i for i, s in enumerate(content) if 'Flexural' in s]
        if index:
            self.PlateModel.flexural = {}
            self.PlateModel.flexural['E1']      = float(content[index[0]+2].split()[-1])
            self.PlateModel.flexural['E2']      = float(content[index[0]+3].split()[-1])
            self.PlateModel.flexural['G12']     = float(content[index[0]+4].split()[-1])
            self.PlateModel.flexural['nu12']    = float(content[index[0]+5].split()[-1])
            self.PlateModel.flexural['eta121']  = float(content[index[0]+6].split()[-1])
            self.PlateModel.flexural['eta122']  = float(content[index[0]+7].split()[-1])

        # density
        index =  [i for i, s in enumerate(content) if 'Density' in s]
        if index:
            self.density = float(content[index[0]].split()[-1])


    def setSolidModelResult(self, SGFileSystem):
        with open(SGFileSystem.dir_file_name_sc_k, 'r') as f:
            content = f.read().split('\n')
            content = [x.strip() for x in content]

        # stiffness
        index =  [i for i, s in enumerate(content) if 'Stiffness' in s]
        if index:
            self.SolidModel.stiffness = [[0.0] * 6] * 6
            for i in range(6):
                self.SolidModel.stiffness[i] = map(float, content[index[0] + i + 2].split())

        # compliance
        index =  [i for i, s in enumerate(content) if 'Compliance' in s]
        if index:
            self.SolidModel.compliance = [[0.0] * 6] * 6
            for i in range(6):
                self.SolidModel.compliance[i] = map(float, content[index[0] + i + 2].split())

        # engineering constants
        index =  [i for i, s in enumerate(content) if 'Engineering' in s]
        if index:
            self.SolidModel.engineering = {}
            self.SolidModel.engineering['E1']   = float(content[index[0]+2].split()[-1])
            self.SolidModel.engineering['E2']   = float(content[index[0]+3].split()[-1])
            self.SolidModel.engineering['E3']   = float(content[index[0]+4].split()[-1])
            self.SolidModel.engineering['G12']  = float(content[index[0]+5].split()[-1])
            self.SolidModel.engineering['G13']  = float(content[index[0]+6].split()[-1])
            self.SolidModel.engineering['G23']  = float(content[index[0]+7].split()[-1])
            self.SolidModel.engineering['nu12'] = float(content[index[0]+8].split()[-1])
            self.SolidModel.engineering['nu13'] = float(content[index[0]+9].split()[-1])
            self.SolidModel.engineering['nu23'] = float(content[index[0]+10].split()[-1])

        # density
        index =  [i for i, s in enumerate(content) if 'Density' in s]
        if index:
            self.density = float(content[index[0]].split()[-1])


    def setDisplacement(self, SGFileSystem):
        ''' set displacment class
       
        SGResult.Displacement.Node[i].displacement: [u1, u2, u3]
        '''
        self.Displacement = SGDisplacement()
        with open(SGFileSystem.dir_file_name_sc_u, 'r') as f:
            for line in f:
                line = line.strip()
                if line == '\n' or line == '':
                    continue
                else:
                    line = line.split()
                    dispplacement = [float(line[1]), float(line[2]), float(line[3])]
                    Node = sg_node.SGNode()
                    Node.displacement = dispplacement
                    self.Displacement.Node.append(Node)

    def setStress(self, SGFileSystem):
        SG = sg.StructureGenome()
        with open(SGFileSystem.user_dir + 'SG.pickle', 'rb') as f:
            SG = pickle.load(f)

        self.Stress = SGStress()
        with open(SGFileSystem.dir_file_name_sc_sn, 'r') as f:
            for i in range(SG.nelem):
                stress = []
                for j in range(SG.Element[i].total_node):
                    line = f.readline()
                    line = line.strip()
                    line = line.split()
                    if SG.nSG == 2:
                        # 11 22 33 12 23 13
                        # 8  9  10 13 11 12
                        stress.extend([float(line[8]), float(line[9]), float(line[10]), float(line[13]), float(line[11]), float(line[12])])
                    elif SG.nSG == 3:
                        # 11 22 33 12 23 13
                        # 9  10 11 14 12 13
                        stress.extend([float(line[9]), float(line[10]), float(line[11]), float(line[14]), float(line[12]), float(line[13])])
                Element = sg_element.SGElement()
                Element.stress_corner = stress[:SG.Element[i].total_corner_node * 6]
                self.Stress.Element.append(Element)


    def setStrain(self, SGFileSystem):
        SG = sg.StructureGenome()
        with open(SGFileSystem.user_dir + 'SG.pickle', 'rb') as f:
            SG = pickle.load(f)

        self.Strain = SGStrain()
        with open(SGFileSystem.dir_file_name_sc_sn, 'r') as f:
            for i in range(SG.nelem):
                strain = []
                for j in range(SG.Element[i].total_node):
                    line = f.readline()
                    line = line.strip()
                    line = line.split()
                    if SG.nSG == 2:
                        # 11 22 33 12 23 13
                        # 2  3  4  7  5  6
                        strain.extend([float(line[2]), float(line[3]), float(line[4]), float(line[7]), float(line[5]), float(line[6])])
                    elif SG.nSG == 3:
                        # 11 22 33 12 23 13
                        # 3  4  5  8  6  7
                        strain.extend([float(line[3]), float(line[4]), float(line[5]), float(line[8]), float(line[6]), float(line[7])])
                Element = sg_element.SGElement()
                Element.strain_corner = strain[:SG.Element[i].total_corner_node * 6]
                self.Strain.Element.append(Element)


class BeamModel(object):
    def __init__(self):
        self.submodel = None
        self.stiffness = None
        self.compliance = None
        self.TimoshenkoStiffness = None
        self.TimoshenkoCompliance = None
        self.shearCenter = None

class PlateModel(object):
    def __init__(self):
        self.submodel = None
        self.stiffness = None
        self.compliance = None
        self.inPlane = None
        self.flexural = None

class SolidModel(object):
    def __init__(self):
        self.stiffness = None
        self.compliance = None
        self.engineering = None


class SGDisplacement(object):
    def __init__(self):
        self.Node = []

class SGStress(object):
    def __init__(self):
        self.Element = []

class SGStrain(object):
    def __init__(self):
        self.Element = []