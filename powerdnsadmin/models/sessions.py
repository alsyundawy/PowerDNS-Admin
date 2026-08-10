import itertools
from datetime import datetime, timezone

from flask import current_app
from sqlalchemy import or_
from sqlalchemy.exc import SQLAlchemyError

from .base import db
from .setting import Setting

# Counts the requests served by this worker so the reaper can run on a
# fraction of them instead of on every single request.
_cleanup_request_counter = itertools.count()


def _naive_utcnow():
    """Current UTC time as a naive datetime.

    Flask-Session persists ``datetime.utcnow()`` values, so comparisons must
    use naive UTC too. ``datetime.utcnow()`` itself is deprecated from Python
    3.12 onwards, hence the timezone-aware conversion.
    """
    return datetime.now(timezone.utc).replace(tzinfo=None)


class Sessions(db.Model):
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.String(255), index=True, unique=True)
    data = db.Column(db.BLOB)
    expiry = db.Column(db.DateTime)

    def __init__(self,
                 id=None,
                 session_id=None,
                 data=None,
                 expiry=None):
        self.id = id
        self.session_id = session_id
        self.data = data
        self.expiry = expiry

    def __repr__(self):
        return '<Sessions {0}>'.format(self.id)

    @staticmethod
    def clean_up_expired_sessions():
        """Remove every stale row from the server-side session store.

        Flask-Session stores naive UTC expiry timestamps and treats a row
        without an expiry as already expired, so both cases are reaped here.
        """
        try:
            db.session.query(Sessions).filter(
                or_(Sessions.expiry.is_(None),
                    Sessions.expiry < _naive_utcnow())
            ).delete(synchronize_session=False)
            db.session.commit()
        except SQLAlchemyError as e:
            db.session.rollback()
            current_app.logger.error(
                'Cannot clean up expired sessions. Error: {0}'.format(e))
            return False
        return True


def clean_up_expired_sessions_if_due():
    """Reap stale sessions, throttled to one run every N requests.

    This is called from every blueprint's ``before_request`` hook. Only the
    SQLAlchemy backend keeps its sessions in the application database; the
    other backends expire their own records.
    """
    try:
        interval = int(current_app.config.get('SESSION_CLEANUP_N_REQUESTS', 100))
    except (TypeError, ValueError):
        interval = 100
    if interval < 1:
        interval = 1

    # Cheap check first so the settings lookup below is not done per request.
    if next(_cleanup_request_counter) % interval:
        return

    if Setting().get('session_type') != 'sqlalchemy':
        return

    Sessions.clean_up_expired_sessions()
