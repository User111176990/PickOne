# Autenticación en PickOne (estado actual y siguiente paso)

## Estado actual (15 de abril de 2026)

Actualmente el repositorio **no tiene aplicación implementada** (frontend/backend), solo documentación de producto y arquitectura.

Eso significa que **todavía no se puede iniciar sesión**, ni con Google ni con email.

## ¿Se podrá iniciar sesión con Google?

Sí, está contemplado como mejora inmediata sobre el MVP de login básico.

## Opciones de login recomendadas

1. **Email + contraseña** (base MVP).
2. **Google OAuth** (muy recomendado para acelerar registro y reducir fricción).

## Propuesta técnica para Google Login

- Usar **Auth.js (NextAuth)** con proveedor Google.
- Variables de entorno:
  - `AUTH_GOOGLE_ID`
  - `AUTH_GOOGLE_SECRET`
  - `AUTH_SECRET`
- Configurar callback URL en Google Cloud Console.
- Persistir usuario en tabla `users` con campo `auth_provider` (`email`/`google`).

## Flujo de inicio de sesión esperado

1. Usuario toca “Continuar con Google”.
2. Google autentica y devuelve perfil.
3. Se crea (o recupera) el usuario.
4. Se establece sesión (JWT/cookie segura).
5. Usuario entra al feed de encuestas.

## Qué falta para que funcione

- Implementar frontend de login.
- Implementar endpoints/session middleware.
- Configurar credenciales reales en entorno.
- Ejecutar pruebas E2E del flujo de auth.
