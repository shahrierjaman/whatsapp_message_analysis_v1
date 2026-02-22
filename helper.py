from collections import Counter
import pandas as pd
from wordcloud import WordCloud
from urlextract import URLExtract
import emoji
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import nltk

extract = URLExtract()

def fetch_states(selected_user,df):
    if selected_user != "Overall":
        df = df[df['user'] == selected_user]

    #fetch number of messages
    num_of_msg = df.shape[0]

    #fetch number of words
    words = []
    for message in df['message']:
        words.extend(message.split())

    #fetch number of media
    num_of_media = df[df['message'] == '<Media omitted>'].shape[0]

    #fetch number of links
    links = []
    for message in df['message']:
        links.extend(extract.find_urls(message))

    return num_of_msg,len(words),num_of_media,len(links)


def most_busy_user(df):
    x = df['user'].value_counts().head(5)
    df = round((df['user'].value_counts() / df.shape[0] ) * 100,2).reset_index().rename(columns={'user':'Name','count':'Percent'})
    return x,df

def create_word_cloude(selected_user,df):
    if selected_user != "Overall":
        df = df[df['user'] == selected_user]

    wc = WordCloud(width = 500, height = 500, background_color ='white', max_font_size = 150)
    df_wc = wc.generate(df['message'].str.cat(sep=" "))

    return df_wc

def emoji_analysis(selected_user, df):
    if selected_user != "Overall":
        df = df[df['user'] == selected_user]

    emojis = []
    for message in df['message']:
        emojis.extend([c for c in message if emoji.is_emoji(c)])

    emoji_df = pd.DataFrame(
        Counter(emojis).most_common(len(Counter(emojis)))
    )

    return emoji_df

def monthly_timeline(selected_user, df):

    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    timeline = df.groupby(['year', 'month_num', 'month']).count()['message'].reset_index()

    time = []
    for i in range(timeline.shape[0]):
        time.append(timeline['month'][i] + "-" + str(timeline['year'][i]))

    timeline['time'] = time

    return timeline

def daily_timeline(selected_user, df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    daily_timeline = df.groupby('only_date').count()['message'].reset_index()

    return daily_timeline


def weekly_activity(selected_user, df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    return df['day_name'].value_counts()


def monthly_activity(selected_user, df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    return df['month'].value_counts()


def activity_heatmap(selected_user, df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    activity_headmap = df.pivot_table(index='day_name', columns='period', values='message', aggfunc='count').fillna(0)

    return activity_headmap



def user_behavior_profile(df):
    # ignore system messages
    df = df[df['user'] != 'group_notification']

    users = df['user'].unique()
    data = []

    for user in users:
        user_df = df[df['user'] == user]

        total_messages = user_df.shape[0]
        active_days = user_df['only_date'].nunique()
        messages_per_day = round(total_messages / active_days, 2)

        # word-based metrics
        words = user_df['message'].apply(lambda x: len(x.split()))
        avg_words = round(words.mean(), 2)

        short_msg_ratio = round((words <= 3).mean(), 2)
        long_msg_ratio = round((words >= 15).mean(), 2)

        # emoji metrics
        emoji_count = user_df['message'].apply(
            lambda x: sum(emoji.is_emoji(c) for c in x)
        ).sum()

        emoji_per_msg = round(emoji_count / total_messages, 2)

        emoji_msg_ratio = round(
            user_df['message'].apply(
                lambda x: any(emoji.is_emoji(c) for c in x)
            ).mean(),
            2
        )

        # media & link
        media_ratio = round(
            (user_df['message'] == '<Media omitted>').mean(),
            2
        )

        link_ratio = round(
            user_df['message'].apply(lambda x: len(extract.find_urls(x)) > 0).mean(),
            2
        )

        # time behavior
        night_msg_ratio = round(
            user_df['hour'].between(0, 5).mean(),
            2
        )

        most_active_hour = user_df['hour'].mode()[0]
        most_active_day = user_df['day_name'].mode()[0]

        data.append([
            user,
            total_messages,
            active_days,
            messages_per_day,
            avg_words,
            emoji_per_msg,
            emoji_msg_ratio,
            media_ratio,
            link_ratio,
            night_msg_ratio,
            short_msg_ratio,
            long_msg_ratio,
            most_active_hour,
            most_active_day
        ])

    columns = [
        'User',
        'Total Messages',
        'Active Days',
        'Messages/Day',
        'Avg Words/Msg',
        'Emoji/Msg',
        'Emoji Msg Ratio',
        'Media Ratio',
        'Link Ratio',
        'Night Msg Ratio',
        'Short Msg Ratio',
        'Long Msg Ratio',
        'Most Active Hour',
        'Most Active Day'
    ]

    return pd.DataFrame(data, columns=columns)

def engagement_score(df):
    # ignore system messages
    df = df[df['user'] != 'group_notification']

    profile_df = user_behavior_profile(df).copy()

    # Columns to normalize
    cols_to_norm = [
        'Total Messages',
        'Messages/Day',
        'Avg Words/Msg',
        'Emoji/Msg',
        'Media Ratio',
        'Link Ratio',
    ]

    # Normalize (min-max)
    for col in cols_to_norm:
        min_val = profile_df[col].min()
        max_val = profile_df[col].max()

        if max_val - min_val == 0:
            profile_df[col + '_norm'] = 0
        else:
            profile_df[col + '_norm'] = (
                (profile_df[col] - min_val) / (max_val - min_val)
            )

    # Engagement score calculation
    profile_df['Engagement Score'] = (
        0.30 * profile_df['Total Messages_norm'] +
        0.20 * profile_df['Messages/Day_norm'] +
        0.20 * profile_df['Avg Words/Msg_norm'] +
        0.10 * profile_df['Emoji/Msg_norm'] +
        0.10 * profile_df['Media Ratio_norm'] +
        0.10 * profile_df['Link Ratio_norm']
    )

    profile_df['Engagement Score'] = (profile_df['Engagement Score'] * 100).round(2)

    return profile_df[['User', 'Engagement Score']] \
        .sort_values(by='Engagement Score', ascending=False)


def sentiment_over_time(selected_user, df, freq='D'):
    """
    freq = 'D' for daily, 'M' for monthly
    """
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    df = df[df['user'] != 'group_notification']
    df = df[df['message'] != '<Media omitted>']

    sia = SentimentIntensityAnalyzer()

    # sentiment score per message
    df = df.copy()
    df['sentiment'] = df['message'].apply(
        lambda x: sia.polarity_scores(x)['compound']
    )

    sentiment_timeline = (
        df
        .resample(freq, on='date')['sentiment']
        .mean()
        .reset_index()
    )

    return sentiment_timeline

def sentiment_distribution(selected_user, df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    df = df[df['user'] != 'group_notification']
    df = df[df['message'] != '<Media omitted>']

    sia = SentimentIntensityAnalyzer()

    def label_sentiment(msg):
        score = sia.polarity_scores(msg)['compound']
        if score > 0.05:
            return 'Positive'
        elif score < -0.05:
            return 'Negative'
        else:
            return 'Neutral'

    df['sentiment_label'] = df['message'].apply(label_sentiment)

    return df['sentiment_label'].value_counts()

def sentiment_by_user(df):
    df = df[df['user'] != 'group_notification']
    df = df[df['message'] != '<Media omitted>']

    sia = SentimentIntensityAnalyzer()

    df = df.copy()
    df['sentiment'] = df['message'].apply(
        lambda x: sia.polarity_scores(x)['compound']
    )

    return (
        df.groupby('user')['sentiment']
        .mean()
        .round(3)
        .sort_values(ascending=False)
    )


