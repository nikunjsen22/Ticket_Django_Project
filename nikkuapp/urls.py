from django.urls import path
from . import views


urlpatterns = [
    path('', views.land, name='landing_page'),
    path('signup/', views.signup, name='signup'),
    path('login/', views.login, name='login'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('tickets/create/', views.create_ticket, name='create_ticket'),
    path('tickets/', views.tickets, name='tickets'),
    path('reports/', views.reports, name='reports'),
    path('customers/', views.customers, name='customers'),
    path('settings/', views.settings, name='settings'),
    path('help-center/', views.help_center, name='help_center'),
    path('notifications/', views.get_notifications, name='get_notifications'),
    path('notifications/<int:notification_id>/read/', views.mark_notification_read, name='mark_notification_read'),
    path('notifications/read-all/', views.mark_all_notifications_read, name='mark_all_notifications_read'),
    path('logout/', views.logout_view, name='logout'),
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('customer-tickets/', views.customer_tickets, name='customer_tickets'),
]

