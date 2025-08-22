# utils/scoring.py
from datetime import date, timedelta
from models import DailyLog, POINTS_MAPPING, db
from sqlalchemy import func

# 1. Daily Score
def calculate_daily_score(user, log_date=None):
    """Calculate total points for a user on a given date."""
    if not log_date:
        log_date = date.today()

    logs = DailyLog.query.filter_by(user_id=user.id, log_date=log_date).all()
    return sum(log.get_points() for log in logs)


# 2. Overall Score
def calculate_overall_score(user):
    """Total points accumulated across all days."""
    logs = DailyLog.query.filter_by(user_id=user.id).all()
    return sum(log.get_points() for log in logs)


# 3. Best Daily Score Till Now
def best_daily_score(user):
    """Return best (max) daily score user has achieved."""
    scores = (
        db.session.query(DailyLog.log_date, func.sum().label("total_points"))
        .with_entities(DailyLog.log_date, func.sum(func.coalesce(func.nullif(func.replace(DailyLog.status, 'not_done', '0'), ''), 0)))
        .filter(DailyLog.user_id == user.id)
        .group_by(DailyLog.log_date)
        .all()
    )
    if not scores:
        return 0
    return max([sum(POINTS_MAPPING.get(log.status, 0) for log in DailyLog.query.filter_by(user_id=user.id, log_date=day).all()) for day, _ in scores])


# 4. Activity-Level Score
def calculate_activity_score(user, activity_id):
    """Cumulative score for a specific activity."""
    logs = DailyLog.query.filter_by(user_id=user.id, activity_id=activity_id).all()
    return sum(log.get_points() for log in logs)


# 5. Best & Worst Activities
def best_and_worst_activities(user):
    """Return best and worst performing activity names."""
    from models import Activity  # avoid circular import

    activities = (
        db.session.query(Activity, func.sum().label("total_points"))
        .join(DailyLog, DailyLog.activity_id == Activity.id)
        .filter(DailyLog.user_id == user.id)
        .group_by(Activity.id)
        .all()
    )

    if not activities:
        return None, None

    best = max(activities, key=lambda x: x[1])
    worst = min(activities, key=lambda x: x[1])

    return best[0].name, worst[0].name


# 6. Consistency Streaks
def streak_count(user):
    """Return longest streak of consecutive days user has logged something."""
    logs = (
        DailyLog.query.filter_by(user_id=user.id)
        .with_entities(DailyLog.log_date)
        .distinct()
        .order_by(DailyLog.log_date)
        .all()
    )
    dates = [l.log_date for l in logs]

    if not dates:
        return 0

    longest, current = 1, 1
    for i in range(1, len(dates)):
        if dates[i] == dates[i-1] + timedelta(days=1):
            current += 1
            longest = max(longest, current)
        else:
            current = 1
    return longest


# 7. Days Completed
def days_completed(user):
    return DailyLog.query.filter_by(user_id=user.id).with_entities(DailyLog.log_date).distinct().count()
