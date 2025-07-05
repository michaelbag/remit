from django.shortcuts import render
from apps.qr.models import QRCode
from django.core.exceptions import ObjectDoesNotExist

# Create your views here.


def index(request):
    short_code = request.GET.get('c')
    try:
        # qr_code = QRCode.objects.get(short_public_code="3EJIte6lTMKNi1OFn6CJFA")[0]
        qr_code = QRCode.objects.get(guid_public_code="dc4248b5-eea5-4cc2-8d8b-53859fa08914")
        # qr_code = QRCode.objects.get(code="TD0000005")
    except ObjectDoesNotExist:
        return render(request, 'q/not_exist.html', {'short_code': short_code })
    return render(request, 'q/qr_card.html', {'code': qr_code})
