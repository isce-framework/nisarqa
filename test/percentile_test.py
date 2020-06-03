from quality.GCOVFile import GCOVFile
from quality.GCOVImage import GCOVImage
from quality import errors_base, errors_derived, utility

import h5py
import numpy
from scipy import constants
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as pyplot
from matplotlib.backends.backend_pdf import PdfPages

import os, os.path
import sys
import unittest

class GCOVFile_test(unittest.TestCase):

    TEST_DIR = "test_data"

    def setUp(self):
        pass
        
    def test_percentile(self):

        # Set up parameters

        # Open for the first time and insert dummy data
        
        self.gcov_file = GCOVFile(os.path.join(self.TEST_DIR, "gcov_stats.h5"), mode="r+")

        # Get rid of NaNs and negative values to avoid throwing an error later
        
        for f in ("A", "B"):
            freq = self.gcov_file["/science/LSAR/GCOV/grids/frequency%s/" % f]
            for p in ("HHHH", "HVHV", "VHVH", "VVVV"):
                pol = freq[p][...]
                pol = numpy.where(~numpy.isnan(pol) & (pol >= 0.0), pol, 0.0)
                freq[p][...] = pol
            
        dset = self.gcov_file["/science/LSAR/GCOV/grids/frequencyA/HHHH"]
        xdata = dset[...]
        shape = dset.shape
        xline = numpy.arange(0, shape[1])
        for i in range(0, shape[0]):
            xdata[i, :] = xline[:]

        dset[...] = xdata
        self.gcov_file.close()

        expect_bscatter = (xline.size-1)/2.0
        expect_pcnt5 = xline[int(xline.size*0.05)]
        expect_pcnt95 = xline[int(xline.size*0.95)]
        
        # Re-open file and calculate power vs. frequency

        self.gcov_file = GCOVFile(os.path.join(self.TEST_DIR, "gcov_stats.h5"), mode="r")
        fhdf = h5py.File(os.path.join(self.TEST_DIR, "gcov_stats_out.h5"), "w")
        fpdf = PdfPages(os.path.join(self.TEST_DIR, "gcov_stats_out.pdf"))
        
        self.gcov_file.get_bands()
        self.gcov_file.get_freq_pol()
        self.gcov_file.check_freq_pol()
        self.gcov_file.create_images()
        self.gcov_file.check_nans()
        self.gcov_file.check_images(fpdf, fhdf)

        self.gcov_file.close()
        fhdf.close()
        fpdf.close()
        
        # Open hdf file and verify frequencies

        summary_file = h5py.File(os.path.join(self.TEST_DIR, "gcov_stats_out.h5"), "r")
        bscatter = summary_file["/gcov_stats/LSAR/ImageAttributes/LSAR A HHHH/MeanBackScatter"][...]
        pcnt5 = summary_file["/gcov_stats/LSAR/ImageAttributes/LSAR A HHHH/5PercentileBackScatter"][...]
        pcnt95 = summary_file["/gcov_stats/LSAR/ImageAttributes/LSAR A HHHH/95PercentileBackScatter"][...]
        summary_file.close()
        
        self.assertTrue(numpy.fabs(bscatter - expect_bscatter) <= 0.01)
        self.assertTrue(numpy.fabs(pcnt5 - expect_pcnt5) <= 0.01)
        self.assertTrue(numpy.fabs(pcnt95 - expect_pcnt95) <= 0.01)

        
if __name__ == "__main__":
    unittest.main()

        
        

