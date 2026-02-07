1. Mock Transactions

# Incomes
- python3 'finance tracker.py' add income --amount 2000 --category "Salary" --date 2026-01-05 --description "January salary"
- python3 'finance tracker.py' add income --amount 150 --category "Gift" --date 2026-01-15 --description "Birthday gift"
- python3 'finance tracker.py' add income --amount 2000 --category "Salary" --date 2026-02-05 --description "February salary"

# Expenses
- python3 'finance tracker.py' add expense --amount 50 --category "Groceries" --date 2026-01-10 --description "Weekly groceries"
- python3 'finance tracker.py' add expense --amount 20 --category "Transport" --date 2026-01-12 --description "Bus pass"
- python3 'finance tracker.py' add expense --amount 100 --category "Groceries" --date 2026-01-20 --description "Extra shopping"
- python3 'finance tracker.py' add expense --amount 60 --category "Utilities" --date 2026-02-10 --description "Electricity"
- python3 'finance tracker.py' add expense --amount 30 --category "Transport" --date 2026-02-15 --description "Gas"
- python3 'finance tracker.py' add expense --amount 80 --category "Groceries" --date 2026-02-18 --description "Weekly groceries"

------------------------------------------------------------------------------------------------------------------------------------------------------------

2. Mock Budget

- python3 'finance tracker.py' budget set --category "Groceries" --limit 150 --month 1
- python3 'finance tracker.py' budget set --category "Transport" --limit 50  --month 1
- python3 'finance tracker.py' budget set --category "Utilities" --limit 100 --month 1

- python3 'finance tracker.py' budget set --category "Groceries" --limit 200 --month 2
- python3 'finance tracker.py' budget set --category "Transport" --limit 50  --month 2
- python3 'finance tracker.py' budget set --category "Utilities" --limit 120 --month 2

- python3 'finance tracker.py' budget set --category "Groceries" --limit 100 --month 2
- python3 'finance tracker.py' budget set --category "Transport" --limit 30  --month 2

------------------------------------------------------------------------------------------------------------------------------------------------------------

3. Export filtered expenses / income

# Export all expenses to in January 2026 in CSV
- python3 'finance tracker.py' export --type expense --month 1 --year 2026 --file-name january_expenses.csv --format csv

# Export Groceries only for January 2026 to JSON
- python3 'finance tracker.py' export --type expense --month 1 --year 2026 --category "Groceries" --file-name jan_groceries.json --format json

# Export all income for Jan → Feb 2026
- python3 'finance tracker.py' export --type income --month 2 --year 2026 --file-name income_jan_feb.json --format json

------------------------------------------------------------------------------------------------------------------------------------------------------------

4. Track Budgets

# Track all budgets for January
- python3 'finance tracker.py' budget status --month 1 --year 2026

# Track budget for overlapping range (Jan 15 → Feb 10) for Groceries
- python3 'finance tracker.py' budget status --category "Groceries" --start-date 2026-01-15 --end-date 2026-02-10

# Track all categories for overlapping range
- python3 'finance tracker.py' budget status --start-date 2026-01-15 --end-date 2026-02-10

------------------------------------------------------------------------------------------------------------------------------------------------------------

5. List / filter transactions

# All transactions
- python3 'finance tracker.py' list

# Filtered by category
- python3 'finance tracker.py' list --category "Groceries"

# Filtered by type
- python3 'finance tracker.py' list --type expense

# Filtered by date range
-python3 'finance tracker.py' list --start-date 2026-01-10 --end-date 2026-01-31