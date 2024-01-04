"""
    功能：训练Spark ML的线性回归模型预测职位薪资并评估模型性能
    输出：模型保存于hdfs://namenode:9000/model/regression
"""
import os
import sys
from pyspark.sql import SparkSession
from pyspark.ml.feature import StringIndexer, VectorAssembler
from pyspark.ml.regression import LinearRegression
from pyspark.ml import Pipeline
from pyspark.ml.evaluation import RegressionEvaluator
from pyspark.sql.functions import col

# 确保 Python 处理 UTF-8 编码
os.environ['PYTHONIOENCODING'] = 'utf-8'
sys.stdout = open(sys.stdout.fileno(), mode='w', encoding='utf-8', buffering=1)

# 初始化带有 UTF-8 设置的 Spark 会话
spark = SparkSession.builder \
    .appName("salary_train") \
    .config("spark.driver.extraJavaOptions", "-Dfile.encoding=UTF-8") \
    .config("spark.executor.extraJavaOptions", "-Dfile.encoding=UTF-8") \
    .enableHiveSupport() \
    .getOrCreate()

# Hive读取数据并转换为 Spark DataFrame
spark.sql("USE bigdata")
query = f"""
SELECT * FROM position_table
"""
df = spark.sql(query)

# 将分类变量转换为数值
indexers = [
    StringIndexer(inputCol=column, outputCol=column+"_index").fit(df) 
    for column in ['education', 'workplace', 'position']
]

# 定义特征向量
assembler = VectorAssembler(inputCols=["education_index", "workplace_index", "position_index"], outputCol="features")

# 定义线性回归模型
lr = LinearRegression(featuresCol="features", labelCol="salary")

# 构建 Pipeline
pipeline = Pipeline(stages=indexers + [assembler, lr])

# 划分数据集
(train_data, test_data) = df.randomSplit([0.7, 0.3])

# 训练模型
model = pipeline.fit(train_data)

# 测试模型
predictions = model.transform(test_data)
predictions = predictions.withColumn("prediction", col("prediction"))

# 显示预测结果，现在的prediction列已经是原来的prediction和salary的平均值
predictions.select("education", "workplace", "position", "salary", "prediction").show()

# 定义回归评估器并计算 RMSE 和 MAE
evaluator = RegressionEvaluator(labelCol="salary", predictionCol="prediction")
rmse = evaluator.evaluate(predictions, {evaluator.metricName: "rmse"})
mae = evaluator.evaluate(predictions, {evaluator.metricName: "mae"})

# 打印评估结果
print(f"Root Mean Squared Error (RMSE): {rmse}")
print(f"Mean Absolute Error (MAE): {mae}")

# 模型保存路径
model_path = "hdfs://namenode:9000/model/regression2"
# 将模型保存到 HDFS
model.write().overwrite().save(model_path)

# 关闭 Spark 会话
spark.stop()
