 RasterArray.py
 Richard Wen @ Ryerson University (rwen@ryerson.ca)
 V0.03a
 --
 Dependencies: QGIS 2.6.1 Brighton, Python 2.7
 Developed on: Windows 8 64-bit
 Last Updated: 23 February 2015

Below are instructions to utilize and get the RasterImage Module running in QGIS console.
See Example.txt for an example run.

Module Setup:
 
 * 1. Go to the python command console in QGIS
      (Plugins > Python Console)
 
 * 2. Enter in the console:
      import sys
 
 * 3. Find the location path of this script
      -- Example: C:\\User\\Desktop
 
 * 4. Append it to the QGIS system paths with:
      sys.path.append(FILE_PATH_HERE)
      -- Example: sys.path.append ("C:\\User\\Desktop")
      
 * 5. Import the Cells class for use in the console:
      from RasterArray import *
 
Cells Class Usage:
 
 * Create a Cells object with a raster file:
 
   cellsObject = Cells ("path_to_raster_file")
   -- "path_to_raster_file" is the location of the raster with
      extension
   
 * Modify a cell value:
   
   cellsObject.modify(x,y, value)
   -- x and y are the coordinates of the cell to modify
   -- value is the value to replace the cell value at the location
   -- for non-geographic coordinates, use geographic=False

 * Obtain a cell value:
 
   cellsObject.get(x,y)
   -- x and y are coordinates of the cell to obtain
   -- for non-geographic coordinates, use geographic=False
   
 * Output a raster representing the changes:
 
   cellsObject.toRaster("path_to_output_raster_file")
   -- "path_to_output_raster_file" is the location of the output
      raster file with extension

GameofLife Class Usage:

 * Create a GameofLife object:

   GoLObject = GameofLife()

 * Cycle the game n times:

   GoLObject.cycle(n)
   -- n is the number of times to cycle the gaming board

 * USEFUL SETTINGS *

 * Set the style of the start and cycle boards with a qml file:

   GoLObject.qmlStyle = "path_to_qml_file"
   -- "path_to_qml_file" is the path to the QGIS .qml style file used for changing the style of the output boards

 * Set the refresh speed:

   GoLObject.speed = x
   -- x is the refresh speed in seconds before processing the next cycle

 * Set the width and height when creating the GameofLife object:
   
   GoLObject = GameofLife(width=w, height=h)
   -- w and h are inputs in whole numbers specify the width and height of the randomly generated board

 * Set the initial board when creating the GameofLife object:
   
   GoLObject = GameofLife(raster="path_to_raster_file")
   -- "path_to_raster_file" is the path to the raster file with extension to be used for the initial board

 * Set whether or not to overwrite cycles:

   GoLObject.overwrite = boolean
   -- boolean is set to True or False, where True overwrites each cycle, and False does not overwrite each cycle
