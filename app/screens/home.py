import tkinter as tk

from app.screens.register import RegisterScreen
from app.screens.attendance import AttendanceScreen

class HomeScreen(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.configure(bg="white")  # Agregar fondo para debug
        
        tk.Label(
            self, 
            text="Bienvenido a la aplicación de reconocimiento facial",
            font=("Arial", 14, "bold"),
            bg="white"
        ).pack(pady=20, padx=10)
        
        tk.Button(
            self, 
            text="Registrar a nuevo alumno",
            command=lambda: controller.show_frame(RegisterScreen),
            bg="#2196F3",
            fg="white",
            font=("Arial", 11, "bold"),
            width=25,
            height=2
        ).pack(pady=10)
        
        tk.Button(
            self,
            text="Tomar Asistencia",
            command=lambda: controller.show_frame(AttendanceScreen),
            bg="#4CAF50",
            fg="white",
            font=("Arial", 11, "bold"),
            width=25,
            height=2
        ).pack(pady=10)