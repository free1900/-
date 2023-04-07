from lxml import etree  # 网页解析，获取数据
import re  # 正则表达式
import urllib.request, urllib.error  # 制定url，获取网页数据

import xlwt  # 进行excel操作
import sqlite3  # 进行sqlite数据库操作
import os
import datetime
import time
import json
import jsonpath


def tim():
    t = datetime.datetime.now()
    mt = t.strftime('%m-')
    return mt


def main():
    base_url = 'http://www.weather.com.cn'
    #   1.爬取网页
    data7_list = get_data(base_url)
    data1_list = get_1_data(base_url)
    # 3.保存数据
    # save_path = '豆瓣电影top250.xls'
    # save_data(save_path, data_list)
    db7_path = 'day7.db'
    db1_path = 'day1.db'
    save_data_day1_db(db1_path, data1_list)
    save_data_day7_db(db7_path, data7_list)


def get_data(base_url):  # 爬取7天天气网页
    mt = tim()
    data7_list = []
    html = get_html(base_url + '/forecast/')  # 保存获取到的源码

    # 2.逐一解析数据
    tree = etree.HTML(html)
    city_list = tree.xpath('//div[@class="maptabboxinBox"]//ul/li/a/text()')

    link_list = tree.xpath('//div[@class="maptabboxinBox"]//ul/li/a/@href')

    for item in range(len(city_list)):
        if item == 47:
            city = '固原'
        else:
            city = city_list[item].replace('\n', '').replace(' ', '')

        link = link_list[item].replace('http://www.weather.com.cn/weather1d', '')
        link_url = base_url + '/weathern' + link

        # 输入城市链接
        print('正在爬取城市7天数据：' + city)
        html = get_html(link_url)
        tree = etree.HTML(html)

        # 获取日期列表
        date_list = tree.xpath('//ul[@class="date-container"]//p[@class="date"]/text()')
        date_list.pop(0)

        # 获取天气列表
        weather_list = tree.xpath('//ul[@class="blue-container sky"]//p[@class="weather-info"]/text()')

        # 获取风向1列表
        wind1_list = tree.xpath('//ul[@class="blue-container sky"]//div[@class="wind-container"]/i[1]/@title')
        wind1_list.pop(0)

        # 获取风向2列表
        wind2_list = tree.xpath('//ul[@class="blue-container sky"]//div[@class="wind-container"]/i[2]/@title')
        wind2_list.pop(0)

        # 获取风级列表
        scale_list = tree.xpath('//ul[@class="blue-container sky"]//p[@class="wind-info"]/text()')

        # 获取最高气温列表
        temperature_data = tree.xpath('//div[@class="blueFor-container"]/script/text()')
        max_data = temperature_data[0].split('=')
        max_data = max_data[1].split(';')
        max_data = max_data[0]
        max_list = []
        for a in max_data[1:-1].split(','):
            tmp = a[1:-1]
            max_list.append(tmp[tmp.index('') + 0:])
        max_list = max_list
        max_list.pop(0)

        # 获取最低气温列表
        min_data = temperature_data[0].split('=')
        min_data = min_data[2].split(';')
        min_data = min_data[0]
        min_list = []
        for a in min_data[1:-1].split(','):
            tmp = a[1:-1]
            min_list.append(tmp[tmp.index('') + 0:])
        min_list = min_list
        min_list.pop(0)

        for i in range(len(date_list)):
            # 存储七天数据
            data7 = []
            data7.append(city)
            date = date_list[i]
            date = re.sub('[\u4e00-\u9fa5]', '', date)
            date = mt + date
            data7.append(date)

            weather = weather_list[i]
            data7.append(weather)

            max = max_list[i]
            data7.append(max)

            min = min_list[i]
            data7.append(min)

            wind1 = wind1_list[i]
            data7.append(wind1)

            wind2 = wind2_list[i]
            data7.append(wind2)

            scale = scale_list[i]
            # 风级转换
            if scale == '<3级':
                scale = '0'
            elif scale == '3-4级转<3级' or scale == '<3级转3-4级':
                scale = '0.5'
            elif scale == '3-4级':
                scale = '1'
            elif scale == '4-5级转3-4级' or scale == '3-4级转4-5级':
                scale = '1.5'
            elif scale == '4-5级':
                scale = '2'
            elif scale == '5-6级转4-5级' or scale == '4-5级转5-6级':
                scale = '2.5'
            elif scale == '5-6级':
                scale = '3'
            elif scale == '6-7级转5-6级' or scale == '5-6级转6-7级':
                scale = '3.5'
            else:
                scale = '4'
            data7.append(scale)
            data7_list.append(data7)

    return data7_list


def get_1_data(base_url):  # 爬取网页
    mt = tim()
    data_list = []
    html = get_html(base_url + '/forecast/')  # 保存获取到的源码

    # 2.逐一解析数据
    tree = etree.HTML(html)
    city_list = tree.xpath('//div[@class="maptabboxinBox"]//ul/li/a/text()')

    link_list = tree.xpath('//div[@class="maptabboxinBox"]//ul/li/a/@href')

    for item in range(len(city_list)):
        if item == 47:
            city = '固原'
        else:
            city = city_list[item].replace('\n', '').replace(' ', '')

        link = link_list[item].replace('http://www.weather.com.cn/weather1d', '')
        link_url = base_url + '/weathern' + link

        # 输入城市链接
        print('正在爬取城市当天数据：' + city)
        html = get_html(link_url)
        tree = etree.HTML(html)
        # 获取日期列表
        date_list = tree.xpath('//ul[@class="date-container"]//p[@class="date"]/text()')
        date_list.pop(0)

        hour3data = tree.xpath('//div[@class="details-container"]/script/text()')[0]
        text = hour3data[hour3data.index('=') + 1:-2]
        text = text[0:text.index('var') - 1]

        with open('wet.json', 'w', encoding='utf-8') as fp:
            fp.write(text)
        obj = json.load(open('wet.json', 'r', encoding='utf-8'))
        # ja: 天气
        # jb：温度
        # jc：风级
        # jd：风向
        # jf: 时间
        # je: 相对湿度
        time_list = jsonpath.jsonpath(obj, '$..jf')
        weather_list = jsonpath.jsonpath(obj, '$..ja')
        temperature_list = jsonpath.jsonpath(obj, '$..jb')
        wind_list = jsonpath.jsonpath(obj, '$..jd')
        scale_list = jsonpath.jsonpath(obj, '$..jc')
        rh_list = jsonpath.jsonpath(obj, '$..je')
        i = 0
        for x in range(len(time_list)):
            # 存储当天数据
            data_day = []

            time = time_list[x]
            time = time[-2:]
            weather = weather_list[x]
            temperature = temperature_list[x]
            wind = wind_list[x]
            scale = scale_list[x]
            rh = rh_list[x]
            if time != '08' and time != '11' and time != '14' and time != '17' and time != '20' and time != '23' and time != '02' and time != '05':
                continue


            else:
                date = date_list[i]
                date = re.sub('[\u4e00-\u9fa5]', '', date)
                date = mt + date
                data_day.append(city)
                data_day.append(date)
                data_day.append(time)
                # 气象转换
                if weather == '00':
                    weather = '晴'
                elif weather == '01':
                    weather = '多云'
                elif weather == '02':
                    weather = '阴'
                elif weather == '03':
                    weather = '阵雨'
                elif weather == '04':
                    weather = '雷阵雨'
                elif weather == '05':
                    weather = '雷阵雨伴有冰雹'
                elif weather == '06':
                    weather = '雨夹雪'
                elif weather == '07':
                    weather = '小雨'
                elif weather == '08':
                    weather = '中雨'
                elif weather == '09':
                    weather = '大雨'
                elif weather == '10':
                    weather = '暴雨'
                elif weather == '11':
                    weather = '大暴雨'
                elif weather == '12':
                    weather = '特大暴雨'
                elif weather == '13':
                    weather = '阵雪'
                elif weather == '14':
                    weather = '小雪'
                elif weather == '15':
                    weather = '中雪'
                elif weather == '16':
                    weather = '大雪'
                elif weather == '17':
                    weather = '暴雪'
                elif weather == '18':
                    weather = '雾'
                elif weather == '19':
                    weather = '冻雨'
                elif weather == '20':
                    weather = '沙尘暴'
                elif weather == '21':
                    weather = '小雨-中雨'
                elif weather == '22':
                    weather = '中雨-大雨'
                elif weather == '23':
                    weather = '大雨-暴雨'
                elif weather == '24':
                    weather = '暴雨-大暴雨'
                elif weather == '25':
                    weather = '大暴雨-特大暴雨'
                elif weather == '26':
                    weather = '小雪-中雪'
                elif weather == '27':
                    weather = '中雪-大雪'
                elif weather == '28':
                    weather = '大雪-暴雪'
                elif weather == '29':
                    weather = '浮尘'
                elif weather == '30':
                    weather = '扬沙'
                elif weather == '31':
                    weather = '强沙尘暴'
                else:
                    weather = '霾'
                data_day.append(weather)
                data_day.append(temperature)
                # 风向转换
                if wind == '0':
                    wind = '无持续风向'
                elif wind == '1':
                    wind = '东北风'
                elif wind == '2':
                    wind = '东风'
                elif wind == '3':
                    wind = '东南风'
                elif wind == '4':
                    wind = '南风'
                elif wind == '5':
                    wind = '西南风'
                elif wind == '6':
                    wind = '西风'
                elif wind == '7':
                    wind = '西北风'
                else:
                    wind = '北风'
                data_day.append(wind)

                data_day.append(scale)
                data_day.append(rh)
                data_list.append(data_day)
            if time == '05':
                i = i + 1
    return data_list


def get_html(url):
    headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36 Edg/110.0.1587.63'}
    request = urllib.request.Request(url=url, headers=headers)

    time.sleep(5)  # 等待5s

    html = ''
    try:
        response = urllib.request.urlopen(request)
        html = response.read().decode('utf-8')

    except urllib.error.URLError as e:
        if hasattr(e, 'code'):
            print(e.code)
        if hasattr(e, 'reason'):
            print(e.reason)
    return html


def save_data_day7_db(db_path, data_list):
    filename = db_path
    if not os.path.exists(filename):
        init_day7_db(db_path)

    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    for data in data_list:
        for index in range(len(data)):
            if index == 3 or index == 4 or index == 7:
                continue
            data[index] = '"' + data[index] + '"'
        sql = '''
                    insert into day7(
                    city,date, weather, max, min, wind1, wind2, scale)
                    values (%s)''' % ','.join(data)
        cur.execute(sql)
        conn.commit()
    cur.close()
    conn.close()


def init_day7_db(db_path):
    sql = '''
            create table day7
            (id integer primary key autoincrement,
            city text,
            date text,
            weather  text,
            max     numeric,
            min     numeric,
            wind1    text,
            wind2    text,
            scale numeric
             );
    '''
    print('创建数据库')
    conn = sqlite3.connect(db_path)  # 创建数据表

    curses = conn.cursor()  # 获取游标
    curses.execute(sql)  # 执行sql语句
    conn.commit()  # 提交数据库操作
    conn.close()  # 关闭数据库连接


def save_data_day1_db(db_path, data_list):
    filename = db_path
    if not os.path.exists(filename):
        init_day1_db(db_path)

    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    for data in data_list:
        for index in range(len(data)):
            if index == 2 or index == 4 or index == 6:
                continue
            data[index] = '"' + data[index] + '"'
        sql = '''
                    insert into day1(
                    city,date,time,weather,temperature,wind,scale,rh)
                    values (%s)''' % ','.join(data)
        cur.execute(sql)
        conn.commit()
    cur.close()
    conn.close()


def init_day1_db(db_path):
    sql = '''
            create table day1
            (id integer primary key autoincrement,
            city text,
            date text,
            time  numeric,
            weather     text,
            temperature     numeric,
            wind    text,
            scale numeric,
            rh numeric
             );
    '''
    print('创建数据库')
    conn = sqlite3.connect(db_path)  # 创建数据表

    curses = conn.cursor()  # 获取游标
    curses.execute(sql)  # 执行sql语句
    conn.commit()  # 提交数据库操作
    conn.close()  # 关闭数据库连接


if __name__ == "__main__":  # 当程序执行时
    # 调用函数

    main()
