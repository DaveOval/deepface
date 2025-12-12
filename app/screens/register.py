import tkinter as tk
from app.utilities.go_home import go_home

class RegisterScreen(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        
        tk.Label(self, text="Register New User").pack(pady=10, padx=10)
        
        tk.Button(
            self,
            text="Volver al Inicio",
            command= lambda: go_home(controller)
        ).pack()