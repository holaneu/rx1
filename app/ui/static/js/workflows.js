let taskId;
let SSE; // SSE for Server-Sent Events

// DOM elements

const domTextareaInput = document.getElementById('textareaInput');
const domWorkflowSelect = document.getElementById('workflowSelect');
const domModelSelect = document.getElementById('modelSelect');
const domStartWorkflowButton = document.getElementById('startWorkflowButton');

const domInteractions = document.getElementById('interactions');
const domResponses = document.getElementById('responses');
const domLogs = document.getElementById('logs');
const domRunningWorkflowMsg = document.getElementById('running-workflow-msg');

// Functions

function populateWorkflowSelect(workflows) {
    domWorkflowSelect.innerHTML = '<option value="" disabled selected>Select workflow ...</option>';
    Object.entries(workflows).forEach(([id, wf]) => {
        const option = document.createElement('option');
        option.value = id;
        option.textContent = wf.title;
        domWorkflowSelect.appendChild(option);
    });
}

async function startWorkflow() {
    // Clear previous responses
    domLogs.innerHTML = "";
    domResponses.innerHTML = "";
    domInteractions.innerHTML = "";
    // Update UI state
    domRunningWorkflowMsg.classList.remove('hidden');
    domStartWorkflowButton.disabled=true;
    domStartWorkflowButton.innerHTML="working...";
    // Prepare payload
    let payload = {
        workflow_id: domWorkflowSelect.value,
        user_input: domTextareaInput.value
    };
    if (domModelSelect.value) {
        payload.model = domModelSelect.value;
    }
    console.log('startWorkflow - payload:', payload);
    // 1) Start the workflow (runs until first yield)
    const res = await fetch('/api/start_task', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
    });
    const data = await res.json();
    taskId = data.task_id;
    console.log('startWorkflow - response:', data);

    
    /* temporary disabled SSE
    // 2) Open SSE stream for status updates
    SSE = new EventSource(`/msg/stream?task_id=${taskId}`);
    SSE.onmessage = e => {
        const msg = JSON.parse(e.data);
        console.log('SSE message:', msg);
        handleMsg(msg);
    };
    SSE.onerror = (error) => console.error('SSE error', error);    
    */

    // 3) Handle the initial response
    handleMsg(data);
};

async function continueWorkflow(input) {
    const res = await fetch('/api/continue_task', {
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

function processFuncLog(response) {
    if (response.func_log && response.func_log.length > 0) {
        response.func_log.forEach(status => {
            domLogs.innerHTML += renderMessageComponent({
                title: status.title,
                body: status.body,
                data: status.data ? JSON.stringify(status.data, null, 2) : null,
                style: 'color: #a1a1a1;'
            });
        });
    }
}

/**
 * Handles the submission of a dynamically generated form.
 * @param {Event} event - The form submission event.
 */
function submitInteractionForm(event) {
    event.preventDefault();
    const form = event.target;
    
    // Disable form to prevent multiple submissions
    form.querySelector('button[type="submit"]').disabled = true;

    // Collect form data into a plain object
    const formData = new FormData(form);
    const userInput = Object.fromEntries(formData.entries());

    // Send the collected data to continue the workflow
    continueWorkflow(userInput);

    // Visually close the interaction panel
    form.closest('details').open = false;
}

/**
 * Renders an HTML form from a JSON definition.
 * @param {Array} formElements - The array of form element definitions from the backend.
 * @returns {string} The HTML string for the form.
 */
function renderFormFromJSON(formElements) {
    // If no elements are defined, fall back to a simple confirmation button
    if (!formElements || formElements.length === 0) {
        return `<button onclick="continueWorkflow('confirm'); this.disabled=true; this.closest('details').open = false;">Confirm</button>`;
    }

    const formFields = formElements.map(el => {
        const required = el.required ? 'required' : '';
        const name = `name="${el.name}"`;
        const id = `id="${el.name}-${Date.now()}"`; // Unique ID for the label
        const label = el.label ? `<label for="${id}">${el.label}</label>` : '';
        let fieldHtml = '';

        switch (el.type) {
            case 'text':
                fieldHtml = `<input type="text" ${id} ${name} placeholder="${el.placeholder || ''}" ${required}>`;
                break;
            case 'textarea':
                fieldHtml = `<textarea ${id} ${name} placeholder="${el.placeholder || ''}" ${required}></textarea>`;
                break;
            case 'select':
                // Add a disabled default option
                const options = [
                    `<option value="" disabled selected>-- select option --</option>`,
                    ...(el.options.map(opt => `<option value="${opt}">${opt}</option>`))
                ].join('');
                fieldHtml = `<select ${id} ${name} ${required}>${options}</select>`;
                break;
            default:
                return `<div class="form-group"><p>Unsupported element type: ${el.type}</p></div>`;
        }
        return `<div class="form-group">${label}${fieldHtml}</div>`;
    }).join('');

    // The onsubmit handler calls our new function
    return `
        <form onsubmit="submitInteractionForm(event)" class="interaction-form">
            ${formFields}
            <button type="submit">Submit</button>
        </form>
    `;
}

function handleMsg(response) {
    if (!response) return;

    // Handle errors
    if (response.status === 'error') {
            processFuncLog(response);
            domResponses.innerHTML += renderMessageComponent({
                isOpen: true,
                title: response.message.title,
                body: response.message.body,
                style: 'color: #f45b5b;'
            });            
            if (SSE) SSE.close(); // realy use it for status = error??
            // update UI state
            domStartWorkflowButton.disabled=false;
            domStartWorkflowButton.innerHTML="Run Workflow";
            domRunningWorkflowMsg.classList.add('hidden');            
            return;        
    }

    // Handle different actions
    switch (response.action) {
        case 'interaction_request':
            processFuncLog(response);

            // Generate the form HTML from the backend JSON response
            const formHtml = renderFormFromJSON(response.message.form_elements);

            domInteractions.innerHTML += renderMessageComponent({
                isOpen: true,
                title: response.message.title,
                body: response.message.body,
                //form: `<button onclick="continueWorkflow('yes'); this.disabled=true; this.closest('details').open=false;">Continue</button>`,
                form: formHtml, // Use the dynamically generated form here
                data: response.data ? JSON.stringify(response.data, null, 2) : null,
                style: 'color: yellow;'
            });
            break;

        case 'workflow_finished':
        case 'task_done':
            processFuncLog(response);
            domResponses.innerHTML += renderMessageComponent({
                isOpen: false,
                title: response.message.title,
                body: response.message.body,
                data: response.data ? JSON.stringify(response.data, null, 2) : null,
                style: 'color: green;'
            });            
            if (SSE) SSE.close();
            // update UI state
            domStartWorkflowButton.disabled=false;
            domStartWorkflowButton.innerHTML="Run Workflow";
            domRunningWorkflowMsg.classList.add('hidden');
            break;        
        
        case 'workflow_finished_partially':
            processFuncLog(response);
            domResponses.innerHTML += renderMessageComponent({
                isOpen: true,
                title: response.message.title,
                body: response.message.body,
                data: response.data ? JSON.stringify(response.data, null, 2) : null,
                style: 'color: #22b3e4;'
            });
            // update UI state
            domStartWorkflowButton.disabled=false;
            domStartWorkflowButton.innerHTML="Run Workflow";
            domRunningWorkflowMsg.classList.add('hidden');
            break;

        case 'status_message':
            processFuncLog(response);
            domResponses.innerHTML += renderMessageComponent({
                title: response.message.title,
                body: response.message.body,
                data: JSON.stringify(response, null, 2),
                style: 'color: #a1a1a1;'
            });
            break;

        default:
            processFuncLog(response);
            domResponses.innerHTML += renderMessageComponent({
                title: response.message?.title || 'Status Update',
                body: response.message?.body,
                data: response.data ? JSON.stringify(response.data, null, 2) : null
            });
            // update UI state
            domStartWorkflowButton.disabled=false;
            domStartWorkflowButton.innerHTML="Run Workflow";
            domRunningWorkflowMsg.classList.add('hidden');
    }
}


// Event listeners

domStartWorkflowButton.onclick = () => {
    startWorkflow();
};

/*
document.getElementById('reload-custom-workflows').onclick = function() {
    fetch('/api/reload_modules', {method: 'POST'})
        .then(response => response.json())
        .then(data => alert(data.message || data.error));
};
*/

document.getElementById('reload-custom-workflows').onclick = async function() {
    const res = await fetch('/api/reload_modules', {method: 'POST'});
    const data = await res.json();
    alert(data.message || data.error);
    if (data.status === 'success') {
        const wfRes = await fetch('/api/workflows');
        const wfData = await wfRes.json();
        populateWorkflowSelect(wfData);
    }
};