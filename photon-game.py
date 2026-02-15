import psycopg2
from psycopg2 import sql
import tkinter as tk
from PIL import Image, ImageTk
from entry_screen import EntryTerminal
from udp_files.udp import UDP
import os

# Define connection parameters
## Uncomment bottom lines if you're coding locally
connection_params = {
    'dbname': 'photon',
    'user': 'student',
    # 'password': 'student',
    # 'host': 'localhost',
    # 'port': '5432'
}

def main():
    """Make instance of UDP class"""
    udp = UDP()
    """Main entry point for the application"""
    root = tk.Tk()
    root.withdraw()

    splash = tk.Toplevel(root)
    splash.title("Photon")
    splash.configure(bg="#0F0E0C")
    splash.overrideredirect(True)

    script_dir = os.path.dirname(os.path.abspath(__file__))
    logo_path = os.path.join(script_dir, "splash_image", "photon_logo.jpg")

    try:
        image = Image.open(logo_path)
        image = image.resize((1080, 600), Image.LANCZOS)
        photo = ImageTk.PhotoImage(image)
        splash.photo = photo
        label = tk.Label(splash, image=photo, bg="#0b0b0b")
        label.pack(padx=(30,0))
    except Exception:
        label = tk.Label(
            splash,
            text="Photon Laser Tag",
            font=("Arial", 20, "bold"),
            fg="#cfe8ff",
            bg="#0b0b0b",
            padx=30,
            pady=30,
        )
        label.pack()

    splash.update_idletasks()
    splash_width = splash.winfo_width()
    splash_height = splash.winfo_height()
    screen_width = splash.winfo_screenwidth()
    screen_height = splash.winfo_screenheight()
    x = (screen_width - splash_width) // 2
    y = (screen_height - splash_height) // 2
    splash.geometry(f"{splash_width}x{splash_height}+{x}+{y}")

    entry_terminal = None  # Store reference to entry terminal

    def show_main():
        udp.setup_sockets()
        nonlocal entry_terminal
        splash.destroy()
        root.deiconify()
        entry_terminal = EntryTerminal(root, udp)

    def on_closing():
        """Handle window closing event - save data before closing"""
        if entry_terminal:
            entry_terminal.save_to_database()
            # Uncomment below to clear database on close
            # entry_terminal.clear_database()
        root.destroy()

    root.after(2500, show_main)
    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()
    udp.close_sockets()

if __name__ == "__main__":
    main()

