# Libraries import

import pandas as pd
import numpy as np
import os
import mlflow
from mlflow.models.signature import infer_signature


from sklearn.model_selection import train_test_split
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import  OneHotEncoder, StandardScaler
from sklearn.compose import ColumnTransformer
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score
from sklearn.linear_model import Ridge, Lasso
from sklearn.model_selection import cross_val_score, GridSearchCV
from sklearn.pipeline import Pipeline


import time


# Set your variables for your environment
EXPERIMENT_NAME="get_around_expirement"

# Instanciate your experiment
client = mlflow.tracking.MlflowClient()


APP_URI = "https://getaround-model-server.herokuapp.com/"

mlflow.set_tracking_uri(APP_URI)


# Set experiment's info 
mlflow.set_experiment(EXPERIMENT_NAME)

# Get our experiment info
experiment = mlflow.get_experiment_by_name(EXPERIMENT_NAME)
#run = client.create_run(experiment.experiment_id) # Creates a new run for a given experiment


#dataset import

print("Loading dataset...")
data = pd.read_csv("get_around_pricing_project.csv")
print("...Done.")
print()

# Separating the target and variables Y from features X

print("Separating labels from features...")

features_list = [ 'model_key', 'mileage', 'engine_power', 'fuel',
       'paint_color', 'car_type', 'private_parking_available', 'has_gps',
       'has_air_conditioning', 'automatic_car', 'has_getaround_connect',
       'has_speed_regulator', 'winter_tires']
       
target_variable =  'rental_price_per_day'

X = data.loc[:,features_list]
Y = data.loc[:,target_variable]
print()
print("...Operation done")

# Divide dataset Train set & Test set 

print("Dividing into train and test sets...")

X_train, X_test, Y_train, Y_test = train_test_split(X, Y, test_size=0.3, random_state= 20)

print()
print("...Done.")
print()

# Encoding categorical features and standardizing numerical features


categorical_features = [ 'model_key', 'fuel',
       'paint_color', 'car_type', 'private_parking_available', 'has_gps',
       'has_air_conditioning', 'automatic_car', 'has_getaround_connect',
       'has_speed_regulator', 'winter_tires']

numerical_features = [ 'mileage', 'engine_power']


numeric_transformer = StandardScaler()
categorical_transformer = OneHotEncoder(drop='first',handle_unknown='ignore')

# Time execution
start_time = time.time()

#Calling autolog
mlflow.sklearn.autolog()

featureencoder = ColumnTransformer(
    transformers=[
        ('cat', categorical_transformer, categorical_features),    
        ('num', numeric_transformer, numerical_features)
        ]
    )

model = Pipeline(steps=[("Preprocessing", featureencoder),
                            ("Regressor", LinearRegression())
                            ])

    # Log experiment to MLFlow
with mlflow.start_run():
        model.fit(X_train, Y_train)
        predictions = model.predict(X_train)

    # Log model seperately to have more flexibility on setup 
        mlflow.sklearn.log_model(
            sk_model=model,
            artifact_path="pricing_cars_predictor",
            registered_model_name="pricing_cars_linearReg",
            signature=infer_signature(X_train, predictions)
            )

        print("...Done!")
        print(f"---Total training time: {time.time()-start_time}")