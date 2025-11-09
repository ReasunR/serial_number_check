# QR Code Match Checking Application

A Python application that captures photos and validates if Data Matrix barcode serial numbers match OCR-detected text.

## Features

- **Live camera preview** - See what you're capturing in real-time
- **Manual capture** - Press SPACE when ready (full control)
- **Automatic processing** - Captures and analyzes in one workflow
- **OCR text extraction** - Uses EasyOCR to read text from images
- **Data Matrix detection** - Detects and decodes Data Matrix barcodes
- **Serial number validation** - Automatically matches serial numbers between barcode and text
- **Detailed results** - Clear terminal output with success/failure indication

## Requirements

- Python 3.12
- Camera/Webcam
- macOS (with Homebrew), Linux, or Windows

## Setup

### 1. Install libdmtx (macOS only)

```bash
brew install libdmtx
```

### 2. Create and activate virtual environment

```bash
python3.12 -m venv venv
source venv/bin/activate  # On macOS/Linux
# or
venv\Scripts\activate     # On Windows
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

**Note:** First run will download EasyOCR language models (~100MB).

## Usage

### Quick Start (One Command)

```bash
cd /Users/checkito950/PycharmProjects/qr_code_matching && \
source venv/bin/activate && \
export DYLD_LIBRARY_PATH=/opt/homebrew/lib:$DYLD_LIBRARY_PATH && \
python match_checking.py
```

### Step by Step

```bash
# 1. Navigate to project directory
cd /Users/checkito950/PycharmProjects/qr_code_matching

# 2. Activate virtual environment
source venv/bin/activate

# 3. Set library path (macOS only)
export DYLD_LIBRARY_PATH=/opt/homebrew/lib:$DYLD_LIBRARY_PATH

# 4. Run the application
python match_checking.py
```

### How to Use

1. **Run the application** - A camera preview window will open
2. **Position your camera** - Ensure both text and Data Matrix barcode are visible
3. **Press SPACE** - Capture the photo when ready
4. **Wait for processing** - The app automatically analyzes the image
5. **View results** - Check terminal output for match validation

### Controls

- **SPACE** - Capture photo
- **q** - Quit application

## How It Works

### Phase 1: Photo Capture
1. Opens camera with live preview window
2. Displays frame counter and resolution
3. Waits for SPACE keypress
4. Captures current frame
5. Saves to `input/capture_YYYYMMDD_HHMMSS.jpg`

### Phase 2: Automatic Processing
1. Loads captured image from disk
2. Performs OCR text detection (EasyOCR)
3. Detects and decodes Data Matrix barcode (pylibdmtx)
4. Extracts serial number from positions 7-13 of Data Matrix data
5. Validates if serial number appears in OCR text
6. Displays detailed results with ✓ (match) or ✗ (no match)

### Why Save-Then-Load?

The app saves the captured image to disk before processing to avoid library conflicts:
- **Problem:** PyTorch (EasyOCR) + OpenCV camera + GUI frameworks cause crashes on macOS
- **Solution:** Separate capture phase from processing phase via disk I/O
- **Benefit:** Stable operation, no crashes, ~0.01s overhead

## Output Examples

### Successful Match ✓

```
============================================================
VALIDATION RESULTS:
============================================================
✓ Both text and Data Matrix code detected!

Serial number extracted: 123456
OCR text: Product ABC 123456 Model

🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉
✓✓✓ SUCCESS: Serial number MATCHES the OCR text! ✓✓✓
🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉
```

### No Match ✗

```
============================================================
VALIDATION RESULTS:
============================================================
✓ Both text and Data Matrix code detected!

Serial number extracted: 123456
OCR text: Product ABC 789012 Model

❌ Serial number does NOT match the OCR text.
```

### Partial Detection ⚠️

```
============================================================
VALIDATION RESULTS:
============================================================
⚠️  Only partial detection:
  ✓ OCR text detected
  ❌ Data Matrix code NOT detected

Try capturing another photo with both elements visible.
```

## Validation Logic

The application checks:
1. Both OCR text and Data Matrix code are detected
2. Serial number is extracted from Data Matrix (characters at positions 7-13)
3. Serial number appears somewhere in the OCR-detected text
4. Returns success (✓) if match found, failure (✗) otherwise

## File Structure

```
qr_code_matching/
├── venv/                      # Virtual environment
├── input/                     # Captured images (auto-created)
│   ├── capture_20251109_143022.jpg
│   └── ...
├── match_checking.py          # ⭐ Main application
├── qr_code_converter.py       # QR code utilities
├── requirements.txt           # Python dependencies
├── README.md                  # This file
└── USAGE_GUIDE.md            # Quick reference guide
```

## Troubleshooting

### ImportError: Unable to find dmtx shared library (macOS)

```bash
brew install libdmtx
export DYLD_LIBRARY_PATH=/opt/homebrew/lib:$DYLD_LIBRARY_PATH
```

### Camera access denied (macOS)

**Error:** "OpenCV: camera access has been denied"

**Solution:**
1. Open **System Settings** → **Privacy & Security** → **Camera**
2. Enable **Terminal** (or iTerm/PyCharm - whichever you're using)
3. Restart the application

### Camera not opening

- Close other apps using the camera
- Ensure Terminal/PyCharm has camera permissions
- Try running from PyCharm directly instead of terminal

### EasyOCR initialization is slow

- Normal on first run (downloading models ~100MB)
- Subsequent runs are much faster
- Using GPU (`gpu=True`) speeds it up significantly if available

### Detection fails

**Tips for better results:**
- Ensure **good lighting** on both text and barcode
- Hold camera **steady** when pressing SPACE
- Get the right **distance** (not too close, not too far)
- Make sure both elements are **in focus** and **in frame**
- Try different **angles** if first attempt fails

### No Data Matrix detected

- Ensure the barcode is a **Data Matrix** (not QR Code)
- Move camera **closer** to the barcode
- Improve **lighting** on the barcode
- Check barcode is **not damaged** or obscured

## Tips for Best Results

1. **Good Lighting** - Ensure both text and barcode are well-lit, avoid glare
2. **Steady Camera** - Hold camera steady when pressing SPACE
3. **Clear View** - Make sure both elements are visible and in focus
4. **Right Distance** - Test different distances to find optimal capture range
5. **Multiple Attempts** - Don't hesitate to try again with different positioning

## Exit Codes

- `0` - Success (match found)
- `1` - Failure (no match or incomplete detection)

Can be used in shell scripts:
```bash
if python match_checking.py; then
    echo "Match confirmed!"
else
    echo "No match - try again"
fi
```

## Notes

- Captured images remain in `input/` folder for review
- You can manually review images to improve capture technique
- Camera permissions are only needed during capture phase
- First run downloads EasyOCR models automatically

## Dependencies

- **opencv-python** - Camera capture and image processing
- **easyocr** - OCR text detection
- **pylibdmtx** - Data Matrix barcode detection
- **torch/torchvision** - Required by EasyOCR
- **numpy/Pillow** - Image manipulation

See `requirements.txt` for specific versions.

## License

This project is for internal use.
