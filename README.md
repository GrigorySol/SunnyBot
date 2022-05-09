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
- Delete (in progress)
- Close inline buttons

### /add (only for admin)
Allows to add next options:
- Events
- Concerts
- Rehearsal
- Song

### /songs
Displays all songs (work in progress). Admin can edit name and add sheets and sounds.

### /calendar
Displays calendar with marked Events/Concerts/Reheearsals. Allows to see all events for selected day. Admin has buttons to edit.

### /voice
Send message with voice info.

### /suits
Send a message and photos with the costumes singer owns. Prompts the user to add/remove a costume.
