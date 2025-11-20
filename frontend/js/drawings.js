// frontend/js/drawings.js
window.Drawings = (function () {
    
    // Helper para notificaciones (consistente con el resto de la app)
    function notify(message, type = 'success') {
        if (window.ProjectModal && typeof window.ProjectModal.showNotification === 'function') {
            window.ProjectModal.showNotification(message, type);
        } else {
            alert(message);
        }
    }

    async function loadProjectDrawings(projectId) {
        try {
            const drawings = await Api.get(`/api/projects/${projectId}/drawings`);

            // Obtenemos las capas de dibujo de AMBOS mapas por seguridad
            const overviewLayer = window.GeneralMap?.getDrawingLayer();
            const detailLayer = window.DistrictMap?.getDrawingLayer();

            // Limpiamos
            if (overviewLayer) overviewLayer.clearLayers();
            if (detailLayer) detailLayer.clearLayers();

            // Dibujamos
            drawings.forEach(d => {
                const geo = JSON.parse(d.geojson);
                
                // Agregamos a ambos mapas para mantener sincronía visual
                if (overviewLayer) L.geoJSON(geo).addTo(overviewLayer);
                if (detailLayer) L.geoJSON(geo).addTo(detailLayer);
            });
        } catch (err) {
            console.error(err);
            // No notificamos aquí para no spamear al navegar
        }
    }

    async function saveCurrentDrawings() {
        const project = Projects.getCurrentProject();
        
        // 1. Validación: Proyecto seleccionado
        if (!project) {
            return notify("Selecciona un proyecto primero (haz clic en una tarjeta)", "error");
        }

        // Determinar de qué mapa sacar los dibujos según el tab activo
        let drawingLayer;
        if (AppState.currentTab === "overview") {
            drawingLayer = window.GeneralMap?.getDrawingLayer();
        } else {
            drawingLayer = window.DistrictMap?.getDrawingLayer();
        }

        if (!drawingLayer) return;

        const layersGeoJSON = drawingLayer.toGeoJSON();

        // 2. Validación: Hay dibujos?
        if (!layersGeoJSON.features.length) {
            return notify("No hay dibujos para guardar en el mapa", "error");
        }

        // 3. Guardado
        try {
            // Usamos el endpoint Batch que creamos en el backend
            const payload = {
                drawings: layersGeoJSON.features.map(feature => ({
                    geojson: feature,
                    drawing_type: feature.geometry.type
                }))
            };

            // Primero borramos los anteriores (estrategia simple de reemplazo)
            // Opcional: Si tu backend batch no borra, podrías necesitar limpiar antes.
            // Asumiremos que el usuario quiere guardar LO QUE VE.
            // Si tu backend solo agrega, esto duplicará.
            // Para un MVP de dibujo, lo ideal es: Borrar todo lo del proyecto -> Insertar lo nuevo.
            
            // Nota: Como tu backend actual solo tiene "add", vamos a asumir adición
            // O implementar una lógica de "replace" en el futuro.
            
            await Api.post(`/api/projects/${project.id}/drawings/batch`, payload);
            
            notify(`Dibujos guardados exitosamente en "${project.name}"`, "success");
            
        } catch (err) {
            console.error(err);
            notify("Error guardando dibujos", "error");
        }
    }

    return {
        loadProjectDrawings,
        saveCurrentDrawings
    };
})();