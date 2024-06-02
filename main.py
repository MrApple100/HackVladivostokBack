import uvicorn
import asyncio
import fastapi
from fastapi import FastAPI, File, UploadFile, status, Header, Request, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
import pkg_resources
from analysis import RzdParser
from fastapi.middleware.cors import CORSMiddleware
app = FastAPI()


origins = [
    "http://localhost.tiangolo.com",
    "https://localhost.tiangolo.com",
    "http://localhost",
    "http://localhost:8080",
    "*"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


static_dir = pkg_resources.resource_filename(__name__, 'static')
app.mount("/_next/static", StaticFiles(directory=static_dir), name="static")

rzd = RzdParser(static_dir+"/dataset.xlsx")

@app.get("/")
async def get_page():
    html_content = ""
    with open(f"{static_dir}/app/index.html", 'r') as f:
        html_content = f.read()
    return HTMLResponse(content=html_content, status_code=200)

@app.get("/{page}")
async def get_page_new(page):
    html_content = ""
    with open(f"{static_dir}/app/{page}.html", 'r') as f:
        html_content = f.read()
    return HTMLResponse(content=html_content, status_code=200)

@app.post("/api/upload_file/")
async def upload(dataset: UploadFile = File(...)):
    with open(static_dir+"/dataset_1.xlsx",'wb+') as f:
        f.write(dataset.file.read())
        f.close()
    rzd.__init__(static_dir+"/dataset_1.xlsx")
    
    return {"status":"ok"}

@app.get("/api/get_values")
async def get_values(name=None):
    return rzd.get_values(name)

@app.get("/api/get_vehicle_division_info")
async def get_vehicle_division_info(name):
    return rzd.get_vehicle_division_info(name)

@app.get("/api/get_polygon_info")
async def get_polygon_info(name):
    return rzd.get_polygon_info(name)

@app.get("/api/get_vehicle_info")
async def get_vehicle_info(name):
    return rzd.get_vehicle_info(name)

@app.get("/api/get_vehicle_transfer_recommendations")
async def get_vehicle_transfer_recommendations(name=None):
    return rzd.get_vehicle_transfer_recommendations(name)

@app.get("/api/calculate_efficiency_rating_division")
async def calculate_efficiency_rating_division(name=None):
    return rzd.calculate_efficiency_rating_division(name)

@app.get("/api/ai_efficiency_rating_division")
async def ai_efficiency_rating_division(name=None):
    return rzd.ai_efficiency_rating_division(name)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8888, reload=False)