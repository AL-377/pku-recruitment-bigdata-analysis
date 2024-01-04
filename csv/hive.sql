CREATE DATABASE IF NOT EXISTS bigdata;
use bigdata;

DROP TABLE IF EXISTS job;
CREATE TABLE `job`(
    `position` string COMMENT '职位',
    `num` string COMMENT '招聘人数',
    `company` string COMMENT '公司',
    `job_type` string COMMENT '职位类型',
    `jobage` string COMMENT '工作年限',
    `lang` string COMMENT '语言',
    `age` string COMMENT '年龄',
    `sex` string COMMENT '性别',
    `education` string COMMENT '学历',
    `workplace` string COMMENT '工作地点',
    `worktime` string COMMENT '工作时间',
    `salary` string COMMENT '薪资',
    `welfare` string COMMENT '福利待遇',
    `hr` string COMMENT '招聘人',
    `phone` string COMMENT '联系电话',
    `address` string COMMENT '联系地址',
    `company_type` string COMMENT '公司类型',
    `industry` string COMMENT '行业',
    `require` string COMMENT '岗位要求',
    `worktime_day` string COMMENT '工作时间(每天)',
    `worktime_week` string COMMENT '工作时间(每周)',
    `skill` string COMMENT '技能要求'
)
row format delimited
fields terminated by ','
lines terminated by '\n';

DROP TABLE IF EXISTS position_table;
CREATE TABLE `position_table`(
    `position` string COMMENT '岗位',
    `company` string COMMENT '公司',
    `jd` string COMMENT 'jd关键词',
    `workplace` string COMMENT '地区',
    `education` string COMMENT '学历要求',
    `salary` int COMMENT '薪资',
    `create_time` TIMESTAMP COMMENT '创建时间'
)
row format delimited
fields terminated by ','
lines terminated by '\n';
LOAD DATA LOCAL INPATH '/csv/jobsWithTime.csv' OVERWRITE INTO TABLE position_table;

DROP TABLE IF EXISTS comment_table;
CREATE TABLE `comment_table`(
    `company` string COMMENT '公司',
    `comment` string COMMENT '评论',
    `label` tinyint COMMENT '标签',
    `create_time` TIMESTAMP COMMENT '创建时间'
)
row format delimited
fields terminated by ','
lines terminated by '\n';
LOAD DATA LOCAL INPATH '/csv/commentsWithTime.csv' OVERWRITE INTO TABLE comment_table;