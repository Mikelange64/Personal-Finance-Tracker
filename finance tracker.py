import argparse
import os
import csv
import json
from datetime import datetime, timezone
from collections import Counter


class FinanceTracker:

    def __init__(self):
        self.transactions = {'transactions': []}

    def add_expense(self, args):
        id = len(self.transactions['transaction']) + 1
        date = args.date if args.date else datetime.now().strftime('%Y-%m-%d')

        expense = {
            'id': id,
            'type' : 'expense',
            'date': date,
            'amount': round(args.amount, 2),
            'category': args.category,
            'description': args.description,
        }

        self.transactions['transaction'].append(expense)

    def add_income(self, args):
        id = len(self.transactions['transaction']) + 1
        date = args.date if args.date else datetime.now().strftime('%Y-%m-%d')

        income = {
            'id': id,
            'type' : 'income',
            'date': date,
            'amount': round(args.amount, 2),
            'category': args.category,
        }

        self.transactions['transaction'].append(income)

    def list_transactions(self, args):

        transaction_list = self.transactions['transactions']
        if not transaction_list:
            print('You have no transactions')
            return False

        filtered_list = []

        filters = vars(args)
        filters = {k: v for k, v in filters.items() if v and not k in ['commands', 'start_date', 'end_date', 'func'] }

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
            # EVEN FASTER: filtered_list = [ tx for tx in transaction_list if self._within_range(args, tx_date) and all(tx.get(k) == v for k, v in filters.items()]

        sorted_transactions = sorted(filtered_list, key=lambda x: self._parse_date(x.get('date')))

        if sorted_transactions:
            for transaction in sorted_transactions:
                print(transaction)
        else:
            print('No transaction matches these filters')

    def _date_filter(self, args, date) -> bool:

        start_date = self._parse_date(args.start_date)
        end_date = self._parse_date(args.end_date)
        month = args.month
        year = args.year

        if start_date and date < start_date:
            return False

        if end_date and date > end_date:
            return False

        if month and month != date.month:
            return False

        if year and year != date.year:
            return False

        return True

    def _parse_date(self, s):
        return datetime.strptime(s, '%Y-%m-%d').date() if s else None

    def generate_report(self, args):
        transaction_list = self.transactions['transactions']
        month = getattr(args, 'month', None)
        year = args.year
        monthly_tx = []
        yearly_tx = []

        for tx in transaction_list:
            date = self._parse_date(tx.get('date'))

            if month and date.month == month and date.year == year:
                monthly_tx.append(tx)

            elif date.year == year:
                yearly_tx.append(tx)

        if month and not monthly_tx:
            print(f'No transaction found for {month}/{year}.')
            return False

        if not month and not yearly_tx:
            print(f'No transaction found for {year}.')
            return False

        filtered_list = monthly_tx if month else yearly_tx

        total_expenses = round(sum(tx['expense'] for tx in filtered_list if 'expense' in tx), 2)
        total_income = round(sum(tx['income'] for tx in filtered_list if 'income' in tx), 2)
        net_savings = total_income - total_expenses

        final_report = {
            'expenses': total_expenses,
            'income': total_income,
            'savings': net_savings,
        }

        categories = [tx['category'] for tx in filtered_list if 'category' in tx]

        if categories:
            most_common_category = Counter(categories).most_common(1)[0][0]
            categories_expense = round(sum(tx['expense'] for tx in filtered_list if tx['category'] == most_common_category), 2)
            final_report['most common expense'] = f'{most_common_category} ({categories_expense})'

        report = 'Monthly Report' if month else 'Yearly Report'
        print(f'\n{report}')
        for k, v in final_report.items():
            print(f'{k:<20}: {v}')






























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
    income_parser.add_argument('--date', type=str, help='Income date (YYYY-MM-DD)')
    income_parser.set_defaults(func=tracker.add_income)

    # ================ LIST COMMAND ================
    list_parser = subparsers.add_parser('list', help='List transactions')
    list_parser.add_argument('--category', type=str, help='Filter by category')
    list_parser.add_argument('--type', choices=['expense', 'income'], help='Filter by type')
    list_parser.add_argument('--start-date', type=str, help='Start date (YYYY-MM-DD)')
    list_parser.add_argument('--end-date', type=str, help='End date (YYYY-MM-DD)')
    list_parser.add_argument('--month', type=int, help='Filter by month (1-12)')
    list_parser.add_argument('--year', type=int, help='Filter by year')
    list_parser.set_defaults(func=tracker.list_transactions)

    # ================ REPORT COMMAND ================
    report_parser = subparsers.add_parser('report', help='Report transactions')
    report_subparsers = report_parser.add_subparsers(dest='report_type', help='Report types')

    # ======== REPORT TYPES: MONTHLY REPORTS =========
    monthly_parser =  report_subparsers.add_parser('monthly', help='Monthly Summary')
    monthly_parser.add_argument('--month', type=int, required=True, help='Month (1-12)')
    monthly_parser.add_argument('--year', type=int, required=True,  help='Year')
    monthly_parser.set_defaults(func=tracker.generate_report)

    # ======== REPORT TYPES: YEARLY REPORTS ==========
    yearly_parser =  report_subparsers.add_parser('yearly', help='Monthly Summary')
    yearly_parser.add_argument('--year',  required=True,  type=int, help='Year')
    yearly_parser.set_defaults(func=tracker.generate_report)

    # =============== EXPORT COMMANDS ================
    export_parser = subparsers.add_parser('export', help='Export Document')
    export_parser.add_argument('--format', choices=['json', 'csv'], required=True, help='Choose file type')
    export_parser.add_argument('--category', type=str, help='Filter by category')
    export_parser.add_argument('--type', choices=['expense', 'income'], help='Filter by type')
    export_parser.add_argument('--month', type=int, help='Filter by month (1-12)')
    export_parser.add_argument('--year', type=int, help='Filter by year')


    args = parser.parse_args()

    if hasattr(args, 'func'):
        args.func(args)
    else:
        parser.print_help()


if __name__ == '__main__':
    main()






