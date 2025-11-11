# Project/urls.py
from django.contrib import admin
from django.urls import path, include
from django.http import HttpResponse

def home(request):
    return HttpResponse("<h2>Welcome to the Employee Attendance & Payroll API</h2>"
                        "<p>Visit <a href='/api/'>/api/</a> to access the API endpoints.</p>")

urlpatterns = [
    path('', home, name='home'),                 # ✅ Root URL (optional, for sanity check)
    path('admin/', admin.site.urls),             # ✅ Django admin
    path('api/', include('hr.urls')),            # ✅ All HR app API routes (employees, payslips, etc.)
]
