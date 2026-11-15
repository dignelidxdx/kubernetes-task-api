# Multi-tier Compose Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Adaptar el proyecto a Docker Compose con una API FastAPI y un frontend estático tipo Linktree servido por Nginx.

**Architecture:** `task-api` construirá la imagen Python existente y expondrá `8000:8000`. `frontend` construirá una imagen Nginx desde una carpeta estática y expondrá `8080:80`; ambos servicios compartirán una red Compose.

**Tech Stack:** Docker Compose, Docker, Python 3.12, FastAPI, Uvicorn, Nginx, HTML y CSS.

**Spec:** `docs/superpowers/specs/2026-11-15-multi-tier-compose-design.md`

## Global Constraints

- No modificar la lógica de negocio de la API.
- El frontend debe consultar `/tasks` al cargar y poder actualizar el resultado.
- CORS debe permitir únicamente `http://localhost:8080`.
- No modificar los manifiestos Kubernetes existentes.
- No agregar base de datos ni persistencia compartida.
- El frontend debe ser HTML/CSS estático, sin framework JavaScript.
- Los enlaces del frontend deben usar `localhost:8000` para funcionar desde el navegador del usuario.

## Review Focus

- La API debe ser alcanzable desde el host en `http://localhost:8000/health`.
- La página debe ser alcanzable desde el host en `http://localhost:8080`.
- El contenedor frontend debe resolver la red compartida y arrancar después de que la API esté saludable.
- Los enlaces a `/docs`, `/health` y `/tasks` deben apuntar al puerto publicado de la API.
- La petición del navegador a `/tasks` debe mostrar el resultado o un mensaje de error legible.
- La configuración debe funcionar desde la raíz del repositorio con `docker compose config`.

### Task 1: Compose multi-tier

**Files:**
- Create: `docker-compose.yml`

**Interfaces:**
- Produces servicios Compose llamados `task-api` y `frontend`.

- [ ] **Step 1: Definir el servicio `task-api`**

Usar el contexto raíz y el `Dockerfile` existente; publicar `8000:8000`; agregar healthcheck contra `http://localhost:8000/health`.

- [ ] **Step 2: Definir el servicio `frontend`**

Usar `./frontend` como contexto; publicar `8080:80`; declarar dependencia saludable de `task-api`.

- [ ] **Step 3: Definir la red compartida**

Asignar ambos servicios a una red llamada `task-network`.

- [ ] **Step 4: Validar la sintaxis**

Run: `docker compose config`

Expected: configuración válida sin errores.

### Task 2: Frontend Linktree estático

**Files:**
- Create: `frontend/Dockerfile`
- Create: `frontend/index.html`
- Create: `frontend/styles.css`
- Create: `frontend/app.js`

**Interfaces:**
- Produces a static page served at `http://localhost:8080`.

- [ ] **Step 1: Crear el Dockerfile de Nginx**

Usar una imagen oficial de Nginx y copiar `index.html` y `styles.css` a `/usr/share/nginx/html`.

- [ ] **Step 2: Crear la página HTML**

Incluir identidad de Kubernetes Task API, una descripción breve, enlaces a `/docs`, `/health` y `/tasks` usando `http://localhost:8000`, un área para el estado de la API y una lista de tareas.

- [ ] **Step 3: Crear estilos responsive**

Diseñar una tarjeta centrada, botones de enlace visibles, contraste legible y adaptación básica a pantallas pequeñas.

- [ ] **Step 4: Verificar los archivos frontend**

Confirmar que el Dockerfile copia los archivos existentes, que los tres enlaces contienen el puerto `8000` y que la página carga `app.js`.

- [ ] **Step 5: Implementar la petición al backend**

En `frontend/app.js`, consultar `http://localhost:8000/tasks` al cargar y al pulsar actualizar; mostrar las tareas en la página y un mensaje claro si la petición falla.

### Task 3: Acceso cross-origin mínimo

**Files:**
- Modify: `app/main.py`

- [ ] **Step 1: Agregar middleware CORS**

Configurar `CORSMiddleware` con `allow_origins=["http://localhost:8080"]` y permitir los métodos y headers necesarios para la consulta GET.

- [ ] **Step 2: Verificar el origen permitido**

Confirmar que la API responde con el header CORS para `http://localhost:8080` y no habilita un comodín global.

### Task 4: Verificación integrada

**Files:**
- Modify: `README.md`

- [ ] **Step 1: Construir y levantar los servicios**

Run: `docker compose up --build -d`

Expected: `task-api` y `frontend` quedan en ejecución.

- [ ] **Step 2: Verificar endpoints**

Run: `Invoke-WebRequest http://localhost:8000/health` y `Invoke-WebRequest http://localhost:8080`

Expected: la API responde correctamente y el frontend entrega HTML.

- [ ] **Step 3: Documentar el uso**

Agregar al README los comandos `docker compose up --build` y las URLs `http://localhost:8080` y `http://localhost:8000/docs`.

- [ ] **Step 4: Detener el entorno**

Run: `docker compose down`

Expected: los servicios del Compose se detienen y eliminan sin modificar imágenes ni archivos del proyecto.

