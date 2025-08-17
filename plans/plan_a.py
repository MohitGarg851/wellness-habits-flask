# -------------------------------
# Plan A: Starter Wellness Program
# -------------------------------

plan_name = "Plan A - Starter Wellness"

plan_name = "Plan A - Starter Wellness"

# thresholds
min_activities = 6
max_activities = 8
min_points = 60
max_points = None   # None = no upper limit

activities = [ 
    {
        "name": "Morning Walk",
        "level1": "10 min walk (5 pts)",
        "level2": "20 min walk (10 pts)",   # Recommended
        "level3": "30 min walk (15 pts)",
        "recommended": "L2",
    },
    {
        "name": "Yoga / Stretching",
        "level1": "5 min light stretch (5 pts)",
        "level2": "15 min yoga (10 pts)",   # Recommended
        "level3": "30 min yoga (15 pts)",
        "recommended": "L2",
    },
    {
        "name": "Sleep Hygiene",
        "level1": "Sleep 6 hrs (5 pts)",
        "level2": "Sleep 7 hrs (10 pts)",   # Recommended
        "level3": "Sleep 8+ hrs (15 pts)",
        "recommended": "L2",
    },
    {
        "name": "Screen-Free Time",
        "level1": "No screens 15 min before bed (5 pts)",
        "level2": "No screens 30 min before bed (10 pts)",   # Recommended
        "level3": "No screens 1 hr before bed (15 pts)",
        "recommended": "L2",
    },
    {
        "name": "Mindful Eating",
        "level1": "1 mindful meal (5 pts)",
        "level2": "2 mindful meals (10 pts)",   # Recommended
        "level3": "3 mindful meals (15 pts)",
        "recommended": "L2",
    },
    {
        "name": "Hydration",
        "level1": "Drink 1.5L water (5 pts)",
        "level2": "Drink 2L water (10 pts)",   # Recommended
        "level3": "Drink 3L water (15 pts)",
        "recommended": "L2",
    },
    {
        "name": "Cardio / Exercise",
        "level1": "10 min cardio/exercise (5 pts)",
        "level2": "20 min cardio/exercise (10 pts)",   # Recommended
        "level3": "30+ min cardio/exercise (15 pts)",
        "recommended": "L2",
    },
    {
        "name": "Healthy Dinner",
        "level1": "Dinner before 9 PM (5 pts)",
        "level2": "Dinner before 8 PM (10 pts)",   # Recommended
        "level3": "Light/early dinner before 7:30 PM (15 pts)",
        "recommended": "L2",
    }
]
