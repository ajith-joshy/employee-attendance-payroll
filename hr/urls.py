# Project/hr/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    DepartmentViewSet, EmployeeViewSet, PayslipViewSet,
    AttendanceViewSet, LeaveRequestViewSet, OvertimeRecordViewSet, DeductionViewSet,
    export_payslips_csv, export_payslips_xlsx, payslip_pdf
)

router = DefaultRouter()
router.register(r'departments', DepartmentViewSet, basename='department')
router.register(r'employees', EmployeeViewSet, basename='employee')
router.register(r'payslips', PayslipViewSet, basename='payslip')
router.register(r'attendance', AttendanceViewSet, basename='attendance')
router.register(r'leaves', LeaveRequestViewSet, basename='leaverequest')
router.register(r'overtime', OvertimeRecordViewSet, basename='overtime')
router.register(r'deductions', DeductionViewSet, basename='deduction')

urlpatterns = [
    path('', include(router.urls)),
    path('export/<int:year>/<int:month>/', export_payslips_csv, name='export_payslips_csv'),
    path('export/xlsx/<int:year>/<int:month>/', export_payslips_xlsx, name='export_payslips_xlsx'),
    path('payslip/<int:payslip_id>/pdf/', payslip_pdf, name='payslip_pdf'),
]
