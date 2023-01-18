from django.urls import path

from .import views

app_name = 'loan_app'

urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('inquiry/', views.InquiryView.as_view(), name='inquiry'),
    path('borrow_able/', views.BorrowAbleView.as_view(), name='borrow_able'),
    path('required_income/', views.RequiredIncomeView.as_view(), name='required_income'),
    path('repaid/', views.RepaidView.as_view(), name='repaid'),
    path('compare_interest/', views.CompareInterestView.as_view(), name='compare_interest'),
    path('create_interest/', views.CreateInterestView.as_view(), name='create_interest'),
    path('choice_bank/', views.ChoiceBankView.as_view(), name='choice_bank'),
    path('update_interest/<int:pk>/', views.UpdateInterestView.as_view(), name='update_interest'),
    path('delete_bank/<int:pk>/', views.DeleteBankView.as_view(), name='delete_bank'),
    path('create_option/', views.CreateOptionView.as_view(), name='create_option'),
    path('choice_option/', views.ChoiceOptionView.as_view(), name='choice_option'),
    path('update_option/<int:pk>/<int:bank_pk>/', views.UpdateOptionView.as_view(), name='update_option'),
    path('delete_option/<int:pk>/<int:bank_pk>/', views.DeleteOptionView.as_view(), name='delete_option'),
    ]
