import os
from deepface import DeepFace
import cv2
import numpy as np

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
        return None, None

    temp_path = "temp_frame.jpg"
    cv2.imwrite(temp_path, frame)

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
            return best_match, best_distance
        
        return None, None
        
    except Exception as e:
        if os.path.exists(temp_path):
            os.remove(temp_path)
        return None, None