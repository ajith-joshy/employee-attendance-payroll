# 🧭 Employee Attendance and Payroll Management System (Django API)

## 📝 Project Overview

This project is a Human Resource (HR) Management System** built using Django and Django REST Framework(DRF).  
It manages employee records, attendance, leave tracking, payroll computation, and payslip generation with Excel export functionality.

The system is designed to automate the core HR operations such as tracking employee attendance, calculating salary based on overtime and deductions, and generating payslips in exportable formats.

---

## ⚙️ Key Features

✅ **Employee & Department Management**  
- Create, update, and view employee profiles.  
- Each employee is linked to a department.

✅ **Attendance Tracking**  
- Record daily attendance.  
- Automatically compute total working days and absences.

✅ **Leave Management**  
- Apply and approve/reject employee leaves.  
- Integrates with payroll calculations for leave deductions.

✅ **Payroll & Salary Calculation**  
- Calculates base salary, overtime, and deductions.  
- Generates monthly payslips with detailed breakdowns.

✅ **Payslip Export**  
- Export payslip data to Excel using `openpyxl`.  
- Downloadable from API endpoint.

✅ **RESTful API Endpoints**  
- Full CRUD operations via Django REST Framework.  
- API tested using Postman.

---

## 🏗️ Tech Stack

| Category | Technology |
|-----------|-------------|
| **Backend Framework** | Django 5.x |
| **API Framework** | Django REST Framework |
| **Database** | MySQL / SQLite |
| **Language** | Python 3.11 |
| **Libraries Used** | `openpyxl`, `mysqlclient`, `djangorestframework`, `django-crispy-forms` |
| **IDE / Tools** | PyCharm, Postman |

---

## 📁 Project Structure

