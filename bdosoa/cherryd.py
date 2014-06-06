#! /usr/bin/env python
"""The CherryPy daemon."""


def start(configfiles=None, daemonize=False, debug=False, environment=None,
          gid=None, imports=None, pidfile=None, uid=None):
    """Subscribe all engine plugins and start the engine."""

    import cherrypy
    from cherrypy.process import plugins

    if debug:
        cherrypy.log.error_log.setLevel(10)

    for i in imports or []:
        exec('import %s' % i)

    for c in configfiles or []:
        cherrypy.config.update(c)

        # If there's only one app mounted, merge config into it.
        if len(cherrypy.tree.apps) == 1:
            for app in cherrypy.tree.apps.values():
                if isinstance(app, cherrypy.Application):
                    app.merge(c)

    if environment is not None:
        cherrypy.config.update({'environment': environment})

    if daemonize:
        # Don't print anything to stdout/sterr.
        cherrypy.config.update({'log.screen': False})
        plugins.Daemonizer(cherrypy.engine).subscribe()

    if gid or uid:
        # Get the gid from the group name
        if gid and not isinstance(gid, int):
            import grp
            gid = grp.getgrnam(gid).gr_gid

        # Get the uid from the user name
        if uid and not isinstance(uid, int):
            import pwd
            uid = pwd.getpwnam(uid).pw_uid

        plugins.DropPrivileges(cherrypy.engine, uid=uid, gid=gid).subscribe()

    if pidfile:
        plugins.PIDFile(cherrypy.engine, pidfile).subscribe()

    # Always start the engine; this will start all other services
    try:
        cherrypy.engine.signals.subscribe()
        cherrypy.engine.start()
    except:
        # Assume the error has been logged already via bus.log.
        sys.exit(1)
    else:
        cherrypy.engine.block()


if __name__ == '__main__':
    import sys
    from optparse import OptionParser

    p = OptionParser()
    p.add_option('-c', '--config', action='append', dest='configs',
                 help='specify config file(s)')
    p.add_option('-d', '--daemon', action='store_true', dest='daemonize',
                 help='run the server as a daemon', default=False)
    p.add_option('-D', '--debug', action='store_true', dest='debug',
                 help='enable debug messages', default=False)
    p.add_option('-e', '--environment', dest='environment',
                 help='apply the given config environment')
    p.add_option('-g', '--gid', dest='gid',
                 help='setgid to the specified group/gid')
    p.add_option('-i', '--import', action='append', dest='imports',
                 help='specify module(s) to import')
    p.add_option('-p', '--pidfile', dest='pidfile',
                 help='store the process id in the given file')
    p.add_option('-P', '--path', action='append', dest='paths',
                 help='add the given path(s) to sys.path')
    p.add_option('-u', '--uid', dest='uid',
                 help='setuid to the specified user/uid')
    options, args = p.parse_args()

    for path in options.paths or []:
        sys.path.insert(0, path)

    start(
        configfiles=options.configs,
        daemonize=options.daemonize,
        debug=options.debug,
        environment=options.environment,
        gid=options.gid,
        imports=options.imports,
        pidfile=options.pidfile,
        uid=options.uid,
    )
