import utilities
import ansys_materials
import sg_material
import sg_node
import sg_element
import sg_layer

class StructureGenome(object):
    '''Structure Genome class: contain all the information for a SG

    Attributes:
    BeamModel: Beam Model object
    PlateModel: Plate Model object
    SolidModel: Solid Model object
    analysis, elem_flag, trans_flag, temp_flag: common flag
    aperiodic: indicate wheather aperiodic or note
    py1, py2, py3: value for aperiodic
    nSG, nnode, nelem, nmate, nslave, nlayer: mesh control parameters
    '''

    def __init__(self):
        self.BeamModel = None
        self.PlateModel = None
        self.SolidModel = None

        self.analysis = 0
        self.elem_flag = 0
        self.trans_flag = 0
        self.temp_flag = 0

        self.aperiodic = False
        self.py1 = 0
        self.py2 = 0
        self.py3 = 0

        self.nSG = 0
        self.nnode = 0
        self.nelem = 0
        self.nmate = 0
        self.nslave = 0
        self.nlayer = 0
        
        self.Material = None
        self.Node = None
        self.Element = None
        self.Layer = None
        self.omega =0

    def setMacroModel(self, macroModel):
        if macroModel == "Beam Model":
            self.BeamModel = BeamModel()
        elif macroModel == "Plate Model":
            self.PlateModel = PlateModel()
        elif macroModel == "Solid Model":
            self.SolidModel = SolidModel()

    def setBeamModelControlParameters(self, submodel, beam_ini_curvatures, beam_ini_oblique, common_flag, aperiodic_flag):   
        self.BeamModel.setBeamModel(submodel, beam_ini_curvatures, beam_ini_oblique)
        self.setCommonFlag(common_flag)
        self.setAperiodicFlag(aperiodic_flag)

    def setPlateModelControlParameters(self, submodel, plate_ini_curvatures, common_flag, aperiodic_flag):
        self.PlateModel.setPlateModel(submodel, plate_ini_curvatures)
        self.setCommonFlag(common_flag)
        self.setAperiodicFlag(aperiodic_flag)

    def setSolidModelControlParameters(self, common_flag, aperiodic_flag):  
        self.setCommonFlag(common_flag)
        self.setAperiodicFlag(aperiodic_flag)

    def setCommonFlag(self, common_flag):
        '''Get: analysis, elem_flag, trans_flag, temp_flag'''

        analysis_dictionary = {'Elastic': 0, 'Thermoelastic': 1, 'Conduction': 2, 
                               'Piezoelectric/Piezomagnetic': 3, 'Thermoepiezoelectric/Thermopiezomagnetic': 4,
                               'Piezoeletromagnetic': 5, 'Thermopiezoeletromagnetic': 6}

        elem_flag_dictionary = {'Regular Elements': 0, 'One Dimension Degenerated': 1, 'Two Dimension Degenerated': 2}

        trans_flag_dictionary = {'Global Coordinate System': 0, 'Element Coordinate System': 1}

        temp_flag_dictionary = {'Uniform': 0, 'Not-uniform': 1}

        self.analysis = analysis_dictionary[common_flag[0]]
        self.elem_flag = elem_flag_dictionary[common_flag[1]]
        self.trans_flag = trans_flag_dictionary[common_flag[2]]
        self.temp_flag = temp_flag_dictionary[common_flag[3]]

    def setAperiodicFlag(self, aperiodic_flag):
        '''Get: py1, py2, py3'''
 
        aperiodic_flag_dictionary = {'No': 0, 'Yes': 1}

        if len(aperiodic_flag) == 1:
            self.py1 = aperiodic_flag_dictionary[aperiodic_flag[0]]
        elif  len(aperiodic_flag) == 2:
            self.py1 = aperiodic_flag_dictionary[aperiodic_flag[0]]
            self.py2 = aperiodic_flag_dictionary[aperiodic_flag[1]]
        elif  len(aperiodic_flag) == 3:
            self.py1 = aperiodic_flag_dictionary[aperiodic_flag[0]]
            self.py2 = aperiodic_flag_dictionary[aperiodic_flag[1]]
            self.py3 = aperiodic_flag_dictionary[aperiodic_flag[2]]

        if self.py1 + self.py2 + self.py3 > 0:
            self.aperiodic = True


    def set1DSG(self, ExtAPI):
        self.nSG = 1
        self.Material1DSG = []
        self.Thickness1DSG = []
        self.Angle1DSG = []

        for x in ExtAPI.DataModel.Project.Model.Children:
            if x.Name == 'Imported Plies':
                ImportedPlies = x

        ACP = ImportedPlies.Children[0]
        ModelingGroup = ACP.Children[0]
        ModelingPlies = ModelingGroup.Children

        for ModelingPly in ModelingPlies:
            P1_ModelingPly = ModelingPly.Children[0]
            for layer in P1_ModelingPly.Children:
                self.Material1DSG.append(layer.Material)
                self.Thickness1DSG.append(float(str(layer.Thickness).split()[0]))
                self.Angle1DSG.append(float(str(layer.Angle).split()[0]))

        # the SwiftComp convention is from bottom to top
        self.Material1DSG = self.Material1DSG[::-1]
        self.Thickness1DSG = self.Thickness1DSG[::-1]
        self.Angle1DSG = self.Angle1DSG[::-1]
        
        self.nelem = len(self.Material1DSG)
        self.nnode = 4 * self.nelem + 1
        self.nmate = len(set(self.Material1DSG))
        self.nslave = 0
        self.nanlge = len(set(self.Angle1DSG))
        self.nlayer = self.nmate * self.nanlge
        self.omega = 1.0

        # node coordinate
        self.Node = []
        half_total_thickness = float(sum(self.Thickness1DSG)) / 2
        Node = sg_node.SGNode()
        Node.coordinate = [0.0, 0.0, -half_total_thickness]
        self.Node.append(Node)
        for i, thickness in enumerate(self.Thickness1DSG):
            for j in range(4):
                Node = sg_node.SGNode()
                z = sum([x for x in self.Thickness1DSG[:i]]) + float(j+1)/4 * thickness - half_total_thickness
                Node.coordinate = [0.0, 0.0, z]
                self.Node.append(Node)

        # layer block
        material_list = list(set(self.Material1DSG))
        angle_list = list(set(self.Angle1DSG))
        self.Layer = []
        for i in range(self.nmate):
            for j in range(self.nanlge):
                Layer = sg_layer.SGLayer()
                Layer.material_id = i + 1
                Layer.angle = angle_list[j]
                self.Layer.append(Layer)

        # element connectivity
        self.Element = []
        for i in range(self.nelem):
            Element = sg_element.SGElement()
            Element.total_node = 5
            Element.total_corner_node = 2
            Element.connectivity = [1 + 4*i, 5 + 4*i, 2 + 4*i, 4 + 4*i, 3 + 4*i]
            for j, Layer in enumerate(self.Layer):
                if material_list[Layer.material_id-1] == self.Material1DSG[i] and Layer.angle == self.Angle1DSG[i]:
                    Element.layer_id = j + 1
                    break
            self.Element.append(Element)

        # material connectivity
        materials = ExtAPI.DataModel.Project.EngineeringDataLibrary.GetMaterials()
        materials_name_list = [mat.DisplayName for mat in materials]
        self.Material = []
        for i in range(self.nmate):
            material = materials[materials_name_list.index(material_list[i])]
            property_names = ansys_materials.GetListMaterialProperties(material)
            ntemp = 1; T = [0.0]; density = [0.0]

            density_dictionary = ansys_materials.GetMaterialPropertyByName(material, "Density")
            if density_dictionary:
                density_list = density_dictionary.get('Density')
                temperature_list = density_dictionary.get('Temperature') 
                if temperature_list:  # there is Temperature key
                    ntemp = len(temperature_list) - 1
                    T = temperature_list[1:ntemp+1]
                    density = density_list[1:ntemp+1]

            elastic_dictionary = ansys_materials.GetMaterialPropertyByName(material, "Elasticity")
            if elastic_dictionary:
                # isotropic
                if "Young's Modulus" in elastic_dictionary:
                    isotropy = 0
                    E  = elastic_dictionary["Young's Modulus"][1:ntemp+1]
                    nu = elastic_dictionary["Poisson's Ratio"][1:ntemp+1]
                elif "Young's Modulus X direction" in elastic_dictionary:  #  orthotropic
                    isotropy = 1
                    E1   = elastic_dictionary["Young's Modulus X direction"][1:ntemp+1]
                    E2   = elastic_dictionary["Young's Modulus Y direction"][1:ntemp+1]
                    E3   = elastic_dictionary["Young's Modulus Z direction"][1:ntemp+1]
                    G12  = elastic_dictionary["Shear Modulus XY"][1:ntemp+1]
                    G13  = elastic_dictionary["Shear Modulus XZ"][1:ntemp+1]
                    G23  = elastic_dictionary["Shear Modulus YZ"][1:ntemp+1]
                    nu12 = elastic_dictionary["Poisson's Ratio XY"][1:ntemp+1]
                    nu13 = elastic_dictionary["Poisson's Ratio XZ"][1:ntemp+1]
                    nu23 = elastic_dictionary["Poisson's Ratio YZ"][1:ntemp+1]
                elif  'D[*,1]' in elastic_dictionary:  # anisotropic
                    isotropy = 2
                    column1 = elastic_dictionary["D[*,1]"][1:]
                    column2 = elastic_dictionary["D[*,2]"][1:]; column2[0] = column1[1]
                    column3 = elastic_dictionary["D[*,3]"][1:]; column3[0] = column1[2]; column3[1] = column2[2]
                    column4 = elastic_dictionary["D[*,4]"][1:]; column4[0] = column1[3]; column4[1] = column2[3]; column4[2] = column3[3]
                    column5 = elastic_dictionary["D[*,5]"][1:]; column5[0] = column1[4]; column5[1] = column2[4]; column5[2] = column3[4]; column5[3] = column4[4]
                    column6 = elastic_dictionary["D[*,6]"][1:]; column6[0] = column1[5]; column6[1] = column2[5]; column6[2] = column3[5]; column6[3] = column4[5]; column6[4] = column5[5]
                    D = []
                    for k in range(6):
                        row = [[column1[k], column2[k], column3[k], column4[k], column5[k], column6[k]]]
                        D += row
                    C = D
                    C[3], C[4] = C[4], C[3]
                    C[4], C[5] = C[5], C[4]
                    C = utilities.transpose(C)
                    C[4], C[5] = C[5], C[4]
                    C[3], C[4] = C[4], C[3]
                    C = utilities.transpose(C)

            Material = sg_material.SGMaterial(isotropy, ntemp, 1)
            Material.name = material_list[i]
            if isotropy == 0:
                Material.setIsotropicMaterialProperty(ntemp, T, density, E, nu)
            elif isotropy == 1:
                Material.setOrthotropicMaterialProperty(ntemp, T, density, E1, E2, E3, G12, G13, G23, nu12, nu13, nu23)
            elif isotropy == 2:
                Material.setAnisotropicMaterialProperty(ntemp, T, density, C)

            self.Material.append(Material)
                   

    def setMaterial(self, ExtAPI):
        ''' set Material attribute'''

        self.Material = []
       
        # total number of parts
        part_total = ExtAPI.DataModel.GeoData.Assemblies[0].Parts.Count

        for part in range(part_total):

            # total number of bodies for current part
            body_total = ExtAPI.DataModel.GeoData.Assemblies[0].Parts[part].Bodies.Count

            for body in range(body_total):

                # body id for this body
                body_id = ExtAPI.DataModel.GeoData.Assemblies[0].Parts[part].Bodies[body].Id

                # material object for this body (Ansys.EngineeringData.Material.MaterialClass)
                material = ExtAPI.DataModel.GeoData.Assemblies[0].Parts[part].Bodies[body].Material

                # list of material property names for this body
                # possible names are:
                # Isotropic (Structural Steel):
                # ['Appearance', 'Compressive Ultimate Strength', 'Compressive Yield Strength', 'Density', 'Tensile Yield Strength', 
                # 'Tensile Ultimate Strength', 'Coefficient of Thermal Expansion', 'Specific Heat', 'Thermal Conductivity', 'S-N Curve', 
                # 'Strain-Life Parameters', 'Resistivity', 'Elasticity', 'Relative Permeability', 'Field Variable']
                # Orthotropic (
                # ['Density', 'Ply Type', 'Elasticity', 'Strain Limits', 'Stress Limits', 'Coefficient of Thermal Expansion',
                # 'Puck Constants', 'Additional Puck Constants', 'Tsai-Wu Constants', 'Appearance']
                property_names = ansys_materials.GetListMaterialProperties(material)

                ntemp = 1; T = [0.0]; density = [0.0]

                if 'Density' in property_names:

                    # Obtain density dictionary
                    # Examples: 
                    # {'Density': ['kg m^-3', 1160]}
                    # {'Density': ['kg m^-3', 7850, 23], 'Temperature': ['C', 1, 2]} 
                    density_dictionary = ansys_materials.GetMaterialPropertyByName(material, "Density")

                    density_list = density_dictionary.get('Density')

                    temperature_list = density_dictionary.get('Temperature') 

                    if temperature_list:  # there is Temperature key
                        ntemp = len(temperature_list) - 1
                        T = temperature_list[1:ntemp+1]
                        density = density_list[1:ntemp+1]
               
                if "Elasticity" in property_names:

                    # Obtain Elasticity dictionary
                    # Examples: 
                    # isotropic: {'Poisson's Ratio': ['', 0.35], 'Bulk Modulus': ['Pa', 4200000000], 'Young's Modulus': ['Pa', 3780000000], 'Shear Modulus': ['Pa', 1400000000]}
                    # isotropic: {'Shear Modulus': ['Pa', 10.4545454545455, 76923076923.0769], 'Bulk Modulus': ['Pa', 9.58333333333333, 166666666666.667], 
                    #             'Poisson's Ratio': ['', 0.1, 0.3], 'Temperature': ['C', 1, 2], 'Young's Modulus': ['Pa', 23, 200000000000]}
                    # orthotropic: {'Poisson's Ratio YZ': ['', 0.3], 'Young's Modulus Z direction': ['Pa', 9000000000], 'Poisson's Ratio XZ': ['', 0.3], 'Young's Modulus Y direction':
                    #               ['Pa', 91820000000], 'Young's Modulus X direction': ['Pa', 91820000000], 'Shear Modulus XY': ['Pa', 19500000000], 'Shear Modulus YZ': ['Pa', 3000000000], 
                    #               'Shear Modulus XZ': ['Pa', 3000000000], 'Poisson's Ratio XY': ['', 0.05]}
                    # anisotropic: {'D[*,3]': ['Pa', 7.88860905221012E-31, 7.88860905221012E-31, 166000000000, 0, 0, 0], 
                    #               'D[*,2]': ['Pa', 7.88860905221012E-31, 166000000000, 64000000000, 0, 0, 0], 
                    #               'D[*,1]': ['Pa', 166000000000, 64000000000, 64000000000, 0, 0, 0], 
                    #               'D[*,6]': ['Pa', 7.88860905221012E-31, 7.88860905221012E-31, 7.88860905221012E-31, 7.88860905221012E-31, 7.88860905221012E-31, 80000000000], 
                    #               'D[*,5]': ['Pa', 7.88860905221012E-31, 7.88860905221012E-31, 7.88860905221012E-31, 7.88860905221012E-31, 80000000000, 0], 
                    #               'D[*,4]': ['Pa', 7.88860905221012E-31, 7.88860905221012E-31, 7.88860905221012E-31, 80000000000, 0, 0]}
                    elastic_dictionary = ansys_materials.GetMaterialPropertyByName(material, "Elasticity")

                    # isotropic
                    if "Young's Modulus" in elastic_dictionary:
                        isotropy = 0
                        E  = elastic_dictionary["Young's Modulus"][1:ntemp+1]
                        nu = elastic_dictionary["Poisson's Ratio"][1:ntemp+1]
                    elif "Young's Modulus X direction" in elastic_dictionary:  #  orthotropic
                        isotropy = 1
                        E1   = elastic_dictionary["Young's Modulus X direction"][1:ntemp+1]
                        E2   = elastic_dictionary["Young's Modulus Y direction"][1:ntemp+1]
                        E3   = elastic_dictionary["Young's Modulus Z direction"][1:ntemp+1]
                        G12  = elastic_dictionary["Shear Modulus XY"][1:ntemp+1]
                        G13  = elastic_dictionary["Shear Modulus XZ"][1:ntemp+1]
                        G23  = elastic_dictionary["Shear Modulus YZ"][1:ntemp+1]
                        nu12 = elastic_dictionary["Poisson's Ratio XY"][1:ntemp+1]
                        nu13 = elastic_dictionary["Poisson's Ratio XZ"][1:ntemp+1]
                        nu23 = elastic_dictionary["Poisson's Ratio YZ"][1:ntemp+1]
                    elif  'D[*,1]' in elastic_dictionary:  # anisotropic
                        isotropy = 2
                        # In ANSYS, it has
                        # 'D[*,1]' = [D11, D21, D31, D41, D51, D61]
                        # 'D[*,2]' = [D22, D32, D42, D52, D62]
                        # 'D[*,3]' = [D33, D43, D53, D63]
                        # 'D[*,4]' = [D44, D54, D64]
                        # 'D[*,5]' = [D55, D65]
                        # 'D[*,6]' = [D66
                        # so the columns are:
                        # column1 = [D11, D21, D31, D41, D51, D61]
                        # column2 = [D12, D22, D32, D42, D52, D62]
                        # column3 = [D13, D23, D33, D43, D53, D63]
                        # column4 = [D41, D42, D43, D44, D54, D64]
                        # column5 = [D51, D52, D53, D54, D55, D65]
                        # column6 = [D61, D62, D63, D64, D65, D66]
                        column1 = elastic_dictionary["D[*,1]"][1:]
                        column2 = elastic_dictionary["D[*,2]"][1:]; column2[0] = column1[1]
                        column3 = elastic_dictionary["D[*,3]"][1:]; column3[0] = column1[2]; column3[1] = column2[2]
                        column4 = elastic_dictionary["D[*,4]"][1:]; column4[0] = column1[3]; column4[1] = column2[3]; column4[2] = column3[3]
                        column5 = elastic_dictionary["D[*,5]"][1:]; column5[0] = column1[4]; column5[1] = column2[4]; column5[2] = column3[4]; column5[3] = column4[4]
                        column6 = elastic_dictionary["D[*,6]"][1:]; column6[0] = column1[5]; column6[1] = column2[5]; column6[2] = column3[5]; column6[3] = column4[5]; column6[4] = column5[5]

                        # now matrix [D] become:
                        # D11 D21 D31 D41 D51 D61
                        # D21 D22 D32 D42 D52 D62
                        # D31 D32 D33 D43 D53 D63
                        # D41 D42 D43 D44 D54 D64
                        # D51 D52 D53 D54 D55 D65
                        # D61 D62 D63 D64 D65 D66
                        D = []
                        for k in range(6):
                            row = [[column1[k], column2[k], column3[k], column4[k], column5[k], column6[k]]]
                            D += row

                        # The engineering notation in ANSYS is 11, 22, 33, 12, 23, 13
                        # We need to change it to be 11, 22, 33, 23, 13, 12 for SwiftComp
                        C = D

                        C[3], C[4] = C[4], C[3]
                        C[4], C[5] = C[5], C[4]
                        C = utilities.transpose(C)
                        C[4], C[5] = C[5], C[4]
                        C[3], C[4] = C[4], C[3]
                        C = utilities.transpose(C)


                    tensile_ultimate_strength_dictionary = {}
                    if 'Tensile Ultimate Strength' in property_names:
                        # Obtain Tensile Ultimate Strength
                        # Examples: 
                        # {'Tensile Ultimate Strength': ['Pa', 460000000]}
                        tensile_ultimate_strength_dictionary = ansys_materials.GetMaterialPropertyByName(material, 'Tensile Ultimate Strength')

                    Compressive_ultimate_strength_dictionary = {}
                    if 'Compressive Ultimate Strength' in property_names:
                        # Obtain Compressive Ultimate Strength
                        # Examples: 
                        # {'Compressive Ultimate Strength': ['Pa', 0]}
                        Compressive_ultimate_strength_dictionary = ansys_materials.GetMaterialPropertyByName(material, 'Compressive Ultimate Strength')

                    stress_limits_dictionary = {}
                    if 'Stress Limits' in property_names:
                        # Obtain Stress Limits
                        # Examples: 
                        # {'Tensile Z direction': ['Pa', 29000000], 'Compressive X direction': ['Pa', -1082000000], 'Shear YZ': ['Pa', 32000000], 
                        # 'Tensile X direction': ['Pa', 2231000000], 'Shear XZ': ['Pa', 60000000], 'Compressive Y direction': ['Pa', -100000000], 
                        # 'Shear XY': ['Pa', 60000000], 'Tensile Y direction': ['Pa', 29000000], 'Compressive Z direction': ['Pa', -100000000]}
                        stress_limits_dictionary = ansys_materials.GetMaterialPropertyByName(material, 'Stress Limits')

                    strain_limits_dictionary = {}
                    if 'Strain Limits' in property_names:
                        # Obtain Strain Limits
                        # Examples: 
                        # {'Tensile Z direction': ['', 0.0032], 'Compressive X direction': ['', -0.0108], 'Shear YZ': ['', 0.011], 
                        # 'Tensile X direction': ['', 0.0167], 'Shear XZ': ['', 0.012], 'Compressive Y direction': ['', -0.0192], 
                        # 'Shear XY': ['', 0.012], 'Tensile Y direction': ['', 0.0032], 'Compressive Z direction': ['', -0.0192]}
                        strain_limits_dictionary = ansys_materials.GetMaterialPropertyByName(material, 'Strain Limits')

                # create SGMaterial instance
                Material = sg_material.SGMaterial(isotropy, ntemp, body_id)
                Material.name = material.DisplayName
                if isotropy == 0:
                    Material.setIsotropicMaterialProperty(ntemp, T, density, E, nu)
                elif isotropy == 1:
                    Material.setOrthotropicMaterialProperty(ntemp, T, density, E1, E2, E3, G12, G13, G23, nu12, nu13, nu23)
                elif isotropy == 2:
                    Material.setAnisotropicMaterialProperty(ntemp, T, density, C)

                # set Tensile Ultimate Strength if any
                if tensile_ultimate_strength_dictionary:
                    tensileUltimateStrength = tensile_ultimate_strength_dictionary['Tensile Ultimate Strength'][1]
                    Material.setTensileUltimateStrength(ntemp, tensileUltimateStrength)

                # set Compressive Ultimate Strength if any
                if Compressive_ultimate_strength_dictionary:
                    compressiveUltimateStrength = Compressive_ultimate_strength_dictionary['Compressive Ultimate Strength'][1]
                    Material.setCompressiveUltimateStrength(ntemp, compressiveUltimateStrength)

                # set Stress Limitsh if any
                if stress_limits_dictionary:
                    X_t = stress_limits_dictionary['Tensile X direction'][1]
                    Y_t = stress_limits_dictionary['Tensile Y direction'][1]
                    Z_t = stress_limits_dictionary['Tensile Z direction'][1]
                    X_c = stress_limits_dictionary['Compressive X direction'][1]
                    Y_c = stress_limits_dictionary['Compressive Y direction'][1]
                    Z_c = stress_limits_dictionary['Compressive Z direction'][1]
                    R   = stress_limits_dictionary['Shear YZ'][1]
                    T   = stress_limits_dictionary['Shear XZ'][1]
                    S   = stress_limits_dictionary['Shear XY'][1]  
                    Material.setOrthotropicStressLimits(ntemp, X_t, Y_t, Z_t, X_c, Y_c, Z_c, R, T, S)

                # set Strain Limits if any
                if strain_limits_dictionary:
                    Xe_t = strain_limits_dictionary['Tensile X direction'][1]
                    Ye_t = strain_limits_dictionary['Tensile Y direction'][1]
                    Ze_t = strain_limits_dictionary['Tensile Z direction'][1]
                    Xe_c = strain_limits_dictionary['Compressive X direction'][1]
                    Ye_c = strain_limits_dictionary['Compressive Y direction'][1]
                    Ze_c = strain_limits_dictionary['Compressive Z direction'][1]
                    Re   = strain_limits_dictionary['Shear YZ'][1]
                    Te   = strain_limits_dictionary['Shear XZ'][1]
                    Se   = strain_limits_dictionary['Shear XY'][1]  
                    Material.setOrthotropicStrainLimits(ntemp, Xe_t, Ye_t, Ze_t, Xe_c, Ye_c, Ze_c, Re, Te, Se)

                # check whether this material is a new material or not
                mark = 0
                for MaterialTemp in self.Material:
                    if Material == MaterialTemp:
                        mark = 1  # mark = 1 means this material is not new
                        break
                if mark == 0:   # mark = 0 means this material is new. add it to Material list property
                    self.Material.append(Material)

    def setMeshControlParameters(self, ExtAPI):
        '''set nSG, nnode, nelem, nmate, nslave, nlayer'''
        # Check one element to determine nSG. (One element is enough)
        # 1D element -> nSG = 1
        # 2D element -> nSG = 2
        # 3D element -> nSG = 3
        self.nSG    = ExtAPI.DataModel.Project.Model.Analyses[0].MeshData.ElementById(1).Dimension
        self.nnode  = ExtAPI.DataModel.Project.Model.Analyses[0].MeshData.Nodes.Count
        self.nelem  = ExtAPI.DataModel.Project.Model.Analyses[0].MeshData.Elements.Count
        self.nmate  = len(self.Material)
        self.nslave = 0
        self.nlayer = 0

    def setNodaCoordinate(self, ExtAPI):
        '''set nodal coordinates'''
        self.Node = []
        for i in range(self.nnode):
            Node = sg_node.SGNode()
            x = ExtAPI.DataModel.Project.Model.Analyses[0].MeshData.NodeById(i+1).X
            y = ExtAPI.DataModel.Project.Model.Analyses[0].MeshData.NodeById(i+1).Y
            z = ExtAPI.DataModel.Project.Model.Analyses[0].MeshData.NodeById(i+1).Z
            Node.coordinate = [x, y, z]
            self.Node.append(Node)

    def setElementConnectivity(self, ExtAPI):
        '''
        ================================================================
        Element connectivity in SwiftComp
        ---------------------------------
        Linear triangular element: kTri3
        connectivity = [1, 2, 3, 0, 0, 0, 0, 0, 0]
        ---------------------------------
        Quadratic triangular element: kTri6
        connectivity = [1, 2, 3, 0, 4, 5, 6, 0, 0]
        ---------------------------------
        Linear quadrilateral element: kQuad4
        connectivity = [1, 2, 3, 4, 0, 0, 0, 0, 0]
        ---------------------------------
        Quadratic quadrilateral element: kQuad8
        connectivity = [1, 2, 3, 4, 5, 6, 7, 8, 0]
        ---------------------------------
        Linear tetrahedral element: kTet4
        connectivity = [1, 2, 3, 4, 0, 0, 0, 0, 0,  0,  0,  0, 0,  0,   0,  0,  0,  0,  0,  0]
        ---------------------------------
        Quadratic tetrahedral element: kTet10
        connectivity = [1, 2, 3, 4, 0, 5, 6, 7, 8,  9, 10,  0, 0,  0,   0,  0,  0,  0,  0,  0]
        ---------------------------------
        Linear brick element: kHex8
        connectivity = [1, 2, 3, 4, 5, 6, 7, 8, 0,  0,  0,  0, 0,  0,   0,  0,  0,  0,  0,  0]
        ---------------------------------
        Quadratic brick element: kHex20
        connectivity = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20]
        ================================================================
        '''
        self.Element = []
        if self.nSG == 2:
            for i in range(self.nelem):
                Element = sg_element.SGElement()
                connectivity = list(ExtAPI.DataModel.Project.Model.Analyses[0].MeshData.NodeIdsFromElementIds([i+1]))
                if len(connectivity) == 3:  # Linear triangular element: kTri3
                    Element.elementType = 'kTri3'
                    Element.total_node = 3
                    Element.total_corner_node = 3
                    Element.connectivity = connectivity + [0] * 6
                elif len(connectivity) == 6:  # Quadratic triangular element: kTri6
                    Element.elementType = 'kTri6'
                    Element.total_node = 6
                    Element.total_corner_node = 3
                    Element.connectivity = connectivity[0:3] + [0] + connectivity[3:6] + [0] * 2
                elif len(connectivity) == 4:  # Linear quadrilateral element: kQuad4
                    Element.elementType = 'kQuad4'
                    Element.total_node = 4
                    Element.total_corner_node = 4
                    Element.connectivity = connectivity + [0] * 5
                elif len(connectivity) == 8:  # Quadratic quadrilateral element: kQuad8
                    Element.elementType = 'kQuad8'
                    Element.total_node = 8
                    Element.total_corner_node = 4
                    Element.connectivity = connectivity + [0]
                else:
                    utilities.element2DTypeWrongMessage()
                    raise EOFError
                self.Element = self.Element + [Element]
        elif self.nSG == 3:
            for i in range(self.nelem):
                Element = sg_element.SGElement()
                connectivity = list(ExtAPI.DataModel.Project.Model.Analyses[0].MeshData.NodeIdsFromElementIds([i+1]))
                if len(connectivity) == 4:  # Linear tetrahedral element: kTet4
                    Element.elementType = 'kTet4'
                    Element.total_node = 4
                    Element.total_corner_node = 4
                    Element.connectivity = connectivity + [0] * 16
                elif len(connectivity) == 10:  # Quadratic tetrahedral element: kTet10
                    Element.elementType = 'kTet10'
                    Element.total_node = 10
                    Element.total_corner_node = 4
                    Element.connectivity = connectivity[0:4] + [0] + connectivity[4:10] + [0] * 9
                elif len(connectivity) == 8:  # Linear brick element: kHex8
                    Element.elementType = 'kHex8'
                    Element.total_node = 8
                    Element.total_corner_node = 8
                    Element.connectivity = connectivity + [0] * 12
                elif len(connectivity) == 20:  # Quadratic brick element: kHex20
                    Element.elementType = 'kHex20'
                    Element.total_node = 20
                    Element.total_corner_node = 8
                    Element.connectivity = connectivity
                else:
                    utilities.element3DTypeWrongMessage()
                    raise EOFError
                self.Element.append(Element)

        # set material id for each element
        for i in range(self.nmate):
            element_ids = ExtAPI.DataModel.Project.Model.Analyses[0].MeshData.MeshRegionById(self.Material[i].body_id).ElementIds
            for element_id in element_ids:
                self.Element[element_id-1].material_id = i + 1

    def setOmega(self, ExtAPI):
        '''
        ================================================================
        Homogenized SG volume calculation
        ---------------------------------
        Solid model (3D structural model): Volume of the homogenized material
        including both the volume of the material and the volume of possible
        voids in the SG.
          1D SG: Length
          2D SG: Area
          3D SG: Volume
        ---------------------------------
        Plate/shell model
            1D SG: 1.0
          2D SG: Length along y2
          3D SG: Area spanned by y1 and y2
        ---------------------------------
        Beam model
          2D SG: 1.0
          3D SG: Length along y1
        ================================================================
        '''
        node_x = [x.coordinate[0] for x in self.Node]
        node_y = [y.coordinate[1] for y in self.Node]
        node_z = [z.coordinate[2] for z in self.Node]

        len_x = max(node_x) - min(node_x)
        len_y = max(node_y) - min(node_y)
        len_z = max(node_z) - min(node_z)

        if self.SolidModel:  # solid model
            if self.nSG == 1:
                self.omega = len_x
            elif self.nSG == 2:
                self.omega = len_y * len_z
            elif self.nSG == 3:
                self.omega = len_x * len_y * len_z
        elif self.PlateModel:  # plate/shell model
            if self.nSG == 1:
                self.omega = 1.0
            elif self.nSG == 2:
                self.omega = len_y
            elif self.nSG == 3:
                self.omega = len_x * len_y
        elif self.BeamModel:  # beam model
            if self.nSG == 1:
                pass  # error
            elif self.nSG == 2:
                self.omega = 1.0
            elif self.nSG == 3:
                self.omega = len_x


class BeamModel:
    '''BeamModel class
    attributes: submodel, beam_ini_curvatures, beam_ini_oblique
    '''
    def __init__(self):
        self.submodel =  0
        self.beam_ini_curvatures = []
        self.beam_ini_oblique = []

    def setBeamModel(self, submodel, beam_ini_curvatures, beam_ini_oblique):
        beamModelName = {'Euler-Bernoulli Beam Model': 0, 'Timoshenko Beam Model': 1,
                'Vlasov Beam Model': 2, 'Beam Model With the Trapeze Effect': 3}
        self.submodel =  beamModelName[submodel]
        self.beam_ini_curvatures = beam_ini_curvatures
        self.beam_ini_oblique = beam_ini_oblique


class PlateModel:
    '''PlateModel class
    attributes: submodel, plate_ini_curvatures
    '''
    def __init__(self):
        self.submodel = 0
        self.plate_ini_curvatures = []

    def setPlateModel(self, submodel, plate_ini_curvatures):
        plateModelName = {'Kirchhoff-Love Model': 0, 'Reissner-Mindlin Model': 1}
        self.submodel = plateModelName[submodel]
        self.plate_ini_curvatures = plate_ini_curvatures


class SolidModel:
    def __init__(self):
        pass
