- [done] provide 'operational hours' input
- add error management + logging + persistent settings

**Error Management:**
- Implement try-except blocks around critical operations (CSV reading, ICS generation, date calculations).
- Display user-friendly popup warnings with descriptive error messages using messagebox.showerror.
- Log errors and key actions (e.g., app start, file operations, errors) to csc.log with timestamps.
**Persistent Settings:**
- Add a csc_settings.json file to store user inputs (active hours, preferred start time, period, reminder times, stagger interval, Weekdays/Weekends, re-import days).
- Load settings on app start and save on successful ICS generation or exit.