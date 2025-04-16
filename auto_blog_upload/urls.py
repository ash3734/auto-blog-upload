from django.urls import path
from .views import PreviewView, HelloWorldView, TestOpenAIView

urlpatterns = [
    path('preview/', PreviewView.as_view(), name='preview'),
    path('hello/', HelloWorldView.as_view(), name='hello'),
    path('test-openai/', TestOpenAIView.as_view(), name='test-openai'),
] 