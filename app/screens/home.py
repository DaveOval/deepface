import tkinter as tk

class HomeScreen(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        
        tk.Label(self, text="Welcome to the Face Detector App").pack(pady=10, padx=10)
        
        