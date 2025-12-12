import tkinter as tk

from app.screens.register import RegisterScreen

class HomeScreen(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        
        tk.Label(self, text="Bienvenido a la aplicación de reconocimiento facial").pack(pady=10, padx=10)
        
        tk.Button(self, text="Registrar a nuevo alumno",
            command=lambda: controller.show_frame(RegisterScreen)
        ).pack()