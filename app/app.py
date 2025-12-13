import tkinter as tk
from app.screens.home import HomeScreen
from app.screens.register import RegisterScreen
from app.screens.attendance import AttendanceScreen

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        
        self.title("Registro de asistencia por reconocimiento facial")
        self.geometry("1000x700")
        
        container = tk.Frame(self)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)
        
        self.frames = {}
        
        for Screen in (HomeScreen, RegisterScreen, AttendanceScreen):
            frame = Screen(parent=container, controller=self)
            self.frames[Screen] = frame
            frame.grid(row=0, column=0, sticky="nsew")
            
        self.show_frame(HomeScreen)
        
    def show_frame(self, screen_name):
        frame = self.frames[screen_name]
        frame.tkraise()