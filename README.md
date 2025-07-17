Claro, aquí tienes una guía completa para tu equipo de software, detallando la configuración, estructura y las pruebas a desarrollar para el módulo `project_management`.

---

## **Guía de Implementación y Pruebas para el Módulo `project_management` en Odoo 18**

### **Introducción**

Este documento sirve como una guía central para configurar el entorno de desarrollo, entender la arquitectura del módulo `project_management` y definir las tareas de testing. El objetivo es asegurar que todos los miembros del equipo tengan una base común para trabajar y contribuir de manera efectiva.

### **Parte 1: Configuración Inicial del Entorno Odoo con Docker**

Estos pasos asumen que Docker, Docker Compose y el código fuente de Odoo ya están instalados en la máquina del desarrollador.

#### **Paso 1: Levantar los Contenedores**

Asegúrate de que tu archivo docker-compose.yml esté configurado para montar la carpeta addons como un volumen en el contenedor de Odoo. Luego, inicia los servicios:

```powershell
# Inicia los contenedores en segundo plano
docker-compose up -d
```

#### **Paso 2: Crear la Base de Datos**

1.  Abre tu navegador y ve a `http://localhost:8069`.
2.  Verás la pantalla de creación de base de datos de Odoo.
3.  Completa los campos:
    *   **Master Password**: La contraseña maestra definida en tu odoo.conf o docker-compose.yml.
    *   **Database Name**: Elige un nombre (ej. `project_db_dev`).
    *   **Email**: `admin`
    *   **Password**: Una contraseña segura para el usuario administrador.
    *   **Demo data**: Marca esta casilla. Es crucial para tener datos de prueba iniciales.
4.  Haz clic en **Create database**. El proceso tardará unos minutos.

#### **Paso 3: Instalar el Módulo `project_management`**

1.  Una vez que la base de datos esté creada y hayas iniciado sesión, ve al menú principal.
2.  Haz clic en **Apps**.
3.  En la barra de búsqueda, elimina el filtro `Apps` por defecto.
4.  Busca `Project Management`.
5.  Verás nuestro módulo. Haz clic en el botón **Activate** para instalarlo.

### **Parte 2: Estructura del Módulo `project_management`**

Nuestro módulo sigue la estructura estándar de Odoo. Es vital entender el propósito de cada directorio:

*   `models/`: Contiene la lógica de negocio y la definición de los modelos de datos (project.py, task.py, role.py).
*   `views/`: Define la interfaz de usuario a través de archivos XML (project_views.xml, task_views.xml, etc.). Aquí se estructuran los formularios, listas y menús.
*   `security/`: Gestiona los permisos y la seguridad.
    *   project_security.xml: Define los grupos de usuarios (Administrator, Supervisor, Executor) y las reglas de acceso a nivel de registro (por ejemplo, un supervisor solo puede ver sus propios proyectos).
    *   ir.model.access.csv: Controla los permisos de CRUD (Crear, Leer, Escribir, Borrar) para cada grupo en cada modelo.
*   `data/`: Contiene datos iniciales que se cargan al instalar el módulo, como los roles predefinidos (project_data.xml).
*   `tests/`: Alberga los scripts de pruebas automatizadas.
*   __manifest__.py: El "corazón" del módulo. Declara sus metadatos, dependencias (como `auth_password_policy`) y los archivos que deben cargarse.

### **Parte 3: Pruebas Ya Implementadas**

Actualmente, el archivo test_unitarias.py contiene las siguientes pruebas base:

1.  **Pruebas Unitarias (`TestUsuarioUnitario`)**:
    *   Verifica la creación básica de un usuario en el sistema.

2.  **Pruebas de Política de Contraseñas (`TestPasswordPolicy`)**:
    *   Estas son las pruebas más completas que tenemos.
    *   **Objetivo**: Asegurar que el módulo `auth_password_policy` (una de nuestras dependencias) funciona como se espera.
    *   **Cobertura**:
        *   **Longitud Mínima**: Valida que no se puedan crear usuarios con contraseñas más cortas que el mínimo establecido.
        *   **Clases de Caracteres**: Comprueba que las contraseñas contengan la mezcla requerida de mayúsculas, minúsculas, números y símbolos.
        *   **Número de Palabras**: Valida que las contraseñas tipo "passphrase" tengan un mínimo de palabras.
        *   **Combinaciones**: Prueba escenarios donde múltiples políticas están activas simultáneamente.

### **Parte 4: Pruebas a Desarrollar (Funcionales y de Integración)**

El equipo debe enfocarse en desarrollar las siguientes pruebas, creando nuevos archivos o extendiendo el existente.

#### **A. Pruebas Funcionales (Simulación de Casos de Uso)**

El objetivo es validar los flujos de trabajo completos desde la perspectiva del usuario.

*   **Caso de Uso 1: Flujo de Vida de un Proyecto**
    1.  Crear un nuevo proyecto con estado "Draft".
    2.  Verificar que el progreso inicial es 0.
    3.  Hacer clic en el botón "Start Project".
    4.  Confirmar que el estado cambia a "In Progress".
    5.  Hacer clic en el botón "Mark as Completed".
    6.  Confirmar que el estado cambia a "Completed".

*   **Caso de Uso 2: Gestión de Tareas**
    1.  Crear una tarea y asociarla a un proyecto existente.
    2.  Verificar que la tarea se crea en estado "Draft".
    3.  Validar que no se puede establecer una fecha de fin anterior a la de inicio.
    4.  Cambiar el estado de la tarea a "In Progress" y luego a "Completed".

#### **B. Pruebas de Integración (Interacción entre Componentes y Seguridad)**

El objetivo es validar que las diferentes partes del sistema (modelos, reglas de seguridad, lógica de negocio) funcionan correctamente juntas.

*   **Caso de Uso 1: Reglas de Acceso del Supervisor**
    1.  Crear dos supervisores (Supervisor A, Supervisor B).
    2.  Crear un proyecto (Proyecto A) asignado al Supervisor A.
    3.  **Probar**: Iniciar sesión como Supervisor A y verificar que puede ver y editar el Proyecto A.
    4.  **Probar**: Iniciar sesión como Supervisor B y verificar que **NO** puede ver el Proyecto A.

*   **Caso de Uso 2: Reglas de Acceso del Ejecutor**
    1.  Crear un ejecutor (Ejecutor A).
    2.  Crear una tarea (Tarea A) y asignarla al Ejecutor A.
    3.  **Probar**: Iniciar sesión como Ejecutor A y verificar que puede ver y modificar el estado de la Tarea A.
    4.  **Probar**: Iniciar sesión como Ejecutor A y verificar que **NO** puede crear un nuevo proyecto.

*   **Caso de Uso 3: Integración Proyecto-Tarea (Cálculo de Progreso)**
    1.  Crear un proyecto con 4 tareas.
    2.  Verificar que el progreso del proyecto es 0%.
    3.  Marcar 1 tarea como "Completed".
    4.  Verificar que el progreso del proyecto se actualiza automáticamente a 25%.
    5.  Marcar 2 tareas más como "Completed".
    6.  Verificar que el progreso del proyecto se actualiza a 75%.

---
Esta guía debe servir como punto de partida. Fomenten la comunicación y no duden en expandir los casos de prueba si identifican más escenarios críticos. ¡Éxito
