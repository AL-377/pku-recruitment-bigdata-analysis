# coding=utf8
jf = {
    "FILE_MAP": {
        "echarts": "echarts.min",
        "echartsgl": "echarts-gl.min",
        "liquidfill": "echarts-liquidfill.min",
        "wordcloud": "echarts-wordcloud.min"
    },
    "PINYIN_MAP": {},
}
f = {
    "PINYIN_MAP": {
        "安庆": "an1_qing4"
        , "蚌埠": "bang4_bu4"
    },
    "FILE_MAP": {
        "an1_qing4": "an1_hui1_an1_qing4"
        , "bang4_bu4": "an1_hui1_bang4_bu4"
    }
}

javascript_file_config = {
    'hosts': {
        'china-provinces': 'https://echarts-maps.github.io/echarts-china-provinces-js/',
        'china-cities': 'https://echarts-maps.github.io/echarts-china-cities-js/'
    },
    'china-provinces': {
        'aliases': {
            '吉林省': '吉林'
        },
        'maps': {
            '吉林': 'jilin',
            '福建': 'fujian'
        }
    },
    'china-cities': {
        'aliases': {
            '吉林市': '吉林'
        },
        'maps': {
            '吉林': 'ji2lin2_ji2lin2'
        }
    }
}


class JsRepository:
    def __init__(self, name):
        self.name = name
