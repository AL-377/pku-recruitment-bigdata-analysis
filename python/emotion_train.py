"""
    功能：训练用于情感分类的模型
    数据：情感分类数据集
    输出：训练完成的模型保存于hdfs://namenode:9000/model/classfication
"""
import os
import sys
from pyspark.sql import SparkSession
from pyspark.ml.feature import Tokenizer, HashingTF, IDF, StringIndexer, StopWordsRemover
from pyspark.ml.classification import NaiveBayes
from pyspark.ml import Pipeline
from pyspark.ml.evaluation import MulticlassClassificationEvaluator
from pyspark.ml import PipelineModel
import joblib

#初始化Spark会话
spark = SparkSession.builder \
    .appName("TextClassificationModelTraining") \
    .config("spark.driver.extraJavaOptions", "-Dfile.encoding=UTF-8") \
    .config("spark.executor.extraJavaOptions", "-Dfile.encoding=UTF-8") \
    .getOrCreate()

# 获取SparkContext对象
sc = spark.sparkContext

# 设置日志级别为ERROR
sc.setLogLevel("ERROR")

#加载训练数据
weibo_senti_df = spark.read.csv("/python/data/weibo_senti_100k.csv", header=True, inferSchema=True)

#划分数据集
train_df, test_df = weibo_senti_df.randomSplit([0.7, 0.3], seed=42)

#pipeline
tokenizer = Tokenizer(inputCol="review", outputCol="words")
remover = StopWordsRemover(inputCol="words", outputCol="filtered")
hashingTF = HashingTF(inputCol="filtered", outputCol="rawFeatures")
idf = IDF(inputCol="rawFeatures", outputCol="features")
label_stringIdx = StringIndexer(inputCol="label", outputCol="labelIndex")
nb = NaiveBayes(featuresCol="features", labelCol="labelIndex")
pipeline = Pipeline(stages=[tokenizer, remover, hashingTF, idf, label_stringIdx, nb])

#训练模型
model = pipeline.fit(train_df)

#模型评估
test_predictions = model.transform(test_df)
evaluator = MulticlassClassificationEvaluator(labelCol="labelIndex", predictionCol="prediction", metricName="accuracy")
test_accuracy = evaluator.evaluate(test_predictions)
print(f"Test Dataset Accuracy: {test_accuracy}")

#模型保存
model_path = "hdfs://namenode:9000/model/classfication"
model.write().overwrite().save(model_path)

# Stop Spark session
spark.stop()
