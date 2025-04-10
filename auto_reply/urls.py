from django.urls import path
from .views import AutoReplyView

urlpatterns = [
    path('auto-reply/', AutoReplyView.as_view(), name='auto-reply'),
] 