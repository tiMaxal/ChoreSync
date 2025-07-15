import tkinter as tk
from tkinter import filedialog, messagebox
import csv
from datetime import datetime, timedelta
from icalendar import Calendar, Event, Alarm
import os
import uuid

class ChoreCalendarApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Household Chores Calendar Generator")
        
        # Initialize variables
        self.csv_file = tk.StringVar()
        self.time_of_day = tk.StringVar(value="09:00")
        self.period = tk.StringVar(value="Month")
        self.reminder_days = tk.StringVar(value="7")
        
        # GUI Elements
        tk.Label(root, text="Chore Calendar Generator", font=("Arial", 14)).pack(pady=10)
        
        # CSV File Selection
        tk.Label(root, text="Select CSV File:").pack()
        tk.Entry(root, textvariable=self.csv_file, width=50).pack()
        tk.Button(root, text="Browse", command=self.browse_file).pack(pady=5)
        
        # Time of Day
        tk.Label(root, text="Time of Day for Chores (HH:MM, 24-hour):").pack()
        tk.Entry(root, textvariable=self.time_of_day, width=10).pack()
        
        # Repetition Period
        tk.Label(root, text="Repetition Period:").pack()
        tk.Radiobutton(root, text="Month", variable=self.period, value="Month").pack()
        tk.Radiobutton(root, text="Year", variable=self.period, value="Year").pack()
        
        # Reminder Days Before End
        tk.Label(root, text="Days Before Period End for Re-import Reminder:").pack()
        tk.Entry(root, textvariable=self.reminder_days, width=10).pack()
        
        # Generate Button
        tk.Button(root, text="Generate ICS File", command=self.generate_ics).pack(pady=20)
    
    def browse_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])
        if file_path:
            self.csv_file.set(file_path)
    
    def validate_time(self, time_str):
        try:
            datetime.strptime(time_str, "%H:%M")
            return True
        except ValueError:
            return False
    
    def validate_days(self, days_str):
        try:
            days = int(days_str)
            return days > 0
        except ValueError:
            return False
    
    def generate_ics(self):
        # Validate inputs
        if not self.csv_file.get():
            messagebox.showerror("Error", "Please select a CSV file")
            return
        if not os.path.exists(self.csv_file.get()):
            messagebox.showerror("Error", "Selected CSV file does not exist")
            return
        if not self.validate_time(self.time_of_day.get()):
            messagebox.showerror("Error", "Invalid time format. Use HH:MM (24-hour)")
            return
        if not self.validate_days(self.reminder_days.get()):
            messagebox.showerror("Error", "Reminder days must be a positive integer")
            return
        
        # Read CSV
        try:
            with open(self.csv_file.get(), newline='') as csvfile:
                reader = csv.DictReader(csvfile)
                if not all(field in reader.fieldnames for field in ['Room', 'Frequency', 'Task']):
                    messagebox.showerror("Error", "CSV must contain Room, Frequency, and Task columns")
                    return
                chores = list(reader)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to read CSV: {str(e)}")
            return
        
        # Create Calendar
        cal = Calendar()
        cal.add('prodid', '-//Chore Calendar Generator//xAI//EN')
        cal.add('version', '2.0')
        
        # Set start date to today
        start_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        time_parts = self.time_of_day.get().split(':')
        hour, minute = int(time_parts[0]), int(time_parts[1])
        
        # Determine period end
        if self.period.get() == "Month":
            end_date = (start_date.replace(day=1) + timedelta(days=32)).replace(day=1) - timedelta(days=1)
        else:  # Year
            end_date = start_date.replace(month=12, day=31)
        
        # Process chores
        for chore in chores:
            freq = chore['Frequency'].lower()
            event = Event()
            event.add('summary', f"{chore['Room']}: {chore['Task']}")
            event.add('uid', str(uuid.uuid4()))
            event.add('dtstamp', datetime.now())
            
            event_start = start_date.replace(hour=hour, minute=minute)
            
            if freq == 'daily':
                event.add('dtstart', event_start)
                event.add('dtend', event_start + timedelta(hours=1))
                event.add('rrule', {'FREQ': 'DAILY', 'UNTIL': end_date})
            elif freq == 'weekly':
                event.add('dtstart', event_start)
                event.add('dtend', event_start + timedelta(hours=1))
                event.add('rrule', {'FREQ': 'WEEKLY', 'UNTIL': end_date})
            elif freq == 'monthly':
                event.add('dtstart', event_start)
                event.add('dtend', event_start + timedelta(hours=1))
                event.add('rrule', {'FREQ': 'MONTHLY', 'UNTIL': end_date})
            else:
                continue  # Skip invalid frequencies
            
            # Add reminder
            alarm = Alarm()
            alarm.add('action', 'DISPLAY')
            alarm.add('description', f"Reminder: {chore['Room']}: {chore['Task']}")
            alarm.add('trigger', timedelta(minutes=-15))
            event.add_component(alarm)
            
            cal.add_component(event)
        
        # Add re-import reminder
        reimport_date = end_date - timedelta(days=int(self.reminder_days.get()))
        reimport_event = Event()
        reimport_event.add('summary', 'Reminder: Re-import Chore Calendar')
        reimport_event.add('uid', str(uuid.uuid4()))
        reimport_event.add('dtstamp', datetime.now())
        reimport_event.add('dtstart', reimport_date.replace(hour=hour, minute=minute))
        reimport_event.add('dtend', reimport_date.replace(hour=hour, minute=minute) + timedelta(hours=1))
        
        alarm = Alarm()
        alarm.add('action', 'DISPLAY')
        alarm.add('description', 'Reminder: Time to re-import your chore calendar')
        alarm.add('trigger', timedelta(minutes=-15))
        reimport_event.add_component(alarm)
        
        cal.add_component(reimport_event)
        
        # Save ICS file
        output_file = filedialog.asksaveasfilename(defaultextension=".ics", filetypes=[("ICS Files", "*.ics")])
        if output_file:
            try:
                with open(output_file, 'wb') as f:
                    f.write(cal.to_ical())
                messagebox.showinfo("Success", f"ICS file generated successfully at {output_file}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save ICS file: {str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    app = ChoreCalendarApp(root)
    root.mainloop()