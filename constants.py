import enum

# Define an enumeration for activity levels
class ActivityLevel(enum.Enum):
    SEDENTARY = "Sedentary"
    LIGHTLY_ACTIVE = "Lightly Active"
    MODERATELY_ACTIVE = "Moderately Active"
    VERY_ACTIVE = "Very Active"
    EXTRA_ACTIVE = "Extra Active"

# Define an enumeration for meal types
class Meals(enum.Enum):
    BREAKFAST = "Breakfast"
    LUNCH = "Lunch"
    DINNER = "Dinner"
    SNACK = "Snack"

class Sex(enum.Enum):
    MALE = "Male"
    FEMALE = "Female"

class WeightLoseGoal(enum.Enum):
    _1lb_per_week = "1lb per week"
    _2lb_per_week = "2lb per week"