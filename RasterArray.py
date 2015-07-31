'''
 RasterArray.py
 Richard Wen @ Ryerson University (rwen@ryerson.ca)
 V0.05a
 
 Dependencies: QGIS 2.6.1 Brighton, Python 2.7
 Developed on: Windows 8 64-bit
 
===============================================================
 
 Contains classes for raster image data interaction using
 numpy array structures.
 
 Modules: Submodules
 -------------------
 * osgeo: gdal, osr
 * qgis: core, qgsMapLayerRegistry, QgsRasterLayer
 * numpy
 * os
 * time
 * shutil
 
 Helpers
 -------
 * (H1.) Array2Raster
 * (H2.) xyOffset
 * (H3.) createDirectory
 
 Classes: Methods
 ----------------
 * (1.) Cells: get, modify, toRaster
 * (2.) GameofLife: cycle, reset
   
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

'''
 (H1.) Array2Raster: numpyArray str (tupleof float) str
                     (tupleof float) float float int -> Effect
 
---------------------------------------------------------------

 Converts a numpy array into a raster image at the specified
 directory in geotif format (.tif)
 
 Notes
 -----
 * Modified from Python GDAL/OGR Cookbook 1.0 @
   http://pcjericks.github.io/py-gdalogr-cookbook/
  raster_layers.html#create-raster-from-array

 Required Parameters
 -------------------
 * inArray: numpyArray
         The numpy array to be converted into a geographic raster.
 * outRaster: str
         The output raser path with geotif extenstion (.tif).
 * rasterOrigin: (tupleof float)
         The geographic origin of the output raster.
 * pixelWidth: float
         The width of a cell in the raster.
 * pixelHeight: float
	The height of a cell in the raster.
 * EPSG: int
         The spatial reference system number to define the
         raster in.
 
 Effects
 -------
 * Produces a geotif raster at the [outRaster] directory
   location

---------------------------------------------------------------
'''
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
    outRaster = driver.Create(outRaster,
                              cols,
                              rows,
                              1,
                              gdal.GDT_Byte)
    outRaster.SetGeoTransform((originX,
                               pixelWidth,
                               0,
                               originY,
                               0,
                               pixelHeight))
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
    
'''
 (H2.) xyOffset: int int (float,float) float float
		 -> (int int)
------------------------------------------------------------

 Calculates the offset for the geographic x and y locations 
 using the raster origin and cell dimensions.
 
 Required Parameters
 -------------------
 * x: int
         The x-axis, row, geographic coordinate.
 * y: int
         The y-axis, row, geographic coordinate.
 * rasterOrigin: (float, float)
         The raster's origin coordinates.
 * cellWidth: float
         The width of a cell in the raster.
 * cellHeight: float
         The height of a cell in the raster.
 
 Output
 ------
 A tuple of integers representing the array position from
 the geographic coordinates [rasterOrigin].

---------------------------------------------------------------
'''
def xyOffset (x, y, rasterOrigin, cellWidth, cellHeight):
    xOffset = int((x - rasterOrigin[0])/cellWidth) ## X
    yOffset = int(((y+1) - rasterOrigin[1])/cellHeight) ## Y
    return (xOffset, yOffset)

'''
 (H3.) createDirectory: str -> Effect
---------------------------------------------------------------
 
 Creates a directory.
 
 Required Parameters
 -------------------
 * directory: str
         The path to create the folder at.
 
 Effects
 -------
 Creates a folder at the [directory], it the folder does
 not exist.

---------------------------------------------------------------
'''
def createDirectory(directory):    
    if not os.path.exists(directory):
	os.makedirs(directory)
    return directory

# =============================================================
# C. Classes
# =============================================================

'''
 (1.) Cells: (str/int/float/None) int int (float, float)
              int int float float -> Object
-------------------------------------------------------------

 A cells object obtained from a raster image file with a
 selected band. The cells represent an array that is mutable
 with method calls. The cells object can then be converted
 to a raster representing changes made to the original raster.
 
 Notes
 -----
 * An appropriate EPSG number must be set, the default is 4326
 * If no input directory is specified, a random raster will be
   used

 Optional Parameters
 -------------------
 * inRaster: (str/int/float/None)
         The input raster to be created or read.
           - If int/float, fill raster with the number
           - If str, read the raster from str path
           - If None, create random raster and read it
 * nband: int
         The band of the raster to read from.
 * EPSG: int
         The spatial reference system number of the raster.
 * rasterOrigin: (float, float)
         The geographic origin coordinates of the raster.
 * cols: int
         The number of columns in the raster.
 * rows: int
         The number of rows in the raster.
 * pixelWidth: float
         The pixel width of the raster.
 * pixelHeight: float
	The pixel height of the raster.
   
 Object Attributes
 -----------------
 * self.array: numpyArray
         A numpy array representing the [inRaster]
 * self.EPSG: int
         [EPSG]
 * self.cols: int
         [cols]
 * self.rows: int
         [rows]
 * self.origin: (float, float)
         [rasterOrigin]
 * self.cellWidth: float
         [pixelWidth]
 * self.cellHeight: float
         [pixelHeight]
 
 Object Methods
 --------------
 * (1.1) modify
         Modify a cell's value.
 * (1.2) get
         Get a cell's value.
 * (1.3) toRaster
         Convert the array into a geotif raster, with changes if 
         applicable.

-------------------------------------------------------------
'''
class Cells (object):
    
    # (1.0) Initialization
    # -------------------------------------------------------
    def __init__(self,
                 inRaster=None,
                 nband=1,
                 EPSG=4326,
                 rasterOrigin=(0,0),
                 cols=10,
                 rows=10,
                 pixelWidth=1,
                 pixelHeight=1):
        
	# (1.0.0) Default Random Cells
	if inRaster == None:
	    array = numpy.random.randint(2,size = (rows,cols))
	
	# (1.0.1) Cell Filled with Numbers
	elif isinstance(inRaster,(int, long, float, complex)):
	    array = numpy.zeros((rows,cols))
	    array.fill(inRaster)
	
	# (1.0.2) Custom Cell with List
	elif isinstance(inRaster,(list, tuple)):
	    array = numpy.array(inRaster)
	    shape = array.shape
	    rows = shape[0]
	    cols = shape[1]
	    
	# (1.0.3) Specified Raster
	else:
	    
	    # (1.0.3a) Obtain Raster Information
	    openRaster = gdal.Open(inRaster)
	    band = openRaster.GetRasterBand(nband) ## get single band
	    rows = openRaster.RasterYSize ## dimension rows
	    cols = openRaster.RasterXSize ## dimension columns
	    geotransform = openRaster.GetGeoTransform()
	    rasterOrigin = (geotransform[0], geotransform[3]) ## coor of origin
	    pixelWidth = geotransform[1] ## cell size x
	    pixelHeight =  geotransform[5] ## cell size y
	    
	    # (1.0.3b) Obtain Array Data     
	    array = band.ReadAsArray(0, 0, cols, rows).astype(numpy.float)
        
        # (1.0.4) Attributes
        self.array = array
        self.EPSG = EPSG
        self.cols = cols
        self.rows= rows
        self.origin = rasterOrigin
        self.cellWidth = pixelWidth
        self.cellHeight = pixelHeight
     
    '''
     (1.1) modify: int int float bool -> Effect
    --------------------------------------------------------
     
     Modifies the cell at the location with a new value set by
     the user.
     
     Required Parameters
     -------------------
     * x: float/int
             The x-axis, row, reference.
     * y: float/int
             The y-axis, row, reference.
     * value: float/int
             The value to be set at the [x] and [y] location
    
     Optional Parameters
     -------------------
     * geographic: bool
             Set to determine if [x] and [y] are geographic
	     coordinates instead of array references.
	       - If True, [x][y] are geographic references
	       - If False, [x][y] are array references
	 
     Effects
     -------
     Mutates the [self.array] field at [x] and [y]
       
    --------------------------------------------------------
    '''
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
        self.array[Offsets[1],Offsets[0]] = value
	
    '''
     (1.2) get: int int bool -> float
    --------------------------------------------------------
     
     Obtains the value of the cell at the user specified
     location.
     
     Required Parameters
     -------------------
     * x: float/int
             The x-axis, row,, column, reference.
     * y: float/int
             The y-axis, row,, row, reference.
	 
     Optional Parameters
     -------------------
     * geographic: bool
             Set to determine if [x] and [y] are geographic
	     coordinates instead of array references.
	       - If True, [x][y] are geographic references
	       - If False, [x][y] are array references
	 
     Output
     ------
     Returns the value at the [x] and [y] location
    
    --------------------------------------------------------
    '''
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
        return self.array[Offsets[1],Offsets[0]] 
    
    '''
     (1.3) toRaster: str -> Effect
    --------------------------------------------------------
    
     Creates a raster from the array data supplied by the 
     class at the location speicifed by the user.
     
     Required Parameters
     -------------------
     * outRaster: str
             The location path to produce the geotif raster
	     from the [self.array] attribute.
	 
     Effects
     -------
     Creates a geotif (.tif) format raster at the 
     [outRaster] location path with the array from the
     [self.array] attribute.
    
    --------------------------------------------------------
    '''
    def toRaster(self, outRaster):
        Array2Raster(self.array,
                     outRaster,
                     self.origin,
                     self.cellWidth,
                     self.cellHeight,
                     self.EPSG)
	
'''
 (2.) GameofLife: str int str int (float,float) int int
                  float float bool str -> Object
-------------------------------------------------------------

 Based on Conway's Game of Life, creates a game of life object
 from a randomly generated raster or a given raster file. The
 user may then choose to start the game, and iterate through
 a given number of cycles.

 Notes
 -----
 Utilizes the Cells class from the RasterArray Module
 
 Optional Parameters
 -------------------
 * outDirectory: None/str
         The output directory to transfer the cycled 
	 rasters.
 * EPSG: int
         The spatial reference number of the rasters to
	 be cycled.
 * raster: None/str
         The raster to be used as the starting board.
	   - If None, starting board is a random board
	   - If str, starting board is the path at str
 * band: int
         The band number of the [raster]
 * origin: (float,float)
         The origin coordiantes of the [raster]
 * width: int
         The width of the [raster]
 * height: int
         The height of the [raster]
 * cellWidth: float
         The width of a cell in the [raster]
 * cellHeight: float
         The height of a cell in the [raster]
 * overwrite: bool
         Whether or not to overwrite cycled raster.
	   - If True, overwrite and don't save cycles
	   - If False, save cycles at [outDirectory]
 * qmlStyle: str
         The style file to be used to visualize
	 the [raster] and its cycles.
	 
 Object Attributes
 -----------------
 * self.startRaster: str
         Path to the input starting raster.
 * self.inRaster: str
         Path to the raster to be cycled.
 * self.output: str
         Path to the output cycled raster at [outDirectory]
 * self.cycles: int
         The cycle count so far.
 * self.board: obj
         The board, stored as a Cells object.
 * self.speed: float
         The speed in which to delay the board by.
 * self.overwrite: bool
         [overwrite]
 * self.style: str
         [qmlStyle]
 * self.EPSG: int
         [EPSG]
 * self.band: int
         [band]
	 	 
 Object Methods
 --------------
 * (2.1) cycle
         Cycle the board a number of times.
 * (2.2) reset
         Reset current board to the starting board.

-------------------------------------------------------------
'''
class GameofLife (object):
    
    # (2.0) Initial Settings
    # -------------------------------------------------------
    def __init__(self,
                 out_directory=None,
                 EPSG=4326,
                 raster = None,
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
	if out_directory == None:
	    outPath = os.path.join(os.path.dirname(os.path.realpath(__file__)),
	                           "GameofLife_Output")
	    createDirectory(outPath)
	else:
	    outPath = createDirectory(out_directory)
        
        # (2.0.1) Create Random Raster if no raster settings defined
        if raster == None:
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
        
        # (2.0.4) Main Attribute Settings
	self.startRaster = rasterPath
        self.inRaster = rasterPath
        self.output = outPath
	self.cycles=0
        self.board = Cells(rasterPath, band, EPSG)
        self.speed = 0.65 ## delay in seconds after creating each cycle
	self.overwrite = overwrite ## whether or not to overwrite each cycle
	self.style = qmlStyle ## raster legend style
	
	# (2.0.6) Sub Attribute Settings
	self.EPSG = EPSG
	self.band = band
	
    '''
     (2.1) cycle: int int -> Effect
    --------------------------------------------------------
    
     Cycles through the game of life board a number of times
     (n) set by the user.
     
     Notes
     -----
     Modified from code provided by Dr. Claus Rinner @
     Ryerson University
     
     Optional Parameters
     -------------------
     * n: int
             The number of times to cycle the booard.
     * jump: int
	     The jumps made for each interval it 
	     reaches [n]
	     
     Effect
     ------
     Creates cycled raster(s) as a geotif (.tif) at the
     [self.output] directory, updates [self.cycles],
     [self.inRaster], and [self.board]
    
    --------------------------------------------------------
    '''
    def cycle(self, n=1,jump=1):
        
        # (2.1.1) Cycle Cells of Game Board n Times
	sumTime = 0
	rows = self.board.rows
	cols = self.board.cols
	iterations = (n*jump)+1
	for cyclenum in range(1,iterations):
	     ## store copy of original cells
	    inBoard = Cells(self.inRaster,nband=self.band,EPSG=self.EPSG)
	    start_time = time.time() ## start cycle time
	    
	    # (2.1.1) Keep track of number of cycles
	    if cyclenum%jump == 0:
		self.cycles+=jump
		print "Cycle: " + str(cyclenum)
		
	    # (2.1.1) Iterate All Cells on Board n Times
	    for i in range(0, rows): 
		for j in range(0, cols):
		    sumNeighbors = 0 ## counter for neighbors
		    boardValue = inBoard.get(j,i,geographic=False)

		    # (2.1.1) Count Neighbours
		    for k in range(i-1, i+2): 
			for l in range(j-1, j+2):
			    ## Only count neighbours and not the cell itself
			    if (l,k) != (j,i):
				sumNeighbors = sumNeighbors+inBoard.get(l%cols,
				                                        k%rows,
				                                        geographic=False)
			
		    # (2.1.2a) Alive Cells
		    if boardValue == 1:
			## Under-population
			if sumNeighbors < 2:
			    self.board.modify(j,i,0,geographic=False)
			## Over-crowding
			elif sumNeighbors > 3:
			    self.board.modify(j,i,0,geographic=False)
		    
		    # (2.1.2b) Reproduction
		    elif boardValue == 0 and sumNeighbors == 3:
			self.board.modify(j,i,1,geographic=False)
	
	    # (2.1.3) Save Cycle as Raster
	    ## Overwrite Raster if needed
	    if self.overwrite:
		outLayer = "cycle"
	    ## Otherwise Produce Rasters
	    else:
		outLayer = "cycle"+str(self.cycles)
	    ## Set input raster to new cycle
	    outCyclePath = os.path.join(self.output,
	                                outLayer+".tif")
	    self.board.toRaster(outCyclePath)
	    self.board = Cells(outCyclePath,self.band,self.EPSG)
	    self.inRaster = outCyclePath
	
	    # (2.1.4) Display the Saved Raster Cycle
	    if (cyclenum%jump == 0) or cyclenum+1 == iterations:
		if self.overwrite: ## remove layer displays if overwriting
		    QgsMapLayerRegistry.instance().removeAllMapLayers()
		rlayer = QgsRasterLayer(outCyclePath, outLayer)
		rlayer.loadNamedStyle(self.style)
		QgsMapLayerRegistry.instance().addMapLayer(rlayer)
		time.sleep(self.speed) ## suspend display
	    sumTime += (time.time() - start_time) ## end time cycles
	print "Average Cycle Time: " + str(round(sumTime/n,2)) + " sec"
	
    '''		
    (2.2) reset -> Effect
    --------------------------------------------------------
    
     Resets the game to the starting board.
     
     Effect
     ------
     Updates [self.inRaster] to the [self.startRaster] and
     resets [self.cycles] and [self.board]
    
    --------------------------------------------------------
    '''
    def reset (self):
	
	# (2.2.1) Reset the Game Board and Cycles
	QgsMapLayerRegistry.instance().removeAllMapLayers() ## clear disp
	self.cycles=0
	self.inRaster=self.startRaster
	self.board=Cells(self.startRaster,self.band,self.EPSG)
	startLayer = QgsRasterLayer(self.inRaster, "start")
	startLayer.loadNamedStyle(self.style)
	QgsMapLayerRegistry.instance().addMapLayer(startLayer)
	
	# (2.2.2) Delete the Cycle Files
	for the_file in os.listdir(self.output):
	    file_path = os.path.join(self.output, the_file)
	    if "cycle" in file_path:
		## Try to delete cycle files
		try:
		    os.remove(file_path)
		## Notify if unable to delete cycle file
		except Exception:
		    basename = os.path.basename(os.path.splitext(file_path)[0])
		    print ("**Unable to Delete Cycle Raster: "+basename)
