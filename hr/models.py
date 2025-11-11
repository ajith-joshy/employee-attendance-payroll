from django.db import models
# Create your models here.
from django.db import models
from django.conf import settings
from django.utils import timezone
from decimal import Decimal

class Department(models.Model):
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=10, blank=True)
    def __str__(self): return self.name

class Employee(models.Model):
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, related_name='employees')
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100, blank=True)
    employee_code = models.CharField(max_length=20, unique=True)
    email = models.EmailField(unique=True)
    date_of_joining = models.DateField()
    is_active = models.BooleanField(default=True)
    # Salary info
    monthly_basic = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    hra = models.DecimalField(max_digits=12, decimal_places=2, default=0)  # house rent allowance
    other_allowances = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    pf_percent = models.DecimalField(max_digits=5, decimal_places=2, default=0)  # e.g., 12.00
    tax_percent = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    def __str__(self): return f"{self.first_name} {self.last_name} ({self.employee_code})"

class Attendance(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='attendances')
    date = models.DateField()
    check_in = models.TimeField(null=True, blank=True)
    check_out = models.TimeField(null=True, blank=True)
    full_day = models.BooleanField(default=True)  # or compute from times
    is_holiday = models.BooleanField(default=False)
    class Meta:
        unique_together = ('employee', 'date')

class LeaveRequest(models.Model):
    PENDING = 'P'
    APPROVED = 'A'
    REJECTED = 'R'
    STATUS_CHOICES = [(PENDING,'Pending'), (APPROVED,'Approved'), (REJECTED,'Rejected')]
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='leaves')
    start_date = models.DateField()
    end_date = models.DateField()
    days = models.DecimalField(max_digits=5, decimal_places=2)
    status = models.CharField(max_length=1, choices=STATUS_CHOICES, default=PENDING)
    unpaid = models.BooleanField(default=False)  # mark if unpaid leave

class OvertimeRecord(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='overtimes')
    date = models.DateField()
    hours = models.DecimalField(max_digits=5, decimal_places=2)
    approved = models.BooleanField(default=False)

class Deduction(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='deductions')
    name = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    reason = models.TextField(blank=True, null=True)
    date = models.DateField(default=timezone.now)

class PayrollPeriod(models.Model):
    year = models.PositiveIntegerField()
    month = models.PositiveIntegerField()  # 1-12
    processed_at = models.DateTimeField(null=True, blank=True)
    finalized = models.BooleanField(default=False)
    class Meta:
        unique_together = ('year','month')

class Payslip(models.Model):
    payroll_period = models.ForeignKey(PayrollPeriod, on_delete=models.CASCADE, related_name='payslips')
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    gross_pay = models.DecimalField(max_digits=12, decimal_places=2)
    total_deductions = models.DecimalField(max_digits=12, decimal_places=2)
    net_pay = models.DecimalField(max_digits=12, decimal_places=2)
    details = models.JSONField(default=dict)  # breakdown: allowances, overtime, taxes, pf, leaves, deductions
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        unique_together = ('payroll_period','employee')
