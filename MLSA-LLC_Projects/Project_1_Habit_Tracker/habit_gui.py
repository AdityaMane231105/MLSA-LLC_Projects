# Enhanced Habit Tracker with improved UI and additional features
# Features: Add/Delete habits, Mark habits as done, Track streaks,
# Daily completions, Statistics, Data persistence, Tabbed Navigation
import tkinter as tk
from tkinter import messagebox, ttk
import csv
import os
from datetime import datetime, timedelta
from collections import defaultdict

class HabitTracker:
    def __init__(self, master):
        self.master = master
        self.master.title("Habit Tracker Pro")
        self.master.geometry("800x700")
        self.master.configure(bg="#e8f4f8")

        # Set modern style with colors
        self.style = ttk.Style()
        self.style.theme_use('clam')

        # Configure colors
        self.style.configure('TFrame', background="#e8f4f8")
        self.style.configure('TLabelFrame', background="#e8f4f8", borderwidth=2, relief="groove")
        self.style.configure('TLabelFrame.Label', background="#e8f4f8", foreground="#2c3e50", font=('Helvetica', 10, 'bold'))

        self.style.configure('Title.TLabel', font=('Helvetica', 18, 'bold'), background="#e8f4f8", foreground="#3498db")
        self.style.configure('Header.TLabel', font=('Helvetica', 11, 'bold'), background="#e8f4f8", foreground="#34495e")
        self.style.configure('Normal.TLabel', font=('Helvetica', 10), background="#e8f4f8", foreground="#2c3e50")

        # Button styles
        self.style.configure('Primary.TButton', font=('Helvetica', 10, 'bold'), background="#3498db", foreground="white")
        self.style.map('Primary.TButton', background=[('active', '#2980b9')])

        self.style.configure('Success.TButton', font=('Helvetica', 10, 'bold'), background="#27ae60", foreground="white")
        self.style.map('Success.TButton', background=[('active', '#229954')])

        self.style.configure('Danger.TButton', font=('Helvetica', 10, 'bold'), background="#e74c3c", foreground="white")
        self.style.map('Danger.TButton', background=[('active', '#c0392b')])

        self.style.configure('Info.TButton', font=('Helvetica', 10, 'bold'), background="#f39c12", foreground="white")
        self.style.map('Info.TButton', background=[('active', '#e67e22')])

        self.habits = {}
        self.habit_dates = defaultdict(list)  # Track dates when habits were completed
        self.load_habits()
        self.create_widgets()
        self.refresh_display()
        self.update_statistics()  # Initialize stats tab

    def create_widgets(self):
        # Main container with padding
        main_frame = ttk.Frame(self.master)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)

        # Title
        title_label = ttk.Label(main_frame, text="📊 Habit Tracker Pro", style='Title.TLabel')
        title_label.pack(pady=(0, 20))

        # Create notebook (tabs)
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        # Home tab
        self.home_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.home_frame, text="🏠 Home")

        # Statistics tab
        self.stats_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.stats_frame, text="📈 Statistics")

        # About tab
        self.about_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.about_frame, text="ℹ️ About")

        # Setup each tab
        self.setup_home_tab()
        self.setup_stats_tab()
        self.setup_about_tab()

    def setup_home_tab(self):
        # Input frame
        input_frame = ttk.LabelFrame(self.home_frame, text="➕ Add New Habit", padding=15)
        input_frame.pack(fill=tk.X, pady=(10, 15))

        ttk.Label(input_frame, text="Habit Name:", style='Header.TLabel').pack(side=tk.LEFT, padx=(0, 10))
        self.habit_entry = ttk.Entry(input_frame, width=35, font=('Helvetica', 10))
        self.habit_entry.pack(side=tk.LEFT, padx=(0, 15))
        self.habit_entry.bind('<Return>', lambda e: self.add_habit())

        add_button = ttk.Button(input_frame, text="➕ Add Habit", style='Primary.TButton', command=self.add_habit)
        add_button.pack(side=tk.LEFT)

        # Quick stats
        stats_frame = ttk.LabelFrame(self.home_frame, text="📊 Quick Stats", padding=15)
        stats_frame.pack(fill=tk.X, pady=(0, 15))

        self.stats_label = ttk.Label(stats_frame, text="Total Habits: 0 | Total Streak: 0 days", style='Header.TLabel')
        self.stats_label.pack()

        # Habits frame with scrollbar
        habits_frame = ttk.LabelFrame(self.home_frame, text="🎯 Your Habits", padding=15)
        habits_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 15))

        # Create a frame for listbox and scrollbar
        listbox_container = ttk.Frame(habits_frame)
        listbox_container.pack(fill=tk.BOTH, expand=True)

        scrollbar = ttk.Scrollbar(listbox_container)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.habit_listbox = tk.Listbox(
            listbox_container,
            font=('Helvetica', 11),
            yscrollcommand=scrollbar.set,
            bg='#ffffff',
            fg='#2c3e50',
            selectmode=tk.SINGLE,
            height=12,
            selectbackground='#3498db',
            selectforeground='white'
        )
        self.habit_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.habit_listbox.yview)

        # Action buttons frame
        button_frame = ttk.Frame(self.home_frame)
        button_frame.pack(fill=tk.X, pady=(0, 10))

        mark_done_btn = ttk.Button(button_frame, text="✅ Mark as Done", style='Success.TButton', command=self.mark_done)
        mark_done_btn.pack(side=tk.LEFT, padx=(0, 8))

        reset_btn = ttk.Button(button_frame, text="🔄 Reset Streak", style='Info.TButton', command=self.reset_streak)
        reset_btn.pack(side=tk.LEFT, padx=(0, 8))

        delete_btn = ttk.Button(button_frame, text="❌ Delete", style='Danger.TButton', command=self.delete_habit)
        delete_btn.pack(side=tk.LEFT, padx=(0, 8))

        view_stats_btn = ttk.Button(button_frame, text="📈 View Detailed Stats", style='Primary.TButton', command=lambda: self.notebook.select(1))
        view_stats_btn.pack(side=tk.LEFT)

    def setup_stats_tab(self):
        # Statistics overview
        overview_frame = ttk.LabelFrame(self.stats_frame, text="📊 Overview", padding=15)
        overview_frame.pack(fill=tk.X, pady=(10, 15))

        self.overview_label = ttk.Label(overview_frame, text="", style='Header.TLabel', justify=tk.LEFT)
        self.overview_label.pack(anchor=tk.W)

        # Detailed stats frame
        details_frame = ttk.LabelFrame(self.stats_frame, text="📈 Detailed Statistics", padding=15)
        details_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 15))

        # Text widget for detailed stats
        self.stats_text = tk.Text(details_frame, font=('Helvetica', 10), bg='#ffffff', fg='#2c3e50', wrap=tk.WORD, height=15)
        scrollbar = ttk.Scrollbar(details_frame, command=self.stats_text.yview)
        self.stats_text.config(yscrollcommand=scrollbar.set)

        self.stats_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Buttons
        button_frame = ttk.Frame(self.stats_frame)
        button_frame.pack(fill=tk.X)

        refresh_btn = ttk.Button(button_frame, text="🔄 Refresh Stats", style='Primary.TButton', command=self.update_statistics)
        refresh_btn.pack(side=tk.LEFT, padx=(0, 10))

        export_btn = ttk.Button(button_frame, text="💾 Export to CSV", style='Success.TButton', command=self.export_stats)
        export_btn.pack(side=tk.LEFT)

    def setup_about_tab(self):
        about_frame = ttk.Frame(self.about_frame)
        about_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Project info
        title_label = ttk.Label(about_frame, text="🎯 Habit Tracker Pro", style='Title.TLabel')
        title_label.pack(pady=(0, 20))

        info_text = """
📝 PROJECT 1: HABIT TRACKER

🔹 Student Information
Name: YOUR NAME
Roll Number: YOUR ROLL NO
Branch & Year: CSE, Second Year
Project Title: Habit Tracker with Power BI Dashboard
Project Number: 14

🔹 Project Description
This project is a GUI-based Habit Tracker developed using Python Tkinter.
It allows users to add daily habits, mark them as completed, and maintain streak counts.
The data is stored in a CSV file and visualized using Power BI dashboards for better analysis.

🔹 Features Implemented
✓ Add new habits
✓ Mark habits as completed
✓ Display list of habits
✓ Track habit status
✓ Streak counter for each habit
✓ Save habit data into CSV file
✓ Habit streak tracking system
✓ Enhanced UI with colors and navigation
✓ Tabbed interface
✓ Detailed statistics

🔹 Technologies Used
• Python 3.x
• Tkinter (GUI)
• CSV (Data Storage)
• Power BI (Visualization)

🔹 GitHub Copilot Usage
I wrote comments like "create a tkinter habit tracker with csv saving and streak counter"
GitHub Copilot generated the base GUI structure and logic
I modified the generated code by adding streak functionality and improving the interface

For Power BI Dashboard:
1. Open habits.csv in Power BI
2. Create visualizations for streaks, completions, and trends
3. Use date fields for time-based analysis
        """

        about_text = tk.Text(about_frame, font=('Helvetica', 10), bg='#ffffff', fg='#2c3e50', wrap=tk.WORD, height=25)
        scrollbar = ttk.Scrollbar(about_frame, command=about_text.yview)
        about_text.config(yscrollcommand=scrollbar.set)

        about_text.insert(tk.END, info_text)
        about_text.config(state=tk.DISABLED)

        about_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    def add_habit(self):
        habit_name = self.habit_entry.get().strip()
        if not habit_name:
            messagebox.showwarning("Input Error", "Please enter a habit name.")
            return
        
        if habit_name in self.habits:
            messagebox.showerror("Duplicate", f"Habit '{habit_name}' already exists.")
            return
        
        self.habits[habit_name] = {
            'streak': 0,
            'last_completed': None,
            'total_completions': 0,
            'created_date': datetime.now().strftime("%Y-%m-%d")
        }
        self.habit_dates[habit_name] = []
        self.habit_entry.delete(0, tk.END)
        self.save_habits()
        self.refresh_display()
        messagebox.showinfo("Success", f"Habit '{habit_name}' added successfully!")

    def mark_done(self):
        selected = self.habit_listbox.curselection()
        if not selected:
            messagebox.showerror("Error", "Please select a habit to mark as done.")
            return
        
        habit_name = self.habit_listbox.get(selected[0]).split(" |")[0]
        today = datetime.now().strftime("%Y-%m-%d")
        
        # Check if already marked today
        if self.habit_dates[habit_name] and self.habit_dates[habit_name][-1] == today:
            messagebox.showinfo("Info", "Habit already marked as done today!")
            return
        
        self.habit_dates[habit_name].append(today)
        self.habits[habit_name]['last_completed'] = today
        self.habits[habit_name]['total_completions'] += 1
        
        # Update streak
        self.update_streak(habit_name)
        
        self.save_habits()
        self.refresh_display()
        messagebox.showinfo("Success", f"Great job! '{habit_name}' marked as done! 🎉")

    def update_streak(self, habit_name):
        """Update streak based on consecutive days"""
        dates = self.habit_dates[habit_name]
        if not dates:
            self.habits[habit_name]['streak'] = 0
            return
        
        streak = 1
        today = datetime.now().date()
        
        for i in range(len(dates) - 1, 0, -1):
            current_date = datetime.strptime(dates[i], "%Y-%m-%d").date()
            prev_date = datetime.strptime(dates[i-1], "%Y-%m-%d").date()
            
            if (current_date - prev_date).days == 1:
                streak += 1
            else:
                break
        
        # Check if streak is broken (last completion wasn't today)
        last_date = datetime.strptime(dates[-1], "%Y-%m-%d").date()
        if (today - last_date).days > 1:
            streak = 1
        
        self.habits[habit_name]['streak'] = streak

    def reset_streak(self):
        selected = self.habit_listbox.curselection()
        if not selected:
            messagebox.showerror("Error", "Please select a habit.")
            return
        
        habit_name = self.habit_listbox.get(selected[0]).split(" |")[0]
        if messagebox.askyesno("Confirm", f"Reset streak for '{habit_name}'?"):
            self.habits[habit_name]['streak'] = 0
            self.save_habits()
            self.refresh_display()
            messagebox.showinfo("Success", "Streak reset!")

    def delete_habit(self):
        selected = self.habit_listbox.curselection()
        if not selected:
            messagebox.showerror("Error", "Please select a habit to delete.")
            return
        
        habit_name = self.habit_listbox.get(selected[0]).split(" |")[0]
        if messagebox.askyesno("Confirm Delete", f"Delete '{habit_name}'? This cannot be undone."):
            del self.habits[habit_name]
            if habit_name in self.habit_dates:
                del self.habit_dates[habit_name]
            self.save_habits()
            self.refresh_display()
            messagebox.showinfo("Success", "Habit deleted!")

    def show_statistics(self):
        # Switch to statistics tab and update
        self.notebook.select(1)
        self.update_statistics()

    def refresh_display(self):
        # Update stats
        total_habits = len(self.habits)
        total_streak = sum(data['streak'] for data in self.habits.values())
        self.stats_label.config(text=f"Total Habits: {total_habits} | Combined Streak: {total_streak} days")

        # Update overview in stats tab
        self.update_overview()

        # Update listbox
        self.habit_listbox.delete(0, tk.END)
        for habit, data in sorted(self.habits.items()):
            status = "✅" if data['last_completed'] == datetime.now().strftime("%Y-%m-%d") else "⏳"
            display_text = f"{status} {habit} | 🔥 Streak: {data['streak']} | ✓ Done: {data['total_completions']}"
            self.habit_listbox.insert(tk.END, display_text)

    def update_overview(self):
        total_habits = len(self.habits)
        total_streak = sum(data['streak'] for data in self.habits.values())
        total_completions = sum(data['total_completions'] for data in self.habits.values())

        overview_text = f"""📊 OVERVIEW STATISTICS

🎯 Total Habits: {total_habits}
🔥 Combined Streak: {total_streak} days
✅ Total Completions: {total_completions}
📅 Today's Date: {datetime.now().strftime('%B %d, %Y')}"""

        if hasattr(self, 'overview_label'):
            self.overview_label.config(text=overview_text)

    def update_statistics(self):
        if not self.habits:
            self.stats_text.delete(1.0, tk.END)
            self.stats_text.insert(tk.END, "📈 No habits tracked yet.\n\nStart by adding some habits in the Home tab!")
            return

        stats_content = "📈 DETAILED HABIT STATISTICS\n" + "="*50 + "\n\n"

        for habit, data in sorted(self.habits.items()):
            stats_content += f"🎯 {habit}\n"
            stats_content += f"   🔥 Current Streak: {data['streak']} days\n"
            stats_content += f"   ✅ Total Completions: {data['total_completions']}\n"
            stats_content += f"   📅 Created: {data['created_date']}\n"
            stats_content += f"   🕒 Last Completed: {data['last_completed'] or 'Never'}\n"

            # Calculate completion rate
            if data['total_completions'] > 0:
                created_date = datetime.strptime(data['created_date'], "%Y-%m-%d")
                days_since_creation = (datetime.now() - created_date).days + 1
                completion_rate = (data['total_completions'] / days_since_creation) * 100
                stats_content += ".1f"
            else:
                stats_content += f"   📊 Completion Rate: 0%\n"

            stats_content += "\n"

        stats_content += "="*50 + "\n"
        stats_content += f"🎯 Total Habits: {len(self.habits)}\n"
        stats_content += f"🔥 Combined Streak: {sum(data['streak'] for data in self.habits.values())} days\n"
        stats_content += f"✅ Total Completions: {sum(data['total_completions'] for data in self.habits.values())}\n"

        self.stats_text.delete(1.0, tk.END)
        self.stats_text.insert(tk.END, stats_content)

    def export_stats(self):
        try:
            with open('habit_statistics.txt', 'w', encoding='utf-8') as f:
                f.write("HABIT TRACKER STATISTICS EXPORT\n")
                f.write("="*40 + "\n\n")
                f.write(f"Export Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")

                for habit, data in sorted(self.habits.items()):
                    f.write(f"Habit: {habit}\n")
                    f.write(f"Streak: {data['streak']} days\n")
                    f.write(f"Total Completions: {data['total_completions']}\n")
                    f.write(f"Created: {data['created_date']}\n")
                    f.write(f"Last Completed: {data['last_completed'] or 'Never'}\n")
                    f.write(f"Completion Dates: {', '.join(self.habit_dates.get(habit, []))}\n\n")

                f.write("="*40 + "\n")
                f.write(f"Total Habits: {len(self.habits)}\n")
                f.write(f"Combined Streak: {sum(data['streak'] for data in self.habits.values())} days\n")

            messagebox.showinfo("Export Success", "Statistics exported to 'habit_statistics.txt'")
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export statistics: {e}")

    def save_habits(self):
        with open('habits.csv', 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['habit_name', 'streak', 'last_completed', 'total_completions', 'created_date', 'completion_dates'])
            for habit, data in self.habits.items():
                dates_str = '|'.join(self.habit_dates.get(habit, []))
                writer.writerow([
                    habit,
                    data['streak'],
                    data['last_completed'] or '',
                    data['total_completions'],
                    data['created_date'],
                    dates_str
                ])

    def load_habits(self):
        if not os.path.exists('habits.csv'):
            return
        
        try:
            with open('habits.csv', 'r', encoding='utf-8') as csvfile:
                reader = csv.reader(csvfile)
                header = next(reader, None)  # Skip header
                for row in reader:
                    if len(row) >= 5:
                        habit_name = row[0]
                        self.habits[habit_name] = {
                            'streak': int(row[1]) if row[1] else 0,
                            'last_completed': row[2] if row[2] else None,
                            'total_completions': int(row[3]) if row[3] else 0,
                            'created_date': row[4] if len(row) > 4 else datetime.now().strftime("%Y-%m-%d")
                        }
                        # Load completion dates
                        if len(row) > 5 and row[5]:
                            self.habit_dates[habit_name] = row[5].split('|')
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load habits: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = HabitTracker(root)
    root.mainloop() 

  

