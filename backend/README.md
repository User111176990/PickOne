# Backend MVP (implementado)

Este backend ya implementa una primera versión funcional de:

- Registro por email con código de verificación.
- Verificación + creación de contraseña.
- Login por email/contraseña.
- Creación de encuestas con cooldown.
- Feed con paginación por cursor.
- Voto único por usuario y resultados inmediatos.

## Ejecutar

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

Servidor: `http://localhost:8000`

## Flujo de registro actual

1. `POST /auth/register/request-code` con `{"email":"..."}`.
2. El backend devuelve `dev_code` (simula email en entorno local).
3. `POST /auth/register/verify` con `email`, `code`, `password`.
4. Devuelve JWT para sesión.

## Nota Google OAuth

Google OAuth está planificado, pero no implementado todavía en este backend.
