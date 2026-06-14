# MentorVirtual-Equipo1
#-------------------------------------------------------------

Mentor Virtual 🤖📱

#-------------------------------------------------------------
## 📝 Problemática
Muchas personas adultas que no completaron su educación formal abandonan el aprendizaje no por falta de capacidad, sino por experiencias negativas previas, baja confianza y dificultades para sostener hábitos de estudio. Los modelos tradicionales suelen omitir aspectos clave como la motivación, el reconocimiento de logros y el acompañamiento cotidiano, lo que genera desmotivación y un abandono temprano.

## 💡 Solución (MVP)
Una aplicación móvil centrada en un mentor virtual que acompaña diariamente al usuario para ayudarlo a generar constancia y una experiencia educativa positiva. El flujo funcional incluye:
1. **Registro de usuario** y selección de intereses iniciales.
2. **Feed de contenidos** interactivo que consume videos cortos educativos.
3. **Desafíos estáticos** breves asignados diariamente por categorías.
4. **Interacción con el Mentor Virtual** básico que provee feedback y mensajes motivacionales.
5. **Seguimiento y progreso** donde se visualizan los logros acumulados y las rachas de constancia.

---

## 🛠️ Stack Tecnológico Recomendado
El desarrollo del producto digital se estructurará con las siguientes herramientas:

*   **Frontend Mobile:** React Native / Expo.
*   **Feed de Contenido:** React + Componentes propios integrados con **YouTube Data API**.
*   **Mentor & Avatar:** Lógica conversacional básica + Avatar animado con **Lottie** / imágenes (con integración opcional a OpenAI/Gemini API y Web Speech API para Text-to-Speech).
*   **Backend:** Node.js + Express.
*   **Base de Datos y Autenticación:** Firebase Auth y Firestore (o PostgreSQL) + JWT.
*   **Testing APIs:** Postman.
*   **Métricas y Analítica:** Firebase Analytics, Google Sheets y Looker Studio.
*   **Hosting & Deploy:** Vercel/Netlify (Frontend) y Railway/Render (Backend).

---

## 📅 Plan de Trabajo (Sprints Clave)
*   **Semana 0:** Organización del equipo, asignación de roles (UX/UI, Devs, Data, QA) y setup inicial.
*   **Sprints 1 y 2 (Semanas 1-4):** Wireframes en Figma, definición del flujo del mentor y setup técnico.
*   **Sprint 3 (Semanas 5-6):** Desarrollo del login, guardado de intereses e integración inicial del feed de videos con YouTube API.
*   **Sprint 4 (Semanas 7-8):** Implementación del sistema de desafíos, cálculo de rachas y conexión con servicios externos de IA/Voz.
*   **Sprint 5 y 6 (Semanas 9-12):** Optimización del engagement, testing End-to-End, Deploy y preparación del Demo Day.
