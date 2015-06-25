"""
bdosoa - Subscription Versions syncing
"""

import cherrypy
import json

from bdosoa.model import (ServiceProviderGateway, SubscriptionVersion,
                          SyncClient, SyncTask)
from bdosoa.model.meta import NoResultFound


# noinspection PyPep8Naming,PyMethodMayBeStatic
class Sync(object):
    """Process Sync requests"""

    @cherrypy.expose
    def index(self, spid, token, task=None):
        """Receive Sync or Subscription Version requests

        :param str spid: Service Provider ID
        :param str token: access token
        :param str task: Sync Task ID
        """

        # Get handler based on request method
        handler = getattr(self, cherrypy.request.method.upper(), None)
        cherrypy.log.error('Got handler: {0!r}'
                           .format(handler), 'SYNC', 10)

        # Return allowed methods if handler not found
        if handler is None:
            cherrypy.response.headers['Allow'] = \
                [m for m in dir(self) if m.isupper()]
            raise cherrypy.HTTPError(405)

        # Check access credentials
        try:
            cherrypy.request.sync_client = cherrypy.request.db \
                .query(SyncClient) \
                .join(ServiceProviderGateway) \
                .filter(
                    ServiceProviderGateway.service_provider_id == spid,
                    SyncClient.token == token,
                    SyncClient.enabled,
                ).one()

        except NoResultFound:
            raise cherrypy.HTTPError(403)

        # Get tasks
        if task:
            if isinstance(task, (str, unicode)):
                task = [task]

            tasks = cherrypy.request.sync_client.tasks.filter(
                SyncTask.id.in_(task))

            if tasks.count() < len(task):
                raise cherrypy.HTTPError(404)

        else:
            tasks = []

        # Process request
        cherrypy.response.headers['Content-Type'] = 'application/json'
        return handler(tasks)

    def GET(self, tasks=None):
        """Get Sync Tasks

        :param list tasks: optional task to query
        """

        if tasks:
            cherrypy.log.error('Processing tasks: {0}'
                               .format([t.id for t in tasks]), 'SYNC', 10)
            result = [
                dict((k, v) for (k, v) in s.__dict__.items()
                     if not k.startswith('_'))
                for s in cherrypy.request.db.query(SubscriptionVersion).filter(
                    SubscriptionVersion.id.in_([t.subscription_version_id
                                                for t in tasks])
                )
            ]
            cherrypy.log.error('Sending subscription version list: {0}'.format(
                [s['subscription_version_id'] for s in result]), 'SYNC', 10)

        else:
            result = [
                t.id for t in cherrypy.request.sync_client.tasks.limit(10000)
            ]
            cherrypy.log.error('Sending task list: {0}'
                               .format(result), 'SYNC', 10)

        return json.dumps(result, default=lambda o: str(o))

    def DELETE(self, tasks):
        """Delete Sync Tasks

        :param SyncTask tasks: task to delete
        """

        if not tasks:
            raise cherrypy.HTTPError(404)

        # Delete task
        cherrypy.log.error('Deleting tasks: {0}'
                           .format([t.id for t in tasks]), 'SYNC', 10)
        tasks.delete(synchronize_session=False)
