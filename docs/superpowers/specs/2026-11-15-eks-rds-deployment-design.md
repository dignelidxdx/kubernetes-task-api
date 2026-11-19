# Diseño: despliegue EKS con Amazon RDS

## Objetivo

Pasar la aplicación de tareas desde almacenamiento en memoria a PostgreSQL administrado por Amazon RDS y desplegar backend y frontend en EKS.

## Alcance

- Reemplazar el almacenamiento en memoria del backend por PostgreSQL.
- Crear la base de datos PostgreSQL en Amazon RDS.
- Mantener las credenciales fuera de Git mediante un Kubernetes Secret.
- Agregar un Job `db-init` para crear el esquema de `tasks` y cargar los datos iniciales.
- Agregar probes, requests/limits y HPA para backend y frontend cuando el clúster tenga Metrics Server.
- Usar imágenes versionadas publicadas en Amazon ECR.
- Mantener Services internos para backend y frontend durante la primera iteración.

## Fuera de alcance

- PostgreSQL dentro de EKS con StatefulSet o PVC.
- Ingress y dominio público en esta iteración.
- Backups, réplicas Multi-AZ y alta disponibilidad de RDS.
- Credenciales reales dentro del repositorio.

## Enfoques considerados

### PostgreSQL dentro de EKS

Usaría PVC, StatefulSet y un Job de inicialización. Es útil para practicar almacenamiento, pero deja backups, actualizaciones y recuperación bajo responsabilidad del clúster.

### Amazon RDS PostgreSQL — elegido

RDS administra el motor, almacenamiento y mantenimiento. EKS solo consume la base mediante una cadena de conexión almacenada en un Secret. Es la opción más adecuada para la aplicación aunque añade configuración de red y costo de AWS.

## Arquitectura elegida

```text
Frontend Pod → frontend Service
Backend Pod  → task-api Service → Amazon RDS PostgreSQL
                                  ↑
                         db-init Job
```

La conexión se proporcionará mediante `DATABASE_URL` desde el Secret `task-api-db`. El Job `db-init` será idempotente y creará la tabla de tareas sin duplicar datos iniciales.

## Recursos previstos

```text
ECR repositories
RDS PostgreSQL instance
Kubernetes Secret: task-api-db
Kubernetes Job: db-init
Backend Deployment + Service + HPA
Frontend Deployment + Service + HPA
ConfigMap del backend
```

## Organización de manifiestos

El flujo vigente para AWS quedará separado de los ejercicios anteriores:

```text
k8s/eks/       configuración de EKS y recursos específicos de AWS
k8s/           manifiestos activos de la aplicación
k8s/practice/  variantes de Minikube, NodePort, LoadBalancer e Ingress local
```

Los manifiestos que ya no formen parte del flujo EKS/RDS se conservarán bajo `k8s/practice/` como material educativo. Las instrucciones principales solo aplicarán los recursos vigentes para evitar duplicados o configuraciones de Minikube en AWS.

## Decisiones pendientes antes de implementar

- Clase y tamaño de RDS para aprendizaje.
- Si el backend y frontend usarán `ClusterIP` o Services `LoadBalancer` sin Ingress.
- Método de creación del esquema: `init.sql` ejecutado por el Job mediante una imagen con cliente PostgreSQL, o inicialización desde el backend.

