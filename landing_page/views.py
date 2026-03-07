from django.shortcuts import render, redirect
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from .models import ContactMessage, SiteConfiguration


def home(request):
    return render(request, 'index.html')


def contact(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        message = request.POST.get('message')

        if name and email and message:
            ContactMessage.objects.create(
                name=name, email=email, message=message
            )

            try:
                site_config = SiteConfiguration.load()
                to_email = (
                    site_config.email_address or settings.EMAIL_HOST_USER
                )
                if to_email:
                    email_msg = (
                        f"Name: {name}\nEmail: {email}\n\n"
                        f"Message:\n{message}"
                    )
                    send_mail(
                        subject=f"New Contact Message from {name}",
                        message=email_msg,
                        from_email=settings.EMAIL_HOST_USER,
                        recipient_list=[to_email],
                        fail_silently=True,
                    )
            except Exception:
                pass

            messages.success(
                request, 'Thank you! Your message has been sent successfully.'
            )
            return redirect('contact')
        else:
            messages.error(request, 'Please fill out all required fields.')

    return render(request, 'contact.html')