# Instructions to Update the Product Spec Markdown Files

## Update Markdown text to match new QA PRs

As new QA PRs are drafted, the best practice is for the product specs to be updated in those PRs to keep them in sync. When preparing to cut a QA releases, the developer should do a final pass updating the product specs in advance of cutting the release.

When updating the product specs, the author needs to be mindful that the output looks "nice" in both GitHub and in .docx output. To view correctly on the GitHub repository, the Markdown must be written in "GitHub-Flavored Markdown". When reformatting the Markdown files into .docx files via `pandoc`, not all formatting will translate correctly.

Guidance on how to correctly write and format the QA product spec Markdown files for viewing both GitHub and the .docx can be found here:
[Tips for Writing Product Spec Markdown](helpers/style_guide_for_writing_markdown_specs.md)


## Auto-Generate Updated QA HDF5 Product Specification tables

First, locate a sample QA HDF5 file with a representative internal file structure for that QA HDF5 file type. Tips:
* If updating the QA HDF5 product specs for e.g. all eight L1/L2 QA HDF5 products, locate a unique QA HDF5 file for each L1/L2 type.
* When selecting these files, the contents and size of the e.g. imagery Datasets do not matter; this script only looks at the internal structure, descriptions, attributes, etc. However, it is useful to consider if the chosen sample files should be for single-pol observations, dual-pol, quad-pol, multi-frequency, etc. 
* When selecting RSLC and GSLC QA HDF5 files, please chose samples with outputs from the AbsCal and PTA Caltools.

Use the [`nisarqa/docs/helpers/generate_stats_markdown.py`](generate_stats_markdown.py) script to auto-generate updated Markdown product specs using the input QA HDF5 file:

```
python path/to/generate_stats_markdown.py /path/to/QA_STATS.h5 /path/to/output/directory/
```

> [!IMPORTANT]
> For the output directory, please use the existing `nisarqa/docs/product_specs/` directory. This is where the current version are stored; the Python script internally uses the correct naming convention to replace the old versions, and this way the .docx files can be smoothly generated with the updated files.

The [`generate_stats_markdown.py`](generate_stats_markdown.py) script automatically adds header information into each output Markdown file, iterates through the input product to parse the structure, formats the tables, and saves it with the correct file name in the `product_specs` directory. It also handles a few known edge cases.

> [!IMPORTANT]
> **To make changes to the QA HDF5 product spec Markdown documents, please update this [`generate_stats_markdown.py`](generate_stats_markdown.py) script and re-run the script. _Do not edit the Markdown files directly._**


## Compress all new or updated image files
To keep the size of the git repo manageable, developers are requested to compress all images prior to submitting a pull request.

> [!IMPORTANT]
> Check out [Tips for Compressing Tips Page](helpers/image_compression_tips.md) for guidelines and tips to compress images for use in the QA product spec documentation. This guide includes a helper script to facilitate image compression.

After compressing images, remember to double-check that the images' relative paths in the Markdown files are all still correct and that the images appear nicely in both display venues.

## Update README

If you added any new Markdown files, or changed the names of existing ones, please:
* Update the [`nisarqa/docs/README.md`](../README.md) Quick Links section
* Update all other instances in the documentation where those old filenames appear
