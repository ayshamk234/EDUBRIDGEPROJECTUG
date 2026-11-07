from django.urls import path
from .views import signup_view, login_view
from django.conf import settings
from django.conf.urls.static import static
from .views import study_material_detail

from . import views 


urlpatterns = [
    path('signup/', signup_view, name='signup_view'),
    path('', login_view, name='login_view'),
    path('book/<int:pk>/', views.book_detail, name='book_detail'),
    path('home/', views.home, name='home'),
    path('donate/', views.donate_view, name='Donate'),
    path('material/<int:material_id>/', study_material_detail, name='study_material_detail'),
    path('donate_study_material/', views.donate_study_material, name='donate_study_material'),
    path('donate/textbooks/', views.donate_textbook, name='donate_textbook'),
    path('receive/', views.receive_view, name='receive'),
     path('dashboard/', views.dashboard, name='user_dashboard'),
    path('update-profile/', views.update_profile, name='update-profile'),
    path('ocr/', views.alumni_chat_view, name='alumini'),
    path('book/<int:pk>/', views.book_detail, name='book_detail'),
    path('manage-requests/', views.manage_requests, name='manage_requests'),
    path('donate/textbook/', views.donate_textbook, name='donate_textbook'),
    path('donate/study-material/', views.donate_study_material, name='donate_study_material'),
    path('edit_donated_books/', views.sell_books, name='sell_books'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)