# Project/hr/serializers.py
from rest_framework import serializers
from .models import (
    Department, Employee, Payslip, PayrollPeriod,
    Attendance, LeaveRequest, OvertimeRecord, Deduction
)

class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = '__all__'

class EmployeeSerializer(serializers.ModelSerializer):
    department = DepartmentSerializer(read_only=True)
    department_id = serializers.PrimaryKeyRelatedField(
        queryset=Department.objects.all(), source='department', write_only=True, required=False
    )

    class Meta:
        model = Employee
        fields = '__all__'

class AttendanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attendance
        fields = '__all__'

class OvertimeRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = OvertimeRecord
        fields = '__all__'

class DeductionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Deduction
        fields = '__all__'

class LeaveRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = LeaveRequest
        fields = '__all__'
        read_only_fields = ('days',)

    def validate(self, data):
        start = data.get('start_date', getattr(self.instance, 'start_date', None))
        end = data.get('end_date', getattr(self.instance, 'end_date', None))
        if start and end and end < start:
            raise serializers.ValidationError("end_date must be the same or after start_date")
        return data

    def _calc_days(self, start, end):
        return (end - start).days + 1

    def create(self, validated_data):
        start = validated_data['start_date']
        end = validated_data['end_date']
        validated_data['days'] = self._calc_days(start, end)
        return super().create(validated_data)

    def update(self, instance, validated_data):
        start = validated_data.get('start_date', instance.start_date)
        end = validated_data.get('end_date', instance.end_date)
        validated_data['days'] = self._calc_days(start, end)
        return super().update(instance, validated_data)

class PayrollPeriodSerializer(serializers.ModelSerializer):
    class Meta:
        model = PayrollPeriod
        fields = '__all__'

class PayslipSerializer(serializers.ModelSerializer):
    employee = EmployeeSerializer(read_only=True)
    payroll_period = PayrollPeriodSerializer(read_only=True)

    class Meta:
        model = Payslip
        fields = '__all__'
