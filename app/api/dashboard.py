from flask import Blueprint, jsonify

from ..services.dashboard_service import get_dashboard_data
from ..utils.decorators import roles_required

dashboard_bp = Blueprint("dashboard", __name__)


@dashboard_bp.get("/dashboard")
@roles_required("admin", "agent")
def dashboard():
    data = get_dashboard_data()
    return jsonify(dashboard=data)