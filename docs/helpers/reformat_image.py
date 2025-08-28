import argparse
import os
from typing import Optional
from PIL import Image


def reformat_image(
    source_image_path: str,
    output_image_dir: Optional[str] = None,
    output_extension: str = "jpg",
    output_image_path: Optional[str] = None,
    max_size: Optional[tuple[float, float]] = None,
    do_not_optimize: bool = False,
    quality: float = "keep",
) -> None:
    """
    Reduce the shape size and compress a PNG into a JPG.

    If converting from an image with an alpha channel, the transparent
    pixels will be colored opaque white.

    Suggestion: Do not reduce the size of ROFF and GOFF browse images; the
    quiver arrows do not appear crisp after conversion to jpg.

    For supported file formats, see:
    https://pillow.readthedocs.io/en/stable/handbook/image-file-formats.html

    Parameters
    ----------
    source_image_path : str
        Filepath to the source image to be processed.
    output_image_dir : str or None, optional
        Filepath (with extension) for the directory to save the processed image.
        The format of the output file is determined from `output_format`.
        The filename will be the same at the input image's filename.
        If None, and if `output_image_path` is None, the processed image
        will be saved to the same path and filename as `source_image_path`,
        but using the extension of `output_format`.
        Defaults to None.
    output_extension : str, optional
        Format for the output processed image. Defaults to "jpg".
        Can be overridden by `output_image_path`.
    output_image_path : str or None, optional
        Filepath (with extension) for saving the processed image.
        The format of the output file is determined from the extension.
        If provided, this parameter will override both `output_image_dir`
        and `output_format`.
        If None, processed image will be saved per `source_image_path`.
        Defaults to None.
    max_size : None or pair of float, optional
        Maximum pixel dimensions of the output image, in the format:
            (<max width>, <max height>)
        If None, then the image dimensions will not be altered.
        Defaults to None.
    do_not_optimize : bool, optional
        If False, indicates that the encoder should make an extra
        pass over the image in order to select optimal encoder settings.
        If True, this optimization is skipped.
        Defaults to False.
        See: https://pillow.readthedocs.io/en/stable/handbook/image-file-formats.html#jpeg-saving
    quality : float or str, optional
        The image quality, on a scale from 0 (worst) to 95 (best), or the
        string keep. The default is 75. Values above 95 should be avoided;
        100 disables portions of the JPEG compression algorithm, and
        results in large files with hardly any gain in image quality.
        The value keep is only valid for JPEG files and will retain the
        original image quality level, subsampling, and qtables.
        Defaults to "keep".
        See: https://pillow.readthedocs.io/en/stable/handbook/image-file-formats.html#jpeg-saving
    """

    # Open the image
    img = Image.open(source_image_path)

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
            source_image_path,
        )

    # Prepare output filename
    out_file = ""
    if output_image_path is not None:
        out_file = output_image_path
    elif output_image_dir is not None:
        filename_with_extension = os.path.basename(source_image_path)
        filename, _ = os.path.splitext(filename_with_extension)
        out_file = os.path.join(
            output_image_dir, f"{filename}.{output_extension}"
        )
    else:
        filepath_and_name, _ = os.path.splitext(source_image_path)
        out_file = f"{filepath_and_name}.{output_extension}"

    optimize = not do_not_optimize

    bkgd.save(out_file, optimize=optimize, quality=quality)


if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        description="Resize and/or reformat images. Useful for compressing large images to small images."
    )
    parser.add_argument("filename", help="Path to the input image file")

    parser.add_argument(
        "--input",
        "-i",
        dest="source_image_path",
        type=str,
        help="Filepath to the source image to be processed.",
    )

    msg = """Filepath (with extension) for the directory to save the processed image.
        The filename will be the same at the input image's filename.
        The format of the output file is determined from `--ext`.
        If not provided, and if `--out-file` is not provided, the processed image
        will be saved to the same path and filename as `--input`,
        but using the extension of `--ext`."""
    parser.add_argument(
        "--out-dir",
        "-o",
        dest="output_image_dir",
        type=str,
        default=None,
        help=msg,
    )

    msg = """Format for the output processed image. Defaults to "jpg".
        Can be overridden by `--out-file`."""
    parser.add_argument(
        "--out-ext",
        "--oe",
        "--ext",
        dest="output_extension",
        type=str,
        default="jpg",
        help=msg,
    )

    msg = """Filepath (with extension) for saving the processed image.
        The format of the output file is determined from the extension.
        If provided, this parameter will override both `output_image_dir`
        and `output_format`.
        If not provided, processed image will be saved per `source_image_path`."""
    parser.add_argument(
        "--out-file", dest="output_image_path", type=str, default=None, help=msg
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

    reformat_image(
        source_image_path=args.source_image_path,
        output_image_dir=args.output_image_dir,
        output_extension=args.output_extension,
        output_image_path=args.output_image_path,
        max_size=args.max_size,
        do_not_optimize=args.do_not_optimize,
        quality=quality,
    )
