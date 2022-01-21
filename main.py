import hashlib
import re

import requests
import ddddocr

ocr = ddddocr.DdddOcr()
headers = {
    "Accept": "",
    "Referer": "https://www.abooky.com/member.php?mod=registerqq",
    "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; rv:11.0) like Gecko",
    "Content-Type": "application/x-www-form-urlencoded",
    "Host": "www.abooky.com",
    "DNT": "1"
}
session = requests.session()

username = ""  # 账号
password = ""  # 密码

# Server酱推送SCKEY
SCKEY = ""


def ServerChanPush():
    if len(SCKEY) > 0:
        serverchan_url = "http://sc.ftqq.com/" + SCKEY + ".send"
        # 推送标题
        text = 'abooky.com'
        # 推送内容
        desp = '已签到'
        requests.get(url=serverchan_url, params={'text': text,
                                                 'desp': desp})


def loginin(url, username, password):
    count = 0
    # 规定只尝试登录5次 防止死循环
    while count < 5:
        r = session.get(url, params={"referer": '',
                                     "mod": "logging",
                                     "action": "login"}, headers=headers).text

        # 获取loginhash
        loginhash = re.search(r'<div id="main_messaqge_(.+?)">', r).group(1).encode('ascii')
        print(loginhash)
        # 获取formhash
        formhash = re.search(r'<input type="hidden" name="formhash" value="(.+?)" />', r).group(1).encode('ascii')
        print(formhash)
        seccodehash = re.search(r'<script type="text/javascript" reload="1">updateseccode\(\'(.+?)\'', r).group(
            1).encode(
            'ascii')
        print(seccodehash)

        misc = "https://www.abooky.com/misc.php"
        print("获取验证码")
        r = session.get(misc, params={
            "mod": "seccode",
            "action": "update",
            "idhash": seccodehash,
            "modid": "member::logging"
        }, headers=headers).text
        veriflyimageGIF = "https://www.abooky.com/" + str(re.search(r'width="100" height="30" src="(.+?)"', r).group(1))

        r = session.get(veriflyimageGIF, headers=headers)
        res = ocr.classification(r.content)  # 验证码结果

        # 进行验证验证码是否识别成功
        r = session.get(misc, params={
            "mod": "seccode",
            "action": "check",
            "inajax": "1",
            "idhash": seccodehash,
            "modid": "member::logging",
            "secverify": res
        }, headers=headers).text
        if re.search(u"succeed", r):
            print("验证码识别成功")

            post_data = {
                "formhash": formhash,
                "questionid": "0",
                "answer": "",
                "username": username,
                "password": password,
                "referer": "https://www.abooky.com/./",
                "seccodehash": seccodehash,
                "seccodemodid": "member::logging",
                "seccodeverify": res
            }

            # 执行登录
            session.post(url, params={'mod': 'logging',
                                      'action': 'login',
                                      'loginsubmit': 'yes',
                                      'loginhash': loginhash,
                                      'inajax': 1}, data=post_data, headers=headers)

            # 获取签到页面的formhash
            r = session.get(url='https://www.abooky.com/plugin.php?id=k_misign:sign').text
            formhash = re.search(r'<input type="hidden" name="formhash" value="(.+?)" />', r).group(1).encode('ascii')

            # 执行签到
            url = "https://www.abooky.com/plugin.php"
            params = {'id': "k_misign:sign",
                      'operation': 'qiandao',
                      'formhash': formhash,
                      'format': 'empty',
                      'inajax': 1,
                      'ajaxtarget': 'JD_sign'}
            checkin = session.get(url=url, params=params, headers=headers)
            if checkin.status_code == 200:
                print("签到成功")
                ServerChanPush()
            break
        if re.search(u"invalid", r):
            print("验证码识别失败")
            print("重新运行")
            count += 1


# 加密密码
def passwordHex(password):
    return hashlib.md5(password.encode("utf-8")).hexdigest()


if __name__ == '__main__':
    url = "https://www.abooky.com/member.php"
    loginin(url, username, passwordHex(password))
