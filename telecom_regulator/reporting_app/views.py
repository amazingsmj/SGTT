from django.shortcuts import render
from rest_framework import views, permissions, response
from django.http import HttpResponse
from reportlab.pdfgen import canvas
from io import BytesIO
from openpyxl import Workbook


# Create your views here.


class SamplePDFReportView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        buffer = BytesIO()
        p = canvas.Canvas(buffer)
        p.drawString(100, 800, "Rapport PDF - Système de Gestion des Titres")
        p.showPage()
        p.save()
        buffer.seek(0)
        resp = HttpResponse(buffer, content_type='application/pdf')
        resp['Content-Disposition'] = 'attachment; filename="rapport.pdf"'
        return resp


class SampleExcelReportView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        wb = Workbook()
        ws = wb.active
        ws.title = 'Rapport'
        ws.append(['Colonne', 'Valeur'])
        ws.append(['Exemple', 123])
        output = BytesIO()
        wb.save(output)
        output.seek(0)
        resp = HttpResponse(output.getvalue(), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        resp['Content-Disposition'] = 'attachment; filename="rapport.xlsx"'
        return resp
