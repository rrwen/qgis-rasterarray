'''
 RasterArray.py
 Richard Wen @ Ryerson University (rwen@ryerson.ca)
 V0.03a
 --
 Dependencies: QGIS 2.6.1 Brighton, Python 2.7
 Developed on: Windows 8 64-bit
 Last Updated: 28 February 2015
 
===============================================================
 
 Contains classes for raster image data interaction using
 numpy array structures.
 
 Modules [Submodules]:
 * osgeo [gdal, osr]
 * qgis [core, qgsMapLayerRegistry, QgsRasterLayer]
 * numpy
 * os
 * time
 * shutil
 
 Helpers:
 * (H1.) Array2Raster
 * (H2.) xyOffset
 * (H3.) createDirectory
 
 Classes [Methods]:
 * (1.) Cells [get, modify, toRaster]
 * (2.) GameofLife [cycle, reset]
   
===============================================================
'''

# =============================================================
# A. Modules
# =============================================================
from osgeo import gdal, osr
import qgis, numpy, os, time, shutil
from qgis.core import QgsMapLayerRegistry, QgsRasterLayer

# =============================================================
# B. Helpers
# =============================================================

# (H1.) Array2Raster: str str (tupleof float) int int int
#                     -> None
# -------------------------------------------------------------
#
# Converts a numpy array into a raster image at the specified
# directory in geotif format.
# * Modified from Python GDAL/OGR Cookbook 1.0 @
#   http://pcjericks.github.io/py-gdalogr-cookbook/
#   raster_layers.html#create-raster-from-array
#
# -------------------------------------------------------------
def Array2Raster(inArray,
                 outRaster,
                 rasterOrigin,
                 pixelWidth,
                 pixelHeight,
                 EPSG):
    
    # (H1.1) Obtain Array Information
    cols = inArray.shape[1]
    rows = inArray.shape[0]
    originX = rasterOrigin[0]
    originY = rasterOrigin[1]
    
    # (H1.2) Write Array to Raster       
    driver = gdal.GetDriverByName('GTiff')
    outRaster = driver.Create(outRaster, cols, rows, 1, gdal.GDT_Byte)
    outRaster.SetGeoTransform((originX, pixelWidth, 0, originY, 0, pixelHeight))
    outband = outRaster.GetRasterBand(1)
    outband.WriteArray(inArray,0,0)
    outRasterSRS = osr.SpatialReference()
    outRasterSRS.ImportFromEPSG(EPSG)
    outRaster.SetProjection(outRasterSRS.ExportToWkt())
    outband.FlushCache()
    outband.SetNoDataValue(-99)
    
    # (H1.3) Reset
    driver = None
    outRaster = None
    outBand = None
    inArray = None

# (H2.) xyOffset: int int (tupleof float) float float
#                 -> (tupleof int)
# ----------------------------------------------------------
# 
# Calculates the offset for the geographic x and y locations 
# using the raster origin and cell dimensions.
#
# ----------------------------------------------------------    
def xyOffset (x, y, rasterOrigin, cellWidth, cellHeight):
    xOffset = int((x - rasterOrigin[0])/cellWidth) ## X
    yOffset = int(((y+1) - rasterOrigin[1])/cellHeight) ## Y
    return (xOffset, yOffset)

# (H3.) createDirectory: str -> str
# ----------------------------------------------------------
# 
# Creates the directory if it does not exist.
#
# ---------------------------------------------------------- 
def createDirectory(directory):    
    if not os.path.exists(directory):
	os.makedirs(directory)
    return directory

# =============================================================
# C. Classes
# =============================================================

# (1.) Cells: str int int -> None
# -------------------------------------------------------------
#
# A cells object obtained from a raster image file with a
# selected band. The cells represent an array that is mutable
# with method calls. The cells object can then be converted
# to a raster representing changes made to the original raster.
# * An appropriate EPSG number must be set
#
# -------------------------------------------------------------
class Cells (object):
    
    # (1.0) Initial Settings
    # ---------------------------------------------------------
    def __init__(self, inDir, nband=1, EPSG=4326):
        
        # (1.0.1) Obtain Raster Information
        openRaster = gdal.Open(inDir)
        band = openRaster.GetRasterBand(nband) # get single band
        rows = openRaster.RasterYSize # dimension rows
        cols = openRaster.RasterXSize # dimension columns
        geotransform = openRaster.GetGeoTransform()
        rasterOrigin = (geotransform[0], geotransform[3]) # coor of rast origin
        pixelWidth = geotransform[1] # cell size x
        pixelHeight =  geotransform[5] # cell size y
        
        # (1.0.2) Obtain Array Data     
        array = band.ReadAsArray(0, 0, cols, rows).astype(numpy.float)
        
        # (1.0.3) Main Fields
        self.inRaster = openRaster
        self.arrayData = array
        
        # (1.0.4) Sub Fields
        self.EPSG = EPSG
        self.cols = cols
        self.rows= rows
        self.origin = rasterOrigin
        self.cellWidth = pixelWidth
        self.cellHeight = pixelHeight
       
    # (1.1) modify: int int num -> None
    # ----------------------------------------------------------
    # 
    # Modifies the cell at the location with a new value set by
    # the user.
    # * Mutates the arrayData field
    #
    # ----------------------------------------------------------
    def modify (self, x, y, value, geographic=True):
        
        # (1.1.1) Calculate XY Geographic Offsets If Needed
	if geographic:
	    Offsets = xyOffset (x,
		               y,
		               self.origin,
		               self.cellWidth,
		               self.cellHeight)
	else:
	    Offsets = (x,y)
        
        # (1.1.2) Modify Array
        self.arrayData[Offsets[0],Offsets[1]] = value
        
    # (1.2) get: int int -> float
    # ----------------------------------------------------------
    # 
    # Obtains the value of the cell at the user specified
    # location.
    #
    # ----------------------------------------------------------    
    def get (self, x, y, geographic=True):
        
        # (1.2.1) Calculate XY Geographic Offsets If Needed
	if geographic:
	    Offsets = xyOffset (x,
		                y,
		                self.origin,
		                self.cellWidth,
		                self.cellHeight)
	else:
	    Offsets = (x,y)
                
        # (1.2.2) Return Cell Value        
        return self.arrayData[Offsets[0],Offsets[1]]          

    # (1.3) toRaster: str -> None
    # ----------------------------------------------------------
    #
    # Creates a raster from the array data supplied by the class
    # at the location speicifed by the user.
    #
    # ----------------------------------------------------------
    def toRaster(self, outRaster):
        Array2Raster(self.arrayData,
                     outRaster,
                     self.origin,
                     self.cellWidth,
                     self.cellHeight,
                     self.EPSG)

# (2.) GameofLife: str str -> None
# -------------------------------------------------------------
#
# Based on Conway's Game of Life, creates a game of life object
# from a randomly generated raster or a given raster file. The
# user may then choose to start the game, and iterate through
# a given number of cycles.
# * Utilizes the Cells class from the RasterArray Module
#
# -------------------------------------------------------------
class GameofLife (object):
    
    # (2.0) Initial Settings
    # ---------------------------------------------------------
    def __init__(self,
                 out_directory="default",
                 EPSG=4326,
                 raster = "random",
                 band=1,
                 origin=(0,0),
                 width=25,
                 height=25,
                 cellWidth=1,
                 cellHeight=1,
                 overwrite=True,
                 qmlStyle=os.path.join(
                     os.path.dirname(os.path.realpath(__file__)),
                     "GameofLife_Style.qml")):
	
	# (2.0.1) Create Default Path at Script Directory
	if out_directory is "default":
	    outPath = os.path.join(os.path.dirname(os.path.realpath(__file__)),
	                           "GameofLife_Output")
	    createDirectory(outPath)
	else:
	    outPath = createDirectory(out_directory)
        
        # (2.0.1) Create Random Raster if no raster settings defined
        if raster is "random":
            random_array = numpy.random.randint(2,size = (height,width))
            rasterPath = os.path.join(outPath,"start.tif")
            Array2Raster(random_array,
                         rasterPath,
                         origin,
                         cellWidth,
                         cellHeight,
                         EPSG)
        
        # (2.0.2) Otherwise use the Raster Defined by the User
        else:
            rasterPath = raster
	    
	# (2.0.3) Add Raster to Display
	startLayer = QgsRasterLayer(rasterPath, "start")
	startLayer.loadNamedStyle(qmlStyle)
	QgsMapLayerRegistry.instance().addMapLayer(startLayer)
        
        # (2.0.4) Main Field Settings
	self.startRaster = rasterPath
        self.inRaster = rasterPath
        self.output = outPath
	self.cycles=0
        self.board = Cells(rasterPath, band, EPSG)
        self.speed = 0.65 ## delay in seconds after creating each cycle
	self.overwrite = overwrite ## whether or not to overwrite each cycle
	self.style = qmlStyle ## raster legend style
	
	# (2.0.6) Sub Field Settings
	self.EPSG = EPSG
	self.band = band
        
    # (2.1) cycle: int -> None
    # ----------------------------------------------------------
    #
    # Cycles through the game of life board a number of times
    # (n) set by the user.
    # * Modified from code provided by Dr. Claus Rinner @
    #   Ryerson University
    #
    # ----------------------------------------------------------
    def cycle(self, n=1):
        
        # (2.1.1) Cycle Cells of Game Board n Times
	rows = self.board.rows
	cols = self.board.cols
	for cyclenum in range (0, n):
	    inBoard = Cells(self.inRaster,
	                    nband=self.band,
	                    EPSG=self.EPSG) ## store copy of original cells
	    self.cycles+=1 ## keep track of number of cycles
	    print ("Cycle: "+str(self.cycles))
	    
	    # (2.1.1) Iterate All Cells on Board n Times
	    for i in range(0, rows): 
		for j in range(0, cols):
		    sumNeighbors = 0 ## counter for neighbors
		    
		    # (2.1.1) Transitions
		    for k in range(i-1, i+1): 
			for l in range(j-1, j+1):
			    # Wrap around edges using mod function
			    sumNeighbors = sumNeighbors +\
			                 inBoard.get(k%rows,l%cols,
			                             geographic=False)
			    # Obtain Value
			    boardValue = self.board.get(i,j,
			                                geographic=False)
			    # (2.1.1a) Alive Cells
			    if boardValue == 1:
				# Under-population
				if sumNeighbors < 2:
				    self.board.modify(i,j,0,
					              geographic=False)
				# Over-crowding
				elif sumNeighbors > 3:
				    self.board.modify(i,j,0,
					              geographic=False)
			    
			    # (2.1.1b) Reproduction
			    elif boardValue == 0 and sumNeighbors == 3:
				self.board.modify(i,j,1,
				                  geographic=False)
			    
			    # (2.1.1c) No Change
			    else:
				self.board.modify(i,j,
				                  inBoard.get(i,j,geographic=False),
				                  geographic=False)
	
	    # (2.1.2) Save Cycle as Raster
	    ## Overwrite Raster if needed
	    if self.overwrite:
		outLayer = "cycle"
		QgsMapLayerRegistry.instance().removeAllMapLayers()
	    ## Otherwise Produce Rasters
	    else:
		outLayer = "cycle"+str(self.cycles)
	    ## Set input raster to new cycle
	    outCyclePath = os.path.join(self.output,
	                                outLayer+".tif")
	    self.board.toRaster(outCyclePath)
	    self.board = Cells(outCyclePath,self.band,self.EPSG)
	    self.inRaster = outCyclePath
	    
	    # (2.1.3) Display the Saved Raster Cycle
	    rlayer = QgsRasterLayer(outCyclePath, outLayer)
	    rlayer.loadNamedStyle(self.style)
	    QgsMapLayerRegistry.instance().addMapLayer(rlayer)
	    time.sleep(self.speed) ## suspend display
	    
    # (2.2) reset: None -> None
    # ----------------------------------------------------------
    #
    # Resets the game to the starting board.
    #
    # ----------------------------------------------------------
    def reset (self):
	
	# (2.2.1) Reset the Game Board and Cycles
	QgsMapLayerRegistry.instance().removeAllMapLayers() ## clear disp
	self.cycles=0
	self.inRaster=self.startRaster
	self.board=Cells(self.startRaster,self.band,self.EPSG)
	startLayer = QgsRasterLayer(self.inRaster, "start")
	QgsMapLayerRegistry.instance().addMapLayer(startLayer)
	
	# (2.2.2) Delete the Cycle Files
	for the_file in os.listdir(self.output):
	    file_path = os.path.join(self.output, the_file)
	    if "cycle" in file_path:
		# Try to delete cycle files
		try:
		    os.remove(file_path)
		# Notify if unable to delete cycle file
		except Exception:
		    basename = os.path.basename(os.path.splitext(file_path)[0])
		    print ("**Unable to Delete Cycle Raster: "+basename)
