# Project/hr/views.py
import csv
import json

from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string
from django.http import HttpResponse

from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response

# Models
from .models import (
    Department, Employee, Attendance, LeaveRequest, OvertimeRecord,
    Deduction, Payslip, PayrollPeriod
)

# Serializers
from .serializers import (
    DepartmentSerializer, EmployeeSerializer,
    AttendanceSerializer, LeaveRequestSerializer,
    OvertimeRecordSerializer, DeductionSerializer,
    PayslipSerializer, PayrollPeriodSerializer
)

# Payroll logic
from .payroll import generate_payroll_for_period
try:
    from weasyprint import HTML
except Exception:
    HTML = None

import openpyxl

# Permissions
class IsHROrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return bool(request.user and request.user.is_staff)


class IsOwnerOrHR(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.user and request.user.is_staff:
            return True
        try:
            if hasattr(obj, 'employee'):
                return obj.employee.email == request.user.email
            if isinstance(obj, Employee):
                return obj.email == request.user.email
        except Exception:
            pass
        return False


# Core ViewSets
class EmployeeViewSet(viewsets.ModelViewSet):
    queryset = Employee.objects.all()
    serializer_class = EmployeeSerializer
    permission_classes = [IsHROrReadOnly]

class DepartmentViewSet(viewsets.ModelViewSet):
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer
    permission_classes = [IsHROrReadOnly]  # reuse existing permission class (read for all, write for staff)


class PayslipViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Payslip.objects.all().select_related('employee', 'payroll_period')
    serializer_class = PayslipSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        qs = super().get_queryset()
        if user.is_authenticated and user.is_staff:
            return qs
        if user.is_authenticated:
            return qs.filter(employee__email=user.email)
        return qs.none()

    @action(detail=False, methods=['post'], permission_classes=[permissions.IsAdminUser])
    def generate(self, request):
        try:
            year = int(request.data.get('year'))
            month = int(request.data.get('month'))
        except (TypeError, ValueError):
            return Response({'detail': 'year and month are required integer values.'}, status=status.HTTP_400_BAD_REQUEST)

        finalize = bool(request.data.get('finalize', False))
        payslips = generate_payroll_for_period(year, month, finalize=finalize)
        serializer = PayslipSerializer(payslips, many=True)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


# Attendance / Leave / Overtime / Deduction ViewSets
class AttendanceViewSet(viewsets.ModelViewSet):
    queryset = Attendance.objects.all().select_related('employee')
    serializer_class = AttendanceSerializer
    permission_classes = [IsHROrReadOnly]


class LeaveRequestViewSet(viewsets.ModelViewSet):
    queryset = LeaveRequest.objects.all().select_related('employee')
    serializer_class = LeaveRequestSerializer
    permission_classes = [IsHROrReadOnly]


class OvertimeRecordViewSet(viewsets.ModelViewSet):
    queryset = OvertimeRecord.objects.all().select_related('employee')
    serializer_class = OvertimeRecordSerializer
    permission_classes = [IsHROrReadOnly]


class DeductionViewSet(viewsets.ModelViewSet):
    queryset = Deduction.objects.all().select_related('employee')
    serializer_class = DeductionSerializer
    permission_classes = [IsHROrReadOnly]


# Export endpoints (CSV, XLSX, PDF)
@api_view(['GET'])
@permission_classes([permissions.IsAdminUser])
def export_payslips_csv(request, year, month):
    period = PayrollPeriod.objects.filter(year=year, month=month).first()
    if not period:
        return HttpResponse("No payroll data found for this period.", status=404)

    payslips = Payslip.objects.filter(payroll_period=period).select_related('employee')

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="payslips_{year}_{month}.csv"'

    writer = csv.writer(response)
    writer.writerow(['Employee Code', 'Employee Name', 'Gross Pay', 'Total Deductions', 'Net Pay', 'Details'])

    for p in payslips:
        writer.writerow([
            p.employee.employee_code,
            f"{p.employee.first_name} {p.employee.last_name}",
            str(p.gross_pay),
            str(p.total_deductions),
            str(p.net_pay),
            json.dumps(p.details),
        ])
    return response


@api_view(['GET'])
@permission_classes([permissions.IsAdminUser])
def export_payslips_xlsx(request, year, month):
    period = PayrollPeriod.objects.filter(year=year, month=month).first()
    if not period:
        return HttpResponse("No payroll data found for this period.", status=404)

    payslips = Payslip.objects.filter(payroll_period=period).select_related('employee')

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.append(['Employee Code', 'Employee Name', 'Gross Pay', 'Total Deductions', 'Net Pay'])

    for p in payslips:
        ws.append([
            p.employee.employee_code,
            f"{p.employee.first_name} {p.employee.last_name}",
            float(p.gross_pay),
            float(p.total_deductions),
            float(p.net_pay),
        ])

    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = f'attachment; filename=payslips_{year}_{month}.xlsx'
    wb.save(response)
    return response


@api_view(['GET'])
@permission_classes([permissions.IsAdminUser])
def payslip_pdf(request, payslip_id):
    p = get_object_or_404(Payslip, pk=payslip_id)
    if HTML is None:
        return HttpResponse("WeasyPrint not available. Install weasyprint and its system deps.", status=500)

    html_string = render_to_string('hr/payslip_template.html', {'p': p})
    pdf = HTML(string=html_string).write_pdf()
    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="payslip_{p.employee.employee_code}_{p.payroll_period}.pdf"'
    return response
