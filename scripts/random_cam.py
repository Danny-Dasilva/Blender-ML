import bpy
from random import randint

def randomize_camera(x, y, z, roll, pitch, yaw):
    x = randint(-x, x)
    y= randint(-y,y)
    z = z

    pitch = randint(pitch[0], pitch[1])
    roll = roll
    yaw = randint(-yaw, yaw)
    


    


    fov = 50.0

    pi = 3.14159265

    scene = bpy.data.scenes['Scene']

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
    scene.render.image_settings.file_format = 'PNG'
    scene.render.filepath = "/home/openpose/Pictures/renders"
    bpy.ops.render.render(write_still = 1)

    
randomize_camera(20, 20, 10, 1, [20, 90], 180)
