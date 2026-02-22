import re
import pandas as pd

def process_text(data):
    pattern = r'\d{1,2}/\d{1,2}/\d{4},\s\d{1,2}:\d{2}[\s\u202F]?[ap]m\s-\s'

    # split messages
    messages = re.split(pattern, data)[1:]
    dates = re.findall(pattern, data)

    df = pd.DataFrame({
        "date": dates,
        "message": messages
    })

    # separate users and messages
    users = []
    clean_messages = []

    for msg in df['message']:
        parts = msg.split(":", 1)  # split only on first colon

        if len(parts) == 2:
            users.append(parts[0].strip())
            clean_messages.append(parts[1].strip())
        else:
            users.append("group_notification")
            clean_messages.append(msg.strip())

    df["user"] = users
    df["message"] = clean_messages

    # normalize WhatsApp invisible space
    df["date"] = df["date"].str.replace("\u202F", " ", regex=False)

    # remove trailing " - "
    df["date"] = df["date"].str.replace(r"\s-\s$", "", regex=True)

    # remove extra spaces
    df["date"] = df["date"].str.strip()

    # convert to datetime
    df["date"] = pd.to_datetime(
        df["date"],
        format="%d/%m/%Y, %I:%M %p"
    )

    df["day_name"] = df["date"].dt.day_name()
    df['only_date'] = df['date'].dt.date
    df["year"] = df["date"].dt.year
    df["month_num"] = df["date"].dt.month
    df["month"] = df["date"].dt.month_name()
    df["day"] = df["date"].dt.day
    df["hour"] = df["date"].dt.hour
    df["minute"] = df["date"].dt.minute

    period = []

    for hour in df[['day_name', 'hour']]['hour']:
        if hour == 23:
            period.append(str(hour) + "-" + str('00'))
        elif hour == 0:
            period.append(str('00') + "-" + str(hour + 1))
        else:
            period.append(str(hour) + "-" + str(hour + 1))

    df["period"] = period

    return df
