class SGMaterial(object):
    """SGMaterial class 
    attributes:
    isotropy: an integer to indicate whether the material is isotropic (0), orthotropic (1), or general anisotropic (2)
    ntemp: number of material property sets according to different temperature
    MaterialProperty [ntemp]: 
    """
    def __init__(self, isotropy, ntemp, body_id):
        self.name = ''
        self.isotropy = isotropy
        self.ntemp = ntemp
        self.body_id = body_id
        self.MaterialProperty = []
        for i in range(ntemp):
             self.MaterialProperty.append(None)

    def setIsotropicMaterialProperty(self, ntemp, T, density, E, nu):
        for i in range(ntemp):
            self.MaterialProperty[i] = SGMaterialProperty(T[i], density[i])
            self.MaterialProperty[i].isotropic = {'E':E[i], 'nu':nu[i]}

    def setOrthotropicMaterialProperty(self, ntemp, T, density, E1, E2, E3, G12, G13, G23, nu12, nu13, nu23):
        for i in range(ntemp):
            self.MaterialProperty[i] = SGMaterialProperty(T[i], density[i])
            self.MaterialProperty[i].orthotropic = {'E1':E1[i], 'E2':E2[i], 'E3':E3[i], 'G12':G12[i], 'G13':G13[i], 'G23':G23[i], 'nu12':nu12[i], 'nu13':nu13[i], 'nu23':nu23[i]}

    def setAnisotropicMaterialProperty(self, ntemp, T, density, C):
        for i in range(ntemp):
            self.MaterialProperty[i] = SGMaterialProperty(T[i], density[i])
            self.MaterialProperty[i].anisotropic = C

    def setTensileUltimateStrength(self, ntemp, tensileUltimateStrength):
        for i in range(ntemp):
            self.MaterialProperty[i].tensileUltimateStrength = tensileUltimateStrength

    def setCompressiveUltimateStrength(self, ntemp, compressiveUltimateStrength):
        for i in range(ntemp):
            self.MaterialProperty[i].compressiveUltimateStrength = compressiveUltimateStrength

    def setOrthotropicStressLimits(self, ntemp, X_t, Y_t, Z_t, X_c, Y_c, Z_c, R, T, S):
        for i in range(ntemp):
            self.MaterialProperty[i].orthotropicStressLimits = {'X_t':X_t, 'Y_t':Y_t, 'Z_t':Z_t, 'X_c':X_c, 'Y_c':Y_c, 'Z_c':Z_c, 'R':R, 'T':T, 'S':S}

    def setOrthotropicStrainLimits(self, ntemp, Xe_t, Ye_t, Ze_t, Xe_c, Ye_c, Ze_c, Re, Te, Se):
        for i in range(ntemp):
            self.MaterialProperty[i].orthotropicStrainLimits = {'Xe_t':Xe_t, 'Ye_t':Ye_t, 'Ze_t':Ze_t, 'Xe_c':Xe_c, 'Ye_c':Ye_c, 'Ze_c':Ze_c, 'Re':Re, 'Te':Te, 'Se':Se}

class SGMaterialProperty(object):
    """MaterialProperty class 
    attributes:
    T: temperature
    density
    isotropic: {E=.., nu=..}
    orthotropic: {E1=.., E2=.., E3=.., G12=.., G13=.., G23=.., nu12=.., nu13=.., nu23=..}
    anisotropic: 2D array
    """
    def __init__(self, T, density):
        self.T = T
        self.density = density
        self.isotropic = {}
        self.orthotropic = {}
        self.anisotropic = []
        self.tensileUltimateStrength = None
        self.compressiveUltimateStrength = None
        self.orthotropicStressLimits = {}
        self.orthotropicStrainLimits = {}
