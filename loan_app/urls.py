from django.urls import path

from .import views

app_name = 'loan_app'

urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('sample/', views.SampleView.as_view(), name='sample'),
    path('sampleB/', views.SamplebView.as_view(), name='sampleb'),
    path('inquiry/', views.InquiryView.as_view(), name='inquiry'),
    path('borrow_able/', views.BorrowAbleView.as_view(), name='borrow_able'),
    path('required_income/', views.RequiredIncomeView.as_view(), name='required_income')
    ]
