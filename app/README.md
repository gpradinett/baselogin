# 📦 Backend - BaseLogin

This backend is built with FastAPI and provides a solid foundation for user authentication and management. The structure follows modern best practices of Python development, including modular organization, database management, and automated testing. 

### 🚀 Key features 
### ✅ OAuth2-based authentication with JWT (access token) 
### 🔐 Support for superuser and normal user login 
### 📄 API paths organized by modules (/login, /users) 
### 🧪 Testing with pytest and FastAPI's TestClient 
### 🗃️ Database managed with SQLModel and alembic 
### ⚙️ Configuration using environment variables (.env) 
### 🌱 Database initialization script with predefined users 

## 📁 Folder Structure

```
cookiecutter-fastapi-auth/
├── cookiecutter.json                  ✅ Archivo de configuración para la plantilla.
│                                      Define variables como project_name, author, etc.
│
├── {{cookiecutter.project_slug}}/     ✅ Carpeta principal generada con el nombre del proyecto.
│                                      Contiene todo el código fuente del proyecto FastAPI.
│
│   ├── app/                           ✅ Código fuente de la aplicación FastAPI.
│   │   ├── __init__.py                Módulo raíz de la aplicación; permite importar como paquete.
│   │   │
│   │   ├── api/                       ✅ Módulo que agrupa la lógica de enrutamiento de la API.
│   │   │   ├── __init__.py
│   │   │   ├── deps.py                ✅ Dependencias que pueden ser usadas con `Depends()`.
│   │   │   ├── main.py                Punto de montaje para los routers definidos en `routes/`.
│   │   │   └── routes/                ✅ Subcarpeta para dividir endpoints por dominio/funcionalidad.
│   │   │       ├── __init__.py
│   │   │       ├── login.py           Endpoints relacionados al login y autenticación (JWT).
│   │   │       └── users.py           Endpoints CRUD para usuarios.
│   │   │
│   │   ├── core/                      ✅ Configuración central del proyecto.
│   │   │   ├── __init__.py
│   │   │   ├── config.py              Configuración del entorno (pydantic Settings, variables env).
│   │   │   ├── db.py                  Conexión e inicialización de la base de datos (SQLModel).
│   │   │   └── security.py            Lógica de autenticación (JWT, hashing, OAuth).
│   │   │
│   │   ├── crud.py                    ✅ Operaciones de acceso a la base de datos (CRUD).
│   │   │                              en SQLModel/SQLAlchemy.
│   │   │
│   │   ├── models.py                  ✅ Definición de modelos de base de datos y esquemas Pydantic.
│   │   │                              Se usa tanto para DB como para validación de datos.
│   │   │
│   │   ├── main.py                    ✅ Punto de entrada de la aplicación FastAPI (`uvicorn app.main:app`).
│   │   │                              Incluye la inicialización de la app y registro de routers.
│   │   │
│   ├── README.md                      ✅ Documentación básica del proyecto.
│   │   │                              Explica cómo usar, instalar y contribuir al proyecto.
│   │   │
│   └── requirements.txt               ✅ Lista de dependencias necesarias para correr el proyecto.
│                                      Compatible con `pip install -r requirements.txt`.
```

### 📦 Requirements Python 3.12 PostgreSQL Virtualenv o entorno virtual similares 
### 🧪 Run tests
```
pytest
```
