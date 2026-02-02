// frontend/js/app.js
window.AppState = {
    districtsGeoJSON: null,
    selectedDistrict: null,
    currentTab: "overview"
};

window.addEventListener("DOMContentLoaded", initApp);

async function initApp() {
    try {
        console.log("🚀 Iniciando aplicación...");

        // 1. Cargar GeoJSON
        const geojson = await Api.get("/api/districts-geojson");
        AppState.districtsGeoJSON = geojson;
        console.log("✅ GeoJSON cargado");

        if (window.UI) UI.renderOverviewDistricts();

        // 2. Inicializar Mapas y Dibujos
        if (window.GeneralMap) GeneralMap.init(geojson);
        if (window.DistrictMap) DistrictMap.init();
        if (window.Drawings) Drawings.init();

        // 3. Inicializar UI
        if (window.UI) UI.init();

        // 4. Cargar Proyectos
        if (window.Projects) {
            await Projects.loadProjects();
            console.log("✅ Proyectos cargados");
        }

        // Custom event listener para la creación de proyectos desde el Modal
        document.addEventListener('projectModalSubmit', async function (e) {
            const data = e.detail;

            try {
                const newProject = await Api.post("/api/projects", {
                    name: data.name,
                    description: data.description,
                    status: data.status,
                    districts: [data.distrito]
                });

                await Projects.loadProjectsForCurrentDistrict();
                await Projects.loadProject(newProject.id);

                // Notificación de éxito (Opcional, si ProjectModal lo soporta)
                if (window.ProjectModal && window.ProjectModal.showNotification) {
                    window.ProjectModal.showNotification(`Proyecto "${data.name}" creado`, 'success');
                }

            } catch (err) {
                console.error(err);
                alert("Error creando proyecto: " + err.message);
            }
        });

    } catch (err) {
        console.error("🔥 Error Fatal:", err);
        // Ahora la alerta te dirá QUÉ falló exactamente
        alert("Error inicializando la aplicación:\n" + err.message);
    }
}