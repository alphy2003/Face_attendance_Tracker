import os
import cv2
import face_recognition
import pickle

# Path to the dataset folder
dataset_dir = "dataset"
encodings = []
names = []

# Loop through all images in the dataset folder
for image_name in os.listdir(dataset_dir):
    # Process only image files
    if image_name.endswith(('.jpg', '.jpeg', '.png')):  
        try:
            # Extract user ID from the filename format: User.<ID>.<number>.jpg
            user_id = int(image_name.split('.')[1])

            # Load the image
            image_path = os.path.join(dataset_dir, image_name)
            image = cv2.imread(image_path)
            rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

            # Get face encodings
            face_encodings = face_recognition.face_encodings(rgb_image)

            # Save the encoding and user ID if the face is detected
            if len(face_encodings) > 0:
                encodings.append(face_encodings[0])
                names.append(user_id)

        except (IndexError, ValueError) as e:
            print(f"Skipping file {image_name} due to format error.")

# Save the encodings and names to a file
if encodings:
    model_data = {"encodings": encodings, "names": names}
    with open("trained_model.pkl", "wb") as model_file:
        pickle.dump(model_data, model_file)

    print("✅ Model trained successfully and saved as 'trained_model.pkl'")
else:
    print("❌ No valid face encodings found. Check your dataset images.")
