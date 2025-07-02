from django.shortcuts import render
from apps.qr.models import QRCode
from django.core.exceptions import ObjectDoesNotExist

# Create your views here.


def index(request):
    short_code = request.GET.get('c')
    try:
        qr_code = QRCode.objects.get(short_public_code=f"{short_code}")
    except ObjectDoesNotExist:
        return render(request, 'index.html', {'template_name': 'q/not_exist.html'})
    return render(request, 'index.html', {'short_code': request.GET.get('c'),
                                            'code': qr_code,
                                            'template_name': 'q/qr_card.html'})
