class SGStructuralResultList(object):
    """SG Structural Result class"""
    def __init__(self):
        self.ResultList = []

    def setStructuralResult(self, name, macro_model, macro_displacement, macro_rotation, macro_strain, macro_stress):
        StructuralResult = SGStructuralResult(name, macro_model, macro_displacement, macro_rotation, macro_strain, macro_stress)

        for i in range(len(self.ResultList)):
            if self.ResultList[i].name == StructuralResult.name:
                self.ResultList[i] = StructuralResult
                return
        
        self.ResultList.append(StructuralResult)


class SGStructuralResult(object):
    '''SG Extract Result class'''
    def __init__(self, name, macro_model, macro_displacement, macro_rotation, macro_strain, macro_stress):
        self.name = name
        self.macro_model = macro_model
        self.macro_displacement = macro_displacement
        self.macro_rotation = macro_rotation
        self.macro_strain = macro_strain
        self.macro_stress = macro_stress