#!/usr/bin/env python3
# Switch backend to one that doesn't require DISPLAY to be set since we're
# just plotting to file anyway. (Some compute notes do not allow X connections)
# This needs to be set prior to opening any matplotlib objects.
import matplotlib

matplotlib.use("Agg")
import argparse

from ruamel.yaml import YAML

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
        description=msg, formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )

    # --version
    parser.add_argument(
        "-v",
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


def load_user_runconfig(runconfig_yaml):
    """
    Load a QA Runconfig yaml file into a dict format.

    Parameters
    ----------
    runconfig_yaml : str
        Filename (with path) to a QA runconfig yaml file.

    Returns
    -------
    user_rncfg : dict
        `runconfig_yaml` loaded into a dict format
    """
    # parse runconfig into a dict structure
    parser = YAML(typ="safe")
    with open(runconfig_yaml, "r") as f:
        user_rncfg = parser.load(f)
    return user_rncfg


def main():
    # parse the args
    args = parse_cli_args()

    subcommand = args.command

    if subcommand == "dumpconfig":
        dumpconfig(product_type=args.product_type, indent=args.indent)
        return

    # parse runconfig into a dict structure
    user_rncfg = load_user_runconfig(args.runconfig_yaml)

    if subcommand == "rslc_qa":
        nisarqa.rslc.verify_rslc(user_rncfg=user_rncfg)
    elif subcommand == "gslc_qa":
        nisarqa.gslc.verify_gslc(user_rncfg=user_rncfg)
    elif subcommand == "gcov_qa":
        nisarqa.gcov.verify_gcov(user_rncfg=user_rncfg)
    elif subcommand == "rifg_qa":
        nisarqa.igram.verify_rifg(user_rncfg=user_rncfg)
    elif subcommand == "runw_qa":
        nisarqa.igram.verify_runw(user_rncfg=user_rncfg)
    elif subcommand == "gunw_qa":
        nisarqa.igram.verify_gunw(user_rncfg=user_rncfg)
    elif subcommand == "roff_qa":
        nisarqa.offsets.verify_roff(user_rncfg=user_rncfg)
    elif subcommand == "goff_qa":
        nisarqa.offsets.verify_goff(user_rncfg=user_rncfg)
    else:
        raise ValueError(f"Unknown subcommand: {subcommand}")


if __name__ == "__main__":
    main()
