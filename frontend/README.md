# Frontend de la clínica

Aplicación SPA creada con SvelteKit, Svelte 5 y JavaScript. La interfaz consume la API de FastAPI para administrar médicos y citas.

## Configuración

Desde `frontend/`, copia `.env.example` a `.env` y confirma que la URL de la API sea la correcta:

```env
VITE_API_URL=http://localhost:8000
```

Reinicia el servidor de desarrollo si cambias el archivo `.env`.

## Desarrollo

```sh
npm install
npm run dev
```

Abre <http://localhost:5173>. El backend debe estar disponible en el puerto 8000. La página de inicio verifica `GET /salud`; las pantallas `/medicos` y `/citas` muestran un mensaje recuperable si la API todavía no está disponible.

## Comprobaciones

```sh
npm run check
npm run build
```

Las llamadas HTTP están centralizadas en `src/lib/api.js`. Se usan las rutas sin barra final del contrato: `/medicos`, `/medicos/{id}`, `/citas` y `/citas/{id}`. El formulario de edición envía todos los campos requeridos por `PUT`; las fechas de cita se envían como texto ISO 8601 local sin zona horaria.
