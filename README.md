Overview
Build a command-line application to track expenses, income, and generate financial reports.

Core Requirements

1. Add Transactions
    • Add expenses with amount, category, date, and description 
    • Add income with amount, category, and date 
    • Auto-generate unique transaction IDs 
    • Default to current date if not specified 
Example Commands:
python finance.py add expense --amount 50.00 --category "Groceries" --description "Weekly shopping"
python finance.py add income --amount 1500.00 --category "Salary" --date 2025-01-15

2. View Transactions
    • List all transactions in chronological order 
    • Display: ID, date, type, category, amount, description 
    • Format amounts with 2 decimal places 
    • Show most recent transactions first 
Example Command:
python finance.py list

3. Filter Transactions
    • Filter by category 
    • Filter by date range (start date, end date) 
    • Filter by type (income or expense) 
    • Filter by month and year 
    • Combine multiple filters 
Example Commands:
python finance.py list --category "Groceries" --month 1 --year 2025
python finance.py list --type expense --start-date 2025-01-01 --end-date 2025-01-31

4. Generate Reports
    • Monthly summary: total income, total expenses, net savings 
    • Yearly summary: aggregated by month 
    • Category breakdown: expenses by category with percentages 
    • Show visual representation (text-based) 
Example Commands:
python finance.py report monthly
python finance.py report yearly
python finance.py report category --month 1 --year 2025

5. Budget Tracking
    • Set monthly budget limits per category 
    • Check budget status (current spending vs limit) 
    • Alert when budget exceeded 
    • Show budget progress (percentage used) 
Example Commands:
python finance.py budget set --category "Groceries" --limit 300.00
python finance.py budget status
python finance.py budget status --category "Groceries"

6. Export Data
    • Export to CSV format 
    • Export to JSON format 
    • Filter exports by date range, category, or type 
    • Specify custom output filename 
Example Commands:
python finance.py export --format csv --output transactions_2025.csv
python finance.py export --format json --month 1 --year 2025

------------------------------------------------------------------------------------------------------------------------

Data Structure

transactions.json:
{
  "transactions": [
    {
      "id": 1,
      "date": "2025-01-20",
      "type": "expense",
      "category": "Groceries",
      "amount": 50.00,
      "description": "Weekly shopping"
    },
    {
      "id": 2,
      "date": "2025-01-15",
      "type": "income",
      "category": "Salary",
      "amount": 1500.00,
      "description": ""
    }
  ],
  "next_id": 3
}

------------------------------------------------------------------

budgets.json:
{
  "budgets": {
    "Groceries": 300.00,
    "Transportation": 100.00,
    "Entertainment": 150.00
  }
}

-------------------------------------------------------------------

Required Modules
    • json - data storage and loading 
    • datetime - date handling and parsing 
    • sys or argparse - command-line argument parsing 
    • csv - CSV export functionality 

-------------------------------------------------------------------

Bonus Features
    1. Recurring Transactions
        ◦ Set up recurring income/expenses 
        ◦ Specify frequency (daily, weekly, monthly) 
        ◦ Auto-add on specified dates 
    2. Text-based Charts
        ◦ Show expense distribution with ASCII bars 
        ◦ Monthly spending trends 
    3. Search Functionality
        ◦ Search transactions by description keyword 
        ◦ Case-insensitive search 
    4. Undo Last Transaction
        ◦ Remove the most recently added transaction 
        ◦ Confirm before deletion 
    5. Backup and Restore
        ◦ Create ZIP backup of all data files 
        ◦ Restore from backup file 
        ◦ Include timestamp in backup filename
