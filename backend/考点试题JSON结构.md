统一外层结构不变，仅扩展内部 content /answer
外层 4 个顶级字段完全不动：question_type、stem、content、analysis
所有差异化内容全部封装在 content 里，答案配套存在 answer，兼容单选、多选、连线、一题多问简答、计算、填空、作文。
一、通用规则
外层结构永远固定，不新增一级 key；
不同题型差异只在 content 内部字段；
一题多问统一用 sub_questions 数组承载，适配简答、综合计算题；
answer 跟随 content 结构对应设计，方便程序批量判分。
1. 单选题 single_choice（扩展选项）
json
{
  "question_type": "single_choice",
  "stem": "圆周率常用近似值是？",
  "content": {
    "options": [
      {"label": "A", "text": "3"},
      {"label": "B", "text": "3.14"},
      {"label": "C", "text": "3.1416"},
      {"label": "D", "text": "3.14159265"}
    ]
  },
  "answer": {
    "correct": "B"
  },
  "analysis": {
    "text": "日常计算一般取3.14作为圆周率近似值。",
    "extra": ""
  }
}
2. 多选题 multi_choice（多正确选项）
json
{
  "question_type": "multi_choice",
  "stem": "下列属于正数的是？",
  "content": {
    "options": [
      {"label": "A", "text": "12"},
      {"label": "B", "text": "-0.5"},
      {"label": "C", "text": "7.8"},
      {"label": "D", "text": "0"}
    ]
  },
  "answer": {
    "correct": ["A", "C"]
  },
  "analysis": {
    "text": "大于0的数字为正数，0既不是正数也不是负数。",
    "extra": ""
  }
}
3. 连线题 match（左右两组待匹配列表）
content 固定 left、right 两个数组，每条带唯一 id 用于匹配
json
{
  "question_type": "match",
  "stem": "将季节与对应典型景物连线",
  "content": {
    "left": [
      {"id": 1, "text": "春天"},
      {"id": 2, "text": "夏天"},
      {"id": 3, "text": "秋天"}
    ],
    "right": [
      {"id": 10, "text": "荷花"},
      {"id": 11, "text": "桃花"},
      {"id": 12, "text": "枫叶"}
    ]
  },
  "answer": {
    "match": [[1, 11], [2, 10], [3, 12]]
  },
  "analysis": {
    "text": "桃花春季开放，荷花夏季盛开，枫叶秋季变红。",
    "extra": ""
  }
}
4. 简答题 / 综合题：一题多问 sub_questions
适用：数学综合大题、道法 / 历史简答多小问、阅读理解问答
结构说明
sub_questions 数组，每个子问题独立题干、独立标准答案
json
{
  "question_type": "short_answer",
  "stem": "阅读材料，回答下列问题",
  "content": {
    "sub_questions": [
      {
        "sub_id": 1,
        "sub_stem": "三角形内角和是多少度？",
        "word_limit": 50
      },
      {
        "sub_id": 2,
        "sub_stem": "直角三角形两个锐角之和为多少？",
        "word_limit": 50
      }
    ]
  },
  "answer": {
    "sub_answers": [
      {"sub_id": 1, "standard": "180°"},
      {"sub_id": 2, "standard": "90°"}
    ]
  },
  "analysis": {
    "text": "三角形内角和恒定180°，直角90°，剩余两锐角相加等于90°。",
    "extra": ""
  }
}
5. 计算题 calculation（多步骤、多小问通用 sub_questions）
json
{
  "question_type": "calculation",
  "stem": "先化简再求值，分两小问计算",
  "content": {
    "requirement": "写出完整演算步骤",
    "sub_questions": [
      {
        "sub_id": 1,
        "sub_stem": "计算 2x+3x，x=2"
      },
      {
        "sub_id": 2,
        "sub_stem": "计算 x²-1，x=3"
      }
    ]
  },
  "answer": {
    "sub_answers": [
      {"sub_id": 1, "steps": ["5x", "5×2=10"], "result": "10"},
      {"sub_id": 2, "steps": ["9-1"], "result": "8"}
    ]
  },
  "analysis": {
    "text": "先合并同类项，再代入数值计算。",
    "extra": ""
  }
}
6. 多空填空题 fill_blank
content.blanks 存放所有空位，answer.blank_answers 顺序对应
json
{
  "question_type": "fill_blank",
  "stem": "平行四边形对边____，对角____。",
  "content": {
    "blanks": [
      {"index": 1, "hint": "边长关系"},
      {"index": 2, "hint": "角度关系"}
    ]
  },
  "answer": {
    "blank_answers": ["相等", "相等"]
  },
  "analysis": {
    "text": "平行四边形基础几何性质。",
    "extra": ""
  }
}
7. 判断题 judge（无扩展字段，content 留空）
json
{
  "question_type": "judge",
  "stem": "边长4cm的正方形面积等于周长。",
  "content": {},
  "answer": {
    "result": false
  },
  "analysis": {
    "text": "面积单位与周长单位不同，无法比较大小。",
    "extra": ""
  }
}
扩展设计核心优势
外层结构完全统一
不需要修改你最开始给定的顶层 JSON，只在 content 内部增加子字段，解析代码顶层逻辑通用。
一题多问标准化
综合大题统一使用 sub_questions，不管简答、计算、阅读都复用同一套子问题结构，便于批量批改、统计得分。
各类题型字段隔离清晰
选择类：options
连线类：left / right
多小问综合题：sub_questions
填空类：blanks
程序通过 question_type 判断后，再读取对应内部字段即可。
可无限兼容新题型
后续增加作图题、听力题，只需要在 content 新增专属子 key，外层不动。


方案：在现有固定外层结构里，统一增加图片存储字段
外层一级键完全不变：question_type、stem、content、analysis
图片分三类场景，全部内嵌，不新增顶层 key：
题干配图（题目本身带图）
选项 / 子小题内配图（选择题选项图、小问附图）
解析配图（解析过程示意图）
统一设计规则
新增通用图片对象结构，所有图片都复用这套：
json
{
  "img_id": "img_001",
  "url": "https://xxx/xxx.png",
  "alt": "直角三角形示意图",
  "width": 400,
  "height": 300
}
url：图片地址（本地相对路径 / 网络链接均可）
alt：图片文字描述（RAG 检索、无障碍阅读必备）
方式 1：题干整体附图（推荐，最常用）
在 content 顶层增加 stem_images 数组，存放题干配套多张图片，单选 / 多选 / 计算 / 简答通用。
带图单选题完整示例
json
{
  "question_type": "single_choice",
  "stem": "观察下图三角形，它是什么三角形？",
  "content": {
    "stem_images": [
      {
        "img_id": "img_001",
        "url": "./imgs/triangle_01.png",
        "alt": "一个直角三角形，直角边长3和4",
        "width": 320,
        "height": 240
      }
    ],
    "options": [
      {"label": "A", "text": "锐角三角形"},
      {"label": "B", "text": "直角三角形"},
      {"label": "C", "text": "钝角三角形"}
    ]
  },
  "answer": {
    "correct": "B"
  },
  "analysis": {
    "text": "图中有直角标记，因此为直角三角形。",
    "extra": ""
  }
}
方式 2：选项内单独配图（选择题每个选项带图）
给 options 每一项增加 images 数组，适配看图选择题。
json
{
  "question_type": "single_choice",
  "stem": "下面哪个是平行四边形？",
  "content": {
    "options": [
      {
        "label": "A",
        "text": "",
        "images": [{"url": "./imgs/a1.png", "alt": "长方形"}]
      },
      {
        "label": "B",
        "text": "",
        "images": [{"url": "./imgs/b1.png", "alt": "梯形"}]
      }
    ]
  },
  "answer": {"correct": "A"},
  "analysis": {"text": "长方形属于特殊平行四边形", "extra": ""}
}
方式 3：一题多问（sub_questions）每个小问独立配图
子问题内部增加 sub_images，实现每个小问单独附图
json
{
  "question_type": "short_answer",
  "stem": "看图回答问题",
  "content": {
    "sub_questions": [
      {
        "sub_id": 1,
        "sub_stem": "图中长方形周长是多少？",
        "sub_images": [{"url": "./imgs/rect.png", "alt": "长5宽3的长方形"}]
      },
      {
        "sub_id": 2,
        "sub_stem": "图中正方形面积是多少？",
        "sub_images": [{"url": "./imgs/square.png", "alt": "边长4正方形"}]
      }
    ]
  },
  "answer": {
    "sub_answers": [
      {"sub_id": 1, "standard": "16"},
      {"sub_id": 2, "standard": "16"}
    ]
  },
  "analysis": {
    "text": "长方形周长=(长+宽)×2",
    "extra": ""
  }
}
方式 4：连线题左右选项配图
left、right 数组内元素增加 images
json
{
  "question_type": "match",
  "stem": "看图连线",
  "content": {
    "left": [
      {"id": 1, "text": "", "images": [{"url": "./imgs/spring.png", "alt": "桃花图"}]},
      {"id": 2, "text": "", "images": [{"url": "./imgs/summer.png", "alt": "荷花图"}]}
    ],
    "right": [
      {"id": 10, "text": "春天"},
      {"id": 11, "text": "夏天"}
    ]
  },
  "answer": {"match": [[1,10],[2,11]]},
  "analysis": {"text": "", "extra": ""}
}
方式 5：解析内插入图片（解析配图）
在 analysis 对象新增 analysis_images 数组，解析步骤示意图专用
json
{
  "question_type": "calculation",
  "stem": "求直角三角形斜边长度",
  "content": {
    "stem_images": [{"url": "./imgs/rt.png", "alt": "直角边3、4"}]
  },
  "answer": {
    "result": "5"
  },
  "analysis": {
    "text": "根据勾股定理计算斜边",
    "extra": "",
    "analysis_images": [
      {"url": "./imgs/gougu.png", "alt": "勾股定理推导图解"}
    ]
  }
}
整体设计优势
外层结构完全不动
只在 content 和 analysis 内部新增图片数组，你原始 4 个顶层 key 无任何改动，兼容旧数据；
分层清晰，图片归属明确
stem_images：整张题目大图
options/images/sub_images /left/images：细分元素配图
analysis_images：解析过程图
支持多图、alt 文本适配 RAG
alt 文字描述图片内容，大模型读取 JSON 做题库检索、AI 批改时能识别图片信息；
全题型通用兼容
单选、多选、填空、连线、计算、多小问综合题全部统一图片结构，一套渲染代码处理所有图片展示。
极简使用规范总结
整张题目一张 / 多张图 → content.stem_images
选择题每个选项带图 → options[].images
综合大题每个小问单独配图 → sub_questions[].sub_images
连线左右素材带图 → left[].images / right[].images
解题解析示意图 → analysis.analysis_images