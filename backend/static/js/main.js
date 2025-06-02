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
    const response_payload = await res.json();
    handleMsg(response_payload);
}

function responseBoxMessageComponent(msgTitle, msgBody, msgData, msgForm) {
    this.title = msgTitle;
    this.body = msgBody;
    this.data = msgData;
    this.form = msgForm;

    let dataHtml = this.data ? `<div class="message-data"><pre>${JSON.stringify(this.data, null, 2)}</pre></div>` : '';
    let formHtml = this.form ? `<div class="message-form">${this.form}</div>` : '';

    return `<div class="message">
        <details>
            <summary>${this.title}</summary>
            <div><pre>${this.body}</pre></div>
            ${dataHtml}
            ${formHtml}
        </details>
    </div>`;
}

function handleMsg(response_payload) {
    if (response_payload.action === 'status_message') {
        //domResponseBox.innerHTML += `<div class="message"><pre>${JSON.stringify(msg, null, 2)}</pre></div>`;
        domResponseBox.innerHTML += `<details><summary>${response_payload.message.title}</summary><div><pre>${JSON.stringify(response_payload, null, 2)}</pre></div></details>`;
        console.log(response_payload);
    }
    else if (response_payload.action === 'interaction_request') {
        //domResponseBox.innerHTML += `<div class="message"><div>${msg.message}</div><div><button onclick="continueWorkflow('yes'); this.disabled=true">Continue</button></div></div>`;
        domResponseBox.innerHTML += `<details open><summary>${response_payload.message.title}</summary><div><pre>${JSON.stringify(response_payload.message.body, null, 2)}</pre></div><div><button onclick="continueWorkflow('yes'); this.disabled=true">Continue</button></div></details>`;
        console.log(response_payload);
    }
    else if (response_payload.action === 'task_done' || response_payload.action === 'workflow_finished') {
        //domResponseBox.innerHTML += `<div class="message"><pre>${JSON.stringify(response_payload, null, 2)}</pre></div>`;
        domResponseBox.innerHTML += `<details open>
        <summary>${response_payload.message.title}</summary>
        <div><pre>${JSON.stringify(response_payload.message.body, null, 2)}</pre></div>
        <div><pre>${JSON.stringify(response_payload, null, 2)}</pre></div>
        </details>`;
        console.log(response_payload);
        // IMPORTANT: Close the SSE connection when the task is done
        if (es) es.close();
    } else {
        //domResponseBox.innerHTML += `<div class="message"><pre>${JSON.stringify(response_payload, null, 2)}</pre></div>`;
        let msgTitle = response_payload.message.title || response_payload.action || 'No action specified';
        let msgBody = response_payload.message.body || response_payload.data || response_payload;
        //let msgTitleStr = JSON.stringify(msgTitle, null, 2);
        let msgBodyStr = JSON.stringify(msgBody, null, 2);        
        domResponseBox.innerHTML += `<details><summary>${msgTitle}</summary><div><pre>${msgBodyStr}</pre></div></details>`;

        console.log(response_payload);
    }
}

// Event listeners
domButtonSendTest.addEventListener('click', sendTest);

document.getElementById('startBtn').onclick = () => {
    startWorkflow();
};