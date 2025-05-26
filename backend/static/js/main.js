let taskId, es;

// DOM elements
const domButtonSendTest = document.getElementById('buttonSendTest');
const domTextareaTest = document.getElementById('textareaTest');
const domResponseTest = document.getElementById('responseTest');
const domResponseBox = document.getElementById('responseBox');
const domWorkflowSelect = document.getElementById('workflowSelect');

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
    const res = await fetch('/start_task', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ workflow_id: domWorkflowSelect.value })
    });
    const data = await res.json();
    taskId = data.task_id;

    // 2) Open SSE stream for status updates
    es = new EventSource(`/msg/stream?task_id=${taskId}`);
    es.onmessage = e => {
        const msg = JSON.parse(e.data);
        console.log('SSE message:', msg);
        handleMsg(msg);
    };
    es.onerror = (error) => console.error('SSE error', error);
    
    domResponseBox.innerHTML = "";

    handleMsg(data);
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
    if (msg.action === 'status_message') {
        domResponseBox.innerHTML += `<div class="message"><pre>${JSON.stringify(msg, null, 2)}</pre></div>`;
    }
    else if (msg.action === 'interaction_request') {
        domResponseBox.innerHTML += `<div class="message"><div>${msg.message}</div><div><button onclick="continueWorkflow('yes'); this.disabled=true">Continue</button></div></div>`;
    }
    else if (msg.action === 'task_done') {
        domResponseBox.innerHTML += `<div class="message"><pre>${JSON.stringify(msg, null, 2)}</pre></div>`;
        if (es) es.close();
    } else {
        domResponseBox.innerHTML += `<div class="message"><pre>${JSON.stringify(msg, null, 2)}</pre></div>`;
    }
}

// Event listeners
domButtonSendTest.addEventListener('click', sendTest);

document.getElementById('startBtn').onclick = () => {
    startWorkflow();
};