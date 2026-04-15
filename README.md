# PickOne

Plataforma web de encuestas rápidas tipo **"¿Qué prefieres?"** enfocada en consumo continuo, interacción instantánea y experiencia **mobile-first**.

## Visión

Crear una experiencia adictiva de micro-interacciones donde cada usuario puede:

- Crear encuestas breves con 2 opciones.
- Votar y ver resultados al instante.
- Descubrir nuevas encuestas mediante scroll infinito.

## Objetivos de negocio

- Maximizar tiempo de sesión y número de interacciones por usuario.
- Escalar tráfico orgánico/social con contenido generado por usuarios.
- Monetizar mediante Google AdSense en espacios no intrusivos.

## Entregables incluidos en este repositorio

- `docs/producto-prd.md`: PRD completo (producto, UX, reglas, monetización).
- `docs/arquitectura-tecnica.md`: arquitectura propuesta, modelo de datos, API y escalabilidad.
- `docs/roadmap-mvp.md`: fases de implementación y métricas clave.
- `docs/autenticacion.md`: estado real del login y plan de Google OAuth.

## Estado

Documento base de planificación para iniciar implementación de MVP.

> Nota: a fecha del documento, aún no hay login implementado en código; ver `docs/autenticacion.md`.


## Implementación actual

Se añadió un backend MVP real en `backend/` con endpoints de autenticación por email+codigo, login, creación de encuestas, voto y resultados.
