import argparse
import logging
import os
from typing import Any

from pymodbus import pymodbus_apply_logging_config


def get_commandline(server: bool = True, description: str | None = None, extras: Any = None, cmdline: str | None = None):
    """Read and check command line arguments."""
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument(
        "-l",
        "--log",
        choices=["critical", "error", "warning", "info", "debug"],
        help="set log level, default is info",
        dest="log",
        default="info",
        type=str,
    )
    parser.add_argument(
        "-b",
        "--baudrate",
        help="set serial device baud rate",
        default=9600,
        type=int,
    )
    parser.add_argument(
        "-i"
        "--id",
        help="set number of device_id, default is 0 (any)",
        default=0,
        type=int
    )
    parser.add_argument(
        "-o",
        "--output",
        help="set output file name",
        default=None,
        type=str
    )
    parser.add_argument(
        "-p",
        "--parity",
        help="set parity of serial device, default is N (none)",
        default="N",
        type=str
    )
    parser.add_argument(
        "-s",
        "--stopbits",
        help="set number of stop bits for serial device, default is 1",
        default=1,
        type=int
    )
    parser.add_argument(
        "-B",
        "--bytesize",
        help="set number of bytesize for serial device, default is 8",
        default=8,
        type=int
    )

    args = parser.parse_args()

    # Setup logging to file or console
    if args.output is not None:
        # create console handler with a higher log level
        fh = logging.FileHandler(args.output, mode='a', encoding='utf-8')
    else:
        # create console handler with a higher log level
        fh = logging.StreamHandler()
    
    # create formatter and set it for the handler depending on log level
    if args.log.upper() is "INFO":
        fh_formatter = logging.Formatter('%(message)s')
    else:
        fh_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # Add the formatter to fh
    fh.setFormatter(fh_formatter)
    fh.setLevel(args.log.upper())

    logger = logging.getLogger("pymodbus")
    pymodbus_apply_logging_config(args.log.upper())
    logger.addHandler(fh)
