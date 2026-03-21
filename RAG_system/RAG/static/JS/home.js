document.addEventListener('DOMContentLoaded', function () {
    const uploadForm = document.getElementById('upload-form');
    const chatSection = document.getElementById('chat-container');
    const history = [];

    if (chatSection) chatSection.style.display = 'none';

    function getCookie(name) {
        const match = document.cookie.match(new RegExp('(^| )' + name + '=([^;]+)'));
        return match ? match[2] : '';
    }

    function showStatus(msg, type) {
        const status = document.getElementById('upload-status');
        if (!status) return;
        status.textContent = msg;
        status.className = 'status ' + type;
    }

    function append(role, text) {
        const messages = document.getElementById('chat-messages');
        if (!messages) return null;
        const div = document.createElement('div');
        div.className = 'msg ' + role;
        div.textContent = text;
        messages.appendChild(div);
        messages.scrollTop = messages.scrollHeight;
        return div;
    }

    function showChat(fileName) {
        if (chatSection) {
            chatSection.style.display = 'flex';
            const label = document.getElementById('file-label');
            if (label) label.textContent = fileName;
        }
    }

    async function uploadFile(file, url, fieldName) {
        showStatus('Uploading and indexing...', 'loading');

        const formData = new FormData();
        formData.append(fieldName, file);

        try {
            const res = await fetch(url, {
                method: 'POST',
                headers: { 'X-CSRFToken': getCookie('csrftoken') },
                body: formData,
            });
            const data = await res.json();

            if (data.error) return showStatus(data.error, 'error');

            const info = data.num_pages
                ? `${data.file_name} — ${data.num_pages} pages, ${data.num_chunks} chunks indexed.`
                : `${data.file_name} — ${data.num_rows} rows, ${data.num_chunks} chunks indexed.`;

            showStatus(info, 'success');
            showChat(data.file_name);

        } catch (err) {
            console.error('Upload error:', err);
            showStatus('Upload failed: ' + err.message, 'error');
        }
    }

    function getFileType(fileName) {
        const ext = fileName.toLowerCase().split('.').pop();
        return ext === 'pdf' ? 'pdf' : ext === 'csv' ? 'csv' : null;
    }

    // Unified file input
    if (uploadForm) {
        const fileInput = document.getElementById('file-input');
        const hint = document.getElementById('file-hint');
        const uploadBtn = document.getElementById('upload-btn');

        // Show file type hint when file is selected
        if (fileInput) {
            fileInput.addEventListener('change', function () {
                if (this.files[0]) {
                    const fileType = getFileType(this.files[0].name);
                    hint.textContent = fileType ? `Selected: ${fileType.toUpperCase()} file` : 'Invalid file type. Please select PDF or CSV.';
                    uploadBtn.disabled = !fileType;
                } else {
                    hint.textContent = '';
                    uploadBtn.disabled = false;
                }
            });
        }

        uploadForm.addEventListener('submit', async function (e) {
            e.preventDefault();
            const file = fileInput.files[0];
            if (!file) return showStatus('Please select a file.', 'error');
            
            const fileType = getFileType(file.name);
            if (!fileType) return showStatus('Please upload a PDF or CSV file.', 'error');
            
            const url = fileType === 'pdf' ? '/upload-pdf/' : '/upload-csv/';
            const fieldName = fileType === 'pdf' ? 'pdf_file' : 'csv_file';
            
            await uploadFile(file, url, fieldName);
            fileInput.value = '';
            hint.textContent = '';
        });
    }

    // chat
    const sendBtn = document.getElementById('send');
    const userMessage = document.getElementById('userMessage');

    if (sendBtn) sendBtn.addEventListener('click', send);
    if (userMessage) userMessage.addEventListener('keydown', e => {
        if (e.key === 'Enter') { e.preventDefault(); send(); }
    });

    async function send() {
        const input = document.getElementById('userMessage');
        const text = input.value.trim();
        if (!text) return;
        input.value = '';

        append('user', text);
        history.push({ role: 'user', content: text });
        const typing = append('bot', '...');

        try {
            const res = await fetch('/chat-api/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken'),
                },
                body: JSON.stringify({ message: text, history: history.slice(-10) }),
            });
            const data = await res.json();
            if (typing) typing.remove();
            const reply = data.reply || data.error || 'No response.';
            history.push({ role: 'assistant', content: reply });
            append('bot', reply);

        } catch (err) {
            if (typing) typing.remove();
            console.error('Chat error:', err);
            append('bot', 'Something went wrong: ' + err.message);
        }
    }
});