import bpy
import random

def simulate(scene, mesh_objects, spawn_range, p_visible):
    scene.frame_set(0)
    for object in mesh_objects:
        if random.uniform(0, 1) <= p_visible:
            object.hide_set(False)
            object.hide_render = False
        else:
            object.hide_set(True)
            object.hide_render = True

        object.location.x = random.randrange(spawn_range[0][0], spawn_range[0][1])
        object.location.y = random.randrange(spawn_range[1][0], spawn_range[1][1])
        object.location.z = random.randrange(spawn_range[2][0], spawn_range[2][1])
    scene.frame_set(100)



if __name__ == '__main__':
    scene = bpy.data.scenes['Scene']
    mesh_names = ['Cube', 'Sphere']
    mesh_objects = [bpy.data.objects[name] for name in mesh_names]
    spawn_range = [
        (-10, 10),
        (-10, 10),
        (5, 10)
    ]
    simulate(scene, mesh_objects, spawn_range, 0.6)