from fastapi import APIRouter, Depends, HTTPException
from database import get_db, AsyncSession
from security import get_current_user
import openfoodfacts
from requests.exceptions import RequestException
from schemas import LogFood, FoodLogResponse, EditFoodEntry
from models import FoodLog
from sqlalchemy import select

food_router = APIRouter(prefix="/log-food", dependencies=[Depends(get_current_user)])

api = openfoodfacts.API(user_agent="Shredly/1.0")

@food_router.get("/food-search")
async def get_food_item(search: str):
    try:
        food_item = api.product.text_search(search)
        if not food_item["products"]:
            raise HTTPException(status_code=404, detail="Food item not found.")
        foods = [{
        "food_name": item.get("product_name"),
        "serving_size": item.get("serving_size", 0), 
        "calories": round(item.get("nutriments", {}).get("energy-kcal_100g",0), 2),
        "protein": round(item.get("nutriments", {}).get("proteins_100g", 0), 2),
        "carbs": round(item.get("nutriments", {}).get("carbohydrates_100g", 0),2),
        "fat": round(item.get("nutriments", {}).get("fat_100g", 0), 2),
        "sugar": round(item.get("nutriments", {}).get("sugars_100g", 0), 2)
        } for item in food_item["products"]]
        return foods
    except RequestException:
        raise HTTPException(detail="Server error while fetching food data", status_code=500)

@food_router.get("/food-scan/{barcode}")
async def get_food_by_barcode(barcode: str):
    try:
        food_item = api.product.get(barcode)
        print(food_item)
        if food_item is None:
            raise HTTPException(status_code=404, detail="Food item not found.")
        if not food_item.get("product"):
            raise HTTPException(status_code=404, detail="Food item not found.")
        product = food_item["product"]
        return {"food_name": product.get("product_name"),
        "serving_size": product.get("serving_size", 0),
        "calories": round(product.get("nutriments", {}).get("energy-kcal_100g",0), 2),
        "protein": round(product.get("nutriments", {}).get("proteins_100g", 0), 2),
        "carbs": round(product.get("nutriments", {}).get("carbohydrates_100g", 0),2),
        "fat": round(product.get("nutriments", {}).get("fat_100g", 0), 2),
        "sugar": round(product.get("nutriments", {}).get("sugars_100g", 0), 2) 
        }
    except RequestException:
        raise HTTPException(detail="Server error while fetching food data", status_code=500)
    

@food_router.post("/log-food")
async def log_food(food:LogFood, user = Depends(get_current_user), db: AsyncSession = Depends(get_db)):

    new_cal = (food.calories/100) * food.serving_size *food.number_of_servings
    new_protein = (food.protein/100) * food.serving_size *food.number_of_servings
    new_carbs = (food.carbs/100) * food.serving_size *food.number_of_servings
    new_fat = (food.fat/100) * food.serving_size *food.number_of_servings
    new_sugar = (food.sugar/100) * food.serving_size *food.number_of_servings

    food_log = FoodLog(
        user_id=user.id,
        food_name=food.food_name,
        serving_size=food.serving_size,
        number_of_servings=food.number_of_servings,
        date=food.date,
        meal_type=food.meal_type,
        calories=new_cal,
        protein=new_protein,
        carbs=new_carbs,
        fat=new_fat,
        sugar=new_sugar
    )
    db.add(food_log)
    await db.commit()
    await db.refresh(food_log)
    return FoodLogResponse.model_validate(food_log)

@food_router.patch("/food_log/edit/{food_id}", status_code=200, response_model=FoodLogResponse)
async def edit_food(food:EditFoodEntry, food_id: int, user = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    db_result = await db.execute(select(FoodLog).where(FoodLog.id == food_id).where(FoodLog.user_id == user.id))
    user_food_item = db_result.scalar_one_or_none()
    if not user_food_item:
        raise HTTPException(status_code=404, detail="Food Not found")
    for field in food.model_fields_set:
        if getattr(food, field) is not None:
            setattr(user_food_item, field, getattr(food, field))
    await db.commit()
    await db.refresh(user_food_item)
    return FoodLogResponse.model_validate(user_food_item)
    
@food_router.delete("/food_log/delete/{food_id}", status_code=204)
async def delete_food(food_id: int, user = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    db_result = await db.execute(select(FoodLog).where(FoodLog.id == food_id).where(FoodLog.user_id == user.id))
    user_food_item = db_result.scalar_one_or_none()
    if not user_food_item:
        raise HTTPException(status_code=404, detail="Food Entry not found")
    await db.delete(user_food_item)
    await db.commit()

@food_router.get("/food_log", status_code=200)
async def foods(user = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    db_result = await db.execute(select(FoodLog).where(FoodLog.user_id == user.id))
    food_list = db_result.scalars().all()
    food_entries = [FoodLogResponse.model_validate(item) for item in food_list]
    return food_entries