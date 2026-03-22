document.addEventListener('DOMContentLoaded', function () {
    const form       = document.getElementById('upload-form');
    const fileInput  = document.getElementById('file-input');
    const uploadBtn  = document.getElementById('upload-btn');
    const dropZone   = document.getElementById('drop-zone');
    const fileSelected = document.getElementById('file-selected');
    const fileName   = document.getElementById('file-name');
    const chatSection = document.getElementById('chat-container');
    const history    = [];

    // ── drag and drop ──
    dropZone.addEventListener('dragover', e => { e.preventDefault(); dropZone.classList.add('drag'); });
    dropZone.addEventListener('dragleave', () => dropZone.classList.remove('drag'));
    dropZone.addEventListener('drop', e => {
        e.preventDefault();
        dropZone.classList.remove('drag');
        const file = e.dataTransfer.files[0];
        if (file) setFile(file);
    });

    fileInput.addEventListener('change', e => {
        if (e.target.files[0]) setFile(e.target.files[0]);
    });

    document.getElementById('clear-file').addEventListener('click', clearFile);

    function setFile(file) {
        const ext = file.name.split('.').pop().toLowerCase();
        if (!['pdf', 'csv'].includes(ext)) return showStatus('Only PDF and CSV files are supported.', 'error');
        fileInput._file = file;
        fileName.textContent = file.name;
        fileSelected.style.display = 'flex';
        uploadBtn.disabled = false;
        showStatus('', '');
    }

    function clearFile() {
        fileInput.value = '';
        fileInput._file = null;
        fileSelected.style.display = 'none';
        uploadBtn.disabled = true;
        showStatus('', '');
    }

    function getCookie(name) {
        const match = document.cookie.match(new RegExp('(^| )' + name + '=([^;]+)'));
        return match ? match[2] : '';
    }

    function showStatus(msg, type) {
        const el = document.getElementById('upload-status');
        el.textContent = msg;
        el.className = 'upload-status ' + type;
    }

    // ── upload ──
    form.addEventListener('submit', async function (e) {
        e.preventDefault();
        const file = fileInput._file || fileInput.files[0];
        if (!file) return showStatus('Please select a file.', 'error');

        uploadBtn.disabled = true;
        showStatus('Uploading and indexing...', 'loading');

        const formData = new FormData();
        const ext = file.name.split('.').pop().toLowerCase();
        formData.append(ext === 'csv' ? 'csv_file' : 'pdf_file', file);

        const url = ext === 'csv' ? '/upload-csv/' : '/upload-pdf/';

        try {
            const res = await fetch(url, {
                method: 'POST',
                headers: { 'X-CSRFToken': getCookie('csrftoken') },
                body: formData,
            });
            const data = await res.json();
            if (data.error) return showStatus(data.error, 'error');

            const info = data.num_pages
                ? `${data.file_name} — ${data.num_pages} pages, ${data.num_chunks} chunks`
                : `${data.file_name} — ${data.num_rows} rows, ${data.num_chunks} chunks`;

            showStatus(info, 'success');

            document.getElementById('upload-section').style.display = 'none';
            document.getElementById('file-label').textContent = data.file_name;
            chatSection.style.display = 'flex';

        } catch (err) {
            showStatus('Upload failed: ' + err.message, 'error');
            uploadBtn.disabled = false;
        }
    });

    // ── reset ──
    window.resetUpload = function () {
        chatSection.style.display = 'none';
        document.getElementById('upload-section').style.display = 'block';
        clearFile();
        document.getElementById('chat-messages').innerHTML =
            '<div class="msg bot-message welcome-msg">Document indexed and ready. Ask me anything about its contents.</div>';
    };

    // ── chat ──
    document.getElementById('send').addEventListener('click', send);
    document.getElementById('userMessage').addEventListener('keydown', e => {
        if (e.key === 'Enter') { e.preventDefault(); send(); }
    });

    function append(role, text) {
        const messages = document.getElementById('chat-messages');
        const div = document.createElement('div');
        div.className = 'msg ' + role + '-message';
        div.textContent = text;
        messages.appendChild(div);
        messages.scrollTop = messages.scrollHeight;
        return div;
    }

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
            typing.remove();
            const reply = data.reply || data.error || 'No response.';
            history.push({ role: 'assistant', content: reply });
            append('bot', reply);
        } catch (err) {
            typing.remove();
            append('bot', 'Something went wrong: ' + err.message);
        }
    }
});