from django.shortcuts import render, HttpResponse
from pyecharts.charts import Bar, Pie, Map, WordCloud
from pyecharts import options as opts
import pandas as pd
from pyecharts.globals import SymbolType
import requests
from django.http import JsonResponse
import random

provinces = ['北京', '上海', '广东', '浙江', '湖北', '江苏', '福建', '四川', '湖南', '山东', '天津', '河南', '陕西', '辽宁', '云南', '黑龙江', '河北', '广西', '重庆', '江西', '武汉', '安徽', '甘肃']
educations = ['本科','硕士','博士','高中及以下']
poses = ['NLP算法工程师','后端工程师']
def charts(request):
    # 福利词云
    data_welfare = pd.read_csv('/python/ljt_data/xiamen/welfare.csv')
    wordcloud_chart = (
        WordCloud()
        .add("", data_welfare.values, word_size_range=[10, 50], shape=SymbolType.DIAMOND)
        .set_global_opts(title_opts=opts.TitleOpts(
            title="福利词云图",
            pos_left='center',  # 将标题居中对齐
            pos_top='bottom'  # 将标题位置设为底部
        ))
    )

    # 岗位分布
    data_workplace = pd.read_csv('/python/ljt_data/xiamen/workplace_mock.csv')
    map_chart = (
        Map()
        .add("岗位数", data_workplace.values, "china")
        .set_global_opts(
            title_opts=opts.TitleOpts(
            title="岗位分布图",
            pos_top='bottom',  # 将标题位置设为底部
            pos_left='center'  # 将标题居中对齐
            ),
            visualmap_opts=opts.VisualMapOpts(max_=20000, min_=5000)
        )
    )

    # 工作经验
    data_jobage = pd.read_csv('/python/ljt_data/xiamen/experience.csv')
    jobage = data_jobage['jobage']
    average_salary = data_jobage['平均工资']
    
    pie_chart = (
        Pie()
        .add("", [list(z) for z in zip(jobage, average_salary)])
        .set_global_opts(title_opts=opts.TitleOpts(
            title="平均工资",
            pos_left='center',  # 将标题居中对齐
            pos_top='bottom'  # 将标题位置设为底部
        ))
        .set_series_opts(label_opts=opts.LabelOpts(formatter='{b}: {c}'))
    )

    # 公司性质情况
    data_company_type = pd.read_csv('/python/ljt_data/xiamen/company_type.csv')
    company_type = data_company_type['company_type']
    num = data_company_type['num']
    pie_chart_company_type = (
        Pie()
        .add("", [list(z) for z in zip(company_type, num)])
        .set_global_opts(title_opts=opts.TitleOpts(
            title="不同公司类型数量分布",
            pos_left='center',  # 将标题居中对齐
            pos_top='bottom'  # 将标题位置设为底部
        ))
        .set_series_opts(label_opts=opts.LabelOpts(formatter='{b}: {c}'))
    )


    # 将图表渲染为HTML页面
    return render(request, 'jobs/charts.html', {
        'wordcloud_chart': wordcloud_chart.render_embed(),
        'map_chart': map_chart.render_embed(),
        'pie_chart': pie_chart.render_embed(),
        'pie_chart_company_type': pie_chart_company_type.render_embed()
    })

def bac_charts(request):
    df = pd.read_csv('/python/ljt_data/mock/jobs_mock.csv')
    # 后端工程师
    df = df[df['position'] == '后端工程师']
    # 岗位地区分布
    # 添加"省"字
    df['workplace'] = df['workplace'].apply(lambda x: x + '省' if not x.endswith('市') else x)
    # 计算岗位数量
    data = df['workplace'].value_counts().reset_index()
    data.columns = ['workplace', 'count']
    map_chart = (
        Map()
        .add("岗位数量", data.values.tolist(), maptype="china")
        .set_global_opts(
            title_opts=opts.TitleOpts(
                title="岗位地区分布图",
                pos_top='bottom',  # 将标题位置设为底部
                pos_left='center'  # 将标题居中对齐
            ),
            visualmap_opts=opts.VisualMapOpts(max_=df.shape[0] // 2),
        )
    )

    # 岗位薪资分布
    # 按照学历分组计算岗位数量和平均工资
    grouped_data = df.groupby('education').agg({'position': 'count', 'salary': 'mean'}).reset_index()
    education = grouped_data['education'].tolist()
    average_salary = grouped_data['salary'].tolist()
    
 
    # 绘制平均工资饼图
    pie_chart = (
        Pie()
        .add(
            "",[list(z) for z in zip(education, average_salary)])
        .set_global_opts(title_opts=opts.TitleOpts(
            title="平均工资",
            pos_left='center',  # 将标题居中对齐
            pos_top='bottom'  # 将标题位置设为底部
        ))
        .set_series_opts(label_opts=opts.LabelOpts(formatter='{b}: {c}'))
    )

    # 岗位关键词统计
    keywords = df['jd'].str.split(',').explode().str.lower().str.strip()
    # keywords = df['jd'].str.split(',').explode().str.lower().str.strip()
    keywords_count = keywords.value_counts().reset_index()
    keywords_count.columns = ['keyword', 'count']
    
    wordcloud_chart = (
        WordCloud()
        .add("", keywords_count.values.tolist(), word_size_range=[10, 50], shape=SymbolType.DIAMOND)
        .set_global_opts(title_opts=opts.TitleOpts(
            title="岗位关键词统计图",
            pos_left='center',  # 将标题居中对齐
            pos_top='bottom'  # 将标题位置设为底部
        ))
    )

    # 发送请求获取公司得分数据
    response = requests.get("http://localhost:8066/company_scores")
    if response.status_code == 200:
        data = response.json()
        # 处理响应数据
        company = data["company"]
        score = data["score"]
    else:
        comment_df = pd.read_csv("/python/ljt_data/mock/comments.csv")
        grouped_data = comment_df.groupby('company').agg({'label': 'mean'}).reset_index()
        company = grouped_data["company"].tolist()
        score = grouped_data['label'].tolist()
    
    bar_chart = (
        Bar()
        .add_xaxis(company)
        .add_yaxis('得分', score)
        .set_global_opts(title_opts=opts.TitleOpts(
            title='热门公司评分',
             pos_left='center',  # 将标题居中对齐
            pos_top='bottom'  # 将标题位置设为底部
        ))
    )
    # 将图表渲染为HTML页面
    return render(request, 'jobs/charts_inter.html', {
        'wordcloud_chart': wordcloud_chart.render_embed(),
        'map_chart': map_chart.render_embed(),
        'pie_chart': pie_chart.render_embed(),
        'pie_chart_company_type': bar_chart.render_embed(),
        'provinces': provinces,
        'educations':educations,
        'poses':poses,
        'pos':'开发岗'
    })

def alg_charts(request):
    df = pd.read_csv('/python/ljt_data/mock/jobs_mock.csv')
    df = df[df['position'] == 'NLP算法工程师']
    # 岗位地区分布
    # 添加"省"字
    df['workplace'] = df['workplace'].apply(lambda x: x + '省' if not x.endswith('市') else x)
    # 计算岗位数量
    data = df['workplace'].value_counts().reset_index()
    data.columns = ['workplace', 'count']
    map_chart = (
        Map()
        .add("岗位数量", data.values.tolist(), maptype="china")
        .set_global_opts(
            title_opts=opts.TitleOpts(
                title="岗位地区分布图",
                pos_top='bottom',  # 将标题位置设为底部
                pos_left='center'  # 将标题居中对齐
            ),
            visualmap_opts=opts.VisualMapOpts(max_=df.shape[0] // 2),
        )
    )

    # 岗位薪资分布
    # 按照学历分组计算岗位数量和平均工资
    grouped_data = df.groupby('education').agg({'position': 'count', 'salary': 'mean'}).reset_index()
    education = grouped_data['education'].tolist()
    average_salary = grouped_data['salary'].tolist()
    
 
    # 绘制平均工资饼图
    pie_chart = (
        Pie()
        .add(
            "",[list(z) for z in zip(education, average_salary)])
        .set_global_opts(title_opts=opts.TitleOpts(
            title="平均工资",
            pos_left='center',  # 将标题居中对齐
            pos_top='bottom'  # 将标题位置设为底部
        ))
        .set_series_opts(label_opts=opts.LabelOpts(formatter='{b}: {c}'))
    )

    # 岗位关键词统计
    keywords = df[df['position'] == 'NLP算法工程师']['jd'].str.split(',').explode().str.lower().str.strip()
    # keywords = df['jd'].str.split(',').explode().str.lower().str.strip()
    keywords_count = keywords.value_counts().reset_index()
    keywords_count.columns = ['keyword', 'count']
    
    wordcloud_chart = (
        WordCloud()
        .add("", keywords_count.values.tolist(), word_size_range=[10, 50], shape=SymbolType.DIAMOND)
        .set_global_opts(title_opts=opts.TitleOpts(
            title="岗位关键词统计图",
            pos_left='center',  # 将标题居中对齐
            pos_top='bottom'  # 将标题位置设为底部
        ))
    )

    # 评分数据
    # 绘制公司评分

    # 发送请求获取公司得分数据
    response = requests.get("http://localhost:8066/company_scores")
    if response.status_code == 200:
        data = response.json()
        # 处理响应数据
        company = data["company"]
        score = data["score"]
    else:
        comment_df = pd.read_csv("/python/ljt_data/mock/comments.csv")
        grouped_data = comment_df.groupby('company').agg({'label': 'mean'}).reset_index()
        company = grouped_data["company"].tolist()
        score = grouped_data['label'].tolist()
        
    bar_chart = (
        Bar()
        .add_xaxis(company)
        .add_yaxis('得分', score)
        .set_global_opts(title_opts=opts.TitleOpts(
            title='热门公司评分',
             pos_left='center',  # 将标题居中对齐
            pos_top='bottom'  # 将标题位置设为底部
        ))
    )
    # 将图表渲染为HTML页面
    return render(request, 'jobs/charts_inter.html', {
        'wordcloud_chart': wordcloud_chart.render_embed(),
        'map_chart': map_chart.render_embed(),
        'pie_chart': pie_chart.render_embed(),
        'pie_chart_company_type': bar_chart.render_embed(),
        'provinces': provinces,
        'educations':educations,
        'poses':poses,
        'pos':'算法岗'
    })

def submit_form(request):
    if request.method == 'POST':
        form_data = request.POST  # 获取表单数据
        # 在这里调用后端接口处理表单数据
        response = requests.post('http://localhost:8066/predict_salary', data=form_data)
        if response.status_code == 200:
            # 处理成功响应，直接返回 JSON 格式的数据
            salary = response.json().get('salary')
            return JsonResponse({'salary': salary})
        else:
            # 处理错误响应，返回错误信息
            error = response.text
            return JsonResponse({'error': error}, status=500)
    
    return JsonResponse({'error': 'Method Not Allowed'}, status=405)
