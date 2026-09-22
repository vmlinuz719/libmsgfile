import argparse
import struct
from pathlib import Path

severities = {
    'D': 0,     # debug
    'I': 1,     # information
    'W': 2,     # warning
    'E': 3,     # error
    'F': 4,     # fatal
    'U': 5      # user
}

def compile_messages(input_fname: Path, output_fname: Path):
    with open(input_fname.resolve(), "r") as input_file:
        num_strings = sum(1 for line in input_file)
    
    with (
        open(input_fname.resolve(), "r") as input_file,
        open(output_fname.resolve(), "wb") as output_file
    ):
        output_file.write(struct.pack("<i", num_strings))
        
        strings_written = 0
        string_offset = (num_strings * 8) + 4
        
        for line in input_file:
            if len(line) >= 2 and line[1] == ':':
                if line[0].upper() in severities:
                    severity = severities[line[0].upper()]
                else:
                    print(
                        f"Warning: invalid severity {line[0]} "
                        f"in message {strings_written}, "
                        "defaulting to I"
                    )
                    severity = severities["I"]
                line_abridged = line[2:]
            else:
                severity = severities["I"]
                line_abridged = line
        
            message = (
                line_abridged.rstrip()
                .encode('utf-8')
                .decode('unicode_escape')
                .encode('utf-8')
                + b'\0'
            )
            
            # write message offset and severity
            output_file.seek((strings_written * 8) + 4)
            output_file.write(struct.pack("<i", string_offset))
            output_file.write(struct.pack("<i", severity))
            strings_written += 1
            
            # write message
            output_file.seek(string_offset)
            output_file.write(message)
            string_offset += len(message)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    
    parser.add_argument(
        "input_file",
        type = Path,
        help = "Input file containing message strings to compile"
    )
    
    parser.add_argument(
        "-o",
        "--output_file",
        type = Path,
        help = "Name under which to save the compiled message file"
    )
    
    args = parser.parse_args()
    
    input_fname: Path = args.input_file
    if args.output_file is not None:
        output_fname: Path = args.output_file
    else:
        output_fname: Path = args.input_file.with_suffix(".msg")
    
    compile_messages(input_fname, output_fname)