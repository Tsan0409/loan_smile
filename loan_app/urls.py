from django.urls import path

from .import views

app_name = 'loan_app'

urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('sample/', views.SampleView.as_view(), name='sample'),
    path('inquiry/', views.InquiryView.as_view(), name='inquiry'),
    path('borrow_able/', views.BorrowAbleView.as_view(), name='borrow_able'),
    path('required_income/', views.RequiredIncomeView.as_view(), name='required_income'),
    path('repaid/', views.RepaidView.as_view(), name='repaid'),
    path('create_interest/', views.CreateInterestView.as_view(), name='create_interest'),
    path('choice_bank/', views.ChoiceBankView.as_view(), name='choice_bank'),
    path('change_interest/<int:pk>/', views.ChangeInterestView.as_view(), name='change_interest'),
    path('delete_bank/', views.DeleteBankView.as_view(), name='delete_bank'),
    path('delete_confirm/<int:pk>/', views.DeleteConfirmView.as_view(), name='delete_confirm'),
    ]
