"""SmartContentBackendContentGeneration URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from posts import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('posts/', views.PostsView.as_view(), name='posts_get'),
    path('save-post/', views.SavePostView.as_view(), name='save_post'),
    path('get-post-chat/<int:post_id>/', views.PostChatView.as_view(), name='get'),
    path('generate-post/', views.PostTemplateView.as_view(), name='get'),
    path('get-post-detail/<int:post_id>/', views.PostDetailView.as_view(), name='get'),
    path('send-message/', views.MessageTemplateView.as_view(), name='post'),
    path('delete-post/<int:post_id>/', views.PostsView.as_view(), name='delete'),
    path('update-message/', views.MessageTemplateView.as_view(), name='put'),
    path('get-survey-questions/', views.SurveyQuestionsTemplateView.as_view(), name='put'),
    path('save-survey/', views.SurveyQuestionsTemplateView.as_view(), name='post'),
    path('get-survey-answers/<int:post_survey_id>/', views.SurveyAnswersTemplateView.as_view(), name='get'),

]
