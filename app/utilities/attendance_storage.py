import json
import os
from datetime import datetime

ATTENDANCE_FILE = "attendance.json"

def load_attendance():
    if os.path.exists(ATTENDANCE_FILE):
        try:
            with open(ATTENDANCE_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return []
    return []

def save_attendance(attendance_records):
    with open(ATTENDANCE_FILE, 'w', encoding='utf-8') as f:
        json.dump(attendance_records, f, ensure_ascii=False, indent=2)

def record_attendance(student_name, session_id=None):
    records = load_attendance()
    
    now = datetime.now()
    date_str = now.strftime("%Y-%m-%d")
    time_str = now.strftime("%H:%M:%S")
    
    if session_id:
        for record in records:
            if (record.get('student_name') == student_name and 
                record.get('date') == date_str and
                record.get('session_id') == session_id):
                return False
    
    new_record = {
        'student_name': student_name,
        'date': date_str,
        'time': time_str,
        'session_id': session_id,
        'timestamp': now.isoformat()
    }
    
    records.append(new_record)
    save_attendance(records)
    return True

def get_attendance_by_date(date_str):
    records = load_attendance()
    return [r for r in records if r.get('date') == date_str]

def get_all_students_present_today():
    today = datetime.now().strftime("%Y-%m-%d")
    records = get_attendance_by_date(today)
    students = list(set([r['student_name'] for r in records]))
    return sorted(students)