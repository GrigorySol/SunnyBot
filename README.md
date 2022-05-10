# SunnyBot
### It's a Telegram Bot for the Sunny Side Singers choir

My first project, that larger than 500 lines.

This bot uses [pyTelegramBotAPI](https://github.com/eternnoir/pyTelegramBotAPI)

### /singers (only for the admin)
Search singers inline, by voice or display all available in the database.
Displays buttons with names that lead to the following options:
- Write private message
- Edit voices
- Edit suits
- Show attendance (in progress)
- Edit comment (in progress)
- Delete
- Close inline buttons

### /add (only for the admin)
Allows the administrator to add the following options:
- Event
- Concert
- Rehearsal
- Song

### /locations (only for the admin)
Allows the administrator to manage locations with the following options:
- Name  (in progress)
- URL  (in progress)
- Delete

### /songs
Displays all songs.
The administrator can edit the name and add sheets and sounds.
Available options:
- All
- In Work (in progress)
- By Concert

### /calendar
Displays calendar with marked Events/Concerts/Rehearsals.
Allows to see all events for the selected day.
The administrator has buttons for editing.

### /voice
Send a message with voice information.

### /suits
Sends information and photos of suits that the singer has.
Suggests the singer to add/remove the suit.
