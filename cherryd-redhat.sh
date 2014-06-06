#!/bin/sh
#
# cherryd Starts/stop the CherryPy daemon
#
# chkconfig:   - 85 15
# description: CherryPy is a pythonic, object-oriented web framework

### BEGIN INIT INFO
# Provides: cherryd
# Required-Start: $local_fs $remote_fs $network
# Required-Stop: $local_fs $remote_fs $network
# Short-Description: Starts/stop the CherryPy daemon
# Description: CherryPy is a pythonic, object-oriented web framework
### END INIT INFO

# Source function library.
. /etc/rc.d/init.d/functions

if [ -f /etc/sysconfig/cherryd ]; then
        . /etc/sysconfig/cherryd
fi

exec=${CHERRYD-/usr/bin/cherryd}
prog=cherryd
pidfile=${PIDFILE-/var/run/cherryd.pid}
lockfile=${LOCKFILE-/var/lock/subsys/cherryd}
RETVAL=0

start() {
    [ -x $exec ] || exit 5
    echo -n $"Starting $prog: "
    daemon $exec --daemon --pidfile=${pidfile} $OPTIONS
    retval=$?
    echo
    [ $RETVAL = 0 ] && touch ${lockfile}
    return $RETVAL
}

stop() {
    echo -n $"Stopping $prog: "
    killproc -p ${pidfile} $exec
	RETVAL=$?
	echo
	[ $RETVAL = 0 ] && rm -f ${lockfile} ${pidfile}

}

restart() {
    stop
    start
}

reload() {
    restart
}

force_reload() {
    restart
}

rh_status() {
    # run checks to determine if the service is running or use generic status
    status $prog
}

rh_status_q() {
    rh_status >/dev/null 2>&1
}


case "$1" in
    start)
        rh_status_q && exit 0
        $1
        ;;
    stop)
        rh_status_q || exit 0
        $1
        ;;
    restart)
        $1
        ;;
    reload)
        rh_status_q || exit 7
        $1
        ;;
    force-reload)
        force_reload
        ;;
    status)
        rh_status
        ;;
    condrestart|try-restart)
        rh_status_q || exit 0
        restart
        ;;
    *)
        echo $"Usage: $0 {start|stop|status|restart|condrestart|try-restart|reload|force-reload}"
        exit 2
esac
exit $?
