import cv2
import os
from tkinter import *
from tkinter import messagebox
from PIL import Image, ImageTk
from datetime import datetime

# Function to capture and save a frame
def capture_frame():
    frame_name = frame_entry.get().strip()
    
    if not frame_name:
        messagebox.showerror("Error", "Please specify the frame name")
        return
    
    ret, frame = cap.read()
    if ret:
        base_folder = "Faces"
        target_folder = os.path.join(base_folder, frame_name)
        if not os.path.exists(target_folder):
            os.makedirs(target_folder)
        # Save the frame with a timestamp to ensure uniqueness
        img_path = os.path.join(target_folder, f"{frame_name}_{datetime.now().strftime('%Y%m%d%H%M%S')}.png")
        cv2.imwrite(img_path, frame)
        messagebox.showinfo("Info", f"Frame captured and saved as {img_path}")
    else:
        messagebox.showerror("Error", "Failed to capture frame")

# Function to display the frame
def show_frame():
    ret, frame = cap.read()
    if ret:
        cv2image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA)
        img = Image.fromarray(cv2image)
        imgtk = ImageTk.PhotoImage(image=img)
        lmain.imgtk = imgtk
        lmain.configure(image=imgtk)
    lmain.after(10, show_frame)

# Set up the main application window
root = Tk()
root.title("Face Register")

# Create a Label widget to display the frames
lmain = Label(root)
lmain.pack()

# Entry for frame (and folder) name
frame_label = Label(root, text="Surname")
frame_label.pack()
frame_entry = Entry(root)
frame_entry.pack()

# Create a Button to capture frames
capture_button = Button(root, text="Register Face", command=capture_frame)
capture_button.pack()

# Initialize the webcam
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    messagebox.showerror("Error", "Failed to open the webcam")
    root.destroy()

# Start displaying the frames
show_frame()

# Run the application
root.mainloop()

# Release the webcam and destroy windows
cap.release()
cv2.destroyAllWindows()
