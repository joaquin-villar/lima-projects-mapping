// frontend/js/ui.js
window.UI = (function () {
    let sidebarCollapsed = false;

    function init() {
        /* ----------------------------
           Sidebar toggle
        ---------------------------- */
        document.getElementById("sidebar-toggle")?.addEventListener("click", toggleSidebar);

        /* ----------------------------
           Tab switching
        ---------------------------- */
        document.querySelectorAll(".tab-button").forEach(btn => {
            btn.addEventListener("click", () => switchTab(btn.dataset.tab));
        });

        /* ----------------------------
           Map style dropdowns
        ---------------------------- */
        const overviewSelect = document.getElementById("map-style-overview");
        const detailSelect = document.getElementById("map-style-detail");

        overviewSelect?.addEventListener("change", () =>
            window.GeneralMap?.setBaseLayer(overviewSelect.value)
        );

        detailSelect?.addEventListener("change", () =>
            window.DistrictMap?.setBaseLayer(detailSelect.value)
        );

        /* -----------------------------------------------
           Populate District Multi-Select (Project Creation - Legacy Sidebar)
        ----------------------------------------------- */
        const districtSelect = document.getElementById("new-project-districts");

        if (districtSelect && AppState.districtsGeoJSON) {
            const names = AppState.districtsGeoJSON.features
                .map(f => f.properties.distrito)
                .sort((a, b) => a.localeCompare(b, "es-PE"));

            districtSelect.innerHTML = names
                .map(name => `<option value="${name}">${name}</option>`)
                .join("");
        }

        /* ----------------------------
           Project Actions
        ---------------------------- */
        document.getElementById("btn-create-project")?.addEventListener("click", () =>
            window.Projects?.createProject()
        );

        document.getElementById("btn-delete-project")?.addEventListener("click", () =>
            window.Projects?.deleteCurrentProject()
        );

        document.getElementById("btn-close-details")?.addEventListener("click", () =>
            window.Projects?.closeProjectDetails()
        );

        document.getElementById("btn-view-on-map")?.addEventListener("click", () =>
            window.Projects?.viewProjectOnMap()
        );

        /* ----------------------------
           District tab actions - MODAL INTEGRATION
        ---------------------------- */
        document.getElementById("btn-new-project-in-district")?.addEventListener("click", () => {
            
            if (AppState.selectedDistrict) {
                // 🟢 AHORA: Pasamos la selección completa directamente.
                // El modal.js ya sabe cómo leer "Lima, Callao" y marcar ambos en el select.
                
                if (window.ProjectModal && typeof window.ProjectModal.open === 'function') {
                    window.ProjectModal.open(AppState.selectedDistrict);
                } else {
                    console.error('ProjectModal not loaded');
                    alert('Error: El modal no está disponible');
                }

            } else {
                // 🔴 CASO ERROR: Sin selección
                if (window.ProjectModal && window.ProjectModal.showNotification) {
                    window.ProjectModal.showNotification("Por favor seleccione al menos un distrito", "error");
                } else {
                    alert("Por favor seleccione al menos un distrito");
                }
                
                // Redirigir al mapa general con un pequeño delay
                setTimeout(() => {
                    switchTab("overview");
                }, 1500);
            }
        });

        document.getElementById("btn-save-drawings")?.addEventListener("click", () =>
            window.Drawings?.saveCurrentDrawings()
        );

        // Renderizar lista inicial de distritos en el sidebar de overview
        // (Se llama también desde app.js al cargar geojson, pero por si acaso)
        if (AppState.districtsGeoJSON) {
             renderOverviewDistricts();
        }

        /* ----------------------------
           Initialize UI state
        ---------------------------- */
        updateSidebarForTab("overview");
        
        // Resize handler para recalcular grid expansion
        window.addEventListener('resize', () => {
            const currentProject = window.Projects?.getCurrentProject();
            if (currentProject && AppState.currentTab === 'projects') {
                window.Projects?.loadProject(currentProject.id);
            }
        });
    }

    function renderOverviewDistricts() {
        const container = document.getElementById("overview-districts-list");
        const districtSelect = document.getElementById("new-project-districts");

        if (!AppState.districtsGeoJSON) return;

        const features = AppState.districtsGeoJSON.features;
        const names = features.map(f => f.properties.distrito).sort((a, b) => a.localeCompare(b, "es-PE"));

        // 1. Poblar lista visual en Overview (si existe el contenedor)
        if (container) {
            container.innerHTML = names.map(name => `
                <div class="district-mini-card" onclick="window.GeneralMap.toggleDistrict('${name}')" title="${name}">
                    <i data-lucide="map-pin" style="width: 14px;"></i>
                    <span>${name}</span>
                </div>
            `).join("");
        }
        
        // 2. Poblar select oculto (Legacy Project Tab) si está vacío
        if (districtSelect && districtSelect.options.length === 0) {
            districtSelect.innerHTML = names
                .map(name => `<option value="${name}">${name}</option>`)
                .join("");
        }

        if (window.lucide) lucide.createIcons();
    }

    function toggleSidebar() {
        const sidebar = document.getElementById("sidebar");
        sidebarCollapsed = !sidebarCollapsed;

        sidebar.classList.toggle("collapsed", sidebarCollapsed);

        sidebar.addEventListener('transitionend', () => {
            window.mapOverview?.invalidateSize();
            window.mapDetail?.invalidateSize();
        }, { once: true });
    }

    function switchTab(tab) {
        AppState.currentTab = tab;

        /* Update active tab button */
        document.querySelectorAll(".tab-button").forEach(btn =>
            btn.classList.remove("active")
        );
        document.querySelector(`.tab-button[data-tab="${tab}"]`)?.classList.add("active");

        /* Switch tab content */
        document.querySelectorAll(".tab-content").forEach(c =>
            c.classList.remove("active")
        );
        document.getElementById(`${tab}-tab`)?.classList.add("active");

        updateSidebarForTab(tab);

        /* Map resize / focus & Load Data */
        setTimeout(() => {
            if (tab === "overview") {
                window.mapOverview?.invalidateSize();
            } else if (tab === "detail") {
                window.mapDetail?.invalidateSize();
                
                if (AppState.selectedDistrict) {
                    window.DistrictMap?.focusOnSelectedDistrict();
                    window.Projects?.loadProjectsForCurrentDistrict();
                    showDistrictStats(AppState.selectedDistrict);
                } else {
                    showDistrictPrompt();
                    // Limpiar stats si no hay distrito
                    const statsContainer = document.getElementById("district-stats-container");
                    if(statsContainer) statsContainer.innerHTML = "";
                }
            }
        }, 150);

        updateSelectedDistrictDisplay();
    }

    function updateSidebarForTab(tab) {
        const overviewSection = document.getElementById("overview-sidebar-section");
        const districtProjectsSection = document.getElementById("district-projects-section");
        const newProjectSection = document.getElementById("new-project-section");

        if(overviewSection) overviewSection.style.display = "none";
        if(districtProjectsSection) districtProjectsSection.style.display = "none";
        if(newProjectSection) newProjectSection.style.display = "none";

        if (tab === "overview") {
            if(overviewSection) overviewSection.style.display = "block";
        }
        else if (tab === "projects") {
            if(newProjectSection) newProjectSection.style.display = "block";
        }
        else if (tab === "detail") {
            if(districtProjectsSection) districtProjectsSection.style.display = "block";
            
            if (AppState.selectedDistrict) {
                window.Projects?.loadProjectsForCurrentDistrict();
                showDistrictStats(AppState.selectedDistrict);
            } else {
                showDistrictPrompt();
            }
        }
    }

    function updateSelectedDistrictDisplay() {
        const s1 = document.getElementById("selected-district-display");
        const s2 = document.getElementById("detail-district-display");

        const rawValue = AppState.selectedDistrict;
        
        // Highlight visual en la lista de overview
        const cards = document.querySelectorAll(".district-mini-card");
        cards.forEach(c => c.classList.remove("active"));
        
        if (rawValue) {
            const selectedArr = rawValue.includes(",") ? rawValue.split(",").map(s=>s.trim()) : [rawValue];
            selectedArr.forEach(name => {
                // Buscar tarjeta por texto (simplificado)
                // Nota: Iteramos para encontrar el div que contiene el texto
                Array.from(cards).forEach(card => {
                    if (card.innerText.trim() === name) card.classList.add("active");
                });
            });
        }

        const generatePills = (value) => {
            if (!value) return '<span style="color: #64748b; font-size: 14px;">Ninguno</span>';

            const districts = value.includes(",") 
                ? value.split(",").map(d => d.trim()).sort() 
                : [value];

            const pillsHTML = districts.map(d => `
                <span class="district-label" 
                      onclick="window.GeneralMap.toggleDistrict('${d}')"
                      title="Clic para deseleccionar ${d}">
                    ${d}
                </span>
            `).join("");

            return `<div class="district-pills-container">${pillsHTML}</div>`;
        };

        const htmlContent = generatePills(rawValue);

        if (s1) s1.innerHTML = htmlContent;
        if (s2) s2.innerHTML = htmlContent;
    }

    function showDistrictPrompt() {
        const listDiv = document.getElementById("district-projects-list");
        const statsDiv = document.getElementById("district-stats-container");
        
        if(statsDiv) statsDiv.innerHTML = "";

        if (listDiv) {
            listDiv.innerHTML = `
                <div class="info-box" style="text-align: center; padding: 24px;">
                    <i data-lucide="map-pin" style="width: 48px; height: 48px; margin: 0 auto 16px; display: block; color: #00B4D8;"></i>
                    <p style="margin-bottom: 8px; font-weight: 600;">Selecciona un distrito</p>
                    <small style="color: #94a3b8;">Haz clic en un distrito del Mapa General</small>
                </div>
            `;
            if (window.lucide) lucide.createIcons();
        }
    }

    async function showDistrictStats(districtName) {
        let statsDiv = document.getElementById("district-stats-container");
        const listDiv = document.getElementById("district-projects-list");
        
        if (listDiv && listDiv.querySelector('.info-box')) listDiv.innerHTML = ''; 
        
        if (!statsDiv && listDiv) {
            statsDiv = document.createElement("div");
            statsDiv.id = "district-stats-container";
            listDiv.parentNode.insertBefore(statsDiv, listDiv);
        }

        if (!statsDiv) return;

        // Lógica para el título (Si son muchos, mostramos resumen)
        let displayTitle = districtName;
        const districtCount = districtName.split(",").length;
        if (districtCount > 2) {
            displayTitle = `${districtCount} Distritos Seleccionados`;
        }

        statsDiv.innerHTML = `
            <div class="district-stats-card" style="text-align: center; padding: 24px;">
                <i data-lucide="loader" style="width: 24px; height: 24px; margin: 0 auto 12px; display: block; color: #00B4D8; animation: spin 1s linear infinite;"></i>
                <p style="color: #94a3b8; font-size: 13px;">Analizando datos...</p>
            </div>
        `;
        if (window.lucide) lucide.createIcons();

        try {
            const encoded = encodeURIComponent(districtName);
            // IMPORTANTE: Este endpoint ya debe soportar comas gracias al fix del backend
            const projects = await Api.get(`/api/districts/${encoded}/projects`);

            const total = projects.length;
            const active = projects.filter(p => p.status === 'active').length;
            const inactive = projects.filter(p => p.status === 'inactive').length;
            const completed = projects.filter(p => p.status === 'completed').length;
            const archived = projects.filter(p => p.status === 'archived').length;

            statsDiv.innerHTML = `
                <div class="district-stats-card">
                    <div class="stats-header" style="display: flex; justify-content: space-between; align-items: center;">
                        <div style="display: flex; align-items: center; gap: 10px; overflow: hidden;">
                            <i data-lucide="bar-chart-3" style="flex-shrink: 0;"></i>
                            <h3 style="white-space: nowrap; overflow: hidden; text-overflow: ellipsis; font-size: 14px;">
                                ${displayTitle}
                            </h3>
                        </div>
                        <span style="background: rgba(0, 180, 216, 0.1); color: #00B4D8; padding: 4px 10px; border-radius: 12px; font-weight: 700; font-size: 14px; flex-shrink: 0;">
                            Total: ${total}
                        </span>
                    </div>
                    
                    <div class="stats-grid">
                        <div class="stat-item stat-active">
                            <i data-lucide="play-circle"></i>
                            <div class="stat-content">
                                <span class="stat-value">${active}</span>
                                <span class="stat-label">Activos</span>
                            </div>
                        </div>

                        <div class="stat-item stat-inactive">
                            <i data-lucide="pause-circle"></i>
                            <div class="stat-content">
                                <span class="stat-value">${inactive}</span>
                                <span class="stat-label">Inactivos</span>
                            </div>
                        </div>
                        
                        <div class="stat-item stat-completed">
                            <i data-lucide="check-circle"></i>
                            <div class="stat-content">
                                <span class="stat-value">${completed}</span>
                                <span class="stat-label">Hechos</span>
                            </div>
                        </div>

                        <div class="stat-item stat-archived">
                            <i data-lucide="archive"></i>
                            <div class="stat-content">
                                <span class="stat-value">${archived}</span>
                                <span class="stat-label">Archivados</span>
                            </div>
                        </div>
                    </div>
                </div>
            `;

            if (window.lucide) lucide.createIcons();

        } catch (error) {
            console.error('Error loading district stats:', error);
            statsDiv.innerHTML = `
                <div class="district-stats-card" style="border-color: #ef4444;">
                    <div style="color: #ef4444; text-align: center; padding: 10px;">
                        <i data-lucide="alert-circle" style="margin: 0 auto 8px;"></i>
                        <p>Error cargando datos</p>
                    </div>
                </div>
            `;
            if (window.lucide) lucide.createIcons();
        }
    }

    return {
        init,
        renderOverviewDistricts, // Exponemos esta función para app.js
        switchTab,
        toggleSidebar,
        updateSidebarForTab,
        updateSelectedDistrictDisplay,
        showDistrictStats
    };
})();