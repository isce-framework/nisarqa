from __future__ import annotations

import os
from collections.abc import Iterator, Mapping
from dataclasses import dataclass

import h5py
import numpy as np

import nisarqa

from .non_insar_product import NonInsarProduct

objects_to_skip = nisarqa.get_all(name=__name__)


@dataclass
class SLCProduct(NonInsarProduct):

    def get_pols(self, freq: str) -> tuple[str, ...]:
        pols = super().get_pols(freq)

        # Sanity checks
        # Check the "discovered" polarizations against the expected
        # `listOfPolarizations` dataset contents
        list_of_pols_ds = self.get_list_of_polarizations(freq=freq)
        if set(pols) != set(list_of_pols_ds):
            errmsg = (
                f"Frequency {freq} contains polarizations {pols}, but"
                f" `listOfPolarizations` says {list_of_pols_ds}"
                " should be available."
            )
            raise nisarqa.InvalidNISARProductError(errmsg)

        return pols

    def get_layers_for_browse(self) -> dict[str, list[str]]:
        """
        Get frequencies+polarization images to use for the SLC Browse Image.

        This function should be used in conjunction with `save_browse()`,
        which handles the final greyscale or color channel assignments.

        See `Notes` for details on possible NISAR modes and assigned channels
        for LSAR band.
        Prioritization order to select the freq/pol to use:
            For frequency: Freq A then Freq B.
            For polarization: 'HH', then 'VV', then first polarization found.

        SSAR is currently only minimally supported, so only a grayscale image
        will be created.

        Returns
        -------
        layers_for_browse : dict
            A dictionary containing the frequency+polarization combinations
            that will be used to generate the browse image. Its structure is:
            layers_for_browse['A']     : list of str, optional
                                            List of the Freq A polarization(s)
                                            required to create the browse image.
                                            A subset of:
                                            ['HH','HV','VV','RH','RV','LH','LV']
            layers_for_browse['B']     : list of str, optional
                                            List of the Freq B polarizations
                                            required to create the browse image.
                                            A subset of ['HH','VV']

        Notes
        -----
        Possible modes for L-Band, as of Feb 2023:
            Single Pol      SP HH:      20+5, 40+5, 77
            Single Pol      SP VV:      5, 40
            Dual Pol        DP HH/HV:   77, 40+5, 20+5
            Dual Pol        DP VV/VH:   5, 77, 20+5, 40+5
            Quasi Quad Pol  QQ:         20+20, 20+5, 40+5, 5+5
            Quad Pol        QP:         20+5, 40+5
            Quasi Dual Pol  QD HH/VV:   5+5
            Compact Pol     CP RH/RV:   20+20           # an experimental mode
        Single Pol (SP) Assignment:
            - Freq A CoPol
            else:
            - Freq B CoPol
        DP and QQ Assignment:
            All image layers should come from a single frequency. Freq A has
            priority over Freq B.
            Two example assignments:
            - Freq A: Red=HH, Green=HV, Blue=HH
            - Freq B: Red=VV, Green=VH, Blue=VV
        QP Assignment:
            - Freq A: Red=HH, Green=HV, Blue=VV
        QD Assignment:
            - Freq A: Red=HH, Blue=HH; Freq B: Green=VV
        CP Assignment:
            - Freq A: Grayscale of one pol image, with
                    Prioritization order: ['RH','RV','LH','LV']

        See Also
        --------
        save_browse :
            Assigns the layers from this function to greyscale or RGBA channels.
        """
        layers_for_browse = {}
        log = nisarqa.get_logger()

        # Get the frequency sub-band containing science mode data.
        freq = self.science_freq
        science_pols = self.get_pols(freq=freq)

        # SSAR is not fully supported by QA, so just make a simple grayscale
        if self.band == "S":
            # Prioritize Co-Pol
            if "HH" in science_pols:
                layers_for_browse[freq] = ["HH"]
            elif "VV" in science_pols:
                layers_for_browse[freq] = ["VV"]
            else:
                # Take the first available pol
                layers_for_browse[freq] = [science_pols[0]]

            return layers_for_browse

        # The input file contains LSAR data. Will need to make
        # grayscale/RGB channel assignments

        def _assign_layers_single_freq(freq: str) -> None:
            """
            Populate `layers_for_browse` for `freq` per pols in `science_pols`.

            This function assumes all images should come from the same
            frequency group, and modifies `layers_for_browse` accordingly.

            Do not use for quasi-dual.
            """
            assert freq in ("A", "B")

            n_pols = len(science_pols)

            if all(
                pol.startswith("L") or pol.startswith("R")
                for pol in science_pols
            ):
                # Compact Pol. This is not a planned mode for LSAR,
                # and there is no test data, so simply make a grayscale image.

                # Per the Prioritization Order, use first available polarization
                for pol in ["RH", "RV", "LH", "LV"]:
                    if pol in science_pols:
                        layers_for_browse[freq] = [pol]
                        break

            elif n_pols == 1:
                # single pol mode
                layers_for_browse[freq] = science_pols

            else:
                # likely Dual Pol, Quasi Quad, Quad Pol

                # HH has priority over VV
                if "HH" in science_pols and "HV" in science_pols:
                    layers_for_browse[freq] = ["HH", "HV"]
                    if "VV" in science_pols:
                        # likely quad pol
                        layers_for_browse[freq].append("VV")

                elif "VV" in science_pols and "VH" in science_pols:
                    layers_for_browse[freq] = ["VV", "VH"]

                else:
                    # Warn, but do not fail. Attempt to continue QA.
                    log.warning(
                        "Product contains an unexpected configuration of"
                        " Frequencies and Polarizations. Please verify the"
                        " input product is as intended."
                    )

                    # Take the first available pol and make greyscale image
                    for pol in ["HH", "VV", "HV", "VH"]:
                        if pol in science_pols:
                            layers_for_browse[freq] = [pol]
                            break
                    else:
                        raise ValueError(
                            f"Input product Frequency {freq} contains unexpected"
                            f" polarization images {science_pols}."
                        )

        # For the browse images, only use images from one frequency; the
        # exception is quasi-dual, where we use layers from both A and B.

        # Identify and handle the quasi-dual case
        b_pols = self.get_pols(freq="B") if "B" in self.freqs else []
        if (freq == "A" and science_pols == ["HH"]) and b_pols == ["VV"]:
            # Quasi Dual Pol: Freq A has HH, Freq B has VV, and there
            # are no additional image layers available
            layers_for_browse["A"] = ["HH"]
            layers_for_browse["B"] = ["VV"]
        elif (freq == "A" and science_pols == ["VV"]) and b_pols == ["HH"]:
            # Quasi Dual Pol: Freq A has VV, Freq B has HH, and there
            # are no additional image layers available
            layers_for_browse["A"] = ["VV"]
            layers_for_browse["B"] = ["HH"]
        else:
            # Assign layers using only images from the primary science freq
            _assign_layers_single_freq(freq=freq)

        # Sanity Check
        if ("A" not in layers_for_browse) and ("B" not in layers_for_browse):
            raise ValueError(
                "Current Mode (configuration) of the NISAR input file"
                " not supported for browse image."
            )

        return layers_for_browse

    @staticmethod
    def save_browse(
        pol_imgs: Mapping[str, np.ndarray], filepath: str | os.PathLike
    ) -> None:
        """
        Save images in `pol_imgs` to a RGB or Grayscale PNG with transparency.

        Dimensions of the output PNG (in pixels) will be the same as the
        dimensions of the input polarization image array(s). (No scaling will
        occur.) Non-finite values will be made transparent.
        Color Channels will be assigned per the following pseudocode:
            If pol_imgs.keys() contains only one image, then:
                grayscale = <that image>
            If pol_imgs.keys() is ['HH','HV','VV'], then:
                red = 'HH'
                green = 'HV'
                blue = 'VV'
            If pol_imgs.keys() is ['HH','HV'], then:
                red = 'HH'
                green = 'HV'
                blue = 'HH'
            If pol_imgs.keys() is ['HH','VV'], then:
                red = 'HH'
                green = 'VV'
                blue = 'HH'
            If pol_imgs.keys() is ['VV','VH'], then:
                red = 'VV'
                green = 'VH'
                blue = 'VV'
            Otherwise, one image in `pol_imgs` will be output as grayscale.

        Parameters
        ----------
        pol_imgs : dict of numpy.ndarray
            Dictionary of 2D array(s) that will be mapped to specific color
            channel(s) for the output browse PNG.
            If there are multiple image arrays, they must have identical shape.
            Format of dictionary:
                pol_imgs[<polarization>] : <2D numpy.ndarray image>, where
                    <polarization> must be a subset of: 'HH', 'HV', 'VV', 'VH',
                                                        'RH', 'RV', 'LV', 'LH',
            Example:
                pol_imgs['HH'] : <2D numpy.ndarray image>
                pol_imgs['VV'] : <2D numpy.ndarray image>
        filepath : path-like
            Full filepath for where to save the browse image PNG.

        Notes
        -----
        Provided image array(s) must previously be image-corrected. This
        function will take  image array(s) as-is and will not apply additional
        image correction processing to them. This function directly combines
        the image(s) into a single browse image.
        If there are multiple input images, they must be thoughtfully prepared
        and standardized relative to each other prior to use by this function.
        For example, trying to combine a Freq A 20 MHz image
        and a Freq B 5 MHz image into the same output browse image might not go
        well, unless the image arrays were properly prepared and standardized
        in advance.
        """
        # WLOG, get the shape of the image arrays
        # They should all be the same shape; the check for this is below.
        arbitrary_img = next(iter(pol_imgs.values()))
        img_2D_shape = np.shape(arbitrary_img)
        for img in pol_imgs.values():
            # Input validation check
            if np.shape(img) != img_2D_shape:
                raise ValueError(
                    "All image arrays in `pol_imgs` must have the same shape."
                )

        # Assign color channels
        set_of_pol_imgs = set(pol_imgs)

        if set_of_pol_imgs == {"HH", "HV", "VV"}:
            # Quad Pol
            red = pol_imgs["HH"]
            green = pol_imgs["HV"]
            blue = pol_imgs["VV"]
        elif set_of_pol_imgs == {"HH", "HV"}:
            # dual pol horizontal transmit, or quasi-quad
            red = pol_imgs["HH"]
            green = pol_imgs["HV"]
            blue = pol_imgs["HH"]
        elif set_of_pol_imgs == {"HH", "VV"}:
            # quasi-dual mode
            red = pol_imgs["HH"]
            green = pol_imgs["VV"]
            blue = pol_imgs["HH"]
        elif set_of_pol_imgs == {"VV", "VH"}:
            # dual-pol only, vertical transmit
            red = pol_imgs["VV"]
            green = pol_imgs["VH"]
            blue = pol_imgs["VV"]
        else:
            # If we get into this "else" statement, then
            # either there is only one image provided (e.g. single pol),
            # or the images provided are not one of the expected cases.
            # Either way, WLOG plot one of the image(s) in `pol_imgs`.
            gray_img = pol_imgs.popitem()[1]
            nisarqa.rslc.plot_to_grayscale_png(
                img_arr=gray_img, filepath=filepath
            )

            # This `else` is a catch-all clause. Return early, so that
            # we do not try to plot to RGB
            return

        nisarqa.rslc.plot_to_rgb_png(
            red=red, green=green, blue=blue, filepath=filepath
        )

    def metadata_geometry_luts(
        self,
    ) -> Iterator[nisarqa.MetadataLUT2D]:
        """
        Generator for all metadata LUTs in geometry calibration info Group.

        Yields
        ------
        ds : nisarqa.MetadataLUT2D
            The next MetadataLUT2D in this Group:
                `../metadata/calibrationInformation/geometry`
        """
        with h5py.File(self.filepath, "r") as f:
            grp_path = "/".join([self._calibration_metadata_path, "geometry"])
            grp = f[grp_path]
            for ds_arr in grp.values():
                if isinstance(ds_arr, h5py.Group):
                    raise TypeError(
                        f"unexpected HDF5 Group found in {grp_path}."
                        " Metadata Groups should only contain Datasets."
                    )
                ds_path = ds_arr.name

                n_dim = np.ndim(ds_arr)
                if n_dim in (0, 1):
                    # Scalar and 1D Datasets in this group are coordinate
                    # dimensions and georeferencing info -- not metadata LUTs.
                    # Skip.
                    pass
                elif n_dim != 2:
                    raise ValueError(
                        f"The geometry metadata group should only contain"
                        " scalar, 1D, or 2D Datasets."
                        f" Dataset contains {n_dim} dimensions: {ds_path}"
                    )
                else:
                    yield self._build_metadata_lut(f=f, ds_arr=ds_arr)


__all__ = nisarqa.get_all(__name__, objects_to_skip)
