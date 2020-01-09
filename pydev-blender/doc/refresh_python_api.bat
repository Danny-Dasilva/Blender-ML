rem This command will refresh the predefinition (*.pypredef) files 
rem They are used in PyDev, to use its autocmpletation feature for Blender Python API objects
rem Just run it, to refresh the files in the doc\python_api\pypredef folder
rem It uses additional folder doc\python_api\pypredef-tmp for internal comparisons
rem
..\blender -b -P python_api/pypredef_gen.py
pause