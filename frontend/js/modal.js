// frontend/js/modal.js

// ================================================
// MODAL CONTROLLER - CREATE & EDIT
// ================================================

let projectBeingEditedId = null;

/**
 * Opens the project modal
 * @param {string|object} data - District Name (for create) OR Project Object (for edit)
 */
function openProjectModal(data) {
    const modal = document.getElementById('project-modal');
    const title = modal.querySelector('.modal-title');
    const submitBtn = document.getElementById('modal-submit-btn');
    const districtSelect = document.getElementById('modal-project-districts');

    // Resetear estado
    projectBeingEditedId = null;

    // 1. POBLAR EL SELECTOR DE DISTRITOS
    // Obtenemos la lista maestra desde el AppState (GeoJSON cargado)
    if (window.AppState && window.AppState.districtsGeoJSON) {
        const allDistricts = window.AppState.districtsGeoJSON.features
            .map(f => f.properties.distrito)
            .sort((a, b) => a.localeCompare(b, "es-PE"));

        districtSelect.innerHTML = allDistricts
            .map(d => `<option value="${d}">${d}</option>`)
            .join("");
    }

    // Helper para seleccionar opciones en el select múltiple
    const setSelectedDistricts = (districtsToSelect) => {
        // Convertimos a array si viene como string único
        const targets = Array.isArray(districtsToSelect) ? districtsToSelect : [districtsToSelect];

        Array.from(districtSelect.options).forEach(option => {
            option.selected = targets.includes(option.value);
        });
    };

    // 2. DETERMINAR MODO (Crear vs Editar)
    if (typeof data === 'object' && data.id) {
        // --- MODO EDICIÓN ---
        const project = data;
        projectBeingEditedId = project.id;

        title.innerHTML = '<i data-lucide="edit-3"></i> Editar Proyecto';
        submitBtn.innerHTML = '<i data-lucide="save"></i> Guardar Cambios';

        document.getElementById('modal-project-name').value = project.name;
        document.getElementById('modal-project-desc').value = project.description || '';
        document.getElementById('modal-project-status').value = project.status;

        // Marcar los distritos actuales del proyecto
        setSelectedDistricts(project.districts);

    } else {
        // --- MODO CREACIÓN ---
        // data es el nombre del distrito (o lista separada por comas)
        const districtInput = data;

        title.innerHTML = '<i data-lucide="map-pin"></i> Nuevo Proyecto';
        submitBtn.innerHTML = '<i data-lucide="check"></i> Crear Proyecto';

        document.getElementById('modal-project-name').value = '';
        document.getElementById('modal-project-desc').value = '';
        document.getElementById('modal-project-status').value = 'active';

        // Marcar el/los distritos seleccionados en el mapa
        const districtsToSelect = districtInput.includes(',')
            ? districtInput.split(',').map(d => d.trim())
            : [districtInput];

        setSelectedDistricts(districtsToSelect);
    }

    modal.classList.add('active');
    document.body.style.overflow = 'hidden';

    if (window.lucide) lucide.createIcons();
}

function closeProjectModal() {
    const modal = document.getElementById('project-modal');
    modal.classList.remove('active');
    document.body.style.overflow = '';
    projectBeingEditedId = null;
}

async function handleModalSubmit() {
    const submitBtn = document.getElementById('modal-submit-btn');
    const name = document.getElementById('modal-project-name').value.trim();
    const description = document.getElementById('modal-project-desc').value.trim();
    const status = document.getElementById('modal-project-status').value;
    const districtSelect = document.getElementById('modal-project-districts');

    // Obtener distritos seleccionados del <select multiple>
    const selectedDistricts = Array.from(districtSelect.selectedOptions).map(opt => opt.value);

    // Validaciones
    if (!name) {
        showNotification('El nombre es obligatorio', 'error');
        return;
    }
    if (selectedDistricts.length === 0) {
        showNotification('Debes seleccionar al menos un distrito', 'error');
        return;
    }

    const projectData = {
        name: name,
        description: description || '',
        status: status,
        districts: selectedDistricts // Enviamos la nueva selección
    };

    try {
        submitBtn.disabled = true;
        const originalHTML = submitBtn.innerHTML;
        submitBtn.innerHTML = '<i data-lucide="loader" style="animation: spin 1s linear infinite;"></i> Procesando...';
        if (window.lucide) lucide.createIcons();

        if (projectBeingEditedId) {
            // --- ACTUALIZAR ---
            if (window.Projects && typeof window.Projects.updateProjectFromModal === 'function') {
                await window.Projects.updateProjectFromModal(projectBeingEditedId, projectData);
                showNotification(`Proyecto actualizado`, 'success');
            }
        } else {
            // --- CREAR ---
            if (window.Projects && typeof window.Projects.createProjectFromModal === 'function') {
                await window.Projects.createProjectFromModal(projectData);
                showNotification(`Proyecto "${name}" creado`, 'success');
            }
        }

        closeProjectModal();

    } catch (error) {
        console.error('Error submitting form:', error);
        // Only show generic error if it wasn't already handled by the API auth interceptor
        if (!error.message.includes('Auth Error')) {
            showNotification('Error al procesar. Verifica los datos.', 'error');
        }
    } finally {
        submitBtn.disabled = false;
        // Restaurar icono si el modal sigue abierto
        if (document.getElementById('project-modal').classList.contains('active')) {
            submitBtn.innerHTML = projectBeingEditedId
                ? '<i data-lucide="save"></i> Guardar Cambios'
                : '<i data-lucide="check"></i> Crear Proyecto';
            if (window.lucide) lucide.createIcons();
        }
    }
}

function showNotification(message, type = 'success') {
    const existing = document.querySelector('.toast-notification');
    if (existing) existing.remove();

    const notification = document.createElement('div');
    notification.className = `toast-notification toast-${type}`;
    notification.innerHTML = `
        <div class="toast-content">
            <i data-lucide="${type === 'success' ? 'check-circle' : 'alert-circle'}"></i>
            <span>${message}</span>
        </div>
    `;

    document.body.appendChild(notification);
    if (window.lucide) lucide.createIcons();

    setTimeout(() => notification.classList.add('show'), 10);
    setTimeout(() => {
        notification.classList.remove('show');
        setTimeout(() => notification.remove(), 300);
    }, 3000);
}

document.addEventListener('DOMContentLoaded', () => {
    document.getElementById('modal-close-btn')?.addEventListener('click', closeProjectModal);
    document.getElementById('modal-cancel-btn')?.addEventListener('click', closeProjectModal);

    document.getElementById('modal-submit-btn')?.addEventListener('click', (e) => {
        e.preventDefault();
        handleModalSubmit();
    });

    const modalOverlay = document.getElementById('project-modal');
    if (modalOverlay) {
        modalOverlay.addEventListener('click', (e) => {
            if (e.target === modalOverlay) closeProjectModal();
        });
    }

    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') {
            const modal = document.getElementById('project-modal');
            if (modal && modal.classList.contains('active')) closeProjectModal();
        }
    });
});

window.ProjectModal = {
    open: openProjectModal,
    close: closeProjectModal,
    showNotification: showNotification
};