import random
import re
from datetime import datetime

# 水晶球占卜结果数据集
crystal_ball_predictions = [
    "今天是个不错的日子，放松自己，享受当下。",
    "未来几天可能会面临一些挑战，但你有足够的能力应对。",
    "如果你心怀希望，未来的道路将会顺畅。",
    "你可能会遇到一位新朋友，他们的出现将给你带来好运。",
    "无论发生什么，都不要放弃，因为明天会更好。",
]

# 塔罗牌占卜结果数据集
tarot_cards = [
    {"card": "愚者", "meaning": "开始一段新的旅程，保持开放的心态，勇敢迎接挑战。"},
    {"card": "魔术师", "meaning": "你具备实现目标的全部资源，现在是展现你技能的时候。"},
    {"card": "女教皇", "meaning": "信任你的直觉，保持内心的宁静，答案就在那里。"},
    {"card": "皇后", "meaning": "母性、关怀与创造力，你可能正在孕育一个新机会或项目。"},
    {"card": "死亡", "meaning": "结束和新开始的转折点，某些事物的结束将迎来新的机遇。"},
]

# 运势占卜结果数据集
fortune_predictions = {
    "健康": [
        "今天的你充满活力，适合进行一些户外活动，保持身心健康。",
        "注意休息，避免过度劳累，保持良好的饮食习惯。",
        "近期的健康状况较好，但也要小心突如其来的感冒或小病痛。",
        "情绪波动可能影响你的健康，保持积极心态非常重要。",
    ],
    "财运": [
        "近期财运不错，有可能会有意外的收入或机会。",
        "今天可能会有一些小小的财务波动，小心管理开支。",
        "未来一段时间你的财运较为平稳，但需要注意节省。",
        "大财运将在未来降临，但需要你做好准备，保持谨慎。",
    ],
    "感情": [
        "今天在感情方面有很多的温暖和支持，适合与爱人共度时光。",
        "可能会遇到一些感情上的挑战，但这只是短暂的考验。",
        "感情运势较好，单身的人有机会遇到心仪的对象。",
        "近期感情波动较大，适合冷静处理情感问题。",
    ]
}

# 使用当前时间或随机数来生成一个占卜结果
def crystal_ball_divination():
    # 获取当前时间的秒数作为随机种子
    random.seed(datetime.now().second)
    prediction = random.choice(crystal_ball_predictions)
    return prediction

def tarot_card_divination():
    # 随机抽取一张塔罗牌
    card = random.choice(tarot_cards)
    return f"你的塔罗牌是：{card['card']}。\n意义：{card['meaning']}"

def fortune_divination():
    # 随机选择运势类型
    fortune_type = random.choice(list(fortune_predictions.keys()))
    fortune_message = random.choice(fortune_predictions[fortune_type])
    return f"{fortune_type}运势：{fortune_message}"

# 用户请求水晶球占卜、塔罗牌占卜或运势占卜
def divination(type):
    if type == "1":
        return crystal_ball_divination()
    elif type == "2":
        return tarot_card_divination()
    elif type == "3":
        return fortune_divination()
    else:
        return crystal_ball_divination()
        #return "无效的占卜类型，请选择 'crystal_ball'、'tarot' 或 'fortune'。"

# # 示例：用户进行水晶球占卜
# result = divination("crystal_ball")
# print(f"水晶球占卜结果：\n{result}\n")

# # 示例：用户进行塔罗牌占卜
# result = divination("tarot")
# print(f"塔罗牌占卜结果：\n{result}\n")

# # 示例：用户进行运势占卜
# result = divination("fortune")
# print(f"运势占卜结果：\n{result}\n")
