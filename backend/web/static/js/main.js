let taskId, es;

// DOM elements
const domButtonSendTest = document.getElementById('buttonSendTest');
const domTextareaTest = document.getElementById('textareaTest');
const domResponseTest = document.getElementById('responseTest');
const domResponseBox = document.getElementById('responseBox');
const domWorkflowSelect = document.getElementById('workflowSelect');
const domUserInteractions = document.getElementById('userInteractions');

// functions
async function sendTest() {
    const response = await fetch('/api/tools/test', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: domTextareaTest.value })
    });
    const data = await response.json();
    domResponseTest.innerHTML += `<p>${data.data}</p>`;
    console.log('sendTest - response:', data);
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
    console.log('startWorkflow - response:', data);

    // 2) Open SSE stream for status updates
    es = new EventSource(`/msg/stream?task_id=${taskId}`);
    es.onmessage = e => {
        const msg = JSON.parse(e.data);
        console.log('SSE message:', msg);
        handleMsg(msg);
    };
    es.onerror = (error) => console.error('SSE error', error);    
    domResponseBox.innerHTML = "";
    domUserInteractions.innerHTML = "";

    // 3) Handle the initial response
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
    console.log('continueWorkflow - response:', response_payload);
}

function renderMessageComponent({ title, body, data, form, isOpen = false, style }) { 
    const bodyHtml = body ? `<div class="message-body"><pre>${body}</pre></div>` : '';
    const dataHtml = data ? `<div class="message-data"><pre>${data}</pre></div>` : '';
    const formHtml = form ? `<div class="message-form">${form}</div>` : '';

    return `<div class="message">
        <details${isOpen ? ' open' : ''}>
            <summary style="${style}">${title}</summary>
            ${bodyHtml}
            ${dataHtml}
            ${formHtml}
        </details>
    </div>`;
}

/*
function handleMsg(response_payload) {
    if (response_payload.action === 'status_message') {
        domResponseBox.innerHTML += responseBoxMessageComponent({
            title: response_payload.message.title,
            body: JSON.stringify(response_payload, null, 2)
        });
    }
    else if (response_payload.action === 'interaction_request') {
        domResponseBox.innerHTML += responseBoxMessageComponent({
            isOpen: true,
            title: response_payload.message.title,
            body: response_payload.message.body,
            form: `<button onclick="continueWorkflow('yes'); this.disabled=true">Continue</button>`,
            data: JSON.stringify(response_payload, null, 2)
        });
    }
    else if (response_payload.action === 'task_done' || response_payload.action === 'workflow_finished') {
        domResponseBox.innerHTML += responseBoxMessageComponent({
            isOpen: true,
            title: response_payload.message.title,
            body: response_payload.message.body,
            data: JSON.stringify(response_payload, null, 2)
        });
        // IMPORTANT: Close the SSE connection when the task is done
        if (es) es.close();
    } else {
        let msgTitle = response_payload.message.title || response_payload.action || 'No action specified';
        let msgBody = response_payload.message.body || response_payload.data || response_payload;
        let msgBodyStr = JSON.stringify(msgBody, null, 2);        
        domResponseBox.innerHTML += responseBoxMessageComponent({
            title: msgTitle,
            body: msgBody
        });
    }
}
*/

function handleMsg(response) {
    if (!response) return;

    // Handle errors
    if (response.status === 'error') {
        domResponseBox.innerHTML += renderMessageComponent({
            title: 'Error',
            body: response.message.body,
            isOpen: true,
            style: 'color: #f45b5b;'
        });
        return;
    }

    // Handle different actions
    switch (response.action) {
        case 'interaction_request':
            domUserInteractions.innerHTML += renderMessageComponent({
                isOpen: true,
                title: response.message.title,
                body: response.message.body,
                form: `<button onclick="continueWorkflow('yes'); this.disabled=true">Continue</button>`,
                data: response.data ? JSON.stringify(response.data, null, 2) : null,
                style: 'color: yellow;'
            });
            break;

        case 'workflow_finished':
        case 'task_done':
            domResponseBox.innerHTML += renderMessageComponent({
                isOpen: false,
                title: response.message.title,
                body: response.message.body,
                data: response.data ? JSON.stringify(response.data, null, 2) : null,
                style: 'color: green;'
            });
            if (es) es.close();
            break;

        case 'status_message':
            domResponseBox.innerHTML += renderMessageComponent({
                title: response.message.title,
                body: response.message.body,
                data: JSON.stringify(response, null, 2),
                style: 'color: #22b3e4;'
            });
            break;

        default:
            domResponseBox.innerHTML += renderMessageComponent({
                title: response.message?.title || 'Status Update',
                body: response.message?.body,
                data: response.data ? JSON.stringify(response.data, null, 2) : null
            });
    }
}

// Event listeners
domButtonSendTest.addEventListener('click', sendTest);

document.getElementById('startBtn').onclick = () => {
    startWorkflow();
};