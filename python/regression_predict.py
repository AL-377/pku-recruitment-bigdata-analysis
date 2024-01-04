"""
    功能：（demo）基于训练好的回归模型预测职位薪资
    模型：加载自hdfs://namenode:9000/model/regression的Spark ML回归模型
    输入数据：特定职位（如NLP算法工程师）、工作地点（如北京）、教育背景（如博士）
    输出：预测的薪资结果
"""
import os
import sys
from pyspark.sql import SparkSession
from pyspark.ml.feature import StringIndexer, VectorAssembler
from pyspark.ml.feature import Tokenizer, StopWordsRemover, HashingTF, IDF, StringIndexer

from pyspark.ml.regression import LinearRegression
from pyspark.ml import Pipeline
from pyspark.ml import PipelineModel
from datetime import datetime
from pyspark.sql import functions as F

from fastapi import FastAPI
from pydantic import BaseModel
import uvicorn
import pandas as pd

# 初始化带有 UTF-8 设置和 Hive 支持的 Spark 会话
spark = SparkSession.builder \
    .appName("prediction") \
    .config("spark.driver.extraJavaOptions", "-Dfile.encoding=UTF-8") \
    .config("spark.executor.extraJavaOptions", "-Dfile.encoding=UTF-8") \
    .enableHiveSupport() \
    .getOrCreate()

# 创建FastAPI应用
app = FastAPI()


# Load trained model
model_path = "hdfs://namenode:9000/model/regression"
model = PipelineModel.load(model_path)

position = "NLP算法工程师"
workspace = "北京"
education = "博士"

# 构建输入数据的DataFrame
input_data = [[position, workspace, education]]
input_df = pd.DataFrame(input_data, columns=['position', 'workplace', 'education'])
input_df = spark.createDataFrame(input_df)

# 对输入数据进行预处理
input_transformed = model.transform(input_df)
# 提取预测结果
prediction = input_transformed.select("prediction").first()[0]
# 返回预测结果
print("res:", prediction)

spark.stop()
