from typing import Union
from fastapi import FastAPI
import requests

app=FastAPI()
@app.get("/")
def read_root():
    return {"welcome":"a Active Service Mesh as Code (ASMaC)"}

@app.get("/categories")
def get_categories():
    pass

@app.get("/objects")
def get_objects():
    pass

@app.get("/objects/{alias}")
def get_objects_by_alias(alias:str):
    pass

@app.post("/publish")
def publish():
    pass