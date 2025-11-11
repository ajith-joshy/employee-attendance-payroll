# Project/hr/management/commands/run_payroll.py
from django.core.management.base import BaseCommand
from hr.payroll import generate_payroll_for_period

class Command(BaseCommand):
    help = 'Generate payroll for a given year and month'

    def add_arguments(self, parser):
        parser.add_argument('--year', type=int, required=True, help='Year, e.g. 2025')
        parser.add_argument('--month', type=int, required=True, help='Month number (1-12)')
        parser.add_argument('--finalize', action='store_true', help='Finalize the payroll period')

    def handle(self, *args, **options):
        year = options['year']
        month = options['month']
        finalize = options['finalize']
        payslips = generate_payroll_for_period(year, month, finalize=finalize)
        self.stdout.write(self.style.SUCCESS(f'Generated {len(payslips)} payslips for {year}-{month:02d}'))
