#!python3
# File: Login
import warnings

# Suppress InconsistentHashingWarning (use with caution)
warnings.filterwarnings("ignore", category=UserWarning, message="InconsistentHashingWarning")

import streamlit as st
import sqlite3
from sqlite3 import Error

if st.session_state.get("logged_in", False):
    st.session_state.logged_in = True
    st.session_state.logged_in = False

st.sidebar.markdown(
    """
    <h1 style='text-align: center; color: #0080FF;'>Health Assistant 🩺❤</h1>
    """,
    unsafe_allow_html=True
)
# Add a logo image
# logo = st.sidebar.image("logo.png", use_column_width=True)

# Add CSS to position the logo in the top right corner
st.markdown(
    """
    <style>
    .css-1l02zno {
        position: absolute;
        top: 10px;
        right: 10px;
    }
    </style>
    """,
    unsafe_allow_html=True
)

def create_connection(db_file):
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        print("Connection to SQLite DB successful")
    except Error as e:
        print(f"The error '{e}' occurred")
    return conn

def check_user(conn, username, password):
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password))
    rows = cursor.fetchall()
    if len(rows) > 0:
        return True
    else:
        return False

def create_user(conn, username, password):
    try:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
        conn.commit()
        return True
    except Error as e:
        print(f"Error occurred: {e}")
        return False

def main():
    st.title("Account Authentication 🔐")
    conn = create_connection("sqlite_db/user_database.db")

    create_table_query = """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            password TEXT NOT NULL
        );
    """
    conn.execute(create_table_query)

    menu = ["Login", "Register"]
    choice = st.sidebar.selectbox("Menu", menu)

    if choice == "Login":
        st.subheader("Login")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        if st.button("Login"):
            if check_user(conn, username, password):
                st.success("Logged in as {}".format(username))
                st.session_state.logged_in = True
                # st.experimental_set_query_params(logged_in=True)  # Set query parameter to indicate login
                st.switch_page("pages/HealthAssistance.py")
            else:
                st.error("Invalid username or password")

    elif choice == "Register":
        st.subheader("Create a New Account")
        new_username = st.text_input("Username")
        new_password = st.text_input("Password", type="password")
        confirm_password = st.text_input("Confirm Password", type="password")

        if new_password == confirm_password:
            if st.button("Register"):
                if create_user(conn, new_username, new_password):
                    st.success("Account created successfully. Please log in.")
                else:
                    st.error("Failed to create account. Please try again.")
        else:
            st.error("Passwords do not match")

    conn.close()

if __name__ == "__main__":
    main()
