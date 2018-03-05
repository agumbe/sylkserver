import datetime

from application.python import Null
from application.python.types import Singleton
from application.notification import IObserver, NotificationCenter
from sylk.applications import ApplicationLogger
from zope.interface import implements
from sylk.db.schema import Call
#from sylk.utils import dump_object_member_vars, dump_object_member_funcs

log = ApplicationLogger(__package__)

'''

'''
class CallData(object):
    """This class has only one instance"""
    __metaclass__ = Singleton
    implements(IObserver)

    def __init__(self):
        self.init_observers()

    def init_observers(self):
        log.info("CallData init_observers")
        notification_center = NotificationCenter()
        notification_center.add_observer(self, name='DataCallUpdate')

    def handle_notification(self, notification):
        log.info("CallData got notification ")
        log.info("CallData got notification %r" % notification.name)
        handler = getattr(self, '_NH_%s' % notification.name, Null)
        handler(notification)

    def _NH_DataCallUpdate(self, notification):
        log.info("incoming _NH_DataCallUpdate")
        session = notification.data.session
        status = notification.data.status
        log.info("incoming _NH_DataCallUpdate call_id %r, status %r" % (session.call_id, status))
        from_uri = str(session.remote_identity.uri)
        log.info("from_uri is %r" % str(from_uri))
        to_uri = str(session.request_uri)
        log.info("to_uri is %r" % str(to_uri))

        if status == 'init':
            call_obj = Call()
            call_obj.sip_call_id = session.call_id
            call_obj.from_uri = from_uri
            call_obj.to_uri = to_uri
            call_obj.direction = session.direction
            call_obj.save()
        elif status == 'reject':
            call_obj = Call.objects.get(sip_call_id = session.call_id)
            call_obj.status = 'reject'
            call_obj.end_time = datetime.datetime.utcnow()
            call_obj.save()




