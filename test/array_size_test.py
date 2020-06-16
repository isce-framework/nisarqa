from quality.GSLCFile import GSLCFile
from quality.SLCFile import SLCFile
from quality.SLCImage import SLCImage
from quality import errors_base, errors_derived

import h5py
import numpy

import os, os.path
import unittest

class SLCFile_test(unittest.TestCase):

    TEST_DIR = "test_data"

    def setUp(self):
        pass
        
    def test_slc_wrong_size(self):

        self.slc_file = SLCFile(os.path.join(self.TEST_DIR, "slc_arraysize.h5"), mode="r")

        self.slc_file.get_bands()
        self.slc_file.get_freq_pol()
        self.slc_file.check_freq_pol()
        self.slc_file.create_images()

        self.assertRaisesRegex(errors_base.FatalError, "Dataset LSAR B HH has.*(2385, 2640).*(2385, 2600).*", \
                               self.slc_file.check_slant_range)

    def test_gslc_wrong_size(self):

        self.gslc_file = GSLCFile(os.path.join(self.TEST_DIR, "gslc_arraysize.h5"), mode="r")

        self.gslc_file.get_bands()
        self.gslc_file.get_freq_pol()
        self.gslc_file.check_freq_pol()
        self.gslc_file.create_images()

        self.assertRaisesRegex(errors_base.FatalError, "Dataset LSAR B VV has.*(8713, 711).*(8700, 711).*", \
                               self.gslc_file.check_slant_range)

        
if __name__ == "__main__":
    unittest.main()

        
        
