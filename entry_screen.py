## Author: Quade Martin
## Last Updated: 2-12-2026
## Description: Entry Terminal class for Phonon laser tag game. 
##              Provides a GUI for entering player names and codenames for red and green teams.

import tkinter as tk  ## GUI framework for the application window
from tkinter import messagebox  ## Message boxes for dialogs
import os  ## File system operations
from PIL import Image, ImageTk
import psycopg2  ## PostgreSQL database stuff

## Entry terminal class for Photon laser tag game
class EntryTerminal:
    """Laser tag entry terminal for red/green teams."""

    ## Initialize the entry terminal
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("Entry Terminal")
        self.root.geometry("1100x680")
        self.root.minsize(980, 680)
        self.root.configure(bg="#0b0b0b")

        self.red_entries = []
        self.green_entries = []
        self.hardware_ids = {}  ## Dictionary to store (player_id, codename) -> hardware_id mappings
        
        ## Database connection parameters
        ## Uncomment bottom lines if you're coding locally
        self.db_params = {
            'dbname': 'photon',
            'user': 'student',
            # 'password': 'student',
            # 'host': 'localhost',
            # 'port': '5432'
        }

        self._build_ui()

    ## Build the user interface
    def _build_ui(self) -> None:
        header_frame = tk.Frame(self.root, bg="#0b0b0b")
        header_frame.pack(fill=tk.X, pady=(16, 8))

        ## Title label
        title = tk.Label(
            header_frame,
            text="Entry Terminal",
            font=("Arial", 18, "bold"),
            fg="#D3D3D3",
            bg="#0b0b0b",
        )
        title.pack()
    
        ## Subtitle label
        subtitle = tk.Label(
            header_frame,
            text="Edit Current Game",
            font=("Arial", 14, "bold"),
            fg="#6aa7ff",
            bg="#0b0b0b",
        )
        subtitle.pack(pady=(2, 0))

        ## Content frame to hold team frames
        content_frame = tk.Frame(self.root, bg="#0b0b0b")
        content_frame.pack(fill=tk.BOTH, expand=True, padx=24, pady=10)

        ## Red team frame
        red_frame = self._create_team_frame(
            content_frame,
            team_name="RED TEAM",
            team_color="#7a1010",
            accent="#ff4b4b",
            entries_list=self.red_entries,
        )
        red_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 10))

        ## Green team frame
        green_frame = self._create_team_frame(
            content_frame,
            team_name="GREEN TEAM",
            team_color="#0f5f0f",
            accent="#51ff7a",
            entries_list=self.green_entries,
        )
        green_frame.grid(row=0, column=1, sticky="nsew", padx=(10, 0))

        ## Configure content frame columns and rows
        content_frame.columnconfigure(0, weight=1)
        content_frame.columnconfigure(1, weight=1)
        content_frame.rowconfigure(0, weight=1)

        status_frame = tk.Frame(self.root, bg="#0b0b0b")
        status_frame.pack(fill=tk.X, pady=(8, 16))

        # status = tk.Label(
        #     status_frame,
        #     text="Game Mode: Standard public mode",
        #     font=("Arial", 9),
        #     fg="#bfc7d5",
        #     bg="#0b0b0b",
        # )
        # status.pack()

    ## Create team frame for entries
    def _create_team_frame(
        self,
        parent: tk.Widget,
        team_name: str,
        team_color: str,
        accent: str,
        entries_list: list,
    ) -> tk.Frame:
        outer = tk.Frame(parent, bg=team_color, bd=2, relief=tk.GROOVE)

        header = tk.Label(
            outer,
            text=team_name,
            font=("Arial", 12, "bold"),
            fg=accent,
            bg=team_color,
        )
        header.grid(row=0, column=0, columnspan=3, sticky="ew", pady=(8, 6))

        label_name = tk.Label(
            outer,
            text="Player ID",
            font=("Arial", 9, "bold"),
            fg="#dfe8f2",
            bg=team_color,
        )
        label_name.grid(row=1, column=1, sticky="w", padx=(6, 2), pady=(0, 6))

        label_code = tk.Label(
            outer,
            text="Codename",
            font=("Arial", 9, "bold"),
            fg="#dfe8f2",
            bg=team_color,
        )
        label_code.grid(row=1, column=2, sticky="w", padx=(2, 6), pady=(0, 6))

        for i in range(15):
            row_index = i + 2
            number = tk.Label(
                outer,
                text=str(i + 1),
                font=("Arial", 9),
                fg="#f2f2f2",
                bg=team_color,
                width=3,
                anchor="e",
            )
            number.grid(row=row_index, column=0, sticky="e", padx=(6, 4), pady=3)

            name_entry = tk.Entry(
                outer,
                font=("Arial", 9),
                bg="#f5f5f5",
                fg="#111111",
                relief=tk.FLAT,
            )
            name_entry.grid(row=row_index, column=1, sticky="ew", padx=(6, 2), pady=3, ipady=3)

            code_entry = tk.Entry(
                outer,
                font=("Arial", 9),
                bg="#f5f5f5",
                fg="#111111",
                relief=tk.FLAT,
            )
            code_entry.grid(row=row_index, column=2, sticky="ew", padx=(2, 6), pady=3, ipady=3)
            
            ## Bind FocusOut event to check for hardware ID when codename is entered
            code_entry.bind("<FocusOut>", lambda e, n=name_entry, c=code_entry: self._on_codename_entered(n, c))

            entries_list.append((name_entry, code_entry))

        outer.columnconfigure(1, weight=1)
        outer.columnconfigure(2, weight=1)
        return outer

    def _collect_entries(self):
        """
        Collect all entered player data from both teams.

        Returns:
            list: List of tuples containing (team, slot, player_id, codename) for each player
        """
        rows = []
        for team_name, entries in (("Red", self.red_entries), ("Green", self.green_entries)):
            for index, (name_entry, code_entry) in enumerate(entries, start=1):
                name = name_entry.get().strip()
                player_codename = code_entry.get().strip()
                if name or player_codename:
                    rows.append((team_name, index, name, player_codename))
        return rows

    def get_entries(self):
        """
        Get all entered player data.
        
        Returns:
            list: List of tuples containing (team, slot, player_id, codename) for each player
        """
        return self._collect_entries()

    def _on_codename_entered(self, name_entry: tk.Entry, code_entry: tk.Entry) -> None:
        """
        Called when codename field loses focus. Checks if both player ID and codename
        are filled, and prompts for hardware ID if not already registered.
        
        Args:
            name_entry: The player ID entry widget
            code_entry: The codename entry widget
        """
        player_id = name_entry.get().strip()
        codename = code_entry.get().strip()
        
        ## Only proceed if both fields are filled
        if not player_id or not codename:
            return
        
        ## Create a unique key for this player
        player_key = (player_id, codename)
        
        ## Check if hardware ID already registered for this player
        if player_key in self.hardware_ids:
            return
        
        ## Show popup to get hardware ID
        hardware_id = self._show_hardware_id_popup(player_id, codename)
        
        if hardware_id:
            self.hardware_ids[player_key] = hardware_id
    
    def _show_hardware_id_popup(self, player_id: str, codename: str) -> str:
        """
        Display a popup dialog to register a hardware ID for a player.
        
        Args:
            player_id: The player's ID
            codename: The player's codename
            
        Returns:
            str: The hardware ID entered by the user, or None if cancelled
        """
        popup = tk.Toplevel(self.root)
        popup.title("Hardware ID Required")
        popup.geometry("450x220")
        popup.configure(bg="#1a1a1a")
        popup.resizable(False, False)
        
        ## Center the popup on screen
        popup.transient(self.root)
        popup.grab_set()
        
        ## Header label
        header = tk.Label(
            popup,
            text="Link Hardware ID",
            font=("Arial", 14, "bold"),
            fg="#51ff7a",
            bg="#1a1a1a"
        )
        header.pack(pady=(20, 5))
        
        ## Info label
        info = tk.Label(
            popup,
            text=f"Player ID: {player_id}\nCodename: {codename}\n\nPlease scan or enter the hardware ID:",
            font=("Arial", 10),
            fg="#d3d3d3",
            bg="#1a1a1a",
            justify=tk.CENTER
        )
        info.pack(pady=(5, 15))
        
        ## Entry field for hardware ID
        hardware_entry = tk.Entry(
            popup,
            font=("Arial", 11),
            bg="#f5f5f5",
            fg="#111111",
            relief=tk.FLAT,
            width=30
        )
        hardware_entry.pack(pady=10, ipady=4)
        hardware_entry.focus_set()
        
        result = {"hardware_id": None}
        
        def on_submit():
            hardware_id = hardware_entry.get().strip()
            if not hardware_id:
                messagebox.showwarning(
                    "Invalid Input",
                    "Hardware ID cannot be empty.",
                    parent=popup
                )
                return
            result["hardware_id"] = hardware_id
            popup.destroy()
        
        def on_cancel():
            popup.destroy()
        
        ## Button frame
        button_frame = tk.Frame(popup, bg="#1a1a1a")
        button_frame.pack(pady=15)
        
        ## Submit button
        submit_btn = tk.Button(
            button_frame,
            text="Link Hardware",
            font=("Arial", 10, "bold"),
            bg="#51ff7a",
            fg="#111111",
            relief=tk.FLAT,
            width=12,
            command=on_submit
        )
        submit_btn.grid(row=0, column=0, padx=5)
        
        ## Cancel button
        cancel_btn = tk.Button(
            button_frame,
            text="Skip",
            font=("Arial", 10),
            bg="#4a4a4a",
            fg="#d3d3d3",
            relief=tk.FLAT,
            width=12,
            command=on_cancel
        )
        cancel_btn.grid(row=0, column=1, padx=5)
        
        ## Bind Enter key to submit
        hardware_entry.bind("<Return>", lambda e: on_submit())
        
        ## Wait for popup to close
        popup.wait_window()
        
        return result["hardware_id"]
    
    def get_hardware_ids(self) -> dict:
        """
        Get the dictionary of all registered hardware IDs.
        
        Returns:
            dict: Dictionary mapping (player_id, codename) tuples to hardware IDs
        """
        return self.hardware_ids.copy()
    
    def get_player_by_id(self, player_id: str):
        """
        Retrieve a specific player from the database by ID.
        
        Args:
            player_id: The player's ID
            
        Returns:
            tuple: (id, codename) if found, None otherwise
        """
        try:
            conn = psycopg2.connect(**self.db_params)
            cursor = conn.cursor()
            cursor.execute("SELECT id, codename FROM players WHERE id = %s;", (player_id,))
            row = cursor.fetchone()
            cursor.close()
            conn.close()
            return row
        except Exception as error:
            messagebox.showerror("Database Error", f"Failed to retrieve player: {error}")
            return None

    ## Test method to save entries to CSV
    # def save_to_csv(self) -> None:
    #     rows = self._collect_entries()
    #     if not rows:
    #         messagebox.showwarning("No Data", "Please enter at least one player before saving.")
    #         return

    #     output_file = filedialog.asksaveasfilename(
    #         title="Save Players CSV",
    #         defaultextension=".csv",
    #         filetypes=[("CSV Files", "*.csv"), ("All Files", "*.*")],
    #         initialfile=f"laser_tag_players_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
    #     )
    #     if not output_file:
    #         return

    #     try:
    #         with open(output_file, "w", newline="", encoding="utf-8") as csv_file:
    #             writer = csv.writer(csv_file)
    #             writer.writerow(["team", "slot", "player_id", "codename"])
    #             writer.writerows(rows)

    #         messagebox.showinfo(
    #             "Saved",
    #             f"Saved {len(rows)} player(s) to:\n{os.path.basename(output_file)}",
    #         )
    #     except Exception as exc:
    #         messagebox.showerror("Error", f"Failed to save CSV:\n{exc}")

    def save_to_database(self) -> None:
        """
        Save all entered player data to the PostgreSQL database.
        """
        rows = self._collect_entries()
        if not rows:
            messagebox.showwarning("No Data Saved", "No player data to save.")
            return

        try:
            conn = psycopg2.connect(**self.db_params)
            cursor = conn.cursor()

            for team_name, slot, player_id, codename in rows:
                cursor.execute(
                    "INSERT INTO players (id, codename) VALUES (%s, %s);",
                    (player_id, codename)
                )

            conn.commit()
            cursor.close()
            conn.close()

            messagebox.showinfo("Saved", f"Saved {len(rows)} player(s) to the database.")
        except Exception as error:
            messagebox.showerror("Database Error", f"Failed to save players: {error}")
    
    def clear_database(self) -> None:
        """
        Clear all player data from the database. Use with caution!
        """
        if not messagebox.askyesno("Confirm Clear", "Are you sure you want to clear all player data from the database? This action cannot be undone."):
            return

        try:
            conn = psycopg2.connect(**self.db_params)
            cursor = conn.cursor()
            cursor.execute("DELETE FROM players;")
            conn.commit()
            cursor.close()
            conn.close()

            messagebox.showinfo("Database Cleared", "All player data has been cleared from the database.")
        except Exception as error:
            messagebox.showerror("Database Error", f"Failed to clear database: {error}")

def main():
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

    def show_main():
        splash.destroy()
        root.deiconify()
        EntryTerminal(root)

    root.after(2500, show_main)
    root.mainloop()


# Only run if this file is executed directly (not imported)
if __name__ == "__main__":
    main()
