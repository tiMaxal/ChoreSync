# ChoreSynCal

ChoreSynCal [Chores Sync to Calendar] is a user-friendly Python application that transforms your household chore list into a calendar-compatible .ics file. Import your chores into Google Calendar, Apple Calendar, or any iCalendar-supported app, with customizable reminders, task distribution, and scheduling options to keep your home organized effortlessly.

## Features
- **CSV Input**: Reads chores from a CSV with columns `Frequency`, `Room`, `Task`.
- **Task Distribution**:
  - Daily tasks are spread evenly across the 7 days of the week.
  - Weekly tasks are distributed across the weeks of a month (~4-5 weeks).
  - Monthly tasks are scheduled on the first available day of the month.
- **Active Hours**: Restricts task scheduling to a user-defined time window (e.g., 08:00–18:00).
- **Staggered Scheduling**: Staggers same-day tasks by a user-defined interval (in minutes).
  - For Daily tasks exceeding active hours: moves to next available day if Monthly or Weekly tasks are present; otherwise, squeezes task durations to fit.
  - For Weekly/Monthly tasks: wraps to the next available day's start time.
- **Day Restrictions**: Schedules tasks on Weekdays, Weekends, or both, based on user selection.
- **Flexible Reminders**: Supports multiple reminder times (1 hour, 30 minutes, 10 minutes; 1 day for Weekly/Monthly tasks).
- **Repetition Periods**: Choose between monthly or yearly chore cycles.
- **Re-import Reminder**: Adds a reminder to regenerate the calendar before the period ends.
- **User-Friendly GUI**: Includes file selection, time inputs, day restrictions, active hours, and centered Generate/Exit buttons.

## Requirements
- Python 3.6+
- Libraries: `tkinter`, `icalendar`
- A CSV file with columns: `Frequency` (Daily, Weekly, Monthly), `Room`, `Task`

## Installation
- Ensure Python is installed on your system.
- Install required libraries:
  ```bash
  pip install icalendar
  ```
  [Note: `tkinter` is typically included with Python. If not, install it (e.g., `sudo apt-get install python3-tk` on Debian-based systems).]
- Download the `ChoreSynCal.py` script.

## Usage
- Prepare a CSV file with your chores, formatted like:
  ```csv
  Frequency,Room,Task
  Daily,Kitchen,Wipe down counters
  Weekly,Bathroom,Scrub toilet
  Monthly,Bedroom,Organize drawers
  ```
- Run the script:
  ```bash
  python ChoreSynCal.py
  ```
- In the GUI:
  - Click "Browse" to select your CSV file.
  - Enter active hours (e.g., Start: "08:00", End: "18:00", 24-hour format).
  - Enter the preferred start time for chores (e.g., "09:00", within active hours).
  - Choose a repetition period (Month or Year).
  - Select reminder times (1 hour, 30 minutes, 10 minutes, 1 day for Weekly/Monthly).
  - Enter a stagger interval (minutes) for same-day tasks (e.g., "30" for 30-minute gaps).
  - Check Weekdays and/or Weekends to restrict task days (at least one required).
  - Enter days before period end for a re-import reminder (e.g., "7" for a week before).
  - Click "Generate ICS File" to save the .ics file, or "Exit" to close the app.
- Import the generated .ics file into your calendar app (e.g., Google Calendar, Apple Calendar).

## Example
For a CSV with:
- `Daily,Kitchen,Wipe down counters`
- `Daily,Bathroom,Wipe sink`
- `Daily,Loungeroom,Tidy cushions`
- `Weekly,Loungeroom,Vacuum`
- `Monthly,Bedroom,Organize drawers`

With settings: Active hours 08:00–10:00, Preferred start 09:00, 30-minute stagger, Weekdays only, 10-minute and 1-hour reminders, Monthly period:
- Daily tasks are spread across Monday–Friday (e.g., counters on Monday at 09:00, sink on Tuesday at 09:00, cushions on Wednesday at 09:00). If staggering exceeds 10:00 (e.g., 3 tasks at 30-minute intervals), tasks are squeezed to fit (e.g., 20-minute intervals: 09:00, 09:20, 09:40) unless Monthly/Weekly tasks are on the same day, then moved to the next available day.
- Weekly tasks are spread across weeks (e.g., vacuum in week 1 at 09:00, repeating every 4 weeks).
- Monthly tasks are on the first weekday (e.g., drawers on first Monday at 09:00, within 08:00–10:00).
- Reminders are set 10 minutes and 1 hour before each task (1 day for Weekly/Monthly).
- A re-import reminder is scheduled 7 days before the month ends, within active hours.

## Notes
- **CSV Format**: Must have `Frequency` (Daily, Weekly, Monthly, case-insensitive), `Room`, `Task` columns.
- **Time Format**: Use HH:MM (24-hour, e.g., "08:00"). Active hours end must be after start.
- **Stagger Interval**: Non-negative integer (0 for no staggering). For Daily tasks, if exceeding active hours, tasks are moved to the next available day if Monthly/Weekly tasks are present; otherwise, durations are adjusted to fit.
- **Day Selection**: At least one of Weekdays or Weekends must be selected.
- **Reminders**: At least one reminder is applied (defaults to 10 minutes if none selected). 1-day reminders are ignored for Daily tasks.
- **Period**: Month schedules until the last day of the current month; Year until December 31.

## Contributing
- Suggestions and pull requests are welcome! Please open an issue to discuss improvements or report bugs.

## License
MIT License - feel free to use, modify, and distribute.

---
*Generated by ChoreSynCal - Sync your chores, simplify your life!*