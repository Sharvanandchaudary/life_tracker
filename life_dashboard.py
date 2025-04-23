import streamlit as st
from datetime import datetime, date, timedelta
import pytz
from utils import db

# Init DB
from utils.db import init_db, get_today_log_status
init_db()

conn = db.connect_db()
cursor = conn.cursor()

# Config
st.set_page_config(page_title="Life Reflector", layout="wide")
CST = pytz.timezone("America/Chicago")

# Background & Theme
st.markdown("""
    <style>
    body {
        background-image: url('https://source.unsplash.com/1600x900/?nature,life');
        background-size: cover;
        color: white;
    }
    .block-container {
        background-color: rgba(0, 0, 0, 0.6);
        padding: 2rem;
        border-radius: 15px;
    }
    </style>
""", unsafe_allow_html=True)

st.title("🌈 Life Reflector")
st.subheader("Your Daily Personal Dashboard")

# Sidebar Navigation
page = st.sidebar.radio("📁 Choose Section", [
    "📚 Study", "💰 Finance", "😴 Sleep", "📖 Diary", "📊 Dashboard"])

# Reminder prompts

def show_prompt_reminders():
    study_done = get_today_log_status("study_logs")
    diary_done = get_today_log_status("diary_logs")
    finance_done = get_today_log_status("finance_logs")
    now_cst = datetime.now(CST)
    show_sleep_prompt = False

    if now_cst.hour >= 5:
        show_sleep_prompt = not get_today_log_status("sleep_logs")

    with st.expander("⚠️ You have pending logs today!", expanded=not all([study_done, diary_done, finance_done])):
        if not study_done:
            st.warning("🧠 You haven’t logged your **Study** yet.")
        if not finance_done:
            st.warning("💸 You haven’t logged your **Finance** yet.")
        if not diary_done:
            st.warning("📔 You haven’t written today’s **Diary**.")
        if show_sleep_prompt:
            st.warning("🛏️ Don’t forget to log your **Sleep** from last night!")

show_prompt_reminders()

# -----------------------------------
# 📚 Study Tracker
# -----------------------------------
if page == "📚 Study":
    st.header("📚 Study Tracker")
    with st.form("study_form"):
        topic = st.text_input("Which topic did you study?")
        duration = st.number_input("How much time did you spend? (in hours)", min_value=0.0, step=0.25)
        summary = st.text_area("Summarize what you learned:")
        interview = st.text_input("Did you give any interview today? (Yes/No or Notes)")
        book = st.text_input("Did you read any book? (Title or Notes)")
        next_plan = st.text_input("What do you want to study tomorrow?")
        submitted = st.form_submit_button("✅ Submit Study Log")

        if submitted:
            today = str(date.today())
            cursor.execute("""
                INSERT OR REPLACE INTO study_logs (log_date, topic, summary, duration, interview_given, book_read, next_plan)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (today, topic, summary, duration, interview, book, next_plan))
            conn.commit()
            st.success("Study log saved successfully!")

    # Display logs
    cursor.execute("SELECT * FROM study_logs ORDER BY log_date DESC LIMIT 7")
    rows = cursor.fetchall()
    if rows:
        st.subheader("🗂️ Recent Study Logs")
        for row in rows:
            st.markdown(f"""
            **🗓️ Date:** {row[1]}  
            - Topic: `{row[2]}`
            - Summary: {row[3]}
            - Duration: {row[4]} hr
            - Interview: {row[5]}
            - Book Read: {row[6]}
            - Next Plan: {row[7]}
            ---
            ")

# -----------------------------------
# 💰 Finance Tracker
# -----------------------------------
elif page == "💰 Finance":
    st.header("💰 Finance Tracker")
    with st.form("finance_form"):
        income = st.number_input("How much did you earn today?", min_value=0.0, step=1.0)
        expense = st.number_input("How much did you spend today?", min_value=0.0, step=1.0)
        submitted = st.form_submit_button("💾 Submit Finance Log")

        if submitted:
            today = str(date.today())
            cursor.execute("""
                INSERT INTO finance_logs (log_date, income, expense)
                VALUES (?, ?, ?)
            """, (today, income, expense))
            conn.commit()
            st.success("Finance log saved successfully!")

    st.divider()
    st.subheader("💳 Debt Tracker")
    with st.form("debt_form"):
        debt_category = st.selectbox("Debt Type", ["Card", "Loan", "Hand Loan"])
        debt_name = st.text_input("Debt Name or Source")
        debt_amount = st.number_input("Amount (USD)", min_value=0.0, step=1.0)
        submit_debt = st.form_submit_button("➕ Add Debt")

        if submit_debt:
            cursor.execute("INSERT INTO debts (category, name, amount) VALUES (?, ?, ?)", 
                           (debt_category, debt_name, debt_amount))
            conn.commit()
            st.success("Debt added!")

    # Summary
    cursor.execute("SELECT SUM(income), SUM(expense) FROM finance_logs")
    total_income, total_expense = cursor.fetchone()

    cursor.execute("SELECT category, SUM(amount) FROM debts GROUP BY category")
    debt_summary = cursor.fetchall()
    total_debt = sum(row[1] for row in debt_summary)

    net_balance = (total_income or 0) - ((total_expense or 0) + total_debt)

    st.subheader("📈 Financial Summary")
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Income", f"${total_income or 0:.2f}")
    col2.metric("Total Expense", f"${total_expense or 0:.2f}")
    col3.metric("Total Debt", f"${total_debt:.2f}")

    st.metric("🏁 Net Balance (Goal: Positive)", f"${net_balance:.2f}", delta_color="inverse")

    st.subheader("📋 Debt Breakdown")
    cursor.execute("SELECT category, name, amount FROM debts ORDER BY category")
    rows = cursor.fetchall()
    if rows:
        for cat in ["Card", "Loan", "Hand Loan"]:
            with st.expander(f"📂 {cat}s"):
                for r in filter(lambda x: x[0] == cat, rows):
                    st.write(f"- {r[1]}: ${r[2]:.2f}")

# -----------------------------------
# 😴 Sleep Tracker
# -----------------------------------
elif page == "😴 Sleep":
    st.header("😴 Sleep Tracker")
    with st.form("sleep_form"):
        bed_time = st.time_input("What time did you go to bed?")
        wake_time = st.time_input("What time did you wake up?")
        quality = st.slider("Sleep Quality (1 = Poor, 5 = Excellent)", 1, 5, 3)
        core_sleep = st.text_input("What was your core sleep time? (e.g., 1 AM to 5 AM)")
        submitted = st.form_submit_button("🌙 Submit Sleep Log")

        if submitted:
            bt = datetime.combine(date.today(), bed_time)
            wt = datetime.combine(date.today(), wake_time)
            if wt < bt:
                wt += timedelta(days=1)
            duration = round((wt - bt).seconds / 3600, 2)
            today = str(date.today())
            cursor.execute("""
                INSERT OR REPLACE INTO sleep_logs (log_date, bed_time, wake_time, sleep_quality, core_sleep, duration)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (today, bed_time.strftime("%H:%M"), wake_time.strftime("%H:%M"), quality, core_sleep, duration))
            conn.commit()
            st.success(f"Sleep log saved! Total sleep: {duration} hours")
# Display past logs
st.subheader("🛌 Recent Sleep Logs")
cursor.execute("SELECT * FROM sleep_logs ORDER BY log_date DESC LIMIT 5")
rows = cursor.fetchall()
for row in rows:
    st.markdown(f"**Date:** {row[1]}")
    st.markdown(f"- Bedtime: {row[2]}")
    st.markdown(f"- Wake time: {row[3]}")
    st.markdown(f"- Quality: {row[4]} / 5")
    st.markdown(f"- Core Sleep: {row[5]}")
    st.markdown(f"- Duration: {row[6]} hrs")
    st.markdown("---")


# -----------------------------------
# 📖 Diary Tracker
# -----------------------------------
elif page == "📖 Diary":
    st.header("📖 Daily Accomplishments")

    with st.form("diary_form"):
        entry = st.text_area("What did you accomplish today?")
        submitted = st.form_submit_button("📝 Submit Diary Entry")

        if submitted:
            today = str(date.today())
            cursor.execute("""
                INSERT OR REPLACE INTO diary_logs (log_date, entry)
                VALUES (?, ?)
            """, (today, entry))
            conn.commit()
            st.success("Diary entry saved!")


    # View past entries
    st.subheader("📅 Past Diary Entries")
    cursor.execute("SELECT * FROM diary_logs ORDER BY log_date DESC LIMIT 10")
    rows = cursor.fetchall()
    for row in rows:
    st.markdown(f"**Date:** {row[1]}")
    st.markdown(f"> {row[2]}")
    st.markdown("---")


conn.close()


# -----------------------------------
# 📊 Dashboard Visualization
# -----------------------------------
if page == "📊 Dashboard":
    st.header("📊 Weekly and Monthly Analytics")

    def load_data(query):
        df = pd.read_sql_query(query, conn)
        df['log_date'] = pd.to_datetime(df['log_date'])
        return df

    # Study chart
    st.subheader("📚 Study Hours")
    df_study = load_data("SELECT log_date, topic, duration FROM study_logs")
    if not df_study.empty:
        st.plotly_chart(px.bar(df_study, x="log_date", y="duration", color="topic", title="Study Duration by Topic"))

    # Finance chart
    st.subheader("💰 Finance Summary")
    df_fin = load_data("SELECT log_date, income, expense FROM finance_logs")
    if not df_fin.empty:
        df_fin['net'] = df_fin['income'] - df_fin['expense']
        st.plotly_chart(px.line(df_fin, x="log_date", y=["income", "expense", "net"], title="Daily Finance Overview"))

    # Debt pie chart
    st.subheader("💳 Debt Composition")
    df_debt = pd.read_sql_query("SELECT category, SUM(amount) as total FROM debts GROUP BY category", conn)
    if not df_debt.empty:
        st.plotly_chart(px.pie(df_debt, names='category', values='total', title='Debt Breakdown by Type'))

    # Sleep quality
    st.subheader("😴 Sleep Quality & Duration")
    df_sleep = load_data("SELECT log_date, duration, sleep_quality FROM sleep_logs")
    if not df_sleep.empty:
        col1, col2 = st.columns(2)
        with col1:
            st.plotly_chart(px.line(df_sleep, x="log_date", y="duration", title="Sleep Duration Over Time"))
        with col2:
            st.plotly_chart(px.line(df_sleep, x="log_date", y="sleep_quality", title="Sleep Quality Over Time"))

conn.close()
