from django.shortcuts import render
from apps.qr.models import QRCode
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned

# Create your views here.


def index(request):
    short_code = request.GET.get('c')
    try:
        qr_code = QRCode.objects.get(short_public_code=f"{short_code}")
    except ObjectDoesNotExist:
        return render(request, 'q/not_exist.html', {'short_code': short_code })
    except MultipleObjectsReturned:
        return render(request, 'q/multi_exists.html', {'short_code': short_code})
    return render(request, 'q/qr_card.html', {'code': qr_code})
