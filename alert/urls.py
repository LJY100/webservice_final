from django.urls import path

from . import views

urlpatterns = [
	path('', views.index, name='index'),
	path('<int:b_id>/', views.detail, name='detail'),
	path('resetAlert/', views.resetAlert, name='resetAlert'),
	path('scraping/<int:page_id>/', views.scraping, name='scraping'),
	path('kakao/', views.kakao, name='kakao'),
]