from django.shortcuts import render
from apps.qr.models import QRCode

# Create your views here.


def index(request):
    short_code = request.GET.get('c')
    qr_code = QRCode.objects.get(short_public_code=f"{short_code}")
    return render(request, 'q/index.html', {'short_code': request.GET.get('c'),
                                            'code': qr_code})
