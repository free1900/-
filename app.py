import sqlite3
import datetime

from flask import Flask, render_template, request

app = Flask(__name__)

@app.route('/')
def index():
    time = []  # 当天时间
    today_t = []  # 当天温度
    wea = []  # 天气情况
    num = []  # 出现次数
    rh = []  # 当天相对湿度
    wd = []  # 当天风向
    sd = []  # 当天风速
    date = []  # 日期
    min = []  # 最低气温
    max = []  # 最高气温
    w_1 = []  # 一周白天风向
    w_2 = [] #一周晚上风向
    w_7 = [] #一周风向
    s_7 = []  # 一周风速
    city = "武汉"
    now = datetime.datetime.now().strftime('%m-%d').replace('-0', '-')

    con1 = sqlite3.connect("day1.db")
    cur = con1.cursor()
    sql_1 = "SELECT time, temperature,rh,wind,scale FROM day1 WHERE city=? and date=?"
    data_1 = cur.execute(sql_1, (city, now))

    for item in data_1:
        time.append(item[0])
        today_t.append(item[1])
        rh.append(item[2])
        wd.append(item[3])
        sd.append(item[4])

    sql_2 = "SELECT weather,count(weather) FROM day1 WHERE city=? group by weather"
    data_2 = cur.execute(sql_2,(city,))
    for b in data_2:
        wea.append(b[0])
        num.append(b[1])
    cur.close()
    con1.close()

    con2 = sqlite3.connect("day7.db")
    cur2 = con2.cursor()

    sql_3 = "SELECT date, min,max,wind1,wind2,scale FROM day7 WHERE city=?"
    data_3 = cur2.execute(sql_3, (city,))

    for c in data_3:
        date.append(c[0])
        min.append(c[1])
        max.append(c[2])
        w_1.append(c[3])
        w_2.append(c[4])
        s_7.append(c[5])
    for w in range(len(w_1)):
        wind_7 = w_1[w]+ ' '+w_2[w]
        w_7.append(wind_7)
    cur2.close()
    con2.close()

    # 获取当前时间和日期
    ti = datetime.datetime.now()  # 获取当前时间
    hour = ti.time().hour  # 获取当前时间的时

    # 连接数据库并查询数据
    con = sqlite3.connect("day1.db")
    cur = con.cursor()
    cur.execute("SELECT temperature,wind,rh FROM day1 WHERE city=? AND date=? AND time<=? AND ?<time+3",
                (city, now, hour, hour))
    rows = cur.fetchall()

    # 如果查询结果为空，则查询前一个时间段的数据
    if not rows:
        cur.execute("SELECT temperature,wind,rh FROM day1 WHERE city=? AND date=? AND time<=? AND ?<time+3",
                    (city, now, hour - 3, hour - 3))
        rows = cur.fetchall()
    for row in rows:
       t =  row[0]
       wi =  row[1]
       r =  row[2]

    return render_template('index.html',city=city,time=time, today_t=today_t, wea=wea, num=num, rh=rh, wd=wd, sd=sd, date=date,
                           min=min, max=max, w_1=w_1,w_2=w_2, s_7=s_7,t=t,wi=wi,r=r)


@app.route('/index.html')
def home():
    return index()


@app.route('/index')
def home1():
    return index()


@app.route('/starter')
def starter():
    return render_template('starter.html')


@app.route('/result', methods=['POST', 'GET'])
def result():
    if request.method == 'POST':
        result = request.form.to_dict().values()
        city = list(result)[0]

        # 如果城市为空则返回错误提示页面
        if not city:
            return render_template('error.html', message='城市名不能为空',message1='请输入城市名称')


        conc = sqlite3.connect("day1.db")
        cur = conc.cursor()
        check_sql = "SELECT COUNT(*) FROM day1 WHERE city=?"
        check_result = cur.execute(check_sql, (city,)).fetchone()
        if check_result[0] == 0:
            return render_template('error.html', message='暂无该城市数据',message1='请核对城市信息')

        cur.close()
        conc.close()


        time = []  # 当天时间
        today_t = []  # 当天温度
        wea = []  # 天气情况
        num = []  # 出现次数
        rh = []  # 当天相对湿度
        wd = []  # 当天风向
        sd = []  # 当天风速
        date = []  # 日期
        min = []  # 最低气温
        max = []  # 最高气温
        w_1 = []  # 一周白天风向
        w_2 = []  # 一周晚上风向
        w_7 = []  # 一周风向
        s_7 = []  # 一周风速

        now = datetime.datetime.now().strftime('%m-%d').replace('-0', '-')

        con1 = sqlite3.connect("day1.db")
        cur = con1.cursor()
        sql_1 = "SELECT time, temperature,rh,wind,scale FROM day1 WHERE city=? and date=?"
        data_1 = cur.execute(sql_1, (city, now))

        for item in data_1:
            time.append(item[0])
            today_t.append(item[1])
            rh.append(item[2])
            wd.append(item[3])
            sd.append(item[4])

        sql_2 = "SELECT weather,count(weather) FROM day1 WHERE city=? group by weather"
        data_2 = cur.execute(sql_2, (city,))
        for b in data_2:
            wea.append(b[0])
            num.append(b[1])
        cur.close()
        con1.close()

        con2 = sqlite3.connect("day7.db")
        cur2 = con2.cursor()

        sql_3 = "SELECT date, min,max,wind1,wind2,scale FROM day7 WHERE city=?"
        data_3 = cur2.execute(sql_3, (city,))

        for c in data_3:
            date.append(c[0])
            min.append(c[1])
            max.append(c[2])
            w_1.append(c[3])
            w_2.append(c[4])
            s_7.append(c[5])
        for w in range(len(w_1)):
            wind_7 = w_1[w] + ' ' + w_2[w]
            w_7.append(wind_7)
        cur2.close()
        con2.close()

        # 获取当前时间和日期
        ti = datetime.datetime.now()  # 获取当前时间
        hour = ti.time().hour  # 获取当前时间的时

        # 连接数据库并查询数据
        con = sqlite3.connect("day1.db")
        cur = con.cursor()
        cur.execute("SELECT temperature,wind,rh FROM day1 WHERE city=? AND date=? AND time<=? AND ?<time+3",
                    (city, now, hour, hour))
        rows = cur.fetchall()

        # 如果查询结果为空，则查询前一个时间段的数据
        if not rows:
            cur.execute("SELECT temperature,wind,rh FROM day1 WHERE city=? AND date=? AND time<=? AND ?<time+3",
                        (city, now, hour - 3, hour - 3))
            rows = cur.fetchall()
        for row in rows:
            t = row[0]
            wi = row[1]
            r = row[2]

        return render_template('index.html', city=city, time=time, today_t=today_t, wea=wea, num=num, rh=rh, wd=wd,
                               sd=sd, date=date,
                               min=min, max=max, w_1=w_1, w_2=w_2, s_7=s_7, t=t, wi=wi, r=r)


if __name__ == '__main__':
    app.run()
