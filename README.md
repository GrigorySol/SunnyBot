# SunnyBot
### It's a Telegram Bot for the Sunny Side Singers choir

My first project, that larger than 500 lines.

This bot uses [pyTelegramBotAPI](https://github.com/eternnoir/pyTelegramBotAPI)

### /singers (only for admin)
Search singers inline, by voice or all available in the database. Shows buttons with names that leads to the next options:
- Write private message
- Edit voices
- Edit suits
- Show attendance (in progress)
- Edit comment (in progress)
- Delete
- Close inline buttons

### /add (only for admin)
Allows to add next options:
- Event
- Concert
- Rehearsal
- Song

### /locations (only for admin)
Allows to manage locations (in progress).

### /songs
Displays all songs. Admin can edit name and add sheets and sounds. Available options:
- All
- In Work
- By Concert

### /calendar
Displays calendar with marked Events/Concerts/Rehearsals. Allows to see all events for selected day. Admin has buttons to edit.

### /voice
Send message with voice info.

### /suits
Send a message and photos with suits a singer owns. Prompts the user to add/remove a costume.
