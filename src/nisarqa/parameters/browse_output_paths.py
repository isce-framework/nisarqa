from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

import nisarqa

objects_to_skip = nisarqa.get_all(name=__name__)


@dataclass(frozen=True)
class BrowseOutputPaths:
    """
    Container for browse and KML output file paths and naming utilities.

    This class encapsulates the output directory and primary browse/KML
    filenames, providing convenient methods to generate related filenames
    (e.g., EPSG 4326 lat/lon variants, frequency/polarization-specific
    variants, or custom suffixes).

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
    >>> paths.primary_browse_path
    PosixPath('/output/qa/BROWSE.png')
    >>> paths.get_browse_filename(suffix="LATLON")
    'BROWSE_LATLON.png'
    >>> paths.get_browse_path(suffix="A_HH")
    PosixPath('/output/qa/BROWSE_A_HH.png')
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

    def get_browse_filename(self, suffix: str | None = None) -> str:
        """
        Return the browse PNG filename, optionally with a suffix.

        Parameters
        ----------
        suffix : str or None, optional
            If provided, this suffix will be appended to the stem before the
            extension. Example: "A_HH" produces "BROWSE_A_HH.png", "LATLON"
            produces "BROWSE_LATLON.png". If None, returns the primary filename.
            Defaults to None.

        Returns
        -------
        png_filename : str
            The browse PNG filename (no path).

        Examples
        --------
        >>> paths.get_browse_filename()
        'BROWSE.png'
        >>> paths.get_browse_filename(suffix="A_HH")
        'BROWSE_A_HH.png'
        >>> paths.get_browse_filename(suffix="LATLON")
        'BROWSE_LATLON.png'
        """
        if suffix is None:
            return self.browse_filename
        return f"{self.browse_stem}_{suffix}.png"

    def get_kml_filename(self, suffix: str | None = None) -> str:
        """
        Return the KML filename, optionally with a suffix.

        Parameters
        ----------
        suffix : str or None, optional
            If provided, this suffix will be appended to the stem before the
            extension. Example: "A_HH" produces "BROWSE_A_HH.kml", "LATLON"
            produces "BROWSE_LATLON.kml". If None, returns the primary filename.
            Defaults to None.

        Returns
        -------
        kml_filename : str
            The KML filename (no path).

        Examples
        --------
        >>> paths.get_kml_filename()
        'BROWSE.kml'
        >>> paths.get_kml_filename(suffix="A_HH")
        'BROWSE_A_HH.kml'
        >>> paths.get_kml_filename(suffix="LATLON")
        'BROWSE_LATLON.kml'
        """
        if suffix is None:
            return self.kml_filename
        return f"{self.kml_stem}_{suffix}.kml"

    def get_browse_path(self, suffix: str | None = None) -> Path:
        """
        Return the full path to the browse PNG, optionally with a suffix.

        Parameters
        ----------
        suffix : str or None, optional
            If provided, this suffix will be appended to the filename.
            If None, returns the path to the primary browse PNG.
            Defaults to None.

        Returns
        -------
        png_path : Path
            The full path to the browse PNG.

        Examples
        --------
        >>> paths.get_browse_path()
        PosixPath('/output/qa/BROWSE.png')
        >>> paths.get_browse_path(suffix="A_HH")
        PosixPath('/output/qa/BROWSE_A_HH.png')
        >>> paths.get_browse_path(suffix="LATLON")
        PosixPath('/output/qa/BROWSE_LATLON.png')
        """
        return self.output_dir / self.get_browse_filename(suffix=suffix)

    def get_kml_path(self, suffix: str | None = None) -> Path:
        """
        Return the full path to the KML file, optionally with a suffix.

        Parameters
        ----------
        suffix : str or None, optional
            If provided, this suffix will be appended to the filename.
            If None, returns the path to the primary KML file.
            Defaults to None.

        Returns
        -------
        kml_path : Path
            The full path to the KML file.

        Examples
        --------
        >>> paths.get_kml_path()
        PosixPath('/output/qa/BROWSE.kml')
        >>> paths.get_kml_path(suffix="A_HH")
        PosixPath('/output/qa/BROWSE_A_HH.kml')
        >>> paths.get_kml_path(suffix="LATLON")
        PosixPath('/output/qa/BROWSE_LATLON.kml')
        """
        return self.output_dir / self.get_kml_filename(suffix=suffix)

    @property
    def primary_browse_path(self) -> Path:
        """Return the full path to the primary browse PNG."""
        return self.get_browse_path()

    @property
    def primary_kml_path(self) -> Path:
        """Return the full path to the primary KML file."""
        return self.get_kml_path()


__all__ = nisarqa.get_all(__name__, objects_to_skip)
