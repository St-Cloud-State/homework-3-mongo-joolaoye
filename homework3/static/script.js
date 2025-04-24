function showSnackbar(message, type = '') {
    const snackbar = document.getElementById('snackbar');
    snackbar.textContent = message;
    snackbar.className = 'snackbar show ' + type;
    setTimeout(() => {
        snackbar.className = snackbar.className.replace('show', '');
    }, 3000);
}

function toggleDropdown(event, id) {
    event.preventDefault()
    const dropdown = document.getElementById(id)
    dropdown.style.display = (dropdown.style.display === "block") ? "none" : "block"
}

async function submitApplication() {
    const name = document.getElementById('name').value.trim();
    const address = document.getElementById('address').value.trim();

    if (!name || !address) {
        showSnackbar('Please fill in all fields', 'error');
        return;
    }

    try {
        const response = await fetch("/api/applications", {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                applicant_name: name,
                applicant_address: address
            })
        });

        const data = await response.json();
        
        if (response.ok) {
            showSnackbar(data.message, 'success');
            document.getElementById('name').value = '';
            document.getElementById('address').value = '';
        } else {
            showSnackbar(data.message || 'Error creating application', 'error');
        }
    } catch (error) {
        showSnackbar('Error connecting to server', 'error');
    }
}

async function addNote() {
    const appId = document.getElementById('applicationID').value.trim();
    const note = document.getElementById('note').value.trim();

    if (!appId) {
        showSnackbar('Please enter an application number', 'error');
        return;
    }

    if (!note) {
        showSnackbar('Note cannot be empty', 'error');
        return;
    }

    try {
        const response = await fetch(`/api/applications/notes/${appId}`, {
            method: 'PATCH',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(
                {"note": note}
            )
        });

        const data = await response.json();

        if (response.ok) {
            showSnackbar(data.message, 'success');
            document.getElementById('note').value = '';
        } else {
            showSnackbar(data.message || 'Error updating status', 'error');
        }
    } catch(error) {
        showSnackbar('Error connecting to server', 'error');
    }

}

async function updateStatus(status) {
    const appId = document.getElementById('applicationID').value.trim();

    if (!appId) {
        showSnackbar('Please enter an application number', 'error');
        return;
    }

    const payload = {"status": status};

    if (status === "rejected") {
        const rejection_reason = document.getElementById('reason').value.trim();
        payload["rejection_reason"] = rejection_reason
    }

    try {
        const response = await fetch(`/api/applications/status/${appId}`, {
            method: 'PATCH',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(payload)
        });

        const data = await response.json();
        
        if (response.ok) {
            showSnackbar(data.message, 'success');
            document.getElementById('applicationID').value = '';
            if (status === "rejected") {
                document.getElementById('reason').value = '';
            }
        } else {
            showSnackbar(data.message || 'Error updating status', 'error');
        }
    } catch (error) {
        showSnackbar('Error connecting to server', 'error');
    }
}

function toggleNoteArea() {
    const textarea = document.getElementById("noteArea");
    textarea.style.display = textarea.style.display === "none" ? "block" : "none";

    const acceptButton = document.getElementById("acceptButton");
    acceptButton.style.display = acceptButton.style.display === "block" ? "none" : "block";

    const toggleButton = document.getElementById("toggleNote")
    toggleButton.innerHTML = textarea.style.display === "block" ? '<i class="fa fa-minus"></i>' : '<i class="fa fa-plus"></i>'
}


function getNotes() {
    const appId = document.getElementById('applicationID').value.trim();
  
    if (appId) {
        window.open(`/applications/notes/results?application_id=${appId}`, "_blank")
        document.getElementById('applicationID').value = '';
    }
    else {
        showSnackbar('Please enter an application number', 'error');
        return;
    } 
}

async function loadNotes() {
    const params = new URLSearchParams(window.location.search)
    const appId = params.get("application_id")

    try {
        const response = await fetch(`/api/applications/notes/${appId}`);
        const data = await response.json();

        const container = document.getElementById("notesContainer");
        container.innerHTML = "";

        if (data.notes && data.notes.length > 0) {
            data.notes.forEach(note => {
                const noteElement = document.createElement("div");
                noteElement.className = "note-card";

                noteElement.innerHTML = `
                    <div>${note}</div>
                `;

                container.appendChild(noteElement);
            });
        } else {
            container.innerHTML = "<p>No notes found for this application.</p>";
        }

    } catch (error) {
        showSnackbar("Failed to load notes", "error");
    }
}

async function loadPendingApplications() {
    try {
        const response = await fetch('/api/applications/status/pending');
        const data = await response.json();
        
        const container = document.getElementById('applicationsTable');

        if (data.message && data.message.length > 0) {
            data.message.forEach(application => {
                const row = document.createElement("tr")
                row.innerHTML = `
                    <td>${application.application_id}</td>
                    <td>${application.applicant_name}</td>
                    <td>${application.applicant_address}</td>
                `;
          container.appendChild(row);
            });
        } else {
            const row = document.createElement("tr");
            row.innerHTML = `<td colspan="3">No pending applications.</td>`
            container.appendChild(row);
        }
    } catch (error) {
        showSnackbar("Failed to load notes", "error");
    }
}
