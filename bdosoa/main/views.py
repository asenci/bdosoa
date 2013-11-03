from django.shortcuts import redirect
from django.views.decorators.csrf import csrf_exempt

from spyne.server.django import DjangoApplication
from spyne.model.primitive import Integer, Unicode
from spyne.service import ServiceBase
from spyne.protocol.soap import Soap11
from spyne.application import Application
from spyne.decorator import srpc

from bdosoa.main.models import Message

import logging


logger = logging.getLogger('django.request')


class SOAPService(ServiceBase):
    @srpc(Unicode, Unicode, _returns=Integer)
    def processRequest(header, message):
        try:
            Message.from_string(message).save()

        except Exception as e:
            logger.error(e)
            return -1

        else:
            return 0


def index(request):
    return redirect('/admin/')


soap_app = csrf_exempt(
    DjangoApplication(
        Application(
            services=[SOAPService],
            tns='processResponse',
            in_protocol=Soap11(validator='lxml'),
            out_protocol=Soap11(),
        )
    )
)
