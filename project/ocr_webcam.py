import cv2
from google.cloud import vision
import requests

# Connect to client
client = vision.ImageAnnotatorClient()
server_url = "http://127.0.0.1:5000"

# Preprocess frame
def preprocess_frame(fr):
    gray = cv2.cvtColor(fr, cv2.COLOR_BGR2GRAY)
    thresh = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 31, 2)
    return thresh

video_capture = cv2.VideoCapture(0)
image_count = 0

while True:
    # Read frames
    ret, frame = video_capture.read()

    # Show and refresh video stream
    cv2.imshow('Video Feed', frame)

    # Check for a key press
    key = cv2.waitKey(1) & 0xFF

    # Capture frame
    if key == ord('c') or key == ord('v'):
        # Close windows from previous capture
        cv2.destroyWindow('Captured Image')
        cv2.destroyWindow('Preprocessed Image')
        
        # Encode frame to JPEG format used as parameter for vision.Image object
        if key == ord('c'):
            check_preproc = False
            image_obj = vision.Image(content=cv2.imencode('.jpg', frame)[1].tostring())
        else:
            # Use preprocessed frame settings instead
            check_preproc = True
            preprocessed = preprocess_frame(frame)
            image_obj = vision.Image(content=cv2.imencode('.jpg', preprocessed)[1].tostring())
        
        
        # Perform text recognition
        # OCR language support: https://cloud.google.com/vision/docs/languages
        response = client.text_detection(image=image_obj, image_context={"language_hints": ["en", "ja", "ch"]})
        texts = response.text_annotations
        
        # Extract and display all recognized text
        if texts:
            ocr_text = ""
            for text in texts[1:]:
                focused_text = text.description

                # Detect bounding box coordinates
                vertices = text.bounding_poly.vertices
                x1, y1 = vertices[0].x, vertices[0].y
                x2, y2 = vertices[2].x, vertices[2].y
                
                # Display OCR text and rectangle in frame
                cv2.putText(frame, focused_text, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                
                # Add OCR text to string
                ocr_text += focused_text + "\n"
            
            # Save as an image and Display it
            image_count += 1
            image_filename = f"img/captured_{image_count}.jpg"
            cv2.imwrite(image_filename, frame)
            print(f"Image saved as {image_filename}")
            cv2.imshow('Captured Image', frame)

            # Save preprocessed frame as an image and Display it
            if(check_preproc):
                preprocessed_filename = f"img/preprocessed_{image_count}.jpg"
                cv2.imwrite(preprocessed_filename, preprocessed)
                cv2.imshow('Preprocessed Image', preprocessed)
                
            #Send OCR text to web server
            response = requests.post(server_url, json={"ocr_text": ocr_text, "image_filename": image_filename})
                
        else:
            focused_text = "No text detected"
        
            
    # Exit program
    elif key == ord('q'):
        break

video_capture.release()
cv2.destroyAllWindows()

