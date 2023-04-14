#!/usr/bin/env python3
# Switch backend to one that doesn't require DISPLAY to be set since we're
# just plotting to file anyway. (Some compute notes do not allow X connections)
# This needs to be set prior to opening any matplotlib objects.
import matplotlib

matplotlib.use('Agg')
import argparse

import nisarqa
import pkg_resources


def parse_cli_args():
    '''
    Parse the command line arguments

    Possible command line arguments:
        nisar_qa --version
        nisar_qa dumpconfig <product type>
        nisar_qa <product type>_qa <runconfig yaml file>

    Examples command line calls for RSLC product:
        nisar_qa --version
        nisar_qa dumpconfig rslc
        nisar_qa rslc_qa runconfig.yaml
    
    Returns
    -------
    args : argparse.Namespace
        The parsed command line arguments
    '''

    list_of_products = ['rslc', 'gslc', 'gcov', 'rifg',
                        'runw', 'gunw', 'roff', 'goff']

    # create the top-level parser
    msg = 'Quality Assurance processing to verify NISAR ' \
          'product files generated by ISCE3'
    parser = argparse.ArgumentParser(
                    description=msg,
                    formatter_class=argparse.ArgumentDefaultsHelpFormatter
                    )

    # --version
    parser.add_argument(
            '-v',
            '--version',
            action='version',
            version=pkg_resources.require('nisarqa')[0].version)

    # create sub-parser
    sub_parsers = parser.add_subparsers(help='sub-command help',
                                        required=True,
                                        dest='command')

    # create the parser for the `dumpconfig` sub-command
    msg = 'Output NISAR QA runconfig template ' \
          'with default values. ' \
          'For usage, see: `nisarqa dumpconfig -h`'
    parser_dumpconfig = sub_parsers.add_parser('dumpconfig', help=msg)

    # Add the required positional argument for the dumpconfig
    parser_dumpconfig.add_argument(
            'product_type',  # positional argument
            choices=list_of_products,
            help='Product type of the default runconfig template')
    
    # create a parser for each *_qa subcommand
    msg = 'Run QA for a NISAR %s with runconfig yaml. Usage: `nisarqa %s_qa <runconfig.yaml>`'
    for prod in list_of_products:
        parser_qa = sub_parsers.add_parser(f'{prod}_qa', 
                help=msg % (prod.upper(), prod.lower()))
        parser_qa.add_argument(
                f'runconfig_yaml',
                help=f'NISAR {prod.upper()} product runconfig yaml file')

    # parse args
    args = parser.parse_args()

    return args


def dumpconfig(product_type):
    if product_type == 'rslc':
        nisarqa.RSLCRootParams.dump_runconfig_template()
    else:
        raise NotImplementedError(
            f'{product_type} dumpconfig code not implemented yet.')


def main():
    # parse the args
    args = parse_cli_args()

    subcommand = args.command

    if subcommand == 'dumpconfig':
        dumpconfig(args.product_type)
    elif subcommand == 'rslc_qa':
        nisarqa.rslc.verify_rslc(runconfig_file=args.runconfig_yaml)
    elif subcommand == 'gslc_qa':
        nisarqa.gslc.verify_gslc(runconfig_file=args.runconfig_yaml)
    elif subcommand == 'gcov_qa':
        nisarqa.gcov.verify_gcov(runconfig_file=args.runconfig_yaml)
    elif subcommand == 'rifg_qa':
        nisarqa.rifg.verify_rifg(runconfig_file=args.runconfig_yaml)
    elif subcommand == 'runw_qa':
        nisarqa.runw.verify_runw(runconfig_file=args.runconfig_yaml)
    elif subcommand == 'gunw_qa':
        nisarqa.gunw.verify_gunw(runconfig_file=args.runconfig_yaml)
    elif subcommand == 'roff_qa':
        nisarqa.roff.verify_roff(runconfig_file=args.runconfig_yaml)
    elif subcommand == 'goff_qa':
        nisarqa.goff.verify_goff(runconfig_file=args.runconfig_yaml)
    else:
        raise ValueError(f'Unknown subcommand: {subcommand}')


if __name__ == '__main__':
    main()
