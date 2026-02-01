# 🗺️ Lima Projects Mapping

Una aplicación web interactiva diseñada para visualizar, gestionar y analizar proyectos de infraestructura pública en los distritos de Lima y Callao. Esta herramienta permite a los usuarios monitorear el estado de las obras (activos, inactivos, completados) mediante mapas satelitales y herramientas de dibujo avanzadas.

## 🚀 Características Principales

- **Mapa General Interactivo:** Visualización completa de Lima y Callao con soporte para selección múltiple de distritos y normalización de nombres.
- **Vista Detallada:** Enfoque visual en distritos específicos con máscara inversa para mayor precisión en la edición de proyectos.
- **Gestión de Proyectos (CRUD):** Creación, edición y eliminación de proyectos con persistencia de datos y estados actualizados.
- **Seguridad y Roles:** Implementación de autenticación basada en **JWT (JSON Web Tokens)** para proteger acciones de edición.
- **Herramientas de Dibujo:** Integración con `Leaflet.draw` para trazar geometrías (líneas, polígonos, puntos) vinculadas directamente a proyectos.
- **Diseño Mobile-First:** Interfaz optimizada para dispositivos móviles con cabecera compacta y tarjetas de alta densidad.
- **Estadísticas Dinámicas:** Panel que muestra el conteo de proyectos por estado en los distritos seleccionados.

## 🛠️ Tecnologías Utilizadas

### Frontend
- **HTML5 / CSS3:** Diseño responsivo con CSS Grid/Flexbox y optimizaciones para móviles.
- **JavaScript (Vanilla ES6+):** Arquitectura modular organizada en módulos (API, Auth, UI, Maps).
- **Leaflet.js & Leaflet.Draw:** Motor de mapas y herramientas de vectorización.
- **Lucide Icons:** Iconografía moderna y escalable.

### Backend
- **Python 3.12**
- **FastAPI:** Framework web asíncrono de alto rendimiento.
- **SQLAlchemy:** ORM para gestión de datos relacionales con soporte para borrado en cascada.
- **PyJWT:** Gestión de seguridad y tokens de acceso.
- **Pydantic:** Validación estricta de esquemas de datos.

### Infraestructura
- **Vercel:** Despliegue del Frontend y Serverless Functions.
- **PostgreSQL (Vercel Storage):** Base de datos relacional en la nube para persistencia en producción.

## ⚙️ Instalación y Configuración Local

Sigue estos pasos para ejecutar el proyecto localmente:

1. **Clonar el repositorio**
   ```bash
   git clone https://github.com/joaquin-villar/lima-projects-mapping.git
   cd lima-projects-mapping
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

4. **Variables de Entorno**
    Crea un archivo `.env` (o configura en tu shell):
    ```bash
    POSTGRES_URL="tu_url_de_postgres"
    SECRET_KEY="tu_clave_secreta_para_jwt"
    ```

5. **Generar Token de Editor (Opcional)**
    ```bash
    python generate_token.py
    ```

6. **Ejecutar el servidor**
    ```bash
    python app.py
    ```

## 📂 Estructura del Proyecto
``` bash 
├── backend/           # Lógica del servidor (FastAPI)
│   ├── routers/       # Endpoints organizados por recurso (Auth, Projects, etc.)
│   ├── models.py      # Definición de tablas y relaciones
│   ├── schemas.py     # Modelos de entrada/salida (Pydantic)
│   └── database.py    # Conexión a Postgres (Local/Producción)
├── frontend/          # Interfaz de Usuario
│   ├── js/            # Lógica cliente (auth.js, api.js, map logic)
│   ├── css/           # Estilos globales y responsive
│   └── index.html     # SPA Entry point
├── data/              # Recursos estáticos (GeoJSON corregidos)
├── app.py             # Entry point para ejecución local
└── generate_token.py  # Utilidad para credenciales de editor
```

## ✒️ Autor

### Joaquin Villar Urrutia