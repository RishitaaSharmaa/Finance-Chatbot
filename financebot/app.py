from flask import Flask, render_template, request, jsonify
import sqlite3

app = Flask(__name__)

# Initialize the SQLite database and create tables
def create_database():
    conn = sqlite3.connect('budget.db')
    cursor = conn.cursor()

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS expenses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        amount REAL NOT NULL,
        category TEXT NOT NULL,
        date TEXT DEFAULT (date('now'))
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS budgets (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        category TEXT NOT NULL,
        budget_limit REAL NOT NULL,
        spent REAL NOT NULL DEFAULT 0
    )
    ''')

    conn.commit()
    conn.close()

# Call the function to create the database and tables
create_database()
print("Database and tables created successfully!")

def log_expense(amount, category):
    conn = sqlite3.connect('budget.db')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO expenses (amount, category, date) VALUES (?, ?, date('now'))", 
                   (amount, category))
    conn.commit()
    conn.close()
    update_budget(category, amount)
    print(f"Expense of {amount} added to {category}!")

def update_budget(category, amount):
    conn = sqlite3.connect('budget.db')
    cursor = conn.cursor()
    cursor.execute("SELECT spent FROM budgets WHERE category = ?", (category,))
    result = cursor.fetchone()
    if result:
        spent = result[0] + amount
        cursor.execute("UPDATE budgets SET spent = ? WHERE category = ?", (spent, category))
    else:
        cursor.execute("INSERT INTO budgets (category, budget_limit, spent) VALUES (?, ?, ?)", 
                       (category, 500, amount))  # Default budget is set to 500
    conn.commit()
    conn.close()

def check_budget(category):
    conn = sqlite3.connect('budget.db')
    cursor = conn.cursor()
    cursor.execute("SELECT budget_limit, spent FROM budgets WHERE category = ?", (category,))
    result = cursor.fetchone()
    conn.close()
    if result:
        budget_limit, spent = result
        remaining = budget_limit - spent
        return f"Category: {category}\nBudget Limit: {budget_limit}\nSpent: {spent}\nRemaining: {remaining}"
    else:
        return f"No budget found for category '{category}'"

def get_advice():
    conn = sqlite3.connect('budget.db')
    cursor = conn.cursor()
    cursor.execute("SELECT category, budget_limit, spent FROM budgets")
    results = cursor.fetchall()
    conn.close()

    advice = []
    for category, budget_limit, spent in results:
        if spent > budget_limit:
            advice.append(f"You're overspending on {category}. Consider cutting down.")
        elif spent < budget_limit * 0.5:
            advice.append(f"You're doing great with {category}. Keep it up!")
    
    if advice:
        return "\n".join(advice)
    else:
        return "Your finances look good overall!"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    user_message = request.json['message']
    response = ""

    # Convert the user message to lower case for easier comparison
    user_message_lower = user_message.lower()

    if "add expense" in user_message_lower:
        try:
            # Extract the part after "add expense"
            parts = user_message.split()
            if len(parts) < 4:  # Check if there are enough parts
                raise IndexError  # Trigger exception if not enough arguments

            amount = float(parts[2])  # Expects input like "add expense 100 food"
            category = " ".join(parts[3:])  # Join the rest as the category
            log_expense(amount, category)
            response = f"Expense of {amount} added to {category}!"
        except ValueError:
            response = "Invalid amount. Please use 'add expense <amount> <category>'."
        except IndexError:
            response = "Invalid input. Please use 'add expense <amount> <category>'."
        except Exception as e:
            response = f"An error occurred: {str(e)}"

    elif "check budget" in user_message_lower:
        parts = user_message.split()
        if len(parts) < 3:
            response = "Please specify a category to check the budget."
        else:
            category = " ".join(parts[2:])  # Join the rest as the category
            response = check_budget(category)

    elif "advice" in user_message_lower:
        response = get_advice()

    elif "help" in user_message_lower:
        response = (
            "Commands:\n"
            "1. 'add expense <amount> <category>' - Log a new expense\n"
            "2. 'check budget <category>' - Check your remaining budget for a category\n"
            "3. 'advice' - Get financial advice based on your spending\n"
            "4. 'exit' - Exit the chatbot"
        )

    else:
        response = "Unknown command. Type 'help' to see the list of available commands."

    return jsonify({"response": response})

if __name__ == '__main__':
    app.run(debug=True)
