import argparse
import os
import csv
import json
from datetime import datetime, timezone
from collections import Counter, defaultdict
import calendar


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

        total_expenses = round(sum(tx['expense'] for tx in tx_lst if 'expense' in tx), 2)
        total_income = round(sum(tx['income'] for tx in tx_lst if 'income' in tx), 2)
        net_savings = total_income - total_expenses

        final_report = {
            'expenses': total_expenses,
            'income': total_income,
            'savings': net_savings,
        }

        categories = [tx['category'] for tx in tx_lst if 'category' in tx]

        if categories:
            most_common_category = Counter(categories).most_common(1)[0][0]
            categories_expense = round(sum(tx['expense'] for tx in tx_lst if tx['category'] == most_common_category), 2)
            final_report['most common expense'] = f'{most_common_category} ({categories_expense})'

        return final_report

    def category_report(self, args):
        expense_list = [tx for tx in self.transactions['transactions'] if 'expense' in tx]
        year = args.year
        month = getattr(args, 'month', None)

        categories = defaultdict(list)


        for tx in expense_list:
            date = self._parse_date(tx.get('date'))

            if month and date.month == month and date.year == year:
                categories[tx['category']].append(tx)

            elif date.year == year:
                categories[tx['category']].append(tx)

        total_by_cat = {}

        for category, expenses in categories.items():
            total_by_cat[category] = round(sum(tx['expense'] for tx in expenses), 2)

        sorted_total = dict(sorted(total_by_cat.items(), key=lambda x: x[1]))
        total_expenses = sum(sorted_total.values())

        print('Report by Category')

        for k, v in sorted_total.items():
            print(f'{k} : ${v} ({v/total_expenses * 100}%)')


































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
    yearly_parser =  report_subparsers.add_parser('yearly', help='Yearly Summary')
    yearly_parser.add_argument('--year',  required=True,  type=int, help='Year')
    yearly_parser.set_defaults(func=tracker.generate_report)

    # ======== REPORT TYPES: CATEGORY REPORTS ==========
    category_parser =  report_subparsers.add_parser('category', help='Summary by categories')
    category_parser.add_argument('--year',type=int, required=True, help='Year')
    category_parser.add_argument('--month', type=int, help='Month (1-12)')
    category_parser.set_defaults(func=tracker.category_report)

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






