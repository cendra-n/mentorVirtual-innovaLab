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

### 6. Listar Usuarios
Devuelve una lista con todos los usuarios registrados (con su perfil y configuración). Útil para vistas del equipo de trabajo.

- **Ruta**: `/api/users/`
- **Método**: `GET`
- **Autenticación**: Requerida (Token)
- **Respuesta Exitosa (200 OK)**:
  ```json
  [
    {
      "id": 1,
      "username": "admin",
      "email": "admin@example.com",
      "phone": "",
      "avatar_url": "",
      "config": {
        "font_size": "MEDIUM",
        "high_contrast": false,
        "voice_guidance": false
      }
    },
    {
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
  ]
  ```
