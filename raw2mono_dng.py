import argparse
import os
import subprocess
import sys

import numpy as np
import rawpy


def convert_raw_to_dng(input_file, output_file):
    try:
        with rawpy.imread(input_file) as raw:
            raw_data = raw.raw_image_visible.astype(np.float32)

            R = raw_data[0::2, 0::2]
            G1 = raw_data[0::2, 1::2]
            G2 = raw_data[1::2, 0::2]
            B = raw_data[1::2, 1::2]

            weight_red = 0.2126
            weight_green = 0.7152
            weight_blue = 0.0722

            L = R * weight_red + ((G1 + G2) / 2) * weight_green + B * weight_blue

            out_16bit = (L * 4).astype(np.uint16)

            new_height, new_width = out_16bit.shape

            from pidng.core import RAW2DNG, DNGTags, Tag

            bpp = 16

            t = DNGTags()
            t.set(Tag.ImageWidth, new_width)
            t.set(Tag.ImageLength, new_height)
            t.set(Tag.TileWidth, new_width)
            t.set(Tag.TileLength, new_height)
            t.set(Tag.Orientation, 1)
            t.set(Tag.PhotometricInterpretation, 1)
            t.set(Tag.SamplesPerPixel, 1)
            t.set(Tag.BitsPerSample, bpp)

            t.set(Tag.BlackLevel, [0])
            t.set(Tag.WhiteLevel, [(1 << bpp) - 1])
            t.set(Tag.Make, "@xuming.studio")
            t.set(Tag.Model, "RAW2DNG Monochrome")
            t.set(Tag.DNGVersion, [1, 4, 0, 0])
            t.set(Tag.DNGBackwardVersion, [1, 2, 0, 0])

            r = RAW2DNG()
            r.options(t, path="", compress=False)
            base_filename = os.path.splitext(output_file)[0]
            r.convert(out_16bit, filename=output_file)
            print(
                f"Conversion to DNG successful! Output written to: {base_filename}.dng"
            )
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
        description="Convert RAW to grayscale DNG (single-pixel conversion) using pidng."
    )
    parser.add_argument("--input", required=True, help="Path to the input RAW file")
    parser.add_argument("--output", required=True, help="Path to the output DNG file")
    args = parser.parse_args()

    if not os.path.isfile(args.input):
        print(f"Input file not found: {args.input}")
        sys.exit(1)

    convert_raw_to_dng(args.input, args.output)


if __name__ == "__main__":
    main()
