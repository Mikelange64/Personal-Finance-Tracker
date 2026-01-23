import argparse
import os
import csv
import json
from datetime import datetime, timezone


class FinanceTracker:

    def __init__(self):

        self.parser = argparse.ArgumentParser(description='Financial Tracker')
        self.subparsers = self.parser.add_subparsers(dest='commands', help='Available commands')

        # ================ ADD COMMAND ================
        self.add_commands = self.subparsers.add_parser('add', help='Add transactions')
        self.add_command_subparser = self.add_commands.add_subparsers(dest='add_types', help='Transaction types')

        # ========= TRANSACTION TYPES: EXPENSE =========
        self.expense_parser = self.add_command_subparser.add_parser('expense', help='Add an expense')
        self.expense_parser.add_argument('--amount', type=float, help='Expense amount')
        self.expense_parser.add_argument('--category', type=str, help='Expense category')
        self.expense_parser.add_argument('--description', type=str, help='Expense description')
        self.expense_parser.add_argument('--date', type=str, help='Expense description (YYYY-MM-DD)')

        # ========= TRANSACTION TYPES: INCOME =========
        self.income_parser = self.add_command_subparser.add_parser('income', help="Add an income")
        self.income_parser.add_argument('--amount', type=float, help='Income amount')
        self.income_parser.add_argument('--category', type=str, help='Income category')
        self.income_parser.add_argument('--date', type=str, help='Income date (YYYY-MM-DD)')

        # ================ LIST COMMAND ================
        self.list_parser = self.subparsers.add_parser('list', help='List transactions')
        self.list_parser.add_argument('--category', type=str, help='Filter by category')
        self.list_parser.add_argument('--type', choices=['expense', 'income'], help='Filter by type')
        self.list_parser.add_argument('--start-date', type=str, help='Start date (YYYY-MM-DD)')
        self.list_parser.add_argument('--end-date', type=str, help='End date (YYYY-MM-DD)')
        self.list_parser.add_argument('--month', type=int, help='Filter by month (1-12)')
        self.list_parser.add_argument('--year', type=int, help='Filter by year')

        # ================ REPORT COMMAND ================
        self.report_parser = self.subparsers.add_parser('report', help='Report transactions')
        self.report_subparsers = self.report_parser.add_subparsers(dest='report_type', help='Report types')

        # ======== REPORT TYPES: MONTHLY REPORTS =========
        self.monthly_parser =  self.report_subparsers.add_parser('monthly', help='Monthly Summary')
        self.monthly_parser.add_argument('--month', type=int, help='Month (1-12)')
        self.monthly_parser.add_argument('--year', type=int, help='Year')

        # ======== REPORT TYPES: YEARLY REPORTS ==========
        self.yearly_parser =  self.report_subparsers.add_parser('yearly', help='Monthly Summary')
        self.yearly_parser.add_argument('--year', type=int, help='Year')

        # =============== EXPORT COMMANDS ================
        self.export_parser = self.subparsers.add_parser('export', help='Export Document')
        self.export_parser.add_argument('--format', choices=['json', 'csv'], required=True, help='Choose file type')
        self.export_parser.add_argument('--category', type=str, help='Filter by category')
        self.export_parser.add_argument('--type', choices=['expense', 'income'], help='Filter by type')
        self.export_parser.add_argument('--month', type=int, help='Filter by month (1-12)')
        self.export_parser.add_argument('--year', type=int, help='Filter by year')




