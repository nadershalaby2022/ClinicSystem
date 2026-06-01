function escapeHtml(value) {
    return String(value ?? '').replace(/[&<>"']/g, (char) => ({
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#039;',
    }[char]));
}

function statusBadge(status, label) {
    return `<span class="badge ${escapeHtml(status)}">${escapeHtml(label)}</span>`;
}

async function getJson(url, options = {}) {
    const response = await fetch(url, {
        headers: { 'Content-Type': 'application/json', ...(options.headers || {}) },
        ...options,
    });
    const data = await response.json();
    if (!response.ok || data.success === false) {
        throw new Error(data.message || 'حدث خطأ أثناء تنفيذ العملية');
    }
    return data;
}

async function loadDoctorState() {
    const table = document.getElementById('doctor-appointments-table');
    if (!table) return;

    const data = await getJson('/api/doctor/state');
    const queue = data.queue;
    const currentLink = document.getElementById('open-current-patient');

    document.getElementById('doctor-current-ticket').textContent = queue.current_number || '-';
    document.getElementById('doctor-current-name').textContent = queue.current_name || 'لا يوجد حالياً';
    document.getElementById('doctor-updated').textContent = queue.updated_at || '--:--';

    if (queue.current) {
        currentLink.href = `/doctor/patient/${queue.current.patient_id}`;
        currentLink.classList.remove('disabled');
    } else {
        currentLink.href = '#';
        currentLink.classList.add('disabled');
    }

    document.getElementById('doctor-waiting-list').innerHTML = queue.waiting.map((entry) => `
        <a class="mini-row" href="/doctor/patient/${entry.patient_id}">
            <strong>${escapeHtml(entry.ticket)}</strong>
            <span>${escapeHtml(entry.name)}</span>
        </a>
    `).join('') || '<div class="empty-state">لا يوجد مرضى في الانتظار</div>';

    table.innerHTML = data.appointments.map((appointment) => `
        <tr>
            <td>${escapeHtml(appointment.ticket_number || '-')}</td>
            <td><strong>${escapeHtml(appointment.patient.reference_number || '-')}</strong></td>
            <td>${escapeHtml(appointment.patient.name)}</td>
            <td>${escapeHtml(appointment.patient.phone)}</td>
            <td>${escapeHtml(appointment.appointment_type)}</td>
            <td>${statusBadge(appointment.status, appointment.status_label)}</td>
            <td><a class="btn small primary" href="/doctor/patient/${appointment.patient.id}">فتح الملف</a></td>
        </tr>
    `).join('') || '<tr><td colspan="7"><div class="empty-state">لا توجد حجوزات اليوم</div></td></tr>';
}

function initDoctorDashboard() {
    if (!document.getElementById('doctor-appointments-table')) return;
    loadDoctorState().catch((error) => console.error(error));
    setInterval(() => loadDoctorState().catch((error) => console.error(error)), 1500);
}

function medicalRecordPayload() {
    return {
        symptoms: document.getElementById('record-symptoms').value.trim(),
        diagnosis: document.getElementById('record-diagnosis').value.trim(),
        prescription: document.getElementById('record-prescription').value.trim(),
        notes: document.getElementById('record-notes').value.trim(),
        finish_visit: true,
    };
}

function initPatientProfile() {
    const form = document.getElementById('medical-record-form');
    if (!form) return;

    form.addEventListener('submit', async (event) => {
        event.preventDefault();
        const shouldPrint = event.submitter?.dataset.print === '1';
        const patientId = form.dataset.patientId;
        try {
            const data = await getJson(`/api/doctor/patient/${patientId}/records`, {
                method: 'POST',
                body: JSON.stringify(medicalRecordPayload()),
            });
            if (shouldPrint) {
                window.open(`${data.print_url}?print=1`, '_blank');
            }
            window.location.reload();
        } catch (error) {
            alert(error.message);
        }
    });
}

async function loadPatientSearch() {
    const results = document.getElementById('patient-search-results');
    const input = document.getElementById('patient-search-input');
    if (!results || !input) return;

    const data = await getJson(`/api/doctor/patients/search?q=${encodeURIComponent(input.value.trim())}`);
    results.innerHTML = data.patients.map((patient) => `
        <tr>
            <td><strong>${escapeHtml(patient.reference_number)}</strong></td>
            <td>${escapeHtml(patient.name)}</td>
            <td>${escapeHtml(patient.phone)}</td>
            <td>${escapeHtml(patient.age || '-')}</td>
            <td>${escapeHtml(patient.visits_count)}</td>
            <td>${escapeHtml(patient.last_visit || '-')}</td>
            <td>${escapeHtml(patient.last_diagnosis || '-')}</td>
            <td><a class="btn small primary" href="/doctor/patient/${patient.id}">فتح الملف</a></td>
        </tr>
    `).join('') || '<tr><td colspan="8"><div class="empty-state">لا توجد نتائج مطابقة</div></td></tr>';
}

function initPatientSearch() {
    const input = document.getElementById('patient-search-input');
    const button = document.getElementById('patient-search-button');
    if (!input || !button) return;

    button.addEventListener('click', () => loadPatientSearch().catch((error) => alert(error.message)));
    input.addEventListener('keydown', (event) => {
        if (event.key === 'Enter') {
            event.preventDefault();
            loadPatientSearch().catch((error) => alert(error.message));
        }
    });
    loadPatientSearch().catch((error) => console.error(error));
}

document.addEventListener('DOMContentLoaded', () => {
    initDoctorDashboard();
    initPatientProfile();
    initPatientSearch();
});
