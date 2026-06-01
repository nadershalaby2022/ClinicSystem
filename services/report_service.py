from datetime import datetime
from html import escape
import os
import re
import zipfile

from flask import current_app

from app import db
from models.medical_record import MedicalRecord
from models.patient import Patient


INVALID_FILENAME_CHARS = r'<>:"/\|?*'


def safe_name(value):
    cleaned = ''.join('_' if char in INVALID_FILENAME_CHARS else char for char in value.strip())
    cleaned = re.sub(r'\s+', '_', cleaned)
    return cleaned or 'patient'


def patient_report_folder(patient):
    patient.ensure_reference_number()
    folder_name = f'{safe_name(patient.reference_number)}_{safe_name(patient.name)}'
    folder = os.path.join(current_app.config['BASE_DIR'], 'exports', 'history', folder_name)
    os.makedirs(folder, exist_ok=True)
    return folder


def prescription_html(record):
    patient = record.patient
    doctor = record.doctor.full_name if record.doctor else 'طبيب العيادة'
    created = record.created_at.strftime('%Y-%m-%d %H:%M')
    return f"""<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <title>روشتة {escape(patient.name)}</title>
    <style>
        body {{ font-family: Tahoma, Arial, sans-serif; margin: 32px; color: #14213d; }}
        .rx {{ max-width: 850px; margin: auto; border: 1px solid #d9e2ec; padding: 28px; border-radius: 12px; }}
        .header {{ display: flex; justify-content: space-between; border-bottom: 2px solid #0ea5e9; padding-bottom: 16px; }}
        h1 {{ margin: 0; color: #0f766e; }}
        .meta, .section {{ margin-top: 18px; }}
        .grid {{ display: grid; grid-template-columns: repeat(2, 1fr); gap: 10px; }}
        .label {{ color: #64748b; font-size: 13px; }}
        .box {{ background: #f8fafc; padding: 14px; border-radius: 10px; min-height: 70px; white-space: pre-wrap; }}
        .footer {{ margin-top: 32px; display: flex; justify-content: space-between; color: #475569; }}
        @media print {{ body {{ margin: 0; }} .rx {{ border: 0; }} .no-print {{ display: none; }} }}
    </style>
</head>
<body>
    <button class="no-print" onclick="window.print()">طباعة</button>
    <article class="rx">
        <div class="header">
            <div>
                <h1>روشتة طبية</h1>
                <p>ClinicSystem - نظام إدارة العيادة</p>
            </div>
            <div>
                <strong>{escape(doctor)}</strong><br>
                <span>{created}</span>
            </div>
        </div>
        <section class="meta grid">
            <div><span class="label">الرقم المرجعي</span><br><strong>{escape(patient.reference_number or '')}</strong></div>
            <div><span class="label">اسم المريض</span><br><strong>{escape(patient.name)}</strong></div>
            <div><span class="label">الهاتف</span><br><strong>{escape(patient.phone)}</strong></div>
            <div><span class="label">العمر</span><br><strong>{escape(str(patient.age or ''))}</strong></div>
            <div><span class="label">النوع</span><br><strong>{escape(patient.gender or '')}</strong></div>
        </section>
        <section class="section">
            <div class="label">الأعراض</div>
            <div class="box">{escape(record.symptoms or '')}</div>
        </section>
        <section class="section">
            <div class="label">التشخيص</div>
            <div class="box">{escape(record.diagnosis or '')}</div>
        </section>
        <section class="section">
            <div class="label">الروشتة والعلاج</div>
            <div class="box">{escape(record.prescription or '')}</div>
        </section>
        <section class="section">
            <div class="label">ملاحظات الطبيب</div>
            <div class="box">{escape(record.notes or '')}</div>
        </section>
        <div class="footer">
            <span>ملف رقم: {record.id}</span>
            <span>توقيع الطبيب: ....................</span>
        </div>
    </article>
    <script>
        if (new URLSearchParams(window.location.search).get('print') === '1') {{
            window.addEventListener('load', () => window.print());
        }}
    </script>
</body>
</html>"""


def save_prescription_file(record):
    folder = patient_report_folder(record.patient)
    filename = f"prescription_{record.id}_{record.created_at.strftime('%Y%m%d_%H%M')}.html"
    path = os.path.join(folder, filename)
    with open(path, 'w', encoding='utf-8') as file:
        file.write(prescription_html(record))
    save_prescription_xlsx(record, folder)
    record.prescription_file = path
    db.session.commit()
    return path


def save_prescription_xlsx(record, folder=None):
    folder = folder or patient_report_folder(record.patient)
    patient = record.patient
    patient.ensure_reference_number()
    rows = [
        ['البيان', 'القيمة'],
        ['الرقم المرجعي', patient.reference_number],
        ['اسم المريض', patient.name],
        ['الهاتف', patient.phone],
        ['العمر', patient.age or ''],
        ['النوع', patient.gender or ''],
        ['العنوان', patient.address or ''],
        ['تاريخ الروشتة', record.created_at.strftime('%Y-%m-%d %H:%M')],
        ['الطبيب', record.doctor.full_name if record.doctor else 'طبيب العيادة'],
        ['الأعراض', record.symptoms or ''],
        ['التشخيص', record.diagnosis or ''],
        ['الروشتة', record.prescription or ''],
        ['ملاحظات', record.notes or ''],
    ]
    path = os.path.join(folder, f"prescription_{record.id}_{record.created_at.strftime('%Y%m%d_%H%M')}.xlsx")
    write_xlsx(path, rows, sheet_name='Prescription')
    return path


def create_medical_record(patient, doctor_id, data):
    record = MedicalRecord(
        patient=patient,
        doctor_id=doctor_id,
        symptoms=data.get('symptoms') or '',
        diagnosis=data.get('diagnosis') or '',
        prescription=data.get('prescription') or '',
        notes=data.get('notes') or '',
    )
    db.session.add(record)
    db.session.commit()
    save_prescription_file(record)
    return record


def cell_ref(row_index, col_index):
    letters = ''
    col = col_index
    while col:
        col, remainder = divmod(col - 1, 26)
        letters = chr(65 + remainder) + letters
    return f'{letters}{row_index}'


def worksheet_xml(rows):
    xml_rows = []
    for row_index, row in enumerate(rows, start=1):
        cells = []
        for col_index, value in enumerate(row, start=1):
            value = '' if value is None else str(value)
            cells.append(
                f'<c r="{cell_ref(row_index, col_index)}" t="inlineStr">'
                f'<is><t>{escape(value)}</t></is></c>'
            )
        xml_rows.append(f'<row r="{row_index}">{"".join(cells)}</row>')
    return f'''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">
<sheetData>{"".join(xml_rows)}</sheetData>
</worksheet>'''


def export_patients_xlsx():
    patients = Patient.query.order_by(Patient.created_at.desc()).all()
    rows = [[
        'رقم المريض', 'الرقم المرجعي', 'الاسم', 'الهاتف', 'العمر', 'النوع', 'العنوان',
        'عدد الزيارات', 'تاريخ التسجيل'
    ]]
    for patient in patients:
        patient.ensure_reference_number()
        rows.append([
            patient.id,
            patient.reference_number,
            patient.name,
            patient.phone,
            patient.age or '',
            patient.gender or '',
            patient.address or '',
            len(patient.medical_records),
            patient.created_at.strftime('%Y-%m-%d %H:%M'),
        ])

    export_dir = os.path.join(current_app.config['BASE_DIR'], 'exports', 'excel')
    os.makedirs(export_dir, exist_ok=True)
    path = os.path.join(export_dir, f"patients_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx")

    write_xlsx(path, rows, sheet_name='Patients')
    return path


def write_xlsx(path, rows, sheet_name='Sheet1'):
    files = {
        '[Content_Types].xml': '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
<Default Extension="xml" ContentType="application/xml"/>
<Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/>
<Override PartName="/xl/worksheets/sheet1.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>
</Types>''',
        '_rels/.rels': '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="xl/workbook.xml"/>
</Relationships>''',
        'xl/workbook.xml': '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">
<sheets><sheet name="''' + escape(sheet_name) + '''" sheetId="1" r:id="rId1"/></sheets>
</workbook>''',
        'xl/_rels/workbook.xml.rels': '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet1.xml"/>
</Relationships>''',
        'xl/worksheets/sheet1.xml': worksheet_xml(rows),
    }
    with zipfile.ZipFile(path, 'w', compression=zipfile.ZIP_DEFLATED) as workbook:
        for filename, content in files.items():
            workbook.writestr(filename, content)
