import requests
import yaml
import random
from datetime import datetime, timedelta
import json
import os
import zwulib
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
import time
from notice import *

time_zone = 8  # 时区
# 两天后日期

def room(id):
    return ['自习室112','自习室113','自习室114','自习室212','自习室213','自习室214','自习室312','自习室313','自习室314'][id]


def get_one_study_room_seat(roomid):

    floorData = [[13344,13688],
    [13124,13799],
    [12806,13035],
    [12435,14862],
    [12186,12434],
    [11939,12183],
    [11720,11938],
    [11550,14848],
    [11376,11549],
    [11376,13688]]
    return random.randint(floorData[roomid][0], floorData[roomid][1])

class SeatAutoBooker:
    def __init__(self, userID, userPass, room_id,begin):
        self.json = None
        self.resp = None
        self.user_data = None

        self.un = userID  # 学号
        print("使用用户：{}".format(self.un))
        self.pd = userPass  # 密码

        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        # self.driver = webdriver.Chrome(service=Service('/usr/local/bin/chromedriver'), options=chrome_options)
        # self.driver = webdriver.Edge(executable_path="msedgedriver.exe",options=chrome_options)
        self.driver = webdriver.Chrome(options=chrome_options)
        self.wait = WebDriverWait(self.driver, 10, 0.5)
        self.cookie = None

        with open("_config.yml", 'r', encoding='utf-8-sig') as f_obj:
            cfg = yaml.safe_load(f_obj)
            self.start_time = cfg['start-time']
            self.book_url = cfg['target']
            self.headers = cfg['headers']
            self.type = room_id

    def book_favorite_seat(self, dday, start_hour, duration):

        # 相关post参数生成
        today_0_clock = datetime.strptime(datetime.now().strftime("%Y-%m-%d 00:00:00"), "%Y-%m-%d %H:%M:%S")
        book_time = today_0_clock + timedelta(days=dday) + timedelta(hours=start_hour)
        delta = book_time - self.start_time
        total_seconds = delta.days * 24 * 3600 + delta.seconds
        
        #avail seat
        seat_url ='https://zjwu.huitu.zhishulib.com/Seat/Index/searchSeats?LAB_JSON=1'
        tmpdata = f"beginTime={total_seconds}&duration={3600 * duration}&num=1&space_category%5Bcategory_id%5D=591&space_category%5Bcontent_id%5D=11"

        # post
        headers = self.headers
        headers['Cookie'] = self.cookie
        print(tmpdata)
        tmpresp = requests.post(seat_url, data=tmpdata, headers=headers)
        tmpjson = json.loads(tmpresp.text)

        df = pd.DataFrame(columns = ['room', 'id', 'title', 'ava'])
        idx = 0
        totalSeatInfo = tmpjson['allContent']['children'][2]['children']['children']
        for i in totalSeatInfo:
            x = i['roomName']
            for j in i['seatMap']['POIs']:
                y = j['id']
                z = j['title']
                ava = j['state']
                #dftmp = pd.DataFrame([x,y,z], columns = ['room', 'id', 'title'])
                #df = pd.concat([df, dftmp])
                # df[len(df)] = [x,y,z]
                df.loc[idx] = [x,y,z, ava]
                idx +=1
        df['id'] = df['id'].astype('int')
        df['title'] = df['title'].astype('int')
        df['ava'] = df['ava'].astype('int')

        df = df[(df['room']==room(self.type)) & (df['ava'] == 0) & (df['title']%2  == 0)]
        print(df)
        seat = random.choice(list(df['id']))
        data = f"beginTime={total_seconds}&duration={3600 * duration}&&seats[0]={seat}&seatBookers[0]={self.user_data['uid']}"

        # post
        headers = self.headers
        headers['Cookie'] = self.cookie
        print(data)
        self.resp = requests.post(self.book_url, data=data, headers=headers)
        self.json = json.loads(self.resp.text)
        return self.json["CODE"], self.json["MESSAGE"] + " 座位:{}".format(seat), seat

    def login(self):
        pwd_path_selector = """//*[@id="react-root"]/div/div/div[1]/div[2]/div/div[1]/div[2]/div/div/div/div/div[1]/div[2]/div/div[3]/div/div[2]/input"""
        button_path_selector = """//*[@id="react-root"]/div/div/div[1]/div[2]/div/div[1]/div[2]/div/div/div/div/div[1]/div[3]"""

        try:
            self.driver.get("https://zjwu.huitu.zhishulib.com/")
            self.wait.until(EC.presence_of_element_located((By.NAME, "login_name")))
            self.wait.until(EC.presence_of_element_located((By.XPATH, pwd_path_selector)))
            self.wait.until(EC.presence_of_element_located((By.XPATH, button_path_selector)))
            self.driver.find_element(By.NAME, 'login_name').clear()
            self.driver.find_element(By.NAME, 'login_name').send_keys(self.un)  # 传送帐号
            self.driver.find_element(By.XPATH, pwd_path_selector).clear()
            self.driver.find_element(By.XPATH, pwd_path_selector).send_keys(self.pd)  # 输入密码
            self.driver.find_element(By.XPATH, button_path_selector).click()
            time.sleep(5)
            cookie_list = self.driver.get_cookies()
            self.cookie = ";".join([item["name"] + "=" + item["value"] + "" for item in cookie_list])
            self.headers['Cookie'] = self.cookie

        except Exception as e:
            print(e.__class__.__name__ + "无法登录")
            return -1
        return 0

        

    def get_user_info(self):
        # 获取UID
        headers = self.headers
        headers['Cookie'] = self.cookie
        try:
            resp = requests.get("https://zjwu.huitu.zhishulib.com/Seat/Index/searchSeats?LAB_JSON=1",
                                headers=headers)
            self.user_data = resp.json()['DATA']
            _ = self.user_data['uid']
        except Exception as e:
            print(self.user_data)
            print(e.__class__.__name__ + ",获取用户数据失败")
            return -1
        print("获取用户数据成功")
        return 0


def appoint_zwulib(username, password,  room_id =3 ,dday =1, begin = 8, duration = 13):

    s = SeatAutoBooker(username, password, room_id,begin)
    if not s.login() == 0:
        s.driver.quit()
        exit(-1)
    if not s.get_user_info() == 0:
        s.driver.quit()
        exit(-1)
    stat, msg, seatid = s.book_favorite_seat(dday, begin, duration)
    if '请勿重复预约' in msg:
        notice('重复预约提醒||'+username, dday, seatid)
        return ''
    elif stat != "ok":
        for i in range(12):
            print("尝试重新预约")
            time.sleep(30)
            stat, msg, seatid = s.book_favorite_seat(dday, begin, duration)
            print(stat, msg)
            if '请勿重复预约' in msg:
                notice('重复预约提醒||'+username, dday, seatid)
            elif stat == "ok":
                notice(username, dday, seatid)
                break
    elif stat == "ok":
        notice(username, dday, seatid)
    # s.wechatNotice("图书馆预约{}".format("成功" if stat == "ok" else "失败"), msg)

    print(stat, msg)
    s.driver.quit()

