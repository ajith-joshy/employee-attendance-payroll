# Register your models here.
from django.contrib import admin
from .models import Department, Employee, Attendance, LeaveRequest, OvertimeRecord, Deduction, PayrollPeriod, Payslip

admin.site.register(Department)
admin.site.register(Employee)
admin.site.register(Attendance)
admin.site.register(LeaveRequest)
admin.site.register(OvertimeRecord)
admin.site.register(Deduction)
admin.site.register(PayrollPeriod)
admin.site.register(Payslip)