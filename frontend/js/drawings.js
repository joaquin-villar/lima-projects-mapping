// frontend/js/drawings.js
window.Drawings = (function () {

    let selectedLayer = null;

    // Helper para notificaciones (consistente con el resto de la app)
    function notify(message, type = 'success') {
        if (window.ProjectModal && typeof window.ProjectModal.showNotification === 'function') {
            window.ProjectModal.showNotification(message, type);
        } else {
            alert(message);
        }
    }

    function init() {
        window.addEventListener('keydown', handleKeyDown);

        // 🟢 Listener global en los mapas para deseleccionar al hacer clic afuera
        if (window.mapOverview) window.mapOverview.on('click', deselectLayer);
        if (window.mapDetail) window.mapDetail.on('click', deselectLayer);
    }

    function deselectLayer() {
        if (selectedLayer && selectedLayer.getElement) {
            const el = selectedLayer.getElement();
            if (el && el.firstChild) el.firstChild.style.boxShadow = "0 0 4px rgba(0,0,0,0.5)";
        }
        selectedLayer = null;

        const editor = document.getElementById('coordinate-editor');
        if (editor) editor.style.display = 'none';
        console.log("Punto deseleccionado");
    }

    function handleKeyDown(e) {
        if (!selectedLayer || AppState.currentTab !== 'detail') return;
        if (!['ArrowUp', 'ArrowDown', 'ArrowLeft', 'ArrowRight'].includes(e.key)) return;

        let latlng = null;
        if (typeof selectedLayer.getLatLng === 'function') {
            latlng = selectedLayer.getLatLng();
        }

        if (!latlng) return;

        const step = e.shiftKey ? 0.0005 : 0.00005;
        let newLat = latlng.lat;
        let newLng = latlng.lng;

        if (e.key === 'ArrowUp') newLat += step;
        else if (e.key === 'ArrowDown') newLat -= step;
        else if (e.key === 'ArrowLeft') newLng -= step;
        else if (e.key === 'ArrowRight') newLng += step;

        e.preventDefault();
        selectedLayer.setLatLng([newLat, newLng]);
        updateCoordinateEditor(newLat, newLng);

        // Si el layer tiene tooltip, forzar su actualización de posición
        if (selectedLayer.getTooltip()) {
            selectedLayer.setTooltipContent(selectedLayer.getTooltip().getContent());
        }
    }

    function updateCoordinateEditor(lat, lng) {
        const editor = document.getElementById('coordinate-editor');
        const latSpan = document.getElementById('current-lat');
        const lngSpan = document.getElementById('current-lng');

        if (editor) editor.style.display = 'block';
        if (latSpan) latSpan.innerText = lat.toFixed(6);
        if (lngSpan) lngSpan.innerText = lng.toFixed(6);
    }

    function selectLayer(layer) {
        // Limpieza visual previa 
        deselectLayer();

        selectedLayer = layer;

        // Resaltar el seleccionado
        if (selectedLayer && selectedLayer.getElement) {
            const el = selectedLayer.getElement();
            if (el && el.firstChild) el.firstChild.style.boxShadow = "0 0 0 4px #38bdf8";
        }

        if (selectedLayer && typeof selectedLayer.getLatLng === 'function') {
            const ll = selectedLayer.getLatLng();
            updateCoordinateEditor(ll.lat, ll.lng);
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
                            // 🟢 MODO EDICIÓN: Usamos Marker estándar con un DivIcon personalizado.
                            // Leaflet.draw maneja mucho mejor el drag de Markers que de circleMarkers.
                            if (targetLayer instanceof L.FeatureGroup) {
                                return L.marker(latlng, {
                                    icon: L.divIcon({
                                        className: 'custom-div-icon',
                                        html: `<div style="background-color: #22c55e; width: 14px; height: 14px; border-radius: 50%; border: 2px solid white; box-shadow: 0 0 4px rgba(0,0,0,0.5);"></div>`,
                                        iconSize: [14, 14],
                                        iconAnchor: [7, 7]
                                    })
                                });
                            }

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
                        interactive: false, // 🟢 IMPORTANTE: No interceptar clics/drags
                        className: 'custom-tooltip'
                    });

                    // 🟢 MODO EDICIÓN: Si el targetLayer es un FeatureGroup (capa de dibujo), 
                    // extraemos los sub-layers para que Leaflet.draw los reconozca individualmente.
                    if (targetLayer instanceof L.FeatureGroup) {
                        geoLayer.eachLayer(layer => {
                            // Copiar el tooltip a la subcapa si existe
                            if (geoLayer.getTooltip()) {
                                layer.bindTooltip(geoLayer.getTooltip().getContent(), geoLayer.options);
                            }

                            // 🟢 Hacer seleccionable para edición con teclado Y arrastrable con mouse
                            layer.on('click', (e) => {
                                L.DomEvent.stopPropagation(e);
                                selectLayer(layer);

                                // 🟢 Sincronizar con el sidebar (buscamos la tarjeta y hacemos scroll)
                                if (window.Projects && typeof window.Projects.selectProjectById === 'function') {
                                    window.Projects.selectProjectById(p.id, { scroll: true, updateMap: false });
                                }
                            });

                            if (typeof layer.setDraggable === 'function') {
                                layer.dragging.enable();
                            } else if (layer instanceof L.Marker) {
                                layer.options.draggable = true;
                            }

                            // Sincronizar arrastre con el panel de coordenadas
                            layer.on('dragstart', () => selectLayer(layer));
                            layer.on('drag', (e) => {
                                const ll = e.target.getLatLng();
                                updateCoordinateEditor(ll.lat, ll.lng);
                            });

                            layer.addTo(targetLayer);
                        });
                    } else {
                        geoLayer.addTo(targetLayer);
                    }

                    // Si estamos cargando un solo proyecto resaltado, centrar el mapa
                    if (isHighlighted && options.fitBounds !== false) {
                        const map = targetLayer === window.GeneralMap?.getDrawingLayer()
                            ? window.mapOverview
                            : window.mapDetail;
                        if (map) {
                            // Detectar geometría (geo puede ser un Feature o directamente un Geometry)
                            const geometry = geo.geometry || geo;
                            if (geometry.type === "Point") {
                                map.setView([geometry.coordinates[1], geometry.coordinates[0]], 16);
                            } else {
                                const bounds = geoLayer.getBounds();
                                if (bounds && bounds.isValid()) {
                                    map.fitBounds(bounds, { padding: [50, 50] });
                                }
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

            const detailLayer = window.DistrictMap?.getDrawingLayer();
            if (detailLayer) {
                renderProjects([project], detailLayer, { clear: true, highlightId: projectId });
            }

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
            // El batch endpoint REEMPLAZA todos los dibujos del proyecto.
            const payload = {
                drawings: layersGeoJSON.features.map(feature => {
                    // Limpiamos propiedades extras que añade Leaflet al exportar
                    const cleanFeature = {
                        type: "Feature",
                        geometry: feature.geometry,
                        properties: {}
                    };

                    return {
                        geojson: cleanFeature,
                        drawing_type: feature.geometry.type.toLowerCase()
                    };
                })
            };

            await Api.post(`/api/projects/${project.id}/drawings/batch`, payload);

            notify(`Dibujos guardados exitosamente en "${project.name}"`, "success");

            // Opcional: Recargar el proyecto en el estado local si es necesario
            if (window.Projects && typeof window.Projects.loadProjects === 'function') {
                await window.Projects.loadProjects();
            }

        } catch (err) {
            console.error(err);
            if (!err.message.includes('Auth Error')) {
                notify("Error guardando dibujos. Revisa tu conexión o permisos.", "error");
            }
        }
    }

    return {
        init,
        loadProjectDrawings,
        saveCurrentDrawings,
        renderProjects
    };
})();