import tkinter as tk
import tkinter.messagebox
import cv2
import os
from PIL import Image, ImageTk

from app.utilities.go_home import go_home

class RegisterScreen(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        
        # Frame para el formulario inicial
        self.form_frame = tk.Frame(self)
        self.form_frame.pack(pady=10, padx=10)
        
        tk.Label(self.form_frame, text="Registro de nuevo alumno", font=("Arial", 14, "bold")).pack(pady=10)
        
        # Input for name
        self.name_var = tk.StringVar()
        tk.Label(self.form_frame, text="Nombre:").pack()
        self.name_entry = tk.Entry(self.form_frame, textvariable=self.name_var, font=("Arial", 11))
        self.name_entry.pack(pady=5)
        
        # Button to photo capture
        self.capture_btn = tk.Button(
            self.form_frame,
            text="Capturar Fotos",
            command=self.capture_photos,
            bg="#2196F3",
            fg="white",
            font=("Arial", 11, "bold"),
            padx=20,
            pady=10
        )
        self.capture_btn.pack(pady=10)
        
        tk.Button(
            self.form_frame,
            text="Volver al Inicio",
            command=lambda: go_home(controller)
        ).pack()
        
    def capture_photos(self):
        nombre = self.name_var.get().strip()
        
        if not nombre:
            tkinter.messagebox.showwarning("Error", "Por favor, ingrese un nombre válido.")
            return
        
        ruta = f"static/captures/{nombre}"
        os.makedirs(ruta, exist_ok=True)
        
        # Intentar abrir cámara automáticamente
        cap = None
        for idx in [0, 1, 2]:
            try:
                cap = cv2.VideoCapture(idx, cv2.CAP_DSHOW)
                if cap.isOpened():
                    ret, _ = cap.read()
                    if ret:
                        break
                    cap.release()
                    cap = None
            except:
                if cap:
                    cap.release()
                cap = None
        
        if cap is None or not cap.isOpened():
            tkinter.messagebox.showerror("Error", "No se pudo abrir la cámara. Verifique que esté conectada.")
            return
        
        # Ocultar formulario inicial
        self.form_frame.pack_forget()
        
        # Configurar cámara
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        
        contador = 0
        max_fotos = 10

        # Crear ventana de preview - colocarlo arriba
        preview_frame = tk.Frame(self)
        preview_frame.pack(side=tk.TOP, pady=5, fill=tk.BOTH, expand=True)

        preview_label = tk.Label(preview_frame, bg="black")
        preview_label.pack(pady=5)

        status_var = tk.StringVar(value=f"Capturas: 0/{max_fotos} - Presiona 'Tomar Captura' para guardar")
        status_label = tk.Label(preview_frame, textvariable=status_var, font=("Arial", 10))
        status_label.pack(pady=5)

        # Botones de control
        controls = tk.Frame(preview_frame)
        controls.pack(pady=10)

        def tomar_captura():
            nonlocal contador
            if current_frame["frame"] is None:
                status_var.set("Esperando frame de la cámara...")
                return
            
            img_path = f"{ruta}/img_{contador}.jpg"
            cv2.imwrite(img_path, current_frame["frame"])
            contador += 1
            status_var.set(f"Capturas: {contador}/{max_fotos} - ¡Foto guardada!")
            
            if contador >= max_fotos:
                status_var.set(f"¡Completado! {max_fotos} fotos guardadas en {ruta}")
                tomar_btn.config(state=tk.DISABLED)
                tkinter.messagebox.showinfo("Completado", f"Se han capturado {max_fotos} fotos exitosamente.")

        preview_running = {"active": True}
        current_frame = {"frame": None}
        
        def cerrar():
            preview_running["active"] = False
            try:
                if cap.isOpened():
                    cap.release()
            except:
                pass
            try:
                preview_frame.destroy()
            except:
                pass
            # Mostrar formulario nuevamente
            self.form_frame.pack(pady=10, padx=10)

        tomar_btn = tk.Button(controls, text="📷 Tomar Captura", command=tomar_captura, 
                             bg="#4CAF50", fg="white", font=("Arial", 12, "bold"), 
                             padx=20, pady=10)
        cerrar_btn = tk.Button(controls, text="Cerrar", command=cerrar, 
                              bg="#f44336", fg="white", font=("Arial", 10), 
                              padx=15, pady=5)
        tomar_btn.pack(side=tk.LEFT, padx=10)
        cerrar_btn.pack(side=tk.LEFT, padx=10)

        # Saltar primeros frames
        for _ in range(5):
            cap.grab()

        def update_preview():
            if not preview_running["active"]:
                return
            
            if not cap.isOpened():
                return
            
            ret, frame = cap.read()
            if not ret or frame is None:
                preview_label.after(30, update_preview)
                return
            
            # Convertir a RGB para mostrar
            try:
                if len(frame.shape) == 2:
                    frame = cv2.cvtColor(frame, cv2.COLOR_GRAY2BGR)
                rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            except:
                preview_label.after(30, update_preview)
                return
            
            # Redimensionar si es muy grande
            h, w = rgb.shape[:2]
            if w > 640:
                scale = 640 / w
                new_w = int(w * scale)
                new_h = int(h * scale)
                rgb = cv2.resize(rgb, (new_w, new_h))
            
            # Mostrar frame
            try:
                img = Image.fromarray(rgb)
                imgtk = ImageTk.PhotoImage(image=img)
                preview_label.imgtk = imgtk
                preview_label.configure(image=imgtk)
                current_frame["frame"] = frame
            except:
                pass
            
            preview_label.after(33, update_preview)

        update_preview()
