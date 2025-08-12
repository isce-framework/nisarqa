# Overview

When adding new images to the repo, the developer must strike a balance between image file size, image pixel dimensions, and clarity. We want to keep images small in file size because we do not want to bloat the `nisarqa` repo, and once an image file is merged into the repo it will forever live in the git history. However, if an image is too small, blurry, or otherwise riddled with compression artifacts, it is not useful to the users.

Furthermore, this balance must occur in the context that the images will be visualized in both the online GitHub format, and the .docx product spec. Images that appear small and/or uniform size through the GitHub interface, often end up very large and or inconsistently-sized in the .docx.

# Tips

After much trial-and-error, here are a few rules-of-thumb and processes for getting images that reasonably strike the correct balance for use in the documentation. Use the tips as starting points to strike that balance. Update this list as better methods are found.

## Image File Size
- Aim for 15-40 KB per image.
In rare cases (e.g. browse images), it is okay to go over, but try to keep them under or around 100KB.
- [`nisarqa/docs/helpers/reformat_image.py`](reformat_image.py) is a helper script provided to either resize large PNGs to smaller JPEGs, and/or convert between file formats. Even without shrinking the pixel dimensions, using this script to convert from PNG to JPEG format with opimization enabled and a minor reduction in quality (e.g. 80) can dramatically reduce the file size with minimal impact to the clarity of the image. The script can be called from the command line, or imported into Python.

## Browse Images
- Nomimal NISAR QA browse images are much too large to use directly in the documentation; they are ~2048x2048 pixels, and 1-10 MB. **Do not use these.**
- Use `nisarqa` to generate new browse images; but use the `longest_side_max` parameter in the runconfig to the reduce the pixel dimensions of the generated browse image. (Every product type contains this parameter in its QA runconfig.)This method produces the most-accurate and crispest representation of browse images, but at a smaller size.
    - Do not use `.../reformat_image.py` to reduce the pixel dimensions of the browse images; it leads to undesirable interpolation.
    - Suggested Pixel Dimensions:
        - **set `longest_side_max` to 400**
    - Product-specific notes:
        - **ROFF and GOFF**: Because of the quiver plot arrows, the ROFF and GOFF browse PNGs do not convert to JPG nicely.
            - _Keep reducing `longest_side_max` until you get a small-enough PNG output, and use the PNG._
        - **RSLC, RIFG, RUNW**: These compress very nicely from PNG to JPG. 
            - _Use [`.../reformat_image.py`](reformat_image.py) to convert from PNG to JPG, but do not reduce the pixel dimensions._
        - **GSLC, GCOV**: These compress nicely from PNG to JPG, but doing so means that the transparent alpha channel is colored opaque white. 
            - _If the file size is small enough, suggest leaving them as PNG._
        - **GUNW**: These compress nicely from PNG to JPG, but doing so means that the transparent alpha channel is colored opaque white. Regardless, the GUNW PNG file size is quite large, so suggest to:
            - _Use [`.../reformat_image.py`](reformat_image.py) to convert from PNG to JPG, but do not reduce the pixel dimensions._
- If using [`.../reformat_image.py`](reformat_image.py) to convert from PNG to JPG, it worked well to have optimization enabled, set `quality` to 85, and have `max_size` be None.

## Converting PDF pages to images
- Step 1) Export the individual PDF pages to PNG
    - There are Python packages to do this
    - In a pinch, use Preview on Mac to `File > Export..` the first page of a PDF to PNG. If the page you want to use is not the first page, then reorder the pages in the thumbnail pane accordingly.
- Step 2) Use [`.../reformat_image.py`](reformat_image.py) to reduce the pixel dimensions, convert from PNG to JPG, enable optimization, and reduce the quality to ~80. (Pages from the PDF compress _really_ nicely.)
    - Suggested pixel dimensions:
        - Dual-plot and Single-plot PDF pages: max of 600 wide x 288 height, i.e. (600, 288)
        - Cover page: max of (2000, 1000)
        - Azimuth Spectra page: max of (600, 600)
        - Misc. Images: max of (700, 700)

