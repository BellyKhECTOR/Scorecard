document.addEventListener('DOMContentLoaded', function () {
    const uploadForm = document.getElementById('upload-form');
    const uploadBtn = document.getElementById('upload-btn');
    if (uploadForm && uploadBtn) {
        uploadForm.addEventListener('submit', function () {
            uploadBtn.disabled = true;
            uploadBtn.textContent = 'Uploading...';
        });
    }

    const dateInput = document.getElementById('document_date');
    if (dateInput && !dateInput.value) {
        dateInput.value = new Date().toISOString().split('T')[0];
    }

    const healthEl = document.getElementById('health-status');
    if (healthEl) {
        fetch('/health')
            .then(function (r) { return r.json(); })
            .then(function (data) {
                const parts = [];
                parts.push('App: ' + (data.application === 'ok' ? 'OK' : 'Error'));
                parts.push('DB: ' + (data.database === 'ok' ? 'OK' : 'Error'));
                parts.push('S3: ' + (data.s3 === 'ok' ? 'OK' : 'Error'));
                parts.push('AI: ' + data.ai);
                healthEl.textContent = parts.join(' · ');
                healthEl.className = 'health-status ' + (
                    data.application === 'ok' && data.database === 'ok' ? 'health-ok' : 'health-warn'
                );
            })
            .catch(function () {
                healthEl.textContent = 'Status unavailable';
                healthEl.className = 'health-status health-warn';
            });
    }
});
