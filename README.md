# CI Pipeline | Calculadora Web

Pipeline de Integración Continua para una aplicación web Python (calculadora) usando GitHub Actions, Docker y herramientas open source.

## Stack

- **Python / Flask** —> aplicación web
- **Pylint / Flake8 / Black** —> calidad y estilo de código
- **pytest / Coverage.py** —> pruebas unitarias y cobertura
- **Selenium** —> pruebas de aceptación
- **SonarCloud** —> análisis estático continuo
- **Docker / Docker Hub** —> empaquetado y publicación
- **GitHub Actions** —> pipeline de CI
- **Terraform / AWS ECS / AWS ALB** —> infraestructura como código y despliegue en la nube
- **AWS S3** —> backend remoto para el estado de Terraform

---

### 1. ¿Qué ventajas le proporciona a un proyecto el uso de un pipeline de CI?

- Automatización del proceso de validación. Cada push dispara automáticamente linting, test y análisis
de calidad.

- Detección temprana de errores (bugs). Los problemas se detectan cuando se suben cambios al repo, y no
correr el riesgo de subir y no revisar.

- Entrega consistente. Las validaciones nos ayudan a garantizar que los cambios hechos no se romperán
en producción.

### 2. ¿Cuál es la diferencia principal entre una prueba unitaria y una prueba de aceptación?

Las pruebas unitarias verifican funciones o clases de forma aislada, sin levantar un servidor ni un navegador. Por ejemplo, en este proyecto desde `test_calculadora.py` probamos que `sumar(2, 3)` retorne `5` directamente, sin pasar por Flask.

Las pruebas de aceptación simulan la interacción real de un usuario con la aplicación. Por ejemplo, `test_acceptance_app.py` abrimos un navegador con Selenium, navegamos a `http://localhost:5000`, llenamos el formulario y verificamos que el resultado aparezca en pantalla. Esas pruebas requirieron que la app estuviera corriendo.

### 3. Describe brevemente qué hace cada step principal del workflow de GitHub Actions

1. **Checkout**: clona el repositorio en el runner de GitHub Actions para que los pasos siguientes tengan acceso al código.
2. **Set up Python**: instala la versión de Python especificada en el runner.
3. **Install dependencies**: instala las librerías del proyecto definidas en `requirements.txt`.
4. **Run Black**: verifica que el código cumple con el formato estándar de Black. Si hay diferencias, el paso falla.
5. **Run Pylint**: analiza el código en busca de errores, code smells y problemas de estilo. Genera `pylint-report.txt` para SonarCloud.
6. **Run Flake8**: analiza el código según PEP8 y detecta errores lógicos. Genera `flake8-report.txt` para SonarCloud.
7. **Run Unit Tests**: corre las pruebas unitarias con pytest, mide la cobertura y genera `coverage.xml` para SonarCloud.
8. **Run Acceptance Tests**: levanta la app con Gunicorn en el puerto 8000 y corre las pruebas de aceptación con Selenium.
9. **Upload Test Reports**: sube los reportes HTML de pruebas y cobertura como artefactos descargables en GitHub Actions.
10. **SonarCloud Scan**: envía el código y los reportes a SonarCloud para análisis estático y valida el Quality Gate.
11. **Set up QEMU**: capa de emulación que permite construir las imágenes Docker para múltiples arquitecturas (amd64, arm64) desde un solo runner.
12. **Set up Docker Buildx**: configura el constructor avanzado de Docker con soporte para múltiples plataformas y caché.
13. **Login to Docker Hub**: se autentica en Docker Hub usando las variables y secretos que configuramos en GitHub.
14. **Build and push Docker image**: construye la imagen Docker y la publica en Docker Hub con dos tags: `latest` y el SHA del commit.


### 4. ¿Qué problemas o dificultades encontraste al implementar este taller?

Validar los quality gate de Sonar cloud, no lo había usado antes.

### 5. ¿Qué ventajas ofrece empaquetar la aplicación en una imagen Docker al final del pipeline?

La imagen garantiza que el entorno de ejecución sea idéntico para cada ambiente como desarrollo, qa y producción; no solo en mi máquina local. Al publicarla en Docker Hub al final del pipeline, solo aquellas versiones que pasaron todas las validaciones (linting, tests, quality gate) quedan disponibles para despliegue. Además, la imagen puede correr en cualquier plataforma que soporte contenedores con configuración adicional o mínima.

### Estudiantes

- Santiago Rozo
- Isis Amaya
- Santiago Higuita
- Samuel Oviedo

---

## Entregable 3 — Despliegue Continuo con AWS ECS y Terraform

### URLs de los entornos desplegados

```
Staging ALB URL:    http://calculadora-staging-alb-1808122732.us-east-1.elb.amazonaws.com/
Production ALB URL: http://calculadora-production-alb-946781434.us-east-1.elb.amazonaws.com/
```

---

### 1. Explica el flujo de trabajo completo implementado con Terraform

Cada `push` a `main` dispara el pipeline `ci-cd.yml` que ejecuta 7 jobs en secuencia:

1. **`build-test-publish`**: corre linters (Black, Pylint, Flake8), pruebas unitarias con cobertura, análisis de SonarCloud, y construye y publica la imagen Docker en Docker Hub con dos tags: `latest` y el SHA del commit. Finalmente, se expone el nombre del repo y el SHA como salidas para los jobs siguientes.

2. **`deploy-tf-staging`**: configura las credenciales de AWS, crea el bucket de S3 de estado si este no existe, inicializa Terraform apuntando a `staging/terraform.tfstate` en S3, y corre `terraform apply` para crear o actualizar (idempotente) toda la infraestructura de Staging (ECS Cluster, ALB, Target Group, Security Groups, Task Definition, Service). Finalmente, expone la URL del ALB de Staging.

3. **`update-service-staging`**: forza un nuevo despliegue en ECS con `aws ecs update-service --force-new-deployment` y espera a que el servicio se estabilice con la nueva imagen.

4. **`test-staging`**: instala las dependencias, espera 30 segundos para que el ALB registre los targets, y corre las pruebas de aceptación con Selenium contra la URL real del ALB de Staging. Por último, valida el flujo funcional completo de la calculadora.

5. **`deploy-tf-prod`**: igual a lo se hace en staging pero apuntando a `production/terraform.tfstate`. Solo corre si las pruebas de Staging pasaron de manera exitosa.

6. **`update-service-prod`**: forza el despliegue en ECS de Producción y espera estabilización (igual al update de staging).

7. **`smoke-test-prod`**: corre pruebas de humo contra el ALB de Producción, donde verifica que la página carga y el título contiene "Calculadora".

El artefacto que se mueve a través del pipeline es la **imagen Docker** identificada por el SHA del commit, garantizando que la misma imagen que pasó CI se despliega en Staging y Producción.

---

### 2. Ventajas y desventajas de Terraform vs despliegue manual

**Ventajas:**
- **Reproducibilidad**: La misma IaC despliega infraestructura idéntica en staging y producción sin errores humanos.

- **Versionado**: los archivos `.tf` viven en Git, lo que permite revisar el historial de cambios en la infraestructura.

- **Automatización**: el pipeline crea y actualiza la infraestructura sin intervención manual.

- **Declarativo**: describes el estado deseado y Terraform se encarga de calcular los cambios necesarios.

- **Idempotencia**: Si la infraestructura ya existe y no cambió nada en los .tf, Terraform no la duplica; solo actualiza lo que cambió o se agregó nuevo.


**Desventajas:**

- **Curva de aprendizaje**: HCL tiene su propia sintaxis y conceptos (providers, state, workspaces, etc.) que toman tiempo aprender. La IA puede acelerar el proceso, pero es necesario entender a nivel de componentes cómo estos operan y se relacionan, y conocer y aplicar las buenas prácticas de Terraform.

- **Estado frágil**: el archivo `terraform.tfstate` debe mantenerse sincronizado. Si se corrompe o se pierde, Terraform pierde el control de los recursos existentes. He ahí la importancia de usar un backend como s3 para restaurar la última versión.

- **Depuración compleja**: cuando algo falla en `terraform apply`, los mensajes de error pueden ser difíciles de interpretar.

Definir la infraestructura en Terraform nos resultó intuitivo una vez entendida la estructura de bloques `resource`, `variable` y `output`; lo asociamos a POO. La separación entre declaración de variables y su uso hace que el código sea limpio y reutilizable.

---

### 3. Ventajas y desventajas de introducir un entorno de Staging

**Ventajas:**
- Permite detectar errores de integración o configuración en un entorno real antes de afectar/tocar producción.

- Las pruebas de aceptación corren contra infraestructura real (ALB, ECS, red), no contra un servidor local.

- Reduce el riesgo de despliegues fallidos en producción.

**Desventajas:**
- Aumenta el tiempo total del pipeline (15-20 minutos vs 5 minutos sin staging).

- Incrementa el costo de infraestructura al mantener dos entornos activos simultáneamente.

- Requiere mantener la paridad entre staging y producción para que las pruebas sean representativas.

Hay claramente un trade-off entre velocidad vs seguridad: Staging agrega tiempo pero aumenta significativamente la confianza y la robustez en cada despliegue a producción.

---

### 4. Diferencia entre pruebas en Staging y Producción

**Staging (`test-staging`)**: Se hicieron pruebas de **aceptación** completas con Selenium. Se simuló el flujo real de un usuario: abrir el navegador, navegar a la app, ingresar números, seleccionar operaciones y verificar resultados. Con esto, se cubrió todos los casos funcionales de la calculadora. Estas pruebas son más lentas y exhaustivas.

**Producción (`smoke-test-prod`)**: Se hicieron pruebas de **humo** mínimas. Aquí solo se verificó que la página cargara correctamente y que el título sea igual a "Calculadora". En estas pruebas no se prueban funcionalidad completa, sino que buscan ser rápidas y que no estresen el entorno productivo.

La diferencia es intencional, pues en staging podemos ser agresivos con las pruebas porque es un entorno de validación. Y una vez validamos, entonces en producción solo confirmamos que el despliegue fue exitoso y la app está viva.

---

### 5. ¿Qué le falta al pipeline?

**1. Rollback automático**: si las pruebas de humo en producción fallan, el pipeline debería ser capaz de revertir automáticamente al despliegue anterior. No obstante, actualmente el pipeline si falla, quedaría una versión rota en producción. Una opción para soportar el rollback, podría ser guardar el ARN de la task definition anterior (del último despliegue exitoso) y ejecutar `aws ecs update-service --task-definition <arn-anterior>` en caso de que haya un fallo.

**2. Monitoreo y alertas post-despliegue**: el pipeline termina cuando las pruebas de humo pasan, pero no hay observabilidad continua. En producción real se necesitan métricas (latencia, tasa de errores, uso de CPU, etc) y alertas automáticas con CloudWatch, por ejemplo. Si la app empieza a fallar 10 minutos después del despliegue, con el pipeline actual, nadie se enteraría hasta que un usuario reporte el problema.

**3. Pruebas de seguridad (SAST/DAST)**: el pipeline actualmente tiene análisis estático con SonarCloud, pero no tiene aún pruebas de seguridad dinámicas (DAST) que ataquen la app en ejecución para tratar de detectar vulnerabilidades como XSS, inyección SQL o CSRF mal configurado. Herramientas mencionadas en clase como OWASP ZAP podrían integrarse en el job de staging para escanear la app contra el ALB antes de pasar a producción.

---

### 6. Experiencia implementando las nuevas funcionalidades

Implementar las dos funciones nuevas (potencia y módulo) fue directo gracias al pipeline de CI/CD existente. El flujo fue básicamente emular lo que ya había con las funciones iniciales: escribir la función en `calculadora.py`, agregar los tests unitarios y de aceptación, hacer push y dejar que el pipeline validara todo automáticamente de nuevo.

Lo más útil del CI/CD fue la confianza al hacer cambios, pues saber que si el pipeline pasa verde, la nueva funcionalidad está correctamente integrada y desplegada en ambos entornos sin intervención manual, además de que todas las validaciones y el análisis con Sonar correrán de nuevo para identificar alguna brecha, sin que haya que volver a realizar la configuración inicial que se hizo.

Lo menos útil fue el tiempo de espera, pues cada iteración toma 15-20 minutos, lo que hace lento el ciclo de corrección si algo falla en los jobs de CD. No obstante, creo que manualmente sería mucho más lento y, sobre todo, más riesgoso.
