from django.db.models.signals import post_save
from django.http import HttpResponse, HttpResponseNotAllowed
from django.shortcuts import redirect
from django.views.decorators.csrf import csrf_exempt

from bdosoa.main.messages import receive_soap
from bdosoa.main.models import Message
from bdosoa.main.soap import SOAPApplication


def index(request):
    return redirect('/admin/')


soap = SOAPApplication('BDO/SoapServer')
soap.register_method('processRequest', receive_soap)
soap.register_method('processResponse', receive_soap)
soap = csrf_exempt(soap)


@csrf_exempt
def api(request):

    import logging
    logger = logging.getLogger('{0}.api'.format(__name__))

    try:
        if not request.user.is_authenticated():
            if not request.get_host().startswith('127.0.0.1:'):
                return redirect('/admin/')

        if request.method != 'POST':
            return HttpResponseNotAllowed(permitted_methods=['POST'])

        command = request.POST.get('command', None)

        if command is None:
            return HttpResponse('Command missing\n')

        if command == 'flush_queue':
            instance = object()
            instance.status = 'queued'
            instance.direction = 'BDRtoBDO'
            post_save.send(Message, instance=instance)

            instance = object()
            instance.status = 'queued'
            instance.direction = 'BDOtoBDR'
            post_save.send(Message, instance=instance)

        return HttpResponse('OK\n')

    except Exception as e:
        logger.exception(e)