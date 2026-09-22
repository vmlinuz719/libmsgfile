import argparse
import struct
from pathlib import Path
from os import SEEK_CUR

severities = {
    0: 'D',     # debug
    1: 'I',     # information
    2: 'W',     # warning
    3: 'E',     # error
    4: 'F',     # fatal
    5: 'U'      # user
}

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    
    parser.add_argument(
        "input_file",
        type = Path,
        help = "Input file containing compiled messages"
    )
    
    parser.add_argument(
        "index",
        type = int,
        help = "Index of the message to display, must be positive"
    )
    
    args = parser.parse_args()
    
    if args.index < 0:
        print(f"Error: message ID must be positive")
        exit()
    
    component = args.input_file.stem.split('.')[0].upper()
    
    with open(args.input_file.resolve(), "rb") as input_file:
        num_messages_b = input_file.read(4)
        num_messages = struct.unpack("<i", num_messages_b)[0]
        
        if args.index >= num_messages:
            print(f"Error: message ID must be less than {num_messages}")
            exit()
        
        input_file.seek(args.index * 8, SEEK_CUR)
        
        message_offset_b = input_file.read(4)
        message_offset = struct.unpack("<i", message_offset_b)[0]
        message_severity_b = input_file.read(4)
        message_severity_n = struct.unpack("<i", message_severity_b)[0]
        message_severity = severities[message_severity_n]
        
        input_file.seek(message_offset)
        
        message_b = bytearray()
        while True:
            byte = input_file.read(1)
            if not byte or byte == b'\x00':
                break
            message_b.extend(byte)
        message = message_b.decode('utf-8')
        
        print(f"{component}-{message_severity}-{args.index:04} " + message)