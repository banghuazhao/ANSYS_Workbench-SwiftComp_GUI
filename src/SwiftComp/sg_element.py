class SGElement(object):
    """SG element class"""
    def __init__(self):
        self.elementType = ''
        self.material_id = 0
        self.layer_id = 0
        self.total_node = 0
        self.total_corner_node = 0
        self.connectivity = []
        self.stress_corner = []
        self.stress_total = []
        self.strain_corner = []
        self.strain_total = []
        self.Gmsh_elementType = None


