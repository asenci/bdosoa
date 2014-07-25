#! /usr/bin/env python
"""The CherryPy daemon."""


# noinspection PyDocstring
def start(cgi=False, config=None, daemon=False, debug=False,
          environment=None, fastcgi=False, gid=None, imports=None,
          path=None, pidfile=None, quiet=False, scgi=False, uid=None):
    """Subscribe all engine plugins and start the engine."""
    import cherrypy
    import sys
    from cherrypy.process import plugins, servers

    # Set logging level
    if debug and quiet:
        cherrypy.log.error(
            'You may only specify one of the debug, quiet options', 'ENGINE',
            severity=50)
        sys.exit(1)

    if debug:
        cherrypy.log.error_log.setLevel(10)
    elif quiet:
        cherrypy.log.error_log.setLevel(30)

    # Insert paths to the search path
    for p in path or []:
        sys.path.insert(0, p)

    # Import requested modules
    for i in imports or []:
        exec('import %s' % i)

    # Merge configuration files
    for c in config or []:
        cherrypy.config.update(c)

        # If there's only one app mounted, merge config into it.
        if len(cherrypy.tree.apps) == 1:
            for app in cherrypy.tree.apps.values():
                if isinstance(app, cherrypy.Application):
                    app.merge(c)

    # Set CherryPy environment
    if environment is not None:
        cherrypy.config.update({'environment': environment})

    # Only daemonize if asked to.
    if daemon:
        # Don't print anything to stdout/sterr.
        cherrypy.config.update({'log.screen': False})
        plugins.Daemonizer(cherrypy.engine).subscribe()

    # Write PID file
    if pidfile:
        plugins.PIDFile(cherrypy.engine, pidfile).subscribe()

    # Drop privileges
    if gid or uid:

        try:
            gid = int(gid) if gid else None
        except ValueError:
            # Get the gid from the group name
            import grp
            gid = grp.getgrnam(gid).gr_gid

        try:
            uid = int(uid) if uid else None
        except ValueError:
            # Get the uid from the user name
            import pwd
            uid = pwd.getpwnam(uid).pw_uid

        plugins.DropPrivileges(cherrypy.engine, uid=uid, gid=gid).subscribe()

    # Handle OS signals
    cherrypy.engine.signals.subscribe()

    # Start a *cgi server instead of the default HTTP server
    if (fastcgi and (scgi or cgi)) or (scgi and cgi):
        cherrypy.log.error(
            'You may only specify one of the cgi, fastcgi, and scgi options.',
            'ENGINE')
        sys.exit(1)

    if fastcgi or scgi or cgi:
        # Turn off autoreload when using *cgi.
        cherrypy.config.update({'engine.autoreload.on': False})

        # Turn off the default HTTP server (which is subscribed by default).
        cherrypy.server.unsubscribe()

        if fastcgi:
            httpserver = servers.FlupFCGIServer(
                application=cherrypy.tree,
                bindAddress=cherrypy.server.bind_addr)
        elif scgi:
            httpserver = servers.FlupSCGIServer(
                application=cherrypy.tree,
                bindAddress=cherrypy.server.bind_addr)
        else:
            httpserver = servers.FlupCGIServer(
                application=cherrypy.tree)

        cherrypy.server = servers.ServerAdapter(
            cherrypy.engine, httpserver, cherrypy.server.bind_addr)
        cherrypy.server.subscribe()

    # Always start the engine; this will start all other services
    try:
        cherrypy.engine.start()
    except:
        # Assume the error has been logged already via bus.log.
        sys.exit(1)
    else:
        cherrypy.engine.block()


# noinspection PyDocstring
def main(args=None):
    from optparse import OptionParser

    p = OptionParser()
    p.add_option('-c', '--config', action='append',
                 help='specify config file(s)')
    p.add_option('-d', '--daemon', action='store_true', default=False,
                 help='run the server as a daemon')
    p.add_option('-D', '--debug', action='store_true', default=False,
                 help='enable debug messages')
    p.add_option('-e', '--environment',
                 help='apply the given config environment')
    p.add_option('-f', '--fastcgi', action="store_true", default=False,
                 help='start a fastcgi server')
    p.add_option('-g', '--gid',
                 help='setgid to the specified group/gid')
    p.add_option('-i', '--import', action='append', dest='imports',
                 help='specify module(s) to import')
    p.add_option('-p', '--pidfile',
                 help='store the process id in the given file')
    p.add_option('-P', '--path', action='append',
                 help='add the given path(s) to sys.path')
    p.add_option('-q', '--quiet', action='store_true', default=False,
                 help='only log warnings and errors')
    p.add_option('-s', '--scgi', action="store_true", default=False,
                 help='start a scgi server')
    p.add_option('-u', '--uid',
                 help='setuid to the specified user/uid')
    p.add_option('-x', '--cgi', action="store_true", default=False,
                 help='start a cgi server')
    options, args = p.parse_args(args)

    start(**vars(options))


if __name__ == '__main__':
    main()
