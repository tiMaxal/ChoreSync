## 20250715

- prompt 1:
    - create a gui app to produce calendar .ics file from a selected csv for household chores [ie, to import the chores as `room, task` from the list, attached file being an example format, but with reminders based on column `Frequency`being in column1];
    - allow to set time-of-day for reminder;
    - allow to set an overall period of repetition [ie, only the month, or a whole year];
    - have an option to add reminder\series-of-reminder to redo the import calendar, starting at a length of time specified in the gui before end-of-period [ie, a week before end-of-month-period, or a month before end-of-a-year-period]

- prompt 2:
    - propose a readme, and speculate on a 'catchy' name for the app

- prompt 3:
    - adjust the code for file columns to be in order "frequency, room, task"
also provide multi-choice for reminders, of 1hr, 30mins, 10mins [instead of 15], and for daily\weekly provide '1day' reminder option as well

- prompt 4:
    - not a dropdown for reminder times, multiple options permitted [but do not apply 1day to daily tasks, if selected]
    - app name is updated to ChoreSynCal [for distinction against similar apps on github]

    - add 'exit' button at the bottom, alongside the 'generate ics' one, using the following styling method
    **Configure columns for centering**
```
frame_buttons.columnconfigure(0, weight=1) # left spacer
frame_buttons.columnconfigure(1, weight=0) # left button [start]
frame_buttons.columnconfigure(2, weight=1) # center spacer
frame_buttons.columnconfigure(3, weight=0) # right button [exit]
frame_buttons.columnconfigure(4, weight=1) # right spacer
```

- prompt 5:
    - spread tasks evenly [across a week for daily's, across the month for weekly's];
    - if multiple on one day, stagger tasks by interval provided by checkbox
    - provide checkboxes for whether to schedule them 'weekdays' or 'weekends' - allow both

## 20250716

- prompt 6:
    - provide a pair of fields to define 'active hours'; restrict calendar placement of events to between these times