def batch_render(file_prefix="render", image_dir="./renders/"):

    scene_setup_steps = 2
    value = True
    loop_count = 0
    labels = []
    while loop_count != scene_setup_steps:
        
        object = bpy.data.objects["Suzanne"]
        scene = bpy.context.scene
        camera = bpy.data.objects['Camera']
        
        randomize_obj(object, 2.5, 3.5, 1.7)
        scene = randomize_camera(scene, camera, 2.5, 3.5, 1.7)
        increment_frames(scene, 40)


         
        center_obj(camera, object)

        offset(scene, camera, 80)
        
        value, percent = get_raycast_percentage(scene, camera, object, 15)
        print(percent, "percent in view")
        if value == False:
            loop_count -= 1
            value = True
        else:
            
            
            # checks whether your output is jpeg or png or another format
            file_format = scene.render.image_settings.file_format.lower()
            filename = f'{file_prefix}-{str(loop_count)}.{file_format}'
            
            #write image out
            bpy.context.scene.render.filepath = f'{image_dir}{filename}'
            bpy.ops.render.render(write_still=True)
            
            
            #pull cordinates
            scene_labels = get_cordinates(scene, camera, object, filename)
            labels.append(scene_labels) 
            print(scene_labels, "loop Iter")
        

            labels.append(scene_labels) # Merge lists
        print(labels, "outide if")
        loop_count += 1
    print(labels, "labels at end")
    with open('./renders/labels.json', 'w+') as f:
        json.dump(labels, f, sort_keys=True, indent=4, separators=(',', ': '))





def batch_render(image_dir="./renders/", file_prefix="render", loop_count = 0):
    
        scene_setup_steps = 2
        value = True
        object = bpy.data.objects["Suzanne"]
        scene = bpy.context.scene
        camera = bpy.data.objects['Camera']

        while loop_count != scene_setup_steps:

            crandomize_obj(object, 2.5, 3.5, 1.7)
            scene = randomize_camera(scene, camera, 2.5, 3.5, 1.7)
            increment_frames(scene, 40)


            
            center_obj(camera, object)

            offset(scene, camera, 80)
            
            value, percent = get_raycast_percentage(scene, camera, object, 15)
            
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


labels = list(batch_render(scene, image_count, filepath, file_format))

with open(f'{filepath}/labels.json', 'w+') as f:
    json.dump(labels, f, sort_keys=True, indent=4, separators=(',', ': '))