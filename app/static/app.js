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
});
