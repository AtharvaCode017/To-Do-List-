import streamlit as st
import sqlite3
from datetime import datetime, date

# ----------------------------
# 📦 Database Functions
# ----------------------------

conn = sqlite3.connect('todo.db', check_same_thread=False)
c = conn.cursor()

def create_table():
    c.execute('''CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task TEXT,
                due_date TEXT,
                priority TEXT,
                category TEXT
                )''')

def add_task(task, due_date, priority, category):
    c.execute('INSERT INTO tasks (task, due_date, priority, category) VALUES (?, ?, ?, ?)',
              (task, due_date, priority, category))
    conn.commit()

def get_tasks():
    c.execute('SELECT * FROM tasks')
    return c.fetchall()

def delete_task(task_id):
    c.execute('DELETE FROM tasks WHERE id=?', (task_id,))
    conn.commit()

def filter_tasks(priority_filter=None, category_filter=None):
    query = "SELECT * FROM tasks WHERE 1=1"
    params = []

    if priority_filter and priority_filter != "All":
        query += " AND priority = ?"
        params.append(priority_filter)

    if category_filter and category_filter != "All":
        query += " AND category = ?"
        params.append(category_filter)

    c.execute(query, tuple(params))
    return c.fetchall()

# ----------------------------
# 🧠 App Layout & Logic
# ----------------------------

st.set_page_config(page_title="Advanced To-Do App", layout="centered")
st.title("🧠 Advanced To-Do List")

create_table()

# ----------------------------
# ➕ Add New Task
# ----------------------------
with st.form("Add Task"):
    col1, col2 = st.columns(2)
    task = col1.text_input("📝 Task")
    due_date = col2.date_input("📅 Due Date", format="YYYY-MM-DD")

    col3, col4 = st.columns(2)
    priority = col3.selectbox("🔼 Priority", ["Low", "Medium", "High"])
    category = col4.selectbox("📂 Category", ["Personal", "Work", "Study", "Other"])

    submitted = st.form_submit_button("➕ Add Task")
    if submitted:
        if task.strip():
            add_task(task, due_date.strftime("%Y-%m-%d"), priority, category)
            st.success(f"Task added: {task}")
            st.rerun()
        else:
            st.warning("Task cannot be empty.")

# ----------------------------
# 📍 Filters
# ----------------------------
st.subheader("🔍 Filter Tasks")
fcol1, fcol2 = st.columns(2)

priority_filter = fcol1.selectbox("Filter by Priority", ["All", "Low", "Medium", "High"])
category_filter = fcol2.selectbox("Filter by Category", ["All", "Personal", "Work", "Study", "Other"])

tasks = filter_tasks(priority_filter, category_filter)

# ----------------------------
# 🔔 Reminders
# ----------------------------
st.subheader("🔔 Reminders")
today = date.today()

due_today = [t for t in tasks if t[2] == today.strftime("%Y-%m-%d")]
overdue = [t for t in tasks if datetime.strptime(t[2], "%Y-%m-%d").date() < today]

if due_today:
    st.info(f"📅 You have {len(due_today)} task(s) due **today**:")
    for t in due_today:
        st.markdown(f"- {t[1]} ({t[4]}, {t[3]})")

if overdue:
    st.error(f"⚠️ You have {len(overdue)} **overdue** task(s):")
    for t in overdue:
        st.markdown(f"- {t[1]} (was due on {t[2]})")

# ----------------------------
# 📋 Task Display
# ----------------------------
st.subheader("📋 Your Tasks")

if tasks:
    for t in tasks:
        task_id, task_text, due_date, priority, category = t
        with st.expander(f"📌 {task_text}"):
            st.markdown(f"**📅 Due Date:** {due_date}")
            st.markdown(f"**🔼 Priority:** {priority}")
            st.markdown(f"**📂 Category:** {category}")
            if st.button(f"✅ Done (Delete Task ID {task_id})", key=task_id):
                delete_task(task_id)
                st.rerun()
else:
    st.info("No tasks found matching your filters.")
