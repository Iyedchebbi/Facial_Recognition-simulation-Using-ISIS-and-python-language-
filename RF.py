import cv2
import face_recognition
import numpy as np
import os
import serial
import smtplib
import imghdr
from email.message import EmailMessage

s = serial.Serial('COM4',9600)

# Load known face images and names
known_face_names = ["iyed"]  # Add names for each corresponding face
known_face_encodings = []

# Load known face encodings from images
for name in known_face_names:
    image = face_recognition.load_image_file(f"{name}.jpg")  # Replace with the actual image file paths
    encoding = face_recognition.face_encodings(image)[0]
    known_face_encodings.append(encoding)

# Initialize variables
face_locations = []
face_encodings = []
face_names = []
process_this_frame = True

# Open the webcam
cap = cv2.VideoCapture(0)

while True:
    print("waiting for bell input")
    serial_data = s.read()
    if(serial_data == b'a'):
        while(1):
            # Grab a single frame of video
            ret, frame = cap.read()

            # Resize frame of video to 1/4 size for faster face recognition processing
            small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)

            # Convert the image from BGR color (which OpenCV uses) to RGB color (which face_recognition uses)
            rgb_small_frame = small_frame[:, :, ::-1]

            # Only process every other frame of video to save time
            if process_this_frame:
                # Find all the faces and face encodings in the current frame of video
                face_locations = face_recognition.face_locations(small_frame)
                face_encodings = face_recognition.face_encodings(small_frame, face_locations)

                face_names = []
                for face_encoding in face_encodings:
                    # See if the face is a match for the known face(s)
                    matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
                    name = "Unknown"

                    # # If a match was found in known_face_encodings, just use the first one.
                    # if True in matches:
                    #     first_match_index = matches.index(True)
                    #     name = known_face_names[first_match_index]

                    # Or instead, use the known face with the smallest distance to the new face
                    face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)
                    best_match_index = np.argmin(face_distances)
                    if matches[best_match_index]:
                        name = known_face_names[best_match_index]

                    face_names.append(name)
                    if(name == "Unknown"):
                        s.write(b'0')
                        i = 0
                        serial_data = s.read()
                        if(serial_data == b'p'):
                            print(" Members present inside home no need to send image")
                        elif(serial_data == b'q'):
                            while i < 10:
                                print("sending image on mail")
                                return_value, image = cap.read()
                                cv2.imwrite('opencv.png', image)
                                i += 1
                                Sender_Email = "chebbiied@gmail.com"
                                Reciever_Email = "chebbiiyad@gmail.com"
                                Password = "lbqf myee deoq ejjs" #type your password here
                                newMessage = EmailMessage()                         
                                newMessage['Subject'] = "Alert Theft inside your home" 
                                newMessage['From'] = Sender_Email                   
                                newMessage['To'] = Reciever_Email                   
                                newMessage.set_content('Let me know what you think. Image attached!') 
                                with open('opencv.png', 'rb') as f:
                                    image_data = f.read()
                                    image_type = imghdr.what(f.name)
                                    image_name = f.name
                                newMessage.add_attachment(image_data, maintype='image', subtype=image_type, filename=image_name)
                                with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
                                    smtp.login(Sender_Email, Password)              
                                    smtp.send_message(newMessage)
                    elif(name == "CHEBBI Iyed"):
                        s.write(b'1')
                        
            process_this_frame = not process_this_frame


            # Display the results
            for (top, right, bottom, left), name in zip(face_locations, face_names):
                # Scale back up face locations since the frame we detected in was scaled to 1/4 size
                top *= 4
                right *= 4
                bottom *= 4
                left *= 4

                # Draw a box around the face
                cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)

                # Draw a label with a name below the face
                cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (0, 0, 255), cv2.FILLED)
                font = cv2.FONT_HERSHEY_DUPLEX
                cv2.putText(frame, name, (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)

            # Display the resulting image
            cv2.imshow('Video', frame)

            # Hit 'q' on the keyboard to quit!
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

video_capture.release()
cv2.destroyAllWindows()