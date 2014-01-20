def uwsgi_app(environ, start_response):
    import uwsgi

    from django.core.handlers.wsgi import WSGIHandler

    try:
        from cStringIO import StringIO
    except ImportError:
        from StringIO import StringIO

    if environ.get('HTTP_TRANSFER_ENCODING', None) == 'chunked':
        wsgi_input = ''

        while True:
            chunk = uwsgi.chunked_read()

            if chunk:
                wsgi_input += chunk

            else:
                break

        environ['wsgi.input'] = StringIO(wsgi_input)
        environ['CONTENT_LENGTH'] = len(wsgi_input)

    return WSGIHandler()(environ, start_response)

