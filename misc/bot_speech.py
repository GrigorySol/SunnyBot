def greetings(current_hour: int):
    if 5 <= current_hour < 12:
        return "Доброе утро."
    elif 12 <= current_hour < 18:
        return "Добрый день."
    elif 18 <= current_hour < 23:
        return "Добрый вечер."
    elif 23 <= current_hour < 5:
        return "Доброй ночи."
