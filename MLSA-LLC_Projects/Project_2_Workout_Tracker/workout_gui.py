# Workout Tracker Pro
# Enhanced Tkinter GUI with navigation, CSV persistence, workout history, and performance tracking.
import csv
import os
from datetime import datetime
import tkinter as tk
from tkinter import messagebox, ttk

DATA_FILE = "workout_data.csv"

class WorkoutTracker:
    def __init__(self, master):
        self.master = master
        self.master.title("Workout Tracker Pro")
        self.master.configure(bg="#12172b")
        self.master.geometry("1200x800")
        self.master.resizable(True, True)
        self.master.state('zoomed')

        self.exercises = []
        self.load_data()
        self.create_widgets()
        self.show_frame(self.tracker_frame)
        self.update_summary()

    def create_widgets(self):
        title_frame = tk.Frame(self.master, bg="#12172b")
        title_frame.pack(fill="x", padx=20, pady=(20, 5))

        title_label = tk.Label(
            title_frame,
            text="WORKOUT TRACKER",
            fg="#f7f7ff",
            bg="#12172b",
            font=("Segoe UI", 22, "bold"),
        )
        title_label.pack(anchor="w")

        subtitle_label = tk.Label(
            title_frame,
            text="Log exercises, track reps, save CSV history, and analyze your best performance.",
            fg="#b8bedd",
            bg="#12172b",
            font=("Segoe UI", 10),
        )
        subtitle_label.pack(anchor="w", pady=(4, 0))

        self.nav_frame = tk.Frame(self.master, bg="#141a31")
        self.nav_frame.pack(fill="x", padx=20, pady=10)

        nav_buttons = [
            ("Tracker", self.show_tracker),
            ("History", self.show_history_tab),
            ("Performance", self.show_performance),
        ]
        for text, command in nav_buttons:
            button = tk.Button(
                self.nav_frame,
                text=text,
                command=command,
                fg="#ffffff",
                bg="#30395d",
                activebackground="#4f5f8b",
                activeforeground="#ffffff",
                relief="flat",
                padx=24,
                pady=10,
                font=("Segoe UI", 10, "bold"),
            )
            button.pack(side="left", padx=8, pady=8)

        self.content_frame = tk.Frame(self.master, bg="#13182f")
        self.content_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        self.tracker_frame = tk.Frame(self.content_frame, bg="#13182f")
        self.history_frame = tk.Frame(self.content_frame, bg="#13182f")
        self.performance_frame = tk.Frame(self.content_frame, bg="#13182f")

        self.create_tracker_tab()
        self.create_history_tab()
        self.create_performance_tab()

        self.status_label = tk.Label(
            self.master,
            text="Ready to log your next workout.",
            fg="#cfd6f1",
            bg="#12172b",
            font=("Segoe UI", 9),
        )
        self.status_label.pack(fill="x", padx=20, pady=(0, 14))

    def create_tracker_tab(self):
        form_frame = tk.Frame(self.tracker_frame, bg="#1b2346", bd=0, relief="ridge")
        form_frame.place(relx=0.02, rely=0.05, relwidth=0.46, relheight=0.9)

        step_label = tk.Label(
            form_frame,
            text="Track a workout session",
            fg="#e8f1ff",
            bg="#1b2346",
            font=("Segoe UI", 14, "bold"),
        )
        step_label.pack(anchor="nw", padx=20, pady=(16, 10))

        fields = [
            ("Exercise", "Enter exercise name"),
            ("Sets", "E.g. 3"),
            ("Reps", "E.g. 12"),
        ]
        self.entries = {}
        for label, placeholder in fields:
            frame = tk.Frame(form_frame, bg="#1b2346")
            frame.pack(fill="x", padx=20, pady=8)
            tk.Label(
                frame,
                text=label,
                fg="#d3d9ec",
                bg="#1b2346",
                font=("Segoe UI", 10, "bold"),
            ).pack(anchor="w")
            entry = tk.Entry(
                frame,
                font=("Segoe UI", 11),
                fg="#9aa6d6",
                bg="#2f3c6b",
                insertbackground="#ffffff",
                relief="flat",
            )
            entry.placeholder = placeholder
            entry.pack(fill="x", pady=6, ipady=8)
            entry.insert(0, placeholder)
            entry.bind("<FocusIn>", lambda event, e=entry, p=placeholder: self._clear_placeholder(event, e, p))
            entry.bind("<FocusOut>", lambda event, e=entry, p=placeholder: self._restore_placeholder(event, e, p))
            entry.bind("<KeyRelease>", self.update_add_button_state)
            self.entries[label.lower()] = entry

        button_frame = tk.Frame(form_frame, bg="#1b2346")
        button_frame.pack(fill="x", padx=20, pady=18)

        self.add_button = tk.Button(
            button_frame,
            text="Log Workout",
            command=self.add_exercise,
            bg="#67c3ff",
            fg="#0f1a33",
            font=("Segoe UI", 10, "bold"),
            relief="flat",
            padx=20,
            pady=10,
            state="normal",
        )
        self.add_button.pack(side="left", expand=True, fill="x", padx=(0, 10))

        clear_button = tk.Button(
            button_frame,
            text="Clear Fields",
            command=self.clear_inputs,
            bg="#444f72",
            fg="#f1f5ff",
            font=("Segoe UI", 10, "bold"),
            relief="flat",
            padx=20,
            pady=10,
        )
        clear_button.pack(side="left", expand=True, fill="x")

        quick_frame = tk.Frame(form_frame, bg="#1b2346")
        quick_frame.pack(fill="x", padx=20, pady=(0, 10))
        tk.Label(
            quick_frame,
            text="Quick logs:",
            fg="#d3d9ec",
            bg="#1b2346",
            font=("Segoe UI", 9, "italic"),
        ).pack(anchor="w")
        quick_grid = tk.Frame(quick_frame, bg="#1b2346")
        quick_grid.pack(fill="x", pady=6)
        sample_logs = [
            ("Push Ups", "3", "15"),
            ("Squats", "4", "12"),
            ("Plank", "1", "60"),
        ]
        for exercise, sets, reps in sample_logs:
            button = tk.Button(
                quick_grid,
                text=f"{exercise} {sets}x{reps}",
                command=lambda e=exercise, s=sets, r=reps: self.fill_quick_log(e, s, r),
                bg="#28355c",
                fg="#d3d9ec",
                relief="flat",
                padx=8,
                pady=8,
                font=("Segoe UI", 8, "bold"),
            )
            button.pack(side="left", padx=4, pady=4)

        info_frame = tk.Frame(form_frame, bg="#1b2346")
        info_frame.pack(fill="x", padx=20, pady=10)
        info_text = (
            "Use the Workout tab to log exercise name, sets, and reps. "
            "The History tab shows saved sessions. Your best performance is calculated automatically."
        )
        tk.Label(
            info_frame,
            text=info_text,
            wraplength=320,
            justify="left",
            fg="#b8c2e4",
            bg="#1b2346",
            font=("Segoe UI", 9),
        ).pack()

        summary_frame = tk.Frame(self.tracker_frame, bg="#171f42", bd=0, relief="ridge")
        summary_frame.place(relx=0.51, rely=0.05, relwidth=0.47, relheight=0.9)

        summary_title = tk.Label(
            summary_frame,
            text="Workout Summary",
            fg="#f7f7ff",
            bg="#171f42",
            font=("Segoe UI", 14, "bold"),
        )
        summary_title.pack(anchor="nw", padx=20, pady=(16, 10))

        self.summary_labels = {}
        metrics = [
            "Total Sessions",
            "Total Sets Logged",
            "Total Reps Logged",
            "Largest Volume",
            "Top Exercise",
        ]
        for metric in metrics:
            label = tk.Label(
                summary_frame,
                text=f"{metric}: —",
                fg="#d7def5",
                bg="#171f42",
                font=("Segoe UI", 11),
            )
            label.pack(anchor="w", padx=20, pady=8)
            self.summary_labels[metric] = label

        save_note = tk.Label(
            summary_frame,
            text="Saved to workout_data.csv",
            fg="#8fa4d3",
            bg="#171f42",
            font=("Segoe UI", 8, "italic"),
        )
        save_note.pack(anchor="w", padx=20, pady=(20, 0))

    def create_history_tab(self):
        tk.Label(
            self.history_frame,
            text="Workout History",
            fg="#f7f7ff",
            bg="#13182f",
            font=("Segoe UI", 16, "bold"),
        ).pack(anchor="nw", padx=18, pady=(18, 10))

        table_frame = tk.Frame(self.history_frame, bg="#1c2444")
        table_frame.place(relx=0.02, rely=0.13, relwidth=0.96, relheight=0.8)

        columns = ("timestamp", "exercise", "sets", "reps", "volume")
        self.history_table = ttk.Treeview(
            table_frame,
            columns=columns,
            show="headings",
            selectmode="browse",
            height=14,
        )
        for col in columns:
            self.history_table.heading(col, text=col.title())
            self.history_table.column(col, anchor="center")
        self.history_table.column("timestamp", width=200)

        style = ttk.Style()
        style.theme_use("default")
        style.configure(
            "Treeview",
            background="#1c2444",
            foreground="#f3f5ff",
            fieldbackground="#1c2444",
            rowheight=26,
            font=("Segoe UI", 10),
        )
        style.map("Treeview", background=[("selected", "#5361a2")])

        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.history_table.yview)
        self.history_table.configure(yscroll=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        self.history_table.pack(fill="both", expand=True, padx=12, pady=12)

        history_actions = tk.Frame(self.history_frame, bg="#13182f")
        history_actions.pack(anchor="nw", padx=18, pady=(10, 0))

        self.history_count_label = tk.Label(
            history_actions,
            text="Entries: 0",
            fg="#cfd6f1",
            bg="#13182f",
            font=("Segoe UI", 10),
        )
        self.history_count_label.pack(side="left")

        clear_button = tk.Button(
            history_actions,
            text="Clear History",
            command=self.clear_history,
            bg="#942626",
            fg="#ffffff",
            relief="flat",
            padx=14,
            pady=8,
            font=("Segoe UI", 9, "bold"),
        )
        clear_button.pack(side="right")

    def create_performance_tab(self):
        tk.Label(
            self.performance_frame,
            text="Performance Insight",
            fg="#f7f7ff",
            bg="#13182f",
            font=("Segoe UI", 16, "bold"),
        ).pack(anchor="nw", padx=18, pady=(18, 10))

        cards_frame = tk.Frame(self.performance_frame, bg="#13182f")
        cards_frame.place(relx=0.02, rely=0.13, relwidth=0.96, relheight=0.82)

        card_data = [
            ("Best Exercise", "No data yet"),
            ("Best Volume", "—"),
            ("Best Reps In A Set", "—"),
            ("Average Volume", "—"),
        ]
        self.performance_cards = {}
        for idx, (title, value) in enumerate(card_data):
            card = tk.Frame(cards_frame, bg="#1d2553", bd=0, relief="flat")
            card.place(relx=0.02 + (idx % 2) * 0.48, rely=0.02 + (idx // 2) * 0.48, relwidth=0.46, relheight=0.45)
            tk.Label(
                card,
                text=title,
                fg="#d9e2ff",
                bg="#1d2553",
                font=("Segoe UI", 11, "bold"),
            ).pack(anchor="nw", padx=18, pady=(18, 6))
            value_label = tk.Label(
                card,
                text=value,
                fg="#ffffff",
                bg="#1d2553",
                font=("Segoe UI", 20, "bold"),
                wraplength=300,
                justify="left",
            )
            value_label.pack(anchor="nw", padx=18)
            self.performance_cards[title] = value_label

    def show_frame(self, frame):
        for widget in (self.tracker_frame, self.history_frame, self.performance_frame):
            widget.place_forget()
        frame.place(relx=0, rely=0, relwidth=1, relheight=1)

    def show_tracker(self):
        self.show_frame(self.tracker_frame)
        self.update_add_button_state()
        self.set_status("Tracker view active.")

    def show_history_tab(self):
        self.show_frame(self.history_frame)
        self.refresh_history_view()
        self.set_status("Review your workout history.")

    def show_performance(self):
        self.show_frame(self.performance_frame)
        self.update_summary()
        self.set_status("Performance insights loaded.")

    def _clear_placeholder(self, event, entry, placeholder):
        if entry.get() == placeholder:
            entry.delete(0, tk.END)
            entry.config(fg="#ffffff")

    def _restore_placeholder(self, event, entry, placeholder):
        if not entry.get():
            entry.insert(0, placeholder)
            entry.config(fg="#9aa6d6")
        self.update_add_button_state()

    def update_add_button_state(self, event=None):
        is_ready = True
        for entry in self.entries.values():
            value = entry.get().strip()
            if not value or value == getattr(entry, "placeholder", ""):
                is_ready = False
                break
        if hasattr(self, "add_button"):
            self.add_button.config(state="normal" if is_ready else "disabled")

    def fill_quick_log(self, exercise, sets, reps):
        for key, value in (("exercise", exercise), ("sets", sets), ("reps", reps)):
            entry = self.entries[key]
            entry.delete(0, tk.END)
            entry.insert(0, value)
            entry.config(fg="#ffffff")
        self.update_add_button_state()
        self.set_status(f"Loaded quick log for {exercise}.")

    def clear_inputs(self):
        for entry in self.entries.values():
            entry.delete(0, tk.END)
            entry.insert(0, entry.placeholder)
            entry.config(fg="#9aa6d6")
        self.update_add_button_state()
        self.set_status("Input fields cleared.")

    def add_exercise(self):
        exercise = self.entries["exercise"].get().strip()
        sets = self.entries["sets"].get().strip()
        reps = self.entries["reps"].get().strip()

        if (
            not exercise
            or exercise == self.entries["exercise"].placeholder
            or not sets
            or sets == self.entries["sets"].placeholder
            or not reps
            or reps == self.entries["reps"].placeholder
        ):
            messagebox.showerror("Validation Error", "Please enter a valid exercise name, sets, and reps.")
            return

        try:
            sets = int(sets)
            reps = int(reps)
            if sets <= 0 or reps <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Validation Error", "Sets and reps must be positive whole numbers.")
            return

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
        volume = sets * reps
        self.exercises.append({
            "timestamp": timestamp,
            "exercise": exercise,
            "sets": sets,
            "reps": reps,
            "volume": volume,
        })
        self.save_data()
        self.refresh_history_view()
        self.update_summary()
        self.clear_inputs()
        self.set_status(f"Logged {exercise} — {sets} sets of {reps} reps.")

    def refresh_history_view(self):
        for row in self.history_table.get_children():
            self.history_table.delete(row)
        for entry in self.exercises:
            self.history_table.insert(
                "",
                tk.END,
                values=(
                    entry["timestamp"],
                    entry["exercise"],
                    entry["sets"],
                    entry["reps"],
                    entry["volume"],
                ),
            )
        self.history_count_label.config(text=f"Entries: {len(self.exercises)}")

    def update_summary(self):
        total_sessions = len(self.exercises)
        total_sets = sum(entry["sets"] for entry in self.exercises)
        total_reps = sum(entry["reps"] for entry in self.exercises)
        best_volume = max((entry["volume"] for entry in self.exercises), default=0)

        exercise_counts = {}
        for entry in self.exercises:
            exercise = entry["exercise"]
            exercise_counts[exercise] = exercise_counts.get(exercise, 0) + 1
        top_exercise = max(exercise_counts, key=exercise_counts.get) if exercise_counts else "—"
        average_volume = round(sum(entry["volume"] for entry in self.exercises) / total_sessions, 1) if total_sessions else 0

        self.summary_labels["Total Sessions"].config(text=f"Total Sessions: {total_sessions}")
        self.summary_labels["Total Sets Logged"].config(text=f"Total Sets Logged: {total_sets}")
        self.summary_labels["Total Reps Logged"].config(text=f"Total Reps Logged: {total_reps}")
        self.summary_labels["Largest Volume"].config(text=f"Largest Volume: {best_volume}")
        self.summary_labels["Top Exercise"].config(text=f"Top Exercise: {top_exercise}")

        best_exercise = self.compute_best_exercise()
        self.performance_cards["Best Exercise"].config(text=best_exercise)
        self.performance_cards["Best Volume"].config(text=str(best_volume))
        self.performance_cards["Best Reps In A Set"].config(text=self.compute_best_reps())
        self.performance_cards["Average Volume"].config(text=f"{average_volume}")

    def compute_best_exercise(self):
        if not self.exercises:
            return "No data yet"
        best_entry = max(self.exercises, key=lambda entry: entry["volume"])
        return f"{best_entry['exercise']} ({best_entry['sets']}x{best_entry['reps']})"

    def compute_best_reps(self):
        if not self.exercises:
            return "—"
        return str(max(entry["reps"] for entry in self.exercises))

    def clear_history(self):
        if not self.exercises:
            self.set_status("History is already empty.")
            return
        answer = messagebox.askyesno(
            "Confirm Clear",
            "This will delete all saved workout history. Continue?",
        )
        if answer:
            self.exercises = []
            self.save_data()
            self.refresh_history_view()
            self.update_summary()
            self.set_status("Workout history cleared.")

    def set_status(self, message):
        self.status_label.config(text=message)

    def save_data(self):
        with open(DATA_FILE, "w", newline="") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=["timestamp", "exercise", "sets", "reps", "volume"])
            writer.writeheader()
            writer.writerows(self.exercises)

    def load_data(self):
        if not os.path.exists(DATA_FILE):
            self.exercises = []
            return
        with open(DATA_FILE, "r", newline="") as csvfile:
            reader = csv.DictReader(csvfile)
            self.exercises = [
                {
                    "timestamp": row["timestamp"],
                    "exercise": row["exercise"],
                    "sets": int(row["sets"]),
                    "reps": int(row["reps"]),
                    "volume": int(row["volume"]),
                }
                for row in reader
                if row.get("exercise")
            ]

if __name__ == "__main__":
    root = tk.Tk()
    app = WorkoutTracker(root)
    root.mainloop()

