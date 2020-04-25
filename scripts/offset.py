import math
import bpy
from math import *
pi = 3.141592

def update():
    dg = bpy.context.evaluated_depsgraph_get() 
    dg.update()
def measure (first, second):

    locx = second[0] - first[0]
    locy = second[1] - first[1]
    locz = second[2] - first[2]

    distance = sqrt((locx)**2 + (locy)**2 + (locz)**2) 
    return distance
def center_obj(obj_camera, point):
    point = point.matrix_world.to_translation()

    loc_camera = obj_camera.matrix_world.to_translation()

    direction = point - loc_camera
    # point the cameras '-Z' and use its 'Y' as up
    rot_quat = direction.to_track_quat('-Z', 'Y')
    
    # assume we're using euler rotation
    obj_camera.rotation_euler = rot_quat.to_euler()
    update()
   
    distance = measure(point, loc_camera)
    return distance



percent_of_image = (1, 0) #between -1 and 1

#point_pos = [20,10,40] #x, y, z local to camera space z is straight out of the camera. Only works if object is in front of camera z is positive. Z positive is out the back of the camera so you may need to take abs value
cube = bpy.data.objects["Cube"]




def calculate_camera_rot(percent_of_image, camera, object, percent_range=(0,1)):
    focal_length = bpy.data.cameras['Camera'].lens
    sensor_height = bpy.data.cameras['Camera'].sensor_height
    sensor_width = bpy.data.cameras['Camera'].sensor_width
    print(sensor_height, sensor_width, "width height")
    globall = object.matrix_world.translation
    invert = camera.matrix_world.inverted()
    local_point_pos = object.matrix_world.translation @ camera.matrix_world.inverted()
#     
#    print(local_point_pos, "local")
    print( globall, "global \n", invert, "invert")
    print(local_point_pos)
    point_pos = local_point_pos
    percent_of_image = [(percent-((percent_range[0]+percent_range[1])/2))*(2/(percent_range[1]-percent_range[0])) for percent in percent_of_image]
    target_sensor_x = sensor_width/2 * percent_of_image[0]
    target_vector_angle_x = math.degrees(math.atan(target_sensor_x/focal_length))
    current_vector_angle_x = math.degrees(math.atan(point_pos[0]/-point_pos[2]))

    target_sensor_y = sensor_height/2 * percent_of_image[1]
    target_vector_angle_y = math.degrees(math.atan(target_sensor_y/focal_length))
    current_vector_angle_y = math.degrees(math.atan(local_point_pos[1]/-local_point_pos[2]))
    print(target_vector_angle_y,current_vector_angle_y)
    camera_xRot_delta = current_vector_angle_x - target_vector_angle_x
    camera_yRot_delta = current_vector_angle_y - target_vector_angle_y
 
    return (camera_xRot_delta, camera_yRot_delta)
scene = bpy.data.scenes['Scene']
camera = scene.camera

fff = center_obj(camera, cube)



camera_rot_delta = calculate_camera_rot(percent_of_image, camera, cube, percent_range=(-1,1))
print(camera_rot_delta, "delta")

def rotate_camera(delta):
    x = scene.camera.rotation_euler[0]
    y = scene.camera.rotation_euler[2]
    desired_y = delta[0]
    desired_x = delta[1]
    print(desired_y, desired_x)
    change_x = x + (desired_x * (pi / 180.0))
    change_y = y + (desired_y * (pi / 180.0))
    scene.camera.rotation_euler[0] = change_x 
    scene.camera.rotation_euler[2] = change_y 
    


rotate_camera(camera_rot_delta)
