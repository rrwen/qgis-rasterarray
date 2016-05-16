 
# RasterArray.py  

A Python module for manipulating geographic raster image data in QGIS using numpy arrays. Includes a demonstration for Conway's Game of Life.  

* **View the [Game of Life Blog Post](http://gis.blog.ryerson.ca/2015/03/)**
* **View [Example.txt](https://github.com/rwenite/QGIS_RasterArray/blob/master/Example.txt) for an example run.**  

_Dependencies: QGIS 2.6.1 Brighton, Python 2.7_  
  
  
#  Authors:
  
  
* Richard Wen (rwen@ryerson.ca)
* Dr. Claus Rinner (crinner@ryerson.ca)
  

#  QGIS Python Console Setup:
  
  
 1. Go to the python command console in QGIS  
   `(Plugins > Python Console)`
  
 2. Enter in the console:  
    `import sys`
  
 3. Find the location path of this script  
    `C:\\User\\Desktop`
  
 4. Append it to the QGIS system paths with:  
       `sys.path.append(FILE_PATH_HERE)`   
       `sys.path.append ("C:\\User\\Desktop")`
      
 5.  Import the Cells class for use in the console:  
    `from RasterArray import *`
  
  
# Cells:
  
  
##  A. Creating the Cells Object  
  
 * Create a Cells object as a random array:
   
    `cellsObject = Cells()`
  
 * Create a Cells object as a filled array:
   
    `cellsObject = Cells(inRaster=n)`  
    + n is the value to fill the array with
  
 * Create a Cells object as a custom array:
   
    `cellsObject = Cells(inRaster=[(r1c1,r1c2,r1c3),(r2c1,r2c2,r2c3)])`  
    + r1c1..rncn refers to row 1 (r1) and column 1(c1) to row n (rn) and column n (cn)  
    + The containers [] define a list and () define a tuple
  
 * Create a Cells object with a raster file:
 
    `cellsObject = Cells ("path_to_raster_file")`  
    + "path_to_raster_file" is the location of the raster with
      extension
  
##  B. Modifying and Obtaining Cell Values  
   
 * Modify a cell value:
   
    `cellsObject.modify(x, y, value)`  
    + x and y are the coordinates of the cell to modify  
    + value is the value to replace the cell value at the location  
    + for non-geographic coordinates, use (x, y, value, geographic=False)
  
 * Obtain a cell value:
 
    `cellsObject.get(x, y)`  
    + x and y are coordinates of the cell to obtain  
    + for non-geographic coordinates, use (x, y, value, geographic=False)
  
##  C. Output to Raster TIF  
  
 * Output a raster representing the changes:
 
    `cellsObject.toRaster("path_to_output_raster_file")`  
    + "path_to_output_raster_file" is the location of the output
      raster file with extension
  
##  D. Additional Settings  
  
 * Set the band of the raster
   
    `cellsObject = Cells (nband=n)`  
    + n is band number of the input raster, does not work for default
  
 * Set the spatial reference system of the randomly generated raster
   
    `cellsObject = Cells (EPSG=coorSys)`  
    + coorSys is the EPSG number of the spatial reference of the randomly generated raster
  
 * Setting the dimensions and cell measurements of the randomly generated raster
   
    `cellsObject = Cells (cols=c,rows=r,pixelWidth=w,pixelHeight)`  
    + c and r are inputs in whole numbers to specify the number of columns and rows  
    + w and h are inputs in real numbers to specify the width and height of cells
  
  
# GameofLife:
  
  
##  A. Creating a GameofLife Object  
  
 * Create a GameofLife object:  

    `GoLObject = GameofLife()`
  
##  B. Cycling the Game Board  
  
 * Cycle the game n times:  

    `GoLObject.cycle(n)`  
    + n is the number of times to cycle the gaming board
  
 * Reset the game:

    `x.reset()`  
    + reset the gaming board to the initial state
  
##  C. Additional Settings  
  
###C1. Data  
  
 * Set the initial board when creating the GameofLife object:
   
    `GoLObject = GameofLife(raster="path_to_raster_file")`  
    + "path_to_raster_file" is the path to the raster file with extension to be used for the initial board
  
 * Set whether or not to overwrite cycles:

    `GoLObject.overwrite = boolean`  
    + boolean is set to True or False, where True overwrites each cycle, and False does not overwrite each cycle
  
 * Set the spatial reference system of the randomly generated raster
   
    `GoLObject = GameofLife(EPSG=coorSys)`  
    + coorSys is the EPSG number of the spatial reference of the randomly generated raster
  
###C2. Aesthetics  
  
 * Set the style of the start and cycle boards with a qml file:

    `GoLObject.qmlStyle = "path_to_qml_file"`  
    + "path_to_qml_file" is the path to the QGIS .qml style file used for changing the style of the output board
  
 * Set the refresh speed:

    `GoLObject.speed = x`  
    + x is the refresh speed in seconds before processing the next cycle
  
###C3. Dimensions  
  
 * Set the width and height when creating the GameofLife object:
   
    `GoLObject = GameofLife(width=w, height=h)`  
    + w and h are inputs in whole numbers to specify the width and height of the randomly generated board
  
* Set the raster cell sizes when creating the GameofLife object:

    `GoLObject = GameofLife(cellWidth=w, cellHeight=h)`  
    + w and h are inputs in real numbers to specify the width and height of cells in the randomly generated board
  
  
