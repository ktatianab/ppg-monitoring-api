# PPG Monitoring API

## Description

This is a RESTful API built with FastAPI for PPG (Photoplethysmography) monitoring. It allows managing users, health records, wearable devices, monitoring sessions, and more. It uses PostgreSQL as the database and SQLAlchemy as the ORM.

## Features

- Application user management  
- Country and city administration  
- Health records and measurements  
- Support for wearable devices and models  
- Monitoring sessions and PPG samples  
- Alerts and severity levels  
- Computation status  

## Installation

### Prerequisites

- Python 3.8+  
- PostgreSQL  

### Installation Steps

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd ppg-api

   
### Pasos de instalación

1. Clona el repositorio:
   ```bash
   git clone <url-del-repositorio>
   cd ppg-api
   ```

2. Crea un entorno virtual:
   ```bash
   python -m venv .venv
   # En Windows:
   .venv\Scripts\activate
   # En Linux/Mac:
   source .venv/bin/activate
   ```

3. Instala las dependencias:
   ```bash
   pip install -r requeriment.txt
   ```

4. Configura la base de datos PostgreSQL:
   - Crea una base de datos llamada `PPG_DB`
   - Actualiza la URL de la base de datos en `DAO/database.py` si es necesario

5. Ejecuta las migraciones (si las tienes) o crea las tablas manualmente basándote en los modelos en `DTO/models.py`

## Uso

Para ejecutar la aplicación:

```bash
uvicorn main:app --reload
```

La API estará disponible en `http://127.0.0.1:8000`

### Documentación de la API

FastAPI proporciona documentación automática en:
- Swagger UI: `http://127.0.0.1:8000/docs`
- ReDoc: `http://127.0.0.1:8000/redoc`

## Estructura del proyecto

- `main.py`: Punto de entrada de la aplicación FastAPI
- `DAO/`: Capa de acceso a datos
  - `database.py`: Configuración de la base de datos
- `DTO/`: Objetos de transferencia de datos
  - `models.py`: Modelos de SQLAlchemy
- `ORM/`: Esquemas Pydantic
  - `schemas.py`: Esquemas para validación y serialización
- `routes/`: Rutas/endpoints de la API
  - `alert.py`, `app_user.py`, etc.: Endpoints para cada entidad

## Endpoints principales

- `/App_users`: Gestión de usuarios
- `/countries`: Países
- `/cities`: Ciudades
- `/health_records`: Registros de salud
- `/wearables`: Dispositivos wearables
- `/monitoring_sessions`: Sesiones de monitoreo
- `/measurements`: Mediciones
- `/alerts`: Alertas
- `/ppg_samples`: Muestras PPG

## Contribución

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## Licencia

Este proyecto está bajo la Licencia MIT. Ver el archivo `LICENSE` para más detalles.

## Contacto

Para preguntas o soporte, contacta al equipo de desarrollo.
