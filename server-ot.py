import argparse
import logging
import sys
#import pymodbus
from pymodbus.server import StartSerialServer
from pymodbus.datastore import (ModbusSparseDataBlock, ModbusSequentialDataBlock,
                               ModbusDeviceContext, ModbusServerContext)


logger = logging.getLogger("server-ot")

def create_datablock(block_type: str, size: int):
    """Create a Modbus data block based on the type."""
    if block_type == "sparse_inputs":
        block = ModbusSparseDataBlock({i: False for i in range(0, size)}) 
        return block
    elif block_type == "sequential_inputs":
        block = ModbusSequentialDataBlock(size, [False])
        return block
    else:
        raise ValueError(f"Unknown block type: {block_type}")

def run_sync_server(args) -> None:
    """Run synchronous server."""
    di_datablock = create_datablock("sequential_inputs", 10)
    co_datablock = create_datablock("sequential_inputs", 10)
    hr_datablock = create_datablock("sparse_inputs", 10)
    ir_datablock = create_datablock("sparse_inputs", 10)

    device_context = ModbusDeviceContext(
            di=di_datablock,
            co=co_datablock,
            hr=hr_datablock,
            ir=ir_datablock,
        )

    server_context = ModbusServerContext(
        {args.id: device_context}, single=False
    )
    try:
        logger.info(f"### start SYNC serial server, listening on {args.port}")
        StartSerialServer(
                    context=server_context,  # Data storage
                    identity=args.id,  # server identify
                    port=args.port,  # serial port
                    framer=args.framer,  # The framer strategy to use
                    stopbits=args.stop_bits,  # The number of stop bits to use
                    bytesize=args.byte_size,  # The bytesize of the serial messages
                    parity=args.parity,  # Which kind of parity to use
                    baudrate=args.baudrate,  # The baud rate to use for the serial device
                    # handle_local_echo=False,  # Handle local echo of the USB-to-RS485 adaptor
                    # ignore_missing_devices=True,  # ignore request to a missing device
                    # broadcast_enable=False,  # treat device_id 0 as broadcast address,
                )
    except KeyboardInterrupt:
        logger.info("### server shutdown requested by keyboard interrupt")
        sys.exit(0)
    except RuntimeError as ex:
        logger.error(f"### server shutdown due to runtime error: {ex}")
    except Exception as ex:
        logger.error(f"### server shutdown due to exception: {ex}")



def sync_helper() -> None:
    """Combine setup and run."""
    run_sync_server(args)
    # server.shutdown()

if __name__ == "__main__":
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

    if args.help is not None:
        parser.print_help()
        sys.exit(0)

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
    sync_helper()