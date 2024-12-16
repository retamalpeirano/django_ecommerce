from django.core.mail import EmailMessage
from django.shortcuts import render, redirect

def home(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        message = request.POST.get('message')

        # Construir el correo
        email_subject = f"Nuevo mensaje de {name}"
        email_body = f"Nombre: {name}\nCorreo: {email}\n\nMensaje:\n{message}"

        # Configurar destinatario y enviar correo
        email = EmailMessage(subject=email_subject, body=email_body, to=['tu_correo@example.com'])
        email.send()

        return redirect('home')  # Redirigir después de enviar

    return render(request, 'home.html')