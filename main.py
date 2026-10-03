from fastapi import FastAPI

app=FastAPI(title="First API") 

@app.get("/")
def home():
    return {'message':'Hello World from FastAPI'}