## Author: Quade Martin
## Last Updated: 2-12-2026
## Description: Entry Terminal class for Phonon laser tag game. 
##              Provides a GUI for entering player names and codenames for red and green teams.

import tkinter as tk  ## GUI framework for the application window
from tkinter import messagebox  ## Message boxes for dialogs
import os  ## File system operations
from PIL import Image, ImageTk
import psycopg2  ## PostgreSQL database stuff
from udp_files.udp import UDP

## Entry terminal class for Photon laser tag game
class EntryTerminal:
    """Laser tag entry terminal for red/green teams."""

    ## Initialize the entry terminal
    def __init__(self, root: tk.Tk, udp) -> None:
        self.root = root
        self.root.title("Entry Terminal")
        self.root.geometry("1100x680")
        self.root.minsize(980, 680)
        self.root.configure(bg="#0b0b0b")

        self.red_entries = []
        self.green_entries = []
        self.hardware_ids = {}  ## Dictionary to store (player_id, codename) -> hardware_id mappings
        self._codename_popup_open = False  ## Flag to track if the codename popup is currently open
        self.udp = udp

        ## Database connection parameters
        ## Uncomment bottom lines if you're coding locally
        self.db_params = {
            'dbname': 'photon',
            'user': 'student',
            # 'password': 'student',
            # 'host': 'localhost',
            # 'port': '5432'
        }

        # All frames that will be initialized using self.root
        self.header_frame = None
        self.content_frame = None
        self.status_frame = None

        self._build_ui()

    # Hide all frames using forget()
    def hide(self) -> None:
        self.header_frame.pack_forget()
        self.content_frame.pack_forget()
        self.status_frame.pack_forget()

    # Show all hidden frames
    def show(self) -> None:
        self.header_frame.pack(fill=tk.X, pady=(16, 8))
        self.content_frame.pack(fill=tk.BOTH, expand=True, padx=24, pady=10)
        self.status_frame.pack(fill=tk.X, pady=(8, 16))

    ## Build the user interface
    def _build_ui(self) -> None:
        self.header_frame = tk.Frame(self.root, bg="#0b0b0b")
        self.header_frame.pack(fill=tk.X, pady=(16, 8))

        ## Title label
        title = tk.Label(
            self.header_frame,
            text="Entry Terminal",
            font=("Arial", 18, "bold"),
            fg="#D3D3D3",
            bg="#0b0b0b",
        )
        title.pack()
    
        ## Subtitle label
        subtitle = tk.Label(
            self.header_frame,
            text="Edit Current Game",
            font=("Arial", 14, "bold"),
            fg="#6aa7ff",
            bg="#0b0b0b",
        )
        subtitle.pack(pady=(2, 0))

        # Network Input
        network_button = tk.Button(
            self.header_frame,
            text = "Update Network",
            font=("Arial", 10, "bold"),
            fg="#6aa7ff",
            bg="#0b0b0b",
            command=self.update_network_address,
        )
        network_button.pack(side=tk.RIGHT, padx=(0, 24))

        self.network_field = tk.Entry(
            self.header_frame,
            font=("Arial", 10, "bold"),
            fg="#6aa7ff",
            bg="#0b0b0b",
            justify="center"
        )
        self.network_field.pack(side=tk.RIGHT, padx=(0, 10))
        self.network_field.insert(10, "")
        

        ## Content frame to hold team frames
        self.content_frame = tk.Frame(self.root, bg="#0b0b0b")
        self.content_frame.pack(fill=tk.BOTH, expand=True, padx=24, pady=10)

        ## Red team frame
        red_frame = self._create_team_frame(
            self.content_frame,
            team_name="RED TEAM",
            team_color="#7a1010",
            accent="#ff4b4b",
            entries_list=self.red_entries,
        )
        red_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 10))

        ## Green team frame
        green_frame = self._create_team_frame(
            self.content_frame,
            team_name="GREEN TEAM",
            team_color="#0f5f0f",
            accent="#51ff7a",
            entries_list=self.green_entries,
        )
        green_frame.grid(row=0, column=1, sticky="nsew", padx=(10, 0))

        ## Configure content frame columns and rows
        self.content_frame.columnconfigure(0, weight=1)
        self.content_frame.columnconfigure(1, weight=1)
        self.content_frame.rowconfigure(0, weight=1)

        self.status_frame = tk.Frame(self.root, bg="#0b0b0b")
        self.status_frame.place(x=100, y=100, anchor = 'center')
        status = tk.Label(
            self.status_frame,
            text="F5 - Switch to action screen\nF12 - Clear terminal entries",
            font=("Arial", 9),
            fg="#BFC7D5",
            bg="#0B0B0B",
        )
        status.pack()

    ## Validation for IDs
    def _validate_numeric(self, value: str) -> bool:
        """Allow only numeric input."""
        return value.isdigit() or value == ""

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
        header.grid(row=0, column=0, columnspan=4, sticky="ew", pady=(8, 6))

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

        label_hardware = tk.Label(
            outer,
            text="Hardware ID",
            font=("Arial", 9, "bold"),
            fg="#dfe8f2",
            bg=team_color,
        )
        label_hardware.grid(row=1, column=3, sticky="w", padx=(2, 6), pady=(0, 6))

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

            # Validation command for numeric input
            vcmd = (self.root.register(self._validate_numeric), "%P")

            name_entry = tk.Entry(
                outer,
                font=("Arial", 9),
                bg="#f5f5f5",
                fg="#111111",
                relief=tk.FLAT,
                validate="key",
                validatecommand=vcmd,
            )
            name_entry.grid(row=row_index, column=1, sticky="ew", padx=(6, 2), pady=3, ipady=3)

            # Resets bg color when they start typing again after an error
            name_entry.bind("<Key>", lambda e, n=name_entry: n.configure(bg="#f5f5f5"))

            code_entry = tk.Entry(
                outer,
                font=("Arial", 9),
                bg="#f5f5f5",
                fg="#111111",
                relief=tk.FLAT,
                state="readonly",
            )
            code_entry.grid(row=row_index, column=2, sticky="ew", padx=(2, 6), pady=3, ipady=3)

            hardware_entry = tk.Entry(
                outer,
                font=("Arial", 9),
                bg="#f5f5f5",
                fg="#111111",
                relief=tk.FLAT,
                validate="key",
                validatecommand=vcmd,
            )
            hardware_entry.grid(row=row_index, column=3, sticky="ew", padx=(2, 6), pady=3, ipady=3)

            # Resets bg color when they start typing again after an error
            hardware_entry.bind("<Key>", lambda e, h=hardware_entry: h.configure(bg="#f5f5f5"))

            ## Bind Player ID to automatic codename lookup
            name_entry.bind("<FocusOut>", lambda e, n=name_entry, c=code_entry: self._on_player_id_entered(n, c))
            name_entry.bind("<Return>", lambda e, n=name_entry, c=code_entry: self._on_player_id_entered(n, c))
            hardware_entry.bind(
                "<FocusOut>",
                lambda e, n=name_entry, c=code_entry, h=hardware_entry: self._on_hardware_id_entered(n, c, h)
            )
            hardware_entry.bind(
                "<Return>",
                lambda e, n=name_entry, c=code_entry, h=hardware_entry: self._on_hardware_id_entered(n, c, h)
            )

            entries_list.append((name_entry, code_entry, hardware_entry))

        outer.columnconfigure(1, weight=1)
        outer.columnconfigure(2, weight=1)
        outer.columnconfigure(3, weight=1)
        return outer

    def _collect_entries(self):
        """
        Collect all entered player data from both teams.

        Returns:
            list: List of tuples containing (team, slot, player_id, codename) for each player
        """
        rows = []
        self.hardware_ids = {}
        for team_name, entries in (("Red", self.red_entries), ("Green", self.green_entries)):
            for index, (name_entry, code_entry, hardware_entry) in enumerate(entries, start=1):
                player_id = name_entry.get().strip()
                player_codename = code_entry.get().strip()
                hardware_id = hardware_entry.get().strip()

                if player_id and player_codename:
                    rows.append((team_name, index, player_id, player_codename))

                if player_id and player_codename and hardware_id:
                    self.hardware_ids[(player_id, player_codename)] = hardware_id
        return rows

    def get_entries(self):
        """
        Get all entered player data.
        
        Returns:
            list: List of tuples containing (team, slot, player_id, codename) for each player
        """
        return self._collect_entries()

    def _set_codename_entry(self, code_entry: tk.Entry, codename: str) -> None:
        code_entry.configure(state=tk.NORMAL)
        code_entry.delete(0, tk.END)
        if codename:
            code_entry.insert(0, codename)
        code_entry.configure(state="readonly")

    def _on_player_id_entered(self, name_entry: tk.Entry, code_entry: tk.Entry) -> None:
        """
        Called when Player ID loses focus or Enter is pressed.
        Loads codename from DB; if not found, prompts user for a codename.

        Args:
            name_entry: The player ID entry widget
            code_entry: The codename entry widget
        """
        player_id = name_entry.get().strip()

        if not player_id.isdigit():
            name_entry.configure(bg="#ffb3b3")
            return
        else:
            name_entry.configure(bg="#f5f5f5")

        previous_player_id = getattr(name_entry, "_last_player_id", None)
        if previous_player_id != player_id:
            setattr(name_entry, "_skip_missing_codename_for", None)
        setattr(name_entry, "_last_player_id", player_id)

        if self._codename_popup_open:
            return

        if not player_id:
            self._set_codename_entry(code_entry, "")
            return

        current_codename = code_entry.get().strip()
        if current_codename and previous_player_id == player_id:
            return

        skipped_player_id = getattr(name_entry, "_skip_missing_codename_for", None)
        if skipped_player_id == player_id:
            return

        player_row = self.get_player_by_id(player_id)
        if player_row and player_row[1]:
            self._set_codename_entry(code_entry, player_row[1])
            setattr(name_entry, "_skip_missing_codename_for", None)
            return

        self._codename_popup_open = True
        codename = self._show_codename_popup(player_id)
        self._codename_popup_open = False

        if not codename:
            self._set_codename_entry(code_entry, "")
            setattr(name_entry, "_skip_missing_codename_for", player_id)
            return

        self._set_codename_entry(code_entry, codename)
        setattr(name_entry, "_skip_missing_codename_for", None)

    def _show_codename_popup(self, player_id: str) -> str:
        """
        Display a popup dialog to register a codename for a player when not found in DB.

        Args:
            player_id: The player's ID
        Returns:
            str: The codename entered by the user, or None if cancelled
        """
        popup = tk.Toplevel(self.root)
        popup.title("Codename Required")
        popup.geometry("450x240")
        popup.configure(bg="#1a1a1a")
        popup.resizable(False, False)

        ## Center the popup on screen
        popup.transient(self.root)
        popup.update_idletasks()
        popup.grab_set()

        ## Header label
        header = tk.Label(
            popup,
            text="Create Codename",
            font=("Arial", 14, "bold"),
            fg="#51ff7a",
            bg="#1a1a1a"
        )
        header.pack(pady=(20, 5))

        ## Info label
        info = tk.Label(
            popup,
            text=f"No codename found for Player ID: {player_id}\n\nPlease enter a codename:",
            font=("Arial", 10),
            fg="#d3d3d3",
            bg="#1a1a1a",
            justify=tk.CENTER
        )
        info.pack(pady=(5, 15))

        ## Entry field for codename
        codename_entry = tk.Entry(
            popup,
            font=("Arial", 11),
            bg="#f5f5f5",
            fg="#111111",
            relief=tk.FLAT,
            width=30
        )
        codename_entry.pack(pady=10, ipady=4)
        codename_entry.focus_set()

        result = {"codename": None}

        ## On submitting the codename, validate and store it
        def on_submit():
            codename = codename_entry.get().strip()
            if not codename:
                messagebox.showwarning(
                    "Invalid Input",
                    "Codename cannot be empty.",
                    parent=popup
                )
                return
            result["codename"] = codename
            popup.destroy()

        ## On cancelling the popup, just close it without saving
        def on_cancel():
            popup.destroy()

        ## Button frame
        button_frame = tk.Frame(popup, bg="#1a1a1a")
        button_frame.pack(pady=15)

        ## Submit button
        submit_btn = tk.Button(
            button_frame,
            text="Save Codename",
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
        codename_entry.bind("<Return>", lambda e: on_submit())

        ## Wait for popup to close
        popup.wait_window()

        return result["codename"]

    def _on_hardware_id_entered(self, name_entry: tk.Entry, code_entry: tk.Entry, hardware_entry: tk.Entry) -> None:
        """
        Called when hardware ID loses focus or Enter is pressed.
        Registers the hardware ID for the player and sends it through UDP.
        """
        player_id = name_entry.get().strip()
        codename = code_entry.get().strip()
        hardware_id = hardware_entry.get().strip()

        if not hardware_id.isdigit():
            hardware_entry.configure(bg="#ffb3b3")  # light red
            return
        else:
            hardware_entry.configure(bg="#f5f5f5")  # reset if valid

        if not player_id or not codename or not hardware_id:
            return

        player_key = (player_id, codename)
        if self.hardware_ids.get(player_key) == hardware_id:
            return

        self.hardware_ids[player_key] = hardware_id
        self.udp.send_data(hardware_id)

    def get_hardware_ids(self) -> dict:
        """
        Get the dictionary of all registered hardware IDs.
        
        Returns:
            dict: Dictionary mapping (player_id, codename) tuples to hardware IDs
        """
        self._collect_entries()
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

    def save_to_database(self) -> None:
        """
        Save all entered player data to the database.
        Avoid inserting duplicate players.
        """
        rows = self._collect_entries()
        if not rows:
            messagebox.showwarning("No Data Saved", "No player data to save.")
            return

        try:
            conn = psycopg2.connect(**self.db_params)
            cursor = conn.cursor()

            # Get all existing players once
            cursor.execute("SELECT id, codename FROM players;")
            existing_players = set((str(row[0]), row[1]) for row in cursor.fetchall())

            new_players = []

            for team_name, slot, player_id, codename in rows:
                player_key = (player_id, codename)

                if player_key not in existing_players and player_key not in new_players:
                    new_players.append(player_key)

            # Insert only new players
            for player_id, codename in new_players:
                cursor.execute(
                    "INSERT INTO players (id, codename) VALUES (%s, %s);",
                    (player_id, codename)
                )

            conn.commit()
            cursor.close()
            conn.close()

            messagebox.showinfo(
                "Saved",
                f"{len(new_players)} new player(s) saved. "
                f"{len(rows) - len(new_players)} duplicate(s) skipped."
            )

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

    def update_network_address(self):
        network_ip = self.network_field.get().strip()
        self.udp.update_server_ip(network_ip)

    def clear_entries(self) -> None:
        """
        Clear all player entries from both red and green teams.
        """
        for entries in (self.red_entries, self.green_entries):
            for name_entry, code_entry, hardware_entry in entries:
                name_entry.delete(0, tk.END)

                code_entry.configure(state=tk.NORMAL)
                code_entry.delete(0, tk.END)
                code_entry.configure(state="readonly")

                hardware_entry.delete(0, tk.END)

        self.hardware_ids.clear()

def main():
    """Main entry point for the application"""
    udp = UDP()
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
        udp.setup_sockets()
        splash.destroy()
        root.deiconify()
        EntryTerminal(root, udp)

    def on_closing():
        udp.close_sockets()
        root.destroy()

    root.after(2500, show_main)
    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()


# Only run if this file is executed directly (not imported)
if __name__ == "__main__":
    main()
