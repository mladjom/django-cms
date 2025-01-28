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





