    for i, v in enumerate( vertices ):
        count += 1
    
        # Get the 2D projection of the vertex
        co2D = world_to_camera_view( scene, cam, v )

        # By default, deselect it
        #obj.data.vertices[i].select = False
        
        # If inside the camera view
        if 0.0 <= co2D.x <= 1.0 and 0.0 <= co2D.y <= 1.0: 
            # Try a ray cast, in order to test the vertex visibility from the camera
            location, normal, index, distance, t, ty = scene.ray_cast(viewlayer, cam.location, (v - cam.location).normalized() )
            t = (v-normal).length
            print(t)
            if t < 0.000008:
                same_count += 1
                print(v)
                bpy.ops.curve.primitive_bezier_curve_add()
                obj = bpy.context.object
                obj.data.dimensions = '3D'
                obj.data.fill_mode = 'FULL'
                obj.data.bevel_depth = 0.001
                obj.data.bevel_resolution = 4
                # set first point to centre of sphere1
                obj.data.splines[0].bezier_points[0].co = (0,-6,1)
                obj.data.splines[0].bezier_points[0].handle_left_type = 'VECTOR'
                # set second point to centre of sphere2
                obj.data.splines[0].bezier_points[1].co = v
                obj.data.splines[0].bezier_points[1].handle_left_type = 'VECTOR'
        ray_percent = same_count/ count
        print(ray_percent, "ray percent")