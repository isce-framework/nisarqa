import argparse
import os
import warnings
from typing import Optional

from PIL import Image


def png2jpg(
    source_filepath: str,
    output_filepath: Optional[str] = None,
    max_size: Optional[tuple[float, float]] = None,
    optimize: bool = True,
    quality: float = 75,
) -> None:
    """
    Reduce the shape size and compress a PNG into a JPEG.

    If converting from an image with an alpha channel, the transparent
    pixels will be colored opaque white.

    Suggestion: Do not reduce the size of ROFF and GOFF browse images; the
    quiver arrows do not appear crisp after conversion to jpg.

    Parameters
    ----------
    source_filepath : str
        Filepath to the source image to be processed.
    output_filepath : str or None, optional
        Filepath (with ".jpg" extension) for saving the processed image.
        If filepath does not end with ".jpg", it will be updated to do so.
        If None, processed image will be saved to the same filepath
        as `source_filepath` but with an extension of ".jpg".
        Defaults to None.
    max_size : None or pair of float, optional
        Maximum pixel dimensions of the output image, in the format:
            (<max width>, <max height>)
        If None, then the image dimensions will not be altered.
        Defaults to None.
    optimize : bool, optional
        If True, indicates that the encoder should make an extra
        pass over the image in order to select optimal encoder settings.
        Defaults to True.
        See: https://pillow.readthedocs.io/en/stable/handbook/image-file-formats.html#jpeg-saving
    quality : float, optional
        The image quality, on a scale from 0 (worst) to 95 (best), or the
        string 'keep'. Values above 95 should be avoided;
        100 disables portions of the JPEG compression algorithm, and
        results in large files with hardly any gain in image quality.
        Defaults to 75.
        See: https://pillow.readthedocs.io/en/stable/handbook/image-file-formats.html#jpeg-saving
    """

    # Prepare output filename
    if output_filepath is not None:
        out_path, out_ext = os.path.splitext(output_filepath)
        if out_ext.lower() != ".jpg":
            out_file = os.path.join(out_path, ".jpg")
        else:
            out_file = output_filepath
    else:
        filepath_and_name, in_ext = os.path.splitext(source_filepath)
        if in_ext.lower() != ".png":
            warnings.warn(
                f"Input file has an extension of '{in_ext=}'."
                " Only PNG files have been tested for this function."
                " Undefined behavior might occur."
            )
        out_file = f"{filepath_and_name}.jpg"

    # Open the image
    img = Image.open(source_filepath)

    # Resize
    if max_size is not None:
        img.thumbnail(size=max_size, resample=Image.Resampling.BILINEAR)

    # Ensure that the transparent pixels appear white by removing the alpha channel.
    if img.mode == "RGBA":
        # color image
        bkgd = Image.new("RGB", (img.width, img.height), (255, 255, 255))
        bkgd.paste(img, mask=img.split()[3])

    elif img.mode == "L":
        # grayscale image
        img = img.convert("LA")
        bkgd = Image.new("L", (img.width, img.height), 255)
        bkgd.paste(img, mask=img.split()[1])
    else:
        raise Exception(
            "Only grayscale and RGBA input files currently supported: ",
            source_filepath,
        )

    bkgd.save(out_file, optimize=optimize, quality=quality)


if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        description=(
            "Resize and/or reformat images from PNG to JPEG."
            " Useful for compressing large images to small images."
        )
    )

    parser.add_argument(
        "--input",
        "-i",
        dest="source_filepath",
        type=str,
        help="Filepath to the source image to be processed.",
    )

    msg = """Filepath (with ".jpg" extension) for saving the processed image.
        If filepath does not end with ".jpg", it will be updated to do so.
        If None, processed image will be saved to the same filepath
        as `source_filepath` but with an extension of ".jpg"."""
    parser.add_argument(
        "--out-file",
        "--out",
        "-o",
        dest="output_filepath",
        type=str,
        default=None,
        help=msg,
    )

    msg = """Maximum pixel dimensions of the output image, in the order:
            <max width> <max height>
        If not provided, then the image dimensions will not be altered."""
    parser.add_argument(
        "--size",
        "--max_size",
        dest="max_size",
        type=int,
        nargs=2,
        default=None,
        help=msg,
    )

    msg = """If omitted, indicates that the encoder should make an extra
        pass over the image in order to select optimal encoder settings.
        Include this flag to skip that optimization.
        See: https://pillow.readthedocs.io/en/stable/handbook/image-file-formats.html#jpeg-saving"""
    parser.add_argument(
        "--do_not_optimize",
        dest="do_not_optimize",
        action="store_true",
        default=False,
        help=msg,
    )

    msg = """The image quality, on a scale from 0 (worst) to 95 (best), or the
        string keep. The default is 75. Values above 95 should be avoided;
        100 disables portions of the JPEG compression algorithm, and
        results in large files with hardly any gain in image quality.
        The value keep is only valid for JPEG files and will retain the
        original image quality level, subsampling, and qtables.
        Defaults to "keep".
        See: https://pillow.readthedocs.io/en/stable/handbook/image-file-formats.html#jpeg-saving"""
    parser.add_argument(
        "--quality", "-q", dest="quality", type=str, default="keep", help=msg
    )

    args = parser.parse_args()

    quality = args.quality
    if quality.isdecimal():
        quality = float(quality)
    elif quality != "keep":
        raise ValueError(
            "`--quality` argument must be either numeric or the string 'keep'."
        )

    input_file = args.filename

    png2jpg(
        source_filepath=args.source_filepath,
        output_image_dir=args.output_image_dir,
        output_extension=args.output_extension,
        output_filepath=args.output_filepath,
        max_size=args.max_size,
        do_not_optimize=not args.do_not_optimize,
        quality=quality,
    )
