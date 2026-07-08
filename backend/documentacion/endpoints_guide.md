# Guía de Endpoints de la API

Esta guía detalla los endpoints disponibles en la API de **Mentor Virtual**, formatos de entrada/salida y métodos de autenticación.

---

## 🔒 Autenticación

Todos los endpoints protegidos requieren el envío de un **Token de Django REST Framework** en las cabeceras HTTP:

```http
Authorization: Token <tu_key_de_token>
```

---

## 📋 Endpoints de Usuario

### 1. Registro de Usuario
Permite a nuevos usuarios registrarse en la plataforma, creando su perfil y sus opciones de accesibilidad de manera simultánea.

- **Ruta**: `/api/register/`
- **Método**: `POST`
- **Autenticación**: Ninguna (Público)
- **Cuerpo de la Petición (JSON)**:
  ```json
  {
    "username": "usuario_ejemplo",
    "password": "MiPasswordSegura1",
    "password_confirm": "MiPasswordSegura1",
    "email": "ejemplo@correo.com",
    "phone": "+56912345678",        // Opcional
    "avatar_url": "https://url.com/img.png", // Opcional
    "font_size": "MEDIUM",           // Opcional ("SMALL", "MEDIUM", "LARGE")
    "high_contrast": false,          // Opcional (boolean)
    "voice_guidance": false          // Opcional (boolean)
  }
  ```
- **Respuesta Exitosa (201 Created)**:
  ```json
  {
    "message": "Usuario registrado exitosamente",
    "token": "9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b",
    "user": {
      "id": 5,
      "username": "usuario_ejemplo",
      "email": "ejemplo@correo.com",
      "phone": "+56912345678",
      "avatar_url": "https://url.com/img.png",
      "config": {
        "font_size": "MEDIUM",
        "high_contrast": false,
        "voice_guidance": false
      }
    }
  }
  ```
- **Respuestas de Error Frecuentes (400 Bad Request)**:
  - *Contraseña débil:*
    ```json
    {
      "password": ["La contraseña debe contener un mínimo de 8 caracteres, una mayúscula y un número."]
    }
    ```
  - *Contraseñas no coinciden:*
    ```json
    {
      "password_confirm": ["Las contraseñas ingresadas no coinciden."]
    }
    ```
  - *Email duplicado:*
    ```json
    {
      "email": ["Este correo electrónico ya se encuentra registrado."]
    }
    ```
  - *Campos obligatorios vacíos:*
    ```json
    {
      "username": ["El username es un campo obligatorio."]
    }
    ```

---

### 2. Inicio de Sesión (Login)
Valida las credenciales y devuelve un token activo junto con la información del usuario.

- **Ruta**: `/api/login/`
- **Método**: `POST`
- **Autenticación**: Ninguna (Público)
- **Cuerpo de la Petición (JSON)**:
  ```json
  {
    "email": "ejemplo@correo.com",
    "password": "MiPasswordSegura1"
  }
  ```
- **Respuesta Exitosa (200 OK)**:
  ```json
  {
    "message": "Login exitoso",
    "token": "9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b",
    "user": {
      "id": 5,
      "username": "usuario_ejemplo",
      "email": "ejemplo@correo.com",
      "phone": "+56912345678",
      "avatar_url": "https://url.com/img.png",
      "config": {
        "font_size": "MEDIUM",
        "high_contrast": false,
        "voice_guidance": false
      }
    }
  }
  ```
- **Respuestas de Error Frecuentes (400 Bad Request)**:
  - *Credenciales incorrectas:*
    ```json
    {
      "error": "Credenciales inválidas."
    }
    ```
  - *Campos obligatorios vacíos:*
    ```json
    {
      "email": ["El email es un campo obligatorio."]
    }
    ```

---

### 3. Cierre de Sesión (Logout)
Invalida y elimina el token de autenticación del usuario logueado en la base de datos.

- **Ruta**: `/api/logout/`
- **Método**: `POST`
- **Autenticación**: Requerida (Token)
- **Respuesta Exitosa (200 OK)**:
  ```json
  {
    "message": "Sesión cerrada y token eliminado exitosamente."
  }
  ```

---

### 4. Obtener Perfil de Usuario
Devuelve los datos del perfil y la configuración de accesibilidad del usuario autenticado.

- **Ruta**: `/api/profile/`
- **Método**: `GET`
- **Autenticación**: Requerida (Token)
- **Respuesta Exitosa (200 OK)**:
  ```json
  {
    "id": 5,
    "username": "usuario_ejemplo",
    "email": "ejemplo@correo.com",
    "phone": "+56912345678",
    "avatar_url": "https://url.com/img.png",
    "config": {
      "font_size": "MEDIUM",
      "high_contrast": false,
      "voice_guidance": false
    }
  }
  ```

---

### 5. Actualizar Perfil de Usuario
Permite actualizar campos de perfil o configuraciones de accesibilidad. Soporta actualizaciones parciales.

- **Ruta**: `/api/profile/`
- **Método**: `PUT` / `PATCH`
- **Autenticación**: Requerida (Token)
- **Cuerpo de la Petición (JSON - Todos opcionales en PATCH)**:
  ```json
  {
    "email": "nuevo_correo@correo.com",
    "phone": "+56987654321",
    "avatar_url": "https://url.com/nuevo_avatar.png",
    "font_size": "LARGE",
    "high_contrast": true,
    "voice_guidance": true
  }
  ```
- **Respuesta Exitosa (200 OK)**:
  ```json
  {
    "message": "Perfil actualizado exitosamente",
    "user": {
      "id": 5,
      "username": "usuario_ejemplo",
      "email": "nuevo_correo@correo.com",
      "phone": "+56987654321",
      "avatar_url": "https://url.com/nuevo_avatar.png",
      "config": {
        "font_size": "LARGE",
        "high_contrast": true,
        "voice_guidance": true
      }
    }
  }
  ```

---

### 6. Listar Usuarios (Paginado)
Retorna una lista paginada de todos los usuarios registrados en la plataforma, incluyendo su rol, perfil y su configuración de accesibilidad. Devuelve 10 registros por página.

> ⚠️ **Nota de Desarrollo / Pruebas en Swagger:**
> Por defecto, cualquier usuario creado mediante el endpoint de `/api/register/` (o desde la interfaz de Swagger) se registra automáticamente con el rol de **STUDENT** (Alumno). Debido a esto, el sistema denegará el acceso a esta lista. Para poder probar este endpoint de forma exitosa, se debe iniciar sesión utilizando una cuenta con privilegios de **Staff/Admin** (creada previamente desde la terminal/shell de Docker).

- **Ruta**: `/api/auth/users/`
- **Método**: `GET`
- **Autenticación**: Requerida (Token) y Acceso restringido solo para miembros del Staff (`is_staff=True`).
- **Parámetros de Consulta (Query Params)**:
  - `page` (Opcional, Entero): Número de página a consultar. Por defecto es `1`.

- **Respuesta Exitosa (200 OK)**:
  ```json
  {
    "count": 5,
    "total_pages": 1,
    "next": null,
    "previous": null,
    "results": [
      {
        "id": 1,
        "username": "nadiaAdmin",
        "email": "nadiaAdmin@example.com",
        "role": "STUDENT",
        "phone": "",
        "avatar_url": "",
        "config": {
          "font_size": "MEDIUM",
          "high_contrast": false,
          "voice_guidance": false
        }
      }
    ]
  }

```

* **Respuestas de Error Frecuentes**:
* *Página vacía o fuera de rango (404 Not Found):*
```json
{
  "detail": "Error página vacía, solo hay 1 páginas cargadas hasta el momento"
}

```

* *Usuario Alumno / Sin privilegios de Staff (403 Forbidden):*
```json
{
  "detail": "Las credenciales de autenticación no proveen privilegios de staff."
}

```

---

## ⚙️ Sistema de Paginación Personalizada (`pagination.py`)

Para mantener respuestas estandarizadas y controlar la navegación en el Frontend, el backend utiliza una extensión del paginador nativo de Django REST Framework (`PageNumberPagination`).

### Lógica de Funcionamiento:

1. **Control de Páginas Vacías:** Si el cliente solicita una página que no posee registros (por ejemplo, escribir `?page=99` de forma manual), el método heredado de Django suele arrojar una excepción genérica. Nuestra clase intercepta este error y calcula en tiempo real mediante `math.ceil` cuántas páginas existen realmente basándose en el total de elementos del sistema, devolviendo un mensaje detallado al usuario.
2. **Inyección de Metadatos:** Se calcula el total de páginas (`total_pages`) y se inyecta directamente en la raíz del cuerpo de la respuesta JSON junto con los enlaces tradicionales de navegación (`next` y `previous`).

### Estructura Base de Respuesta Global Paginada

Cualquier endpoint que implemente la clase `CustomPagination` adoptará la siguiente estructura de salida:

* **Estructura del Cuerpo (JSON)**:
```json
{
  "count": 0,           // Cantidad total de registros existentes en la base de datos
  "total_pages": 1,     // Cantidad total de páginas disponibles basadas en bloques de 10
  "next": null,         // URL de la siguiente página (String o null)
  "previous": null,     // URL de la página anterior (String o null)
  "results": []         // Array con los objetos de datos solicitados
}

```
