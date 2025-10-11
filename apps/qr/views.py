from django.shortcuts import render, get_object_or_404
from apps.qr.models import QRCode
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from django.http import Http404

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


def qr_form_view(request, shortcode):
    """
    View for displaying QR code form at q/[shortcode] URL
    """
    try:
        # Get QR code by short_public_code
        qr_code = QRCode.objects.get(short_public_code=shortcode)
        
        # Check if QR code is not archived
        if qr_code.archive:
            return render(request, 'q/not_exist.html', {
                'short_code': shortcode,
                'error_message': 'This QR code has been archived.'
            })
        
        # Render the form template
        return render(request, 'q/qr_form.html', {
            'qr_code': qr_code,
            'shortcode': shortcode
        })
        
    except ObjectDoesNotExist:
        return render(request, 'q/not_exist.html', {
            'short_code': shortcode,
            'error_message': 'QR code not found.'
        })
    except MultipleObjectsReturned:
        return render(request, 'q/multi_exists.html', {
            'short_code': shortcode,
            'error_message': 'Multiple QR codes found with the same short code.'
        })
