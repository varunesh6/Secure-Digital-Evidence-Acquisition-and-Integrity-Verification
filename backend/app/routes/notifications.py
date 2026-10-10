from flask import Blueprint, jsonify
from flask_login import current_user, login_required

from app.models import Notification

notifications_bp = Blueprint("notifications", __name__)


@notifications_bp.route("/notifications", methods=["GET"])
@login_required
def list_notifications():
    records = Notification.query.filter_by(user_id=current_user.id).order_by(Notification.created_at.desc()).all()
    return jsonify({"notifications": [{
        "id": n.id,
        "notification_type": n.notification_type,
        "message": n.message,
        "linked_record": n.linked_record,
        "is_read": n.is_read,
        "created_at": n.created_at.isoformat(),
    } for n in records]})
