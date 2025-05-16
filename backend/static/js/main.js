let taskId, es;

// DOM elements
const domButtonSendTest = document.getElementById('buttonSendTest');
const domTextareaTest = document.getElementById('textareaTest');
const domResponseTest = document.getElementById('responseTest');
const domResponseBox = document.getElementById('responseBox');

// functions
async function sendTest() {
    const response = await fetch('/api/tools/test', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: domTextareaTest.value })
    });
    const data = await response.json();
    domResponseTest.innerHTML += `<p>${data.data}</p>`;
}

 async function startWorkflow() {
    // 1) Start the workflow (runs until first yield)
    const res = await fetch('/start_task', { method:'POST' });
    const data = await res.json();
    taskId = data.task_id;
    handleMsg(data);

    // 2) Open SSE stream for status updates
    es = new EventSource(`/status/stream?task_id=${taskId}`);
    es.onmessage = e => {
        const msg = JSON.parse(e.data);
        console.log('SSE message:', msg);
        domResponseBox.innerHTML += `<div class="message"><pre>${JSON.stringify(msg, null, 2)}</pre></div>`;
        //document.getElementById('status-title').innerText = msg.message.title;
        //document.getElementById('status-body').innerText  = msg.message.body;
    };
    es.onerror = (error) => console.error('SSE error', error);
};

async function continueWorkflow(input) {
    const res = await fetch('/continue_task', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ task_id: taskId, user_input: input })
    });
    const msg = await res.json();
    handleMsg(msg);
}

function handleMsg(msg) {
    if (msg.action === 'need_user_input') {
        document.getElementById('prompt').innerText = msg.message;
        document.getElementById('confirmBtn').style.display = 'inline-block';
    }
    else if (msg.action === 'task_done') {
        //document.getElementById('prompt').innerText = '🎉 ' + msg.result;
        domResponseBox.innerHTML += `<div class="message"><pre>${JSON.stringify(msg, null, 2)}</pre></div>`;
        document.getElementById('confirmBtn').style.display = 'none';
        if (es) es.close();
    }
}

// Event listeners
domButtonSendTest.addEventListener('click', sendTest);

document.getElementById('confirmBtn').onclick = () => {
    continueWorkflow('yes');
    document.getElementById('confirmBtn').style.display = 'none';
};

document.getElementById('startBtn').onclick = () => {
    startWorkflow();
};