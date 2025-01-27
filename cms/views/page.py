from django.views.generic import DetailView, TemplateView
from cms.models import Page, Post, Category
from cms.views.mixins import ViewCountMixin, SEOMetadataMixin, BreadcrumbsMixin, SchemaMixin
import json
from django.db.models import Count, Q
from cms.settings import SITE_SETTINGS
from django.shortcuts import render, redirect
from django.contrib import messages
from cms.forms import ContactForm
from cms.models import ContactMessage
import logging
from django.conf import settings
from django.core.mail import send_mail, BadHeaderError
from django.utils.translation import gettext_lazy as _

logger = logging.getLogger(__name__)

class HomeView(SEOMetadataMixin, SchemaMixin, TemplateView):
    model = Post
    template_name = 'site/home.html' 
    context_object_name = 'posts'

    def get_featured_posts(self):
        return Post.objects.filter(
            status=1, is_featured=True
        ).select_related('author', 'category').prefetch_related('tags')[:3]

    def get_schema(self):

        schema = {
            **self.get_base_schema(),
            "@type": "WebPage",
            "name": f"{SITE_SETTINGS['NAME']} - {SITE_SETTINGS['TAGLINE']}",
            "description": SITE_SETTINGS['DESCRIPTION'],
            "headline": SITE_SETTINGS['TAGLINE'],
            "mainEntity": {
                 "@type": "ItemList",
                "itemListElement": [
                    {
                        "@type": "BlogPosting",
                        "headline": post.title,
                        "description": post.excerpt or '',
                        "url": self.request.build_absolute_uri(post.get_absolute_url())
                    } for post in self.get_featured_posts()[:3]
                ]      
            }
        }
        return schema
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Optimize queries with select_related and prefetch_related
        featured_posts = self.get_featured_posts()
        latest_posts = Post.objects.filter(status=1).select_related(
            'author', 'category'
        ).prefetch_related('tags').order_by('-created_at')[:4]
        
        popular_posts = Post.objects.filter(status=1).select_related(
            'author', 'category'
        ).prefetch_related('tags').order_by('-view_count')[:5]
        
        categories = Category.objects.annotate(
            post_count=Count('posts', filter=Q(posts__status=1))
        ).order_by('-post_count')[:6]
        
        context.update({
            'featured_posts': featured_posts,
            'latest_posts': latest_posts,
            'popular_posts': popular_posts,
            'categories': categories,
            'schema': json.dumps(self.get_schema()),
            'meta_title': self.get_meta_title(),
            'meta_description': self.get_meta_description(),
        })
        
        return context

    def get_meta_title(self):
        return f"{SITE_SETTINGS['NAME']} - {SITE_SETTINGS['TAGLINE']}"
    
    def get_meta_description(self):
        return str(SITE_SETTINGS['DESCRIPTION'])

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

class PageView(ViewCountMixin, SEOMetadataMixin, BreadcrumbsMixin, SchemaMixin, DetailView):
    model = Page 
    template_name = 'site/page.html'
    context_object_name = 'page'

    def get_schema(self):
        page = self.get_object()
        schema = {
            **self.get_base_schema(),
            "@type": "WebPage",
            "name": page.title,
            "description": page.meta_description,
            "mainEntityOfPage": self.request.build_absolute_uri(),
            "text": page.content
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
    
    def get_breadcrumbs(self):
        page = self.get_object()
        breadcrumbs = super().get_breadcrumbs()
        breadcrumbs.append({'name': page.title, 'url': page.get_absolute_url()})
        return breadcrumbs