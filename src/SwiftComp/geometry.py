import math


##############################################################################
# Geometry
##############################################################################

def dummyPlateAtToolbar(ag):
    ExtAPI.CreateFeature("dummyPlate")
    ExtAPI.Log.WriteMessage("Dummy Plate at toolbar")


def dummyPlateAtTree(feature, fct):

    dummyPlate = []

    # Generate part
    L = feature.Properties["Definition/Dummy Plate Length"].Value

    # Some useful builder
    primitive = ExtAPI.DataModel.GeometryBuilder.Primitives

    # Creat dummy  plate
    dummy_plate = primitive.Sheet.CreatePolygon([0., L / 2., L / 2., 0., -L / 2., L / 2., 0., -L / 2., -L / 2., 0., L / 2., -L / 2.]).Generate()

    # Create Part
    dummyPlate.Add(dummy_plate)

    # Add resultant entities to feature
    feature.Bodies = dummyPlate

    # Assign material type to the entities. Different options are Add, Cut, Freeze
    feature.MaterialType = MaterialTypeEnum.Freeze

    ExtAPI.Log.WriteMessage("Dummy Plate at tree")

    return True

def dummyPlateAtTreeAfterGenerate(arg):

    if ExtAPI.DataModel.GeoData.Bodies.Count == 1:

        area = ExtAPI.DataModel.GeoData.Bodies[0].Area

        L = sqrt(area)

        # Run script to renew entities and assign Thickness
        # This can only be done by script since ACT doesn't have this capbility
        script = '''
        ag.fm.Body(0).Name = 'dummy plate';
        ag.fm.Body(0).Thickness = ''' + '\'' + str(0.01 * L) + '\'' + ''';
        ag.b.Regen();
        ag.gui.ZoomFit();
        '''

        # In DesignModeler, AG should be added before ag when using ACT
        script_new = script.replace('ag.', 'AG.ag.')

        ExtAPI.Application.ScriptByName('jscript').ExecuteCommand(script_new)


def dummyPlateLengthIsValid(entity, property):
    if property.Value <= 0:
        return False
    return True


def square2DAtToolbar(ag):
    ExtAPI.CreateFeature("square2D")
    ExtAPI.Log.WriteMessage("Square Pack Microstructure 2D at toolbar")

def square2DAtTree(feature, fct):
    # Volume fraction
    vol_fra = feature.Properties["Definition/Fiber Volume Fraction"].Value

    # Generate part
    L = feature.Properties["Information/SG Length"].Value

    if vol_fra <= 0 or vol_fra >= 78.5:
        Ansys.UI.Toolkit.MessageBox.Show("Fiber Volume Fraction [%] should larger than 0 and less than 78.5")
        return False

    # Calculate the radius of the fiber
    radius = L * ((vol_fra / 100) / math.pi) ** (1. / 2.)

    feature.Properties["Information/Calculated Fiber Radius"].Value = radius

    # Some useful builder
    primitive = ExtAPI.DataModel.GeometryBuilder.Primitives
    operation = ExtAPI.DataModel.GeometryBuilder.Operations

    # Created matrix
    sheet_square = primitive.Sheet.CreatePolygon([0., L / 2., L / 2., 0., -L / 2., L / 2., 0., -L / 2., -L / 2., 0., L / 2., -L / 2.]).Generate()
    wire = primitive.Wire.CreateArc(radius, [0., 0., 0.], [0., 1., 0.], [1., 0., 0.]).Generate()
    sheet_circle = operation.Tools.WireToSheetBody(wire)
    matrix = operation.CreateSubtractOperation([sheet_circle]).ApplyTo([sheet_square])[0]

    # Create fiber
    wire = primitive.Wire.CreateArc(radius, [0., 0., 0.], [0., 1., 0.], [1., 0., 0.]).Generate()
    fiber = operation.Tools.WireToSheetBody(wire)

    # Create Part
    part = operation.Tools.CreatePart([fiber, matrix])
    part.Name = 'Square Pack Microstructure 2D'

    # Add resultant entities to feature
    feature.Bodies = [part]

    # Assign material type to the entities. Different options are Add, Cut, Freeze
    feature.MaterialType = MaterialTypeEnum.Freeze

    ExtAPI.Log.WriteMessage("Square Pack Microstructure 2D at tree")

    return True


def square2DAtTreeAfterGenerate(arg):
    if ExtAPI.DataModel.GeoData.Bodies.Count == 2:

        area = ExtAPI.DataModel.GeoData.Bodies[0].Area + ExtAPI.DataModel.GeoData.Bodies[1].Area

        L = sqrt(area)

        # Run script to renew entities and assign Thickness
        # This can only be done by script since ACT doesn't have this capbility
        script = '''
        ag.fm.Body(0).Name = 'fiber';
        ag.fm.Body(1).Name = 'matrix';
        ag.fm.Body(0).Thickness = ''' + '\'' + str(0.01 * L) + '\'' + ''';
        ag.fm.Body(1).Thickness = ''' + '\'' + str(0.01 * L) + '\'' + ''';
        ag.b.Regen();
        ag.gui.ZoomFit();
        '''

        # In DesignModeler, AG should be added before ag when using ACT
        script_new = script.replace('ag.', 'AG.ag.')

        ExtAPI.Application.ScriptByName('jscript').ExecuteCommand(script_new)


def square2DFiberFractionIsValid(entity, fiberFractionProperty):
    if fiberFractionProperty.Value >= 78.5 or fiberFractionProperty.Value <= 0:
        return False
    return True


def square2DFiberRadiusVisible(entity, fiberProperty):
    if fiberProperty.Value > 0:
        return True
    return False


def sphericalAtToolbar(ag):
    ExtAPI.CreateFeature("spherical")
    ExtAPI.Log.WriteMessage("Spherical Inclusion Microstructure at toolbar")


def sphericalAtTree(feature, fct):
    vol_fra = feature.Properties["Definition/Sphere Volume Fraction"].Value

    # Generate part
    L = feature.Properties["Information/SG Length"].Value

    if vol_fra <= 0 or vol_fra >= 52.3:
        Ansys.UI.Toolkit.MessageBox.Show("Shpere Volume Fraction [%] should larger than 0 and less than 52.3")
        return False

    # Calculate the radius of the sphere
    radius = (3. * (vol_fra / 100) * L ** 3 / (4. * math.pi)) ** (1. / 3.)

    feature.Properties["Information/Calculated Sphere Radius"].Value = radius

    primitive = ExtAPI.DataModel.GeometryBuilder.Primitives
    operation = ExtAPI.DataModel.GeometryBuilder.Operations

    # Create matrix
    body_box = primitive.Solid.CreateBox([-L / 2., -L / 2., -L / 2.], [L / 2., L / 2., L / 2.]).Generate()
    body_sphere = primitive.Solid.CreateSphere([0., 0., 0.], radius).Generate()
    matrix = operation.CreateSubtractOperation([body_sphere]).ApplyTo([body_box])[0]

    # Create sphere
    sphere = primitive.Solid.CreateSphere([0., 0., 0.], radius).Generate()

    # Create Part
    part = operation.Tools.CreatePart([sphere, matrix])
    part.Name = 'Spherical Inclusion Microstructure'

    feature.Bodies = [part]

    feature.MaterialType = MaterialTypeEnum.Freeze

    ExtAPI.Log.WriteMessage("Spherical Inclusion Microstructure at tree")

    return True


def sphericalAtTreeAfterGenerate(arg):
    if ExtAPI.DataModel.GeoData.Bodies.Count == 2:
        # Run script to renew entities and assign Thickness
        # This can only be done by script since ACT doesn't have this capbility
        script = '''
        ag.fm.Body(0).Name = 'sphere';
        ag.fm.Body(1).Name = 'matrix';
        ag.b.Regen();
        ag.gui.ZoomFit();
        '''
        # In DesignModeler, AG should be added before ag when using ACT
        script_new = script.replace('ag.', 'AG.ag.')

        ExtAPI.Application.ScriptByName('jscript').ExecuteCommand(script_new)


def sphericalSphereFractionIsValid(entity, fiberFractionProperty):
    if fiberFractionProperty.Value <= 0 or fiberFractionProperty.Value >= 52.3:
        return False
    return True


def sphericalSphereRadiusVisible(entity, fiberProperty):
    if fiberProperty.Value > 0 and fiberProperty.Value < 52.3:
        return True
    return False



def square2DAtSpaceClaimToolbar(ag):
    ExtAPI.Log.WriteMessage("test")