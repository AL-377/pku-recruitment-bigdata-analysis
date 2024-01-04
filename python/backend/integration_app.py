import os
import sys
from pyspark.sql import SparkSession
from fastapi import FastAPI, Request
from pyspark.ml.feature import StringIndexer, VectorAssembler
from pyspark.ml.feature import Tokenizer, StopWordsRemover, HashingTF, IDF, StringIndexer
import pandas as pd
from pyspark.ml.regression import LinearRegression
from pyspark.ml import Pipeline
from pyspark.ml import PipelineModel
from datetime import datetime,timedelta
from pyspark.sql import functions as F
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI
from pydantic import BaseModel
import uvicorn

# 初始化带有 UTF-8 设置和 Hive 支持的 Spark 会话
spark = SparkSession.builder \
    .appName("prediction") \
    .config("spark.driver.extraJavaOptions", "-Dfile.encoding=UTF-8") \
    .config("spark.executor.extraJavaOptions", "-Dfile.encoding=UTF-8") \
    .enableHiveSupport() \
    .getOrCreate()

# 创建FastAPI应用
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

# 预测薪资（回归接口）
@app.post("/predict_salary")
async def predict_salary(request: Request):
    form_data = await request.form()
    # Load trained model
    model_path = "hdfs://namenode:9000/model/regression"
    model = PipelineModel.load(model_path)
    input_data = [[form_data.get('input_pos'), form_data.get('input_region'), form_data.get('input_education')]]  # 输入岗位、地区、学历
    input_df = pd.DataFrame(input_data, columns=['position', 'workplace', 'education'])
    # 构建输入数据的DataFrame
    input_df = spark.createDataFrame(input_df)
    # 对输入数据进行预处理
    input_transformed = model.transform(input_df)
    # 提取预测结果
    prediction = input_transformed.select("prediction").first()[0]
    # 返回预测结果
    return {"salary": prediction}

# 预测得分（分类接口）
@app.get("/company_scores")
async def get_company_scores():
    # 读取从上次读取时间到现在的新评论（过去10天+5min以内）
    last_read_time = datetime.now() - timedelta(days=10,minutes=5)  

    # 指定要使用的数据库
    spark.sql("USE bigdata")

    query = f"""
    SELECT * FROM comment_table
    WHERE create_time > '{last_read_time.strftime('%Y-%m-%d %H:%M:%S')}'
    """

    new_comments_df = spark.sql(query)
    # field: company, comment, label, create_time

    # 如果没有新数据，返回空列表
    if new_comments_df.count() == 0:
        response_data={"company": [], "score": []}
    else:
        new_comments_df = new_comments_df.toPandas()
        grouped_data = new_comments_df.groupby('company').agg({'label': 'mean'}).reset_index()
        company = grouped_data["company"].tolist()
        score = grouped_data['label'].tolist()

        # 构建响应数据
        response_data = {
            "company": company,
            "score": score
        }

    # 返回响应
    return response_data

# # 运行uvicorn服务器
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8066)
