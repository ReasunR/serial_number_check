"""
Match Checking Application
Combined two-step process:
1. Capture photo when user presses SPACE (no GUI to avoid conflicts)
2. Automatically process the captured photo for OCR and Data Matrix matching

Press SPACE to capture, 'q' to quit
"""
import cv2
import easyocr
import os
import sys
import time
from datetime import datetime
from pylibdmtx.pylibdmtx import decode


def wait_for_keypress():
    """
    Wait for user to press SPACE to capture or 'q' to quit
    Shows live camera feed info
    """
    print("\n" + "="*60)
    print("CAMERA CONTROLS:")
    print("="*60)
    print("  Press SPACE    → Capture photo")
    print("  Press 'q'      → Quit application")
    print("="*60)
    
    cap = cv2.VideoCapture(0)
    
    if not cap.isOpened():
        print("\n❌ Error: Could not open camera")
        print("Make sure no other application is using the camera.")
        return None, None
    
    print("\n✓ Camera opened successfully!")
    print("\n📹 Camera is ready... Press SPACE when ready to capture")
    
    # Let camera warm up
    for i in range(10):
        cap.read()
        time.sleep(0.05)
    
    frame_count = 0
    captured_frame = None
    
    # Keep reading frames until user presses SPACE or 'q'
    while True:
        ret, frame = cap.read()
        
        if not ret:
            print("\n❌ Error: Failed to read frame")
            break
        
        frame_count += 1
        
        # Show frame info every 30 frames (~1 second at 30fps)
        if frame_count % 30 == 0:
            print(f"   Frame {frame_count:04d} - Resolution: {frame.shape[1]}x{frame.shape[0]} - Waiting for SPACE...", end='\r')
        
        # Check for keypress (non-blocking)
        # We need to display frame briefly to capture keypresses
        cv2.imshow('Camera Preview - Press SPACE to capture, Q to quit', frame)
        key = cv2.waitKey(1) & 0xFF
        
        if key == ord(' '):  # Space key
            print(f"\n\n📸 SPACE pressed! Capturing frame {frame_count}...")
            captured_frame = frame.copy()
            break
        elif key == ord('q'):  # Q key
            print("\n\n❌ Quit requested by user")
            break
    
    # Clean up
    cap.release()
    cv2.destroyAllWindows()
    
    return captured_frame, frame_count


def capture_photo():
    """Capture photo with user control"""
    # Create input folder
    input_folder = "input"
    if not os.path.exists(input_folder):
        os.makedirs(input_folder)
        print(f"✓ Created folder: {input_folder}")
    
    print("\n" + "="*60)
    print("STEP 1: PHOTO CAPTURE")
    print("="*60)
    
    # Wait for user to press SPACE
    frame, frame_number = wait_for_keypress()
    
    if frame is None:
        print("\n❌ No photo captured")
        return None
    
    # Save image
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"capture_{timestamp}.jpg"
    filepath = os.path.join(input_folder, filename)
    cv2.imwrite(filepath, frame)
    
    print(f"\n{'='*60}")
    print(f"✓✓✓ PHOTO CAPTURED!")
    print(f"{'='*60}")
    print(f"Saved to: {filepath}")
    print(f"Image size: {frame.shape[1]}x{frame.shape[0]} pixels")
    print(f"{'='*60}")
    
    return filepath


def process_image(image_path):
    """Process image for OCR and Data Matrix detection"""
    
    print("\n" + "="*60)
    print("STEP 2: PHOTO ANALYSIS")
    print("="*60)
    print(f"Processing: {image_path}")
    print("="*60 + "\n")
    
    # Load image
    print("📷 Loading image from disk...")
    image = cv2.imread(image_path)
    
    if image is None:
        print(f"❌ Error: Could not load image: {image_path}")
        return False
    
    print(f"✓ Image loaded: {image.shape[1]}x{image.shape[0]} pixels\n")
    
    # Initialize EasyOCR
    print("🔤 Initializing EasyOCR (this may take a moment on first run)...")
    reader = easyocr.Reader(['en'], gpu=False)
    print("✓ EasyOCR initialized\n")
    
    # Variables to track detection
    ocr_detected = False
    dm_detected = False
    combined_text = ""
    dm_data = ""
    
    # Perform OCR
    print("-" * 60)
    print("OCR TEXT DETECTION:")
    print("-" * 60)
    try:
        results = reader.readtext(image)
        
        if results:
            print("✓ Text detected:")
            for (bbox, text, confidence) in results:
                print(f"  - {text} (confidence: {confidence:.2f})")
            combined_text = " ".join([text for (bbox, text, confidence) in results])
            ocr_detected = True
        else:
            print("❌ No text detected")
    except Exception as e:
        print(f"❌ OCR error: {e}")
    
    print()
    
    # Perform Data Matrix detection
    print("-" * 60)
    print("DATA MATRIX DETECTION:")
    print("-" * 60)
    try:
        decoded_objects = decode(image)
        
        if decoded_objects:
            print("✓ Data Matrix code(s) detected:")
            for obj in decoded_objects:
                dm_data = obj.data.decode('utf-8')
                print(f"  - {dm_data}")
                dm_detected = True
        else:
            print("❌ No Data Matrix code detected")
    except Exception as e:
        print(f"❌ Data Matrix detection error: {e}")
    
    print()
    
    # Validation
    print("=" * 60)
    print("VALIDATION RESULTS:")
    print("=" * 60)
    
    if ocr_detected and dm_detected:
        print("✓ Both text and Data Matrix code detected!")
        serial_number = dm_data[7:13]
        print(f"\nSerial number extracted: {serial_number}")
        print(f"OCR text: {combined_text}")
        
        if serial_number in combined_text:
            print("\n" + "🎉" * 20)
            print("✓✓✓ SUCCESS: Serial number MATCHES the OCR text! ✓✓✓")
            print("🎉" * 20)
            return True
        else:
            print("\n❌ Serial number does NOT match the OCR text.")
            return False
    elif not ocr_detected and not dm_detected:
        print("❌ Detection failed: No text or Data Matrix code found.")
        print("Try capturing another photo with better lighting/positioning.")
        return False
    else:
        print("⚠️  Only partial detection:")
        if ocr_detected:
            print("  ✓ OCR text detected")
            print("  ❌ Data Matrix code NOT detected")
        else:
            print("  ❌ OCR text NOT detected")
            print("  ✓ Data Matrix code detected")
        print("\nTry capturing another photo with both elements visible.")
        return False


def main():
    print("\n" + "="*60)
    print("QR CODE MATCH CHECKING APPLICATION")
    print("="*60)
    print("This application:")
    print("  1. Captures a photo when you press SPACE")
    print("  2. Analyzes it for OCR text and Data Matrix codes")
    print("  3. Validates if the serial number matches")
    print("="*60)
    
    try:
        # Step 1: Capture photo
        image_path = capture_photo()
        
        if image_path is None:
            print("\n❌ Application terminated - No photo captured")
            sys.exit(1)
        
        # Small delay before processing
        print("\n⏳ Starting analysis in 2 seconds...")
        time.sleep(2)
        
        # Step 2: Process photo
        success = process_image(image_path)
        
        # Final summary
        print("\n" + "="*60)
        if success:
            print("APPLICATION COMPLETE - MATCH FOUND! ✓✓✓")
        else:
            print("APPLICATION COMPLETE - No match or incomplete detection")
        print("="*60)
        print(f"\nCaptured image saved at: {image_path}")
        print("You can review the image or run the application again.")
        print("="*60 + "\n")
        
        sys.exit(0 if success else 1)
        
    except KeyboardInterrupt:
        print("\n\n❌ Application interrupted by user (Ctrl+C)")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

