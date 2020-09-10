from quality.GUNWFile import GUNWFile
from quality.GUNWGridImage import GUNWGridImage
from quality import errors_base, errors_derived, logging_base, utility

import h5py
import numpy
from scipy import constants
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as pyplot
from matplotlib.backends.backend_pdf import PdfPages
from testfixtures import LogCapture

import os, os.path
import sys
import unittest
import xml.etree.ElementTree as ET

class NISARFile_test(unittest.TestCase):

    TEST_DIR = "test_data"
    XML_DIR = "xml"

    def setUp(self):
        self.gunw_xml_tree = ET.parse(os.path.join(self.XML_DIR, "nisar_L2_GUNW.xml"))
        self.lcapture = LogCapture()
        self.logger = logging_base.NISARLogger("junk.log")

    def tearDown(self):
        self.logger.close()
        self.lcapture.uninstall()
        
    def test_frequency(self):

        # Re-open file and calculate power vs. frequency

        self.gunw_file = GUNWFile(os.path.join(self.TEST_DIR, "gunw_connected.h5"), \
                                  self.logger, xml_tree=self.gunw_xml_tree, mode="r")
        fhdf = h5py.File(os.path.join(self.TEST_DIR, "connected_out.h5"), "w")
        fpdf = PdfPages(os.path.join(self.TEST_DIR, "connected_out.pdf"))
        
        self.gunw_file.get_bands()
        self.gunw_file.get_freq_pol()
        self.gunw_file.check_freq_pol("LSAR", [self.gunw_file.GRIDS], [self.gunw_file.FREQUENCIES_GRID], \
                                      ["Grids"])
        self.gunw_file.find_missing_datasets()
        self.gunw_file.create_images()
        self.gunw_file.check_images(fpdf, fhdf)
        self.gunw_file.close()

        fhdf.close()
        fpdf.close()

        # Calculate expected results

        nline = 512
        nsmp = 512
        ngroup = (nline//8) * (nsmp//4)

        values = list(range(1, 5)) + list(range(1, 5)) + list(range(5, 9)) + list(range(50, 90, 10))

        expect_nonzero_hh = 75.0
        expect_nonzero_vv = 50.0

        id_expect_contig = []
        size_expect_contig = []
        id_expect_noncontig = []
        size_expect_noncontig = []
        
        for v in values:
            
            if (v in range(1, 5)):
                if (v not in id_expect_contig):
                    size_expect_contig.append(ngroup)
                    id_expect_noncontig.append(v)
                    size_expect_noncontig.append(3*ngroup)
                else:
                    size_expect_contig.append(2*ngroup)
                id_expect_contig.append(v)
            elif (v in range(5, 9)):
                size_expect_contig.append(ngroup)
                id_expect_contig.append(v)
                size_expect_noncontig.append(ngroup)
                id_expect_noncontig.append(v)
            elif (v in range(50, 90, 10)):
                size_expect_contig.append(2*ngroup)
                id_expect_contig.append(v)
                size_expect_noncontig.append(2*ngroup)
                id_expect_noncontig.append(v)

        id_expect_contig = numpy.array(id_expect_contig)
        size_expect_contig = numpy.array(size_expect_contig).astype(numpy.uint32)
        id_expect_noncontig = numpy.array(id_expect_noncontig)
        size_expect_noncontig = numpy.array(size_expect_noncontig).astype(numpy.uint32)

        idx_sort = numpy.argsort(~size_expect_contig)
        id_expect_contig = id_expect_contig[idx_sort]
        size_expect_contig = 100.0*size_expect_contig[idx_sort]/(nline*nsmp)

        idx_sort = numpy.argsort(~size_expect_noncontig)
        id_expect_noncontig = id_expect_noncontig[idx_sort]
        size_expect_noncontig = 100.0*size_expect_noncontig[idx_sort]/(nline*nsmp)
                
        # Open hdf summary file and verify connectness results

        fhdf = h5py.File(os.path.join(self.TEST_DIR, "connected_out.h5"), "r")
        handle_hh = fhdf["gunw_connected/LSAR/ImageAttributes/Grid: (LSAR A HH)"]
        handle_vv = fhdf["gunw_connected/LSAR/ImageAttributes/Grid: (LSAR A VV)"]
        nonzero_hh = handle_hh["pcnt_nonzero_connected (connectedComponents)"]
        nonzero_vv = handle_vv["pcnt_nonzero_connected (connectedComponents)"]

        # Verify HH numbers
        
        id_found = handle_hh["region_value (connectedComponents_contiguous)"][...]
        size_found = handle_hh["region_size (connectedComponents_contiguous)"][...]

        self.assertTrue(nonzero_hh[...] == expect_nonzero_hh)
        self.assertTrue(nonzero_vv[...] == expect_nonzero_vv)

        self.assertTrue(len(id_expect_contig) == len(id_found))
        self.assertTrue(len(size_expect_contig) == len(size_found))
        self.assertTrue(numpy.all(id_expect_contig == id_found))
        self.assertTrue(numpy.all(size_expect_contig == size_found))

        id_found = handle_hh["region_value (connectedComponents_non_contiguous)"][...]
        size_found = handle_hh["region_size (connectedComponents_non_contiguous)"][...]

        self.assertTrue(len(id_expect_noncontig) == len(id_found))
        self.assertTrue(len(size_expect_noncontig) == len(size_found))
        self.assertTrue(numpy.all(id_expect_noncontig == id_found))
        self.assertTrue(numpy.all(size_expect_noncontig == size_found))
        
        # Verify VV numbers

        id_found = handle_vv["region_value (connectedComponents_contiguous)"]
        size_found = handle_vv["region_size (connectedComponents_contiguous)"]

        self.assertTrue(id_found[...] == 1)
        self.assertTrue(size_found[...] == 50.0)

        id_found = handle_vv["region_value (connectedComponents_non_contiguous)"]
        size_found = handle_vv["region_size (connectedComponents_non_contiguous)"]

        self.assertTrue(id_found[...] == 1)
        self.assertTrue(size_found[...] == 50.0)
        
        fhdf.close()
        
        
if __name__ == "__main__":
    unittest.main()

        
        
