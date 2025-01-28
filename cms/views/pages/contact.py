import json
from django.shortcuts import render, redirect
from django.core.mail import send_mail, BadHeaderError
from django.conf import settings
from django.contrib import messages
from django.utils.translation import gettext as _
from cms.forms import ContactForm
from cms.models import ContactMessage
import logging
from django.views.generic import TemplateView
from cms.views.mixins import SEOMetadataMixin, SchemaMixin, BreadcrumbsMixin
from cms.models.admin_notification import AdminNotification

logger = logging.getLogger(__name__)

class ContactView(SEOMetadataMixin, SchemaMixin, BreadcrumbsMixin, TemplateView):
    template_name = 'site/contact.html'

    def get(self, request):
        form = ContactForm()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = ContactForm(request.POST)
        if form.is_valid():

            # Save message to the database
            contact_message = ContactMessage.objects.create(**form.cleaned_data)

            # Create admin notification
            AdminNotification.objects.create(
                title=_("New Contact Form Submission"),
                message=_(
                    "A new contact form submission has been received.\n\n"
                    "Name: {name}\n"
                    "Email: {email}\n"
                    "Subject: {subject}\n\n"
                    "Message:\n{message}"
                ).format(
                    name=form.cleaned_data['name'],
                    email=form.cleaned_data['email'],
                    subject=form.cleaned_data['subject'],
                    message=form.cleaned_data['message']
                ),
            )

            # Prepare email details
            subject = _("Contact Form: {subject}").format(subject=form.cleaned_data['subject'])
            message = _(
                "Name: {name}\n"
                "Email: {email}\n\n"
                "{message}"
            ).format(
                name=form.cleaned_data['name'],
                email=form.cleaned_data['email'],
                message=form.cleaned_data['message']
            )
            sender = form.cleaned_data['email']
            recipient_list = [settings.DEFAULT_CONTACT_EMAIL]
            
            try:
                # Send email to the sender
                send_mail(subject, message, sender, recipient_list)

                # Notify admins
                if hasattr(settings, 'ADMIN_NOTIFICATION_EMAILS') and settings.ADMIN_NOTIFICATION_EMAILS:
                    admin_subject = _("New Contact Form Submission: {subject}").format(subject=form.cleaned_data['subject'])
                    admin_message = _(
                        "New contact form submission received.\n\n"
                        "Name: {name}\n"
                        "Email: {email}\n"
                        "Subject: {subject}\n\n"
                        "Message:\n{message}"
                    ).format(
                        name=form.cleaned_data['name'],
                        email=form.cleaned_data['email'],
                        subject=form.cleaned_data['subject'],
                        message=form.cleaned_data['message']
                    )
                    send_mail(admin_subject, admin_message, settings.DEFAULT_CONTACT_EMAIL, list(settings.ADMIN_NOTIFICATION_EMAILS))

                # Success message for the user
                messages.success(request, "Your message has been sent successfully!")

            except BadHeaderError:
                logger.error("Invalid email header detected.")
                messages.error(request, "Invalid email header. Please try again.")
            except Exception as e:
                logger.error(f"Error sending email: {e}")
                messages.error(request, "An error occurred while sending your message. Please try again later.")

            return redirect('contact')
        
        # Handle invalid form submission
        messages.error(request, "There were errors in your submission. Please correct them below.")
        return render(request, self.template_name, {'form': form})

    def get_schema(self):
        schema = {
            **self.get_base_schema(),
            "@type": "WebPage",
            "name": "Contact Us",
            "description": "Contact us for any queries",
            "mainEntityOfPage": self.request.build_absolute_uri(),
            "text": "Contact us for any queries"
        }
        return schema

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'schema': json.dumps(self.get_schema()),
            'schema_breadcrumbs': json.dumps(self.get_schema_breadcrumbs()),
            'meta_title': self.get_meta_title(),
            'meta_description': self.get_meta_description()
        })
        return context

    def get_meta_title(self):
        return "Contact Us"

    def get_meta_description(self):
        return "Contact us for any queries"
    
    def get_breadcrumbs(self):
        breadcrumbs = super().get_breadcrumbs()
        breadcrumbs.append({'name': 'Contact Us', 'url': self.request.path})
        return breadcrumbs