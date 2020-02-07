import requests
from bs4 import BeautifulSoup
import re
from fake_useragent import UserAgent
import threading

booksurl = 'https://search.books.com.tw/search/query/key/'
keyword = ''

kingurl = 'https://www.kingstone.com.tw/search/search?q='
headers={'user-agent':'Mozilla/5.0'}

blist = []
klist = []

def showbooks(url): #取得博客來資訊並加入list
	books_res = requests.get(url,headers=headers)
	books_res.encoding = "utf-8"
	books_soup = BeautifulSoup(books_res.text, 'html.parser')

	items = books_soup.select('.item')
	for item in items:
		title = [i.get("title") for i in item.select('h3 a')][0]
		allprice = item.select('span.price strong b')
		img = str(item.find_all(attrs={'data-original': True}))
		imgs = img[img.find('https://im1.book.com.tw/image'):-28].replace('amp;','')
		addr = str(item.select('h3 a'))
		add = addr[addr.find('item/')+5:addr.find('/page')]

		if len(allprice)>1:
			sale = int(str(allprice[0])[3:-4])
			price = int(str(allprice[1])[3:-4])
		else:
			sale = ''
			price = int(str(allprice[0])[3:-4])

		blist.append([title,price,sale,add,imgs])

		


def showking(url): #取得金石堂資訊並加入list
	king_res = requests.get(url,headers=headers)
	king_res.encoding = "utf-8"
	king_soup = BeautifulSoup(king_res.text, 'html.parser')

	items = king_soup.select('.displayunit')
	reg = re.compile('<[^>]*>')
	
	for item in items:
		title = reg.sub('',str(item.select('h3 a')[0]))
		price = item.select('.buymixbox span b')
		sale = ''
		img = str(item.select('.coverbox img'))
		imgs = img[img.find('src="')+5:img.find('.jpg"')+4]
		addr = str(item.select('.pdnamebox a')).replace('amp;','')
		addrnum = addr[addr.find('ic/')+3:addr.find('?zo')]


		if len(price)>1:
			sale = int(reg.sub('',str(price[0])))
			price = int(str(price[1])[3:-4])
		else:
			sale = ''
			price = int(str(price[0])[3:-4])

		addr = 'https://www.kingstone.com.tw/basic/' + addrnum + '?zone=book&lid=search&actid=WISE'
		klist.append([title,price,sale,addr,imgs])


def GetBookspages(url): #獲取博客來結果頁數
	books_res = requests.get(url,headers=headers)
	books_res.encoding = "utf-8"
	books_soup = BeautifulSoup(books_res.text, 'html.parser')
	
	try:
		pages = int(books_soup.select('.page span')[0].text)
	except:
		pages = 1

	return pages

def GetKingpages(url): #獲取金石堂結果頁數
	res = requests.get(url,headers=headers)
	res.encoding = "utf-8"
	soup = BeautifulSoup(res.text, 'html.parser')
	tmp = str(soup.select('.totalcolumn'))
	try:
		pages = int(tmp[tmp.find('>/',70)+2:-7].strip())
	except:
		pages = 1

	return pages

def Showpages(url,mode,pages): #逐頁呼叫抓取資料
	if pages > 5: #頁數限制不然會爆
		pages = 5

	if pages > 1: 
		for page in range(1,pages+1):
			print("第" + str(page) + "頁")
			pageurl = url + mode + str(page)
			showitems(url,mode)
	else:
		showitems(url,mode)

def showitems(url,mode):
	if mode == '&page=':
		showking(url)
	else:
		showbooks(url)

def SetTheard(key): #進行關鍵字資料抓取
	if blist != []:
		blist.clear()

	bookspages = threading.Thread(target=Showpages(booksurl + key,'/page/',GetBookspages(booksurl + key)))
	bookspages.start()

	kingpages = threading.Thread(target=Showpages(kingurl + key,'&page=',GetKingpages(kingurl + key)))
	kingpages.start()


import tkinter as tk
import tkinter.font as tkFont
import PIL
from PIL import ImageTk
from PIL import Image
import os
import webbrowser

# 建立主視窗
window = tk.Tk()
window.title('平台爬蟲比價系統-ADT105126')
window.geometry('1220x700')
window.resizable(False,False)


#字體設定
h1 = tkFont.Font(family='微軟正黑體', size=20, weight=tkFont.BOLD)
h2 = tkFont.Font(family='微軟正黑體', size=12)

#區域:關鍵字搜尋
enterkey = tk.Entry(window,width=60,font=h2)
enterkey.grid(row=1,column=0,columnspan=2,pady=20,ipady=3)

title = tk.Label(window,text='博客來-金石堂 比價查詢',font=h1,fg="blue")
title.grid(row=0,column=0,columnspan=2,pady=5)

content = tk.StringVar()
content.set(('請於上方鍵入關鍵字'))

#功能:關鍵字搜尋
def search():
	key = enterkey.get()
	SetTheard(key)
	printlist()


ebut = tk.Button(window,text='GO!',command=search,font=h2,bg='blue',fg='white')
ebut.grid(row=1,column=1,columnspan=2,padx=20)

#區域:兩個主要ListBox
lbb = tk.Listbox(window,width=82,height=20)
lbb.grid(row=3,column=0,padx=20)

scrollb = tk.Scrollbar(window,orient="horizontal")
scrollb.config(command=lbb.xview)
lbb.config(xscrollcommand=scrollb.set)
scrollb.grid(row=4,column=0)

lbk = tk.Listbox(window,width=82,height=20)
lbk.grid(row=3,column=1)


text = tk.Label(window,text='註：單擊選單項目顯示詳細資料，雙擊選單項目即可開啟商品網頁')
text.grid(row=4,column=0,columnspan=2,stick='E')

#區域:詳細資料布局
df = tk.LabelFrame(window,text="詳細資料")
df.grid(row=5,column=0,columnspan=2,ipadx=10,ipady=5,pady=10)

detail = tk.Label(df,wraplength=400,justify='left',text='商品名稱',font=h2)
detail.grid(row=0,column=1,stick='E')

dprice = tk.Label(df,text='$價格',font=h1,fg="red")
dprice.grid(row=2,column=1,stick='E')

#url_text
'''durl = tk.Label(df,text='url',wraplength=400,justify='left')
durl.grid(row=3,column=0,columnspan=2,stick='E')'''

imgs  = tk.Label(df,text='img:',image='')
imgs.grid(row=0,column=0,rowspan=3,stick='W',padx=8)

#顯示圖片
def Simgurl(imgurl):
	im = Image.open(requests.get(imgurl,stream=True).raw)
	img = ImageTk.PhotoImage(im.resize((100,100), Image.ANTIALIAS))
	imgs.configure(image=img)
	imgs.image = img

#功能:顯示詳細資料
def pollb(self):
	selected = lbb.curselection()
	try:
		detail.config(text=blist[selected[0]][0] ,font=h2)
		strp = str(blist[selected[0]][2])+"折 "+str(blist[selected[0]][1])+"元"
		dprice.config(text=strp)
		Simgurl(blist[selected[0]][4])
	except:
		pass

def pollk(self):
	selected = lbk.curselection()
	try:
		detail.config(text=klist[selected[0]][0],font=h2)
		strp = str(klist[selected[0]][2])+"折 "+str(klist[selected[0]][1])+"元"
		dprice.config(text=strp)
		Simgurl(klist[selected[0]][4])
	except:
		pass

#雙擊選單事件
def click(self):
	webbrowser.open(klist[lbk.curselection()[0]][3])

def clicb(self):
	url = 'https://www.books.com.tw/products/'+blist[lbb.curselection()[0]][3]
	webbrowser.open(url)

#listbox功能:印出項目
def printlist():
	lbb.delete(0,'end')
	lbk.delete(0,'end')

	for bitem in blist:
		if bitem[2] == '':
			lbb.insert('end',"$%4d" % bitem[1] + " (原價)＊– " + bitem[0])

		else:
			lbb.insert('end',"$%4d" % bitem[1] + " (%2d折)＊– " % bitem[2] + bitem[0])

	for kitem in klist:
		if kitem[2] == '':
			lbk.insert('end',"$%4d" % kitem[1] + " (原價)＊– " + kitem[0])

		else:
			lbk.insert('end',"$%4d" % kitem[1] + " (%2d折)＊– " % kitem[2] + kitem[0])


#選單互動事件
lbb.bind('<<ListboxSelect>>',pollb)
lbk.bind('<<ListboxSelect>>',pollk)
lbb.bind('<Double-Button-1>',clicb)
lbk.bind('<Double-Button-1>',click)

# 運行主程式
window.mainloop()