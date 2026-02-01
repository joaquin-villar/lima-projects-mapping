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

    function renderProjects(projects, targetLayer, options = {}) {
        if (!targetLayer) return;

        const { clear = false, highlightId = null } = options;
        if (clear) targetLayer.clearLayers();

        projects.forEach(p => {
            const isHighlighted = p.id === highlightId;

            p.drawings.forEach(d => {
                try {
                    const geo = typeof d.geojson === 'string' ? JSON.parse(d.geojson) : d.geojson;

                    const geoLayer = L.geoJSON(geo, {
                        style: {
                            color: isHighlighted ? "#22c55e" : "#00B4D8",
                            weight: isHighlighted ? 5 : 3,
                            opacity: 1,
                            fillOpacity: 0.2
                        },
                        pointToLayer: (feature, latlng) => {
                            return L.circleMarker(latlng, {
                                radius: isHighlighted ? 10 : 7,
                                fillColor: isHighlighted ? "#22c55e" : "#00B4D8",
                                color: "#fff",
                                weight: 2,
                                opacity: 1,
                                fillOpacity: 0.8
                            });
                        }
                    });

                    geoLayer.bindTooltip(`<strong>${p.name}</strong><br>${p.status}`, {
                        sticky: true,
                        className: 'custom-tooltip'
                    });

                    geoLayer.addTo(targetLayer);

                    // Si estamos cargando un solo proyecto resaltado, centrar el mapa
                    if (isHighlighted && options.fitBounds !== false) {
                        const map = targetLayer === window.GeneralMap?.getDrawingLayer()
                            ? window.mapOverview
                            : window.mapDetail;
                        if (map) {
                            if (geo.type === "Point") {
                                map.setView([geo.coordinates[1], geo.coordinates[0]], 16);
                            } else {
                                map.fitBounds(geoLayer.getBounds(), { padding: [50, 50] });
                            }
                        }
                    }
                } catch (e) {
                    console.error("Error parsing geojson", e);
                }
            });
        });
    }

    async function loadProjectDrawings(projectId) {
        try {
            const project = await Api.get(`/api/projects/${projectId}`);
            if (!project) return;

            renderProjects([project], detailLayer, { clear: true, highlightId: projectId });

        } catch (err) {
            console.error(err);
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
            // Only show error if it wasn't already handled by the API auth interceptor
            if (!err.message.includes('Auth Error')) {
                notify("Error guardando dibujos", "error");
            }
        }
    }

    return {
        loadProjectDrawings,
        saveCurrentDrawings,
        renderProjects
    };
})();