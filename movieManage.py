from flask import Flask, render_template, request
from openai import OpenAI
import sqlite3
import os
import json
from dotenv import load_dotenv
from openrouter.modelCtrl import get_free_models

load_dotenv()

app = Flask(__name__)

client = OpenAI(
    api_key=os.getenv("api_key"),
    base_url=os.getenv("base_url")
)

# Config SQLite Database
DB_PATH = os.path.join(os.path.dirname(__file__), "youtube_links.db")

def update_env_file(key, value):
    """Update or add a key-value pair in .env file"""
    env_path = os.path.join(os.path.dirname(__file__), ".env")
    
    lines = []
    if os.path.exists(env_path):
        with open(env_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
    
    # Find and update or add the key
    updated = False
    for i, line in enumerate(lines):
        if line.startswith(f"{key}="):
            lines[i] = f"{key}={value}\n"
            updated = True
            break
    
    if not updated:
        lines.append(f"{key}={value}\n")
    
    # Write back
    with open(env_path, 'w', encoding='utf-8') as f:
        f.writelines(lines)
    
    # Update os.environ
    os.environ[key] = value

def get_schema_text(conn):
    cur = conn.cursor()
    # Get table names
    cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cur.fetchall()
    
    schema_dict = {}
    for (table_name,) in tables:
        cur.execute(f"PRAGMA table_info({table_name});")
        columns = cur.fetchall()
        schema_dict[table_name] = [f"{col[1]} ({col[2]})" for col in columns]
    
    # Format thành prompt cho AI
    schema_text = ""
    for table, columns in schema_dict.items():
        cols = ", ".join(columns)
        schema_text += f"Table {table}: {cols}\n"
    return schema_text
    
def get_sql_from_prompt(prompt_text, model=None):
    if model is None:
        model = os.getenv("model", "gpt-4o-mini")
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": "You are an assistant that only returns SQL queries without markdown or explanation."},
            {"role": "user", "content": prompt_text}
        ]
    )
    return response.choices[0].message.content.strip()

def run_sql_query(sql):
    try:
        if not sql.strip().lower().startswith("select"):
            return [("Error:", "Only SELECT queries allowed")]
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute(sql)
        rows = cur.fetchall()
        cur.close()
        conn.close()
        return rows
    except Exception as e:
        return [("Error:", str(e))]

@app.route("/", methods=["GET", "POST"])
def index():
    history = []
    current_model = os.getenv("model", "")
    
    # Get free models from OpenRouter
    try:
        available_models = get_free_models()
    except Exception as e:
        print(f"Error loading models: {e}")
        available_models = [os.getenv("model", "gpt-4o-mini")]
    
    if request.method == "POST":
        user_input = request.form["user_input"]
        selected_model = request.form.get("model", "")
        
        # Save model to .env if provided
        if selected_model:
            update_env_file("model", selected_model)
            current_model = selected_model
        
        # Get database schema
        conn = sqlite3.connect(DB_PATH)
        schema_text = get_schema_text(conn)
        conn.close()
        
        # Add schema to prompt for AI
        prompt_with_schema = f"Database schema:\n{schema_text}\nUser query: {user_input}"
        # Get SQL query from AI
        # In ra Prompt để debug
        print("Prompt sent to AI:")
        print(prompt_with_schema)
        print(f"Model used: {selected_model}")

        sql = get_sql_from_prompt(prompt_with_schema, model=selected_model)
        result = run_sql_query(sql)
        
        history.append(("user", user_input))
        history.append(("system", f"SQL: {sql}"))
        for row in result:
            history.append(("Row", str(row)))
    return render_template("index.html", history=history, models=available_models, current_model=current_model)

if __name__ == "__main__":
    app.run(debug=True)