import rawpy
import numpy as np
import tifffile
import argparse
import sys
import subprocess
import os


def convert_raw_to_tiff(input_file, output_file):
    try:
        with rawpy.imread(input_file) as raw:
            raw_data = raw.raw_image_visible.astype(np.float32)

            R = raw_data[0::2, 0::2]
            G1 = raw_data[::2, 1::2]
            G2 = raw_data[1::2, ::2]
            B = raw_data[1::2, 1::2]

            # Rec.709 weights
            weight_red = 0.2126
            weight_green = 0.7152
            weight_blue = 0.0722

            L = R * weight_red + (G1 + G2) / 2 * weight_green + B * weight_blue

            out_16bit = (L * 4).astype(np.uint16)

            tifffile.imwrite(output_file, out_16bit, photometric="minisblack")
            print(f"Conversion successful! Output written to: {output_file}")
            subprocess.run(
                [
                    "exiftool",
                    "-overwrite_original",
                    "-tagsfromfile",
                    input_file,
                    "-all:all",
                    output_file,
                ]
            )

    except Exception as e:
        print(f"Error during conversion: {e}")
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description="Convert RAW to black & white TIFF (single-pixel conversion)."
    )
    parser.add_argument("--input", required=True, help="Path to the input RAW file")
    parser.add_argument("--output", required=True, help="Path to the output TIFF file")
    args = parser.parse_args()

    if not os.path.isfile(args.input):
        print(f"Input file not found: {args.input}")
        sys.exit(1)

    convert_raw_to_tiff(args.input, args.output)


if __name__ == "__main__":
    main()
