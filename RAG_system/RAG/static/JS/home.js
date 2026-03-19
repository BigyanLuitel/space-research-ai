// home.js
document.addEventListener('DOMContentLoaded', function () {
    const form = document.getElementById('upload-form');
    const chatSection = document.getElementById('chat-container');
    const history = [];

    if (!form) {
        console.error('Upload form not found');
        return;
    }

    // hide chat initially
    chatSection.style.display = 'none';

    function getCookie(name) {
        const match = document.cookie.match(new RegExp('(^| )' + name + '=([^;]+)'));
        return match ? match[2] : '';
    }

    // intercept form submit — use fetch instead of page reload
    form.addEventListener('submit', async function (e) {
        e.preventDefault();

        const fileInput = document.getElementById('file-input');
        const file = fileInput.files[0];
        if (!file) {
            showError('Please select a PDF.');
            return;
        }

        const status = document.getElementById('upload-status');
        status.textContent = 'Uploading and indexing...';
        status.className = 'status loading';

        const formData = new FormData();
        formData.append('pdf_file', file);

        try {
            const res = await fetch('/upload/', {
                method: 'POST',
                headers: { 'X-CSRFToken': getCookie('csrftoken') },
                body: formData,
            });
            const data = await res.json();

            if (data.error) {
                status.textContent = data.error;
                status.className = 'status error';
                return;
            }

            status.textContent = `${data.pdf_name} — ${data.num_pages} pages, ${data.num_chunks} chunks indexed.`;
            status.className = 'status success';

            // show chat section
            chatSection.style.display = 'flex';
            document.getElementById('pdf-label').textContent = data.pdf_name;
            
            // Clear file input for next upload
            fileInput.value = '';

        } catch (error) {
            console.error('Upload error:', error);
            showError('Upload failed: ' + error.message);
        }
    });

    // chat send
    document.getElementById('send').addEventListener('click', send);
    document.getElementById('userMessage').addEventListener('keydown', e => {
        if (e.key === 'Enter') { e.preventDefault(); send(); }
    });

    function append(role, text) {
        const messages = document.getElementById('chat-messages');
        const div = document.createElement('div');
        div.className = 'msg ' + role;
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
        } catch (error) {
            typing.remove();
            console.error('Chat error:', error);
            append('bot', 'Something went wrong: ' + error.message);
        }
    }

    function showError(msg) {
        const status = document.getElementById('upload-status');
        status.textContent = msg;
        status.className = 'status error';
    }
});