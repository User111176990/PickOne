# PRD — PickOne

## 1. Resumen del producto

PickOne es una plataforma de encuestas binarias de respuesta rápida ("A o B") diseñada para consumo continuo. La propuesta de valor es una interacción inmediata: el usuario responde en segundos y obtiene feedback instantáneo en forma de resultados.

## 2. Problema y oportunidad

Las plataformas de contenido breve han demostrado alta retención cuando eliminan fricción y recompensan cada acción con un resultado inmediato. PickOne traslada ese patrón a encuestas de texto ultra cortas y virales.

## 3. Público objetivo

- Usuarios móviles de 16–35 años.
- Audiencia activa en redes sociales.
- Personas que consumen contenido rápido y participativo.

## 4. Funcionalidades principales

### 4.1 Cuenta de usuario

- Registro por email/contraseña (MVP).
- Inicio de sesión y cierre de sesión.
- Recuperación de contraseña (fase 2).

### 4.2 Encuestas

Cada encuesta incluye:

- Pregunta corta (máximo recomendado: 120 caracteres).
- Opción A (obligatoria).
- Opción B (obligatoria).
- Autor, fecha de creación, estado de moderación.

### 4.3 Votación y resultados

- Un voto por usuario por encuesta.
- Resultado visible justo después de votar.
- Mostrar porcentaje + total de votos.
- Actualización en tiempo real o casi real.

### 4.4 Feed infinito

- Scroll infinito móvil-first.
- Mezcla de encuestas recientes + tendencia.
- Inserción de anuncio cada N encuestas.

## 5. Reglas de negocio

- Frecuencia de creación limitada por usuario: configurable entre 3 y 7 días.
- Validaciones anti-spam:
  - Longitud mínima/máxima de texto.
  - Rate limiting por IP/usuario.
  - Lista de palabras prohibidas (MVP básico).
- Moderación:
  - Reporte de contenido.
  - Ocultar encuesta reportada bajo umbral de seguridad.

## 6. Engagement y retención

- Ranking de “Tendencia” por votos y velocidad de crecimiento.
- “Encuesta del día” (selección automática o curada).
- Notificaciones internas (fase 2): nuevas encuestas de autores seguidos.
- Reacciones/likes (opcional, fase futura).

## 7. Monetización

- Google AdSense.
- Formatos recomendados:
  - In-feed (entre encuestas cada 4–8 ítems).
  - Banner fijo no intrusivo en móvil.
- Reglas:
  - Evitar saturación.
  - Mantener consistencia visual.

## 8. KPIs de producto

- DAU/MAU.
- Encuestas respondidas por sesión.
- Tiempo medio por sesión.
- Retención D1, D7 y D30.
- Tasa de creación de encuestas por usuario activo.
- CTR e ingresos por mil impresiones (RPM) de anuncios.

## 9. Requisitos no funcionales

- Mobile-first, responsive.
- Tiempo de carga percibida < 2s en feed inicial.
- Alta disponibilidad en API de votación.
- Cumplimiento básico de privacidad y consentimiento de cookies.

## 10. Riesgos

- Spam y contenido ofensivo.
- Dependencia de tráfico social.
- Saturación de anuncios reduciendo retención.

## 11. Fuera de alcance (MVP)

- Comentarios complejos por encuesta.
- Mensajería privada.
- Sistema de seguidores completo.
