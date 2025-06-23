let taskId, es;

// DOM elements

const domTextareaInput = document.getElementById('textareaInput');
const domResponses = document.getElementById('responses');
const domWorkflowSelect = document.getElementById('workflowSelect');
const domInteractions = document.getElementById('interactions');


// Functions

async function startWorkflow() {
    // Clear previous responses
    domResponses.innerHTML = "";
    domInteractions.innerHTML = "";

    // 1) Start the workflow (runs until first yield)
    const res = await fetch('/start_task', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ workflow_id: domWorkflowSelect.value, user_input: domTextareaInput.value })
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

function processCollectedMessages(response) {
    if (response.collected_messages && response.collected_messages.length > 0) {
        response.collected_messages.forEach(status => {
            domResponses.innerHTML += renderMessageComponent({
                title: status.title,
                body: status.body,
                data: status.data ? JSON.stringify(status.data, null, 2) : null,
                style: 'color: #22b3e4;'
            });
        });
    }
}

function handleMsg(response) {
    if (!response) return;

    // Handle errors
    if (response.status === 'error') {
        processCollectedMessages(response);
        domResponses.innerHTML += renderMessageComponent({
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
            domInteractions.innerHTML += renderMessageComponent({
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
            processCollectedMessages(response);
            domResponses.innerHTML += renderMessageComponent({
                isOpen: false,
                title: response.message.title,
                body: response.message.body,
                data: response.data ? JSON.stringify(response.data, null, 2) : null,
                style: 'color: green;'
            });            
            if (es) es.close();
            break;

        case 'status_message':
            domResponses.innerHTML += renderMessageComponent({
                title: response.message.title,
                body: response.message.body,
                data: JSON.stringify(response, null, 2),
                style: 'color: #22b3e4;'
            });
            break;

        default:
            domResponses.innerHTML += renderMessageComponent({
                title: response.message?.title || 'Status Update',
                body: response.message?.body,
                data: response.data ? JSON.stringify(response.data, null, 2) : null
            });
    }
}


// Event listeners

document.getElementById('startBtn').onclick = () => {
    startWorkflow();
};