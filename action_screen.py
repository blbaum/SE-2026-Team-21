import tkinter as tk
from tkinter import *
from udp_files.udp import RED_SCORE_CODE, GREEN_SCORE_CODE

import PIL.Image
import PIL.ImageTk

from pygame import mixer ## Music lib
import random
import os
import threading
import socket

SCREEN_WIDTH = 1100
SCREEN_HEIGHT = 680
BASE_DIR = os.path.dirname(__file__)
GAME_DURATION = 360

def select_random_track():
    tracks = [
        os.path.join(BASE_DIR, "photon_tracks", f"Track0{i}.mp3")
        for i in range(1, 9)
    ]
    return random.choice(tracks)

def play_random_track():
    if mixer.music.get_busy():
        return

    try:
        track = select_random_track()
        mixer.music.load(track)
        mixer.music.set_volume(0.5)
        mixer.music.play()
    except Exception as e:
        print(f"Music error: {e}")

class ActionScreen:

    def __init__(self, root: tk.Tk, udp, entry_terminal=None):

        self.root = root
        self.entry_terminal = entry_terminal
        self.udp = udp
        mixer.pre_init(44100, -16, 2, 512)
        mixer.init() 

        self.root.title("Action Screen")
        self.root.geometry(f"{SCREEN_WIDTH}x{SCREEN_HEIGHT}")
        self.root.minsize(980, 680)
        self.root.configure(bg="#0b0b0b")

        self.players_green = []
        self.players_red = []

        # game state
        self.game_active = False
        self.receive_thread = None
        self.players_hardware = {}
        self.players_team = {}

        # countdown system
        self.countdown_imgs = []
        self.countdown_id = None
        self.time_remaining = GAME_DURATION
        self.timer_label = None

        # frames
        self.full_frame = None
        self.player_info_red = None
        self.player_info_green = None
        self.countdown_frame = None
        self.countdown_label_fg = None
        self.game_action_frame = None
        self.game_action_feed = None

        self._load_countdown_images()
        self._build_ui()
        self.sync_from_entry()

    def _load_countdown_images(self):

        for i in range(31):
            img = PIL.Image.open(f"countdown_images/{i}.tif")
            self.countdown_imgs.append(PIL.ImageTk.PhotoImage(img))

        bg = PIL.Image.open("countdown_images/background.tif")
        alert = PIL.Image.open("countdown_images/alert-on.tif")

        self.countdown_imgs.append(PIL.ImageTk.PhotoImage(bg))     # index 31
        self.countdown_imgs.append(PIL.ImageTk.PhotoImage(alert))  # index 32

    def hide(self) -> None:

        self.full_frame.pack_forget()
        self.game_active = False

        if self.countdown_id:
            self.root.after_cancel(self.countdown_id)
            self.countdown_id = None

        mixer.music.stop()

    def show(self) -> None:

        self.sync_from_entry()

        self.full_frame.pack(fill=tk.BOTH, expand=True, padx=4, pady=4)

        if self.countdown_frame:
            self.countdown_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

        self._run_countdown(5)

    def set_entry_terminal(self, entry_terminal) -> None:

        self.entry_terminal = entry_terminal
        self.sync_from_entry()

    def sync_from_entry(self) -> None:

        if self.entry_terminal is None:
            return

        entries = self.entry_terminal.get_entries()
        hardware_ids = self.entry_terminal.get_hardware_ids()

        red_players = []
        green_players = []

        for team_name, slot, player_id, codename in entries:

            player_id = str(player_id).strip()
            codename = str(codename).strip()

            display_name = codename if codename else player_id
            equipment_id = hardware_ids.get((player_id, codename), "")

            player = {
                'name': display_name if display_name else f"Player {slot}",
                'id': player_id,
                'equipment_id': equipment_id,
                'score': 0,
                'slot': slot,
            }

            if team_name == "Red":
                red_players.append(player)

            elif team_name == "Green":
                green_players.append(player)

        self.players_red = sorted(red_players, key=lambda player: player['slot'])
        self.players_green = sorted(green_players, key=lambda player: player['slot'])
        
        self._render_player_lists()

    def _render_player_lists(self) -> None:

        if self.player_info_red is None or self.player_info_green is None:
            return

        for widget in self.player_info_red.winfo_children():
            if getattr(widget, "is_team_header", False):
                continue
            widget.destroy()

        for widget in self.player_info_green.winfo_children():
            if getattr(widget, "is_team_header", False):
                continue
            widget.destroy()

        if not self.players_red:

            empty_red = Label(
                self.player_info_red,
                text="No red team players",
                font=("Arial", 11),
                fg="#c8a6a6",
                bg="#0b0b0b",
            )

            empty_red.pack(fill=tk.X, padx=10, pady=6)

        else:

            for red_player in self.players_red:

                row = tk.Frame(self.player_info_red, bg="#0b0b0b")
                row.pack(fill=tk.X, padx=10, pady=5)

                player_name = Label(
                    row,
                    text=red_player['name'],
                    font=("Ariel", 12, "bold"),
                    fg="#ff4b4b",
                    bg="#0b0b0b",
                )

                player_name.pack(side=LEFT)

                player_score = Label(
                    row,
                    text=red_player['score'],
                    font=("Ariel", 12, "bold"),
                    fg="#ff4b4b",
                    bg="#0b0b0b",
                )

                player_score.pack(side=RIGHT)

        if not self.players_green:

            empty_green = Label(
                self.player_info_green,
                text="No green team players",
                font=("Arial", 11),
                fg="#a7cfb2",
                bg="#0b0b0b",
            )

            empty_green.pack(fill=tk.X, padx=10, pady=6)

        else:

            for green_player in self.players_green:

                row = tk.Frame(self.player_info_green, bg="#0b0b0b")
                row.pack(fill=tk.X, padx=10, pady=5)

                player_name = Label(
                    row,
                    text=green_player['name'],
                    font=("Ariel", 12, "bold"),
                    fg="#51ff7a",
                    bg="#0b0b0b",
                )

                player_name.pack(side=LEFT)

                player_score = Label(
                    row,
                    text=green_player['score'],
                    font=("Ariel", 12, "bold"),
                    fg="#51ff7a",
                    bg="#0b0b0b",
                )

                player_score.pack(side=RIGHT)

    def _build_ui(self) -> None:

        # yellow border
        self.full_frame = tk.Frame(self.root, bg="#FFD355")
        self.full_frame.pack(fill=tk.BOTH, expand=True, padx=4, pady=4)

        # main frame
        player_frame = tk.Frame(self.full_frame, bg="#0b0b0b")
        player_frame.pack(fill=tk.BOTH, expand=True, padx=4, pady=4)

        player_frame_header = tk.Frame(player_frame, bg="#0b0b0b")
        player_frame_header.pack(fill=tk.BOTH)

        current_score_header = tk.Label(
            player_frame_header,
            text="Current Scores",
            font=("Arial", 16, "bold"),
            fg="#ffffff",
            bg="#0b0b0b",
        )

        current_score_header.pack(fill=tk.X)

        # red team
        self.player_info_red = tk.Frame(player_frame, bg="#0b0b0b")
        self.player_info_red.pack(fill=tk.BOTH, side=tk.LEFT, expand=True, padx=4)

        player_red_label = tk.Label(
            self.player_info_red,
            text="Red Team",
            font=("Arial", 12, "bold"),
            fg="#ffffff",
            bg="#0b0b0b",
        )

        player_red_label.pack(fill=tk.X)
        player_red_label.is_team_header = True

        # green team
        self.player_info_green = tk.Frame(player_frame, bg="#0b0b0b")
        self.player_info_green.pack(fill=tk.BOTH, side=tk.RIGHT, expand=True, padx=4)

        player_green_label = tk.Label(
            self.player_info_green,
            text="Green Team",
            font=("Arial", 12, "bold"),
            fg="#ffffff",
            bg="#0b0b0b",
        )

        player_green_label.pack(fill=tk.X)
        player_green_label.is_team_header = True

        # game action
        self.game_action_frame = tk.Frame(self.full_frame, bg="#0b0b0b")
        self.game_action_frame.pack(fill=tk.BOTH, expand=True, padx=4, pady=(0, 4))

        game_action_header = tk.Label(
            self.game_action_frame,
            text="Game Action",
            font=("Arial", 16, "bold"),
            fg="#ffffff",
            bg="#0b0b0b",
        )
        game_action_header.pack(fill=tk.X)

        # timer
        timer_frame = tk.Frame(self.full_frame, bg="#0b0b0b")
        timer_frame.pack(fill=tk.X, padx=4, pady=(0, 4))

        self.timer_label = tk.Label(
            timer_frame,
            text=f"Time Remaining: 00:00",
            font=("Arial", 12, "bold"),
            fg="#ffffff",
            bg="#0b0b0b",
        )

        self.timer_label.pack(side="right", padx=16)

        # countdown overlay
        self.countdown_frame = tk.Frame(self.full_frame, bg="#0b0b0b", width=586, height=445)

        self.countdown_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

        bg_label = tk.Label(
            self.countdown_frame,
            image=self.countdown_imgs[31],
            borderwidth=0
        )

        bg_label.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
        bg_label.image = self.countdown_imgs[31]

        self.countdown_label_fg = tk.Label(
            self.countdown_frame,
            image=self.countdown_imgs[30],
            borderwidth=0,
            highlightthickness=0
        )

        self.countdown_label_fg.place(relx=0.501, rely=0.585, anchor=tk.CENTER)
        self.countdown_label_fg.image = self.countdown_imgs[30]

        self._render_player_lists()

    def _build_action_feed(self, ):
        self.game_action_feed = tk.Frame(self.game_action_frame, bg="#0b0b0b")
        self.game_action_feed(fill= tk.X, padx = 10, pady=5)
        feed = []

        return

    def _run_game_timer(self):
        if(self.time_remaining >= 0):
            self.timer_label.config(text=f"Time Remaining: {int(self.time_remaining / 60):02d}:{self.time_remaining % 60:02d}")
            self.time_remaining -= 1
            self.root.after(1000, self._run_game_timer)
        else:
            self.game_active = False
            self.udp.send_end_code()
            mixer.music.stop()

    def _run_countdown(self, index):
        if index >= 0:
            img = self.countdown_imgs[index]

            self.countdown_label_fg.config(image=img)
            self.countdown_label_fg.image = img

            if index == 17: 
                play_random_track()

            self.countdown_id = self.root.after(
                1000,
                lambda: self._run_countdown(index - 1)
            )
        else:
            self.countdown_frame.destroy()
            self._build_equipment_map()
            self.game_active = True
            self.udp.send_start_code()
            self.receive_thread = threading.Thread(target=self._receive_loop, daemon=True)
            self.receive_thread.start()
            self._run_game_timer()

    def _build_equipment_map(self):
        self.players_hardware = {}
        self.players_team = {}
        # assign players to their proper equipment and team
        # based on their hardware id that they input from 
        # entry screen
        for player in self.players_red:
            equipment_id = str(player['equipment_id'])
            if equipment_id:
                self.players_hardware[equipment_id] = player
                self.players_team[equipment_id] = "red"
        for player in self.players_green:
            equipment_id = str(player['equipment_id'])
            if equipment_id:
                self.players_hardware[equipment_id] = player
                self.players_team[equipment_id] = "green"
        print(f"equip to player {self.players_hardware}")
        print(f"equip to team {self.players_team}")

    def _receive_loop(self):
        while self.game_active:
            try:
                data = self.udp.receive_sock.recvfrom(self.udp.buffer_size)
                message = data[0].decode('utf-8')
                print(f"Received hit: {message}")

                parts = message.split(":")
                if len(parts) != 2:
                    continue

                attacker_id = parts[0].strip()
                target_id = parts[1].strip()

                attacker = self.players_hardware.get(attacker_id)
                attacker_team = self.players_team.get(attacker_id)

                target = self.players_hardware.get(target_id)
                target_team = self.players_team.get(target_id)

                print(f"attacker = {attacker}, target = {target}")
                self._build_action_feed(attacker, target)

                if attacker is None:
                    continue

                if target_id == str(GREEN_SCORE_CODE):
                    # hit green base
                    attacker['score'] += 100
                    self.udp.send_data(attacker_id)
                elif target_id == str(RED_SCORE_CODE):
                    # hit red base
                    attacker['score'] += 100
                    self.udp.send_data(attacker_id)
                else:
                    target_team = self.players_team.get(target_id)
                    if attacker_team and attacker_team == target_team:
                        # friendly fire
                        attacker['score'] -= 10
                        self.udp.send_data(attacker_id)
                        self.udp.send_data(attacker_id)
                    else:
                        # normal hit
                        attacker['score'] += 10
                        self.udp.send_data(attacker_id)

                self.root.after(0, self._render_player_lists)
            except Exception as e:
                if self.game_active:
                    print(f"Receive error: {e}")