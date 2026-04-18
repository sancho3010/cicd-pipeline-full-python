# CI Pipeline - Calculadora Web

Pipeline de Integración Continua para una aplicación web Python (calculadora) usando GitHub Actions, Docker y herramientas open source.

## Stack

- **Python / Flask** —> aplicación web
- **Pylint / Flake8 / Black** —> calidad y estilo de código
- **pytest / Coverage.py** —> pruebas unitarias y cobertura
- **Selenium** —> pruebas de aceptación
- **SonarCloud** —> análisis estático continuo
- **Docker / Docker Hub** —> empaquetado y publicación
- **GitHub Actions** —> pipeline de CI

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
