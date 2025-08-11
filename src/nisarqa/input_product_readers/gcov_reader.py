from __future__ import annotations

import os
from collections.abc import Mapping
from dataclasses import dataclass

import h5py
import numpy as np

import nisarqa

from .non_insar_geo_product import NonInsarGeoProduct

objects_to_skip = nisarqa.get_all(name=__name__)


@dataclass
class GCOV(NonInsarGeoProduct):
    @property
    def product_type(self) -> str:
        return "GCOV"

    def get_pols(self, freq: str) -> tuple[str, ...]:
        pols = super().get_pols(freq)

        # Sanity checks
        # Check the "discovered" polarizations against the expected
        # `listOfCovarianceTermss` dataset contents
        list_of_pols_ds = self.get_list_of_covariance_terms(freq=freq)
        if set(pols) != set(list_of_pols_ds):
            errmsg = (
                f"Frequency {freq} contains terms {pols}, but"
                f" `listOfCovarianceTerms` says {list_of_pols_ds}"
                " should be available."
            )
            raise nisarqa.InvalidNISARProductError(errmsg)

        return pols

    def get_layers_for_browse(self) -> dict[str, list[str]]:
        """
        Assign polarizations to grayscale or RGBA channels for the Browse Image.

        Only on-diagonal terms will be used to create the browse image.
        See `Notes` for details on the possible NISAR modes and assigned
        channels for LSAR band.
        SSAR is currently only minimally supported, so only a grayscale image
        will be created. Prioritization order to select the freq/pol to use:
            For frequency: Freq A then Freq B.
            For polarization: 'HHHH', then 'VVVV', then first pol found.

        Returns
        -------
        layers_for_browse : dict
            A dictionary containing the frequency+polarization combinations
            that will be used to generate the browse image.
            For GCOV, either `layers_for_browse['A']` or
            `layers_for_browse['B']` will exist, but not both.
            Its structure is:
            layers_for_browse['A']  : list of str, optional
                                         List of the Freq A polarization(s)
                                         required to create the browse image.
                                         Warning: Only on-diag terms supported.
            layers_for_browse['B']  : list of str, optional
                                         List of the Freq B polarizations
                                         required to create the browse image.
                                         Warning: Only on-diag terms supported.

        See Also
        --------
        save_browse : Assigns color channels and generates the browse PNG.

        Notes
        -----
        Unlike RSLC products, the polarizations contained within a GCOV product
        do not map to the NISAR mode table. For GCOV, The user selects a subset
        of polarizations of the RSLC to process. With that subset, the GCOV
        SAS workflow verifies if it should symmetrize the cross-polarimetric
        channels (HV and VH) into a single cross-polarimetric channel (HV),
        and also verifies if it should generate the full covariance or only
        the diagonal terms.
        Usually polarimetric symmetrization is applied; symmetrization
        joins HV and VH into a single polarimetric channel HV.
        Layer selection for LSAR GCOV Browse:
        - Frequency A is used if available. Otherwise, Frequency B.
        - If only one polarization is available, or if the images are cross-pol,
        make one layer into grayscale. This function selects that layer.
        - Otherwise, generate an RGB color composition, per the algorithm
        described in `save_gcov_browse_img()`. This function will gather the
        largest subset of: {HHHH, VVVV, (HVHV or VHVH)}, in prep for that
        function.
        GCOV and RTC-S1 pixels are square on the ground, so the multilooking
        factor is the same in both directions, depending only in the expected
        output dimensions.
        """
        layers_for_browse = {}

        # Get the frequency sub-band containing science mode data.
        freq = self.science_freq
        science_pols = self.get_pols(freq=freq)

        # SSAR is not fully supported by QA, so just make a simple grayscale
        if self.band == "S":
            # Prioritize Co-Pol
            if "HHHH" in science_pols:
                layers_for_browse[freq] = ["HHHH"]
            elif "VVVV" in science_pols:
                layers_for_browse[freq] = ["VVVV"]
            else:
                # Take the first available on-diagonal term
                for pol in science_pols:
                    if pol[0:2] == pol[2:4]:
                        layers_for_browse[freq] = [pol]
                        break
                else:
                    # Take first available pol, even if it is an off-diag term
                    layers_for_browse[freq] = [science_pols[0]]

            return layers_for_browse

        # The input file contains LSAR data. Will need to make
        # grayscale/RGB channel assignments

        # Keep only the on-diagonal polarizations
        # (On-diag terms have the same first two letters as second two letters,
        # e.g. HVHV or VVVV.)
        science_pols = [p for p in science_pols if (p[0:2] == p[2:4])]
        n_pols = len(science_pols)

        # Sanity check: There should always be on-diag pols for GCOV
        if n_pols == 0:
            raise ValueError(
                "No on-diagonal polarizations found in input GCOV."
            )

        elif n_pols == 1:
            # Only one image; it will be grayscale
            layers_for_browse[freq] = science_pols

        elif all(p.startswith(("R", "L")) for p in science_pols):
            # Only compact pol(s) are available. Create grayscale.
            # Per the Prioritization Order, use first available polarization
            for pol in ("RHRH", "RVRV", "LHLH", "LVLV"):
                if pol in science_pols:
                    layers_for_browse[freq] = [pol]
                    break
            else:
                # Use first available pol
                layers_for_browse[freq] = [science_pols[0]]

            assert len(layers_for_browse[freq]) == 1

        else:
            # Only keep "HHHH", "HVHV", "VHVH", "VVVV".
            keep = [
                p
                for p in science_pols
                if (p in ("HHHH", "HVHV", "VHVH", "VVVV"))
            ]

            # Sanity Check
            assert len(keep) >= 1

            # If both cross-pol terms are available, only keep one
            if ("HVHV" in keep) and ("VHVH" in keep):
                if ("VVVV" in keep) and not ("HHHH" in keep):
                    # Only VVVV is in keep, and not HHHH. So, prioritize
                    # keeping VHVH with VVVV.
                    keep.remove("HVHV")
                else:
                    # prioritize keeping "HVHV"
                    keep.remove("VHVH")

            layers_for_browse[freq] = keep

        # Sanity Checks
        if ("A" not in layers_for_browse) and ("B" not in layers_for_browse):
            raise ValueError(
                "Input file must contain either Frequency A or Frequency B"
                " iamges."
            )

        if len(layers_for_browse[freq]) == 0:
            raise ValueError(
                f"The input file's Frequency {freq} group does not contain "
                "the expected polarization names."
            )

        return layers_for_browse

    @staticmethod
    def save_browse(
        pol_imgs: Mapping[str, np.ndarray], filepath: str | os.PathLike
    ) -> None:
        """
        Save the given polarization images to a RGB or Grayscale PNG.

        Dimensions of the output PNG (in pixels) will be the same as the
        dimensions of the input polarization image array(s). (No scaling will
        occur.) Non-finite values will be made transparent.
        Color Channels will be assigned per the following pseudocode:
            If pol_imgs.keys() contains only one image, then:
                grayscale = <that image>
            Else:
                Red: first available co-pol of the list [HHHH, VVVV]
                Green: first of the list [HVHV, VHVH, VVVV]
                if Green is VVVV:
                    Blue: HHHH
                else:
                    Blue: first co-pol of the list [VVVV, HHHH]

        Parameters
        ----------
        pol_imgs : dict of numpy.ndarray
            Dictionary of 2D array(s) that will be mapped to specific color
            channel(s) for the output browse PNG.
            If there are multiple image arrays, they must have identical shape.
            Format of dictionary:
                pol_imgs[<polarization>] : <2D numpy.ndarray image>, where
                    <polarization> is a subset of:
                                            'HHHH', 'HVHV', 'VVVV', 'VHVH',
                                            'RHRH', 'RVRV', 'LVLV', 'LHLH'
            Example:
                pol_imgs['HHHH'] : <2D numpy.ndarray image>
                pol_imgs['VVVV'] : <2D numpy.ndarray image>
        filepath : path-like
            Full filepath for where to save the browse image PNG.

        See Also
        --------
        select_layers_for_browse : Function to select the layers.

        Notes
        -----
        Provided image array(s) must previously be image-corrected. This
        function will take the image array(s) as-is and will not apply
        additional image correction processing to them. This function
        directly combines the image(s) into a single browse image.
        If there are multiple input images, they must be thoughtfully prepared
        and standardized relative to each other prior to use by this function.
        For example, trying to combine a Freq A 20 MHz image
        and a Freq B 5 MHz image into the same output browse image might not go
        well, unless the image arrays were properly prepared and standardized
        in advance.
        """
        # WLOG, get the shape of the image arrays
        # They should all be the same shape; the check for this is below.
        first_img = next(iter(pol_imgs.values()))
        img_2D_shape = np.shape(first_img)
        for img in pol_imgs.values():
            # Input validation check
            if np.shape(img) != img_2D_shape:
                raise ValueError(
                    "All image arrays in `pol_imgs` must have the same shape."
                )

        # Only on-diagonal terms are supported.
        if not set(pol_imgs.keys()).issubset(set(nisarqa.GCOV_DIAG_POLS)):
            raise ValueError(
                f"{pol_imgs.keys()=}, must be a subset of"
                f" {nisarqa.GCOV_DIAG_POLS}"
            )

        # Assign channels

        if len(pol_imgs) == 1:
            # Single pol. Make a grayscale image.
            nisarqa.products.rslc.plot_to_grayscale_png(
                img_arr=first_img, filepath=filepath
            )

            # Return early, so that we do not try to plot to RGB
            return

        # Initialize variables. Later, check to ensure they were all used.
        red = None
        blue = None
        green = None

        for pol in ["HHHH", "VVVV"]:
            if pol in pol_imgs:
                red = pol_imgs[pol]
                break

        # There should only be one cross-pol in the input
        if ("HVHV" in pol_imgs) and ("VHVH" in pol_imgs):
            raise ValueError(
                "`pol_imgs` should only contain one cross-pol image."
                f"It contains {pol_imgs.keys()}. Please update logic in "
                "`_select_layers_for_gcov_browse()`"
            )

        for pol in ["HVHV", "VHVH", "VVVV"]:
            if pol in pol_imgs:
                green = pol_imgs[pol]

                if pol == "VVVV":
                    # If we get here, this means two things:
                    #   1: no cross-pol images were available
                    #   2: only HHHH and VVVV are available
                    # So, final assignment should be R: HHHH, G: VVVV, B: HHHH
                    blue = pol_imgs["HHHH"]
                else:
                    for pol2 in ["VVVV", "HHHH"]:
                        if pol2 in pol_imgs:
                            blue = pol_imgs[pol2]
                            break
                break

        # Sanity Check, and catch-all logic to make a browse image
        if any(arr is None for arr in (red, green, blue)):
            # If we get here, then the images provided are not one of the
            # expected cases. WLOG plot one of the image(s) in `pol_imgs`.
            nisarqa.get_logger().warning(
                "The images provided are not one of the expected cases to form"
                " the GCOV browse image. Grayscale image will be created by"
                " default."
            )

            for gray_img in pol_imgs.values():
                nisarqa.products.rslc.plot_to_grayscale_png(
                    img_arr=gray_img, filepath=filepath
                )

        else:
            # Output the RGB Browse Image
            nisarqa.products.rslc.plot_to_rgb_png(
                red=red, green=green, blue=blue, filepath=filepath
            )

    def get_list_of_covariance_terms(self, freq: str) -> tuple[str, ...]:
        """
        Gets contents of ../frequency<freq>/listOfCovarianceTerms in input file.

        Returns
        -------
        list_of_cov : tuple of str
            The contents of `listOfCovarianceTerms` in the `.../frequency<freq>`
            group in the input file.  Example output: ("HHHH", "HVHV").

        Raises
        ------
        ValueError
            If `listOfCovarianceTerms` contains invalid options.
        KeyError
            If `listOfCovarianceTerms` is missing.
        """

        # `listOfCovarianceTerms` is always a child of the frequency group.
        freq_group = self.get_freq_path(freq=freq)

        with h5py.File(self.filepath) as f:
            # `listOfCovarianceTerms` should be in all frequency groups.
            # If not, let h5py handle raising an error message.
            list_of_cov = f[freq_group]["listOfCovarianceTerms"]
            nisarqa.verify_str_meets_isce3_conventions(ds=list_of_cov)

            if list_of_cov.shape == ():
                # dataset is scalar, not a list
                list_of_cov = [
                    nisarqa.byte_string_to_python_str(list_of_cov[()])
                ]
                nisarqa.get_logger().error(
                    "`listOfCovarianceTerms` dataset is a scalar string, should"
                    " be a list of strings."
                )
            else:
                list_of_cov = nisarqa.byte_string_to_python_str(list_of_cov[()])

            # Sanity check that the contents make sense
            # For GCOV, `get_possible_pols()` actually returns the
            # possible covariance terms, e.g. "HHHH", "HVHV".
            poss_pols = nisarqa.get_possible_pols(self.product_type.lower())

            if not set(list_of_cov).issubset(set(poss_pols)):
                raise ValueError(
                    "Input file's `listOfCovarianceTerms` dataset contains"
                    f" {list_of_cov}, but must be a subset of {poss_pols}."
                )

            return tuple(list_of_cov)


__all__ = nisarqa.get_all(__name__, objects_to_skip)
