# coding: utf-8
import requests
import re
from workflow import Workflow3
import argparse
import commands
from threading import Thread, Lock
from multiprocessing import Pool
import base64

import sys
reload(sys)
sys.setdefaultencoding('utf8')

def ping_ip(idx, ip):
    ''' ping 3 次输入的ip, 3次操作超过3s超时中断，返回无穷大
        返回 3 次 ping 的平均值

        param:
            idx: server序号
            ip: ip地址
    '''
    ping_info = commands.getoutput('ping -c 3 -t 3 ' + ip)
    connected = re.findall(r'\b(\d)\b packets received', ping_info)
    if connected[0] == '0':  # fail
        return [idx, float('inf'), '0']
    else:
        avg_time = float(re.findall(
            r'stddev = [\d|.]+/([\d|.]+)', ping_info)[0])
        return [idx, avg_time, connected[0]]


def pa(username, password):
    s = requests.Session()
    s.headers = {
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
    "accept-encoding": "gzip, deflate, br",
    "accept-language": "zh-CN,zh;q=0.8,en;q=0.6",
    "dnt": "1",
    "referer": "https://www.kycloud.co/",
    "upgrade-insecure-requests": "1",
    "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.78 Safari/537.36"
    }

    data = {'username': username, 'password': password}
    z1 = s.post(url="https://www.kycloud.co/dologin.php",
                data=data)  # 登陆后的网页界面抓取
    userid = re.findall(pattern=r'action=productdetails&id=(\d+)', string=z1.content)[0]

    link2 = 'https://www.kycloud.co/clientarea.php?action=productdetails&id=' + userid  # 服务器列表界面
    z2 = s.get(url=link2)
    info = z2.content

    # 流量
    traffic = re.findall(pattern=r'\d+.\d+.GB', string=info)
    duedate = re.findall(pattern=r'下次付款日期 / (.*)</p>',
                         string=info)[0].split('/')  # 日，月，年
    passwd = re.findall(pattern=r"innerHTML='(\d+)", string=info)[0]
    port = re.findall(pattern=r"端口编号.*?(\d+)", string=info)[0]
    method = re.findall(pattern=r"加密方式</strong>(.*\d+)", string=info)[0]
    protocol = re.findall(pattern=r'协议插件</strong>(.*)</li>', string=info)[0]
    obfs = re.findall(pattern=r'混淆插件</strong>(.*)</li>', string=info)[0]

    ss = re.findall(r'data-qrcode="(.*)" title="原版', info)
    ssr = re.findall(r'data-qrcode="(.*)" title="SSR', info)


    def name_prefix(name):
        if '中国' in name:
            return '🇨🇳' + name
        elif '台湾' in name:
            return '🇨🇳' + name
        elif '新加坡' in name:
            return '🇸🇬' + name
        elif '日本' in name:
            return '🇯🇵' + name
        elif '香港' in name:
            return '🇭🇰' + name
        elif '英国' in name:
            return '🇬🇧' + name
        elif '韩国' in name:
            return '🇰🇷' + name
        elif '美国' in name:
            return '🇺🇸' + name
        elif '俄罗斯' in name:
            return '🇷🇺' + name
        else:
            return '🗺' + name

    servers = re.findall(
        pattern=r'<h4>(.*)</h4>\s+<code>(.*)</code>\s+<p>(.*)</p>', string=info)
    servers = [list(item) for item in servers]  # tuple -> list

    # s[0]: 主机名 s[1]: IP s[2]: 流量是否超了
    # server有n个元素，每个元素又有以上3个元素
    for s in servers:
        s[0] = name_prefix(re.sub(' ', '-', s[0]))
        a = re.findall(pattern=r':(.*)】', string=s[2])
        if a:
            s[0] = s[0] + '(' + a[0] + 'T)'
        b = re.search(pattern=r'流量已超', string=s[2])
        if b:
            s[2] = '->流量爆啦！'
        else:
            s[2] = ''

    return servers, traffic, duedate, passwd, port, method, protocol, obfs, ss, ssr


def main(wf):
    parser = argparse.ArgumentParser()
    parser.add_argument('--setkey', dest='userinfo', nargs='?', default=None)
    parser.add_argument('query', nargs='?', default=None)
    args = parser.parse_args(wf.args)

    if args.userinfo:
        wf.settings['userinfo'] = args.userinfo
        return 0

    userinfo = wf.settings.get('userinfo', None)
    if not userinfo:
        wf.add_item('还没录入你的用户信息呢！',
                    '请使用 yyset 来键入你的优越用户信息',
                    valid=False)
        wf.send_feedback()
        return 0
    else:
        username, userpasswd = str(userinfo).split(' ')

    query = args.query

    # 缓存，每60s更新一次，免得多次获取
    def wrapper():
    # cached_data 第二个参数为函数，是不能接收参数的，所以要wrap一下
        return pa(username, userpasswd)
    try:
        info = wf.cached_data('post', wrapper, max_age=60 * 10)
        servers, traffic, duedate, passwd, port, method, protocol, obfs, ss, ssr = info
    except:
        wf.add_item('Error',
                    '是不是用户信息输错了?键入yyset重新录入吧',
                    valid=False, icon='error.png')
        wf.send_feedback()
        return 0

    # ping ip
    if query == 'ping':
        wf.add_item(title='*****Ping结果****', subtitle='每个IP均ping三次，取平均值排序',
                valid=False, icon='1.png')
        p = Pool(len(servers))
        data = []  # 多线程坑爹，对同一个list访问，容易冲突; 多进程有不能在函数用list，否则一直是一个
        for idx, server in enumerate(servers):
            data.append(p.apply_async(ping_ip, args=(idx, server[1])))
        p.close()
        p.join()
        ping_result = [res.get() for res in data]

        ping_result.sort(key=lambda x: x[1])  # 按ping值由小到大排序

        for i in range(len(ping_result)):
            sort_idx = ping_result[i][0]
            title = '{:.2f}  ms {}{}'.format(ping_result[i][1], servers[sort_idx][0], servers[sort_idx][2])
            subtitle = '[丢包率:{:.0f}%] IP:{}, port:{}, encryption: {}'.format(
                (1 - float(ping_result[i][2]) / 3) * 100, servers[sort_idx][1], port, method)
            wf.add_item(title=title, subtitle=subtitle, arg='ss://' + base64.b64encode(ss[sort_idx]) + 'bound' + 'ssr://' + base64.b64encode(ssr[sort_idx]),
                valid=True, icon='1.png')

    elif query == 'surge':
        surge_conf = ''
        server_name = ''
        for i, server in enumerate(servers):
            if i == len(servers) - 1:
                surge_conf = surge_conf + server[0] +  ' = custom, ' + server[1] + ', ' + port + ', ' + method + ', ' + passwd + ', http://abclite.cn/SSEncrypt.module'
                server_name = server_name + server[0]
            else:
                surge_conf = surge_conf + server[0] +  ' = custom, ' + server[1] + ', ' + port + ', ' + method + ', ' + passwd + ', http://abclite.cn/SSEncrypt.module' + '\n'
                server_name = server_name + server[0] + ', '
        wf.add_item(title='Surge配置信息生成', subtitle='点击fn或者ctrl依次复制相应配置信息', arg=surge_conf + 'bound' + server_name,
                valid=True, icon='surge.png')

    elif query == 'update':
        wf.add_item('是否检查更新?', '回车开始检查更新并自升级',
                autocomplete='workflow:update',
                icon='update.png')
        wf.send_feedback()
        return

    else:
        wf.add_item(
                title='已用流量:{0}, 剩余流量:{1}'.format(traffic[0], traffic[1]), subtitle='套餐: 100G  下次付费日期: ' + duedate[2] + '年' + \
                duedate[1] + '月' + duedate[0] + '日' , arg='arg',
                valid=False, icon='2.png')

        for i, s in enumerate(servers):
            title = s[0] + s[2]
            subtitle = 'IP:{0}, port:{1}, encryption: {2}'.format(s[1], port, method)
            # valid=True tells that the item is actionable and the arg value is the value it will pass
            # to the next action
            wf.add_item(
                title=title, subtitle=subtitle, arg='ss://' + base64.b64encode(ss[i]) + 'bound' + 'ssr://' + base64.b64encode(ssr[i]),
                valid=True, icon='1.png')

    wf.send_feedback()
    return


if __name__ == '__main__':
    wf = Workflow3(update_settings={
        'github_slug': 'wizyoung/workflows.kyoyue',
        'frequency': 1
    })
    if wf.update_available:
        wf.add_item('有新版本',
                '回车开始更新',
                autocomplete='workflow:update',
                icon='update.png')
    sys.exit(wf.run(main))
