import numpy as np
from matplotlib import pyplot as plt
import matplotlib.image as mpimg
from scipy.ndimage.filters import median_filter
import cv2
from osgeo import gdal

class shoreline:
    def __init__(self, img_path, k, output_img_dir, output_geol_img_dir, name_file): # k is the size of the kernel define to reduce the speckle effect
        self.denoised = []
        self.land_mask = []
        self.water_mask = []
        self.shoreline = []
        self.image = []
        
        self.k = k
        self.image_path = img_path
        self.output_dir = output_img_dir 
        self.output_dir_geol = output_geol_img_dir
        self.name = name_file        
        
        self.calc_shoreline()
        
    def calc_shoreline(self, minVal=100, maxVal=200):
        img = mpimg.imread(self.image_path)
    
        self.denoised = self._denoise_image(img)
        self.land_mask = self._calc_land_mask()
        self.water_mask = self._calc_water_mask()
        
        self.canny_filter = self._canny_filter()
        
        self.shoreline = self._shoreline()
        
        self.shoreline_ref = self._shoreline_ref()
        
        return self.image, self.outdata
    
    def _denoise_image(self, img):
        denoised_image = median_filter(img, self.k)
        
        return denoised_image

    def _calc_land_mask(self, assigned_threshold_value=0, assigned_value=255):
        #img2 = denoised_image
        threshold_value, land_mask = cv2.threshold(self.denoised, 0,255,cv2.THRESH_BINARY+cv2.THRESH_OTSU)
        print('threshold_value =', threshold_value)
        
        return land_mask #; threshold_value

    def _calc_water_mask(self, assigned_threshold_value_binarisation=127, assigned_value=255): #assigned_value is the value assigned to all the pixel major than the threshold (=127)
        # init kernel
        kernel = np.ones((7,7), np.uint8)
        
        opening = cv2.morphologyEx(self.land_mask, cv2.MORPH_OPEN, kernel)
        closing = cv2.morphologyEx(opening, cv2.MORPH_CLOSE, kernel)
        
        ret, water_mask = cv2.threshold(closing, assigned_threshold_value_binarisation, assigned_value, cv2.THRESH_BINARY_INV)
        
        return water_mask
        
    def _canny_filter(self, minVal=100, maxVal=200):           
        canny_filter = cv2.Canny(self.water_mask, minVal, maxVal)
        return canny_filter        
        
    def _shoreline(self):
        self.fig = plt.figure()
        self.ax= self.fig.add_subplot(111)       
        #set axes limits
        image = self.ax.imshow(self.canny_filter, 'gray') 
        plt.savefig(self.output_dir + 'shoreline.png', dpi=300)
        return image
    
    def _shoreline_ref(self):
        [cols, rows] = self.canny_filter.shape
        self.driver = gdal.GetDriverByName("GTiff")
        self.outdata = self.driver.Create(self.output_dir_geol + self.name, rows, cols, 1, gdal.GDT_UInt16)
        ds = gdal.Open(self.image_path)
        self.outdata.SetGeoTransform(ds.GetGeoTransform()) ##sets same geotransform as input
        self.outdata.SetProjection(ds.GetProjection()) ##sets same projection as input
        self.outdata.GetRasterBand(1).WriteArray(self.canny_filter)
        self.outdata.GetRasterBand(1).SetNoDataValue(10000) ##if you want these values transparent
        self.outdata.FlushCache() ##saves to disk!!
        outdata = None
        band=None
        return outdata 

    
