import math
import bpy
import mathutils
def update():
    dg = bpy.context.evaluated_depsgraph_get() 
    dg.update()


def world_to_camera_view(scene, obj, coord):
    """
    Returns the camera space coords for a 3d point.
    (also known as: normalized device coordinates - NDC).
    Where (0, 0) is the bottom left and (1, 1)
    is the top right of the camera frame.
    values outside 0-1 are also supported.
    A negative 'z' value means the point is behind the camera.
    Takes shift-x/y, lens angle and sensor size into account
    as well as perspective/ortho projections.
    :arg scene: Scene to use for frame size.
    :type scene: :class:`bpy.types.Scene`
    :arg obj: Camera object.
    :type obj: :class:`bpy.types.Object`
    :arg coord: World space location.
    :type coord: :class:`mathutils.Vector`
    :return: a vector where X and Y map to the view plane and
       Z is the depth on the view axis.
    :rtype: :class:`mathutils.Vector`
    """
    from mathutils import Vector

    co_local = obj.matrix_world.normalized().inverted() @ coord
    z = -co_local.z
    
    camera = obj.data
    frame = [-v for v in camera.view_frame(scene=scene)[:3]]
    if camera.type != 'ORTHO':
        if z == 0.0:
            return Vector((0.5, 0.5, 0.0))
        else:
            frame = [(v / (v.z / z)) for v in frame]

    min_x, max_x = frame[1].x, frame[2].x
    min_y, max_y = frame[0].y, frame[1].y

    x = (co_local.x - min_x) / (max_x - min_x)
    y = (co_local.y - min_y) / (max_y - min_y)

    return x, y, z


def reverse(scene, camera, object, angle):
    """
    Returns the camera space coords for a 3d point.
    (also known as: normalized device coordinates - NDC).
    Where (0, 0) is the bottom left and (1, 1)
    is the top right of the camera frame.
    values outside 0-1 are also supported.
    A negative 'z' value means the point is behind the camera.
    Takes shift-x/y, lens angle and sensor size into account
    as well as perspective/ortho projections.
    :arg scene: Scene to use for frame size.
    :type scene: :class:`bpy.types.Scene`
    :arg obj: Camera object.
    :type obj: :class:`bpy.types.Object`
    :arg coord: World space location.
    :type coord: :class:`mathutils.Vector`
    :return: a vector where X and Y map to the view plane and
       Z is the depth on the view axis.
    :rtype: :class:`mathutils.Vector`
    """
    from mathutils import Vector
    
    print(camera, "camera")
    co_local = camera.matrix_world.normalized().inverted() @ object
    
    z = -co_local.z
    print(co_local, "loca")
    camera = camera.data
   
    frame = [-v for v in camera.view_frame(scene=scene)[:3]]
    if camera.type != 'ORTHO':
        if z == 0.0:
            return Vector((0.5, 0.5, 0.0))
        else:
            frame = [(v / (v.z / z)) for v in frame]

    min_x, max_x = frame[1].x, frame[2].x
    print(frame, "frame")

    x = (co_local.x - min_x) / (max_x - min_x)
    
    
    current_ang = x
    
    
    desired_ang = 50 / 2 * angle/100
    print(desired_ang, "desired change")
    scene.camera.rotation_mode = 'XYZ'
    euler = scene.camera.rotation_euler[2]
    print(euler, "eulers")
    change = desired_ang * (pi / 180.0) + euler
    print(change)
    scene.camera.rotation_euler[2] = change 
    update()
    #scene.camera.data.angle = fov*(pi/180.0)
    return x





scene = bpy.context.scene
fov = 50.0
pi = 3.14159265
scene.camera.data.angle = fov*(pi/180.0)
angle = 10
obj = scene.camera
object = bpy.context.scene.cursor.location
print(obj, "co", object)
x = reverse(scene, obj, object, angle)
#print("2D Coords:", co_2d)


print(x, "x, y")


# If you want pixel coords
#render_scale = scene.render.resolution_percentage / 100
#render_size = (
#    int(scene.render.resolution_x * render_scale),
#    int(scene.render.resolution_y * render_scale),
#)

#print("Pixel Coords:", (
#      round(co_2d.x * render_size[0]),
#      round(co_2d.y * render_size[1]),
#))
