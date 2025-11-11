from decimal import Decimal, ROUND_HALF_UP
from calendar import monthrange
from django.db import transaction
from django.utils import timezone
from .models import Employee, PayrollPeriod, Payslip, OvertimeRecord, Deduction, LeaveRequest, Attendance

def _quant(x):
    return Decimal(x).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

def generate_payslip_for_employee(employee: Employee, year: int, month: int, overtime_rate=Decimal('1.5'), daily_hours=Decimal('8')):
    # base_salary_components
    basic = Decimal(employee.monthly_basic)
    hra = Decimal(employee.hra)
    other_allowances = Decimal(employee.other_allowances)
    gross = _quant(basic + hra + other_allowances)

    # month_info
    days_in_month = monthrange(year, month)[1]

    # overtime
    ots = OvertimeRecord.objects.filter(employee=employee, date__year=year, date__month=month, approved=True)
    total_ot_hours = sum([o.hours for o in ots]) if ots else Decimal('0')
    # per-hour basic rate = basic / (working_days * daily_hours). For simplicity use calendar days.
    per_hour_rate = (basic / Decimal(days_in_month)) / daily_hours
    overtime_pay = _quant(Decimal(total_ot_hours) * per_hour_rate * Decimal(overtime_rate))

    # unpaid_leaves
    unpaid_leaves = LeaveRequest.objects.filter(employee=employee, status=LeaveRequest.APPROVED, unpaid=True,
                                                start_date__year=year, start_date__month=month)
    unpaid_days = sum([lr.days for lr in unpaid_leaves]) if unpaid_leaves else Decimal('0')
    unpaid_deduction = _quant((gross / Decimal(days_in_month)) * Decimal(unpaid_days))

    # fixed/variable manual deductions in this month
    manual_deds = Deduction.objects.filter(employee=employee, date__year=year, date__month=month)
    manual_total = sum([d.amount for d in manual_deds]) if manual_deds else Decimal('0')
    manual_total = _quant(manual_total)

    # statutory
    pf = _quant(basic * (Decimal(employee.pf_percent) / Decimal('100'))) if employee.pf_percent else Decimal('0')
    tax = _quant(gross * (Decimal(employee.tax_percent) / Decimal('100'))) if employee.tax_percent else Decimal('0')

    total_deductions = _quant(pf + tax + manual_total + unpaid_deduction)
    net_pay = _quant(gross + overtime_pay - total_deductions)

    details = {
        'basic': str(basic),
        'hra': str(hra),
        'other_allowances': str(other_allowances),
        'overtime_hours': str(total_ot_hours),
        'overtime_pay': str(overtime_pay),
        'pf': str(pf),
        'tax': str(tax),
        'manual_deductions': str(manual_total),
        'unpaid_deduction': str(unpaid_deduction),
        'days_in_month': days_in_month,
    }

    return {
        'gross': gross,
        'overtime_pay': overtime_pay,
        'total_deductions': total_deductions,
        'net_pay': net_pay,
        'details': details
    }

@transaction.atomic
def generate_payroll_for_period(year: int, month: int, finalize=False):
    period, created = PayrollPeriod.objects.get_or_create(year=year, month=month)
    employees = Employee.objects.filter(is_active=True)
    results = []
    for emp in employees:
        calc = generate_payslip_for_employee(emp, year, month)
        payslip, created = Payslip.objects.update_or_create(
            payroll_period=period,
            employee=emp,
            defaults={
                'gross_pay': calc['gross'],
                'total_deductions': calc['total_deductions'],
                'net_pay': calc['net_pay'],
                'details': calc['details']
            }
        )
        results.append(payslip)
    if finalize:
        period.finalized = True
        period.processed_at = timezone.now()
        period.save()
    return results
