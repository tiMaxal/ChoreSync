import tkinter as tk
from tkinter import filedialog, messagebox
import csv
from datetime import datetime, timedelta
from icalendar import Calendar, Event, Alarm
import os
import uuid
from math import ceil
import json
import logging

class ChoreSynCalApp:
    def __init__(self, root):
        self.root = root
        self.root.title("ChoreSynCal - Household Chores Calendar Generator")
        
        # Setup logging
        logging.basicConfig(
            filename='csc.log',
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        logging.info("ChoreSynCal application started")
        
        # Initialize variables
        self.csv_file = tk.StringVar()
        self.time_of_day = tk.StringVar(value="09:00")
        self.active_start = tk.StringVar(value="08:00")
        self.active_end = tk.StringVar(value="18:00")
        self.period = tk.StringVar(value="Month")
        self.reminder_days = tk.StringVar(value="7")
        self.reminder_1hr = tk.BooleanVar(value=False)
        self.reminder_30min = tk.BooleanVar(value=True)
        self.reminder_10min = tk.BooleanVar(value=False)
        self.reminder_1day = tk.BooleanVar(value=False)
        self.stagger_interval = tk.StringVar(value="30")
        self.schedule_weekdays = tk.BooleanVar(value=True)
        self.schedule_weekends = tk.BooleanVar(value=True)
        
        # Load settings
        self.load_settings()
        
        # GUI Elements
        tk.Label(root, text="ChoreSynCal - Chore Calendar Generator", font=("Arial", 14)).pack(pady=10)
        
        # CSV File Selection
        tk.Label(root, text="Select CSV File:").pack()
        tk.Entry(root, textvariable=self.csv_file, width=50).pack()
        tk.Button(root, text="Browse", command=self.browse_file).pack(pady=5)
        
        # Active Hours
        tk.Label(root, text="Active Hours for Scheduling (HH:MM, 24-hour):").pack()
        tk.Label(root, text="Start Time:").pack()
        tk.Entry(root, textvariable=self.active_start, width=10).pack()
        tk.Label(root, text="End Time:").pack()
        tk.Entry(root, textvariable=self.active_end, width=10).pack()
        
        # Time of Day
        tk.Label(root, text="Preferred Start Time for Chores (HH:MM, within active hours):").pack()
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
        tk.Button(frame_buttons, text="Exit", command=self.exit_app).grid(row=0, column=3, padx=5)
    
    def load_settings(self):
        try:
            if os.path.exists('csc_settings.json'):
                with open('csc_settings.json', 'r') as f:
                    settings = json.load(f)
                    self.csv_file.set(settings.get('csv_file', ''))
                    self.active_start.set(settings.get('active_start', '08:00'))
                    self.active_end.set(settings.get('active_end', '18:00'))
                    self.time_of_day.set(settings.get('time_of_day', '09:00'))
                    self.period.set(settings.get('period', 'Month'))
                    self.reminder_days.set(settings.get('reminder_days', '7'))
                    self.reminder_1hr.set(settings.get('reminder_1hr', False))
                    self.reminder_30min.set(settings.get('reminder_30min', True))
                    self.reminder_10min.set(settings.get('reminder_10min', False))
                    self.reminder_1day.set(settings.get('reminder_1day', False))
                    self.stagger_interval.set(settings.get('stagger_interval', '30'))
                    self.schedule_weekdays.set(settings.get('schedule_weekdays', True))
                    self.schedule_weekends.set(settings.get('schedule_weekends', True))
                logging.info("Settings loaded from csc_settings.json")
        except Exception as e:
            logging.error(f"Failed to load settings: {str(e)}")
            messagebox.showerror("Error", f"Failed to load settings: {str(e)}. Using default values.")
    
    def save_settings(self):
        try:
            settings = {
                'csv_file': self.csv_file.get(),
                'active_start': self.active_start.get(),
                'active_end': self.active_end.get(),
                'time_of_day': self.time_of_day.get(),
                'period': self.period.get(),
                'reminder_days': self.reminder_days.get(),
                'reminder_1hr': self.reminder_1hr.get(),
                'reminder_30min': self.reminder_30min.get(),
                'reminder_10min': self.reminder_10min.get(),
                'reminder_1day': self.reminder_1day.get(),
                'stagger_interval': self.stagger_interval.get(),
                'schedule_weekdays': self.schedule_weekdays.get(),
                'schedule_weekends': self.schedule_weekends.get()
            }
            with open('csc_settings.json', 'w') as f:
                json.dump(settings, f, indent=4)
            logging.info("Settings saved to csc_settings.json")
        except Exception as e:
            logging.error(f"Failed to save settings: {str(e)}")
            messagebox.showerror("Error", f"Failed to save settings: {str(e)}")
    
    def exit_app(self):
        self.save_settings()
        self.root.quit()
    
    def browse_file(self):
        try:
            file_path = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])
            if file_path:
                self.csv_file.set(file_path)
                logging.info(f"Selected CSV file: {file_path}")
        except Exception as e:
            logging.error(f"Error browsing file: {str(e)}")
            messagebox.showerror("Error", f"Error selecting CSV file: {str(e)}")
    
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
    
    def validate_active_hours(self, start_str, end_str):
        try:
            if not (self.validate_time(start_str) and self.validate_time(end_str)):
                return False
            start_time = datetime.strptime(start_str, "%H:%M")
            end_time = datetime.strptime(end_str, "%H:%M")
            return end_time > start_time
        except Exception as e:
            logging.error(f"Error validating active hours: {str(e)}")
            return False
    
    def validate_reminder_days(self, days_str, period, start_date, end_date):
        try:
            days = int(days_str)
            if days <= 0:
                return False
            if period == "Month" and days > 28:  # Prevent overflow in February
                return False
            if period == "Year" and days > 365:
                return False
            # Ensure re-import date is within period
            reimport_date = end_date - timedelta(days=days)
            return start_date.date() <= reimport_date.date() <= end_date.date()
        except Exception as e:
            logging.error(f"Error validating reminder days: {str(e)}")
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
        try:
            available_days = []
            delta = end_date - start_date
            for i in range(delta.days + 1):
                current_day = start_date + timedelta(days=i)
                is_weekday = current_day.weekday() < 5  # Monday=0, Sunday=6
                if (is_weekday and self.schedule_weekdays.get()) or (not is_weekday and self.schedule_weekends.get()):
                    available_days.append(current_day)
            return available_days
        except Exception as e:
            logging.error(f"Error getting available days: {str(e)}")
            return []
    
    def has_monthly_or_weekly(self, target_date, monthly_chores, weekly_chores, available_days, start_date):
        try:
            target_date = target_date.date()
            # Check monthly chores (scheduled on first available day)
            if monthly_chores:
                event_start = available_days[0].replace(hour=0, minute=0)
                if event_start.date() == target_date:
                    return True
            # Check weekly chores
            weeks_in_month = ceil((end_date - start_date).days / 7)
            chores_per_week = ceil(len(weekly_chores) / weeks_in_month)
            for i, chore in enumerate(weekly_chores):
                week_offset = (i // chores_per_week) * 7
                event_start = start_date + timedelta(days=week_offset)
                if event_start.date() == target_date:
                    return True
            return False
        except Exception as e:
            logging.error(f"Error checking monthly/weekly tasks: {str(e)}")
            return False
    
    def adjust_to_active_hours(self, event_time, active_start, active_end, stagger_offset, available_days, frequency, monthly_chores, weekly_chores, start_date):
        try:
            active_start_time = datetime.strptime(active_start, "%H:%M")
            active_end_time = datetime.strptime(active_end, "%H:%M")
            active_duration = (active_end_time - active_start_time).seconds // 60  # Duration in minutes
            
            # Calculate total minutes since active start
            event_minutes = (event_time.hour * 60 + event_time.minute + stagger_offset) - (active_start_time.hour * 60 + active_start_time.minute)
            
            # If event time is before active start, move to active start
            if event_minutes < 0:
                event_minutes = 0
            
            # Handle daily tasks differently
            if frequency.lower() == 'daily':
                # Check if the day has monthly or weekly tasks
                if self.has_monthly_or_weekly(event_time, monthly_chores, weekly_chores, available_days, start_date):
                    # Move to next available day
                    event_time += timedelta(days=1)
                    while event_time.date() not in [d.date() for d in available_days]:
                        event_time += timedelta(days=1)
                    event_time = event_time.replace(hour=active_start_time.hour, minute=active_start_time.minute)
                    return event_time
                # If no monthly/weekly tasks, check if staggering exceeds active hours
                if event_minutes >= active_duration:
                    # Count daily tasks on this day to squeeze
                    daily_count = sum(1 for d in self.daily_chores if (start_date + timedelta(days=(self.daily_chores.index(d) // ceil(len(self.daily_chores) / 7)) % 7)).date() == event_time.date())
                    if daily_count > 1:
                        # Squeeze tasks by adjusting duration
                        total_duration = active_duration - (active_start_time.hour * 60 + active_start_time.minute)
                        new_interval = total_duration // daily_count
                        task_index = sum(1 for d in self.daily_chores if (start_date + timedelta(days=(self.daily_chores.index(d) // ceil(len(self.daily_chores) / 7)) % 7)).date() == event_time.date() and self.daily_chores.index(d) <= self.daily_chores.index(chore))
                        event_minutes = task_index * new_interval
                        event_time = event_time.replace(hour=active_start_time.hour, minute=active_start_time.minute) + timedelta(minutes=event_minutes)
                    else:
                        # Move to next available day
                        event_time += timedelta(days=1)
                        while event_time.date() not in [d.date() for d in available_days]:
                            event_time += timedelta(days=1)
                        event_time = event_time.replace(hour=active_start_time.hour, minute=active_start_time.minute)
            else:
                # For weekly/monthly, wrap to next available day if exceeds active hours
                if event_minutes >= active_duration:
                    days_to_add = event_minutes // active_duration
                    minutes_remaining = event_minutes % active_duration
                    event_time = event_time.replace(hour=active_start_time.hour, minute=active_start_time.minute) + timedelta(minutes=minutes_remaining, days=days_to_add)
                    while event_time.date() not in [d.date() for d in available_days]:
                        event_time += timedelta(days=1)
                        event_time = event_time.replace(hour=active_start_time.hour, minute=active_start_time.minute)
            
            return event_time
        except Exception as e:
            logging.error(f"Error adjusting to active hours: {str(e)}")
            raise
    
    def generate_ics(self):
        try:
            # Validate inputs
            if not self.csv_file.get():
                messagebox.showerror("Error", "Please select a CSV file")
                logging.error("No CSV file selected")
                return
            if not os.path.exists(self.csv_file.get()):
                messagebox.showerror("Error", "Selected CSV file does not exist")
                logging.error(f"CSV file does not exist: {self.csv_file.get()}")
                return
            if not self.validate_time(self.time_of_day.get()):
                messagebox.showerror("Error", "Invalid time format. Use HH:MM (24-hour)")
                logging.error(f"Invalid time format: {self.time_of_day.get()}")
                return
            if not self.validate_days(self.reminder_days.get()):
                messagebox.showerror("Error", "Reminder days must be a positive integer")
                logging.error(f"Invalid reminder days: {self.reminder_days.get()}")
                return
            if not self.validate_stagger(self.stagger_interval.get()):
                messagebox.showerror("Error", "Stagger interval must be a non-negative integer")
                logging.error(f"Invalid stagger interval: {self.stagger_interval.get()}")
                return
            if not (self.schedule_weekdays.get() or self.schedule_weekends.get()):
                messagebox.showerror("Error", "Select at least one: Weekdays or Weekends")
                logging.error("No day type selected (Weekdays/Weekends)")
                return
            if not self.validate_active_hours(self.active_start.get(), self.active_end.get()):
                messagebox.showerror("Error", "Invalid active hours. Ensure start and end are HH:MM and end is after start")
                logging.error(f"Invalid active hours: start={self.active_start.get()}, end={self.active_end.get()}")
                return
            
            # Read CSV
            try:
                with open(self.csv_file.get(), newline='') as csvfile:
                    reader = csv.DictReader(csvfile)
                    if not all(field in reader.fieldnames for field in ['Frequency', 'Room', 'Task']):
                        messagebox.showerror("Error", "CSV must contain Frequency, Room, and Task columns")
                        logging.error("CSV missing required columns")
                        return
                    chores = list(reader)
                    logging.info(f"Successfully read CSV: {self.csv_file.get()}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to read CSV: {str(e)}")
                logging.error(f"Failed to read CSV: {str(e)}")
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
            
            # Validate reminder days
            if not self.validate_reminder_days(self.reminder_days.get(), self.period.get(), start_date, end_date):
                messagebox.showerror("Error", "Invalid re-import reminder days. Must be positive and not exceed period (max 28 for Month, 365 for Year)")
                logging.error(f"Invalid re-import reminder days: {self.reminder_days.get()} for period {self.period.get()}")
                return
            
            # Get available days based on weekday/weekend selection
            available_days = self.get_available_days(start_date, end_date)
            if not available_days:
                messagebox.showerror("Error", "No available days in the selected period")
                logging.error("No available days in the selected period")
                return
            
            # Group chores by frequency
            self.daily_chores = [c for c in chores if c['Frequency'].lower() == 'daily']
            weekly_chores = [c for c in chores if c['Frequency'].lower() == 'weekly']
            monthly_chores = [c for c in chores if c['Frequency'].lower() == 'monthly']
            
            # Process Daily Chores (spread across 7 days)
            if self.daily_chores:
                days_in_week = 7
                chores_per_day = ceil(len(self.daily_chores) / days_in_week)
                for i, chore in enumerate(self.daily_chores):
                    day_offset = (i // chores_per_day) % days_in_week
                    event_start = start_date + timedelta(days=day_offset)
                    stagger_offset = (i % chores_per_day) * stagger_minutes
                    event_start = event_start.replace(hour=hour, minute=minute)
                    
                    # Adjust to active hours
                    event_start = self.adjust_to_active_hours(event_start, self.active_start.get(), self.active_end.get(), stagger_offset, available_days, 'daily', monthly_chores, weekly_chores, start_date)
                    
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
                    event_start = event_start.replace(hour=hour, minute=minute)
                    
                    # Adjust to active hours
                    event_start = self.adjust_to_active_hours(event_start, self.active_start.get(), self.active_end.get(), stagger_offset, available_days, 'weekly', monthly_chores, weekly_chores, start_date)
                    
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
                event_start = event_start.replace(hour=hour, minute=minute)
                
                # Adjust to active hours
                event_start = self.adjust_to_active_hours(event_start, self.active_start.get(), self.active_end.get(), stagger_offset, available_days, 'monthly', monthly_chores, weekly_chores, start_date)
                
                if event_start.date() not in [d.date() for d in available_days]:
                    event_start = available_days[0].replace(hour=hour, minute=minute)
                    event_start = self.adjust_to_active_hours(event_start, self.active_start.get(), self.active_end.get(), stagger_offset, available_days, 'monthly', monthly_chores, weekly_chores, start_date)
                
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
            
            reimport_date = reimport_date.replace(hour=hour, minute=minute)
            reimport_date = self.adjust_to_active_hours(reimport_date, self.active_start.get(), self.active_end.get(), 0, available_days, 'daily', monthly_chores, weekly_chores, start_date)
            
            reimport_event = Event()
            reimport_event.add('summary', 'Reminder: Re-import Chore Calendar')
            reimport_event.add('uid', str(uuid.uuid4()))
            reimport_event.add('dtstamp', datetime.now())
            reimport_event.add('dtstart', reimport_date)
            reimport_event.add('dtend', reimport_date + timedelta(hours=1))
            
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
                    logging.info(f"ICS file generated: {output_file}")
                    self.save_settings()
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to save ICS file: {str(e)}")
                    logging.error(f"Failed to save ICS file: {str(e)}")
                    return
        
        except Exception as e:
            messagebox.showerror("Error", f"Unexpected error during ICS generation: {str(e)}")
            logging.error(f"Unexpected error in generate_ics: {str(e)}")
    
if __name__ == "__main__":
    try:
        root = tk.Tk()
        app = ChoreSynCalApp(root)
        root.mainloop()
    except Exception as e:
        logging.error(f"Application startup error: {str(e)}")
        messagebox.showerror("Error", f"Failed to start application: {str(e)}")