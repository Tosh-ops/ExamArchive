from django.urls import path
from . import views

urlpatterns = [
    path('', views.landing, name='landing'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    path('otp/', views.otp_view, name='otp'),
    path('home/', views.home, name='home'),
    path('search/', views.search, name='search'),
    path('paper/<int:paper_id>/', views.paper_detail, name='paper_detail'),
    path('paper/<int:paper_id>/report/', views.report_paper, name='report_paper'),
    path('paper/<int:paper_id>/delete/', views.delete_paper, name='delete_paper'),
    path('upload/', views.upload, name='upload'),
    path('upload/success/', views.upload_success, name='upload_success'),
    path('profile/', views.profile, name='profile'),
    path('badges/', views.badges, name='badges'),
    path('notifications/', views.notifications, name='notifications'),
    path('saved/', views.saved_papers, name='saved_papers'),
    path('admin-queue/', views.admin_queue, name='admin_queue'),
    path('approve/<int:paper_id>/', views.approve_paper, name='approve_paper'),
    path('reject/<int:paper_id>/', views.reject_paper, name='reject_paper'),
    path('admin-delete/<int:paper_id>/', views.admin_delete_paper, name='admin_delete_paper'),
]