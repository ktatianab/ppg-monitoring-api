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
   git clone <url-del-repositorio>
   cd ppg-api
   ```

2. Create a virtual environment:
   ```bash
   python -m venv .venv
   # En Windows:
   .venv\Scripts\activate
   # En Linux/Mac:
   source .venv/bin/activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requeriment.txt
   ```

4. Create a database named PPG_DB
Update the database URL in DAO/database.py if necessary


5. Run migrations (if available) or create tables manually based on the models in DTO/models.py
Usage

To run the application:

```bash
uvicorn main:app --reload
```

The API will be available at `http://127.0.0.1:8000`

API Documentation

FastAPI provides automatic documentation at:

`Swagger UI`: http://127.0.0.1:8000/docs
`ReDoc`: http://127.0.0.1:8000/redoc

##Project Structure
`main.py`: FastAPI application entry point
`DAO/`: Data access layer
`database.py`: Database configuration
`DTO/`: Data transfer objects
`models.py`: SQLAlchemy models
`ORM/`: Pydantic schemas
`schemas.py`: Schemas for validation and serialization
`routes/`: API routes/endpoints
`alert.py`, `app_user.py`, etc.: Endpoints for each entity

##Main Endpoints

- `/App_users`: User management
- `/countries`: Countries
- `/cities`: Cities
- `/health_records`:  Health records
- `/wearables`: Wearable devices
- `/monitoring_sessions`: Monitoring sessions
- `/measurements`: Measurements
- `/alerts`: Alerts
- `/ppg_samples`: PPG samples

##Contribution

1. Fork the project
2. Create a feature branch (git checkout -b feature/AmazingFeature)
3. Commit your changes (git commit -m 'Add some AmazingFeature')
4. Push to the branch (git push origin feature/AmazingFeature)
5. Open a Pull Request


For questions or support, contact the development team.
