# CRUD de médicos y citas

Aplicación web para administrar médicos y citas de una clínica. El proyecto está dividido en un frontend SPA hecho con SvelteKit y Svelte 5, una API REST construida con FastAPI y SQLAlchemy, y una base de datos PostgreSQL 17 ejecutada con Docker Compose.

## Requisitos

- Node.js 20.19 o superior, o 22.12 o superior.
- Python 3.10 o superior.
- Docker Desktop con Docker Compose v2.
- Git.

## Estructura

```text
crud_software/
├── backend/
│   ├── app/
│   │   ├── routers/       # Rutas de médicos y citas
│   │   ├── database.py    # Conexión y sesiones de SQLAlchemy
│   │   ├── main.py        # Aplicación FastAPI y configuración CORS
│   │   ├── models.py      # Modelos Medico y Cita
│   │   └── schemas.py     # Esquemas y validaciones Pydantic
│   ├── seed.py            # Datos de prueba
│   └── requirements.txt
├── frontend/
│   └── src/
│       ├── lib/api.js     # Llamadas HTTP centralizadas
│       └── routes/        # Inicio, médicos y citas
├── docker-compose.yml
└── README.md
```

## Configuración inicial

Desde la raíz del repositorio, copia los archivos de ejemplo. En PowerShell:

```powershell
Copy-Item .env.example .env
Copy-Item backend\.env.example backend\.env
Copy-Item frontend\.env.example frontend\.env
```

La configuración local actual reserva el puerto `5433` para PostgreSQL, porque el `5432` predeterminado puede estar ocupado por otra instalación. Comprueba que `backend/.env` tenga una URL con el puerto `5433`, por ejemplo:

```env
DATABASE_URL=postgresql+psycopg://clinica:clinica123@localhost:5433/clinica
CORS_ORIGINS=http://localhost:5173,http://127.0.0.1:5173
```

El archivo raíz `.env` configura las credenciales que Docker Compose utiliza al inicializar PostgreSQL. `frontend/.env` debe contener:

```env
VITE_API_URL=http://localhost:8000
```

Los archivos `.env` locales no se deben subir a Git. Si modificas `frontend/.env`, reinicia el servidor de desarrollo para que Vite cargue los cambios.

## Ejecutar el proyecto

Se necesitan tres terminales: una para la base de datos, otra para el backend y otra para el frontend.

### 1. Iniciar PostgreSQL

Desde la raíz del repositorio:

```powershell
docker compose up -d
docker compose ps
```

Espera a que el servicio `db` aparezca como `healthy`. Docker publica PostgreSQL en `localhost:5433` y lo conecta al puerto `5432` dentro del contenedor.

### 2. Instalar e iniciar el backend

Desde la carpeta `backend`:

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m uvicorn app.main:app --reload --port 8000
```

Si PowerShell no permite activar el entorno virtual, usa CMD y ejecuta `.venv\Scripts\activate.bat`. También puedes llamar al ejecutable del entorno directamente sin activarlo:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload --port 8000
```

Al iniciar, la API crea las tablas si aún no existen. La documentación interactiva de FastAPI queda disponible en <http://localhost:8000/docs>; la comprobación de salud está en <http://localhost:8000/salud>.

### 3. Instalar e iniciar el frontend

Desde otra terminal, en la carpeta `frontend`:

```powershell
cd frontend
npm install
npm run dev
```

Abre <http://localhost:5173>. El frontend comprueba la conexión con `GET /salud` y permite administrar médicos y citas.

## Datos de prueba

Para cargar médicos y citas de ejemplo, abre una terminal en `backend`, activa su entorno virtual y ejecuta:

```powershell
python seed.py
```

El script puede ejecutarse varias veces; no vuelve a insertar los mismos datos. La información permanece en el volumen de Docker aunque se detengan o recreen los contenedores.

## Funcionalidad

- **Médicos:** listar, crear, editar y eliminar. Cada médico tiene nombre, especialidad y correo único.
- **Citas:** listar, crear, editar y eliminar. Cada cita incluye paciente, médico, fecha y hora, y un motivo opcional.
- Las citas muestran los datos del médico asociado.
- El frontend valida los campos y presenta los errores de validación (`422`), conflictos (`409`) y recursos inexistentes (`404`) devueltos por la API.
- Los datos se vuelven a consultar después de crear, editar o eliminar registros.

### Rutas principales de la API

Las rutas no llevan barra final:

| Método | Ruta | Descripción |
| --- | --- | --- |
| `GET` | `/salud` | Comprueba que la API está activa |
| `GET`, `POST` | `/medicos` | Listar o crear médicos |
| `GET`, `PUT`, `DELETE` | `/medicos/{id}` | Consultar, reemplazar o eliminar un médico |
| `GET`, `POST` | `/citas` | Listar o crear citas |
| `GET`, `PUT`, `DELETE` | `/citas/{id}` | Consultar, reemplazar o eliminar una cita |

Los cuerpos y respuestas usan JSON. Las fechas de cita se envían como texto ISO 8601 local, sin zona horaria, por ejemplo `2026-10-12T09:00:00`. En una actualización `PUT` se envían todos los campos requeridos.

## Comprobaciones del frontend

Desde `frontend`:

```powershell
npm run check
npm run build
```

## Detener servicios y conservar los datos

Desde la raíz del repositorio:

```powershell
docker compose down
```

Este comando elimina el contenedor y conserva el volumen `pgdata`. **No ejecutes `docker compose down -v` salvo que quieras borrar también la base de datos y todos sus datos.**

## Solución de problemas

- **El backend se queda en `Waiting for application startup`:** revisa que Docker esté en ejecución y que `docker compose ps` muestre la base como `healthy`. Confirma que `DATABASE_URL` en `backend/.env` apunte a `localhost:5433`.
- **`connection refused` al conectar con PostgreSQL:** inicia la base con `docker compose up -d` y confirma el puerto configurado.
- **Error de CORS en el navegador:** incluye el origen del frontend (`http://localhost:5173` o `http://127.0.0.1:5173`) en `CORS_ORIGINS` de `backend/.env` y reinicia Uvicorn.
- **El frontend no puede conectar con la API:** confirma que Uvicorn esté en el puerto `8000` y que `VITE_API_URL` sea `http://localhost:8000`. Reinicia Vite si cambiaste el `.env`.
- **El puerto `5433` también está ocupado:** cambia el puerto publicado en `docker-compose.yml` y usa ese mismo puerto en `DATABASE_URL` dentro de `backend/.env`.
