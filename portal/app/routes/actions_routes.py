from flask import Blueprint, render_template

actions_bp = Blueprint('actions', __name__)

@actions_bp.route('/dashboard')
def dashboard():
    actions_list = [
        {
            "id": "abcd",
            "name": "Calculator",
            "apis": 2,
            "gpts": 4,
            "uses": 27,
            "last_updated": "3 hours ago",
            "sparkline_data": "0,48 60,24 120,36 180,40 240,24 300,0"
        },
        {
            "id": "efgh",
            "name": "PDF tools",
            "apis": 0,
            "gpts": 0,
            "uses": 0,
            "last_updated": "6 days ago",
            "sparkline_data": "0,48 60,48 120,48 180,48 240,48 300,48"
        },
    ]
    return render_template('dashboard.html', actions_list=actions_list)
