import math

focal_length = 10 #mm
percent_of_image = (0.5,0.5) #between -1 and 1
sensor_size = (10,5) #mm
point_pos = [20,10,40] #x, y, z local to camera space z is straight out of the camera. Only works if object is in front of camera z is positive. Z positive is out the back of the camera so you may need to take abs value

def calculate_camera_rot(percent_of_image, focal_length, sensor_size, local_point_pos, percent_range=(0,1)):
    percent_of_image = [(percent-((percent_range[0]+percent_range[1])/2))*(2/(percent_range[1]-percent_range[0])) for percent in percent_of_image]
    print(percent_of_image)
    target_sensor_x = sensor_size[0]/2 * percent_of_image[0]
    target_vector_angle_x = math.degrees(math.atan(target_sensor_x/focal_length))
    current_vector_angle_x = math.degrees(math.atan(point_pos[0]/point_pos[2]))

    target_sensor_y = sensor_size[1]/2 * percent_of_image[1]
    target_vector_angle_y = math.degrees(math.atan(target_sensor_y/focal_length))
    current_vector_angle_y = math.degrees(math.atan(point_pos[1]/point_pos[2]))
    print(target_vector_angle_y,current_vector_angle_y)
    camera_xRot_delta = current_vector_angle_x - target_vector_angle_x
    camera_yRot_delta = current_vector_angle_y - target_vector_angle_y

    return (camera_xRot_delta, camera_yRot_delta)

camera_rot_delta = calculate_camera_rot(percent_of_image, focal_length, sensor_size, point_pos, percent_range=(-1,1))
print(camera_rot_delta)

