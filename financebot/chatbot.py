import sqlite3

# Initialize the SQLite database and create tables
def create_database():
    # Connect to the database (or create it if it doesn't exist)
    conn = sqlite3.connect('budget.db')
    
    # Create a cursor object to execute SQL commands
    cursor = conn.cursor()

    # Create the 'expenses' table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS expenses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        amount REAL NOT NULL,
        category TEXT NOT NULL,
        date TEXT DEFAULT (date('now'))
    )
    ''')

    # Create the 'budgets' table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS budgets (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        category TEXT NOT NULL,
        budget_limit REAL NOT NULL,
        spent REAL NOT NULL DEFAULT 0
    )
    ''')

    # Commit the changes and close the connection
    conn.commit()
    conn.close()

# Call the function to create the database and tables
create_database()
print("Database and tables created successfully!")


def log_expense(amount, category):
    conn = sqlite3.connect('budget.db')
    cursor = conn.cursor()
    
    # Insert the expense into the expenses table
    cursor.execute("INSERT INTO expenses (amount, category, date) VALUES (?, ?, date('now'))", 
                   (amount, category))
    
    conn.commit()
    conn.close()

    # Update the budget for the category
    update_budget(category, amount)
    print(f"Expense of {amount} added to {category}!")


def update_budget(category, amount):
    conn = sqlite3.connect('budget.db')
    cursor = conn.cursor()
    
    # Check if the category already exists in the budget table
    cursor.execute("SELECT spent FROM budgets WHERE category = ?", (category,))
    result = cursor.fetchone()

    if result:
        # If the category exists, update the spent amount
        spent = result[0] + amount
        cursor.execute("UPDATE budgets SET spent = ? WHERE category = ?", (spent, category))
    else:
        # If the category does not exist, create a new entry with a default budget limit
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
        print(f"Category: {category}")
        print(f"Budget Limit: {budget_limit}")
        print(f"Spent: {spent}")
        print(f"Remaining: {remaining}")
    else:
        print(f"No budget found for category '{category}'")


def get_advice():
    conn = sqlite3.connect('budget.db')
    cursor = conn.cursor()

    # Retrieve all budget data
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
        for tip in advice:
            print(tip)
    else:
        print("Your finances look good overall!")


def chatbot():
    print("Welcome to your Budget Management Chatbot!")
    print("You can add expenses, check your budget, or get financial advice.")
    print("Type 'help' to see available commands or 'exit' to quit.")

    while True:
        command = input("\nWhat would you like to do? ").strip().lower()

        if command == "help":
            print("\nCommands:")
            print("1. 'add expense' - Log a new expense")
            print("2. 'check budget' - Check your remaining budget for a category")
            print("3. 'advice' - Get financial advice based on your spending")
            print("4. 'exit' - Exit the chatbot")

        elif command == "add expense":
            try:
                amount = float(input("Enter the amount: "))
                category = input("Enter the category: ").strip()
                log_expense(amount, category)
            except ValueError:
                print("Invalid input. Please enter a valid amount.")

        elif command == "check budget":
            category = input("Enter the category: ").strip()
            check_budget(category)

        elif command == "advice":
            get_advice()

        elif command == "exit":
            print("Goodbye!")
            break

        else:
            print("Unknown command. Type 'help' to see the list of available commands.")

# Start the chatbot
chatbot()
