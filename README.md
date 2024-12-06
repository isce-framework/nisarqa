# QualityAssurance
Quality Assurance software for NISAR

For the upcoming [NISAR mission](https://nisar.jpl.nasa.gov/),
eight types of L1/L2 data products will be generated.
This Quality Assurance (QA) software is designed to look at the data products
produced one at a time. For each product, the QA code can:
- Verify the metadata matches the product spec
- Generate metrics, a PDF report, and a summary CSV describing the quality
of the product
- Run CalTools processes on RSLC products
- Produce a browse image PNG with sidecar KML file for that product

# Minimum PreRequisites:
See `environment.yaml` for required packages.

# Operating Instructions:

## Installation

Step 1) Install the conda package manager.

Step 2) Clone the `nisarqa` repo and `cd` into the top level directory.
```
git clone https://github.com/isce-framework/nisarqa.git
cd nisarqa
```

Step 3) Create a conda environment with the correct packages for QA.

By creating a new environment using the `environment.yaml` file, the required 
packages and their versions will all be resolved by conda from the conda-forge 
channel, and thus remain consistent with each other. (Mixing package managers 
has led to import errors during testing.) The `environment.yaml` defaults to 
naming the new conda environment `nisarqa`.
```
conda env create -f environment.yaml
conda activate nisarqa  # activate the new environment
```

Step 4) Install

For standard installation, run:
```
pip install --no-deps .
```

For develop mode, run:
```
pip install --no-deps -e .
```

To test installation, try:
```
nisarqa --version
nisarqa -h
nisarqa dumpconfig -h
```

> [!CAUTION]
> `--no-deps` is necessary for installation due to the `isce3` dependency.
> Otherwise, `isce3` would need to be removed from `pyproject.toml`, causing
> that dependency list to fall out of sync with `environment.yaml`'s list.

## Running the QA Code

Run the QA code from the command line using a runconfig.yaml file.

Because the QA code is uniquely written for each product type, each product
type has a unique subcommand.

See `nisarqa -h` and e.g. `nisarqa rslc_qa -h` for usage.

Example commands to process QA:
```
nisarqa rslc_qa <rslc_runconfig.yaml>
nisarqa gslc_qa <gslc_runconfig.yaml>
```

By default, QA outputs the majority of log messages to the log file only.
To additionally stream the log messages to the console, use the verbose flag.
Example:
```
nisarqa gslc_qa <gslc_runconfig.yaml> -v
nisarqa rslc_qa <rslc_runconfig.yaml> --verbose
```

Step 5) Set up `pre-commit` (Optional for users) (Required for contributors)

QA repo uses a `pre-commit` workflow to ensure consistent code style for
developers. Configuration options are found in the `pyproject.toml` and
`.pre-commit-config.yaml` files.

Install pre-commit and check if it was correctly installed:
```
conda install -c conda-forge pre-commit
pre-commit help
```

Install and set up the git hook scripts:
```
pre-commit install  # stdout: pre-commit installed at .git/hooks/pre-commit
```

Now `pre-commit` will run automatically on `git commit`.

Some useful commands:
```
pre-commit run --all-files  # run on all files (not just files in commit)
git commit --no-verify -m "message"  # skip pre-commit entirely
SKIP=flake8,black git commit -m "foo"  # temporarily disable flake8 and black
```

## Runconfig Template w/ default parameters
Because the QA code is uniquely written for each product type, each product
also has a unique runconfig yaml file template and default settings.

The runconfig is where a user specifies the filepath to the input NISAR product,
which workflows to run, what units to use for a given metric, and so forth.

To get a product's example runconfig file that has been populated with
the default parameters, use the `dumpconfig` subcommand.

See `nisarqa dumpconfig -h` for usage.

Example commands:
```
nisarqa dumpconfig rslc
nisarqa dumpconfig rslc --indent 2                # change the indent spacing
nisarqa dumpconfig rslc > my_rslc_runconfig.yaml  # save runconfig to a file
nisarqa dumpconfig gcov
```


## Expected Outputs

For each NISAR product, if all workflows are requested via the `workflows`
parameter in the runconfig, the QA code will generate six output files
and store them in the directory specified by `qa_output_dir` in the runconfig:

1) `BROWSE.png` - RGB browse image for the input NISAR product
2) `BROWSE.kml` - geolocation information for `BROWSE.png`
3) `REPORT.pdf` - graphical summary PDF containing histograms,
                  low-res images of the input datasets, etc.
4) `STATS.h5` - statistical summary HDF5 file containing computed quality
                metrics, the datasets used to generate the plots in 
                `REPORT.pdf`, the QA processing parameters, etc.
5) `SUMMARY.csv` - a high-level PASS/FAIL check summary
6) `LOG.txt` - textual listing of errors encountered during QA processing

These file names are hardcoded; they are not configurable via the
runconfig.


## Copyright
Copyright 2024, by the California Institute of Technology. ALL RIGHTS RESERVED.
United States Government Sponsorship acknowledged.

## Export Classification
This software may be subject to U.S. export control laws. By accepting
this software, the user agrees to comply with all applicable U.S. export
laws and regulations. User has the responsibility to obtain export licenses,
or other export authority as may be required before exporting such
information to foreign countries or providing access to foreign persons.

## License

This software is licensed under your choice of BSD-3-Clause or Apache-2.0
licenses. The exact terms of each license can be found in the accompanying
[LICENSE-BSD-3-Clause.txt] and [LICENSE-Apache-2.0.txt] files, respectively.

[LICENSE-BSD-3-Clause.txt]: LICENSE-BSD-3-Clause.txt
[LICENSE-Apache-2.0.txt]: LICENSE-Apache-2.0.txt

SPDX-License-Identifier: BSD-3-Clause OR Apache-2.0
