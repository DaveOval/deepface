import os
from deepface import DeepFace
import cv2
import numpy as np

# Cargar el clasificador de rostros de OpenCV
face_cascade = None
def get_face_cascade():
    global face_cascade
    if face_cascade is None:
        cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        face_cascade = cv2.CascadeClassifier(cascade_path)
    return face_cascade

def load_registered_students():
    students = {}
    captures_dir = "static/captures"

    if not os.path.exists(captures_dir):
        return students

    for folder_name in os.listdir(captures_dir):
        folder_path = os.path.join(captures_dir, folder_name)
        if os.path.isdir(folder_path):
            name_parts = folder_name.rsplit("_", 1)[0]
            student_name = name_parts.replace("_", " ")

            images = []

            for file in os.listdir(folder_path):
                if file.lower().endswith((".jpg", ".jpeg", ".png")):
                    images.append(os.path.join(folder_path, file))

            if images:
                students[student_name] = images

    return students


def recognize_face(frame, registered_students, threshold=0.5):
    if not registered_students:
        return None, None, None

    # Detectar rostro con OpenCV primero (más rápido)
    face_region = None
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    cascade = get_face_cascade()
    faces = cascade.detectMultiScale(gray, 1.1, 4)
    
    if len(faces) > 0:
        # Usar el primer rostro detectado
        x, y, w, h = faces[0]
        face_region = (x, y, w, h)
        # Recortar el rostro para el reconocimiento
        face_crop = frame[y:y+h, x:x+w]
    else:
        face_crop = frame

    temp_path = "temp_frame.jpg"
    cv2.imwrite(temp_path, face_crop)

    try:
        best_match = None
        best_distance = float('inf')
        
        for student_name, image_paths in registered_students.items():
            for img_path in image_paths:
                try:
                    result = DeepFace.verify(
                        img1_path=temp_path,
                        img2_path=img_path,
                        model_name='VGG-Face',
                        enforce_detection=False,
                        silent=True
                    )
                    
                    distance = result['distance']
                    if distance < best_distance:
                        best_distance = distance
                        best_match = student_name
                        
                except Exception as e:
                    continue
        
        if os.path.exists(temp_path):
            os.remove(temp_path)
        
        if best_match and best_distance < threshold:
            return best_match, best_distance, face_region
        
        return None, None, face_region
        
    except Exception as e:
        if os.path.exists(temp_path):
            os.remove(temp_path)
        return None, None, face_region