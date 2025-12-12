import tkinter as tk
from app.screens.home import HomeScreen
from app.screens.register import RegisterScreen

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        
        self.title("Registro de asistencia por reconocimiento facial")
        self.geometry("800x600")
        
        container = tk.Frame(self)
        container.pack(side="top", fill="both", expand=True)
        
        self.frames = {}
        
        for Screen in (HomeScreen, RegisterScreen):
            frame = Screen(parent=container, controller=self)
            self.frames[Screen] = frame
            frame.grid(row=0, column=0, sticky="nsew")
            
        self.show_frame(HomeScreen)
        
    def show_frame(self, screen_name):
        frame = self.frames[screen_name]
        frame.tkraise()