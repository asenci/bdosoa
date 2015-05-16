"""
bdosoa - Subscription Versions syncing
"""

import cherrypy
import json

from bdosoa.model import SubscriptionVersion, SyncClient, SyncTask
from bdosoa.model.meta import NoResultFound


# noinspection PyPep8Naming,PyMethodMayBeStatic
class Sync(object):
    """Process Sync requests"""

    @cherrypy.expose
    def index(self, spid, token, task_id=None):
        """Receive Sync or Subscription Version requests

        :param str spid: Service Provider ID
        :param str token: access token
        :param str task_id: Sync Task ID
        """

        # Get handler based on request method
        handler = getattr(self, cherrypy.request.method.upper(), None)

        # Return allowed methods if handler not found
        if handler is None:
            cherrypy.response.headers['Allow'] = \
                [m for m in dir(self) if m.isupper()]
            raise cherrypy.HTTPError(405)

        # Check access credentials
        try:
            cherrypy.request.sync_client = \
                cherrypy.request.db.query(SyncClient).filter_by(
                    spid=spid, token=token, enabled=True).one()

        except NoResultFound:
            raise cherrypy.HTTPError(403)

        # Check if a task exists for the specified task_id
        if task_id:
            try:
                task = cherrypy.request.sync_client.tasks.filter_by(
                    id=task_id).one()

            except NoResultFound:
                raise cherrypy.HTTPError(404)

        else:
            task = None

        # Process request
        cherrypy.response.headers['Content-Type'] = 'application/json'
        return handler(task)

    def GET(self, task=None):
        """Get Sync Tasks

        :param SyncTask task: optional task to query
        """

        if task:
            sv = cherrypy.request.db.query(SubscriptionVersion).get(
                task.subscriptionversion_id)
            return json.dumps(dict((k, v) for (k, v) in sv.__dict__.items()
                                   if not k.startswith('_')),
                              default=lambda o: str(o))

        result = []

        for task in cherrypy.request.sync_client.tasks.limit(1000):
            sv = cherrypy.request.db.query(SubscriptionVersion).get(
                task.subscriptionversion_id)

            sv_dict = dict(
                (k, v) for (k, v) in sv.__dict__.items()
                if not k.startswith('_')
            )

            result.append({
                'task_id': task.id,
                'subscription_version': sv_dict,
            })

        return json.dumps(result, default=lambda o: str(o))

    def DELETE(self, task=None):
        """Delete Sync Tasks

        :param SyncTask task: task to delete
        """

        if task is None:
            raise cherrypy.HTTPError(404)

        # Delete task
        cherrypy.request.db.delete(task)
