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


def _clamp(value, limits):
    lower, upper = limits
    if value is None:
        return None
    elif upper is not None and value > upper:
        return upper
    elif lower is not None and value < lower:
        return lower
    return value


try:
    # get monotonic time to ensure that time deltas are always positive
    _current_time = time.monotonic
except AttributeError:
    # time.monotonic() not available (using python < 3.3), fallback to time.time()
    _current_time = time.time
    warnings.warn('time.monotonic() not available in python < 3.3, using time.time() as fallback')


class PID(object):
    """
    A simple PID controller. No fuss.
    """

    def __init__(self,
                 Kp=1.0, Ki=0.0, Kd=0.0,
                 setpoint=0,
                 sample_time=0.01,
                 output_limits=(None, None),
                 auto_mode=True,
                 proportional_on_measurement=False):
        """
        :param Kp: The value for the proportional gain Kp
        :param Ki: The value for the integral gain Ki
        :param Kd: The value for the derivative gain Kd
        :param setpoint: The initial setpoint that the PID will try to achieve
        :param sample_time: The time in seconds which the controller should wait before generating a new output value.
                            The PID works best when it is constantly called (eg. during a loop), but with a sample
                            time set so that the time difference between each update is (close to) constant. If set to
                            None, the PID will compute a new output value every time it is called.
        :param output_limits: The initial output limits to use, given as an iterable with 2 elements, for example:
                              (lower, upper). The output will never go below the lower limit or above the upper limit.
                              Either of the limits can also be set to None to have no limit in that direction. Setting
                              output limits also avoids integral windup, since the integral term will never be allowed
                              to grow outside of the limits.
        :param auto_mode: Whether the controller should be enabled (in auto mode) or not (in manual mode)
        :param proportional_on_measurement: Whether the proportional term should be calculated on the input directly
                                            rather than on the error (which is the traditional way). Using
                                            proportional-on-measurement avoids overshoot for some types of systems.
        """
        self.Kp, self.Ki, self.Kd = Kp, Ki, Kd
        self.setpoint = setpoint
        self.sample_time = sample_time

        self._min_output, self._max_output = output_limits
        self._auto_mode = auto_mode
        self.proportional_on_measurement = proportional_on_measurement

        self.reset()

    def __call__(self, input_, dt=None):
        """
        Call the PID controller with *input_* and calculate and return a control output if sample_time seconds has
        passed since the last update. If no new output is calculated, return the previous output instead (or None if
        no value has been calculated yet).
        :param dt: If set, uses this value for timestep instead of real time. This can be used in simulations when
                   simulation time is different from real time.
        """
        if not self.auto_mode:
            return self._last_output

        now = _current_time()
        if dt is None:
            dt = now - self._last_time if now - self._last_time else 1e-16
        elif dt <= 0:
            raise ValueError("dt has nonpositive value {}. Must be positive.".format(dt))

        if self.sample_time is not None and dt < self.sample_time and self._last_output is not None:
            # only update every sample_time seconds
            return self._last_output

        # compute error terms
        error = self.setpoint - input_
        d_input = input_ - (self._last_input if self._last_input is not None else input_)

        # compute the proportional term
        if not self.proportional_on_measurement:
            # regular proportional-on-error, simply set the proportional term
            self._proportional = self.Kp * error
        else:
            # add the proportional error on measurement to error_sum
            self._proportional -= self.Kp * d_input

        # compute integral and derivative terms
        self._integral += self.Ki * error * dt
        self._integral = _clamp(self._integral, self.output_limits)  # avoid integral windup

        self._derivative = -self.Kd * d_input / dt

        # compute final output
        output = self._proportional + self._integral + self._derivative
        output = _clamp(output, self.output_limits)

        # keep track of state
        self._last_output = output
        self._last_input = input_
        self._last_time = now

        return output

    @property
    def components(self):
        """
        The P-, I- and D-terms from the last computation as separate components as a tuple. Useful for visualizing
        what the controller is doing or when tuning hard-to-tune systems.
        """
        return self._proportional, self._integral, self._derivative

    @property
    def tunings(self):
        """The tunings used by the controller as a tuple: (Kp, Ki, Kd)"""
        return self.Kp, self.Ki, self.Kd

    @tunings.setter
    def tunings(self, tunings):
        """Setter for the PID tunings"""
        self.Kp, self.Ki, self.Kd = tunings

    @property
    def auto_mode(self):
        """Whether the controller is currently enabled (in auto mode) or not"""
        return self._auto_mode

    @auto_mode.setter
    def auto_mode(self, enabled):
        """Enable or disable the PID controller"""
        self.set_auto_mode(enabled)

    def set_auto_mode(self, enabled, last_output=None):
        """
        Enable or disable the PID controller, optionally setting the last output value.
        This is useful if some system has been manually controlled and if the PID should take over.
        In that case, pass the last output variable (the control variable) and it will be set as the starting
        I-term when the PID is set to auto mode.
        :param enabled: Whether auto mode should be enabled, True or False
        :param last_output: The last output, or the control variable, that the PID should start from
                            when going from manual mode to auto mode
        """
        if enabled and not self._auto_mode:
            # switching from manual mode to auto, reset
            self.reset()

            self._integral = (last_output if last_output is not None else 0)
            self._integral = _clamp(self._integral, self.output_limits)

        self._auto_mode = enabled

    @property
    def output_limits(self):
        """
        The current output limits as a 2-tuple: (lower, upper). See also the *output_limts* parameter in
        :meth:`PID.__init__`.
        """
        return self._min_output, self._max_output

    @output_limits.setter
    def output_limits(self, limits):
        """Setter for the output limits"""
        if limits is None:
            self._min_output, self._max_output = None, None
            return

        min_output, max_output = limits

        if None not in limits and max_output < min_output:
            raise ValueError('lower limit must be less than upper limit')

        self._min_output = min_output
        self._max_output = max_output

        self._integral = _clamp(self._integral, self.output_limits)
        self._last_output = _clamp(self._last_output, self.output_limits)

    def reset(self):
        """
        Reset the PID controller internals, setting each term to 0 as well as cleaning the integral,
        the last output and the last input (derivative calculation).
        """
        self._proportional = 0
        self._integral = 0
        self._derivative = 0

        self._last_time = _current_time()
        self._last_output = None
        self._last_input = None







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
    print(obj, "obj")
    co_local = obj.matrix_world.normalized().inverted() @ coord
    z = -co_local.z
    print(z, "zx")
    camera = obj.data
    
    print(camera, "cam cords")
    frame = [-v for v in camera.view_frame(scene=scene)[:3]]
    print(frame, "frame")
    if camera.type != 'ORTHO':
        if z == 0.0:
            return Vector((0.5, 0.5, 0.0))
        else:
            frame =  [(v / (v.z / z)) for v in frame]
    print(frame, "frame 2" )
    
    t =  [(v * (v.z * z)) for v in frame]
    print(t, " t")
    min_x, max_x = frame[1].x, frame[2].x
    min_y, max_y = frame[0].y, frame[1].y

    x = (co_local.x - min_x) / (max_x - min_x)
    y = (co_local.y - min_y) / (max_y - min_y)

    return Vector((x, y, z))
def camera_to_world_view(scene, obj, coord):
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
    print(obj, "obj")
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

    return Vector((x, y, z))


import bpy_extras
monkey = bpy.data.objects["Cube"]

scene, camera = randomize_camera(0, 0, 0)

scene = bpy.context.scene
###         
distance, z = center_obj(camera, monkey.matrix_world.to_translation())


#offset(scene, camera, 90)




#amera = bpy.data.objects["Camera"]


#co_2d = bpy_extras.object_utils.world_to_camera_view(scene, obj, monkey.location)
#print("2D Coords:", co_2d)

## If you want pixel coords
#render_scale = scene.render.resolution_percentage / 100
#render_size = (
#    int(scene.render.resolution_x * render_scale),
#    int(scene.render.resolution_y * render_scale),
#)
#print("Pixel Coords:", (
#      round(co_2d.x * render_size[0]),
#      round(co_2d.y * render_size[1]),
#))



#print(distance)
#R = distance 
#d = 10

#print(R, "distance")

#x = sqrt((R**2)-(d**2))
#print(x)


    
    

# Test the function using the active object (which must be a camera)
# and the 3D cursor as the location to find.

def update1(x):
    print(x, "curent")
    x = x / scene.render.resolution_x
    
    camera.rotation_mode = 'XYZ'
    
    x = camera.rotation_euler[2] + (x * (pi / 180.0))
    camera.rotation_euler[2] = x 
    
    update()
    
  
    co_2d = bpy_extras.object_utils.world_to_camera_view(scene, obj, co)

    # If you want pixel coords
    render_scale = scene.render.resolution_percentage / 100
    
    render_size = (
    int(scene.render.resolution_x * render_scale),
    int(scene.render.resolution_y * render_scale),
    )
    x = round(co_2d.x * render_size[0])
    print(x, "x cordinate")
    return x
#import bpy
#import bpy_extras

scene = bpy.context.scene
obj = bpy.context.object
co = monkey.location

#pixels = 200

#pid = PID(50, 0.01, 0.5, setpoint=pixels)
#v = update1(pixels)
#update1(0)


#while True:
#    # compute new ouput from the PID according to the systems current value
#    control = pid(v)
#    print(control, " control" )
#    v = update1(control)
#    if pixels == v:
#        break




#co_2d = camera_to_world_view(scene, obj, co)
#print("3d Coords:", co_2d)


#obj = bpy.data.objects["Camera"]
#cube = bpy.data.objects["Cube"]


#angle = 2 # or pi/2
#axis = [0,0,1]  # the z axis
#axis = cube.location.normalized().cross(obj.location.normalized())
#print(axis)
#qrot = Quaternion(axis,angle)



#obj.rotation_mode = 'QUATERNION'
#obj.rotation_quaternion = qrot   # expects a quaternion


#print(obj.location.angle(cube.location))
#print(cube.location, obj.location)
##.angle(mathutils.Vector((v1.x,v1.y,v1.z)))





from mathutils import Matrix














def get_calibration_matrix_K_from_blender(camd):
    f_in_mm = camd.lens
    scene = bpy.context.scene
    resolution_x_in_px = scene.render.resolution_x
    resolution_y_in_px = scene.render.resolution_y
    scale = scene.render.resolution_percentage / 100
    sensor_width_in_mm = camd.sensor_width
    sensor_height_in_mm = camd.sensor_height
    pixel_aspect_ratio = scene.render.pixel_aspect_x / scene.render.pixel_aspect_y
    if (camd.sensor_fit == 'VERTICAL'):
        # the sensor height is fixed (sensor fit is horizontal), 
        # the sensor width is effectively changed with the pixel aspect ratio
        s_u = resolution_x_in_px * scale / sensor_width_in_mm / pixel_aspect_ratio 
        s_v = resolution_y_in_px * scale / sensor_height_in_mm
    else: # 'HORIZONTAL' and 'AUTO'
        # the sensor width is fixed (sensor fit is horizontal), 
        # the sensor height is effectively changed with the pixel aspect ratio
        pixel_aspect_ratio = scene.render.pixel_aspect_x / scene.render.pixel_aspect_y
        s_u = resolution_x_in_px * scale / sensor_width_in_mm
        s_v = resolution_y_in_px * scale * pixel_aspect_ratio / sensor_height_in_mm


    # Parameters of intrinsic calibration matrix K
    alpha_u = f_in_mm * s_u
    alpha_v = f_in_mm * s_v
    u_0 = resolution_x_in_px * scale / 2
    v_0 = resolution_y_in_px * scale / 2
    skew = 0 # only use rectangular pixels

    K = Matrix(
        ((alpha_u, skew,    u_0),
        (    0  , alpha_v, v_0),
        (    0  , 0,        1 )))
    return K

K = get_calibration_matrix_K_from_blender(camera.data)
coord = Vector([20, 2, 1])   
5000
coord = Vector([-5000, -5000, 3])  

print(coord)  # <Vector (-3.5007, -7.1511, 0.1595)>

tt = K.inverted() @ coord 


center_obj(camera, tt)