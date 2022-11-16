import mlflow 
import uvicorn
import json
import pandas as pd 

from pydantic import BaseModel
from typing import Literal, List, Union
from fastapi import FastAPI, File, UploadFile
import boto3

mlflow.set_tracking_uri("https://getaround-model-server.herokuapp.com/")

tag_metadata = [
    {
        "name": "Price of a rental predictor",
        "description": "Use the predict endpoint to get your price for a rental"
    }
]

app = FastAPI(
    title="GetAround API helping you to know your price for a rental",
    openapi_tags=tag_metadata
)


@app.get("/")
async def index():

    message = "Welcome to this GetAround API. Here, you can calculate the price of a rental for a car based on the previous rentals. Check /docs to learn more and make predictions`"

    return message

class PredictionFeatures(BaseModel):
    model_key: str = "Citroën"
    mileage: int = 90401
    engine_power: int = 135
    fuel: str = "diesel"
    paint_color: str = "grey"
    car_type: str = "convertible"
    private_parking_available: bool = True
    has_gps: bool = True
    has_air_conditioning: bool = False
    automatic_car: bool = False
    has_getaround_connect: bool = True
    has_speed_regulator: bool = True
    winter_tires: bool = True


@app.post("/Predict" , tags=['Predictor'])
async def predict(predictionFeatures: PredictionFeatures):
    """
    Make a rental price prediction with the rental and car informations
    """

    price_rental_per_day = pd.DataFrame(dict(predictionFeatures), index=[0])

    # Log model from mlflow 
    logged_model = 'runs:/4342329ee93b4a7b8b4fb93c7662e555/pricing_cars_predictor'

    # Load model as a PyFuncModel.
    loaded_model = mlflow.pyfunc.load_model(logged_model)
    prediction = loaded_model.predict(price_rental_per_day)

    # Format response
    response = {"prediction": prediction.tolist()[0]}
    return response



if __name__=="__main__":
    uvicorn.run(app, host="0.0.0.0", port=4010)