# coding=utf-8
import requests
import urllib.parse

import re
from bs4 import BeautifulSoup

#主要参数
origin_url = 'http://10.5.2.80'
host = '10.5.2.80'
userAgent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.13; rv:57.0) Gecko/20100101 Firefox/57.0"


#获取成绩列表
def getGradefromsoup(grade_response):
    soup = BeautifulSoup(grade_response,'html.parser')
    grades = soup.find_all('table')[2].find_all('tr')
    scores = []

    for grade in grades:
        details = grade.find_all('td')
        score = [detail.string for detail in details]
        scores.append(score)

    for score in scores:
        score.pop(0)
        score.pop(1)
        score.pop(5)
        score.pop(5)

    new_scores=scores[::-1]
    return new_scores

#获取考试信息
def getExaminformation(exam_response):
    soup = BeautifulSoup(exam_response,'html.parser')
    infs = soup.find_all('table')[0].find_all('tr')
    exam_infs = []
    for inf in infs:
        details = inf.find_all('td')
        exam_inf = [detail.string for detail in details]
        if ''.join(exam_inf[3].split())!='':
            exam_infs.append(exam_inf)
    for item in exam_infs:
        item.pop(0)
        item.pop(1)
        item.pop(3)
    return exam_infs

    #模拟登录
def jwclogin(student_number,password,parsers):
    global host
    global origin_url
    global userAgent
    #登录初始页面
    #session方法保留cookie
    try:
        s = requests.session()
        enter_page = s.get(origin_url, timeout=5)
    except:
        print(u'教务处网页无法打开')
        return 0
    #检查登录状态
    #print(enter_page.url)
    #print(enter_page.status_code)
    #登录页面寻找__VIEWSTATE值
    enter_page_soup = BeautifulSoup(enter_page.text,'html.parser')
    __VIEWSTATE = enter_page_soup.find(id='form1').input['value']
    #检查__VIEWSTATE
    #print(__VIEWSTATE)

    #开始登录，进入主页面
    main_url = enter_page.url

    #student_number = '1120161174'
    #password = '221418'

    data_main_url = {
        "__VIEWSTATE": __VIEWSTATE,
        "TextBox1": student_number,
        "TextBox2": password,
        #请求参数头，反编码url，‘gb2312'
        "RadioButtonList1":r'%D1%A7%C9%FA',# 学生
        "Button1":r'+%B5%C7+%C2%BC+',#登录
    }
    header_main_url = {
    'User-Agent': userAgent
    }

    #开始登录
    try:
        main_page = s.post(main_url,data=data_main_url,headers=header_main_url)#检查状态 print(main_page.status_code) print(len(main_page.text))
        main_page_soup = BeautifulSoup(main_page.text,'html.parser') #登录主页面
        student_name = main_page_soup.find(id="xhxm").string #获取学生姓名
    except:
        print( u'账号或密码错误,请重新输入')
        return 0

    #获取成绩
    if parsers == '-s':
        grade_first_url = main_url[:-13]+'xscj.aspx?' #成绩页面url
        header_grade_url_1 = {
            'Accept': '*/*',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'zh-CN',
            'Connection': 'keep-alive',
            'Host': host,
            'Referer': main_url[:-13]+'xs_main.aspx?xh=' + student_number,
            "User-Agent": userAgent,
        }
        data_grade_url_1 = urllib.parse.urlencode({
            'xh': student_number,
            'xm': student_name[12:14].encode('gb2312'),
            'gnmkdm': 'N121605',
        })
        #检查状态
        #print(student_name[12:14])
        #print(grade_first_url)
        #print(grade_first_url+data_grade_url_1)
        grade_first_page = s.get(grade_first_url+data_grade_url_1, headers=header_grade_url_1)
        #检查状态
        #print(grade_first_page.status_code)

        grade_first_page.encoding = grade_first_page.apparent_encoding
        #检查状态
        #print(len(grade_first_page.text))
        __VIEWSTATE = getViewState(grade_first_page.content.decode('gb2312'))
        #print(__VIEWSTATE)
        header_grade_url_2 ={
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Cache-Control': 'max-age=0',
            'Connection': 'keep-alive',
            'Content-Length': '1493',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Host': host,
            'Origin': 'http://10.5.2.80',
            'Referer': grade_first_page.url,
            'Upgrade-Insecure-Requests': '1',
            "User-Agent": userAgent
            }
        data_grade_url_2 = urllib.parse.urlencode({
            "__VIEWSTATE": __VIEWSTATE,
            "ddlXN": "",
            "ddlXQ": "",
            "Button2": "在校学习成绩查询".encode('gb2312'),
                })
        #检查状态
        #print(data_grade_url_2)
        #print(grade_first_page.url)
        #进入成绩二级页面，历年成绩
        grade_second_page = s.post(grade_first_page.url, data=data_grade_url_2, headers=header_grade_url_2)
        #检查状态
        #print(grade_second_page.status_code,len(grade_second_page.text))
        return grade_second_page.content.decode('gb2312')

    #查询考试信息
    if parsers == '-k':
        exam_information_url = main_url[:-13] + 'xskscx.aspx?'  # 考试信息页面
        header_exam_inf_url = {
            'Accept': '*/*',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'zh-CN',
            'Connection': 'keep-alive',
            'Host': host,
            'Referer': main_url[:-13] + 'xs_main.aspx?xh=' + student_number,
            "User-Agent": userAgent,
        }
        data_exam_inf_url = urllib.parse.urlencode({
            'xh': student_number,
            'xm': student_name[12:14].encode('gb2312'),
            'gnmkdm': 'N121604',
        })
        exam_inf_page = s.get(exam_information_url + data_exam_inf_url, headers=header_exam_inf_url)
        #检查状态
        #print(exam_inf_page.status_code,len(exam_inf_page.text))
        #print(exam_inf_page.text)
        return exam_inf_page.content.decode('gb2312')

    #查询课表
    if parsers == '-t':
        Schedule_url = main_url[:-13] + 'xskbcx.aspx?'  # 考试信息页面
        header_Schedule_url = {
            'Accept': '*/*',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'zh-CN',
            'Connection': 'keep-alive',
            'Host': host,
            'Referer': main_url[:-13] + 'xs_main.aspx?xh=' + student_number,
            "User-Agent": userAgent,
        }
        data_Schedule_url = urllib.parse.urlencode({
            'xh': student_number,
            'xm': student_name[12:14].encode('gb2312'),
            'gnmkdm': 'N121603',
        })
        Schedule_page = s.get(Schedule_url + data_Schedule_url, headers=header_Schedule_url)
        # 检查状态
        return Schedule_page.content.decode('gb2312')

    #一键评教
    if parsers == '-i':
        try:
            href = main_page_soup.find_all('table')[3].find_all('a')
            pj_url = [i['href'] for i in href]
            url = main_url[:-13] + pj_url[0]
        except:
            print('该学生已评价过!')
            return 0
        head = {
            'Accept': '*/*',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'zh-CN',
            'Connection': 'keep-alive',
            'Host': host,
            'Referer': main_url[:-13] + 'xs_main.aspx?xh=' + student_number,
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': userAgent
        }
        try:
            res = s.get(url, headers=head)
        except IndexError:
             print('该学生已评价过')
             return 0
        doEvaluate(res.content.decode('gb2312'), pj_url, 0, main_url[:-13], s)

#获取__VIEWSTATE
def getViewState(response):
    view = r'name="__VIEWSTATE" value="(.+)" '
    view = re.compile(view)
    __VIEWSTATE = view.findall(response)[0]
    return __VIEWSTATE


def doEvaluate(response, pj_url, index, url, s):
    global user
    global userAgent
    __VIEWSTATE = getViewState(response)
    soup = BeautifulSoup(response,'html.parser')
    pjkc = pj_url[index][pj_url[index].find('=') + 1: pj_url[index].find('&')]  # 如(2016-2017-2)-02013024-1001945-3
    dataGird = soup.find(id='DataGrid1')
    pjkc_name = soup.find(id='pjkc').find_all('option')
    for i in pjkc_name:
        try:
            i['selected']
            print('正在评教：',i.string)
        except:
            print('',end='')
    Js1 = {}  # DataGrid1:_ctl2:JS1
    tr = dataGird.find_all('tr')
    # 设置评价
    for i in range(1, len(tr)):
        select = tr[i].find('select')
        if select is not None:
            Js1[select.get('name')] = u'优秀'.encode('gb2312')
    head = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'zh-CN,zh;q=0.8',
        'Connection': 'keep - alive',
        'Origin': host,
        'Referer': url + pj_url[0],
        'User-Agent': userAgent
    }
    data={}
    # data = collections.OrderedDict()
    data['__EVENTTARGET'] = ''
    data['__EVENTARGUMENT'] = ''
    data['__VIEWSTATE'] = __VIEWSTATE
    data['pjkc'] = pjkc
    data.update(Js1)
    data['pjxx'] = ''
    data['txt1'] = ''
    data['TextBox1'] = '0'
    data['Button1'] = u'保  存'.encode('gb2312')
    res= s.post(url+pj_url[0], data=data, headers=head)
    res = res.content.decode('gb2312')
    index += 1
    if index < len(pj_url):
        doEvaluate(res, pj_url, index, url,s)
    else:
        data['Button2'] = u'提  交'.encode('gb2312')
        res = s.post(url + pj_url[0], data=data, headers=head)
        print('该学生已完成评教，为保证安全，请登录教务处查看')

