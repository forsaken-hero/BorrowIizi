from django.urls import path
from . import views

urlpatterns = [
    path('', views.sign_in, name='sign_in'),
    path('sign_out/', views.sign_out, name='sign_out'),
    path('sign_up/', views.sign_up, name='sign_up'),
    path('front_page/', views.front_page, name='front_page'),
    path('loans/', views.loans, name='loans'),
    path('loan/<int:item_id>/', views.loan, name='loan'),
    path('return/<int:item_id>/', views.ret, name='ret'),
]