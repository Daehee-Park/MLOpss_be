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

@app.post("/get/chart")
async def get_chart_data(request: Request):
    data = await request.json()
    df = pd.DataFrame(data['data'])

    # List to store base64-encoded images
    images_base64 = []

    # Generate a separate plot for each numeric column
    for col in df.columns:
        plt.figure(figsize=(8, 6))
        ax = plt.gca()
        if pd.api.types.is_numeric_dtype(df[col]):
            sns.kdeplot(df[col], fill=True, ax=ax)
            skewness = df[col].skew()
            ax.set_title(f'Distribution of {col}', fontsize=22)
            ax.set_xlabel(col, fontsize=18)
            ax.set_ylabel('Density', fontsize=18)
            ax.annotate(f'Skew: {skewness:.2f}', xy=(0.95, 0.9), xycoords='axes fraction',
                    fontsize=12, ha='right',
                    bbox=dict(boxstyle='round,pad=0.5', edgecolor='black', facecolor='white'))
            
            mean_value = df[col].mean()
            ax.axvline(mean_value, color='black', linestyle='--')
        else:
            print(f'{col} is categorical')
            value_counts = df[col].value_counts(normalize=True) * 100
            sns.barplot(x=value_counts.index, y=value_counts.values, ax=ax, palette='Set2')
            ax.set_title(f'Distribution of {col}', fontsize=22)
            ax.set_xlabel(col, fontsize=18)
            ax.set_ylabel('Percentage (%)', fontsize=18)
            for p in ax.patches:
                ax.annotate(f"{p.get_height():.1f}%", (p.get_x() + p.get_width() / 2., p.get_height()),
                            ha='center', va='center', fontsize=10, color='black', xytext=(0, 5),
                            textcoords='offset points')
            
        # Convert the plot to a base64 string
        buffer = BytesIO()
        plt.savefig(buffer, format='png')
        buffer.seek(0)
        image_png = buffer.getvalue()
        buffer.close()
        image_base64 = base64.b64encode(image_png)
        image_str = image_base64.decode('utf-8')

        # Add the base64 string to the list
        images_base64.append(image_str)

        # Clear the figure after each plot
        plt.clf()

    # Return list of base64 strings
    return JSONResponse(content={"charts": images_base64})