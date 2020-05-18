from quality.SLCFile import SLCFile
from quality import errors_base, errors_derived

import h5py
import numpy

import os, os.path
import unittest

class SLCFile_test(unittest.TestCase):

    TEST_DIR = "test_data"

    def setUp(self):
        pass

    #def tearDown(self):
    #    self.slc_file.close()
    
    def test_start_end_time(self):

        self.slc_file = SLCFile(os.path.join(self.TEST_DIR, "identification1.h5"), "r")
        self.slc_file.get_bands()
        self.slc_file.get_freq_pol()
        self.slc_file.check_freq_pol()
        self.assertRaisesRegex(errors_base.FatalError, \
                               "Start Time b'2018-07-30T16:15:47' not less than End Time b'2018-07-30T16:14:39.382875'", \
                               self.slc_file.check_identification)

    def test_orbit(self):

        self.slc_file = SLCFile(os.path.join(self.TEST_DIR, "identification2.h5"), "r")
        self.slc_file.get_bands()
        self.slc_file.get_freq_pol()
        self.slc_file.check_freq_pol()
        self.assertRaisesRegex(errors_base.FatalError, "Invalid Orbit Number: *", \
                               self.slc_file.check_identification)
        
    def test_track(self):

        self.slc_file = SLCFile(os.path.join(self.TEST_DIR, "identification3.h5"), "r")
        self.slc_file.get_bands()
        self.slc_file.get_freq_pol()
        self.slc_file.check_freq_pol()
        self.assertRaisesRegex(errors_base.FatalError, "Invalid Track Number: *", \
                               self.slc_file.check_identification)
        
    def test_frame(self):

        self.slc_file = SLCFile(os.path.join(self.TEST_DIR, "identification4.h5"), "r")
        self.slc_file.get_bands()
        self.slc_file.get_freq_pol()
        self.slc_file.check_freq_pol()
        self.assertRaisesRegex(errors_base.FatalError, "Invalid Frame Number: *", \
                               self.slc_file.check_identification)
        
    def test_cycle(self):

        self.slc_file = SLCFile(os.path.join(self.TEST_DIR, "identification5.h5"), "r")
        self.slc_file.get_bands()
        self.slc_file.get_freq_pol()
        self.slc_file.check_freq_pol()
        self.assertRaisesRegex(errors_base.FatalError, "Invalid Cycle Number: *", \
                               self.slc_file.check_identification)
        
    def test_product_type(self):

        self.slc_file = SLCFile(os.path.join(self.TEST_DIR, "identification6.h5"), "r")
        self.slc_file.get_bands()
        self.slc_file.get_freq_pol()
        self.slc_file.check_freq_pol()
        self.assertRaisesRegex(errors_base.FatalError, "Invalid Product Type: *", \
                               self.slc_file.check_identification)
        
    def test_look_direction(self):

        self.slc_file = SLCFile(os.path.join(self.TEST_DIR, "identification7.h5"), "r")
        self.slc_file.get_bands()
        self.slc_file.get_freq_pol()
        self.slc_file.check_freq_pol()
        self.assertRaisesRegex(errors_base.FatalError, "Invalid Look Direction: *", \
                               self.slc_file.check_identification)
        
         
    def test_acquired_frequencies(self):

        self.slc_file = SLCFile(os.path.join(self.TEST_DIR, "identification8.h5"), "r")
        self.slc_file.get_bands()
        self.slc_file.get_freq_pol()
        self.slc_file.check_freq_pol()
        self.slc_file.check_identification()
        self.assertRaisesRegex(errors_base.FatalError, \
                               "acquiredCenterFrequency A=1243000000.0* not less than B=1233000000.0*", \
                               self.slc_file.check_frequencies)
        
    def test_processed_frequencies(self):

        self.slc_file = SLCFile(os.path.join(self.TEST_DIR, "identification9.h5"), "r")
        self.slc_file.get_bands()
        self.slc_file.get_freq_pol()
        self.slc_file.check_freq_pol()
        self.slc_file.check_identification()
        self.assertRaisesRegex(errors_base.FatalError, \
                               "processedCenterFrequency A=1243000000.0* not less than B=1233000000.0*", \
                               self.slc_file.check_frequencies)
        
    def test_orbit_track(self):

        self.slc_file = SLCFile(os.path.join(self.TEST_DIR, "identification2b.h5"), "r")
        self.slc_file.get_bands()
        self.slc_file.get_freq_pol()
        self.slc_file.check_freq_pol()
        self.assertRaisesRegex(errors_base.FatalError, \
                               "[Invalid Orbit*, Invalid Track*]", \
                               self.slc_file.check_identification)
        
         

    
        
if __name__ == "__main__":
    unittest.main()

        
        
