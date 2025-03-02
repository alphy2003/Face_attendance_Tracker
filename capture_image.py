import cv2
import os

# Create a directory for storing images if it doesn't exist
dataset_dir = "dataset"
if not os.path.exists(dataset_dir):
    os.makedirs(dataset_dir)

# Load the Haar Cascade Classifier for face detection
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")

# Get User ID input
user_id = input("Enter a unique User ID (e.g., 1): ")

# Initialize the webcam
cam = cv2.VideoCapture(0)
image_count = 0
max_images = 100  # Capture up to 100 images

while True:
    ret, frame = cam.read()
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, 1.3, 5)

    # Detect face and save images
    for (x, y, w, h) in faces:
        image_count += 1
        face_img = gray[y:y+h, x:x+w]
        cv2.imwrite(f"{dataset_dir}/User.{user_id}.{image_count}.jpg", face_img)
        cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)

        # Display the count on the frame
        cv2.putText(frame, f"Image Count: {image_count}", (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

    # Show the live feed
    cv2.imshow('Capturing Images - Press Q to Quit', frame)

    # Break after capturing 100 images or pressing 'q'
    if cv2.waitKey(1) & 0xFF == ord('q') or image_count >= max_images:
        break

# Cleanup
cam.release()
cv2.destroyAllWindows()
print(f"Images for User ID {user_id} saved successfully in the '{dataset_dir}' folder.")
