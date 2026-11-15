# Kubernetes Task API

A small FastAPI task API for learning Kubernetes locally. The current version stores tasks in each process's memory. It provides a three-replica Deployment so you can observe Kubernetes replacing a deleted Pod.

## Run locally

Requires Python 3.12 or a compatible Python 3 version.

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements-dev.txt
python -m uvicorn app.main:app --reload
```

Open `http://localhost:8000/docs` to try `GET /health`, `GET /info`, `GET /tasks`, `POST /tasks`, and `DELETE /tasks/{task_id}`. `/health` returns only the service status; `/info` exposes the current Pod hostname for Kubernetes exercises. Run tests with `python -m pytest -q`.

## Docker

```powershell
docker build -t kubernetes-task-api:local .
docker run --rm -p 8000:8000 kubernetes-task-api:local
```

Open `http://localhost:8000/docs`. Stop the container with Ctrl+C.

## Docker Compose multi-tier

The Compose setup runs the FastAPI backend and a static Nginx frontend:

```powershell
docker compose up --build
```

Open the Linktree-style frontend at `http://localhost:8080`. It queries the
backend through `/api/tasks` and displays the default tasks. The
API documentation remains available at `http://localhost:8000/docs`.

Stop the services with:

```powershell
docker compose down
```

## Eliminar el entorno

### Por qué es importante limpiar

Cada `Deployment` crea Pods y cada Pod consume recursos del clúster, como
CPU, memoria, almacenamiento temporal y direcciones de red. Si se dejan
activos Deployments de pruebas o variantes antiguas, pueden ocurrir estos
problemas:

- Consumo innecesario de CPU y memoria.
- Más Pods de los esperados y mayor dificultad para leer el estado real.
- Peticiones distribuidas entre versiones o configuraciones equivocadas.
- Services duplicados que dificultan saber qué endpoint probar.
- Conflictos de puertos, rutas o nombres.
- Resultados engañosos al probar réplicas, balanceo y autorreparación.
- Mayor consumo y costo si el clúster está en un proveedor cloud.

En este proyecto se deben conservar únicamente los recursos del flujo actual:

```text
task-api Deployment        -> backend
task-api Service           -> acceso interno al backend
task-frontend Deployment   -> frontend
task-frontend Service      -> acceso interno al frontend
task-api-ingress y         -> entrada HTTP del backend y frontend
task-frontend-ingress
```

Los Deployments antiguos como `task-api-nodeport`,
`task-api-loadbalancer-v2` y `task-api-clusterip-v2` son variantes didácticas.
Si ya no se están usando, conviene eliminarlos del clúster. Los Pods creados
por un Deployment se eliminan al eliminar el Deployment, por lo que no hace
falta borrarlos uno por uno.

Al terminar una práctica, primero eliminá los recursos de la aplicación:

```powershell
kubectl delete -f k8s/frontend/ --ignore-not-found
kubectl delete -f k8s/ingress.yaml --ignore-not-found
kubectl delete -f k8s/service.yaml --ignore-not-found
kubectl delete -f k8s/deployment.yaml --ignore-not-found
kubectl delete -f k8s/auth-config.yaml --ignore-not-found
kubectl delete secret auth-secret --ignore-not-found
```

Versión directa, cuando sabés que todos los recursos existen:

```powershell
kubectl delete -f k8s/frontend/
kubectl delete -f k8s/ingress.yaml
kubectl delete -f k8s/service.yaml
kubectl delete -f k8s/deployment.yaml
kubectl delete -f k8s/auth-config.yaml
minikube stop
```

Si también usaste Docker Compose, asegurate de detenerlo:

```powershell
docker compose down
```

Para conservar el clúster de Minikube pero liberar sus recursos:

```powershell
minikube stop
```

Para eliminar completamente el clúster y sus imágenes locales de Minikube:

```powershell
minikube delete
```

Usá `minikube delete` solo cuando quieras empezar desde cero. No es necesario
ejecutarlo después de cada práctica.

## Kubernetes con Minikube

Kubernetes reemplaza la ejecución de Compose y administra los Pods, réplicas,
Services, healthchecks e Ingress. Requiere Docker, Minikube y `kubectl`.

### 1. Iniciar Minikube

Si Compose está ejecutándose, detenelo primero para liberar los puertos:

```powershell
docker compose down
minikube start --driver=docker
minikube status
kubectl get nodes
```

### 2. Habilitar Ingress

```powershell
minikube addons enable ingress
kubectl get pods -n ingress-nginx
```

### 3. Construir las imágenes

```powershell
docker build -t kubernetes-task-api:local .
docker build -t kubernetes-task-frontend:local ./frontend
```

### 4. Cargar las imágenes en Minikube

Los manifiestos usan `imagePullPolicy: Never`, por lo que las imágenes deben
existir dentro del entorno de Minikube:

```powershell
minikube image load kubernetes-task-api:local
minikube image load kubernetes-task-frontend:local
```

### Recargar una imagen después de modificar el código

Cuando cambies el backend o el frontend, reconstruí la imagen y volvela a
cargar en Minikube. Después reiniciá el Deployment correspondiente:

Backend:

```powershell
docker build -t kubernetes-task-api:local .
minikube image load kubernetes-task-api:local
kubectl rollout restart deployment/task-api
kubectl rollout status deployment/task-api
```

Frontend:

```powershell
docker build -t kubernetes-task-frontend:local ./frontend
minikube image load kubernetes-task-frontend:local
kubectl rollout restart deployment/task-frontend
kubectl rollout status deployment/task-frontend
```

Verificá los Pods después de la actualización:

```powershell
kubectl get pods
```

Esto es necesario porque `imagePullPolicy: Never` usa la imagen local de
Minikube y no descarga automáticamente una versión nueva desde Docker.

### 5. Crear el Secret requerido por el backend

Comprobar si ya existe:

```powershell
kubectl get secret auth-secret
```

Si no existe, crearlo para el entorno local:

```powershell
kubectl create secret generic auth-secret `
  --from-literal=AUTH_TOKEN=local-dev-token
```

### 6. Aplicar los manifiestos

Aplicar solo los manifiestos principales. Las variantes didácticas de
`ClusterIP`, `NodePort` y `LoadBalancer` quedaron agrupadas en
`k8s/practice/` y no se deben aplicar junto con el backend principal.

```powershell
kubectl apply -f k8s/auth-config.yaml
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml
kubectl apply -f k8s/frontend/
kubectl apply -f k8s/ingress.yaml
```

### 7. Verificar los recursos

```powershell
kubectl get deployments
kubectl get pods
kubectl get services
kubectl get ingress
kubectl rollout status deployment/task-api
kubectl rollout status deployment/task-frontend
```

Esperá 3 réplicas listas para `task-api` y 2 para `task-frontend`.

### 8. Probar cada Service con Minikube

Estos comandos exponen temporalmente cada Service por separado y devuelven una
URL local:

```powershell
minikube service task-api --url
minikube service task-frontend --url
```

El backend se puede probar con la URL resultante:

```text
<URL_BACKEND>/health
<URL_BACKEND>/docs
<URL_BACKEND>/tasks
```

`minikube service task-frontend --url` sirve para comprobar que el frontend
está vivo. Para que el frontend consulte al backend mediante `/api/tasks`, se
debe usar el Ingress de la sección siguiente.

### 9. Probar frontend y backend juntos mediante Ingress

En otra terminal, ejecutar y dejar activo:

```powershell
minikube tunnel
```

Agregar como administrador esta línea al archivo
`C:\Windows\System32\drivers\etc\hosts`:

```text
127.0.0.1 task-api.local
```

La aplicación queda disponible en:

```text
http://task-api.local/
http://task-api.local/api/tasks
http://task-api.local/api/docs
http://task-api.local/api/health
```

El backend recibe `ROOT_PATH=/api` mediante el ConfigMap cuando corre detrás
del Ingress. Esto permite que Swagger UI busque correctamente el esquema en
`/api/openapi.json` en lugar de consultar `/openapi.json` en el frontend.

El enrutamiento es:

```text
/          -> task-frontend Service -> frontend Pods
/api/...   -> task-api Service      -> backend Pods
```

### Actualizar y volver a levantar el entorno

Después de modificar el backend, el frontend o el Ingress, ejecutá esta
secuencia completa:

```powershell
docker build -t kubernetes-task-api:local .
docker build -t kubernetes-task-frontend:local ./frontend

minikube image load kubernetes-task-api:local
minikube image load kubernetes-task-frontend:local

kubectl apply -f k8s/auth-config.yaml
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml
kubectl apply -f k8s/frontend/

kubectl delete ingress example-ingress --ignore-not-found
kubectl apply -f k8s/ingress.yaml

kubectl rollout restart deployment/task-api
kubectl rollout restart deployment/task-frontend
kubectl rollout status deployment/task-api
kubectl rollout status deployment/task-frontend
```

En otra terminal, dejá activo el túnel:

```powershell
minikube tunnel
```

Luego recargá el navegador con `Ctrl + F5` y verificá en DevTools → Network:

```text
app.js     200
api/tasks  200
```

## Formas de exponer los Services

Hay dos alternativas para exponer los servicios en Minikube. No es necesario
usar ambas al mismo tiempo.

### Camino A: ClusterIP + Ingress — recomendado

Los Services permanecen internos:

```yaml
type: ClusterIP
```

El acceso externo se concentra en el Ingress:

```powershell
minikube addons enable ingress
minikube tunnel
kubectl apply -f k8s/ingress.yaml
```

Accesos:

```text
http://task-api.local/          -> frontend
http://task-api.local/api/tasks -> backend
http://task-api.local/api/docs  -> backend
```

Este camino es el recomendado porque ofrece una única entrada HTTP y permite
enrutar frontend y backend por host y path.

### Camino B: LoadBalancer — exposición directa

Para probar un Service sin Ingress, cambiar el tipo del Service a:

```yaml
type: LoadBalancer
```

Ejemplo para el backend:

```yaml
apiVersion: v1
kind: Service
metadata:
  name: task-api
spec:
  selector:
    app: task-api
  ports:
    - protocol: TCP
      port: 8000
      targetPort: 8000
  type: LoadBalancer
```

Ejemplo para el frontend:

```yaml
apiVersion: v1
kind: Service
metadata:
  name: task-frontend
spec:
  selector:
    app: task-frontend
  ports:
    - protocol: TCP
      port: 80
      targetPort: 80
  type: LoadBalancer
```

Aplicar el cambio sobre los Services existentes y crear la IP externa local:

```powershell
kubectl patch service task-api -p '{"spec":{"type":"LoadBalancer"}}'
kubectl patch service task-frontend -p '{"spec":{"type":"LoadBalancer"}}'
minikube tunnel
kubectl get services
```

También se puede obtener una URL temporal directamente con:

```powershell
minikube service task-api --url
minikube service task-frontend --url
```

En este camino se prueban los servicios por separado. El frontend no usará
automáticamente `/api/tasks` a través de un LoadBalancer independiente; para
ese enrutamiento conjunto se debe usar el Camino A con Ingress.

### 10. Observar la autorreparación

To observe reconciliation, copy an actual Pod name from `kubectl get pods -l app=task-api`, then run:

```powershell
kubectl delete pod POD_NAME
kubectl get pods -l app=task-api -w
```

The ReplicaSet creates a replacement to return to three Pods. `DESIRED` is the requested count, `CURRENT` is how many Pods the ReplicaSet has created, and `READY` is how many are ready to serve.

**Memory limitation:** each replica owns its own task list. Requests routed to different Pods can show different tasks; deleting a Pod loses its tasks. Use the three-replica setup to study reconciliation and `/health`. For consistent task operations during this first version, run locally with Uvicorn or Docker, or temporarily scale the Deployment to one replica:

```powershell
kubectl scale deployment/task-api --replicas=1
```

Restore the exercise with `kubectl scale deployment/task-api --replicas=3`. Shared persistence is planned for Version 6.

The complete progression from Version 1 to Version 8 is in [the project specification](docs/specs/2026-11-14-kubernetes-task-api.md).
