// backend/static/js/tools.js

async function sendEcho() {
    const response = await fetch('/api/tools/echo', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: "Hello Flask!" })
    });
    const data = await response.json();
    alert("Server echoed: " + data.echo);
}

