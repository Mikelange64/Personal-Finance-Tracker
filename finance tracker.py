import argparse
import os
import csv
import json
from csv import DictWriter
from datetime import datetime, timezone
import time


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
            'amount': args.amount,
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
            'amount': args.amount,
            'category': args.category,
        }

        self.transactions['transaction'].append(income)

    def list_transactions(self, args):

        transaction_list = self.transactions['transactions']
        filtered_list = []
        target = 0

        filters = vars(args)
        filters = {k: v for k, v in filters.items() if filters[k] or k in  ['commands', 'start_date', 'end_date']}

        for key in ['commands', 'start_date', 'end_date']:
            if key in filters:
                del filters[key]

        for transaction in transaction_list:
            transaction_date = self._parse_date(transaction.get('date'))

            for key, value in filters.items():
                if transaction[key] == value:
                    target += 1

            if self._within_range(args, transaction_date) and target == len(filters):
                filtered_list.append(transaction)

        for transaction in filtered_list:
            print(transaction)

    def _within_range(self, args, date):
        filters = vars(args)

        start_date = self._parse_date(filters.get('start_date'))
        end_date = self._parse_date(filters.get('end_date'))

        if not start_date and not end_date:
                return False

        if start_date and date < start_date:
            return False


        if end_date and date > end_date:
            return False

        return True

    def _parse_date(self, s):
        return datetime.strptime(s, '%Y-%m-%d').date() if s else None







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
    expense_parser.add_argument('--category', type=str, help='Expense category')
    expense_parser.add_argument('--description', type=str, help='Expense description')
    expense_parser.add_argument('--date', type=str, help='Expense description (YYYY-MM-DD)')
    expense_parser.set_defaults(func=tracker.add_expense)

    # ========= TRANSACTION TYPES: INCOME =========
    income_parser = add_command_subparser.add_parser('income', help="Add an income")
    income_parser.add_argument('--amount', type=float, help='Income amount')
    income_parser.add_argument('--category', type=str, help='Income category')
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
    monthly_parser.add_argument('--month', type=int, help='Month (1-12)')
    monthly_parser.add_argument('--year', type=int, help='Year')

    # ======== REPORT TYPES: YEARLY REPORTS ==========
    yearly_parser =  report_subparsers.add_parser('yearly', help='Monthly Summary')
    yearly_parser.add_argument('--year', type=int, help='Year')

    # =============== EXPORT COMMANDS ================
    export_parser = subparsers.add_parser('export', help='Export Document')
    export_parser.add_argument('--format', choices=['json', 'csv'], required=True, help='Choose file type')
    export_parser.add_argument('--category', type=str, help='Filter by category')
    export_parser.add_argument('--type', choices=['expense', 'income'], help='Filter by type')
    export_parser.add_argument('--month', type=int, help='Filter by month (1-12)')
    export_parser.add_argument('--year', type=int, help='Filter by year')


    args = parser.parse_args()

if __name__ == '__main__':
    main()






