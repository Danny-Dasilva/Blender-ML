import bpy
import mathutils
from random import randint, uniform
from math import *
import os
import json
from time import sleep

from mathutils import Vector
import numpy as np
def update():
    """
    Update scene
    """
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
    dg = bpy.context.evaluated_depsgraph_get()
    
    ob = mesh_object.evaluated_get(dg) #this gives us the evaluated version of the object. Aka with all modifiers and deformations applied.
    mesh = ob.to_mesh()
    #mesh = mesh_object.to_mesh()
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








def randomize_camera(x, y, z, roll=0, pitch=0, yaw=0, resolution_x=640, resolution_y=480):
    x = uniform(-x, x)
    y= uniform(-y,y)
    z = z
 

    pitch = pitch
    roll = roll
    yaw = randint(-yaw/2, yaw/2)
  
    fov = 50.0

    pi = 3.14159265
    
    scene = bpy.data.scenes['_mainScene']

    # Set render resolution
    scene.render.resolution_x = resolution_x
    scene.render.resolution_y = resolution_y

    # Set camera fov in degrees
    scene.camera.data.angle = fov*(pi/180.0)

    # Set camera rotation in euler angles
    scene.camera.rotation_mode = 'XYZ'
    scene.camera.rotation_euler[0] = pitch*(pi/180.0)
    scene.camera.rotation_euler[1] = roll*(pi/180)
    scene.camera.rotation_euler[2] = yaw*(pi/180.0)

    # Set camera translation
    scene.camera.location.x = x
    scene.camera.location.y = y
    scene.camera.location.z = z
    update()
    return scene, scene.camera


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


def center_obj(camera, point):
    """
    Rotate obj_camera to look at target

    :arg obj: the object to be rotated. Usually the camera
    :arg target: the location (3-tuple or Vector) to be looked at
    :arg roll: The angle of rotation about the axis from obj to target in radians. 

    Based on: https://blender.stackexchange.com/a/5220/12947 (ideasman42)      
    """
    loc_camera = camera.matrix_world.to_translation()

    direction = point - loc_camera
    # point the cameras '-Z' and use its 'Y' as up
    rot_quat = direction.to_track_quat('-Z', 'Y')
    
    # assume we're using euler rotation
    camera.rotation_euler = rot_quat.to_euler()
    update()
    eulers = [degrees(a) for a in camera.matrix_world.to_euler()]
    z = eulers[2]
    distance = measure(point, loc_camera)
    return distance, z



def offset(scene, camera, angle, width, height):
    
    angle = uniform(-angle, angle)

    if width > height:    
        ratio = height / width  
        desired_x = (50 / 2) * (angle/100) * ratio
        desired_y = (50 / 2) * (angle/100) 
    
    elif height > width:
        ratio = width / height  
        desired_x = (50 / 2) * (angle/100)
        desired_y = (50 / 2) * (angle/100) * ratio
        
   
    scene.camera.rotation_mode = 'XYZ'
    x = scene.camera.rotation_euler[0]
    y = scene.camera.rotation_euler[2]
    
    change_x = x + (desired_x * (pi / 180.0))
    change_y = y + (desired_y * (pi / 180.0))
    scene.camera.rotation_euler[0] = change_x 
    scene.camera.rotation_euler[2] = change_y 
    update()
    



 

def batch_render(file_prefix="render"):
    # in px
    width, height = 640, 480
    scene_setup_steps = 4

    labels = []
    for i in range(0, scene_setup_steps):
        monkey = bpy.data.objects["monkey"]
        scene, camera = randomize_camera(2.5, 3.5, 1.7)

         
        distance, z = center_obj(camera, monkey.matrix_world.to_translation())

        offset(scene, camera, 85, width, height)

        filename = '{}-{}y.png'.format(str(file_prefix), str(i))
        
        bpy.context.scene.render.filepath = os.path.join('/renders/', filename)
        bpy.ops.render.render(write_still=True)
        scene_labels = get_cordinates(scene, camera, monkey, filename)

        labels.append(scene_labels) # Merge lists

    with open('./renders/labels.json', 'w+') as f:
        json.dump(labels, f, sort_keys=True, indent=4, separators=(',', ': '))


batch_render()