import argparse
import os
import tempfile
from pathlib import Path
import csv
import json
from datetime import datetime, date
from collections import Counter, defaultdict
import calendar
import logging


# Basic logging config for debugginq
logging.basicConfig(level=logging.DEBUG, format='[%(levelname)s] %(message)s')

class FinanceTracker:

    def __init__(self, base_dir = None):

        self.BASE_DIR = Path(base_dir).expanduser().resolve() if base_dir else Path(__file__).resolve().parent
        self.TRANSACTION_FILE = self.BASE_DIR / 'transactions.json'
        self.BUDGET_FILE = self.BASE_DIR / 'budgets.json'

        self.BASE_DIR.mkdir(parents=True, exist_ok=True)

        if self.TRANSACTION_FILE.exists():
            with open(self.TRANSACTION_FILE, 'r') as f:
                self.transactions = json.load(f)
        else:
            self.transactions = {'transactions': []}

        if self.BUDGET_FILE.exists():
            with open(self.BUDGET_FILE, 'r') as j:
                self.budgets = json.load(j)
        else:
            self.budgets = {'budgets': []}

        logging.debug(f"FinanceTracker initialized. BASE_DIR={self.BASE_DIR}")
        logging.debug(f"Loaded {len(self.transactions.get('transactions', []))} transactions and {len(self.budgets.get('budgets', []))} budgets")

        # similarly I could use self.transactions = self.TRANSACTION_FILE.open('r') as f using the pathlib module
        # or I could use self.transactions = json.loads(self.TRANSACTION_FILE.read_text())

    def add_expense(self, args):
        id = len(self.transactions['transactions']) + 1
        date = args.date if args.date else datetime.now().strftime('%Y-%m-%d')

        expense = {
            'id': id,
            'type' : 'expense',
            'date': date,
            'amount': round(args.amount, 2),
            'category': args.category,
            'description': args.description,
        }
        logging.debug(f"Adding expense: {expense}")
        self.transactions['transactions'].insert(0, expense)
        self._save('transaction', self.transactions)

    def add_income(self, args):
        id = len(self.transactions['transactions']) + 1
        date = args.date if args.date else datetime.now().strftime('%Y-%m-%d')

        income = {
            'id': id,
            'type' : 'income',
            'date': date,
            'amount': round(args.amount, 2),
            'category': args.category,
            'description': args.description
        }

        logging.debug(f"Adding income: {income}")
        self.transactions['transactions'].insert(0, income)
        self._save('transaction', self.transactions)

    def list_transactions(self, args):

        transaction_list = self.transactions['transactions']
        logging.debug(f"Listing transactions - total available: {len(transaction_list)}")
        if not transaction_list:
            print('You have no transactions')
            return False

        filtered_list = []

        filters = vars(args)
        filters = {k: v for k, v in filters.items() if v and not k in ['commands', 'start_date', 'end_date', 'func'] }

        logging.debug(f"Applied filters: {filters}")

        for transaction in transaction_list:
            match = True
            tx_date = self._parse_date(transaction.get('date'))

            for key, value in filters.items():
                if transaction[key] != value:
                    match = False
                    break

            if self._date_filter(args, tx_date) and match:
                filtered_list.append(transaction)

            # FASTER ALTERNATIVE PROPOSED BY AI: if all(transaction.get(k) == v for k, v in filters.items()) and self._within_range(args, tx_date): filtered_list.append(transaction)
            # EVEN FASTER: filtered_list = [ tx for tx in transaction_list if self._date_filter(args, tx_date) and all(tx.get(k) == v for k, v in filters.items()]

        sorted_transactions = sorted(filtered_list, key=lambda x: self._parse_date(x.get('date')), reverse=True)

        logging.debug(f"Filtered transactions count: {len(sorted_transactions)}")
        print()
        if sorted_transactions:
            for transaction in sorted_transactions:
                for k, v in transaction.items():
                    print(f'{k}: {v}')
                print('-' * 30)
        else:
            print('No transaction matches these filters')

    def generate_report(self, args):
        transaction_list = self.transactions['transactions']
        month = getattr(args, 'month', None)
        year = args.year

        logging.debug(f"Generating report - month: {month}, year: {year}, total_transactions: {len(transaction_list)}")

        tx_in_month = []
        tx_in_year = []

        for tx in transaction_list:
            date = self._parse_date(tx.get('date'))

            if month and date.month == month and date.year == year:
                tx_in_month.append(tx)

            elif date.year == year:
                tx_in_year.append(tx)

        if month and not tx_in_month:
            print(f'No transaction found for {month}/{year}.')
            return False

        if not month and not tx_in_year:
            print(f'No transaction found for {year}.')
            return False

        filtered_list = tx_in_month if month else tx_in_year
        report = 'Monthly Report' if month else 'Yearly Report'
        final_report = self._report(filtered_list)

        if not month:
            monthly_breakdown = self._monthly_breakdown(tx_in_year)

            print(f'{report}')
            for k, v in final_report.items():
                print(f'{k:<20}: {v}')

            print('=' * 30)
            for month, month_breakdown in monthly_breakdown.items():
                print(f'\n{month}')
                for k, v in month_breakdown.items():
                    print(f'{k:<20}: {v}')
                print('-' * 30)
        else:
            print(f'{report}')
            for k, v in final_report.items():
                print(f'{k:<20}: {v}')

    def category_report(self, args):
        expense_list = [tx for tx in self.transactions['transactions'] if tx.get('type') == 'expense']
        year = args.year
        month = getattr(args, 'month', None)

        logging.debug(f"Category report requested for year={year} month={month} - expense count={len(expense_list)}")

        categories = defaultdict(list)


        for tx in expense_list:
            date = self._parse_date(tx.get('date'))

            if month and date.month == month and date.year == year:
                categories[tx['category']].append(tx)

            elif date.year == year:
                categories[tx['category']].append(tx)

        total_by_cat = {}

        for category, expenses in categories.items():
            total_by_cat[category] = round(sum(tx['amount'] for tx in expenses), 2)

        sorted_total = dict(sorted(total_by_cat.items(), key=lambda x: x[1]))
        total_expenses = sum(sorted_total.values())

        print('Report by Category')

        for k, v in sorted_total.items():
            print(f'{k} : ${v} ({v/total_expenses * 100}%)')

    def set_budget(self, args):
        budgets = self.budgets['budgets']
        id = len(budgets) + 1

        limit = args.limit
        budget_month = args.month
        category = getattr(args, 'category', None)

        month = date.today().month

        # if the month entered is greater than the current month, the budget is set for that month next year
        if args.month < month:
            year = date.today().year + 1
        else:
            year = date.today().year

        logging.debug(f"Setting budget for month={budget_month}({date(year, budget_month, 1).strftime('%Y-%m-%d')}) limit={limit} category={category}")

        budget_exists = False

        for b in budgets:
            if b['start_date'] == date(year, budget_month, 1).strftime("%Y-%m-%d"):
                b[category] = limit
                b.pop('total', None)
                b['total'] = sum(
                    v for k, v in b.items()
                    if k not in ('start_date', 'end_date', 'total')
                )
                budget_exists = True
                break

        if not budget_exists:
            new_budget = {
                'id': id,
                'start_date': date(year, budget_month, 1).strftime('%Y-%m-%d'),
                'end_date': date(year, budget_month, calendar.monthrange(year, budget_month)[1]).strftime('%Y-%m-%d'),
                category: limit,
                'total': limit
            }
            budgets.insert(0, new_budget)
            logging.debug(f"New budget added: {new_budget}")

        self._save('budget', self.budgets)

    def track_budget(self, args):
        expense_list = [tx for tx in self.transactions['transactions'] if tx.get('type') == 'expense']
        latest_budgets = self._select_budget(args)

        logging.debug(f"Tracking budget - found {len(latest_budgets) if latest_budgets else 0} matching budgets and {len(expense_list)} expenses")

        if not latest_budgets:
           print('There are no budgets matching these dates')
           return

        elif not expense_list:
            print('You have no expenses')
            return

        budget_start = min(self._parse_date(b['start_date']) for b in latest_budgets)
        budget_end = max(self._parse_date(b['end_date']) for b in latest_budgets)

        category = getattr(args, 'category', None)

        if category:
            if not any(category in b for b in latest_budgets):
                print(f'{category} was not part of your latest budget.')
                return

        expense_so_far = []

        for tx in expense_list:
            tx_date = self._parse_date(tx.get('date'))

            if category:
                if budget_start <= tx_date <= budget_end and category == tx['category']:
                    expense_so_far.append(tx)
            else:
                if budget_start <= tx_date <= budget_end:
                    expense_so_far.append(tx)

        budget_status = {}
        alert = None

        if category:
            budget_total = sum(b.get(category, 0) for b in latest_budgets)
            total_expense = sum(tx['amount'] for tx in expense_so_far)
            budget_progress = total_expense / budget_total * 100

            budget_status['category'] = category

        else:
            expense_report = self._report(expense_so_far)
            budget_total = sum(b['total'] for b in latest_budgets)
            total_expense = float(expense_report['expenses'])
            if budget_total == 0:
                print('Your budget is 0. Cannot calculate progress')
                return
            else:
                budget_progress = total_expense / budget_total * 100

        if budget_progress > 100:
            alert = f'You have exceeded your budget by ${total_expense - budget_total:.2f}!'
        elif budget_progress == 100:
            alert = 'You have reached your budget!'
        elif 70 < budget_progress < 100:
            alert = "You have almost reached your budget!"

        budget_status['Budget total'] = f'${budget_total:.2f}'
        budget_status['Total expenses'] = f'${total_expense:.2f}'
        budget_status['Progress'] = f'{round(budget_progress)}%'
        if alert: budget_status['Alert'] = alert

        print('Budget Status')

        for k, v in budget_status.items():
            print(f'{k}: {v}')

        logging.debug(f"Budget status: {budget_status}")

    def export_report(self, args):
        expenses = [tx for tx in self.transactions['transactions'] if tx.get('type') == 'expense']
        incomes = [tx for tx in self.transactions['transactions'] if tx.get('type') == 'income']
        category = getattr(args, 'category', None)
        file_name = args.file_name

        if args.month and not args.year:
            print('Please specify the year for the month you entered')
            return

        base_dir = Path(args.file_path).expanduser() if args.file_path else Path.home()/'Documents'

        logging.debug(f"Exporting report to {base_dir} filename={file_name} format={args.format}")

        if not base_dir.exists():
            print('The path you provided does not exist')
            return

        output_path = base_dir/file_name

        if args.format == 'csv' and output_path.suffix != '.csv':
            logging.warning('Filename did not end with .csv, fixing automatically')
            output_path = output_path.with_suffix('.csv')

        elif args.format == 'json' and output_path.suffix != '.json':
            logging.warning('Filename did not end with .json, fixing automatically')
            output_path = output_path.with_suffix('.json')

        if output_path.exists():
            response = input(f"{output_path} exists. Overwrite? [y/N]: ").lower()
            if response != 'y':
                print("Aborted by user.")
                return

        transaction_list = []
        transactions_to_filter = expenses if args.type == 'expense' else incomes

        for tx in transactions_to_filter:
            tx_date = self._parse_date(tx.get('date'))
            if self._date_filter(args, tx_date) and (category is None or tx['category'] == category):
                transaction_list.append(tx)

        if args.format == 'csv':
            self._create_csv(output_path, transaction_list)
            print(f'{file_name} has been created as {output_path}.')

            logging.debug(f"Exported {len(transaction_list)} transactions to CSV: {output_path}")

        elif args.format == 'json':
            self._create_json(output_path, transaction_list)
            print(f'{file_name} has been created as {output_path}.')

            logging.debug(f"Exported {len(transaction_list)} transactions to JSON: {output_path}")

    def _save(self, data_type, data:dict ):
        if data_type == 'transaction':
            file = self.TRANSACTION_FILE
        elif data_type == 'budget':
            file = self.BUDGET_FILE

        logging.debug(f"Saving {data_type} data to {file}")

        with tempfile.NamedTemporaryFile('w', dir=file.parent, delete=False) as tmp:
            json.dump(data, tmp, indent=2)
            temp_name = tmp.name

        os.replace(temp_name, file)

    def _parse_date(self, s):
        return datetime.strptime(s, '%Y-%m-%d').date() if s else None

    def _date_filter(self, args, date) -> bool:

        start_date = self._parse_date(getattr(args, 'start_date', None))
        end_date = self._parse_date(getattr(args, 'end_date', None))
        month = getattr(args, 'month', None)
        year =getattr(args, 'year', None)

        if start_date and date < start_date:
            return False

        if end_date and date > end_date:
            return False

        if month and month != date.month:
            return False

        if year and year != date.year:
            return False

        return True

    def _monthly_breakdown(self, transactions:list) -> dict:
        monthly = defaultdict(list)
        monthly_report = {}

        for tx in transactions:
            date = self._parse_date(tx.get('date'))
            monthly[date.month].append(tx)

        sorted_monthly = dict(sorted(monthly))

        for month, tx in sorted_monthly.items():
            monthly_report[calendar.month_name[month]] = self._report(tx)

        return monthly_report

    def _report(self, tx_lst:list) -> dict:

        total_expenses = round(sum(tx['amount'] for tx in tx_lst if tx.get('type') == 'expense'), 2)
        total_income = round(sum(tx['amount'] for tx in tx_lst if tx.get('type') == 'income'), 2)
        net_savings = total_income - total_expenses

        final_report = {
            'expenses': f'{total_expenses:.2f}',
            'income': f'{total_income:.2f}',
            'savings': f'{net_savings:.2f}',
        }

        categories = [tx['category'] for tx in tx_lst if 'category' in tx]

        if categories:
            most_common_category = Counter(categories).most_common(1)[0][0]
            categories_expense = round(sum(tx['amount'] for tx in tx_lst if tx['category'] == most_common_category), 2)
            final_report['most common expense'] = f'{most_common_category} ({categories_expense})'

        return final_report

    def _select_budget(self, args) -> list:

        budgets = self.budgets['budgets']

        if not any([args.month, args.year, args.start_date, args.end_date]):
            return [budgets[0]]

        else:
            start = self._parse_date(args.start_date)
            end = self._parse_date(args.end_date)

            b_list = []
            for b in budgets:
                b_start = self._parse_date(b['start_date'])
                b_end = self._parse_date(b['end_date'])

                if args.start_date and args.end_date:
                    if b_start <= end and b_end >= start:
                        b_list.append(b)
                else:
                    if self._date_filter(args, b_start) or self._date_filter(args, b_end):
                        b_list.append(b)

            return b_list

    def _create_csv(self, output, data:list):

        with open(output, 'w', newline='') as f:
            fieldnames = ['id', 'type', 'date', 'amount', 'category', 'description']
            writer = csv.DictWriter(f, fieldnames=fieldnames)

            writer.writeheader()
            writer.writerows(data)

    def _create_json(self, output, data:list):

        with open(output, 'w') as f:
            json.dump(data, f, indent=2)

def main():

    tracker = FinanceTracker()

    parser = argparse.ArgumentParser(description='Financial Tracker')
    subparsers = parser.add_subparsers(dest='commands', help='Available commands')


    # ================ ADD COMMAND (DEST: COMMANDS) ================
    add_commands = subparsers.add_parser('add', help='Add transactions')
    add_command_subparser = add_commands.add_subparsers(dest='add_types', help='Transaction types')

    # ========= TRANSACTION TYPES: EXPENSE =========
    expense_parser = add_command_subparser.add_parser('expense', help='Add an expense')
    expense_parser.add_argument('--amount', type=float, help='Expense amount')
    expense_parser.add_argument('--category', type=str, required=True, help='Expense category')
    expense_parser.add_argument('--description', type=str, help='Expense description')
    expense_parser.add_argument('--date', type=str, help='Expense description (YYYY-MM-DD)')
    expense_parser.set_defaults(func=tracker.add_expense)

    # ========= TRANSACTION TYPES: INCOME =========
    income_parser = add_command_subparser.add_parser('income', help="Add an income")
    income_parser.add_argument('--amount', type=float, help='Income amount')
    income_parser.add_argument('--category', required=True,  type=str, help='Income category')
    income_parser.add_argument('--description', type=str, help='Income description')
    income_parser.add_argument('--date', type=str, help='Income date (YYYY-MM-DD)')
    income_parser.set_defaults(func=tracker.add_income)

    # ================ LIST COMMAND ================
    list_parser = subparsers.add_parser('list', help='List transactions')
    list_parser.add_argument('--category', type=str, help='Filter by category')
    list_parser.add_argument('--type', choices=['expense', 'income'], help='Filter by type')
    list_parser.add_argument('--start-date', type=str, help='Start date (YYYY-MM-DD)')
    list_parser.add_argument('--end-date', type=str, help='End date (YYYY-MM-DD)')
    list_parser.add_argument('--month', type=int, choices=range(1,12), help='Filter by month (1-12)')
    list_parser.add_argument('--year', type=int, help='Filter by year')
    list_parser.set_defaults(func=tracker.list_transactions)

    # ================ REPORT COMMAND ================
    report_parser = subparsers.add_parser('report', help='Report transactions')
    report_subparsers = report_parser.add_subparsers(dest='report_type', help='Report types')

    # ======== REPORT TYPES: MONTHLY REPORTS =========
    monthly_parser =  report_subparsers.add_parser('monthly', help='Monthly Summary')
    monthly_parser.add_argument('--month', type=int, choices=range(1,12), required=True, help='Month (1-12)')
    monthly_parser.add_argument('--year', type=int, required=True,  help='Year')
    monthly_parser.set_defaults(func=tracker.generate_report)

    # ======== REPORT TYPES: YEARLY REPORTS ==========
    yearly_parser =  report_subparsers.add_parser('yearly', help='Yearly Summary')
    yearly_parser.add_argument('--year',  required=True,  type=int, help='Year')
    yearly_parser.set_defaults(func=tracker.generate_report)

    # ======== REPORT TYPES: CATEGORY REPORTS ==========
    category_parser =  report_subparsers.add_parser('category', help='Summary by categories')
    category_parser.add_argument('--year',type=int, required=True, help='Year')
    category_parser.add_argument('--month', type=int, help='Month (1-12)')
    category_parser.set_defaults(func=tracker.category_report)

    # =============== BUDGET COMMAND =================
    budget_parser = subparsers.add_parser('budget', help='Set and track budgets')
    budget_subparser = budget_parser.add_subparsers(dest='budget actions', help='Choose action')

    # ========== BUDGET ACTION: SET BUDGET ===========
    set_parser = budget_subparser.add_parser('set', help='Set a budget')
    set_parser.add_argument('--limit', type=float, required=True, help='Set a limit')
    set_parser.add_argument('--month', type=int, choices=range(1,13), required=True, help='Budget month. If the month entered is greater than the current month, the budget is set for that same month, next year')
    set_parser.add_argument('--category', type=str, required=True, help='Choose a category to budget')
    set_parser.set_defaults(func=tracker.set_budget)

    # ========= BUDGET ACTION: BUDGET STATUS =========
    set_parser = budget_subparser.add_parser('status', help='Set a budget')
    set_parser.add_argument('--category', type=str, help='Choose a category to track')
    set_parser.add_argument('--start-date', type=str, help='Start date (YYYY-MM-DD)')
    set_parser.add_argument('--end-date', type=str, help='End date (YYYY-MM-DD)')
    set_parser.add_argument('--month', type=int, help='Filter by month (1-12)')
    set_parser.add_argument('--year', type=int, help='Filter by year')
    set_parser.set_defaults(func=tracker.track_budget)

    # =============== EXPORT COMMANDS ================
    export_parser = subparsers.add_parser('export', help='Export Document')
    export_parser.add_argument('--format', choices=['json', 'csv'], required=True, help='Choose file type')
    export_parser.add_argument('--category', type=str, help='Filter by category')
    export_parser.add_argument('--type', choices=['expense', 'income'], help='Filter by type')
    export_parser.add_argument('--month', type=int, help='Filter by month (1-12)')
    export_parser.add_argument('--year', type=int, help='Filter by year')
    export_parser.add_argument('--file-name', type=str, required=True, help='File name')
    export_parser.add_argument('--file-path', type=str, help='File path')
    export_parser.set_defaults(func=tracker.export_report)


    args = parser.parse_args()

    if hasattr(args, 'func'):
        args.func(args)
    else:
        parser.print_help()

if __name__ == '__main__':
    main()