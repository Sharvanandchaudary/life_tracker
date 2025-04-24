
import streamlit as st
import pandas as pd
import plotly.express as px
import sqlite3
from datetime import datetime, date, timedelta 

from utils.db import init_db, connect_db
init_db()
conn = connect_db()
cursor = conn.cursor()

st.set_page_config(page_title="Life Tracker", layout="wide")
# -------------------------
# ⏳ Daily Time Tracker
# -------------------------
import pytz
from datetime import datetime, timedelta

# Set timezone
CST = pytz.timezone("America/Chicago")
now = datetime.now(CST)

# Set time range: 8:00 AM to 11:59 PM
start_time = now.replace(hour=8, minute=0, second=0, microsecond=0)
end_time = now.replace(hour=23, minute=59, second=0, microsecond=0)

st.markdown("## ⏳ Daily Time Tracker")

if now < start_time:
    st.warning("⚠️ Your day hasn’t started yet! It begins at 8:00 AM.")
else:
    time_passed = now - start_time
    time_left = end_time - now

    total_day_seconds = (end_time - start_time).total_seconds()
    passed_seconds = time_passed.total_seconds()
    percent_used = round((passed_seconds / total_day_seconds) * 100, 1)

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "Time Passed Since 8:00 AM",
        f"{time_passed.seconds // 3600}h {(time_passed.seconds // 60) % 60}m"
    )

    col2.metric(
        "Time Left Until Midnight",
        f"{time_left.seconds // 3600}h {(time_left.seconds // 60) % 60}m"
    )

    col3.progress(min(int(percent_used), 100), text=f"{percent_used}% of your day used")

    # Optional motivational hint
    if percent_used > 90:
        st.info("🔔 It's late — wrap up and plan tomorrow!")
    elif percent_used > 60:
        st.warning("🕒 Day's ending — prioritize your remaining tasks!")
    elif percent_used < 25:
        st.success("🌞 Good start! Plenty of time to accomplish your goals.")
    else:
        st.info("✅ Keep the momentum going!")


# Sidebar
with st.sidebar:
    st.image("https://i.imgur.com/2V5cF3P.png", width=100)  # Placeholder profile pic
    st.title("🌟 Good Morning, User")
    nav = st.radio("Navigate", ["🏠 Home", "📚 Study", "💰 Finance", "😴 Sleep", "📖 Diary", "📈 Trends"])

# Load data
def load_data():
    df = {}
    try:
        df['study'] = pd.read_sql_query("SELECT * FROM study_logs", conn, parse_dates=['log_date'])
        df['finance'] = pd.read_sql_query("SELECT * FROM finance_logs", conn, parse_dates=['log_date'])
        df['sleep'] = pd.read_sql_query("SELECT * FROM sleep_logs", conn, parse_dates=['log_date'])
        df['diary'] = pd.read_sql_query("SELECT * FROM diary_logs", conn, parse_dates=['log_date'])
        df['debt'] = pd.read_sql_query("SELECT category, SUM(amount) as total FROM debts GROUP BY category", conn)
    except Exception as e:
        st.error(f"Error loading data: {e}")
    return df

df = load_data()

if nav == "🏠 Home":
    st.title("🏠 Dashboard Overview")

    # Pending Tasks
    today = str(datetime.today().date())
    study_done = today in df['study']['log_date'].astype(str).values
    finance_done = today in df['finance']['log_date'].astype(str).values
    sleep_done = today in df['sleep']['log_date'].astype(str).values
    diary_done = today in df['diary']['log_date'].astype(str).values

    with st.container():
        st.subheader("📝 Today's Tasks")
        st.checkbox("📚 Study Log", value=study_done, disabled=True)
        st.checkbox("💰 Finance Log", value=finance_done, disabled=True)
        st.checkbox("😴 Sleep Log", value=sleep_done, disabled=True)
        st.checkbox("📖 Diary Entry", value=diary_done, disabled=True)

    # Quote + Timer
    col1, col2 = st.columns(2)
    with col1:
        st.info("💬 *“Look well into thyself; there is a source of strength which will always spring up if thou wilt always look.”* – Marcus Aurelius")
    with col2:
        now = datetime.now()
        sunset = now.replace(hour=23, minute=59, second=59)
        countdown = sunset - now
        st.metric("⏳ Time Left Today", str(countdown).split('.')[0], help="Until 11:59 PM")

    # Donut Chart
    latest_summary = {
        "Study": df['study']['duration'].sum() if not df['study'].empty else 0,
        "Finance": df['finance']['income'].sum() if not df['finance'].empty else 0,
        "Sleep": df['sleep']['duration'].sum() if not df['sleep'].empty else 0,
        "Diary": len(df['diary']) if not df['diary'].empty else 0
    }
    donut_df = pd.DataFrame(latest_summary.items(), columns=["Activity", "Value"])
    st.subheader("🧭 Life Engagement Overview")
    st.plotly_chart(px.pie(donut_df, names="Activity", values="Value", hole=0.4), use_container_width=True)

    # Metrics
    st.subheader("📊 Weekly Highlights")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Study Hours", f"{df['study']['duration'].tail(7).sum():.1f}")
    col2.metric("Total Income", f"${df['finance']['income'].tail(7).sum():.2f}")
    col3.metric("Avg Sleep", f"{df['sleep']['duration'].tail(7).mean():.1f} hrs")
    col4.metric("New Debts", f"${df['debt']['total'].sum():.2f}" if not df['debt'].empty else "$0")
# STUDY FORM
elif page == "Study":
    st.header("📚 Study Tracker")

    with st.form("study_form"):
        topic = st.text_input("Topic you studied")
        summary = st.text_area("Summary of what you learned")
        duration = st.number_input("Duration (in hours)", min_value=0.0, step=0.25)
        submitted = st.form_submit_button("Add to Study Log")

        if submitted:
            today = str(date.today())
            cursor.execute(
                "INSERT INTO study_logs (log_date, topic, summary, duration) VALUES (?, ?, ?, ?)",
                (today, topic, summary, duration)
            )
            conn.commit()
            st.success("Study log added!")

    st.subheader("📅 View Study History")
    cursor.execute("SELECT DISTINCT log_date FROM study_logs ORDER BY log_date DESC")
    available_dates = [row[0] for row in cursor.fetchall()]
    selected_date = st.selectbox("Select a date to view logs", available_dates)

    if selected_date:
        cursor.execute("SELECT topic, summary, duration FROM study_logs WHERE log_date = ?", (selected_date,))
        for topic, summary, duration in cursor.fetchall():
            st.markdown(f"**🗓 Date:** {selected_date}")
            st.markdown(f"- **Topic:** {topic}")
            st.markdown(f"- **Summary:** {summary}")
            st.markdown(f"- **Duration:** {duration} hrs")
            st.markdown("---")

    # Past logs display
    st.subheader("📅 View Study History")
    cursor.execute("SELECT DISTINCT log_date FROM study_logs ORDER BY log_date DESC")
    available_dates = [row[0] for row in cursor.fetchall()]
    selected_date = st.selectbox("Select a date to view logs", available_dates)

    if selected_date:
        cursor.execute("SELECT topic, summary, duration FROM study_logs WHERE log_date = ?", (selected_date,))
        rows = cursor.fetchall()
        for topic, summary, duration in rows:
            st.markdown(f"**Topic:** {topic}")
            st.markdown(f"- ⏱ Duration: {duration} hr")
            st.markdown(f"- 📝 Summary: {summary}")
            st.markdown("---")

# FINANCE FORM
elif nav == "💰 Finance":
    st.header("💰 Log Daily Finance")
    with st.form("finance_form"):
        income = st.number_input("Today's Income", min_value=0.0)
        expense = st.number_input("Today's Expense", min_value=0.0)
        submitted = st.form_submit_button("Submit")
        if submitted:
            today = str(datetime.today().date())
            cursor.execute("INSERT INTO finance_logs (log_date, income, expense) VALUES (?, ?, ?)", (today, income, expense))
            conn.commit()
            st.success("Finance log saved!")

    st.subheader("➕ Add Debt")
    with st.form("debt_form"):
        category = st.selectbox("Debt Type", ["Card", "Loan", "Hand Loan"])
        name = st.text_input("Debt Name")
        amount = st.number_input("Amount", min_value=0.0)
        submitted = st.form_submit_button("Add Debt")
        if submitted:
            cursor.execute("INSERT INTO debts (category, name, amount) VALUES (?, ?, ?)", (category, name, amount))
            conn.commit()
            st.success("Debt entry saved!")

# SLEEP FORM
elif nav == "😴 Sleep":
    st.header("😴 Log Sleep")
    with st.form("sleep_form"):
        bed = st.time_input("Bedtime")
        wake = st.time_input("Wake Time")
        quality = st.slider("Quality (1-5)", 1, 5, 3)
        core = st.text_input("Core Sleep Time")
        submitted = st.form_submit_button("Submit")
        if submitted:
            bt = datetime.combine(datetime.today(), bed)
            wt = datetime.combine(datetime.today(), wake)
            if wt < bt:
                wt += timedelta(days=1)
            duration = round((wt - bt).seconds / 3600, 2)
            today = str(datetime.today().date())
            cursor.execute(
                "INSERT OR REPLACE INTO sleep_logs (log_date, bed_time, wake_time, sleep_quality, core_sleep, duration) VALUES (?, ?, ?, ?, ?, ?)",
                (today, bed.strftime("%H:%M"), wake.strftime("%H:%M"), quality, core, duration)
            )
            conn.commit()
            st.success("Sleep log saved!")

elif nav == "📖 Diary":
    st.header("📖 Daily Accomplishments")

    # 📝 Input Form
    with st.form("diary_form"):
        entry = st.text_area("What did you accomplish today?")
        submitted = st.form_submit_button("Submit Diary Entry")

        if submitted:
            try:
                today = str(date.today())
                cursor.execute(
                    "INSERT OR REPLACE INTO diary_logs (log_date, entry) VALUES (?, ?)",
                    (today, entry)
                )
                conn.commit()
                st.success("Diary entry saved!")
            except Exception as e:
                st.error(f"Failed to save diary: {e}")

    # 📅 Display Past Entries
    st.subheader("📅 Past Diary Entries")
    try:
        cursor.execute("SELECT log_date, entry FROM diary_logs ORDER BY log_date DESC LIMIT 10")
        rows = cursor.fetchall()
        if not rows:
            st.info("No diary entries found.")
        else:
            for log_date, entry in rows:
                st.markdown(f"**{log_date}**\n> {entry}")
                st.markdown("---")
    except Exception as e:
        st.error(f"Error loading diary entries: {e}")


# TRENDS
elif nav == "📈 Trends":
    st.header("📈 Weekly Trends & Productivity")

    col1, col2 = st.columns(2)

    # 📚 Study Chart
    with col1:
        st.subheader("Study Duration")
        df_study = pd.read_sql_query("SELECT log_date, topic, duration FROM study_logs", conn)
        if not df_study.empty:
            df_study["log_date"] = pd.to_datetime(df_study["log_date"])
            st.plotly_chart(px.bar(df_study, x="log_date", y="duration", color="topic", title="Study Time by Topic"), use_container_width=True)

    # 💰 Finance Chart
    with col2:
        st.subheader("Income vs Expense")
        df_fin = pd.read_sql_query("SELECT log_date, income, expense FROM finance_logs", conn)
        if not df_fin.empty:
            df_fin["log_date"] = pd.to_datetime(df_fin["log_date"])
            df_fin["net"] = df_fin["income"] - df_fin["expense"]
            st.plotly_chart(px.line(df_fin, x="log_date", y=["income", "expense", "net"], title="Finance Trends"), use_container_width=True)

    col3, col4 = st.columns(2)

    # 😴 Sleep Chart
    with col3:
        st.subheader("Sleep Duration")
        df_sleep = pd.read_sql_query("SELECT log_date, duration FROM sleep_logs", conn)
        if not df_sleep.empty:
            df_sleep["log_date"] = pd.to_datetime(df_sleep["log_date"])
            st.plotly_chart(px.line(df_sleep, x="log_date", y="duration", title="Sleep Hours"), use_container_width=True)

    with col4:
        st.subheader("Sleep Quality")
        df_sleep_q = pd.read_sql_query("SELECT log_date, sleep_quality FROM sleep_logs", conn)
        if not df_sleep_q.empty:
            df_sleep_q["log_date"] = pd.to_datetime(df_sleep_q["log_date"])
            st.plotly_chart(px.line(df_sleep_q, x="log_date", y="sleep_quality", title="Sleep Quality"), use_container_width=True)

    # 🔄 Productivity Donut (simulated categories)
    st.subheader("🎯 Productivity Breakdown (Simulated)")
    prod_df = pd.DataFrame({
        "Category": ["Very Productive", "Productive", "Neutral", "Distracting", "Very Distracting"],
        "Time": [22, 30, 34, 19, 22]
    })
    st.plotly_chart(px.pie(prod_df, names="Category", values="Time", hole=0.4), use_container_width=True)
