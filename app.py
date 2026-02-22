import streamlit as st
import preprocess_text, helper
import plotly.express as px
import plotly.graph_objects as go
import matplotlib.pyplot as plt
import seaborn as sns

# =========================
# Page Config
# =========================
st.set_page_config(
    page_title="WhatsApp Chat Analyzer",
    layout="wide",
    initial_sidebar_state="expanded"
)

PLOTLY_THEME = "plotly_white"

# =========================
# Emoji Font (for matplotlib only)
# =========================
#This part will not work in streamlit cloud. Comment out for deploy 
#from matplotlib import font_manager, rcParams
#emoji_font = font_manager.FontProperties(
    #fname=r"C:\Windows\Fonts\seguiemj.ttf"
#)
#rcParams['font.family'] = emoji_font.get_name()

# =========================
# Sidebar
# =========================
st.sidebar.markdown("## 💬 WhatsApp Chat Analyzer")
st.sidebar.markdown("Analyze chats, behavior & emotions")
st.sidebar.divider()

upload_file = st.sidebar.file_uploader("📁 Upload WhatsApp Chat (.txt)")

# =========================
# Main App
# =========================
if upload_file is not None:
    data = upload_file.getvalue().decode("utf-8")
    df = preprocess_text.process_text(data)

    user_list = df['user'].unique().tolist()
    user_list.remove("group_notification")
    user_list.sort()
    user_list.insert(0, "Overall")

    selected_user = st.sidebar.selectbox("👤 Select User", user_list)

    if st.sidebar.button("🚀 Analyze Chat"):
        # =========================
        # Header
        # =========================
        st.markdown(
            f"# 📊 Chat Analysis Dashboard\n"
            f"### {'All Users' if selected_user == 'Overall' else selected_user}"
        )
        st.divider()

        # =========================
        # Top Statistics
        # =========================
        num_messages, words, media, links = helper.fetch_states(selected_user, df)

        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Messages", num_messages)
        col2.metric("Words", words)
        col3.metric("Media", media)
        col4.metric("Links", links)

        st.divider()

        # =========================
        # Timelines
        # =========================
        st.markdown("## 🕒 Message Timelines")

        col1, col2 = st.columns(2)

        with col1:
            timeline = helper.monthly_timeline(selected_user, df)
            fig = px.line(
                timeline,
                x="time",
                y="message",
                markers=True,
                title="Monthly Message Volume",
                template=PLOTLY_THEME
            )
            fig.update_layout(
                xaxis_tickangle=90
            )
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            daily = helper.daily_timeline(selected_user, df)
            fig = px.line(
                daily,
                x="only_date",
                y="message",
                title="Daily Message Activity",
                template=PLOTLY_THEME
            )
            fig.update_layout(
                xaxis_tickangle=90
            )
            st.plotly_chart(fig, use_container_width=True)

        st.divider()

        # =========================
        # Activity Patterns
        # =========================
        st.markdown("## 📆 Activity Patterns")

        col1, col2 = st.columns(2)

        with col1:
            busy_day = helper.weekly_activity(selected_user, df)
            fig = px.bar(
                x=busy_day.index,
                y=busy_day.values,
                title="Most Active Days",
                labels={"x": "Day", "y": "Messages"},
                template=PLOTLY_THEME
            )
            fig.update_layout(
                xaxis_tickangle=90
            )
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            busy_month = helper.monthly_activity(selected_user, df)
            fig = px.bar(
                x=busy_month.index,
                y=busy_month.values,
                title="Most Active Months",
                labels={"x": "Month", "y": "Messages"},
                template=PLOTLY_THEME
            )
            fig.update_layout(
                xaxis_tickangle=90
            )
            st.plotly_chart(fig, use_container_width=True)

        st.subheader("Weekly Activity Heatmap")
        heatmap = helper.activity_heatmap(selected_user, df)
        fig, ax = plt.subplots(figsize=(12, 5))
        sns.heatmap(heatmap, cmap="Blues", annot=True, ax=ax)
        st.pyplot(fig)

        st.divider()

        # =========================
        # Overall User Insights
        # =========================
        if selected_user == "Overall":
            st.markdown("## 👥 User Insights")

            with st.expander("Most Active Users", expanded=True):
                x, new_df = helper.most_busy_user(df)
                fig = px.bar(
                    x=x.index,
                    y=x.values,
                    title="Top Active Users",
                    labels={"x": "User", "y": "Messages"},
                    template=PLOTLY_THEME
                )
                fig.update_layout(
                    xaxis_tickangle=90
                )
                st.plotly_chart(fig, use_container_width=True)
                st.dataframe(new_df, use_container_width=True)

            with st.expander("User Behavior Profiling"):
                profile_df = helper.user_behavior_profile(df)
                st.dataframe(profile_df, use_container_width=True)

                fig = px.bar(
                    profile_df,
                    x="User",
                    y="Total Messages",
                    title="Messages per User",
                    template=PLOTLY_THEME
                )
                fig.update_layout(
                    xaxis_tickangle=90
                )
                st.plotly_chart(fig, use_container_width=True)

            with st.expander("Engagement Score"):
                engagement_df = helper.engagement_score(df)
                st.dataframe(engagement_df, use_container_width=True)

                top_user = engagement_df.iloc[0]
                st.success(
                    f"🔥 Most Engaged User: **{top_user['User']}** "
                    f"(Score: {top_user['Engagement Score']})"
                )

        st.divider()

        # =========================
        # Sentiment Analysis
        # =========================
        st.markdown("## 😊 Sentiment Analysis")

        sent_dist = helper.sentiment_distribution(selected_user, df)
        fig = px.bar(
            x=sent_dist.index,
            y=sent_dist.values,
            title="Sentiment Distribution",
            labels={"x": "Sentiment", "y": "Messages"},
            color=sent_dist.index,
            template=PLOTLY_THEME
        )
        fig.update_layout(
            xaxis_tickangle=90
        )
        st.plotly_chart(fig, use_container_width=True)

        if selected_user == "Overall":
            user_sent = helper.sentiment_by_user(df)
            fig = px.bar(
                x=user_sent.index,
                y=user_sent.values,
                title="Average Sentiment per User",
                labels={"x": "User", "y": "Avg Sentiment"},
                template=PLOTLY_THEME
            )
            fig.update_layout(
                xaxis_tickangle=90
            )
            fig.add_hline(y=0, line_dash="dash", line_color="gray")
            st.plotly_chart(fig, use_container_width=True)

        st.divider()

        # =========================
        # Word Cloud
        # =========================
        st.markdown("## ☁️ Word Cloud")
        wc = helper.create_word_cloude(selected_user, df)
        fig, ax = plt.subplots(figsize=(8, 4))
        ax.imshow(wc)
        ax.axis("off")
        st.pyplot(fig)

        st.divider()


        # =========================
        # Emoji Analysis
        # =========================
        st.markdown("## 😀 Emoji Usage")

        emoji_df = helper.emoji_analysis(selected_user, df)

        if emoji_df.empty:
            st.info("No emojis were used by this user.")
        else:
            col1, col2 = st.columns(2)

            with col1:
                st.dataframe(
                    emoji_df,
                    use_container_width=True,
                    column_config={
                        0: "Emoji",
                        1: "Count"
                    }
                )

            with col2:
                fig = px.pie(
                    emoji_df,
                    values=1,
                    names=0,
                    hole=0.4,
                    title="Emoji Usage Share",
                    template=PLOTLY_THEME
                )

                st.plotly_chart(fig, use_container_width=True)
