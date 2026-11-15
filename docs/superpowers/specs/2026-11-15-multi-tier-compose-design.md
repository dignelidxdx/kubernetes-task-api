# Diseño: Compose multi-tier con frontend Linktree

## Intención

Adaptar el proyecto a un despliegue Docker Compose de dos servicios, tomando como referencia el ejemplo multi-tier compartido y agregando una página estática básica tipo Linktree.

## Alcance

- Mantener la API FastAPI existente en `task-api`, publicada en `8000`.
- Agregar un frontend estático servido por Nginx en `frontend`, publicado en `8080`.
- Conectar ambos servicios mediante una red Compose compartida.
- Agregar healthcheck para la API y dependencia del frontend respecto de la API.
- Enlazar desde el frontend a `/docs`, `/health` y `/tasks` usando `localhost:8000`.
- Hacer desde el navegador una petición `fetch` a `/tasks` y mostrar el resultado.
- Permitir CORS únicamente desde `http://localhost:8080`.

## Fuera de alcance

- No agregar base de datos ni persistencia compartida.
- No modificar la lógica de negocio de la API ni los manifiestos Kubernetes existentes.
- No agregar un framework frontend; la página será HTML/CSS estático.

## Enfoques considerados

1. Un único servicio con la API sirviendo también HTML: menos archivos, pero no representa el patrón multi-tier solicitado.
2. **Dos servicios Compose con frontend Nginx estático: recomendado.** Reproduce el ejemplo, mantiene responsabilidades separadas y es simple de ejecutar.
3. Frontend con framework JavaScript: ofrece más posibilidades, pero agrega dependencias y complejidad sin necesidad para una página de enlaces.

## Decisión

Implementar el enfoque 2. La API seguirá almacenando tareas en memoria, porque la persistencia no forma parte de este cambio. Se agregará solo el middleware CORS necesario para que el frontend pueda consultar la API desde el navegador.

