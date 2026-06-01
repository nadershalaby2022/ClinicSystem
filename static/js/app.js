let receptionAppointments = [];
let adminUsers = [];

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

function localDateTimeValue(date = new Date()) {
    const localDate = new Date(date.getTime() - date.getTimezoneOffset() * 60000);
    return localDate.toISOString().slice(0, 16);
}

async function requestJson(url, options = {}) {
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

function bookingPayload() {
    return {
        name: document.getElementById('patient-name').value.trim(),
        phone: document.getElementById('patient-phone').value.trim(),
        age: document.getElementById('patient-age').value,
        gender: document.getElementById('patient-gender').value,
        address: document.getElementById('patient-address').value.trim(),
        appointment_type: document.getElementById('appointment-type').value,
        appointment_time: document.getElementById('appointment-time').value,
        notes: document.getElementById('appointment-notes').value.trim(),
    };
}

function resetBookingForm() {
    const form = document.getElementById('appointment-form');
    if (!form) return;
    form.reset();
    document.getElementById('appointment-id').value = '';
    document.getElementById('appointment-time').value = localDateTimeValue();
    form.querySelector('button[type="submit"]').textContent = 'حفظ الحجز وإصدار رقم';
}

function fillBookingForm(appointmentId) {
    const appointment = receptionAppointments.find((item) => item.id === appointmentId);
    if (!appointment) return;
    document.getElementById('appointment-id').value = appointment.id;
    document.getElementById('patient-name').value = appointment.patient.name;
    document.getElementById('patient-phone').value = appointment.patient.phone;
    document.getElementById('patient-age').value = appointment.patient.age;
    document.getElementById('patient-gender').value = appointment.patient.gender;
    document.getElementById('patient-address').value = appointment.patient.address;
    document.getElementById('appointment-type').value = appointment.appointment_type;
    document.getElementById('appointment-time').value = appointment.appointment_time;
    document.getElementById('appointment-notes').value = appointment.notes;
    document.querySelector('#appointment-form button[type="submit"]').textContent = 'تحديث الحجز';
    window.scrollTo({ top: 0, behavior: 'smooth' });
}

async function loadReceptionState() {
    const queueTable = document.getElementById('queue-table');
    if (!queueTable) return;

    const data = await requestJson('/api/reception/state');
    const queue = data.queue;
    receptionAppointments = data.appointments;

    document.getElementById('current-ticket').textContent = queue.current_number || '-';
    document.getElementById('current-name').textContent = queue.current_name || 'لا يوجد حالياً';
    document.getElementById('reception-updated').textContent = queue.updated_at || '--:--';

    const queueRows = [];
    if (queue.current) {
        queueRows.push(`
            <tr>
                <td><strong>${escapeHtml(queue.current.ticket)}</strong></td>
                <td>${escapeHtml(queue.current.name)}</td>
                <td>${escapeHtml(queue.current.appointment_type)}</td>
                <td>${statusBadge(queue.current.status, queue.current.status_label)}</td>
                <td><a class="btn small ghost" href="/doctor/patient/${queue.current.patient_id}" target="_blank">ملف</a></td>
            </tr>
        `);
    }
    queue.waiting.forEach((entry) => {
        queueRows.push(`
            <tr>
                <td><strong>${escapeHtml(entry.ticket)}</strong></td>
                <td>${escapeHtml(entry.name)}</td>
                <td>${escapeHtml(entry.appointment_type)}</td>
                <td>${statusBadge(entry.status, entry.status_label)}</td>
                <td>
                    <div class="status-actions">
                        <button class="btn small success" onclick="callPatient(${entry.id})">استدعاء</button>
                        <button class="btn small warning" onclick="skipPatient(${entry.id})">تخطي</button>
                    </div>
                </td>
            </tr>
        `);
    });
    queue.skipped.forEach((entry) => {
        queueRows.push(`
            <tr>
                <td><strong>${escapeHtml(entry.ticket)}</strong></td>
                <td>${escapeHtml(entry.name)}</td>
                <td>${escapeHtml(entry.appointment_type)}</td>
                <td>${statusBadge(entry.status, entry.status_label)}</td>
                <td><button class="btn small success" onclick="callPatient(${entry.id})">استدعاء</button></td>
            </tr>
        `);
    });
    queueTable.innerHTML = queueRows.join('') || '<tr><td colspan="5"><div class="empty-state">لا يوجد مرضى في الانتظار</div></td></tr>';

    document.getElementById('appointments-table').innerHTML = receptionAppointments.map((appointment) => `
        <tr>
            <td>${escapeHtml(appointment.ticket_number || '-')}</td>
            <td>${escapeHtml(appointment.patient.name)}</td>
            <td>${escapeHtml(appointment.patient.phone)}</td>
            <td>${escapeHtml(appointment.appointment_time_label)}</td>
            <td>${escapeHtml(appointment.appointment_type)}</td>
            <td>${statusBadge(appointment.status, appointment.status_label)}</td>
            <td>
                <div class="status-actions">
                    <button class="btn small ghost" onclick="fillBookingForm(${appointment.id})">تعديل</button>
                    <button class="btn small danger" onclick="cancelAppointment(${appointment.id})">إلغاء</button>
                </div>
            </td>
        </tr>
    `).join('') || '<tr><td colspan="7"><div class="empty-state">لا توجد حجوزات اليوم</div></td></tr>';
}

async function callPatient(queueId) {
    await requestJson(`/api/reception/call/${queueId}`, { method: 'POST' });
    await loadReceptionState();
}

async function skipPatient(queueId) {
    await requestJson(`/api/reception/skip/${queueId}`, { method: 'POST' });
    await loadReceptionState();
}

async function cancelAppointment(appointmentId) {
    if (!confirm('هل تريد إلغاء هذا الحجز؟')) return;
    await requestJson(`/api/reception/appointments/${appointmentId}`, { method: 'DELETE' });
    await loadReceptionState();
}

function initReception() {
    const form = document.getElementById('appointment-form');
    if (!form) return;

    resetBookingForm();
    document.getElementById('reset-booking').addEventListener('click', resetBookingForm);
    form.addEventListener('submit', async (event) => {
        event.preventDefault();
        const appointmentId = document.getElementById('appointment-id').value;
        try {
            if (appointmentId) {
                await requestJson(`/api/reception/appointments/${appointmentId}`, {
                    method: 'PUT',
                    body: JSON.stringify(bookingPayload()),
                });
            } else {
                await requestJson('/api/reception/appointments', {
                    method: 'POST',
                    body: JSON.stringify(bookingPayload()),
                });
            }
            resetBookingForm();
            await loadReceptionState();
        } catch (error) {
            alert(error.message);
        }
    });
    loadReceptionState().catch((error) => console.error(error));
    setInterval(() => loadReceptionState().catch((error) => console.error(error)), 1500);
}

function resetUserForm() {
    const form = document.getElementById('user-form');
    if (!form) return;
    form.reset();
    document.getElementById('user-id').value = '';
    document.getElementById('admin-active').checked = true;
    form.querySelector('button[type="submit"]').textContent = 'حفظ المستخدم';
}

function fillUserForm(userId) {
    const user = adminUsers.find((item) => item.id === userId);
    if (!user) return;
    document.getElementById('user-id').value = user.id;
    document.getElementById('admin-username').value = user.username;
    document.getElementById('admin-full-name').value = user.full_name;
    document.getElementById('admin-role').value = user.role;
    document.getElementById('admin-password').value = user.password_plain;
    document.getElementById('admin-active').checked = user.is_active;
    document.querySelector('#user-form button[type="submit"]').textContent = 'تحديث المستخدم';
}

function userPayload() {
    return {
        username: document.getElementById('admin-username').value.trim(),
        full_name: document.getElementById('admin-full-name').value.trim(),
        role: document.getElementById('admin-role').value,
        password: document.getElementById('admin-password').value,
        is_active: document.getElementById('admin-active').checked,
    };
}

async function loadUsers() {
    const table = document.getElementById('admin-users-table');
    if (!table) return;
    const data = await requestJson('/api/admin/users');
    adminUsers = data.users;
    table.innerHTML = adminUsers.map((user) => `
        <tr>
            <td><strong>${escapeHtml(user.username)}</strong></td>
            <td>${escapeHtml(user.full_name)}</td>
            <td>${escapeHtml(user.role_label)}</td>
            <td><code>${escapeHtml(user.password_plain)}</code></td>
            <td>${user.is_active ? statusBadge('done', 'مفعل') : statusBadge('cancelled', 'معطل')}</td>
            <td>
                <div class="status-actions">
                    <button class="btn small ghost" onclick="fillUserForm(${user.id})">تعديل</button>
                    <button class="btn small danger" onclick="deleteUser(${user.id})">حذف</button>
                </div>
            </td>
        </tr>
    `).join('');
}

async function deleteUser(userId) {
    if (!confirm('هل تريد حذف هذا المستخدم؟')) return;
    try {
        await requestJson(`/api/admin/users/${userId}`, { method: 'DELETE' });
        await loadUsers();
    } catch (error) {
        alert(error.message);
    }
}

function initAdminUsers() {
    const form = document.getElementById('user-form');
    if (!form) return;
    document.getElementById('reset-user').addEventListener('click', resetUserForm);
    form.addEventListener('submit', async (event) => {
        event.preventDefault();
        const userId = document.getElementById('user-id').value;
        try {
            if (userId) {
                await requestJson(`/api/admin/users/${userId}`, {
                    method: 'PUT',
                    body: JSON.stringify(userPayload()),
                });
            } else {
                await requestJson('/api/admin/users', {
                    method: 'POST',
                    body: JSON.stringify(userPayload()),
                });
            }
            resetUserForm();
            await loadUsers();
        } catch (error) {
            alert(error.message);
        }
    });
    loadUsers().catch((error) => console.error(error));
}

document.addEventListener('DOMContentLoaded', () => {
    initReception();
    initAdminUsers();
});
