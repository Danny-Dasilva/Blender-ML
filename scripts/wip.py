import bpy
from random import randint
from mathutils import Vector



import numpy as np

def camera_view_bounds_2d(scene, camera_object, mesh_object):
    """
    Returns camera space bounding box of the mesh object.
    Gets the camera frame bounding box, which by default is returned without any transformations applied.
    Create a new mesh object based on mesh_object and undo any transformations so that it is in the same space as the
    camera frame. Find the min/max vertex coordinates of the mesh visible in the frame, or None if the mesh is not in view.
    :param scene:
    :param camera_object:
    :param mesh_object:
    :return:
    """

    """ Get the inverse transformation matrix. """
    matrix = camera_object.matrix_world.normalized().inverted()
    """ Create a new mesh data block, using the inverse transform matrix to undo any transformations. """
    dg = bpy.context.evaluated_depsgraph_get()
    ob = mesh_object.evaluated_get(dg) #this gives us the evaluated version of the object. Aka with all modifiers and deformations applied.
    mesh = ob.to_mesh()
    #mesh = mesh_object.to_mesh(scene, True, 'RENDER')
    mesh.transform(mesh_object.matrix_world)
    mesh.transform(matrix)

    """ Get the world coordinates for the camera frame bounding box, before any transformations. """
    frame = [-v for v in camera_object.data.view_frame(scene=scene)[:3]]


    lx = []
    ly = []

    for v in mesh.vertices:
        co_local = v.co
        z = -co_local.z

        if z <= 0.0:
            """ Vertex is behind the camera; ignore it. """
            continue
        else:
            """ Perspective division """
            frame = [(v / (v.z / z)) for v in frame]

        min_x, max_x = frame[1].x, frame[2].x
        min_y, max_y = frame[0].y, frame[1].y

        x = (co_local.x - min_x) / (max_x - min_x)
        y = (co_local.y - min_y) / (max_y - min_y)

        lx.append(x)
        ly.append(y)
    
    mesh_object.to_mesh_clear()

    """ Image is not in view if all the mesh verts were ignored """
    if not lx or not ly:
        return None

    min_x = np.clip(min(lx), 0.0, 1.0)
    min_y = np.clip(min(ly), 0.0, 1.0)
    max_x = np.clip(max(lx), 0.0, 1.0)
    max_y = np.clip(max(ly), 0.0, 1.0)

    """ Image is not in view if both bounding points exist on the same side """
    if min_x == max_x or min_y == max_y:
        return None

    """ Figure out the rendered image size """
    render = scene.render
    fac = render.resolution_percentage * 0.01
    dim_x = render.resolution_x * fac
    dim_y = render.resolution_y * fac

    return (min_x, min_y), (max_x, max_y)






def randomize_camera(x, y, z, roll, pitch, yaw):
    x = randint(-x, x)
    y= randint(-y,y)
    z = z
    x = -3

    pitch = randint(pitch[0], pitch[1])
    roll = roll
    yaw = randint(-yaw/2, yaw/2)
  
    fov = 50.0

    pi = 3.14159265
    
    print(bpy.data.scenes.keys())
    scene = bpy.data.scenes['_mainScene']

    # Set render resolution
    scene.render.resolution_x = 640
    scene.render.resolution_y = 480

    # Set camera fov in degrees
    scene.camera.data.angle = fov*(pi/180.0)

    # Set camera rotation in euler angles
    scene.camera.rotation_mode = 'XYZ'
    scene.camera.rotation_euler[0] = pitch*(pi/180.0)
    scene.camera.rotation_euler[1] = roll*(pi/180)
    scene.camera.rotation_euler[2] = yaw*(pi/180.0)
    print(roll)
    # Set camera translation
    scene.camera.location.x = x
    scene.camera.location.y = y
    scene.camera.location.z = z
    
#    scene.render.image_settings.file_format = 'PNG'
#    scene.render.filepath = "/home/danny/Pictures/renders"
#    bpy.ops.render.render(write_still = 1)
#    
  
    
#andomize_camera(0, 0, 10, 1, [20, 90], 180)
randomize_camera(0, 0, 1.7, 1, [20, 90], 360)

scene = bpy.data.scenes['Scene']
camera_object = bpy.data.objects['Camera']
object = bpy.data.objects['Cube.001']

bounding_box = camera_view_bounds_2d(scene, camera_object, object)
lisst = {}
if bounding_box:
   lisst = {
       'x1': bounding_box[0][0],
       'y1': bounding_box[0][1],
       'x2': bounding_box[1][0],
       'y2': bounding_box[1][1]
   }
   print(lisst)
else:
   print("none in frame")

# 500 render samples 48 s 32 tiles



# 500 render samples 44 s 16 tiles both


# 500 render samples 44 s 64 tiles gpu

# same but 64 
8 45