// frontend/js/general_map.js
window.GeneralMap = (function () {
    let map = null;
    let drawingLayer = null;
    let tileLayer = null;
    const districtLayers = {}; 
    
    const selectedDistricts = new Set();

    const DEFAULT_STYLE = {
        color: "#6B7280",
        weight: 2,
        fillOpacity: 0,
        opacity: 1
    };

    const SELECTED_STYLE = {
        color: "#58a6ff",
        weight: 4,
        fillColor: "#58a6ff",
        fillOpacity: 0.2,
        opacity: 1
    };

    function init(districtsGeoJSON) {
        map = L.map("map-overview", {
            center: [-12.0464, -77.0428],
            zoom: 11,
            zoomControl: true
        });

        setBaseLayer("satellite");
        
        // 🟢 SOLO INICIALIZAMOS LA CAPA (Sin barra de herramientas)
        setupDrawingLayer();
        
        loadDistricts(districtsGeoJSON);

        map.on('click', (e) => {
            // Ya no necesitamos chequear si estamos dibujando porque no hay herramientas
            deselectAll();
        });

        window.mapOverview = map;
    }

    // 🟢 FUNCIÓN MODIFICADA: Solo crea el contenedor para ver dibujos
    function setupDrawingLayer() {
        drawingLayer = new L.FeatureGroup();
        map.addLayer(drawingLayer);
        // AQUÍ QUITAMOS: L.Control.Draw y map.addControl(...)
    }

    function setBaseLayer(style) {
        if (tileLayer) map.removeLayer(tileLayer);

        if (style === "streets") {
            tileLayer = L.tileLayer("https://tile.openstreetmap.org/{z}/{x}/{y}.png", {
                attribution: "© OpenStreetMap contributors", maxZoom: 19
            });
        } else {
            tileLayer = L.tileLayer(
                "https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
                { attribution: "Tiles © Esri", maxZoom: 19 }
            );
        }
        tileLayer.addTo(map);
    }

    function loadDistricts(districtsGeoJSON) {
        districtsGeoJSON.features.forEach(feature => {
            const distrito = feature.properties.distrito;

            const layer = L.geoJSON(feature, {
                style: DEFAULT_STYLE
            });

            layer.bindTooltip(distrito, {
                permanent: false,
                direction: "top",
                className: "custom-tooltip",
                sticky: true,
                opacity: 1
            });

            layer.on({
                click: (e) => {
                    L.DomEvent.stopPropagation(e);
                    toggleDistrict(distrito);
                },
                dblclick: (e) => {
                    L.DomEvent.stopPropagation(e);
                    
                    selectedDistricts.clear();
                    selectedDistricts.add(distrito);

                    updateVisuals();
                    updateGlobalState();
                    
                    if (window.UI) {
                        UI.switchTab("detail");
                        if (window.ProjectModal && window.ProjectModal.showNotification) {
                            ProjectModal.showNotification(`Abriendo ${distrito}`, 'success');
                        }
                    }
                },
                mouseover: e => {
                    if (!selectedDistricts.has(distrito)) {
                        e.target.setStyle({ color: "#FFFFFF", weight: 3 });
                    }
                    map.getContainer().style.cursor = "pointer";
                },
                mouseout: e => {
                    if (!selectedDistricts.has(distrito)) {
                        updateVisuals(); 
                    }
                    map.getContainer().style.cursor = "";
                }
            });

            layer.addTo(map);
            districtLayers[distrito] = layer;
        });
    }

    function toggleDistrict(distrito) {
        if (selectedDistricts.has(distrito)) {
            selectedDistricts.delete(distrito);
        } else {
            selectedDistricts.add(distrito);
        }

        updateVisuals();
        updateGlobalState();
    }

    function deselectAll(updateUI = true) {
        selectedDistricts.clear();
        updateVisuals();
        if(updateUI) updateGlobalState();
    }

    function updateVisuals() {
        Object.entries(districtLayers).forEach(([name, layer]) => {
            if (selectedDistricts.has(name)) {
                layer.setStyle(SELECTED_STYLE);
                layer.bringToFront();
            } else {
                layer.setStyle(DEFAULT_STYLE);
                layer.bringToBack(); 
            }
        });
    }

    function updateGlobalState() {
        const districtsArray = Array.from(selectedDistricts);
        
        if (districtsArray.length === 0) {
            AppState.selectedDistrict = null;
        } else if (districtsArray.length === 1) {
            AppState.selectedDistrict = districtsArray[0];
        } else {
            AppState.selectedDistrict = districtsArray.join(", ");
        }

        if (window.UI) {
            UI.updateSelectedDistrictDisplay();
            
            if (AppState.currentTab === 'detail' && window.DistrictMap) {
                window.DistrictMap.focusOnSelectedDistrict();
            }
            
            if (AppState.currentTab === 'detail' && window.UI && window.UI.showDistrictStats) {
                if (AppState.selectedDistrict) {
                    if (districtsArray.length === 1) {
                        UI.showDistrictStats(AppState.selectedDistrict);
                        window.Projects?.loadProjectsForCurrentDistrict();
                    }
                } else {
                     document.getElementById("district-stats-container").innerHTML = "";
                     document.getElementById("district-projects-list").innerHTML = "";
                }
            }
        }
    }

    function getDrawingLayer() {
        return drawingLayer;
    }

    return {
        init,
        setBaseLayer,
        toggleDistrict, 
        deselectAll,
        getDrawingLayer,
        districtLayers
    };
})();