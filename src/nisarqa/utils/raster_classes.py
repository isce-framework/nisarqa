from dataclasses import dataclass

import nisarqa

# List of objects from the import statements that
# should not be included when importing this module
objects_to_skip = nisarqa.get_all(name=__name__)


@dataclass
class GeoRaster(nisarqa.rslc.SARRaster):
    '''
    A Raster with attributes specific to Geocoded products.

    The attributes specified here are based on the needs of the QA code
    for generating and labeling plots, etc.
    
    Parameters
    ----------
    data : array_like
        Raster data to be stored.
    name : str
        Name for the dataset
    band : str
        name of the band for `data`, e.g. 'LSAR'
    freq : str
        name of the frequency for `data`, e.g. 'A' or 'B'
    pol : str
        name of the polarization for `data`, e.g. 'HH' or 'HV'
    x_spacing : float
        X spacing of pixels of input array
    x_start : float
        The starting X position of the input array
    x_stop : float
        The stopping X position of the input array
    y_spacing : float
        Y spacing of pixels of input array
    y_start : float
        The starting (near) y position of the input array
    y_stop : float
        The stopping (far) Y position of the input array

    Notes
    -----
    If data is NISAR HDF5 dataset, suggest initializing using
    the class method init_from_nisar_h5_product(..).
    '''

    # Attributes of the input array
    x_spacing: float
    x_start: float
    x_stop: float

    y_spacing: float
    y_start: float
    y_stop: float


    @property
    def y_axis_spacing(self):
        return self.y_spacing

    @property
    def x_axis_spacing(self):
        return self.x_spacing


    @classmethod
    def init_from_nisar_h5_product(cls,
                       h5_file, band, freq, pol):
        '''
        Initialize an GeoRaster object for the given 
        band-freq-pol image in the input NISAR Geocoded HDF5 file.

        NISAR product type must be one of: 'GSLC', 'GCOV', 'GUNW', 'GOFF'
        
        Parameters
        ----------
        h5_file : h5py.File
            File handle to a valid NISAR Geocoded product hdf5 file.
            Polarization images must be located in the h5 file in the path: 
            /science/<band>/<product name>/grids/frequency<freq>/<pol>
            or they will not be found. This is the file structure
            as determined from the NISAR Product Spec.
        band : str
            name of the band for `img`, e.g. 'LSAR'
        freq : str
            name of the frequency for `img`, e.g. 'A' or 'B'
        pol : str
            name of the polarization for `img`, e.g. 'HH' or 'HV'

        Raises
        ------
        DatasetNotFoundError
            If the file does not contain an image dataset for the given 
            band-freq-pol combination, a DatasetNotFoundError
            exception will be thrown.

        Notes
        -----
        The `name` attribute will be populated with a string
        of the format: <band>_<freq>_<pol>
        '''

        product = nisarqa.get_NISAR_product_type(h5_file)

        if product not in ('GSLC', 'GCOV', 'GUNW', 'GOFF'):
            # self.logger.log_message(logging_base.LogFilterError, 'Invalid file structure.')
            raise nisarqa.InvalidNISARProductError

        # Hardcoded paths to various groups in the NISAR RSLC h5 file.
        # These paths are determined by the .xml product specs
        grids_path = f'/science/{band}/{product}/grids'
        freq_path = f'{grids_path}/frequency{freq}'
        pol_path = f'{freq_path}/{pol}'

        if pol_path in h5_file:
            # self.logger.log_message(logging_base.LogFilterInfo, 
            #                         'Found image %s' % band_freq_pol_str)
            pass
        else:
            # self.logger.log_message(logging_base.LogFilterInfo, 
            #                         'Image %s not present' % band_freq_pol_str)
            raise nisarqa.DatasetNotFoundError

        # From the xml Product Spec, xCoordinateSpacing is the 
        # 'Nominal spacing in meters between consecutive pixels'
        x_spacing = h5_file[freq_path]['xCoordinateSpacing'][...]

        # X in meters (units are specified as meters in the product spec)
        x_start = float(h5_file[freq_path]['xCoordinates'][0])
        x_stop =  float(h5_file[freq_path]['xCoordinates'][-1])

        # From the xml Product Spec, yCoordinateSpacing is the 
        # 'Nominal spacing in meters between consecutive lines'
        y_spacing = h5_file[freq_path]['yCoordinateSpacing'][...]

        # Y in meters (units are specified as meters in the product spec)
        y_start = float(h5_file[freq_path]['yCoordinates'][0])
        y_stop = float(h5_file[freq_path]['yCoordinates'][-1])

        # Get dataset object
        try:
            # GSLC Product Spec says that NISAR GSLC files should be complex64.
            # If so, then testing for the dtype should not break anything.
            # (Other Geocoded products should also be directly readible
            # by h5py, too.)
            h5_file[pol_path][...].dtype

        except TypeError as e:
            # As of R3.3 the GSLC workflow recently gained the ability
            # to generate products in complex32 format as well as complex64 
            # with some bits masked out to improve compression.
            # If the input GSLC product has dtype complex32, then we'll need
            # to use ComplexFloat16Decoder.
            if (product == 'GSLC') \
                and (str(e) == "data type '<c4' not understood"):

                # The GSLC dataset is complex32. Handle accordingly.
                dataset = nisarqa.rslc.ComplexFloat16Decoder(h5_file[pol_path])
                print('(FAIL) PASS/FAIL Check: Product raster dtype conforms'
                      ' to Product Spec dtype of complex64.')
            else:
                # A TypeError that is not anticipated was raised. Re-raise it.
                raise e
        else:
             # Use h5py's standard reader
            dataset = h5_file[pol_path]

            if product == 'GSLC':
                print('(PASS) PASS/FAIL Check: Product raster dtype conforms'
                        ' to Product Spec dtype of complex64.')
            else:
                # TODO - for GCOV, GUNW, and GOFF, confirm that this
                # next print statement is, in fact, true.
                print('(PASS) PASS/FAIL Check: Product raster dtype conforms '
                      f'to {product} Product Spec dtype.')

        return cls(data=dataset,
                   name=f'{product.upper()}_{band}_{freq}_{pol}',
                   band=band,
                   freq=freq,
                   pol=pol,
                   x_spacing=x_spacing,
                   x_start=x_start,
                   x_stop=x_stop,
                   y_spacing=y_spacing,
                   y_start=y_start,
                   y_stop=y_stop)


__all__ = nisarqa.get_all(__name__, objects_to_skip)