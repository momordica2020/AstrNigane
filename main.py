import asyncio
import datetime
import os
import re
from astrbot.api.event import filter, AstrMessageEvent, MessageEventResult, MessageChain
from astrbot.api.star import Context, Star, register
from astrbot.api import logger
from astrbot.api import message_components as Comp
from astrbot.api.all import CommandResult, Image, Plain
import aiohttp

import socket
import json
import random
import hashlib

from . import zhanbu

@register("sdqy", "Firebuggy", "沙雕群友v1", "0.1.0")
class MyPlugin(Star):

    root_path = r"D:/Projects/momordica2020/Kugua/output/Debug/net8.0/RunningData/"  
                
    def __init__(self, context: Context):
        super().__init__(context)
        self.messages = {}
        self.eventinfos = {}
        self.data = self.get_group_infos()
        self.askName={"3994145344":"我危","1741346019":"我厄"}

          


        what_to_eat_data_path = self.root_path + "official/food.json"
        if not os.path.exists(what_to_eat_data_path):
            with open(what_to_eat_data_path, "w", encoding="utf-8") as f:
                f.write(json.dumps([], ensure_ascii=False, indent=2))
        with open(what_to_eat_data_path, "r", encoding="utf-8") as f:
            self.what_to_eat_data :list = json.loads(
                open(what_to_eat_data_path, "r", encoding="utf-8").read()
            )

        morning_path = self.root_path + "official/morning.json"
        if not os.path.exists(morning_path):
            with open(morning_path, "w", encoding="utf-8") as f:
                f.write(json.dumps({}, ensure_ascii=False, indent=2))
        with open(morning_path, "r", encoding="utf-8") as f:
            # self.data = json.loads(f.read())
            self.good_morning_data = json.loads(f.read())

        # moe
        self.moe_urls = [
            "https://t.mwm.moe/pc/",
            "https://t.mwm.moe/mp",
            "https://www.loliapi.com/acg/",
            "https://www.loliapi.com/acg/pc/",
        ]

        self.search_anmime_demand_users = {}

        loop = asyncio.get_event_loop()
        loop.create_task(self.periodic_task(30))


    def __enter__(self):
        logger.info("Enter!")
        pass

    def __exit__(self, type, value, trace):
        logger.info("Exit!")
        pass


    async def __aenter__(self):
        logger.info("async Enter!")
        
        pass

    async def __aexit__(self, type, value, trace):
        logger.info("async Exit!")
        pass
    
    

    # 注册指令的装饰器。指令名为 helloworld。注册成功后，发送 `/helloworld` 就会触发这个指令，并回复 `你好, {user_name}!`
    @filter.event_message_type(filter.EventMessageType.ALL)
    async def helloworld(self, event: AstrMessageEvent):
        '''响应特定群的对话喵'''
        uni_id = f"{event.get_group_id()}_{event.get_self_id()}"
        # logger.warning(f"uni_id = {uni_id} : {event.message_str}")
        # if(random.randint(0, 10) > 3):
        #     return
        # if(self.messages.get(uni_id) != None):
        #     if datetime.now() - self.messages[uni_id] <= timedelta(seconds=random(10, 50)):
        #         return
        self.messages[uni_id] = datetime.datetime.now()

        if(self.eventinfos.get(uni_id) == None):
            self.eventinfos[uni_id] = event


        id = event.get_group_id()
        user_name = event.get_sender_name()
        message_str = event.message_str
        messages = event.get_messages()
        # logger.info(self.has_tag(id,"测试"))
        # logger.info(str(event.get_sender_id()) == '287859992')



        if self.isSelfMsg(event):
            return
        # filter massage_str at
        (isAsk, message_str) = self.isAskMe(event)
        # 去掉开头的标点符号
        # message_str = re.sub(r'^\p{P}+\s*', '', message_str)  
        isOfficial = event.get_self_id() == "qq_official"
        # 
        if isAsk and isOfficial:
            res = await self.call_official(message_str, event)
            if res:
                if self.root_path in res:
                    yield event.image_result(res)
                else:
                    yield event.plain_result(res)
        else:
            if isAsk and message_str and self.has_tag(event.get_group_id(),"测试"):
                res = await self.call_not_official(message_str, event)
                if res:
                    if self.root_path in res:
                        yield event.image_result(res)
                    else:
                        yield event.plain_result(res)
                    return

            thash = self.generate_random_from_hash(
                f"{random.randint(1,100000)}{datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}{message_str}{event.get_self_id()}{event.get_sender_id()}"
                 ,1000)
            if( 
                
                isAsk and self.has_tag(event.get_group_id(),"测试") or
                 self.has_tag(event.get_group_id(),"自言自语") and thash >=985):    
                logger.warning(f"[{thash}]{event.get_self_id()} - {user_name}发了 {message_str}!")   
            
                for line in self.get_history_react(event):
                    yield event.plain_result(line)
                # yield event.plain_result(f"{id}")
                # await asyncio.sleep(10)

            if(message_str and message_str.startswith("日你妈") and event.get_sender_id() == '287859992'):
                yield event.image_result(f"{self.root_path}gifsfox/1_1.gif")
                
            









            # message_chain = MessageChain().message(message_str)
            # await self.context.send_message(event.unified_msg_origin, message_chain)   
            # pass
        #     user_name = event.get_sender_name()
        #     message_str = event.message_str # 用户发的纯文本消息字符串
        #     message_chain = event.get_messages() # 用户所发的消息的消息链 # from astrbot.api.message_components import *
        #     logger.info(message_chain)
        #     yield event.plain_result(f"Hello, {user_name}, 你发了 {message_str}!") # 发送一条纯文本消息

    async def call_official(self, message_str:str, event: AstrMessageEvent):
        uid = event.get_sender_id()
        msg = ""
        logger.warning(f"官方调用 {uid} {message_str}")
        if message_str == "测试":
            msg = f"{self.root_path}imgmj/1.jpg"
            # message_chain = MessageChain().message(event.message_str)
            # await self.context.send_message(event.unified_msg_origin, message_chain)   
            # yield event.Image(file=f"{self.root_path}gifsfox/1_1.gif")
        elif message_str == "测试2":
            msg = "靠"+uid
            pass
        elif message_str == "一言":
            msg = await self.hitokoto(event)
        elif "今天吃什么" in message_str:
            msg = await self.what_to_eat(event)
        elif "喜加一" in message_str:
            msg = await self.epic_free_game(event)
        elif "moe" in message_str:
            msg = await self.get_moe(event)
        elif any(key in message_str for key in ["早","午","晚","安","夜","醒","睡"]):
            msg = await self.good_morning(message_str, event)

        
    
        return msg
        
        #pass

    async def call_not_official(self, message_str:str, event: AstrMessageEvent):
        uid = event.get_sender_id()
        msg = ""
        match = re.match(r'占卜(\w+)', message_str)
        if(match):
            res = zhanbu.divination(match.group(1))
            return event.plain_result(res)
        if message_str == "一言":
            msg = await self.hitokoto(event)
        elif "今天吃什么" in message_str:
            msg = await self.what_to_eat(event)
        elif "喜加一" in message_str:
            msg = await self.epic_free_game(event)
        elif "moe" in message_str:
            msg = await self.get_moe(event)
        elif any(key in message_str for key in ["早","午","晚","安","夜","醒","睡"]):
            msg = await self.good_morning(message_str, event)

        
    
        return msg
        


    def isSelfMsg(self, event: AstrMessageEvent):
        return str(event.get_sender_id()) == str(event.get_self_id())
    
    def get_message_str_without_at(self, event: AstrMessageEvent):
        message_str = ""
        for i in event.get_messages():
            if isinstance(i, Comp.Plain):
                message_str += i.text
        return message_str



    def isAskMe(self, event: AstrMessageEvent):
        '''返回值：是否at我，去掉at后的消息'''
        if(event.get_self_id() == "qq_official"):
            return (True,event.message_str)
        # logger.warning(f"{event.get_self_id()} <- {event.message_str}")
        # At
        for i in event.get_messages():
            # logger.warning(i)
            if isinstance(i, Comp.At) and str(i.qq) == str(event.get_self_id()):
                return (True,self.get_message_str_without_at(event))
        # begin word
        if str(event.get_self_id()) in self.askName.keys():
            if event.message_str.startswith(self.askName[str(event.get_self_id())]):
                return (True,event.message_str[len(self.askName[str(event.get_self_id())]):])

        return (False,"")


    async def terminate(self):
        '''可选择实现 terminate 函数，当插件被卸载/停用时会调用。'''


    async def periodic_task(self, interval):
        while True:
            # logger.info("定期任务执行")

            
            for event in self.eventinfos.values():
                if(self.has_tag(event.get_group_id(),"自言自语")):
                    if random.randint(0, 100) > 95:
                        # umo = event.unified_msg_origin
                        logger.info(f"{event.get_self_name()}发送消息到{event.get_group_id()}")
                        for line in self.get_history_react(event):
                            # message_chain = MessageChain().message(line)
                            # await self.context.send_message(event.unified_msg_origin, message_chain)
                            message_chain = MessageChain().message(line)
                            await self.context.send_message(event.unified_msg_origin, message_chain)               

            await asyncio.sleep(interval)


    
    def get_group_infos(self):
        
        file_path = self.root_path + "data_playgroup.json"
        with open(file_path, 'r', encoding='utf-8') as file:
            # 使用 json.load() 将JSON文件内容解析为Python对象
            data = json.load(file)
            return data

    def has_tag(self, number, tag):
        """
        检查指定号码是否包含指定的标签。
        :param number: 号码（字符串）
        :param tag: 要查询的标签（字符串）
        :return: 如果包含标签返回True，否则返回False
        """
        if number in self.data and "Tags" in self.data[number]:
            return tag in self.data[number]["Tags"]
        return False
    
    def get_all_files(self, directory):
        """递归获取目录下所有文件的完整路径"""
        file_paths = []
        for root, _, files in os.walk(directory):
            for file in files:
                file_paths.append(os.path.join(root, file))
        return file_paths


    def filter_react(self, str: str) -> bool:
        filter_key = ["您的", "老虎","马币","镜像","翻转","视频信息",
                      "tag","url","qq", "json", "cq", "app", "xml",
                      "不支持", "押","淘宝","旗舰","武汉","中","国","宪",
                      "习","湾","军","警","法","共","党","坦","肺","封",
                      "疫","新闻","小电酱","小崽子"]
        filter_start_key = ["签到","1号","2号","3号","4号","4号","拳交"]
        if len(str) <= 0:
            return False
        if any(str.startswith(key) for key in filter_start_key):
            return False
        if any (key.lower() in str.lower() for key in filter_key):
            return False
        return True

    def get_history_react(self, event: AstrMessageEvent) -> list[str]:
        """随机获取历史消息中的部分消息"""
        result = []
        try:
            files = self.get_all_files(self.root_path + "History/group")
            max_time = 10
            
            if not files:
                return []

            while max_time > 0:
                max_time -= 1
                file_index = random.randint(0, len(files) - 1)
                logger.debug(file_index)
                with open(files[file_index], 'r', encoding='utf-8') as file:
                    lines = file.readlines()
                    logger.debug(f"line -- {len(lines)}")
                    if len(lines) < 100:
                        continue

                    begin = random.randint(0, len(lines) - 5)
                    max_num = random.randint(1, 5)
                    num = len(lines) - begin
                    find = False
                    target_user = ""

                    for i in range(num):
                        items = lines[begin + i].strip().split('\t')
                        if len(items) >= 3:
                            if items[1] == event.get_self_id(): 
                                continue
                            if target_user and target_user != items[1]:
                                continue
                            target_user = items[1]
                            msg = items[2].strip()

                            # 过滤 CQ 代码
                            #logger.warning(msg)
                            msg = re.sub(r'\[.*?\]', "", msg)
                            #logger.warning(msg)
                            # msg = re.sub(r"$$\[CQ:[^$$]+\]", "", msg)
                            if not self.filter_react(msg):
                                logger.warning(f"filtered:{msg}")
                                continue
                            # else :
                            #     logger.warning(f"not filtered:{msg}")
                            # 过滤呼唤词
                            # for prefix in ["/", "我危","我厄","我苦","我瓜", "苦瓜", "小电酱", "小崽子"]:
                            #     if msg.startswith(prefix):
                            #         break
                            find=True
                            result.append(msg)
                            max_num -= 1
                            if max_num <= 0:
                                break
                    if find:
                        return result

        except Exception as e:
            logger.error(f"Error: {e}")
            pass
        # logger.info(result)
        return result


    def official_load_data(self):
        file_path = self.root_path + "data_official.json"
        with open(file_path, 'r', encoding='utf-8') as file:
            # 使用 json.load() 将JSON文件内容解析为Python对象
            data = json.load(file)
            return data
        

    def generate_random_from_hash(self, input_message: str, maxval: int):
        # 使用SHA256算法计算消息的哈希值
        hash_object = hashlib.sha256(input_message.encode())
        hash_value = hash_object.hexdigest()

        # 将哈希值转换为一个整数
        hash_int = int(hash_value, 16)

        random_value = hash_int % (abs(maxval) + 1)
        return random_value

    # def start_server(host='127.0.0.1', port=8849):
    #     # 创建一个 TCP/IP socket
    #     with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
    #         # 绑定地址和端口
    #         server_socket.bind((host, port))
    #         # 监听连接
    #         server_socket.listen()
    #         print(f"Server started on {host}:{port}")

    #         while True:
    #             # 等待客户端连接
    #             client_socket, client_address = server_socket.accept()
    #             with client_socket:
    #                 print(f"Connected by {client_address}")

    #                 # 接收数据
    #                 data = client_socket.recv(1024)
    #                 if not data:
    #                     continue

    #                 # 解析 JSON 数据
    #                 try:
    #                     json_data = json.loads(data.decode('utf-8'))
    #                     print(f"Received JSON: {json_data}")

    #                     # 处理 JSON 数据（这里只是一个示例）
    #                     response_data = {"status": "success", "message": "Data received"}

    #                     # 发送 JSON 响应
    #                     response_json = json.dumps(response_data)
    #                     client_socket.sendall(response_json.encode('utf-8'))
    #                 except json.JSONDecodeError:
    #                     print("Invalid JSON received")
    #                     response_data = {"status": "error", "message": "Invalid JSON"}
    #                     response_json = json.dumps(response_data)
    #                     client_socket.sendall(response_json.encode('utf-8'))



    async def get_moe(self, message: AstrMessageEvent):
        """随机动漫图片"""
        shuffle = random.sample(self.moe_urls, len(self.moe_urls))
        for url in shuffle:
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(url) as resp:
                        if resp.status != 200:
                            return ""
                        data = await resp.read()
                        break
            except Exception as e:
                logger.error(f"从 {url} 获取图片失败: {e}。正在尝试下一个API。")
                continue
        # 保存图片到本地
        try:
            with open(f"{self.root_path}moe.jpg", "wb") as f:
                f.write(data)
            return f"{self.root_path}moe.jpg"

        except Exception as e:
            return ""

    async def hitokoto(self, message: AstrMessageEvent):
        """来一条一言"""
        url = "https://v1.hitokoto.cn"
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                if resp.status != 200:
                    return ""
                data = await resp.json()
        return f"{data["hitokoto"]}——{data["from"]}"


    async def save_what_eat_data(self):
        # path = os.path.abspath(os.path.dirname(__file__))
        with open(self.root_path + "/official/food.json", "w", encoding="utf-8") as f:
            f.write(
                json.dumps(
                    self.what_to_eat_data, ensure_ascii=False, indent=2
                )
            )

    async def what_to_eat(self, message: AstrMessageEvent):
        """今天吃什么"""
        if "添加" in message.message_str:
            l = message.message_str.split(" ")
            # 今天吃什么 添加 xxx xxx xxx
            if len(l) < 3:
                return  "格式：今天吃什么 添加 [食物1] [食物2] ..."
                
            self.what_to_eat_data += l[2:]  # 添加食物
            await self.save_what_eat_data()
            return ("添加成功")
        elif "删除" in message.message_str:
            l = message.message_str.split(" ")
            # 今天吃什么 删除 xxx xxx xxx
            if len(l) < 3:
                return "格式：今天吃什么 删除 [食物1] [食物2] ..."
            for i in l[2:]:
                if i in self.what_to_eat_data:
                    self.what_to_eat_data.remove(i)
            await self.save_what_eat_data()
            return "删除成功"

        ret = f"今天吃 {random.choice(self.what_to_eat_data)}！"
        return ret

    async def epic_free_game(self, message: AstrMessageEvent):
        """EPIC 喜加一"""
        url = "https://store-site-backend-static-ipv4.ak.epicgames.com/freeGamesPromotions"

        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                if resp.status != 200:
                    return "请求失败"
                data = await resp.json()

        games = []
        upcoming = []

        for game in data["data"]["Catalog"]["searchStore"]["elements"]:
            title = game.get("title", "未知")
            try:
                if not game.get("promotions"):
                    continue
                original_price = game["price"]["totalPrice"]["fmtPrice"][
                    "originalPrice"
                ]
                discount_price = game["price"]["totalPrice"]["fmtPrice"][
                    "discountPrice"
                ]
                promotions = game["promotions"]["promotionalOffers"]
                upcoming_promotions = game["promotions"]["upcomingPromotionalOffers"]

                if promotions:
                    promotion = promotions[0]["promotionalOffers"][0]
                else:
                    promotion = upcoming_promotions[0]["promotionalOffers"][0]
                start = promotion["startDate"]
                end = promotion["endDate"]
                # 2024-09-19T15:00:00.000Z
                start_utc8 = datetime.datetime.strptime(
                    start, "%Y-%m-%dT%H:%M:%S.%fZ"
                ) + datetime.timedelta(hours=8)
                start_human = start_utc8.strftime("%Y-%m-%d %H:%M")
                end_utc8 = datetime.datetime.strptime(
                    end, "%Y-%m-%dT%H:%M:%S.%fZ"
                ) + datetime.timedelta(hours=8)
                end_human = end_utc8.strftime("%Y-%m-%d %H:%M")
                discount = float(promotion["discountSetting"]["discountPercentage"])
                if discount != 0:
                    # 过滤掉不是免费的游戏
                    continue

                if promotions:
                    games.append(
                        f"【{title}】\n原价: {original_price} | 现价: {discount_price}\n活动时间: {start_human} - {end_human}"
                    )
                else:
                    upcoming.append(
                        f"【{title}】\n原价: {original_price} | 现价: {discount_price}\n活动时间: {start_human} - {end_human}"
                    )

            except BaseException as e:
                raise e
                games.append(f"处理 {title} 时出现错误")

        if len(games) == 0:
            return "暂无免费游戏"
        ret = "【EPIC 喜加一】\n"
        ret += "\n\n".join(games)
        ret += "\n\n"
        ret += "【即将免费】\n"
        ret += "\n\n".join(upcoming)
        return ret
            
        





    def get_morning_state_num(self, date):
        now_stage = 0
        if date.hour >= 5 and date.hour < 9:
            now_stage = 0
        elif date.hour >= 9 and date.hour < 12:
            now_stage = 1
        elif date.hour >= 12 and date.hour < 14:
            now_stage = 2
        elif date.hour >= 14 and date.hour < 18:
            now_stage = 3
        elif date.hour >= 18 or date.hour < 5:
            now_stage = 4
        return now_stage
    
    def get_date_6morning(self, date):
        if date.hour >= 6:
            return date.replace(hour=6, minute=0, second=0)
        else:
            return date.replace(hour=6, minute=0, second=0) - datetime.timedelta(days=1)

    async def good_morning(self,message_str:str, message: AstrMessageEvent):
        """和Bot说早晚安，记录睡眠时间"""
        # CREDIT: 灵感部分借鉴自：https://github.com/MinatoAquaCrews/nonebot_plugin_morning
        umo_id = message.unified_msg_origin
        user_id = message.message_obj.sender.user_id
        if umo_id in self.good_morning_data:
            umo = self.good_morning_data[umo_id]
        else:
            umo = {}
        if user_id in umo:
            user = umo[user_id]
        else:
            user = {
                "sum": 0,
                "day_first_record": "",
                "day_last_record": "",
            }

        

        # user_name = message.message_obj.sender.nickname
        curr_utc8 = datetime.datetime.now(datetime.timezone(offset=datetime.timedelta(hours=8)))
        curr_human = curr_utc8.strftime("%Y-%m-%d %H:%M:%S")

        ask_stage = 0
        if any (message_str.startswith(key) for key in ["醒了","我醒了","早安", "早", "早上好"]):
            ask_stage = 0
        elif any (message_str.startswith(key) for key in ["上午好"]):
            ask_stage = 1
        elif any (message_str.startswith(key) for key in ["午安", "中午好"]):
            ask_stage = 2
        elif any (message_str.startswith(key) for key in ["下午好"]):
            ask_stage = 3
        elif any (message_str.startswith(key) for key in ["晚上好"]):
            ask_stage = 4  
        elif any (message_str.startswith(key) for key in ["晚安", "夜安", "睡了","我睡了"]):
            ask_stage = 5
        else:
            return ""

        ret = ""
        now_stage = self.get_morning_state_num(curr_utc8)
        time_zone_human = ""
        

        if ask_stage <= 4:
            greeting = ["早安", "上午好","中午好","下午好", "晚上好"][now_stage]
            ret += f"{greeting}！现在是{time_zone_human} {curr_human}\n"
            if user["day_last_record"]:
                last_date_end = datetime.datetime.strptime(user["day_last_record"], "%Y-%m-%d %H:%M:%S")
                last_date_end = last_date_end.replace(tzinfo=datetime.timezone(offset=datetime.timedelta(hours=8)))
                duration_to_last_evening = curr_utc8 - last_date_end
                hrs = int(duration_to_last_evening.total_seconds() / 3600)
                mins = int((duration_to_last_evening.total_seconds() % 3600) / 60)
                if hrs>0 or mins >0:
                    ret += f"你睡了{hrs}小时{mins}分。\n"
                user["sum"] =  int(user["sum"]) + 1
                user["day_last_record"] = ""
            user["day_first_record"] = curr_human
                

        elif ask_stage==5:
            if now_stage == 2:
                greeting = "午安"
            elif now_stage == 4:
                greeting = "晚安"
            else:
                greeting = "睡个好觉"
            ret += f"{greeting}！现在是{time_zone_human} {curr_human}\n"
            if user["day_first_record"]:
                last_date_start = datetime.datetime.strptime(user["day_first_record"], "%Y-%m-%d %H:%M:%S")
                last_date_start = last_date_start.replace(tzinfo=datetime.timezone(offset=datetime.timedelta(hours=8)))
                duration_to_last_morning = curr_utc8 - last_date_start
                hrs = int(duration_to_last_morning.total_seconds() / 3600)
                mins = int((duration_to_last_morning.total_seconds() % 3600) / 60)
                if hrs>0 or mins >0:
                    ret += f"你有{hrs}小时{mins}分没睡觉了。\n"
                user["day_first_record"] = ""
            user["day_last_record"] = curr_human
            
        




        umo[user_id] = user
        self.good_morning_data[umo_id] = umo

        with open(self.root_path+f"official/morning.json", "w", encoding="utf-8") as f:
            f.write(json.dumps(self.good_morning_data, ensure_ascii=False, indent=2))

        # 根据 day 判断今天是本群第几个睡觉的
        curr_day: int = curr_utc8.day
        # curr_day_sleeping = 0
        # for v in umo.values():
        #     if v["daily"]["night_time"] and not v["daily"]["morning_time"]:
        #         # he/she is sleeping
        #         user_day = datetime.datetime.strptime(
        #             v["daily"]["night_time"], "%Y-%m-%d %H:%M:%S"
        #         ).day
        #         if user_day == curr_day:
        #             # 今天睡觉的人数
        #             curr_day_sleeping += 1
        return ret



