#!/usr/bin/env python3
from __future__ import annotations

import matplotlib

# Switch backend to one that doesn't require DISPLAY to be set since we're
# just plotting to file anyway. (Some compute notes do not allow X connections)
# This needs to be set prior to opening any matplotlib objects.
matplotlib.use("Agg")
import argparse

import nisarqa


def parse_cli_args():
    """
    Parse the command line arguments

    Possible command line arguments:
        nisar_qa --version
        nisar_qa dumpconfig <product type>
        nisar_qa <product type>_qa <runconfig yaml file>

    Examples command line calls for RSLC product:
        nisar_qa --version
        nisar_qa dumpconfig rslc
        nisar_qa dumpconfig rslc --indent 8
        nisar_qa rslc_qa runconfig.yaml

    Returns
    -------
    args : argparse.Namespace
        The parsed command line arguments
    """

    # create the top-level parser
    msg = (
        "Quality Assurance processing to verify NISAR "
        "product files generated by ISCE3"
    )
    parser = argparse.ArgumentParser(
        description=msg,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    # --version
    parser.add_argument(
        "-V",
        "--version",
        action="version",
        version=nisarqa.__version__,
    )

    # create sub-parser
    sub_parsers = parser.add_subparsers(
        help="sub-command help", required=True, dest="command"
    )

    # create the parser for the `dumpconfig` sub-command
    msg = (
        "Output NISAR QA runconfig template "
        "with default values. "
        "For usage, see: `nisarqa dumpconfig -h`"
    )
    parser_dumpconfig = sub_parsers.add_parser("dumpconfig", help=msg)

    # Add the required positional argument for dumpconfig
    parser_dumpconfig.add_argument(
        "product_type",  # positional argument
        choices=nisarqa.LIST_OF_NISAR_PRODUCTS,
        help="Product type of the default runconfig template",
    )

    # Add an optional argument to set the indent spacing for dumpconfig
    parser_dumpconfig.add_argument(
        "-i",
        "--indent",
        default=4,
        type=int,
        help="Indent spacing for the output runconfig yaml",
    )

    # create a parser for each *_qa subcommand
    msg = (
        "Run QA for a NISAR %s with runconfig yaml. Usage: `nisarqa %s_qa"
        " <runconfig.yaml>`"
    )
    for prod in nisarqa.LIST_OF_NISAR_PRODUCTS:
        parser_qa = sub_parsers.add_parser(
            f"{prod}_qa", help=msg % (prod.upper(), prod.lower())
        )
        parser_qa.add_argument(
            f"runconfig_yaml",
            help=f"NISAR {prod.upper()} product runconfig yaml file",
        )

        # Add an optional flag to stream log messages to console
        parser_qa.add_argument(
            "-v",
            "--verbose",
            dest="verbose",
            action="store_true",  # sets default value to False
            help=(
                "Flag to stream log messages to console in addition to log"
                " file."
            ),
        )

    # parse args
    args = parser.parse_args()

    return args


def dumpconfig(product_type, indent=4):
    """
    Output a template runconfig file with default values to stdout.

    Parameters
    ----------
    product_type : str
        One of: 'rslc', 'gslc', 'gcov', 'rifg', 'runw', 'gunw', 'roff', 'goff'.
    indent : int, optional
        Number of spaces of an indent in the output runconfig yaml.
        Defaults to 4.
    """
    if product_type not in nisarqa.LIST_OF_NISAR_PRODUCTS:
        raise ValueError(
            f"`product_type` is {product_type}; must one of:"
            f" {nisarqa.LIST_OF_NISAR_PRODUCTS}"
        )

    if product_type == "rslc":
        nisarqa.RSLCRootParamGroup.dump_runconfig_template(indent=indent)
    elif product_type == "gslc":
        nisarqa.GSLCRootParamGroup.dump_runconfig_template(indent=indent)
    elif product_type == "gcov":
        nisarqa.GCOVRootParamGroup.dump_runconfig_template(indent=indent)
    elif product_type == "rifg":
        nisarqa.RIFGRootParamGroup.dump_runconfig_template(indent=indent)
    elif product_type == "runw":
        nisarqa.RUNWRootParamGroup.dump_runconfig_template(indent=indent)
    elif product_type == "gunw":
        nisarqa.GUNWRootParamGroup.dump_runconfig_template(indent=indent)
    elif product_type == "roff":
        nisarqa.ROFFRootParamGroup.dump_runconfig_template(indent=indent)
    elif product_type == "goff":
        nisarqa.GOFFRootParamGroup.dump_runconfig_template(indent=indent)
    else:
        raise NotImplementedError(
            f"{product_type} dumpconfig code not implemented yet."
        )


def run():
    # parse the args
    args = parse_cli_args()

    subcommand = args.command

    # Warning: Do not emit any log messages before dumpconfig!
    if subcommand == "dumpconfig":
        dumpconfig(product_type=args.product_type, indent=args.indent)
        return

    log = nisarqa.get_logger()

    # Generate the *RootParamGroup object from the runconfig
    product_type = subcommand.replace("_qa", "")
    try:
        root_params = nisarqa.RootParamGroup.from_runconfig_file(
            args.runconfig_yaml, product_type
        )
    except nisarqa.ExitEarly:
        # No workflows were requested. Exit early.
        log.info(
            "All `workflows` set to `False` in the runconfig, "
            "so no QA outputs will be generated. This is not an error."
        )
        return

    log.info(
        "Parsing of runconfig complete. Beginning QA for"
        f" {product_type.upper()} input product."
    )

    # Run QA SAS
    verbose = args.verbose

    with nisarqa.create_unique_subdirectory(
        parent_dir=root_params.prodpath.scratch_dir_parent,
        prefix=f"qa-{product_type}",
        delete=root_params.software_config.delete_scratch_files,
    ) as scratch_dir:

        nisarqa.set_global_scratch_dir(scratch_dir)

        if subcommand == "rslc_qa":
            nisarqa.rslc.verify_rslc(root_params=root_params, verbose=verbose)
        elif subcommand == "gslc_qa":
            nisarqa.gslc.verify_gslc(root_params=root_params, verbose=verbose)
        elif subcommand == "gcov_qa":
            nisarqa.gcov.verify_gcov(root_params=root_params, verbose=verbose)
        elif subcommand in ("rifg_qa", "runw_qa", "gunw_qa"):
            nisarqa.igram.verify_igram(root_params=root_params, verbose=verbose)
        elif subcommand in ("roff_qa", "goff_qa"):
            nisarqa.offsets.verify_offset(
                root_params=root_params, verbose=verbose
            )
        else:
            raise ValueError(f"Unknown subcommand: {subcommand}")


def main():
    log = nisarqa.get_logger()

    # Wrap all processing in a try/catch block to log exceptions.
    try:
        # Warning: Do not emit any log messages before calling run().
        # Otherwise, it will mess up the output from call to dumpconfig().
        run()
    except SystemExit:
        # When the CLI arguments are parsed inside of run(), in the case where
        # --help or --version is requested, argparse raises a SystemExit 0
        # error to exit the process. This needs to be caught here, or else the
        # nisarqa application will awkardly fail.
        pass
    except BaseException as e:
        # Use BaseException instead of Exception so that "special" exceptions
        # (e.g. KeyboardInterrupt) to be caught and logged before re-raising

        # Note: inside main(), the log output might have
        # been redirected to the log file instead of stderr.
        log.exception(e)

        try:
            summary = nisarqa.get_summary()
        except RuntimeError:
            # Summary CSV was never initialized. Cannot note the failure.
            pass
        else:
            summary.check_QA_completed_no_exceptions(result="FAIL")

        # Do not silently fail! Alert user via the console
        raise

    try:
        summary = nisarqa.get_summary()
    except RuntimeError:
        # Summary CSV was never initialized. Cannot note the success.
        pass
    else:
        summary.check_QA_completed_no_exceptions(result="PASS")


if __name__ == "__main__":
    main()
