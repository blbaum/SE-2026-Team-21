import tkinter as tk
from tkinter import Label

from udp_files.udp import UDP

import PIL.Image
import PIL.ImageTk

SCREEN_WIDTH = 1100
SCREEN_HEIGHT = 680

class ActionScreen:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.udp = UDP()
        self.root.title("Action Screen")
        self.root.geometry(f"{SCREEN_WIDTH}x{SCREEN_HEIGHT}")
        self.root.minsize(980, 680)
        self.root.configure(bg="#0b0b0b")
        self.players_green = [
            {
                'name': "green-player",
                'id': "111",
                'equipment_id': "123",
                'score': 0,
            },
            {
                'name': "green-player2",
                'id': "111",
                'equipment_id': "789",
                'score': 0,
            },
        ]
        self.players_red = [
            {
                'name': "red-player",
                'id': "222",
                'equipment_id': "456",
                'score': 0,
            },
            {
                'name': "red-player2",
                'id': "444",
                'equipment_id': "101112",
                'score': 0,
            },
        ]


        # Load  countdown images 
        self.countdown_imgs = []
        for i in range(0, 31):
            img = PIL.Image.open(f"countdown_images/{i}.tif")
            photo = PIL.ImageTk.PhotoImage(img)
            self.countdown_imgs.append(photo) #index 0-30
        
        # Load countdown bg image
        img = PIL.Image.open(f"countdown_images/background.tif")
        photo = PIL.ImageTk.PhotoImage(img)
        self.countdown_imgs.append(photo) # index 31

        # Load countdown alert image
        img = PIL.Image.open(f"countdown_images/alert-on.tif")
        photo = PIL.ImageTk.PhotoImage(img)
        self.countdown_imgs.append(photo) # index 32


        # All frames that will be initialized using self.root
        self.full_frame = None

        self._build_ui()

    def hide(self) -> None:
        self.full_frame.pack_forget()

    # Show all hidden frames
    def show(self) -> None:
        self.full_frame.pack(fill=tk.BOTH, expand=True, padx=4, pady=4)
        self._run_countdown(30)

    def _build_ui(self) -> None:
        # yellow border effect
        self.full_frame = tk.Frame(self.root, bg="#FFD355")
        self.full_frame.pack(fill=tk.BOTH, expand=True, padx=4, pady=4)

        # main frame
        player_frame = tk.Frame(self.full_frame, bg="#0b0b0b")
        player_frame.pack(fill=tk.BOTH, expand=True, padx=4, pady=4)

        player_frame_header = tk.Frame(player_frame, bg="#0b0b0b")
        player_frame_header.pack(fill=tk.BOTH) 
        
        # header
        current_score_header = tk.Label(
            player_frame_header,
            text="Current Scores",
            font=("Arial", 16, "bold"),
            fg="#ffffff",
            bg="#0b0b0b",
        )
        current_score_header.pack(fill=tk.X)

        # red team info
        player_info_red = tk.Frame(player_frame, bg="#0b0b0b")
        player_info_red.pack(fill=tk.BOTH, side=tk.LEFT,  expand=True,padx=4)

        player_red_label = tk.Label(
            player_info_red,
            text="Red Team",
            font=("Arial", 12, "bold"),
            fg="#ffffff",
            bg="#0b0b0b",
        )
        player_red_label.pack(fill=tk.X)
        
        for red_player in self.players_red:
            row = tk.Frame(player_info_red, bg="#0b0b0b")
            row.pack(fill=tk.X, padx=10, pady=5)

            player_name= Label(
                row, 
                text=red_player['name'],
                font=("Ariel", 12, "bold"),
                fg="#ff4b4b", 
                bg="#0b0b0b", 
            )
            player_name.pack(side=tk.LEFT)
            player_score = Label(
                row, 
                text=red_player['score'], 
                font=("Ariel", 12, "bold"),
                fg="#ff4b4b", 
                bg="#0b0b0b", 
            )
            player_score.pack(side=tk.RIGHT)
        
        # green team info
        player_info_green = tk.Frame(player_frame, bg="#0b0b0b")
        player_info_green.pack(fill=tk.BOTH, side=tk.RIGHT, expand=True, padx=4)

        player_green_label = tk.Label(
            player_info_green,
            text="Green Team",
            font=("Arial", 12, "bold"),
            fg="#ffffff",
            bg="#0b0b0b",
        )
        player_green_label.pack(fill=tk.X)
        
        for green_player in self.players_green:
            row = tk.Frame(player_info_green, bg="#0b0b0b")
            row.pack(fill=tk.X, padx=10, pady=5)

            player_name= Label(
                row, 
                text=green_player['name'],
                font=("Ariel", 12, "bold"),
                fg="#51ff7a", 
                bg="#0b0b0b", 
            )
            player_name.pack(side=tk.LEFT)
            player_score = Label(
                row, 
                text=green_player['score'], 
                font=("Ariel", 12, "bold"),
                fg="#51ff7a", 
                bg="#0b0b0b", 
            )
            player_score.pack(side=tk.RIGHT)
        
        # game action
        game_action_frame = tk.Frame(self.full_frame, bg="#0b0b0b")
        game_action_frame.pack(fill=tk.BOTH, expand=True, padx=4, pady=(0,4))
        game_action_header = tk.Label(
            game_action_frame,
            text="Game Action",
            font=("Arial", 16, "bold"),
            fg="#ffffff",
            bg="#0b0b0b",
        )
        game_action_header.pack(fill=tk.X)
        
        # timer
        timer_frame = tk.Frame(self.full_frame, bg="#0b0b0b")
        timer_frame.pack(fill=tk.X, padx=4, pady=(0,4))
        timer_label = tk.Label(
            timer_frame,
            text=f"Time Remaining: {60}",
            font=("Arial", 12, "bold"),
            fg="#ffffff",
            bg="#0b0b0b",
        )
        timer_label.pack(side="right", padx=16)

        # Countdown
        self.countdown_frame = tk.Frame(self.full_frame, bg="#0b0b0b", width=586, height=445)
        self.countdown_frame.pack(side="top", padx=16)
        self.countdown_frame.place(relx= 0.5, rely=0.5, anchor= tk.CENTER)

        # CD Background
        countdown_bg_img = self.countdown_imgs[31]
        countdown_label_bg = tk.Label(self.countdown_frame, image = countdown_bg_img)
        countdown_label_bg.place(relx= 0.5, rely=0.5, anchor= tk.CENTER)

        # CD Foreground
        countdown_fg_img = self.countdown_imgs[30]
        self.countdown_label_fg = tk.Label(self.countdown_frame, image = countdown_fg_img, borderwidth= 0, highlightthickness= 0)
        self.countdown_label_fg.place(relx= 0.501, rely=0.585, anchor= tk.CENTER)

    def _run_countdown(self, index) -> None:
        # Update countdown image
        self.countdown_label_fg.config(image=self.countdown_images[index])
        if index > 0:
            # Schedule next countdown 
            self.root.after(1000, lambda: self._run_countdown(index - 1))
        else:
            # Hide countdown
            self.countdown_frame.hide()
            # Start game timer
            # TODO : implement game timer
