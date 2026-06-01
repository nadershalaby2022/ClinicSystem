@echo off
title Clinic System - Local Server Control
color 0A
cls

echo ===================================================
echo   🌟 Clinic System الذكي (Plug and Play) 🌟
echo ===================================================
echo.

:: 1. الفحص التلقائي لوجود البايثون في الجهاز
python --version >nul 2>&1
if errorlevel 1 (
    color 0C
    echo [ERROR] البايثون غير مثبت على هذا الجهاز!
    echo برجاء تثبيت Python 3.10 او احدث وتفعيل خيار "Add Python to PATH".
    pause
    exit
)

:: 2. تحديث وتثبيت المكتبات تلقائيا صامتا دون تدخل المستخدم
echo [INFO] جاري التحقق من مكتبات النظام وتحديثها...
pip install -r requirements.txt --quiet
if errorlevel 1 (
    echo [WARNING] حدثت مشكلة اثناء تحديث المكتبات، سيتم محاولة التشغيل على اي حال...
)

echo [SUCCESS] بيئة العمل جاهزة تماما!
echo.
echo ===================================================
echo      🚀 جاري تشغيل خادم العيادة المحلي...
echo ===================================================
echo.

:: 3. تشغيل التطبيق الرئيسي
python app.py

pause