const socket = io();
let currentWorkflowInstanceId = null;
const responseBox = document.getElementById('response-box');
const workflowDropdown = document.getElementById('workflow-dropdown');
const startWorkflowButton = document.getElementById('start-workflow-button');
const mainInputTextarea = document.getElementById('main-input-textarea');

// --- Helper to add messages to response box ---
function addResponseItem(type, title, contentHtml, workflowInstanceIdForInteraction = null) {
    const details = document.createElement('details');
    const summary = document.createElement('summary');
    const contentDiv = document.createElement('div');
    contentDiv.className = 'response-content';

    summary.textContent = title;
    details.appendChild(summary);
    
    if (typeof contentHtml === 'string') {
        contentDiv.innerHTML = contentHtml;
    } else if (contentHtml instanceof Node) {
        contentDiv.appendChild(contentHtml);
    }
    details.appendChild(contentDiv);

    // Add type class for styling and open if interaction
    if (type === 'interaction') {
        details.classList.add('status-interaction');
        details.open = true; // Auto-open interaction requests
    } else if (type === 'complete') {
        details.classList.add('status-complete');
    } else if (type === 'error') {
        details.classList.add('status-error');
        details.open = true; 
    }


    responseBox.appendChild(details);
    responseBox.scrollTop = responseBox.scrollHeight; // Scroll to newest message

    // If it's an interaction, hook up the form
    if (type === 'interaction' && workflowInstanceIdForInteraction) {
        const interactionForm = contentDiv.querySelector('.interaction-form');
        if (interactionForm) {
            interactionForm.addEventListener('submit', function(e) {
                e.preventDefault();
                const formData = {};
                const inputs = interactionForm.querySelectorAll('input, select, textarea');
                inputs.forEach(input => {
                    if (input.type === 'radio') {
                        if (input.checked) formData[input.name] = input.value;
                    } else if (input.type === 'checkbox') {
                        formData[input.name] = input.checked;
                    } else {
                        formData[input.name] = input.value;
                    }
                });
                socket.emit('submit_interaction', {
                    workflow_instance_id: workflowInstanceIdForInteraction,
                    form_data: formData
                });
                // Disable form after submission to prevent multiple submissions
                interactionForm.querySelectorAll('button, input, select, textarea').forEach(el => el.disabled = true);
                summary.textContent = title + " (Submitted - Waiting for continuation...)";
            });
        }
    }
}

// --- Populate Workflows ---
async function fetchAndPopulateWorkflows() {
    try {
        const response = await fetch('/api/workflows');
        if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
        const workflows_fetched = await response.json();
        
        console.log('Fetched workflows:', workflows_fetched);
        
        workflowDropdown.innerHTML = '<option value="">-- Select a Workflow --</option>'; // Clear loading/previous
        if (workflows_fetched.length > 0) {
            workflows_fetched.forEach(wf => {
                const option = document.createElement('option');
                option.value = wf.id;
                option.textContent = `${wf.name} (${wf.description || wf.id})`;
                workflowDropdown.appendChild(option);
            });
            startWorkflowButton.disabled = false;
        } else {
            workflowDropdown.innerHTML = '<option value="">No workflows available</option>';
        }
    } catch (error) {
        console.error('Failed to load workflows:', error);
        workflowDropdown.innerHTML = '<option value="">Error loading workflows</option>';
        addResponseItem('error', 'System Error', `<p>Could not load workflows: ${error.message}</p>`);
    }
}

// --- Socket Event Handlers ---
socket.on('connected', function(data) {
    console.log('Connected to server:', data);
    addResponseItem('info', 'System', `<p>Connected to server. Session ID: ${data.session_id}, SID: ${data.sid}</p>`);
    fetchAndPopulateWorkflows(); // Fetch workflows after connection established
});

socket.on('progress_update', function(data) {
    console.log('Progress Update:', data);
    const bodyHtml = `<p>${data.message.body.replace(/\n/g, '<br>')}</p><small>Instance: ${data.workflow_instance_id}</small>`;
    addResponseItem('progress', `Progress: ${data.message.title}`, bodyHtml);
});

socket.on('interaction_request', function(data) {
    console.log('Interaction Request:', data);
    currentWorkflowInstanceId = data.workflow_instance_id; // Should be the same, but good to update
    
    const formConfig = data.form_config;
    const formHtml = document.createElement('form');
    formHtml.className = 'interaction-form';
    
    if (formConfig.description) {
        const descP = document.createElement('p');
        descP.textContent = formConfig.description;
        formHtml.appendChild(descP);
    }

    formConfig.fields.forEach(field => {
        const formGroup = document.createElement('div');
        formGroup.className = 'form-group';
        
        const label = document.createElement('label');
        label.setAttribute('for', field.id);
        label.textContent = field.label;
        formGroup.appendChild(label);

        if (field.type === 'text' || field.type === 'email' || field.type === 'password' || field.type === 'number') {
            const input = document.createElement('input');
            input.type = field.type; input.id = field.id; input.name = field.id;
            if (field.value) input.value = field.value;
            if (field.placeholder) input.placeholder = field.placeholder;
            if (field.required) input.required = true;
            formGroup.appendChild(input);
        } else if (field.type === 'textarea') {
            const textarea = document.createElement('textarea');
            textarea.id = field.id; textarea.name = field.id;
            if (field.rows) textarea.rows = field.rows; else textarea.rows = 3;
            if (field.value) textarea.value = field.value;
            if (field.placeholder) textarea.placeholder = field.placeholder;
            if (field.required) textarea.required = true;
            formGroup.appendChild(textarea);
        } else if (field.type === 'select') {
            const select = document.createElement('select');
            select.id = field.id; select.name = field.id;
            field.options.forEach(optVal => {
                const option = document.createElement('option');
                option.value = optVal; option.textContent = optVal;
                if (field.default === optVal) option.selected = true;
                select.appendChild(option);
            });
            formGroup.appendChild(select);
        } else if (field.type === 'radio') {
            const radioGroup = document.createElement('div');
            radioGroup.className = 'radio-group';
            field.options.forEach((optVal, index) => {
                const radioOptionDiv = document.createElement('div');
                radioOptionDiv.className = 'radio-option';
                const radio = document.createElement('input');
                radio.type = 'radio'; radio.id = `${field.id}_${index}`; radio.name = field.id; radio.value = optVal;
                if (field.default === optVal || (index === 0 && !field.default && field.required)) radio.checked = true;
                const radioLabel = document.createElement('label');
                radioLabel.setAttribute('for', `${field.id}_${index}`); radioLabel.textContent = optVal;
                radioOptionDiv.appendChild(radio); radioOptionDiv.appendChild(radioLabel);
                radioGroup.appendChild(radioOptionDiv);
            });
            formGroup.appendChild(radioGroup);
        } else if (field.type === 'checkbox') {
                const checkboxOptionDiv = document.createElement('div');
                checkboxOptionDiv.className = 'checkbox-option';
                const checkbox = document.createElement('input');
                checkbox.type = 'checkbox'; checkbox.id = field.id; checkbox.name = field.id; checkbox.value = "true"; // Common practice
                if (field.default) checkbox.checked = true;
                const checkboxLabel = document.createElement('label'); // Optional: if label text is part of field.label
                checkboxLabel.setAttribute('for', field.id); checkboxLabel.textContent = " " + field.label; // Prepend space
                checkboxOptionDiv.appendChild(checkbox); 
                // formGroup.appendChild(checkbox); // If label is already handled by main label
                formGroup.replaceChild(checkboxOptionDiv, label); // Replace main label if checkbox has its own
                checkboxOptionDiv.insertBefore(label, checkboxOptionDiv.firstChild); // Put main label first
                checkboxOptionDiv.appendChild(checkbox);

        }
        formHtml.appendChild(formGroup);
    });

    const submitButton = document.createElement('button');
    submitButton.type = 'submit';
    submitButton.textContent = formConfig.submit_text || 'Submit';
    formHtml.appendChild(submitButton);
    
    addResponseItem('interaction', `Interaction: ${data.message.title}`, formHtml, data.workflow_instance_id);
});

socket.on('interaction_processed', function(data) {
    console.log('Interaction Processed:', data);
    // The form should already be disabled. We can optionally find the <details> and update its summary.
    const detailsElements = Array.from(responseBox.querySelectorAll('details'));
    const targetDetails = detailsElements.find(d => {
        const summaryText = d.querySelector('summary')?.textContent || "";
        return summaryText.includes("(Submitted - Waiting for continuation...)") &&
                d.innerHTML.includes(data.workflow_instance_id); // Crude check if instance_id was in form
    });
    if(targetDetails){
            targetDetails.querySelector('summary').textContent = targetDetails.querySelector('summary').textContent.replace("(Submitted - Waiting for continuation...)", "(Processed)");
    } else {
            addResponseItem('info', 'Interaction Update', `<p>${data.message} for ${data.workflow_instance_id}</p>`);
    }
});

socket.on('workflow_complete', function(data) {
    console.log('Workflow Complete:', data);
    const resultString = JSON.stringify(data.result, null, 2);
    addResponseItem('complete', `Workflow Completed: ${data.workflow_name}`, `<p>Instance: ${data.workflow_instance_id}</p><pre>${resultString}</pre>`);
    if (currentWorkflowInstanceId === data.workflow_instance_id) {
        currentWorkflowInstanceId = null;
        startWorkflowButton.disabled = false; // Re-enable for new workflow
    }
});

socket.on('workflow_error', function(data) {
    console.error('Workflow Error:', data);
    addResponseItem('error', `Workflow Error: ${data.workflow_name}`, `<p>Instance: ${data.workflow_instance_id}</p><pre>${data.error}</pre>`);
    if (currentWorkflowInstanceId === data.workflow_instance_id) {
        currentWorkflowInstanceId = null;
        startWorkflowButton.disabled = false; // Re-enable
    }
});

socket.on('connect_error', (err) => {
    console.error("Connection Error:", err);
    addResponseItem('error', 'Connection Error', `<p>Could not connect to the server: ${err.message}. Please check if the server is running and refresh the page.</p>`);
    startWorkflowButton.disabled = true;
});


// --- Start Workflow ---
startWorkflowButton.addEventListener('click', function() {
    const selectedWorkflowId = workflowDropdown.value;
    const mainInput = mainInputTextarea.value;

    if (!selectedWorkflowId) {
        alert('Please select a workflow.');
        return;
    }

    // Clear only workflow-specific parts of response box, or all if preferred
    // responseBox.innerHTML = ''; // Or more selectively remove old workflow items
    addResponseItem('info', 'System', `Attempting to start workflow: ${selectedWorkflowId}`);


    startWorkflowButton.disabled = true; // Disable button while a workflow is running

    fetch('/workflows', {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded', },
        body: `workflow_id=${encodeURIComponent(selectedWorkflowId)}&main_input_text=${encodeURIComponent(mainInput)}`
    })
    .then(response => {
        if (!response.ok) { // Check for non-2xx responses
            return response.json().then(errData => {
                throw new Error(errData.message || `Server error: ${response.status}`);
            });
        }
        return response.json();
    })
    .then(data => {
        if (data.status === 'success') {
            currentWorkflowInstanceId = data.workflow_instance_id;
            console.log('Started workflow instance:', currentWorkflowInstanceId);
            addResponseItem('info', 'Workflow Started', `<p>Workflow '${selectedWorkflowId}' initiated. Instance ID: ${currentWorkflowInstanceId}</p>`);
        } else {
            console.error('Failed to start workflow:', data.message);
            addResponseItem('error', 'Failed to Start Workflow', `<p>${data.message}</p>`);
            startWorkflowButton.disabled = false; // Re-enable if start failed immediately
        }
    })
    .catch(error => {
        console.error('Error starting workflow:', error);
        addResponseItem('error', 'Error Starting Workflow', `<p>${error.message}</p>`);
        startWorkflowButton.disabled = false; // Re-enable on fetch error
    });
});

// Initial population of workflows
// fetchAndPopulateWorkflows(); // Moved to 'connected' event
