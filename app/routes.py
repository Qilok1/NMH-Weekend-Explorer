from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app import app, db
from app.models import Activity, Participation

@app.route("/my-activities")
@login_required
def my_activities():
    """Show activities the current user is hosting and joining."""
    hosted = Activity.query.filter_by(creator_id=current_user.id).all()

    joined = (
        Activity.query.join(Participation)
        .filter(Participation.user_id == current_user.id)
        .all()
    )

    # SQL like Ethan wanted
    def to_dict(a, status=""):
        return {
            "id": a.id,
            "title": a.title,
            "description": a.description or "",
            "date": a.date.strftime("%Y-%m-%d") if a.date else "",
            "time": a.time.strftime("%H:%M") if a.time else "",
            "location": a.location_name or "",
            "current_participants": len(a.participants),
            "max_participants": a.max_participants,
            "is_pending": getattr(a, "is_pending", False),
            "is_full": a.max_participants
                        and len(a.participants) >= a.max_participants,
            "status": status,
        }

    hosted_dicts = [to_dict(a, "host") for a in hosted]
    joined_dicts = [to_dict(a, "joined") for a in joined]

    return render_template(
        "my_activities.html",
        hosted_activities=hosted_dicts,
        joined_activities=joined_dicts,
    )


@app.route("/activities/<int:activity_id>/delete", methods=["POST"])
@login_required
def delete_activity(activity_id):
    """Delete an activity if the current user is the creator or an admin."""
    activity = Activity.query.get_or_404(activity_id)

    if activity.creator_id != current_user.id and not current_user.is_admin:
        flash("You do not have permission to delete this activity.", "warning")
        return redirect(url_for("my_activities"))

    # Delete related Participation rows first
    Participation.query.filter_by(activity_id=activity.id).delete()
    db.session.delete(activity)
    db.session.commit()
    flash("Activity deleted.", "success")
    return redirect(url_for("my_activities"))
