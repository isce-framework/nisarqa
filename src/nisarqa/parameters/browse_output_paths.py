from __future__ import annotations

from dataclasses import dataclass, replace
from pathlib import Path

import nisarqa

objects_to_skip = nisarqa.get_all(name=__name__)


@dataclass(frozen=True)
class BrowseOutputPaths:
    """
    Container for browse and KML output file paths and naming utilities.

    This class encapsulates the output directory and primary browse/KML
    filenames, providing convenient methods to generate related filenames.

    To add a suffix to the filenames (e.g. "_HH"), use the `with_suffix()`
    function to generate a copy of this instance but with the suffix
    appended (see example below).

    Parameters
    ----------
    output_dir : path-like
        The directory where browse and KML files will be written.
        This directory must already exist.
        Input argument will be cast to Path during post init.
    browse_filename : str
        The basename of the primary browse image PNG file.
        Example: "BROWSE.png"
    kml_filename : str
        The basename of the primary browse image KML file.
        Example: "BROWSE.kml"

    Examples
    --------
    >>> paths = BrowseOutputPaths(
    ...     output_dir="/output/qa",
    ...     browse_filename="BROWSE.png",
    ...     kml_filename="BROWSE.kml"
    ... )
    >>> paths.browse_filename
    'BROWSE.png'
    >>> paths.get_png_path()
    PosixPath('/output/qa/BROWSE.png')
    >>> paths_pol = paths.with_suffix("_HH")
    >>> paths_pol.browse_filename
    'BROWSE_HH.png'
    >>> paths_pol.get_png_path()
    PosixPath('/output/qa/BROWSE_HH.png')
    """

    output_dir: Path
    browse_filename: str
    kml_filename: str

    def __post_init__(self):
        """Validate inputs."""
        # Convert output_dir to Path for internal use
        object.__setattr__(self, "output_dir", Path(self.output_dir))

        if not self.browse_filename.endswith(".png"):
            raise ValueError(
                f"browse_filename must end with '.png': {self.browse_filename}"
            )
        if not self.kml_filename.endswith(".kml"):
            raise ValueError(
                f"kml_filename must end with '.kml': {self.kml_filename}"
            )

    @property
    def browse_stem(self) -> str:
        """Return the browse filename without extension. Example: 'BROWSE'"""
        return Path(self.browse_filename).stem

    @property
    def kml_stem(self) -> str:
        """Return the KML filename without extension. Example: 'BROWSE'"""
        return Path(self.kml_filename).stem

    def with_suffix(self, suffix: str) -> BrowseOutputPaths:
        """
        Return a copy of this instance but with a suffix added to filenames.

        Parameters
        ----------
        suffix : str
            The suffix to append to the filename stems before the extensions.
            (See examples below.)

        Returns
        -------
        BrowseOutputPaths
            A new instance with updated browse_filename and kml_filename.

        Examples
        --------
        >>> paths = BrowseOutputPaths(
        ...     output_dir="/output/qa",
        ...     browse_filename="BROWSE.png",
        ...     kml_filename="BROWSE.kml"
        ... )
        >>> paths_with_suffix = paths.with_suffix("_A_HH")
        >>> paths_with_suffix.browse_filename
        'BROWSE_A_HH.png'
        >>> paths_with_suffix.kml_filename
        'BROWSE_A_HH.kml'
        """
        return replace(
            self,
            browse_filename=f"{self.browse_stem}{suffix}.png",
            kml_filename=f"{self.kml_stem}{suffix}.kml",
        )

    def get_png_filename(self) -> str:
        """
        Return the browse PNG filename.

        Returns
        -------
        png_filename : str
            The browse PNG filename (no path).

        Examples
        --------
        >>> paths.get_png_filename()
        'BROWSE.png'
        """
        return self.browse_filename

    def get_kml_filename(self) -> str:
        """
        Return the KML filename.

        Returns
        -------
        kml_filename : str
            The KML filename (no path).

        Examples
        --------
        >>> paths.get_kml_filename()
        'BROWSE.kml'
        """
        return self.kml_filename

    def get_png_path(self) -> Path:
        """
        Return the full path to the browse PNG.

        Returns
        -------
        png_path : Path
            The full path to the browse PNG.

        Examples
        --------
        >>> paths.get_png_path()
        PosixPath('/output/qa/BROWSE.png')
        """
        return self.output_dir / self.get_png_filename()

    def get_kml_path(self) -> Path:
        """
        Return the full path to the KML file.

        Returns
        -------
        kml_path : Path
            The full path to the KML file.

        Examples
        --------
        >>> paths.get_kml_path()
        PosixPath('/output/qa/BROWSE.kml')
        """
        return self.output_dir / self.get_kml_filename()


__all__ = nisarqa.get_all(__name__, objects_to_skip)
