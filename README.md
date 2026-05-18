# API para gestión de usuarios - IndoorPilot

## Manual de instalación

### Requisitos previos

- Python 3.8 o superior
- PostgreSQL (o tu base de datos preferida)
- pip (gestor de paquetes de Python)

### Instalación Paso a Paso

#### 1. Clonar el repositorio

```bash
git clone <url-del-repositorio>
cd <nombre-del-proyecto>
```

#### 2. Crear y activar entorno virtual

```bash
python -m venv venv
venv\Scripts\activate
```

#### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

#### 4. Configurar variables de entorno

Crea un archivo ``.env`` en la raíz del proyecto.

```bash
DATABASE_URL=postgresql://usuario:contraseña@localhost:5432/nombre_bd
JWT_SECRET=tu_clave_secreta_muy_segura
```

Notas:

- Cambia usuario, contraseña y nombre_bd con tus credenciales de PostgreSQL.

- JWT_SECRET debe ser una cadena larga y aleatoria.
- Se recomienda utilizar el servicio Neon para la creación de esta base de datos.

#### 5. Ejecutar migraciones

Una vez configurada la base de datos, se deben ejecutar las migraciones.

```bash
flask db upgrade
```

Si es la primera vez, inicializa las migraciones. Esto es solo en caso de que no existan las migraciones.

```bash
flask db init
flask db migrate -m "Initial migration"
flask db upgrade
```

#### 6. Iniciar la API

```bash
python app.py
```

La apliación se iniciará en ``http://localhost:5002``.