import threading
import logging
from django.core.mail import send_mail
from django.conf import settings
from courses.models import Course

logger = logging.getLogger('enrollment')

def _send_async(subject, message, recipient_list):
    """Ejecuta el envío de correo en un hilo en segundo plano."""
    try:
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=recipient_list,
            fail_silently=False,
        )
        logger.info(f"Correo de inscripción enviado exitosamente a: {recipient_list}")
    except Exception as e:
        logger.error(f"Error al enviar correo de inscripción a {recipient_list}: {str(e)}", exc_info=True)

def trigger_enrollment_email(user, course_id):
    """Prepara los datos del curso y dispara el correo en un hilo secundario.
    Se llama DESPUÉS de que sp_enroll_student confirmó la inscripción — si esto
    falla, no afecta la inscripción ya persistida en base."""
    try:
        course = Course.objects.get(id=course_id)
        professor_name = course.professor.username.replace('.', ' ') if course.professor else "Tu docente asignado"
        level_display = course.get_level_display()
        discipline = course.discipline if course.discipline else "Formación General"
        objectives = course.objectives if course.objectives else "Desarrollar nuevas habilidades y potenciar tu perfil."

        subject = f"¡Inscripción Confirmada! Bienvenido/a a: {course.title}"

        message = (
            f"Hola, {user.username}!\n\n"
            f"Te confirmamos que te has inscrito correctamente en nuestra plataforma Mentor Virtual.\n\n"
            f"--- DETALLES DEL CURSO ---\n"
            f"• Curso: {course.title}\n"
            f"• Disciplina: {discipline}\n"
            f"• Nivel: {level_display}\n"
            f"• Profesor a cargo: {professor_name}\n\n"
            f"--- ¿QUÉ LOGRARÁS EN ESTE CURSO? ---\n"
            f"{objectives}\n\n"
            f"Ya puedes ingresar a tu portal y comenzar con el primer módulo. ¡Mucho éxito en tu aprendizaje!\n\n"
            f"Atentamente,\n"
            f"El equipo de Mentor Virtual."
        )

        email_thread = threading.Thread(
            target=_send_async,
            args=(subject, message, [user.email])
        )
        email_thread.daemon = True
        email_thread.start()

    except Exception as e:
        logger.error(f"Error al preparar el correo para el curso ID {course_id}: {str(e)}", exc_info=True)
