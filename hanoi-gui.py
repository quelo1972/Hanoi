#!/usr/bin/python3
import tkinter as tk
from tkinter import messagebox
import sqlite3
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
        self.game_over = False

        # timing
        self.start_time = None
        self.timer_running = False

        self.colors = ["red","orange","yellow","green","cyan",
                       "blue","purple","brown","pink","magenta"]
        self.tower_centers = [150, 300, 450]

        # persistence
        self.db_path = "hanoi.sqlite"

        self.build_ui()
        self.init_db()
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

        tk.Label(top, text="Giocatore:").pack(side="left")
        self.player_entry = tk.Entry(top, width=20)
        self.player_entry.insert(0, "Anonimo")
        self.player_entry.pack(side="left")

        tk.Button(top, text="Start Auto",
                  command=self.start_auto).pack(side="left")

        tk.Button(top, text="Reset",
                  command=self.reset_game).pack(side="left")

        tk.Button(top, text="Top 10",
                  command=self.show_top_ten).pack(side="left")

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
        self.time_label = tk.Label(top, text="Tempo: 00:00.00")
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
        self.game_over = False
        self.update_labels()

    def update_labels(self):
        self.move_label.config(text=f"Mosse: {self.move_count}")
        min_moves = 2**self.num_disks - 1
        self.min_label.config(text=f"Minime: {min_moves}")

    # ---------------- TIMER ----------------

    def format_time(self, elapsed):
        total_cs = int(elapsed * 100)
        minutes = total_cs // 6000
        seconds = (total_cs // 100) % 60
        centis = total_cs % 100
        return f"{minutes:02d}:{seconds:02d}.{centis:02d}"

    def start_timer(self):
        if not self.timer_running:
            self.start_time = time.time()
            self.timer_running = True
            self.update_timer()

    def update_timer(self):
        if self.timer_running and self.start_time is not None:
            elapsed = time.time() - self.start_time
            self.time_label.config(text=f"Tempo: {self.format_time(elapsed)}")
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
        if self.game_over:
            return

        for i in (1, 2):  # torri diverse da 0
            if len(self.towers[i]) == self.num_disks:
                min_moves = 2**self.num_disks - 1
                # compute elapsed time if available
                elapsed = 0.0
                if self.start_time is not None:
                    elapsed = time.time() - self.start_time
                # stop the timer immediately and freeze the display
                self.stop_timer()
                self.time_label.config(text=f"Tempo: {self.format_time(elapsed)}")

                player = self.get_player_name()
                tempo = self.format_time(elapsed)
                self.save_result(player, self.move_count, min_moves, tempo)
                self.game_over = True

                messagebox.showinfo(
                    "Vittoria!",
                    f"Hai completato la torre!\n\n"
                    f"Mosse: {self.move_count}\n"
                    f"Minimo teorico: {min_moves}\n"
                    f"Tempo: {self.format_time(elapsed)}"
                )
                self.auto_mode = True
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
        self.time_label.config(text="Tempo: 00:00.00")

        self.init_towers()
        self.draw()

    # ---------------- DB ----------------

    def init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS risultati (
                    giocatore TEXT NOT NULL,
                    n_mosse INTEGER NOT NULL,
                    minimo TEXT NOT NULL,
                    tempo TEXT NOT NULL
                )
                """
            )

    def ensure_table(self, num_disks):
        table = f"risultati_{num_disks}"
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                f"""
                CREATE TABLE IF NOT EXISTS {table} (
                    giocatore TEXT NOT NULL,
                    mosse INTEGER NOT NULL,
                    min_mosse INTEGER NOT NULL,
                    tempo TEXT NOT NULL
                )
                """
            )

            columns = {
                row[1]
                for row in conn.execute(f"PRAGMA table_info({table})").fetchall()
            }

            if columns != {"giocatore", "mosse", "min_mosse", "tempo"}:
                temp_table = f"{table}_v2"
                conn.execute(
                    f"""
                    CREATE TABLE IF NOT EXISTS {temp_table} (
                        giocatore TEXT NOT NULL,
                        mosse INTEGER NOT NULL,
                        min_mosse INTEGER NOT NULL,
                        tempo TEXT NOT NULL
                    )
                    """
                )

                if "n_mosse" in columns:
                    conn.execute(
                        f"""
                        INSERT INTO {temp_table} (giocatore, mosse, min_mosse, tempo)
                        SELECT giocatore, n_mosse, ?, tempo
                        FROM {table}
                        """,
                        (2**num_disks - 1,),
                    )
                elif "mosse" in columns:
                    conn.execute(
                        f"""
                        INSERT INTO {temp_table} (giocatore, mosse, min_mosse, tempo)
                        SELECT giocatore, mosse, ?, tempo
                        FROM {table}
                        """,
                        (2**num_disks - 1,),
                    )

                conn.execute(f"DROP TABLE {table}")
                conn.execute(f"ALTER TABLE {temp_table} RENAME TO {table}")
        return table

    def get_player_name(self):
        name = self.player_entry.get().strip()
        return name if name else "Anonimo"

    def save_result(self, giocatore, mosse, min_mosse, tempo):
        table = self.ensure_table(self.num_disks)
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                f"INSERT INTO {table} (giocatore, mosse, min_mosse, tempo) VALUES (?, ?, ?, ?)",
                (giocatore, mosse, min_mosse, tempo)
            )

    def show_top_ten(self):
        try:
            n = int(self.disk_entry.get())
            if n <= 0 or n > 10:
                n = self.num_disks
        except:
            n = self.num_disks

        table = self.ensure_table(n)
        with sqlite3.connect(self.db_path) as conn:
            rows = conn.execute(
                f"""
                SELECT giocatore, mosse, min_mosse, tempo
                FROM {table}
                ORDER BY
                    CASE WHEN mosse = min_mosse THEN 0 ELSE 1 END,
                    tempo ASC
                LIMIT 10
                """
            ).fetchall()

        if not rows:
            messagebox.showinfo("Top 10", "Nessun risultato salvato.")
            return

        header = f"Top 10 dischi: {n}"
        widths = {"pos": 3, "name": 22, "time": 10, "moves": 7, "min": 7}
        title = (
            f"{'#':<{widths['pos']}} | "
            f"{'Giocatore':<{widths['name']}} | "
            f"{'Tempo':<{widths['time']}} | "
            f"{'Mosse':<{widths['moves']}} | "
            f"{'Minimo':<{widths['min']}}"
        )
        sep = "".join("+" if c == "|" else "-" for c in title)
        lines = [title, sep]
        for i, (g, m, min_m, t) in enumerate(rows, start=1):
            name = g[:widths["name"] - 1]
            lines.append(
                f"{i:<{widths['pos']}} | "
                f"{name:<{widths['name']}} | "
                f"{t:<{widths['time']}} | "
                f"{m:<{widths['moves']}} | "
                f"{min_m:<{widths['min']}}"
            )

        def reset_top_ten():
            if not messagebox.askyesno(
                "Conferma reset",
                f"Vuoi svuotare la top ten per {n} dischi?",
            ):
                return
            with sqlite3.connect(self.db_path) as conn:
                conn.execute(f"DELETE FROM {table}")
            return True

        self.show_table_window(
            header,
            "\n".join(lines),
            reset_label="Reset",
            on_reset=reset_top_ten,
        )

    def show_table_window(self, title, content, reset_label=None, on_reset=None):
        win = tk.Toplevel(self.root)
        win.title(title)
        win.transient(self.root)
        win.grab_set()

        tk.Label(win, text=title, font=("Courier", 12, "bold")).pack(
            side="top", anchor="w", padx=10, pady=(10, 4)
        )
        text = tk.Text(
            win,
            font=("Courier", 11),
            width=60,
            height=12,
            padx=6,
            pady=6,
            borderwidth=0,
            wrap="none",
        )
        text.insert("1.0", content)
        text.configure(state="disabled")
        text.pack(side="top", fill="both", expand=True, padx=10, pady=(0, 10))

        if reset_label and on_reset:
            actions = tk.Frame(win)
            actions.pack(side="bottom", fill="x", padx=10, pady=(0, 10))

            def handle_reset():
                did_reset = on_reset()
                if not did_reset:
                    return
                text.configure(state="normal")
                text.delete("1.0", "end")
                text.insert("1.0", "Nessun risultato salvato.")
                text.configure(state="disabled")
                reset_btn.configure(state="disabled")

            reset_btn = tk.Button(actions, text=reset_label, command=handle_reset)
            reset_btn.pack(side="right")

# ---------------- AVVIO ----------------

root = tk.Tk()
game = HanoiGame(root)
root.mainloop()
