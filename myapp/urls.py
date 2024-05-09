from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('index', views.index, name='index'),
    path('about/', views.about, name='about'),
    path('allcourses/', views.allcourses, name='allcourses'),
    path('contact/', views.contact, name='contact'),
    path('course/<int:id>', views.course, name='course'),
    path('forgot_password/', views.forgot_password, name='forgot_password'),
    path('login/', views.user_login, name='login'),
    path('payment/<int:id>', views.payment, name='payment'),
    path('register/', views.user_register, name='register'),
    path('watchlist/', views.watchlist, name='watchlist'),
    path('gallery/', views.gallery, name='gallery'),
    path('create_account',views.create_account,name='create_account'),
    path('auth_login',views.auth_login,name='auth_login'),
      path('mpesa_checkout',views.mpesa_checkout,name='mpesa_checkout'),
      path('card_checkout',views.CardPayments,name="card_checkout"),
      path('paymentProcessing',views.PaymentCallback,name='paymentProcessing'),
      path('profile',views.user_profile,name='profile'),
      path('reset_password',views.reset_password,name="reset_password"),
      path('submit_quiz',views.submit_quiz,name='submit_quiz'),
      path('logout',views.logout,name='logout'),
      path("terms",views.terms,name="terms"),
      path('module/<int:id>', views.module, name='module'),
      path('download_certificate',views.download_certificate,name="download_certificate"),
      path('faqs',views.faqs,name='faqs')
  
]

