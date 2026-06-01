function escapeHtml(value) {
    return String(value ?? '').replace(/[&<>"']/g, (char) => ({
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#039;',
    }[char]));
}

async function refreshTvQueue() {
    const response = await fetch('/api/queue');
    const data = await response.json();

    const liveNumber = document.getElementById('live-number');
    const liveName = document.getElementById('live-name');
    const nextContainer = document.getElementById('next-container');
    const updatedAt = document.getElementById('tv-updated');

    if (liveNumber) liveNumber.innerText = data.current_number || '-';
    if (liveName) liveName.innerText = data.current_name || 'لا يوجد حالياً';
    if (updatedAt) updatedAt.innerText = data.updated_at || '--:--';

    if (nextContainer) {
        nextContainer.innerHTML = '';
        if (!data.next_patients.length) {
            nextContainer.innerHTML = '<div class="tv-empty">لا توجد حالات منتظرة الآن</div>';
            return;
        }
        data.next_patients.slice(0, 5).forEach(patient => {
            nextContainer.innerHTML += `
                <div class="patient-row">
                    <span class="name">${escapeHtml(patient.name)}</span>
                    <span class="num">${escapeHtml(patient.ticket)}</span>
                </div>
            `;
        });
    }
}

document.addEventListener('DOMContentLoaded', () => {
    refreshTvQueue().catch((error) => console.error(error));
    setInterval(() => refreshTvQueue().catch((error) => console.error(error)), 1200);
});
