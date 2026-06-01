@echo off
title ClinicSystem Project Builder

set ROOT=E:\ClinicSystem

echo Creating project structure...

:: Root Files
type nul > "%ROOT%\app.py"
type nul > "%ROOT%\config.py"
type nul > "%ROOT%\requirements.txt"
type nul > "%ROOT%\Start.bat"

:: Database
mkdir "%ROOT%\database"
mkdir "%ROOT%\database\backup"
mkdir "%ROOT%\database\scripts"
type nul > "%ROOT%\database\clinic.db"

:: Views
mkdir "%ROOT%\view"

mkdir "%ROOT%\view\common"
type nul > "%ROOT%\view\common\login.html"
type nul > "%ROOT%\view\common\dashboard.html"
type nul > "%ROOT%\view\common\error.html"

mkdir "%ROOT%\view\reception"
type nul > "%ROOT%\view\reception\patient_register.html"
type nul > "%ROOT%\view\reception\waiting_list.html"
type nul > "%ROOT%\view\reception\appointments.html"
type nul > "%ROOT%\view\reception\reception_dashboard.html"

mkdir "%ROOT%\view\doctor"
type nul > "%ROOT%\view\doctor\doctor_dashboard.html"
type nul > "%ROOT%\view\doctor\patient_profile.html"
type nul > "%ROOT%\view\doctor\prescription.html"
type nul > "%ROOT%\view\doctor\medical_notes.html"
type nul > "%ROOT%\view\doctor\reports.html"

mkdir "%ROOT%\view\tv"
type nul > "%ROOT%\view\tv\queue_screen.html"
type nul > "%ROOT%\view\tv\ads_screen.html"

mkdir "%ROOT%\view\admin"
type nul > "%ROOT%\view\admin\users.html"
type nul > "%ROOT%\view\admin\settings.html"
type nul > "%ROOT%\view\admin\sponsors.html"

:: Static
mkdir "%ROOT%\static"

mkdir "%ROOT%\static\css"
type nul > "%ROOT%\static\css\style.css"
type nul > "%ROOT%\static\css\reception.css"
type nul > "%ROOT%\static\css\doctor.css"
type nul > "%ROOT%\static\css\tv.css"

mkdir "%ROOT%\static\js"
type nul > "%ROOT%\static\js\app.js"
type nul > "%ROOT%\static\js\queue.js"
type nul > "%ROOT%\static\js\doctor.js"
type nul > "%ROOT%\static\js\ads.js"

mkdir "%ROOT%\static\audio"
type nul > "%ROOT%\static\audio\next_patient.mp3"
type nul > "%ROOT%\static\audio\notification.mp3"

mkdir "%ROOT%\static\images"

mkdir "%ROOT%\static\images\sponsors"

mkdir "%ROOT%\static\images\clinic"
type nul > "%ROOT%\static\images\clinic\logo.png"
type nul > "%ROOT%\static\images\clinic\doctor.jpg"
type nul > "%ROOT%\static\images\clinic\reception_bg.jpg"
type nul > "%ROOT%\static\images\clinic\banner.jpg"

mkdir "%ROOT%\static\images\system"
mkdir "%ROOT%\static\images\system\icons"
mkdir "%ROOT%\static\images\system\default"

:: Assets
mkdir "%ROOT%\static\assets"
mkdir "%ROOT%\static\assets\clinic_logo"
mkdir "%ROOT%\static\assets\doctor_signature"
mkdir "%ROOT%\static\assets\doctor_stamp"
mkdir "%ROOT%\static\assets\reports"
mkdir "%ROOT%\static\assets\uploads"

:: Controllers
mkdir "%ROOT%\controllers"
type nul > "%ROOT%\controllers\reception_controller.py"
type nul > "%ROOT%\controllers\doctor_controller.py"
type nul > "%ROOT%\controllers\tv_controller.py"
type nul > "%ROOT%\controllers\sponsor_controller.py"
type nul > "%ROOT%\controllers\auth_controller.py"

:: Models
mkdir "%ROOT%\models"
type nul > "%ROOT%\models\patient.py"
type nul > "%ROOT%\models\appointment.py"
type nul > "%ROOT%\models\queue.py"
type nul > "%ROOT%\models\sponsor.py"
type nul > "%ROOT%\models\user.py"

:: Services
mkdir "%ROOT%\services"
type nul > "%ROOT%\services\queue_service.py"
type nul > "%ROOT%\services\audio_service.py"
type nul > "%ROOT%\services\backup_service.py"
type nul > "%ROOT%\services\auth_service.py"
type nul > "%ROOT%\services\report_service.py"

:: Modules
mkdir "%ROOT%\modules"
mkdir "%ROOT%\modules\dental"
mkdir "%ROOT%\modules\pediatric"
mkdir "%ROOT%\modules\dermatology"
mkdir "%ROOT%\modules\ophthalmology"
mkdir "%ROOT%\modules\cardiology"

:: Logs
mkdir "%ROOT%\logs"
type nul > "%ROOT%\logs\app.log"
type nul > "%ROOT%\logs\errors.log"

:: Exports
mkdir "%ROOT%\exports"
mkdir "%ROOT%\exports\pdf"
mkdir "%ROOT%\exports\excel"
mkdir "%ROOT%\exports\reports"

:: Docs
mkdir "%ROOT%\docs"
type nul > "%ROOT%\docs\manual.pdf"
type nul > "%ROOT%\docs\installation.pdf"

echo.
echo =====================================
echo Project Created Successfully
echo =====================================
pause