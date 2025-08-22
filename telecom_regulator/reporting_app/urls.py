from django.urls import path
from .views import SamplePDFReportView, SampleExcelReportView

urlpatterns = [
    path('sample/pdf/', SamplePDFReportView.as_view(), name='report-pdf'),
    path('sample/excel/', SampleExcelReportView.as_view(), name='report-excel'),
]