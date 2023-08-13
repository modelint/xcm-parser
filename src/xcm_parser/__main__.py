"""
__main__.py

Class Model Parser
"""

import logging
import logging.config
import sys
import argparse
from pathlib import Path
from xcm_parser import version
from xcm_parser.class_model_parser import ClassModelParser

_logpath = Path("xcm_parser.log")

def get_logger():
    """Initiate the logger"""
    log_conf_path = Path(__file__).parent / 'log.conf'  # Logging configuration is in this file
    logging.config.fileConfig(fname=log_conf_path, disable_existing_loggers=False)
    return logging.getLogger(__name__)  # Create a logger for this module

# Configure the expected parameters and actions for the argparse module
def parse(cl_input):
    """
    The command line interface is for diagnostic purposes

    :param cl_input:
    :return:
    """
    parser = argparse.ArgumentParser(description='Class model parser')
    parser.add_argument('cmfile', nargs='?', action='store',
                        help='Class model file name with .xcm extension')
    parser.add_argument('-D', '--debug', action='store_true',
                        help='Debug mode'),
    parser.add_argument('-V', '--version', action='store_true',
                        help='Print the current version of parser')
    return parser.parse_args(cl_input)


def main():
    # Start logging
    logger = get_logger()
    logger.info(f'Class model parser version: {version}')

    # Parse the command line args
    args = parse(sys.argv[1:])

    if args.version:
        # Just print the version and quit
        print(f'Class model parser version: {version}')
        sys.exit(0)

    if args.cmfile:
        fpath = Path(args.cmfile)
        d = args.debug
        result = ClassModelParser.parse_file(file_input=fpath, debug=d)

    logger.info("No problemo")  # We didn't die on an exception, basically
    print("\nNo problemo")


if __name__ == "__main__":
    main()
