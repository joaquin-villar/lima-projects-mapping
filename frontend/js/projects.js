// frontend/js/projects.js
window.Projects = (function () {
    let currentProject = null;

    /* ---------------------------------------------------------
       HELPER: NOTIFICATIONS
    --------------------------------------------------------- */
    function notify(message, type = 'success') {
        if (window.ProjectModal && typeof window.ProjectModal.showNotification === 'function') {
            window.ProjectModal.showNotification(message, type);
        } else {
            alert(message);
        }
    }

    /* ---------------------------------------------------------
       LOAD ALL PROJECTS (Projects tab)
    --------------------------------------------------------- */
    async function loadProjects() {
        try {
            // 1. Salvar el panel de detalles antes de regenerar la lista
            const detailsSection = document.getElementById("project-details-section");
            const projectsContainer = document.querySelector('.projects-content');

            if (detailsSection && detailsSection.parentNode.id === "project-list") {
                projectsContainer.appendChild(detailsSection);
                detailsSection.style.display = "none";
            }

            const projects = await Api.get("/api/projects");
            const listDiv = document.getElementById("project-list");

            if (!projects.length) {
                listDiv.innerHTML = `
                    <div class="empty-state">
                        <div class="empty-icon"><i data-lucide="list"></i></div>
                        <p>No hay proyectos todavía</p>
                        <small>Usa el panel lateral para crear tu primer proyecto</small>
                    </div>`;
                if (window.lucide) lucide.createIcons();
                return;
            }

            listDiv.innerHTML = projects.map(p => `
                <div class="project-card ${currentProject?.id === p.id ? "active" : ""}" 
                     data-id="${p.id}">
                     
                    <div class="project-name">${escapeHTML(p.name)}</div>

                    <div class="project-description">
                        ${escapeHTML(p.description || "Sin descripción")}
                    </div>

                    <div class="project-meta">
                        <span class="status-badge ${p.status}">
                            ${getStatusText(p.status)}
                        </span>
                        <span>${formatDate(p.created_at)}</span>
                    </div>

                    <div class="district-badges">
                        ${p.districts.map(d => `<span class="district-badge">${d}</span>`).join("")}
                    </div>

                </div>
            `).join("");

            document.querySelectorAll(".project-card").forEach(el =>
                el.addEventListener("click", () => loadProject(el.dataset.id))
            );

            // Restaurar panel si había un proyecto abierto
            if (currentProject) {
                setTimeout(() => injectDetailsPanelAfterRow(currentProject.id), 0);
            }

            if (window.lucide) lucide.createIcons();
        } catch (err) {
            console.error(err);
            console.log("Error cargando lista de proyectos");
        }
    }

    /* ---------------------------------------------------------
       GRID EXPANSION LOGIC
    --------------------------------------------------------- */
    function injectDetailsPanelAfterRow(projectId) {
        const grid = document.getElementById("project-list");
        const detailsSection = document.getElementById("project-details-section");

        const cards = Array.from(grid.querySelectorAll(".project-card"));
        const selectedCard = grid.querySelector(`.project-card[data-id="${projectId}"]`);

        if (!selectedCard || !detailsSection) return;

        detailsSection.style.display = "block";

        const gridWidth = grid.offsetWidth;
        const cardWidth = cards[0].offsetWidth;
        const gap = 24;

        const columns = Math.floor((gridWidth + gap) / (cardWidth + gap)) || 1;
        const index = cards.indexOf(selectedCard);

        const currentRow = Math.floor(index / columns);
        let lastCardInRowIndex = (currentRow + 1) * columns - 1;

        if (lastCardInRowIndex >= cards.length) {
            lastCardInRowIndex = cards.length - 1;
        }

        const referenceCard = cards[lastCardInRowIndex];

        if (lastCardInRowIndex === cards.length - 1) {
            grid.appendChild(detailsSection);
        } else {
            grid.insertBefore(detailsSection, referenceCard.nextSibling);
        }

        setTimeout(() => {
            detailsSection.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
        }, 100);
    }

    /* ---------------------------------------------------------
       CREATE PROJECT (Sidebar Form)
    --------------------------------------------------------- */
    async function createProject() {
        const nameInput = document.getElementById("new-project-name");
        const descInput = document.getElementById("new-project-desc");
        const statusInput = document.getElementById("new-project-status");
        const districtSelect = document.getElementById("new-project-districts");

        const name = nameInput.value.trim();
        const desc = descInput.value.trim();
        const status = statusInput.value;
        const districts = [...districtSelect.selectedOptions].map(o => o.value);

        if (!name) return notify("Por favor, ingresa un nombre para el proyecto", "error");
        if (!districts.length) return notify("Selecciona al menos un distrito", "error");

        try {
            const newProject = await Api.post("/api/projects", {
                name, description: desc, status, districts
            });

            nameInput.value = "";
            descInput.value = "";
            statusInput.value = "active";
            for (let i = 0; i < districtSelect.options.length; i++) districtSelect.options[i].selected = false;

            await loadProjects();
            await loadProject(newProject.id);

            notify(`Proyecto "${newProject.name}" creado exitosamente`, "success");
        } catch (err) {
            console.error(err);
            notify("Error al crear el proyecto. Intenta nuevamente.", "error");
        }
    }

    /* ---------------------------------------------------------
       LOAD PROJECT DETAILS
    --------------------------------------------------------- */
    async function loadProject(projectId) {
        try {
            document.querySelectorAll(".project-card").forEach(c => c.classList.remove("active"));
            const card = document.querySelector(`.project-card[data-id="${projectId}"]`);
            if (card) card.classList.add("active");

            currentProject = await Api.get(`/api/projects/${projectId}`);

            document.getElementById("current-project-info").innerHTML = `
                <div style="display: flex; justify-content: space-between; align-items: start;">
                    <div>
                        <strong style="font-size: 22px;">${escapeHTML(currentProject.name)}</strong>
                        <div style="margin-top: 8px; margin-bottom: 12px;">
                            <span class="status-badge ${currentProject.status}">${getStatusText(currentProject.status)}</span>
                        </div>
                    </div>
                    <button id="btn-edit-project-modal" class="action-btn secondary" style="width: auto; padding: 8px 12px;">
                        <i data-lucide="edit-3"></i> Editar
                    </button>
                </div>
                
                <p style="color: #cbd5e1; line-height: 1.6;">${escapeHTML(currentProject.description || "Sin descripción")}</p>
                
                <div style="margin-top: 16px; font-size: 13px; color: #94a3b8;">
                    <span><i data-lucide="calendar" style="width:14px; display:inline;"></i> ${formatDate(currentProject.created_at)}</span>
                </div>
            `;

            document.getElementById("project-districts").innerHTML =
                currentProject.districts
                    .map(d => `<span class="district-badge">${d}</span>`)
                    .join("");

            // Listener para botón Editar
            document.getElementById("btn-edit-project-modal").addEventListener("click", () => {
                if (window.ProjectModal) {
                    window.ProjectModal.open(currentProject);
                }
            });

            if (window.Drawings) await Drawings.loadProjectDrawings(currentProject.id);

            injectDetailsPanelAfterRow(projectId);
            if (window.lucide) lucide.createIcons();

        } catch (err) {
            console.error(err);
            notify("Error cargando detalles del proyecto", "error");
        }
    }

    /* ---------------------------------------------------------
       PROJECTS FOR CURRENT DISTRICT (Detail tab)
       🟢 ACTUALIZADO CON LÓGICA DE TOGGLE
    --------------------------------------------------------- */
    async function loadProjectsForCurrentDistrict() {
        if (!AppState.selectedDistrict) return;

        try {
            const encoded = encodeURIComponent(AppState.selectedDistrict);
            const projects = await Api.get(`/api/districts/${encoded}/projects`);
            const listDiv = document.getElementById("district-projects-list");

            if (!projects.length) {
                listDiv.innerHTML = `
                    <div class="info-box" style="margin-top: 10px;">
                        No hay proyectos en este distrito
                    </div>`;
                return;
            }

            listDiv.innerHTML = projects.map(p => `
                <div class="project-card" data-id="${p.id}">
                    <div class="project-name">${escapeHTML(p.name)}</div>
                    <div class="project-description">${escapeHTML(p.description || "")}</div>
                    <div class="project-meta">
                        <span class="status-badge ${p.status}">${getStatusText(p.status)}</span>
                    </div>
                </div>
            `).join("");

            // 🟢 NUEVO: Renderizar dibujos de TODOS los proyectos del distrito en los mapas
            if (window.Drawings) {
                const detailLayer = window.DistrictMap?.getDrawingLayer();
                Drawings.renderProjects(projects, detailLayer, { clear: true });
            }

            // Seleccionamos todas las tarjetas recién creadas
            const cards = document.querySelectorAll("#district-projects-list .project-card");

            cards.forEach(el => {

                // 🟢 1. UN SOLO CLICK: Toggle (Seleccionar / Deseleccionar)
                el.addEventListener("click", async () => {
                    // Comprobamos si esta tarjeta YA estaba activa
                    const isAlreadyActive = el.classList.contains("active");

                    // A. Limpieza General: Quitamos active de todos y limpiamos mapas
                    cards.forEach(c => c.classList.remove("active"));

                    // Limpiar capas de dibujo inmediatamente para evitar confusión visual
                    if (window.DistrictMap) window.DistrictMap.getDrawingLayer().clearLayers();

                    if (isAlreadyActive) {
                        // --- CASO DESELECCIONAR ---
                        console.log("Proyecto deseleccionado");
                        currentProject = null;

                        // Volver a renderizar todos en azul
                        if (window.Drawings) {
                            const detailLayer = window.DistrictMap?.getDrawingLayer();
                            Drawings.renderProjects(projects, detailLayer, { clear: true });
                        }
                    } else {
                        // --- CASO SELECCIONAR ---
                        el.classList.add("active");
                        const projectId = parseInt(el.dataset.id);

                        try {
                            currentProject = await Api.get(`/api/projects/${projectId}`);

                            // Cargamos dibujos (Modo Edición: loadProjectDrawings se encarga de todo)
                            if (window.Drawings) {
                                await Drawings.loadProjectDrawings(projectId);
                            }
                        } catch (e) {
                            console.error("Error al seleccionar proyecto", e);
                        }
                    }
                });

                // 🟢 2. DOBLE CLICK: Ir a Gestión (Se mantiene igual)
                el.addEventListener("dblclick", () => {
                    loadProject(el.dataset.id);
                    if (window.UI) UI.switchTab("projects");
                });
            });

            if (window.lucide) lucide.createIcons();
        } catch (err) {
            console.error(err);
        }
    }

    /* ---------------------------------------------------------
       MODAL ACTIONS
    --------------------------------------------------------- */
    async function createProjectFromModal(projectData) {
        try {
            const newProject = await Api.post("/api/projects", projectData);
            if (window.UI) UI.switchTab("projects");
            await loadProjects();
            await loadProject(newProject.id);
            return newProject;
        } catch (err) {
            console.error('Error creating project:', err);
            throw err;
        }
    }

    async function updateProjectFromModal(projectId, projectData) {
        try {
            const updatedProject = await Api.put(`/ api / projects / ${projectId} `, projectData);
            await loadProjects();
            await loadProject(updatedProject.id);
            return updatedProject;
        } catch (err) {
            console.error('Error updating project:', err);
            throw err;
        }
    }

    /* ---------------------------------------------------------
       DELETE PROJECT
    --------------------------------------------------------- */
    let isDeleting = false;
    async function deleteCurrentProject() {
        if (!currentProject || isDeleting) return;

        const confirmed = await window.Auth.showConfirm(`¿Estás seguro de que deseas eliminar permanentemente el proyecto "${currentProject.name}" ? `);
        if (!confirmed) return;

        isDeleting = true;
        const deletedId = currentProject.id;
        const deletedName = currentProject.name;

        try {
            await Api.del(`/ api / projects / ${deletedId} `);

            // Importante: Limpiar estado ANTES de recargar
            currentProject = null;
            closeProjectDetails();

            await loadProjects();

            if (window.GeneralMap) window.GeneralMap.getDrawingLayer().clearLayers();
            if (window.DistrictMap) window.DistrictMap.getDrawingLayer().clearLayers();

            notify(`Proyecto "${deletedName}" eliminado`, "success");
        } catch (err) {
            console.error("Delete Error:", err);
            // Only show error if it wasn't already handled by the API auth interceptor
            if (!err.message.includes('Auth Error')) {
                notify("Error eliminando proyecto: " + (err.message || "Error desconocido"), "error");
            }
        } finally {
            isDeleting = false;
        }
    }

    /* ---------------------------------------------------------
       Helpers
    --------------------------------------------------------- */
    function getStatusText(status) {
        const statusMap = {
            active: "Activo", completed: "Completado", inactive: "Inactivo", archived: "Archivado"
        };
        return statusMap[status] || status;
    }

    function formatDate(d) {
        if (!d) return "";
        return new Date(d).toLocaleDateString("es-PE", { year: "numeric", month: "short", day: "numeric" });
    }

    function escapeHTML(str) {
        if (!str) return "";
        const div = document.createElement('div');
        div.textContent = str;
        return div.innerHTML;
    }

    function closeProjectDetails() {
        currentProject = null;
        const detailsSection = document.getElementById("project-details-section");
        if (detailsSection) {
            detailsSection.style.display = "none";
        }
        document.querySelectorAll(".project-card").forEach(c => c.classList.remove("active"));

        if (window.GeneralMap) window.GeneralMap.getDrawingLayer().clearLayers();
        if (window.DistrictMap) window.DistrictMap.getDrawingLayer().clearLayers();
    }

    function viewProjectOnMap() {
        if (!currentProject) return;

        if (currentProject.districts && currentProject.districts.length > 0) {
            if (window.GeneralMap) {
                window.GeneralMap.deselectAll(false);
                currentProject.districts.forEach(distrito => {
                    window.GeneralMap.toggleDistrict(distrito);
                });
            }
            if (window.UI) UI.switchTab("detail");
            const distStr = currentProject.districts.join(", ");
            notify(`Visualizando ${currentProject.name} en: ${distStr} `, "success");
        } else {
            notify("Este proyecto no tiene distritos asignados", "error");
        }
    }

    return {
        loadProjects,
        createProject,
        createProjectFromModal,
        updateProjectFromModal,
        loadProject,
        loadProjectsForCurrentDistrict,
        deleteCurrentProject,
        getCurrentProject: () => currentProject,

        viewProjectOnMap,
        closeProjectDetails
    };
})();