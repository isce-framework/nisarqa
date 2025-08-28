# Overview

When writing the product spec Markdown files, the developer must be aware that the files will be displayed in both the online GitHub format, and the .docx format.

In theory, GitHub-Flavored Markdown should translate nicely to both the GitHub interface and also in the .docx when converted via `pandoc`. In practice, there are bugs.

Here are some guidelines for writing the Markdown files for the QA products specs, and workarounds for the issues.


# Section Heading Levels

The section heading levels must be considered holistically for all of the product spec Markdown documents.

In GitHub, each Markdown file is viewed independently, so section heading levels might seem to only be relative to the other headings within a single file.

But, when these Markdown files are compiled into the .docx, the section heading levels are parsed by `pandoc` and used to construct the sections within the .docx, which in-turn are used to build the hierarchy of the .docx's table of contents. Fortunately, `pandoc` seems to handle this parsing quite well.

There is an existing hierarchy established in the product specs Markdown files; pleaes be mindful of this hierarchy when making updates.


# HTML tags
HTML tags, tables, etc. seem to display nicely in the GitHub interface. However, in they do not seem to be recognized when `pandoc` converts to .docx.

Suggest avoiding them, until a solution is found.


# Tables
Instead of taking screenshots of tables in other applications, recreate the tables using GitHub-Flavored Markdown pipe tables, https://docs.github.com/en/get-started/writing-on-github/working-with-advanced-formatting/organizing-information-with-tables

Tips for getting tables to display nicely in both GitHub and in the .docx:

* Horizontal Alignment of the columns
    - You can align text to the left, right, or center of a column by including colons `:` to the left, right, or on both sides of the hyphens within the header row.
* Relative Column size:
    - Having non-uniform sized columns in both GitHub and the .docx is finnicky.
    - To do so, vary the number of hyphens in the header row. The more hyphens, the wider the column. (Minimum of three hyphens.)
    - For example, to have a medium-width column 1, a very wide column 2, and a narrow column 3, use this:

    > ```
    > | ------ | ----------------- | --- |
    > ```
* Merged cells:
    - Even though `pandoc` Markdown allows for merged cells via grid tables, GitHub-Flavored Markdown does not support merged cells. **Do not use them.**
        - In practice, this means that the HDF5 product spec tables are rather tricky to format and keep concise.

# Bulleted and Numbered Lists

Even though GitHub is able to successfully parse both bulleted lists and numbered lists and display nicely-formatted lists, unfortunately `pandoc` is only able to understand bulleted lists when converting to .docx. Rephrased, **`pandoc` cannot convert numbered lists nicely.**

To get around this, suggest using only bulleted lists. If you need a numbered sequence, the QA product specs currently uses a convention like this:

```
* **Step 1:** Read the raster
    - Note 1
    - Note 2

* **Step 2:** Process the raster
    - Processing Steps:
        - **Step 3i:** Reduce Size
        - **Step 3ii:** Remove alpha channel
            - Note 3
    - Note 4

* **Step 3:** Output to file
```

