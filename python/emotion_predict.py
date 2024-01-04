"""
    功能：（demo）测试情感分类模型
    模型：加载自hdfs://namenode:9000/model/classfication
    预测文本：自定义文本
    输出：情感分类标签
"""
from pyspark.sql import SparkSession
from pyspark.ml import PipelineModel
from pyspark.ml.feature import Tokenizer, StopWordsRemover, HashingTF, IDF, StringIndexer
from pyspark.sql.functions import lit
import pandas as pd

# Initialize Spark Session
spark = SparkSession.builder \
    .appName("TextClassificationModelInference") \
    .config("spark.driver.extraJavaOptions", "-Dfile.encoding=UTF-8") \
    .config("spark.executor.extraJavaOptions", "-Dfile.encoding=UTF-8") \
    .getOrCreate()

# Load trained model
model_path = "hdfs://namenode:9000/model/classfication"
loaded_model = PipelineModel.load(model_path)

# Define inference data
input_data = ["公司实在是太差了!"]  # 待推断的字符串列表

# Create DataFrame from the input data
inference_df = pd.DataFrame({"review": input_data})
inference_spark_df = spark.createDataFrame(inference_df)

# Preprocessing pipeline (make sure to use the same preprocessing steps as during training)
tokenizer = Tokenizer(inputCol="review", outputCol="word_tmp")
remover = StopWordsRemover(inputCol="word_tmp", outputCol="filtered_tmp")
hashingTF = HashingTF(inputCol="filtered_tmp", outputCol="rawFeatures_tmp")

# Apply preprocessing pipeline to the inference data
preprocessed_data = tokenizer.transform(inference_spark_df)
preprocessed_data = remover.transform(preprocessed_data)
preprocessed_data = hashingTF.transform(preprocessed_data)

# Perform inference using the loaded model
predictions = loaded_model.transform(preprocessed_data)

# Convert Spark DataFrame to Pandas DataFrame
predictions_res = predictions.select("prediction").first()[0]

print("res:", predictions_res)

# Stop Spark session
spark.stop()