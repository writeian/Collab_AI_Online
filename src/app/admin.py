from flask import Blueprint, render_template, Response
from src.app.access_control import require_admin
from src.app import db

admin = Blueprint("admin", __name__)


@admin.route("/admin")
@require_admin
def dashboard():
    from src.models import User, Room, Chat, Message
    from flask import current_app

    try:
        totals = {
            "users": db.session.query(User).count(),
            "rooms": db.session.query(Room).count(),
            "chats": db.session.query(Chat).count(),
            "messages": db.session.query(Message).count(),
        }
        return render_template("admin_analytics.html", totals=totals)
    except Exception as e:
        current_app.logger.exception(f"/admin render error: {e}")
        # Minimal fallback to avoid 500
        totals = {"users": 0, "rooms": 0, "chats": 0, "messages": 0}
        return render_template("admin_analytics.html", totals=totals)


@admin.route("/admin/users")
@require_admin
def users_report():
    from src.models import User, Chat
    from sqlalchemy import func
    from flask import current_app

    try:
        rows = (
            db.session.query(
                User.id,
                User.username,
                User.email,
                User.display_name,
                func.count(Chat.id).label("total_chats"),
                func.max(Chat.created_at).label("last_chat_created_at"),
            )
            .outerjoin(Chat, Chat.created_by == User.id)
            .group_by(User.id, User.username, User.email, User.display_name)
            .order_by(func.count(Chat.id).desc())
            .all()
        )

        formatted = []
        for r in rows:
            last_dt = r[5]
            last_str = last_dt.strftime('%Y-%m-%d %H:%M') if last_dt else ''
            formatted.append({
                'user_id': r[0],
                'username': r[1],
                'email': r[2],
                'display_name': r[3],
                'total_chats': r[4] or 0,
                'last_chat_created_at': last_str,
            })

        return render_template("admin_users.html", users_rows=formatted)
    except Exception as e:
        current_app.logger.exception(f"/admin/users render error: {e}")
        # Fallback to CSV if rendering fails
        return users_report_csv()


@admin.route("/admin/users.csv")
@require_admin
def users_report_csv():
    from src.models import User, Chat
    from sqlalchemy import func
    import csv
    from io import StringIO

    rows = (
        db.session.query(
            User.id,
            User.username,
            User.email,
            User.display_name,
            func.count(Chat.id).label("total_chats"),
            func.max(Chat.created_at).label("last_chat_created_at"),
        )
        .outerjoin(Chat, Chat.created_by == User.id)
        .group_by(User.id, User.username, User.email, User.display_name)
        .order_by(func.count(Chat.id).desc())
        .all()
    )

    output = StringIO()
    writer = csv.writer(output)
    writer.writerow(["user_id", "username", "email", "display_name", "total_chats", "last_chat_created_at"])
    for r in rows:
        writer.writerow([
            r[0], r[1], r[2], r[3], r[4] or 0, (r[5].isoformat() if r[5] else "")
        ])

    csv_data = output.getvalue()
    return Response(
        csv_data,
        mimetype="text/csv",
        headers={
            "Content-Disposition": "attachment; filename=users_chats_report.csv"
        },
    )


