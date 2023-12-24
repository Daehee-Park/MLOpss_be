from fastapi import FastAPI, UploadFile, File, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import base64
from io import BytesIO

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True
)

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.post("/upload")
async def upload_data(file: UploadFile = File(...)):
    df = pd.read_csv(file.file)
    # Convert the DataFrame to a dictionary
    data = df.to_dict(orient="records")
    return {"data": data}

@app.post("/get/chartData")
async def get_chart_data(request: Request):
    data = await request.json()
    df = pd.DataFrame(data['data'])

    # Create a plot
    plt.figure(figsize=(10, 6))
    for col in df.columns:
        sns.kdeplot(df[col], shade=True)
    
    # Convert plot to a base64 string
    buffer = BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    image_png = buffer.getvalue()
    buffer.close()
    image_base64 = base64.b64encode(image_png)
    image_str = image_base64.decode('utf-8')

    # Return base64 string
    return JSONResponse(content={"chart": image_str})