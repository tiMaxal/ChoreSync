import tkinter as tk
from tkinter import filedialog, messagebox
import csv
from datetime import datetime, timedelta
from icalendar import Calendar, Event, Alarm
import os
import uuid
from math import ceil

class ChoreSynCalApp:
    def __init__(self, root):
        self.root = root
        self.root.title("ChoreSynCal - Household Chores Calendar Generator")
        
        # Initialize variables
        self.csv_file = tk.StringVar()
        self.time_of_day = tk.StringVar(value="09:00")
        self.period = tk.StringVar(value="Month")
        self.reminder_days = tk.StringVar(value="7")
        self.reminder_1hr = tk.BooleanVar(value=False)
        self.reminder_30min = tk.BooleanVar(value=True)
        self.reminder_10min = tk.BooleanVar(value=False)
        self.reminder_1day = tk.BooleanVar(value=False)
        self.stagger_interval = tk.StringVar(value="30")
        self.schedule_weekdays = tk.BooleanVar(value=True)
        self.schedule_weekends = tk.BooleanVar(value=True)
        
        # GUI Elements
        tk.Label(root, text="ChoreSynCal - Chore Calendar Generator", font=("Arial", 14)).pack(pady=10)
        
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
        
        # Reminder Times
        tk.Label(root, text="Reminder Times Before Chore (select all that apply):").pack()
        tk.Checkbutton(root, text="1 hour", variable=self.reminder_1hr).pack()
        tk.Checkbutton(root, text="30 minutes", variable=self.reminder_30min).pack()
        tk.Checkbutton(root, text="10 minutes", variable=self.reminder_10min).pack()
        tk.Checkbutton(root, text="1 day (Weekly/Monthly only)", variable=self.reminder_1day).pack()
        
        # Stagger Interval
        tk.Label(root, text="Stagger Interval for Same-Day Tasks (minutes):").pack()
        tk.Entry(root, textvariable=self.stagger_interval, width=10).pack()
        
        # Schedule Days
        tk.Label(root, text="Schedule Tasks On (select at least one):").pack()
        tk.Checkbutton(root, text="Weekdays", variable=self.schedule_weekdays).pack()
        tk.Checkbutton(root, text="Weekends", variable=self.schedule_weekends).pack()
        
        # Reminder Days Before End
        tk.Label(root, text="Days Before Period End for Re-import Reminder:").pack()
        tk.Entry(root, textvariable=self.reminder_days, width=10).pack()
        
        # Buttons Frame
        frame_buttons = tk.Frame(root)
        frame_buttons.pack(pady=20)
        
        # Configure columns for centering
        frame_buttons.columnconfigure(0, weight=1)  # left spacer
        frame_buttons.columnconfigure(1, weight=0)  # left button [start]
        frame_buttons.columnconfigure(2, weight=1)  # center spacer
        frame_buttons.columnconfigure(3, weight=0)  # right button [exit]
        frame_buttons.columnconfigure(4, weight=1)  # right spacer
        
        # Generate and Exit Buttons
        tk.Button(frame_buttons, text="Generate ICS File", command=self.generate_ics).grid(row=0, column=1, padx=5)
        tk.Button(frame_buttons, text="Exit", command=self.root.quit).grid(row=0, column=3, padx=5)
    
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
    
    def validate_stagger(self, stagger_str):
        try:
            minutes = int(stagger_str)
            return minutes >= 0
        except ValueError:
            return False
    
    def get_reminder_triggers(self, frequency):
        triggers = []
        if self.reminder_1hr.get():
            triggers.append(timedelta(hours=-1))
        if self.reminder_30min.get():
            triggers.append(timedelta(minutes=-30))
        if self.reminder_10min.get():
            triggers.append(timedelta(minutes=-10))
        if self.reminder_1day.get() and frequency.lower() in ['weekly', 'monthly']:
            triggers.append(timedelta(days=-1))
        return triggers if triggers else [timedelta(minutes=-10)]  # Default to 10 minutes if none selected
    
    def get_available_days(self, start_date, end_date):
        available_days = []
        delta = end_date - start_date
        for i in range(delta.days + 1):
            current_day = start_date + timedelta(days=i)
            is_weekday = current_day.weekday() < 5  # Monday=0, Sunday=6
            if (is_weekday and self.schedule_weekdays.get()) or (not is_weekday and self.schedule_weekends.get()):
                available_days.append(current_day)
        return available_days
    
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
        if not self.validate_stagger(self.stagger_interval.get()):
            messagebox.showerror("Error", "Stagger interval must be a non-negative integer")
            return
        if not (self.schedule_weekdays.get() or self.schedule_weekends.get()):
            messagebox.showerror("Error", "Select at least one: Weekdays or Weekends")
            return
        
        # Read CSV
        try:
            with open(self.csv_file.get(), newline='') as csvfile:
                reader = csv.DictReader(csvfile)
                if not all(field in reader.fieldnames for field in ['Frequency', 'Room', 'Task']):
                    messagebox.showerror("Error", "CSV must contain Frequency, Room, and Task columns")
                    return
                chores = list(reader)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to read CSV: {str(e)}")
            return
        
        # Create Calendar
        cal = Calendar()
        cal.add('prodid', '-//ChoreSynCal Calendar Generator//xAI//EN')
        cal.add('version', '2.0')
        
        # Set start date to today
        start_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        time_parts = self.time_of_day.get().split(':')
        hour, minute = int(time_parts[0]), int(time_parts[1])
        stagger_minutes = int(self.stagger_interval.get())
        
        # Determine period end
        if self.period.get() == "Month":
            end_date = (start_date.replace(day=1) + timedelta(days=32)).replace(day=1) - timedelta(days=1)
        else:  # Year
            end_date = start_date.replace(month=12, day=31)
        
        # Get available days based on weekday/weekend selection
        available_days = self.get_available_days(start_date, end_date)
        if not available_days:
            messagebox.showerror("Error", "No available days in the selected period")
            return
        
        # Group chores by frequency
        daily_chores = [c for c in chores if c['Frequency'].lower() == 'daily']
        weekly_chores = [c for c in chores if c['Frequency'].lower() == 'weekly']
        monthly_chores = [c for c in chores if c['Frequency'].lower() == 'monthly']
        
        # Process Daily Chores (spread across 7 days)
        if daily_chores:
            days_in_week = 7
            chores_per_day = ceil(len(daily_chores) / days_in_week)
            for i, chore in enumerate(daily_chores):
                day_offset = (i // chores_per_day) % days_in_week
                event_start = start_date + timedelta(days=day_offset)
                stagger_offset = (i % chores_per_day) * stagger_minutes
                event_start = event_start.replace(hour=hour, minute=minute) + timedelta(minutes=stagger_offset)
                
                if event_start.date() not in [d.date() for d in available_days]:
                    continue  # Skip if not an available day
                
                event = Event()
                event.add('summary', f"{chore['Room']}: {chore['Task']}")
                event.add('uid', str(uuid.uuid4()))
                event.add('dtstamp', datetime.now())
                event.add('dtstart', event_start)
                event.add('dtend', event_start + timedelta(hours=1))
                event.add('rrule', {'FREQ': 'WEEKLY', 'UNTIL': end_date, 'INTERVAL': 1})
                
                for trigger in self.get_reminder_triggers('daily'):
                    alarm = Alarm()
                    alarm.add('action', 'DISPLAY')
                    alarm.add('description', f"Reminder: {chore['Room']}: {chore['Task']}")
                    alarm.add('trigger', trigger)
                    event.add_component(alarm)
                
                cal.add_component(event)
        
        # Process Weekly Chores (spread across weeks in a month)
        if weekly_chores:
            weeks_in_month = ceil((end_date - start_date).days / 7)
            chores_per_week = ceil(len(weekly_chores) / weeks_in_month)
            for i, chore in enumerate(weekly_chores):
                week_offset = (i // chores_per_week) * 7
                event_start = start_date + timedelta(days=week_offset)
                stagger_offset = (i % chores_per_week) * stagger_minutes
                event_start = event_start.replace(hour=hour, minute=minute) + timedelta(minutes=stagger_offset)
                
                if event_start.date() not in [d.date() for d in available_days]:
                    continue  # Skip if not an available day
                
                event = Event()
                event.add('summary', f"{chore['Room']}: {chore['Task']}")
                event.add('uid', str(uuid.uuid4()))
                event.add('dtstamp', datetime.now())
                event.add('dtstart', event_start)
                event.add('dtend', event_start + timedelta(hours=1))
                event.add('rrule', {'FREQ': 'WEEKLY', 'UNTIL': end_date, 'INTERVAL': 4})
                
                for trigger in self.get_reminder_triggers('weekly'):
                    alarm = Alarm()
                    alarm.add('action', 'DISPLAY')
                    alarm.add('description', f"Reminder: {chore['Room']}: {chore['Task']}")
                    alarm.add('trigger', trigger)
                    event.add_component(alarm)
                
                cal.add_component(event)
        
        # Process Monthly Chores
        for i, chore in enumerate(monthly_chores):
            event_start = start_date
            stagger_offset = i * stagger_minutes
            event_start = event_start.replace(hour=hour, minute=minute) + timedelta(minutes=stagger_offset)
            
            if event_start.date() not in [d.date() for d in available_days]:
                event_start = available_days[0].replace(hour=hour, minute=minute) + timedelta(minutes=stagger_offset)
            
            event = Event()
            event.add('summary', f"{chore['Room']}: {chore['Task']}")
            event.add('uid', str(uuid.uuid4()))
            event.add('dtstamp', datetime.now())
            event.add('dtstart', event_start)
            event.add('dtend', event_start + timedelta(hours=1))
            event.add('rrule', {'FREQ': 'MONTHLY', 'UNTIL': end_date})
            
            for trigger in self.get_reminder_triggers('monthly'):
                alarm = Alarm()
                alarm.add('action', 'DISPLAY')
                alarm.add('description', f"Reminder: {chore['Room']}: {chore['Task']}")
                alarm.add('trigger', trigger)
                event.add_component(alarm)
            
            cal.add_component(event)
        
        # Add re-import reminder
        reimport_date = end_date - timedelta(days=int(self.reminder_days.get()))
        if reimport_date.date() not in [d.date() for d in available_days]:
            reimport_date = available_days[-1]  # Use last available day if needed
        
        reimport_event = Event()
        reimport_event.add('summary', 'Reminder: Re-import Chore Calendar')
        reimport_event.add('uid', str(uuid.uuid4()))
        reimport_event.add('dtstamp', datetime.now())
        reimport_event.add('dtstart', reimport_date.replace(hour=hour, minute=minute))
        reimport_event.add('dtend', reimport_date.replace(hour=hour, minute=minute) + timedelta(hours=1))
        
        for trigger in self.get_reminder_triggers('daily'):
            alarm = Alarm()
            alarm.add('action', 'DISPLAY')
            alarm.add('description', 'Reminder: Time to re-import your chore calendar')
            alarm.add('trigger', trigger)
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
    app = ChoreSynCalApp(root)
    root.mainloop()