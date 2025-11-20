# 🗺️ Lima Projects Mapping

Una aplicación web interactiva diseñada para visualizar, gestionar y analizar proyectos de infraestructura pública en los distritos de Lima y Callao. Esta herramienta permite a los usuarios monitorear el estado de las obras (activos, completados, archivados) mediante mapas satelitales y herramientas de dibujo.

## 🚀 Características Principales

- **Mapa General Interactivo:** Visualización completa de Lima y Callao con soporte para selección múltiple de distritos.
- **Vista Detallada** Enfoque visual en distritos específicos, oscureciendo el resto del mapa para mayor precisión al editar.
- **Gestión de Proyectos (CRUD):** Creación, edición y eliminación de proyectos con campos detallados y estados personalizables.
- **Herramientas de Dibujo:** Integración con `Leaflet.draw` para trazar polígonos y geometrías sobre el mapa y guardarlos en la base de datos.
- **Estadísticas:** Panel lateral dinámico que muestra estado de proyectos por estado y distrito.
- **Base de Datos en la Nube:** Persistencia de datos segura y escalable utilizando PostgreSQL (Vercel).

## 🛠️ Tecnologías Utilizadas

### Frontend
- **HTML5 / CSS3:** Diseño responsivo con CSS Grid y Flexbox.
- **JavaScript (Vanilla ES6+):** Arquitectura modula (IIFE).
- **Leaflet.js:** Motor de mapas interactivos.
- **Leaflet.Draw:** Librería para herramientas de vectorización.
- **Lucide Icons:** Iconografía moderna

### Backend
- **Python 3.12.10**
- **FastAPI**
- **SQLAlchemy:** ORM para Gestion de Datos
- **Pydantic:** Validación de datos

### Infraestructura
- **Vercel:** Despliegue del Frontend y Serverless Functions.
- **PostgreSQL (Vercel Storage):** Base de datos relacional en la nube.

## ⚙️ Instalación y Configuración Local

Sigue estos pasos para ejecutar el proyecto en tu computadora:

1. **Clonar el repositorio**
   ```bash
   git clone https://github.com/joaquin-villar/lima-proyect-mapping.git
   cd lima-proyect-mapping
   ```

2. **Configurar entorno virtual (Python)**
    ```bash
    python -m venv venv
    # En Windows:
    .\venv\Scripts\activate
    # En Mac/Linux:
    source venv/bin/activate
    ```
3. **Instalar dependencias**
    ```bash
    pip install -r requirements.txt
    ```

4. **Configurar Variables de Entorno**
    ```bash
    POSTGRES_URL="postgresql://usuario:password@host:port/database"
    ```

5. **Ejecutar el servidor**
    ```bash
    python app.py
    ```

## 📂 Estructura del Proyecto
``` bash 
├── backend/           # Lógica del servidor (FastAPI)
│   ├── models.py      # Modelos de Base de Datos (SQLAlchemy)
│   ├── schemas.py     # Esquemas de Validación (Pydantic)
│   ├── main.py        # Configuración principal de la API
│   └── database.py    # Conexión a Postgres
├── frontend/          # Interfaz de Usuario
│   ├── js/            # Módulos JS (UI, Mapas, API, Proyectos, Modal)
│   ├── css/           # Estilos globales
│   └── index.html     # Punto de entrada
├── data/              # GeoJSON estáticos de distritos
├── app.py             # Script de ejecución local
└── requirements.txt   # Dependencias de Python
```

## ✒️ Autor

### Joaquin Villar Urrutia