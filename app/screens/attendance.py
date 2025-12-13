import tkinter as tk
import tkinter.messagebox
import cv2
from PIL import Image, ImageTk
import uuid
from datetime import datetime

from app.utilities.go_home import go_home
from app.utilities.face_recognition import load_registered_students, recognize_face
from app.utilities.attendance_storage import record_attendance

class AttendanceScreen(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.configure(bg="#F0F0F0")
        
        self.controller = controller
        self.cap = None
        self.preview_running = False
        self.recognition_active = False
        self.registered_students = {}
        self.session_id = None
        self.present_students = set()
        
        # Header superior
        header = tk.Frame(self, bg="#34495E", height=60)
        header.pack(fill=tk.X, side=tk.TOP)
        header.pack_propagate(False)
        
        title = tk.Label(
            header,
            text="📹 Sistema de Asistencia Automatizada",
            font=("Arial", 16, "bold"),
            bg="#34495E",
            fg="white"
        )
        title.pack(expand=True)
        
        # Contenedor principal
        main_container = tk.Frame(self, bg="#F0F0F0")
        main_container.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        # Frame para cámara (izquierda)
        camera_section = tk.Frame(main_container, bg="white", relief=tk.RAISED, bd=1)
        camera_section.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        # Título de sección cámara
        camera_label = tk.Label(
            camera_section,
            text="Vista de Cámara",
            font=("Arial", 12, "bold"),
            bg="white",
            fg="#2C3E50",
            pady=10
        )
        camera_label.pack()
        
        # BOTONES PRIMERO - SIEMPRE VISIBLES EN LA PARTE SUPERIOR
        buttons_frame = tk.Frame(camera_section, bg="white")
        buttons_frame.pack(pady=10, padx=15, fill=tk.X)
        
        self.start_btn = tk.Button(
            buttons_frame,
            text="▶ INICIAR RECONOCIMIENTO",
            command=self.start_recognition,
            bg="#4CAF50",
            fg="white",
            font=("Arial", 12, "bold"),
            width=22,
            height=2,
            relief=tk.RAISED,
            bd=3,
            cursor="hand2",
            activebackground="#45a049"
        )
        self.start_btn.pack(side=tk.LEFT, padx=5, expand=True, fill=tk.X)
        
        self.stop_btn = tk.Button(
            buttons_frame,
            text="⏹ DETENER",
            command=self.stop_recognition,
            bg="#F44336",
            fg="white",
            font=("Arial", 12, "bold"),
            width=22,
            height=2,
            state=tk.DISABLED,
            relief=tk.RAISED,
            bd=3,
            cursor="hand2",
            activebackground="#da190b"
        )
        self.stop_btn.pack(side=tk.LEFT, padx=5, expand=True, fill=tk.X)
        
        # Status bar
        status_frame = tk.Frame(camera_section, bg="#E3F2FD", relief=tk.FLAT)
        status_frame.pack(fill=tk.X, padx=15, pady=(0, 10))
        
        self.status_var = tk.StringVar(value="⏸️ Presiona 'Iniciar Reconocimiento' para comenzar")
        status_label = tk.Label(
            status_frame,
            textvariable=self.status_var,
            font=("Arial", 9),
            bg="#E3F2FD",
            fg="#1565C0",
            pady=6,
            wraplength=500
        )
        status_label.pack()
        
        # Contenedor del preview con borde - TAMAÑO MUY AUMENTADO
        preview_wrapper = tk.Frame(camera_section, bg="#2C3E50", relief=tk.SUNKEN, bd=2)
        preview_wrapper.pack(padx=15, pady=10, fill=tk.BOTH, expand=True)
        
        self.preview_label = tk.Label(
            preview_wrapper,
            bg="#000000",
            width=100,  # MUY AUMENTADO
            height=40,  # MUY AUMENTADO
            text="📷\n\nPresiona 'Iniciar Reconocimiento'\npara activar la cámara",
            fg="white",
            font=("Arial", 11),
            justify=tk.CENTER
        )
        self.preview_label.pack(padx=3, pady=3, fill=tk.BOTH, expand=True)
        
        # Frame para lista (derecha) - tamaño fijo
        list_section = tk.Frame(main_container, bg="white", width=300, relief=tk.RAISED, bd=1)
        list_section.pack(side=tk.RIGHT, fill=tk.BOTH, padx=(10, 0))
        list_section.pack_propagate(False)
        
        # Título de lista
        list_title = tk.Label(
            list_section,
            text="👥 Estudiantes Presentes",
            font=("Arial", 12, "bold"),
            bg="white",
            fg="#2C3E50",
            pady=10
        )
        list_title.pack()
        
        # Contador
        self.count_var = tk.StringVar(value="Total: 0")
        count_label = tk.Label(
            list_section,
            textvariable=self.count_var,
            font=("Arial", 9),
            bg="white",
            fg="#7F8C8D"
        )
        count_label.pack()
        
        # Lista con scrollbar
        list_container = tk.Frame(list_section, bg="#F5F5F5", relief=tk.SUNKEN, bd=1)
        list_container.pack(fill=tk.BOTH, expand=True, padx=15, pady=(5, 15))
        
        scrollbar = tk.Scrollbar(list_container)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.present_listbox = tk.Listbox(
            list_container,
            yscrollcommand=scrollbar.set,
            font=("Arial", 10),
            bg="white",
            fg="#2C3E50",
            selectbackground="#2196F3",
            selectforeground="white",
            relief=tk.FLAT,
            bd=0,
            height=20
        )
        self.present_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.present_listbox.yview)
        
        # Footer con botón volver
        footer = tk.Frame(self, bg="#F0F0F0")
        footer.pack(fill=tk.X, side=tk.BOTTOM, pady=10)
        
        back_btn = tk.Button(
            footer,
            text="← Volver al Inicio",
            command=lambda: self.cleanup_and_go_home(),
            font=("Arial", 10),
            bg="#2196F3",
            fg="white",
            width=18,
            height=1,
            relief=tk.FLAT,
            cursor="hand2",
            activebackground="#1976D2"
        )
        back_btn.pack()
        
        self.load_students()
    
    def load_students(self):
        self.registered_students = load_registered_students()
        if not self.registered_students:
            self.status_var.set("⚠️ No hay estudiantes registrados. Registra estudiantes primero.")
    
    def start_recognition(self):
        if not self.registered_students:
            tkinter.messagebox.showwarning(
                "Sin estudiantes",
                "No hay estudiantes registrados. Por favor, registra estudiantes primero."
            )
            return
        
        self.session_id = str(uuid.uuid4())
        self.present_students.clear()
        self.present_listbox.delete(0, tk.END)
        self.count_var.set("Total: 0")
        
        self.cap = None
        for idx in [0, 1, 2]:
            try:
                self.cap = cv2.VideoCapture(idx, cv2.CAP_DSHOW)
                if self.cap.isOpened():
                    ret, _ = self.cap.read()
                    if ret:
                        break
                    self.cap.release()
                    self.cap = None
            except:
                if self.cap:
                    self.cap.release()
                self.cap = None
        
        if self.cap is None or not self.cap.isOpened():
            tkinter.messagebox.showerror(
                "Error",
                "No se pudo abrir la cámara. Verifique que esté conectada."
            )
            return
        
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        
        self.recognition_active = True
        self.preview_running = True
        
        self.start_btn.config(state=tk.DISABLED)
        self.stop_btn.config(state=tk.NORMAL)
        
        self.status_var.set("🔍 Reconocimiento activo - Mirando a la cámara...")
        self.preview_label.config(text="")
        
        self.update_preview()
    
    def stop_recognition(self):
        self.recognition_active = False
        self.preview_running = False
        
        if self.cap:
            self.cap.release()
            self.cap = None
        
        self.start_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)
        
        count = len(self.present_students)
        self.status_var.set(f"⏸️ Reconocimiento detenido - {count} estudiante(s) registrado(s)")
        self.count_var.set(f"Total: {count}")
        
        self.preview_label.config(
            text="📷\n\nCámara detenida\n\nPresiona 'Iniciar Reconocimiento'\npara continuar",
            fg="white"
        )
    
    def update_preview(self):
        if not self.preview_running:
            return
        
        if not self.cap or not self.cap.isOpened():
            return
        
        ret, frame = self.cap.read()
        if not ret or frame is None:
            self.preview_label.after(100, self.update_preview)
            return
        
        if self.recognition_active:
            if not hasattr(self, 'frame_count'):
                self.frame_count = 0
            
            self.frame_count += 1
            if self.frame_count % 30 == 0:
                student_name, distance = recognize_face(frame, self.registered_students)
                
                if student_name:
                    if student_name not in self.present_students:
                        if record_attendance(student_name, self.session_id):
                            self.present_students.add(student_name)
                            self.present_listbox.insert(tk.END, f"✓ {student_name}")
                            count = len(self.present_students)
                            self.count_var.set(f"Total: {count}")
                            self.status_var.set(f"✅ {student_name} registrado - Distancia: {distance:.3f}")
        
        try:
            if len(frame.shape) == 2:
                frame = cv2.cvtColor(frame, cv2.COLOR_GRAY2BGR)
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        except:
            self.preview_label.after(33, self.update_preview)
            return
        
        # Redimensionar para que quepa bien - TAMAÑO MUY AUMENTADO
        h, w = rgb.shape[:2]
        # Tamaño máximo mucho más grande para que se vea bien
        max_width = 1200  # MUY AUMENTADO
        max_height = 900  # MUY AUMENTADO
        
        if w > max_width or h > max_height:
            scale_w = max_width / w
            scale_h = max_height / h
            scale = min(scale_w, scale_h)
            new_w = int(w * scale)
            new_h = int(h * scale)
            rgb = cv2.resize(rgb, (new_w, new_h))
        else:
            # Si el video es más pequeño que el máximo, escalarlo para que use más espacio
            # Aumentar hasta el 90% del tamaño máximo si es posible
            target_width = min(max_width, int(w * 1.5))
            target_height = min(max_height, int(h * 1.5))
            if target_width > w or target_height > h:
                rgb = cv2.resize(rgb, (target_width, target_height))
        
        try:
            img = Image.fromarray(rgb)
            imgtk = ImageTk.PhotoImage(image=img)
            self.preview_label.imgtk = imgtk
            self.preview_label.configure(image=imgtk, text="")
        except:
            pass
        
        self.preview_label.after(33, self.update_preview)
    
    def cleanup_and_go_home(self):
        """Limpia recursos y vuelve al inicio"""
        self.stop_recognition()
        go_home(self.controller)