// frontend/js/district_map.js
window.DistrictMap = (function () {
    let map = null;
    let drawingLayer = null;
    let tileLayer = null;
    let districtMaskLayer = null;

    // Guardamos las capas de los bordes blancos para poder limpiarlas
    let activeBorderLayers = [];

    function init() {
        map = L.map("map-detail", {
            center: [-12.0464, -77.0428],
            zoom: 13,
            zoomControl: true
        });

        // Panel especial para la máscara oscura (z-index bajo entre tiles y vectores)
        map.createPane("maskPane");
        map.getPane("maskPane").style.zIndex = 350;
        map.getPane("maskPane").style.pointerEvents = "none";

        setBaseLayer("satellite");
        setupDrawingTools();

        // expose for other code if needed
        window.mapDetail = map;
    }

    function setupDrawingTools() {
        drawingLayer = new L.FeatureGroup();
        map.addLayer(drawingLayer);

        const drawControl = new L.Control.Draw({
            edit: { featureGroup: drawingLayer },
            draw: {
                polygon: true,
                polyline: true,
                rectangle: true,
                circle: true,
                marker: true,
                circlemarker: false
            }
        });

        map.addControl(drawControl);
        map.on(L.Draw.Event.CREATED, e => drawingLayer.addLayer(e.layer));
    }

    function setBaseLayer(style) {
        if (tileLayer) map.removeLayer(tileLayer);

        if (style === "streets") {
            tileLayer = L.tileLayer("https://tile.openstreetmap.org/{z}/{x}/{y}.png", {
                attribution: "© OpenStreetMap contributors",
                maxZoom: 19
            });
        } else {
            tileLayer = L.tileLayer(
                "https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
                {
                    attribution: "Tiles © Esri",
                    maxZoom: 19
                }
            );
        }

        tileLayer.addTo(map);
    }

    // ---------------------------------------------------------
    //  ENFOQUE Y MÁSCARA (Soporte Multiselect)
    // ---------------------------------------------------------
    function focusOnSelectedDistrict() {
        const rawSelection = AppState.selectedDistrict;
        const geo = AppState.districtsGeoJSON;

        // Limpiar capas anteriores
        activeBorderLayers.forEach(l => map.removeLayer(l));
        activeBorderLayers = [];

        if (districtMaskLayer) {
            map.removeLayer(districtMaskLayer);
            districtMaskLayer = null;
        }

        if (!rawSelection || !geo) return;

        // 1. Obtener lista de nombres (maneja "Callao" y "Callao, Lima")
        const districtNames = rawSelection.includes(",")
            ? rawSelection.split(",").map(s => s.trim())
            : [rawSelection];

        // 2. Buscar todos los features correspondientes en el GeoJSON
        const features = geo.features.filter(f =>
            districtNames.includes(f.properties.distrito)
        );

        if (features.length === 0) return;

        // 3. Dibujar bordes blancos para cada distrito encontrado
        const group = new L.FeatureGroup(); // Grupo para calcular el zoom total

        features.forEach(feature => {
            const layer = L.geoJSON(feature, {
                style: {
                    color: "#FFFFFF", // Borde blanco
                    weight: 3,
                    fillOpacity: 0,
                    opacity: 1
                },
                interactive: false // El detalle suele ser para dibujar, no para seleccionar distritos
            }).addTo(map);

            activeBorderLayers.push(layer);
            layer.addTo(group);
        });

        // 4. Aplicar la máscara inversa a TODOS los distritos
        applyMask(features);

        // 5. Ajustar el mapa para ver todos los distritos
        if (group.getLayers().length > 0) {
            map.fitBounds(group.getBounds(), { padding: [50, 50] });
        }
    }

    function applyMask(features) {
        // Coordenadas del "Mundo" (rectángulo gigante)
        // Leaflet usa [Lat, Lng], GeoJSON usa [Lng, Lat]. 
        // L.geoJSON maneja la conversión, pero si dibujamos a mano:
        // coordinates: [ [ [lng, lat] ... outer ring ], [ [lng, lat] ... inner hole ] ]

        const world = [
            [-180, -90],
            [-180, 90],
            [180, 90],
            [180, -90],
            [-180, -90]
        ];

        // Recolectamos TODOS los agujeros (polígonos de los distritos)
        let allHoles = [];

        features.forEach(feature => {
            const coords = feature.geometry.coordinates;

            if (feature.geometry.type === "Polygon") {
                // Un polígono simple: coordinates[0] es el anillo exterior
                allHoles.push(coords[0]);
            }
            else if (feature.geometry.type === "MultiPolygon") {
                // MultiPolígono: coordinates es un array de polígonos
                // Cada polígono tiene [outerRing, hole1, hole2...]
                // Necesitamos el outerRing (index 0) de cada parte del multipolígono
                coords.forEach(polygon => {
                    allHoles.push(polygon[0]);
                });
            }
        });

        // Estructura GeoJSON para Polígono con agujeros:
        // [ [Anillo Exterior (Mundo)], [Agujero 1], [Agujero 2], ... ]
        const maskCoordinates = [world, ...allHoles];

        const maskFeature = {
            type: "Feature",
            geometry: {
                type: "Polygon",
                coordinates: maskCoordinates
            }
        };

        districtMaskLayer = L.geoJSON(maskFeature, {
            pane: "maskPane",
            style: {
                fillColor: "black",
                fillOpacity: 0.7, // Qué tan oscuro es el fondo
                color: "transparent",
                weight: 0,
                stroke: false
            }
        }).addTo(map);
    }

    function getDrawingLayer() {
        return drawingLayer;
    }

    return {
        init,
        setBaseLayer,
        focusOnSelectedDistrict,
        getDrawingLayer
    };
})();