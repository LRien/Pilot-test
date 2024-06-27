import os
import cv2 as cv
import numpy as np
from datetime import datetime
import sqlite3
import sys

# Function to get the list of people
def get_people_list(directory):
    return [person for person in os.listdir(directory) if os.path.isdir(os.path.join(directory, person))]

# Directory containing face images
DIR = r'C:\Users\Leon\Desktop\CASESTUDY\Faces'

# Load Haar cascades for face and eye detection
haar_face_cascade = cv.CascadeClassifier('haar_face.xml')
haar_eye_cascade = cv.CascadeClassifier(cv.data.haarcascades + 'haarcascade_eye.xml')

# Check if the Haar cascades were loaded correctly
if haar_face_cascade.empty():
    raise IOError("Failed to load haar_face.xml")
if haar_eye_cascade.empty():
    raise IOError("Failed to load haascascades/haarcascade_eye.xml")

# Get the list of people from the images directory
people = get_people_list(DIR)
print("People found:", people)

features = []
labels = []

# Function to create training data
def create_train():
    for person in people:
        path = os.path.join(DIR, person)
        label = people.index(person)

        for img in os.listdir(path):
            img_path = os.path.join(path, img)

            img_array = cv.imread(img_path)
            if img_array is None:
                print(f"Failed to load image: {img_path}")
                continue

            gray = cv.cvtColor(img_array, cv.COLOR_BGR2GRAY)
            
            # Apply histogram equalization
            gray = cv.equalizeHist(gray)

            face_rect = haar_face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=4)

            for (x, y, w, h) in face_rect:
                faces_roi = gray[y:y+h, x:x+w]
                features.append(faces_roi)
                labels.append(label)

create_train()
print('Training Done -----------------------------')

features = np.array(features, dtype='object')
labels = np.array(labels)

# Create the LBPH face recognizer
face_recognizer = cv.face.LBPHFaceRecognizer_create()

# Train the recognizer on the feature and label arrays
try:
    face_recognizer.train(features, labels)
except cv.error as e:
    print(f"Error during training: {e}")

# Save the trained recognizer and people list
try:
    face_recognizer.save('face_trained.yml')
    np.save('features.npy', features)
    np.save('labels.npy', labels)
    np.save('people.npy', np.array(people))  # Save the people list
    print("Training data saved successfully.")
except Exception as e:
    print(f"Error saving training data: {e}")

# Load the people list
people = np.load('people.npy', allow_pickle=True).tolist()
print("People loaded:", people)

# Reload the face recognizer and read the trained data
face_recognizer = cv.face.LBPHFaceRecognizer_create()
try:
    face_recognizer.read('face_trained.yml')
    print("Face recognizer loaded successfully.")
except cv.error as e:
    print(f"Error loading face recognizer: {e}")

cap = cv.VideoCapture(0)

blink_detected = False
blink_counter = 0
blink_threshold = 3  # Number of blinks required for confirmation
attendance_confirmed = False

def create_database():
    conn = sqlite3.connect('attendance.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS attendance (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    timestamp TEXT NOT NULL
                )''')
    conn.commit()
    conn.close()

def insert_attendance(name, timestamp):
    conn = sqlite3.connect('attendance.db')
    c = conn.cursor()
    c.execute('INSERT INTO attendance (name, timestamp) VALUES (?, ?)', (name, timestamp))
    conn.commit()
    conn.close()

# Initialize the database
create_database()

# Read user information from the temporary file and extract last_name
def read_user_info(file_path):
    if not os.path.exists(file_path):
        print("User info file does not exist.")
        return None

    with open(file_path, 'r') as file:
        user_info = {}
        for line in file:
            key, value = line.strip().split(": ", 1)
            user_info[key] = value
    
    print("User info extracted:", user_info)  # Debugging output

    if 'last_name' in user_info:
        return user_info['last_name']
    else:
        print("last_name not found in user info file.")
        return None

if len(sys.argv) < 2:
    print("No user info file provided.")
    sys.exit(1)

user_info_file = sys.argv[1]
last_name = read_user_info(user_info_file)

if not last_name:
    print("last_name not provided or found. Exiting...")
    sys.exit(1)

print("last_name:", last_name)

while True:
    ret, frame = cap.read()
    
    if not ret:
        break
    
    gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
    
    # Apply histogram equalization
    gray = cv.equalizeHist(gray)

    faces_rect = haar_face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=4)

    for (x, y, w, h) in faces_rect:
        faces_roi = gray[y:y+h, x:x+w]

        label, confidence = face_recognizer.predict(faces_roi)

        if confidence < 80:  # Confidence threshold to consider a match
            detected_person = people[label]
            detected_last_name = detected_person.split()[-1]  # Assuming last_name is the last part of the name
            if detected_last_name.lower() == last_name.lower():  # Case insensitive comparison
                cv.putText(frame, f"{detected_person} {confidence:.2f}", (x, y-10), cv.FONT_HERSHEY_COMPLEX, 1.0, (0, 255, 0), thickness=2)
                cv.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), thickness=2)

                eyes = haar_eye_cascade.detectMultiScale(gray[y:y+h, x:x+w])
                if len(eyes) == 0 and not blink_detected:  # Eyes closed
                    blink_detected = True
                    print(f"Blink detected for {detected_person}")
                elif len(eyes) >= 2 and blink_detected:  # Eyes open
                    blink_counter += 1
                    blink_detected = False
                    print(f"Blink count for {detected_person}: {blink_counter}")

                if blink_counter >= blink_threshold:
                    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    print(f"{timestamp} - {detected_person}: Is present with an accuracy of {confidence:.2f}")
                    cv.putText(frame, "Attendance Confirmed", (x, y+h+20), cv.FONT_HERSHEY_COMPLEX, 1.0, (0, 255, 0), thickness=2)
                    attendance_confirmed = True
                    insert_attendance(detected_person, timestamp)  # Insert record into database
        cv.putText(frame, f"Blinks: {blink_counter}/{blink_threshold}", (10, 30), cv.FONT_HERSHEY_SIMPLEX, 1.0, (0, 255, 0), 2)
        if not attendance_confirmed:
            cv.putText(frame, "Please blink to confirm attendance", (10, 60), cv.FONT_HERSHEY_SIMPLEX, 1.0, (0, 255, 255), 2)

    frame = cv.resize(frame, (min(frame.shape[1], 800), min(frame.shape[0], 600)))

    cv.imshow("Face Detection", frame)

    if attendance_confirmed or (cv.waitKey(1) & 0xFF == ord('q')):
        break

cap.release()
cv.destroyAllWindows()