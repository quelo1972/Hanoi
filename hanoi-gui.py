#!/usr/bin/python3
import tkinter as tk
from tkinter import messagebox
import time

class HanoiGame:

    def __init__(self, root):
        self.root = root
        self.root.title("Torre di Hanoi - Versione Python")

        # Parametri
        self.num_disks = 4
        self.towers = [[], [], []]
        self.move_count = 0
        self.delay = 500
        self.selected_tower = None
        self.auto_mode = False

        # timing
        self.start_time = None
        self.timer_running = False

        self.colors = ["red","orange","yellow","green","cyan",
                       "blue","purple","brown","pink","magenta"]
        self.tower_centers = [150, 300, 450]

        self.build_ui()
        self.init_towers()
        self.draw()

    # ---------------- UI ----------------

    def build_ui(self):
        top = tk.Frame(self.root)
        top.pack(side="top")

        tk.Label(top, text="Dischi:").pack(side="left")

        self.disk_entry = tk.Entry(top, width=5)
        self.disk_entry.insert(0, str(self.num_disks))
        self.disk_entry.pack(side="left")

        tk.Button(top, text="Start Auto",
                  command=self.start_auto).pack(side="left")

        tk.Button(top, text="Reset",
                  command=self.reset_game).pack(side="left")

        tk.Label(top, text="Velocità").pack(side="left")

        self.speed = tk.Scale(top, from_=100, to=1000,
                              orient="horizontal",
                              command=self.update_delay)
        self.speed.set(self.delay)
        self.speed.pack(side="left")

        self.move_label = tk.Label(top, text="Mosse: 0")
        self.move_label.pack(side="left")

        self.min_label = tk.Label(top, text="Minime: 0")
        self.min_label.pack(side="left")

        # Timer display
        self.time_label = tk.Label(top, text="Tempo: 0.00s")
        self.time_label.pack(side="left")

        self.canvas = tk.Canvas(self.root,
                                width=600,
                                height=400,
                                bg="white")
        self.canvas.pack()

        self.canvas.bind("<Button-1>", self.handle_click)

    def update_delay(self, val):
        self.delay = int(val)

    # ---------------- LOGICA ----------------

    def init_towers(self):
        self.towers = [[], [], []]
        for i in range(self.num_disks, 0, -1):
            self.towers[0].append(i)

        self.move_count = 0
        self.selected_tower = None
        self.update_labels()

    def update_labels(self):
        self.move_label.config(text=f"Mosse: {self.move_count}")
        min_moves = 2**self.num_disks - 1
        self.min_label.config(text=f"Minime: {min_moves}")

    # ---------------- TIMER ----------------

    def start_timer(self):
        if not self.timer_running:
            self.start_time = time.time()
            self.timer_running = True
            self.update_timer()

    def update_timer(self):
        if self.timer_running and self.start_time is not None:
            elapsed = time.time() - self.start_time
            self.time_label.config(text=f"Tempo: {elapsed:.2f}s")
            self.root.after(100, self.update_timer)

    def stop_timer(self):
        self.timer_running = False

    def draw(self):
        self.canvas.delete("all")

        for t in range(3):

            pole_color = "red" if self.selected_tower == t else "black"

            # Palo
            self.canvas.create_rectangle(
                self.tower_centers[t]-5, 100,
                self.tower_centers[t]+5, 300,
                fill=pole_color
            )

            # Base
            self.canvas.create_rectangle(
                self.tower_centers[t]-80, 300,
                self.tower_centers[t]+80, 310,
                fill="black"
            )

            # Dischi
            for i, disk in enumerate(self.towers[t]):
                width = disk * 15
                y = 290 - (i * 20)

                self.canvas.create_rectangle(
                    self.tower_centers[t]-width,
                    y-15,
                    self.tower_centers[t]+width,
                    y,
                    fill=self.colors[disk % len(self.colors)]
                )

    def valid_move(self, from_t, to_t):
        if not self.towers[from_t]:
            return False
        if not self.towers[to_t]:
            return True
        return self.towers[from_t][-1] < self.towers[to_t][-1]

    def move_disk(self, from_t, to_t):
        if not self.valid_move(from_t, to_t):
            return

        # start timer on first move (manual play)
        if not self.timer_running:
            self.start_timer()

        disk = self.towers[from_t].pop()
        self.towers[to_t].append(disk)

        self.move_count += 1
        self.update_labels()
        self.draw()
        self.check_win()

    def check_win(self):
        for i in (1, 2):  # torri diverse da 0
            if len(self.towers[i]) == self.num_disks:
                min_moves = 2**self.num_disks - 1
                # compute elapsed time if available
                elapsed = 0.0
                if self.start_time is not None:
                    elapsed = time.time() - self.start_time
                messagebox.showinfo(
                    "Vittoria!",
                    f"Hai completato la torre!\n\n"
                    f"Mosse: {self.move_count}\n"
                    f"Minimo teorico: {min_moves}\n"
                    f"Tempo: {elapsed:.2f}s"
                )
                self.auto_mode = True
                self.stop_timer()
                return

    # ---------------- CLICK ----------------

    def handle_click(self, event):
        if self.auto_mode:
            return

        x = event.x
        tower = None

        for i in range(3):
            if abs(x - self.tower_centers[i]) < 80:
                tower = i
                break

        if tower is None:
            return

        if self.selected_tower is None:
            if self.towers[tower]:
                self.selected_tower = tower
        else:
            self.move_disk(self.selected_tower, tower)
            self.selected_tower = None

        self.draw()

    # ---------------- AUTO ----------------

    def hanoi_auto(self, n, from_t, to_t, aux):
        if n == 0:
            return

        self.hanoi_auto(n-1, from_t, aux, to_t)
        self.move_disk(from_t, to_t)
        self.root.update()
        time.sleep(self.delay / 1000)
        self.hanoi_auto(n-1, aux, to_t, from_t)

    def start_auto(self):
        self.auto_mode = True

        try:
            n = int(self.disk_entry.get())
            if n <= 0 or n > 10:
                return
            self.num_disks = n
        except:
            return

        self.init_towers()
        self.draw()
        # start timing for auto mode
        self.start_timer()

        self.root.after(500, lambda:
                        self.hanoi_auto(self.num_disks, 0, 2, 1))

    def reset_game(self):
        self.auto_mode = False
        try:
            self.num_disks = int(self.disk_entry.get())
        except:
            self.num_disks = 4

        # reset timer
        self.start_time = None
        self.timer_running = False
        self.time_label.config(text="Tempo: 0.00s")

        self.init_towers()
        self.draw()


# ---------------- AVVIO ----------------

root = tk.Tk()
game = HanoiGame(root)
root.mainloop()
