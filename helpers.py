from constants import Sex, ActivityLevel, WeightLoseGoal
from datetime import date


def profile_response(user, profile):
    return {
        "name": user.name,
        "email": user.email,
        "username": user.username,
        "profile_picture_url": profile.profile_picture_url,
        "age": profile.age,
        "height": profile.height,
        "sex": profile.sex,
        "start_weight": profile.start_weight,
        "goal_weight": profile.goal_weight,
        "weight_loss_goal": profile.weight_loss_goal,
        "target_date": profile.target_date,
        "activity_level": profile.activity_level
}

def calculate_age(birth_date):
    today = date.today()
    age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
    return age

def calculate_calories(sex, weight, height, age, activity_level, weight_lose_goal): 
    weight_kg = weight / 2.20462

    height_cm = height * 2.54

    if sex == Sex.MALE:
        bmr = (10 * weight_kg) + (6.25 * height_cm) - (5 * age) + 5
    else:
        bmr = (10 * weight_kg) + (6.25 * height_cm) - (5 * age) - 161
        
    multipliers = {
        ActivityLevel.SEDENTARY: 1.2,
        ActivityLevel.LIGHTLY_ACTIVE: 1.375,
        ActivityLevel.MODERATELY_ACTIVE: 1.55,
        ActivityLevel.VERY_ACTIVE: 1.725,
        ActivityLevel.EXTRA_ACTIVE: 1.9
    }
    tdee = bmr * multipliers.get(activity_level, 1.2)

    deficit = 500 if weight_lose_goal == WeightLoseGoal._1lb_per_week else 1000
    return tdee - deficit