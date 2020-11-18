import bpy
import json
from random import uniform
from mathutils.bvhtree import BVHTree
from bpy_extras.object_utils import world_to_camera_view
import numpy as np

pi = 3.1415
def update():
    dg = bpy.context.evaluated_depsgraph_get() 
    dg.update()

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
    mesh = mesh_object.to_mesh(scene, True, 'RENDER')
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

    bpy.data.meshes.remove(mesh)

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










def get_cordinates(scene, camera,  object, filename):
    camera_object = camera
    bounding_box = camera_view_bounds_2d(scene, camera_object, object)
    cordinates = {
            'image': filename,
            'meshes': {}
        }
    if bounding_box:
       cordinates['meshes'][object.name] = {
                    'x1': bounding_box[0][0],
                    'y1': bounding_box[0][1],
                    'x2': bounding_box[1][0],
                    'y2': bounding_box[1][1]
                }
       return cordinates
    else:
       return None
def measure (first, second):

    locx = second[0] - first[0]
    locy = second[1] - first[1]
    locz = second[2] - first[2]

    distance = sqrt((locx)**2 + (locy)**2 + (locz)**2) 
    return distance


def center_obj(camera, obj):
    point = obj.matrix_world.to_translation()
    loc_camera = camera.matrix_world.to_translation()

    direction = point - loc_camera
    # point the cameras '-Z' and use its 'Y' as up
    rot_quat = direction.to_track_quat('-Z', 'Y')
    
    # assume we're using euler rotation
    camera.rotation_euler = rot_quat.to_euler()
    update()

def percent_offset(distance, z, degrees):
    fov = 50 * .9
    width = 640

    new_yaw = 640 / distance / fov

    yaw = z + new_yaw
    scene = bpy.data.scenes['_mainScene']
    scene.camera.rotation_mode = 'XYZ'
    scene.camera.rotation_euler[2] = yaw*(pi/180.0)
    update()


def offset(scene, camera, angle):
    
    angle = uniform(-angle, angle)
    width = bpy.context.scene.render.resolution_x
    height = bpy.context.scene.render.resolution_y
    lens = bpy.data.cameras[camera.name].lens
    if width > height:    
        ratio = height / width  
        desired_x = (lens / 2) * (angle/100) * ratio
        desired_y = (lens / 2) * (angle/100) 
    
    elif height > width:
        ratio = width / height  
        desired_x = (lens / 2) * (angle/100)
        desired_y = (lens / 2) * (angle/100) * ratio
        
   
    scene.camera.rotation_mode = 'XYZ'
    x = scene.camera.rotation_euler[0]
    y = scene.camera.rotation_euler[2]
    
    change_x = x + (desired_x * (pi / 180.0))
    change_y = y + (desired_y * (pi / 180.0))
    scene.camera.rotation_euler[0] = change_x 
    scene.camera.rotation_euler[2] = change_y 
    update()
    




def randomize_obj(obj, spawn_range: 'list[tuple]', rotation_range=None):
    
    if rotation_range:
        pitch, roll, yaw = rotation_range
        obj.rotation_mode = 'XYZ'
        obj.rotation_euler[0] = uniform(*pitch) * (pi/180.0) # pitch
        obj.rotation_euler[1] = uniform(*roll) * (pi/180.0) # roll
        obj.rotation_euler[2] = uniform(*yaw) * (pi/180.0) # yaw
    
    #randomly position object 
    x, y, z = spawn_range
    obj.location.x = uniform(*x) #unpacking x values
    obj.location.y = uniform(*y) #unpacking y values
    obj.location.z = uniform(*z) #unpacking z values

    update()



def increment_frames(scene, frames):
    for i in range(frames + 1):
        scene.frame_set(i)

def BVHTreeAndVerticesInWorldFromObj( obj ):
    mWorld = obj.matrix_world
    vertsInWorld = [mWorld @ v.co for v in obj.data.vertices]

    bvh = BVHTree.FromPolygons( vertsInWorld, [p.vertices for p in obj.data.polygons] )

    return bvh, vertsInWorld

# Deselect mesh polygons and vertices
def DeselectEdgesAndPolygons( obj ):
    for p in obj.data.polygons:
        p.select = False
    for e in obj.data.edges:
        e.select = False




def get_raycast_percentage(scene, cam, obj, cutoff):
    # Threshold to test if ray cast corresponds to the original vertex
    limit = 0.0001
    viewlayer = bpy.context.view_layer
    # Deselect mesh elements
    DeselectEdgesAndPolygons( obj )

    # In world coordinates, get a bvh tree and vertices
    bvh, vertices = BVHTreeAndVerticesInWorldFromObj( obj )


    same_count = 0 
    count = 0 
    for i, v in enumerate( vertices ):
        count += 1
        # Get the 2D projection of the vertex
        co2D = world_to_camera_view( scene, cam, v )

        # By default, deselect it
        obj.data.vertices[i].select = False
        
        # If inside the camera view
        if 0.0 <= co2D.x <= 1.0 and 0.0 <= co2D.y <= 1.0: 
            # Try a ray cast, in order to test the vertex visibility from the camera
            location, normal, index, distance, t, ty = scene.ray_cast(viewlayer, cam.location, (v - cam.location).normalized() )
            t = (v-normal).length
            if t < 0.000008:
                same_count += 1
    del bvh
    ray_percent = same_count/ count
    if ray_percent > cutoff/ 100:
        value = True
    else:
        value = False
    return value, ray_percent 


def batch_render(img_count=1, image_dir="./renders/", file_prefix="render",loop_count = 0):
    
        value = True
        object = bpy.data.objects["Suzanne"]
        scene = bpy.context.scene
        camera = bpy.data.objects['Camera']
        
        while loop_count != img_count:
            spawn_range = [
                (-2.5, 2.5), # x
                (3.5, 3.5),  # y 
                (1.7, 1.7)   # z
            ]

            rotation_range = [
                (0, 360), # x
                (0, 360), # y
                (0, 360), # z
            ]

            randomize_obj(object, spawn_range, rotation_range=rotation_range)
            randomize_obj(camera, spawn_range)

            increment_frames(scene, 40)
            center_obj(camera, object)
            offset(scene, camera, 80)

            value, percent = get_raycast_percentage(scene, camera, object, 15)
            print(percent, "percent in view")
            if value == False:
                    loop_count -= 1
                    value = True
            else:
                    file_format = scene.render.image_settings.file_format.lower()
                    filename = f'{file_prefix}-{str(loop_count)}.{file_format}'
                    
                    #write image out
                    bpy.context.scene.render.filepath = f'{image_dir}{filename}'
                    bpy.ops.render.render(write_still=True)
                    
                    
                    #pull cordinates
                    scene_labels = get_cordinates(scene, camera, object, filename)
                    
                    yield scene_labels

            loop_count += 1
            
image_dir = "./renders/"
labels = list(batch_render(img_count=5))
with open(f'{image_dir}/labels.json', 'w+') as f:
    json.dump(labels, f, sort_keys=True, indent=4, separators=(',', ': '))
