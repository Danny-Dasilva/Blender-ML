import bpy
import mathutils
from random import randint, uniform
from math import *
import os
import json
from mathutils import Vector, Quaternion
from time import sleep 



import time
import warnings
#from scripts import PID


import time
import warnings



def update():
    dg = bpy.context.evaluated_depsgraph_get() 
    dg.update()

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








def randomize_camera(x, y, z, roll=0, pitch=0, yaw=0):
    x = y
    y= x
    z = z
 

    pitch = pitch
    roll = roll
    yaw = randint(-yaw/2, yaw/2)
  
    fov = 50.0

    pi = 3.14159265
    print(bpy.data.scenes.keys())
    scene = bpy.data.scenes['Scene']

    # Set render resolution
    scene.render.resolution_x = 640
    scene.render.resolution_y = 640

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


def center_obj(obj_camera, point):
    print(point, " [pooooiint")
    loc_camera = obj_camera.matrix_world.to_translation()

    direction = point - loc_camera
    print(direction, "diredctr")
    # point the cameras '-Z' and use its 'Y' as up
    rot_quat = direction.to_track_quat('-Z', 'Y')
    print(rot_quat, rot_quat.to_euler(), "quat")
    # assume we're using euler rotation
    obj_camera.rotation_euler = rot_quat.to_euler()
    update()
    eulers = [degrees(a) for a in obj_camera.matrix_world.to_euler()]
    z = eulers[2]
    print(eulers, "eulsers")
    distance = measure(point, loc_camera)
    return distance, z

def percent_offset(distance, z, degrees):
    fov = 50 * .9
    width = 640

    new_yaw = 640 / distance / fov

    yaw = z + new_yaw
    scene = bpy.data.scenes['_mainScene']
    scene.camera.rotation_mode = 'XYZ'
    scene.camera.rotation_euler[2] = yaw*(pi/180.0)
    update()

def point_at(obj, target, roll=0):
    obj = obj.matrix_world.to_translation()
    """
    Rotate obj to look at target

    :arg obj: the object to be rotated. Usually the camera
    :arg target: the location (3-tuple or Vector) to be looked at
    :arg roll: The angle of rotation about the axis from obj to target in radians. 

    Based on: https://blender.stackexchange.com/a/5220/12947 (ideasman42)      
    """
    if not isinstance(target, mathutils.Vector):
        target = mathutils.Vector(target)
    #oc = obj.location
    loc = obj
    # direction points from the object to the target
    direction = target - loc
    
    quat = direction.to_track_quat('-Z', 'Y')

    # /usr/share/blender/scripts/addons/add_advanced_objects_menu/arrange_on_curve.py
    quat = quat.to_matrix().to_4x4()
    rollMatrix = mathutils.Matrix.Rotation(roll, 4, 'Z')

    # remember the current location, since assigning to obj.matrix_world changes it
    loc = loc.to_tuple()
    
    
    obj.matrix_world = quat * rollMatrix
    obj.location = loc


def offset(scene, camera, angle):
    
    angle = angle
    height = 640
    width = 640
        
    if width > height:    
        ratio = height / width  
        desired_x = (50 / 2) * (angle/100) * ratio
        desired_y = (50 / 2) * (angle/100) 
    
    elif height > width:
        ratio = width / height  
        desired_x = (50 / 2) * (angle/100)
        desired_y = (50 / 2) * (angle/100) * ratio
    else:
        desired_x = (50 / 2) * (angle/100)
        desired_y = (50 / 2) * (angle/100)
   
    scene.camera.rotation_mode = 'XYZ'
    x = scene.camera.rotation_euler[0]
    y = scene.camera.rotation_euler[2]
    
    change_x = x + (desired_x * (pi / 180.0))
    change_y = y + (desired_y * (pi / 180.0))
    #scene.camera.rotation_euler[0] = change_x 
    #scene.camera.rotation_euler[2] = change_y 
    update()
    

def randomize_obj(obj, x, y, z):
    
    roll = uniform(0, 90)
    pitch = uniform(0, 90)
    yaw = uniform(0, 90)
    obj.rotation_mode = 'XYZ'
    obj.rotation_euler[0] = pitch*(pi/180.0)
    obj.rotation_euler[1] = roll*(pi/180)
    obj.rotation_euler[2] = yaw*(pi/180.0)
    
    
    obj.location.x = uniform(-x, x)
    obj.location.y = uniform(-y, y)
    obj.location.z = z

def increment_frames(frames):
    for i in range(frames):
        scene.frame_set(i)



#import bpy_extras
#monkey = bpy.data.objects["Cube"]
#randomize_obj(monkey, 2, 2, 3)
#scene, camera = randomize_camera(10, 10, 1.7)
#increment_frames(100)
#scene = bpy.context.scene
####         
#distance, z = center_obj(camera, monkey.matrix_world.to_translation())



dg = bpy.context.evaluated_depsgraph_get() 


import bpy
from mathutils.bvhtree import BVHTree
#src = bpy.data.objects["Cube"]
#bvhtree = BVHTree.FromObject(bpy.data.objects["Cube"], dg)
#ray_origin = bpy.data.objects["Cube"].location
#scene = bpy.data.scenes['Scene']
#ray_direction = bpy.data.objects["Camera"].location
#location, normal, index, dist = scene.ray_cast(ray_origin, ray_direction)

#print(location, normal, index, dist)
 # get the context arguments
# 





### foir kiater

#from bpy_extras import view3d_utils



#scene = bpy.data.scenes['Scene']
#region = context.region
#rv3d = context.region_data
#coord = 320, 320
#scene = bpy.context.scene 
#viewlayer = bpy.context.view_layer

## get the ray from the viewport and mouse
#view_vector = view3d_utils.region_2d_to_vector_3d(region, rv3d, coord)
#ray_origin = view3d_utils.region_2d_to_origin_3d(region, rv3d, coord)
#ray_target = ray_origin + (view_vector *-10)
#ray_goal = ray_origin + (view_vector *1000)

#rayresult = scene.ray_cast(viewlayer, ray_target, ray_goal)

#print (rayresult)
#print (ray_goal)
#print (ray_target)

object = bpy.data.objects["Suzanne"]
camera = bpy.context.scene.camera
scene = bpy.data.scenes['Scene']



viewlayer = bpy.context.view_layer

import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree
from bpy_extras.object_utils import world_to_camera_view

# Create a BVH tree and return bvh and vertices in world coordinates 
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

# Get context elements: scene, camera and mesh


def get_raycast_percentage(cam, obj, cutoff):
    # Threshold to test if ray cast corresponds to the original vertex
    limit = 0.0001

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


#scene = bpy.context.scene
cam = bpy.context.scene.camera
obj = bpy.data.objects['Suzanne']

value, percent = get_raycast_percentage(cam, obj, 10)


print(value, percent)
