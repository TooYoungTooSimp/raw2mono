# raw2mono: RAW to Monochrome Conversion Scripts

This repository contains two Python scripts designed to convert RAW image files into monochrome (black & white) images. One script outputs a DNG file, while the other produces a TIFF file. Both scripts:

- Extract each color channel (R, G1, G2, B) from the Bayer pattern.
- Apply Rec.709 luminance coefficients to generate a single-channel (grayscale) image.
- Multiply the result by a small factor to utilize the 16-bit range effectively.
- Copy relevant metadata from the original RAW file using **exiftool**.

## Table of Contents

1. [Overview of Scripts](#overview-of-scripts)  
2. [Requirements](#requirements)  
3. [Installation](#installation)  
4. [Usage](#usage)  
   - [Converting to Monochrome DNG](#converting-to-monochrome-dng)  
   - [Converting to Monochrome TIFF](#converting-to-monochrome-tiff)  
5. [How It Works](#how-it-works)  
6. [License](#license)

---

## Overview of Scripts

### 1. `raw2mono_dng.py`
- **Description**: Converts RAW files to a single-channel (monochrome) DNG.
- **Key Steps**:
  1. Reads the RAW file using [`rawpy`](https://pypi.org/project/rawpy/).
  2. Extracts color channels (R, G1, G2, B).
  3. Applies Rec.709 luminance coefficients to get a grayscale image.
  4. Multiplies by 4 and converts to a 16-bit array.
  5. Uses [`pidng`](https://pypi.org/project/pidng/) to create a DNG container.
  6. Copies EXIF data from the original RAW using `exiftool`.

### 2. `raw2mono_tiff.py`
- **Description**: Converts RAW files to a single-channel (monochrome) TIFF.
- **Key Steps**:
  1. Reads the RAW file using [`rawpy`](https://pypi.org/project/rawpy/).
  2. Extracts color channels (R, G1, G2, B).
  3. Applies Rec.709 luminance coefficients to get a grayscale image.
  4. Multiplies by 4 and converts to a 16-bit array.
  5. Writes the result as a TIFF using [`tifffile`](https://pypi.org/project/tifffile/).
  6. Copies EXIF data from the original RAW using `exiftool`.

---

## Requirements

Make sure you have the following installed:

- **Python** 3.6+ (tested on Python **3.10**).
- **pip** for installing Python packages.
- [**rawpy**](https://pypi.org/project/rawpy/) (Python RAW image processing library).
- [**numpy**](https://pypi.org/project/numpy/).
- [**exiftool**](https://exiftool.org/) (external command-line tool for metadata).
  - Ensure `exiftool` is accessible in your system’s PATH.
- **pidng** (required only for the DNG script).
- **tifffile** (required only for the TIFF script).

You can install the Python dependencies via:

```bash
pip install rawpy numpy pidng tifffile
```

*Note: If you do not need to convert to DNG, you may skip installing `pidng`. If you do not need TIFF output, you can skip `tifffile`.*

---

## Installation

1. **Clone** this repository or **download** the two script files (`raw2mono_dng.py` and `raw2mono_tiff.py`).
2. **Install dependencies** as described above.
3. **Confirm `exiftool`** is installed and available in your PATH. For example:

   ```bash
   exiftool -ver
   ```

   This should display the installed version of exiftool.

---

## Usage

Both scripts use a straightforward command-line interface with `--input` and `--output` arguments.

### Converting to Monochrome DNG

```bash
python raw2mono_dng.py --input path/to/input.raw --output path/to/output.dng
```

**Parameters**:
- `--input`: The path to your source RAW file.
- `--output`: The path (and filename) for the resulting DNG file.

**Example**:

```bash
python raw2mono_dng.py --input IMG_0001.NEF --output IMG_0001_monochrome.dng
```

Once completed, the script will:
1. Read the RAW file (`IMG_0001.NEF`).
2. Convert it to a single-channel grayscale image using the Rec.709 coefficients.
3. Save it as `IMG_0001_monochrome.dng`.
4. Copy metadata from the original file via `exiftool`.

### Converting to Monochrome TIFF

```bash
python raw2mono_tiff.py --input path/to/input.raw --output path/to/output.tiff
```

**Parameters**:
- `--input`: The path to your source RAW file.
- `--output`: The path (and filename) for the resulting TIFF file.

**Example**:

```bash
python raw2mono_tiff.py --input IMG_0001.CR2 --output IMG_0001_monochrome.tiff
```

Once completed, the script will:
1. Read the RAW file (`IMG_0001.CR2`).
2. Convert it to a single-channel grayscale image using the Rec.709 coefficients.
3. Save it as `IMG_0001_monochrome.tiff`.
4. Copy metadata from the original file via `exiftool`.

---

## How It Works

1. **Reading RAW**:  
   - We use **rawpy** to decode the RAW file into a numpy array (`raw_data`).  
   - This array represents the sensor’s Bayer pattern data.

2. **Extracting Channels**:  
   - We slice the raw mosaic into the four color channels: R, G1, G2, and B.  
   - For example, `R = raw_data[0::2, 0::2]`, `B = raw_data[1::2, 1::2]`, etc.

3. **Grayscale Conversion**:  
   - We apply the Rec.709 luminance coefficients:  
     \[
     L = R \times 0.2126 + \frac{(G1 + G2)}{2} \times 0.7152 + B \times 0.0722
     \]
   - This produces a single-channel float array.

4. **16-Bit Scaling**:  
   - The float array is multiplied by 4 (arbitrary scaling to better use the 16-bit range).  
   - The result is converted to 16-bit integers (`np.uint16`).

5. **Writing to DNG or TIFF**:  
   - **DNG**: We use [**pidng**](https://pypi.org/project/pidng/) to embed the single-channel data in a DNG file structure.  
   - **TIFF**: We use [**tifffile**](https://pypi.org/project/tifffile/) to write out a single-channel grayscale TIFF (minisblack).

6. **Metadata Copy**:  
   - Finally, we use `exiftool` to copy all tags from the original RAW into the new DNG or TIFF. This preserves capture time, camera make/model, and other relevant EXIF data.
