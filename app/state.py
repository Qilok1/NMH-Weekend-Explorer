hosted_activities: List[dict] = []
joined_activities: List[dict] = []

def load_my_activities(self):
    """Populate hosted_activities and joined_activities for the current user."""
    if not self.is_authenticated or self.current_user_id is None:
        self.hosted_activities = []
        self.joined_activities = []
        return

    db = self.get_db()
    try:
        hosted = db.query(Activity).filter_by(
            creator_id=self.current_user_id
        ).all()

        joined = (
            db.query(Activity)
            .join(Participation)
            .filter(Participation.user_id == self.current_user_id)
            .all()
        )

        def serialize(a):
            return {
                "id": a.id,
                "title": a.title,
                "description": a.description or "",
                "date": str(a.date),
                "time": str(a.time),
                "location_name": a.location_name,
                "max_participants": a.max_participants,
            }

        self.hosted_activities = [serialize(a) for a in hosted]
        self.joined_activities = [serialize(a) for a in joined]
    finally:
        db.close()

def delete_activity(self, activity_id: int):
    """Delete an activity owned by the current user or by admin."""
    if not self.is_authenticated:
        self.message = "You must be logged in to delete an activity."
        self.message_type = "error"
        return

    db = self.get_db()
    try:
        activity = db.query(Activity).get(activity_id)
        if not activity:
            self.message = "Activity not found."
            self.message_type = "error"
            return

        if activity.creator_id != self.current_user_id and not self.is_admin:
            self.message = "You do not have permission to delete this activity."
            self.message_type = "warning"
            return

        db.query(Participation).filter_by(activity_id=activity_id).delete()
        db.delete(activity)
        db.commit()
        self.message = "Activity deleted."
        self.message_type = "success"
        self.load_my_activities()
    except Exception as e:
        db.rollback()
        self.message = f"Error deleting activity: {str(e)}"
        self.message_type = "error"
    finally:
        db.close()
