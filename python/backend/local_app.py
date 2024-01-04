import uvicorn
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import OneHotEncoder
import joblib
import pickle

app = FastAPI()
origins = [
    "http://localhost",
    "http://localhost:8000",
    "http://127.0.0.1",
    "http://127.0.0.1:8000",
    "http://0.0.0.0:8000"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)


# 读取 CSV 数据并转换为 Pandas DataFrame
file_path_csv = 'python/ljt_data/mock/jobs_mock2.csv'  # 请替换为你的文件路径
df = pd.read_csv(file_path_csv)

# 将分类变量进行独热编码
categorical_features = ['position', 'workplace', 'education']
encoder = OneHotEncoder(sparse=False)
encoded_data = encoder.fit_transform(df[categorical_features])

# 创建编码后的 DataFrame
encoded_df = pd.DataFrame(encoded_data, columns=encoder.get_feature_names(categorical_features))

# 合并编码后的 DataFrame 和 原始 DataFrame
df_encoded = pd.concat([df, encoded_df], axis=1)

# 定义特征向量列和目标列
feature_columns = encoded_df.columns

@app.post("/submit")
async def handle_submit(request: Request):
    form_data = await request.form()
    input_data = [[form_data.get('input_pos'), form_data.get('input_region'), form_data.get('input_education')]]  # 输入岗位、地区、学历
    input_df = pd.DataFrame(input_data, columns=['position', 'workplace', 'education'])
    # 进行独热编码
    encoded_input_data = encoder.transform(input_df[categorical_features])
    encoded_input_df = pd.DataFrame(encoded_input_data, columns=encoder.get_feature_names(categorical_features))

    # 合并编码后的输入 DataFrame 和 原始输入 DataFrame
    input_df_encoded = pd.concat([input_df, encoded_input_df], axis=1)
    # 加载模型
    model = joblib.load('python/ljt_data/model.pkl')
    # 使用模型进行预测
    prediction = model.predict(input_df_encoded[feature_columns])

    # 打印预测结果

    return {"salary": prediction[0]}


@app.post("/predict")
async def predict(request:Request):
    form_data = await request.form()


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8066)
