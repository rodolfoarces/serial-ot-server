#!/usr/bin/env python3
"""Pymodbus datastore simulator Example.

An example of using simulator datastore with json interface.

Detailed description of the device definition can be found at:

    https://pymodbus.readthedocs.io/en/latest/source/library/simulator/config.html#device-entries

usage: serial-server-ot.py [-h] [-l {critical,error,warning,info,debug}] [-b BAUDRATE] [-i ID] [-o OUTPUT] [-P PARITY] [-S STOP_BITS] [-B BYTE_SIZE] -p PORT
                           [-F {rtu,ascii}]

pymodbus synchronous serial server

options:
  -h, --help            show this help message and exit
  -l {critical,error,warning,info,debug}, --log-level {critical,error,warning,info,debug}
                        set log level, default is info
  -b BAUDRATE, --baudrate BAUDRATE
                        set serial device baud rate
  -i ID, --id ID        set number of device_id, default is 0 (any)
  -o OUTPUT, --output OUTPUT
                        set output file name
  -P PARITY, --parity PARITY
                        set parity of serial device, default is N (none)
  -S STOP_BITS, --stop-bits STOP_BITS
                        set number of stop bits for serial device, default is 1
  -B BYTE_SIZE, --byte-size BYTE_SIZE
                        set number of bytesize for serial device, default is 8
  -p PORT, --port PORT  set port or serial device. default is /dev/ttyS0
  -F {rtu,ascii}, --framer {rtu,ascii}
                        set framer type, default is RTU
"""
import argparse
import asyncio
import logging
import sys

from pymodbus import ModbusDeviceIdentification, pymodbus_apply_logging_config
from pymodbus.datastore import ModbusServerContext, ModbusSimulatorContext
from pymodbus.server import StartAsyncSerialServer


logger = logging.getLogger("server-ot")

demo_config = {
    "setup": {
        "co size": 100,
        "di size": 150,
        "hr size": 200,
        "ir size": 250,
        "shared blocks": True,
        "type exception": False,
        "defaults": {
            "value": {
                "bits": 0x0708,
                "uint16": 1,
                "uint32": 45000,
                "float32": 127.4,
                "string": "X",
            },
            "action": {
                "bits": None,
                "uint16": None,
                "uint32": None,
                "float32": None,
                "string": None,
            },
        },
    },
    "invalid": [
        1,
        [6, 6],
    ],
    "write": [
        3,
        [7, 8],
        [16, 18],
        [21, 26],
        [31, 36],
    ],
    "bits": [
        [7, 9],
        {"addr": 2, "value": 0x81},
        {"addr": 3, "value": 17},
        {"addr": 4, "value": 17},
        {"addr": 5, "value": 17},
        {"addr": 10, "value": 0x81},
        {"addr": [11, 12], "value": 0x04342},
        {"addr": 13, "action": "reset"},
        {"addr": 14, "value": 15, "action": "reset"},
    ],
    "uint16": [
        {"addr": 16, "value": 3124},
        {"addr": [17, 18], "value": 5678},
        {"addr": [19, 20], "value": 14661, "action": "increment"},
    ],
    "uint32": [
        {"addr": [21, 22], "value": 3124},
        {"addr": [23, 26], "value": 5678},
        {"addr": [27, 30], "value": 345000, "action": "increment"},
    ],
    "float32": [
        {"addr": [31, 32], "value": 3124.17},
        {"addr": [33, 36], "value": 5678.19},
        {"addr": [37, 40], "value": 345000.18, "action": "increment"},
    ],
    "string": [
        {"addr": [41, 42], "value": "Str"},
        {"addr": [43, 44], "value": "Strx"},
    ],
    "repeat": [{"addr": [0, 45], "to": [46, 138]}],
}


def custom_action1(_inx, _cell):
    """Test action."""


def custom_action2(_inx, _cell):
    """Test action."""


demo_actions = {
    "custom1": custom_action1,
    "custom2": custom_action2,
}


def get_commandline(cmdline=None):
    """Read and check command line arguments."""
    parser = argparse.ArgumentParser(description="pymodbus synchronous serial server")
    parser.add_argument( "-l",  "--log-level", choices=["critical", "error", "warning", "info", "debug"], help="set log level, default is info", dest="log", default="info", type=str)
    parser.add_argument( "-b", "--baudrate", help="set serial device baud rate", default=9600, type=int )
    parser.add_argument( "-i", "--id", help="set number of device_id, default is 0 (any)", default=0, type=int)
    parser.add_argument( "-o", "--output", help="set output file name", default=None, type=str)
    parser.add_argument( "-P", "--parity", help="set parity of serial device, default is N (none)", default="N", type=str)
    parser.add_argument( "-S", "--stop-bits", help="set number of stop bits for serial device, default is 1", default=1, type=int)
    parser.add_argument( "-B", "--byte-size", help="set number of bytesize for serial device, default is 8", default=8, type=int)
    parser.add_argument( "-p", "--port", help="set port or serial device. default is /dev/ttyS0",default="/dev/ttyS0", type=str, required=True)
    parser.add_argument( "-F", "--framer", choices=["rtu", "ascii"], help="set framer type, default is RTU", default="rtu", type=str )
    args = parser.parse_args()

    try:
        if args.help is not None:
            parser.print_help()
            sys.exit(0)
    except AttributeError as ex:
        pass

    # Setup logging to file or console
    if args.output is not None:
        # create console handler with a higher log level
        fh = logging.FileHandler(args.output, mode='a', encoding='utf-8')
    else:
        # create console handler with a higher log level
        fh = logging.StreamHandler()
    
    # create formatter and set it for the handler depending on log level
    if args.log.upper() == "INFO":
        fh_formatter = logging.Formatter('%(message)s')
    else:
        fh_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # Add the formatter to fh
    fh.setFormatter(fh_formatter)
    fh.setLevel(args.log.upper())

    logger.addHandler(fh)
    #pymodbus_apply_logging_config(args.log.upper())
    logger.setLevel(args.log.upper())
    logger.debug("Command line arguments: %s", args)
    args = parser.parse_args(cmdline)
    return args


def setup_simulator(setup=None, actions=None, cmdline=None):
    """Run server setup."""
    if not setup:
        setup=demo_config
    if not actions:
        actions=demo_actions
    args = get_commandline(cmdline=cmdline)
    #pymodbus_apply_logging_config(args.log.upper())
    logger.setLevel(args.log.upper())

    logger.debug("Creating Modbus simulator context")
    context = ModbusSimulatorContext(setup, actions)
    args.context = ModbusServerContext(devices=context, single=True)
    args.identity = ModbusDeviceIdentification(
        info_name={
            "VendorName": "Pymodbus",
            "ProductCode": "PM",
            "VendorUrl": "https://github.com/pymodbus-dev/pymodbus/",
            "ProductName": "Pymodbus Server",
            "ModelName": "Pymodbus Server",
            "MajorMinorRevision": "test",
        }
    )
    return args


async def run_server_simulator(args):
    """Run server."""
    logger.info("### start server simulator")

    await StartAsyncSerialServer(
                    context=args.context,  # Data storage
                    identity=args.id,  # server identify
                    port=args.port,  # serial port
                    framer=args.framer,  # The framer strategy to use
                    stopbits=args.stop_bits,  # The number of stop bits to use
                    bytesize=args.byte_size,  # The bytesize of the serial messages
                    parity=args.parity,  # Which kind of parity to use
                    baudrate=args.baudrate,  # The baud rate to use for the serial device
                    
                )


async def main(cmdline=None):
    """Combine setup and run."""
    run_args = setup_simulator(cmdline=cmdline)
    await run_server_simulator(run_args)
    logger.info("### server simulator finished")

if __name__ == "__main__":
    asyncio.run(main(), debug=True)
