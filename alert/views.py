from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from django.urls import reverse
from django.utils import timezone

from .models import Board
from .forms import UnknownForm
#blog/urls.py
#blog/models.py
#blog/forms.py
#blog/admin.py
#blog/views.py

#mysite/urls.py
#mysite/settings.py


###custom library
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from bs4 import BeautifulSoup
from selenium.common.exceptions import NoSuchElementException
import re
import random
#pip install selenium
#pip install bs4
#pip install regex

### static
#C:/information/post_image.jpg
#C:/information/item_image1.jpg
#C:/information/item_image2.jpg
#C:/information/item_image3.jpg
#alert/chromedriver.exe
#alert/static/
#alert/templates/
#End

# Create your views here.

def index(request):
	latest_board_list = Board.objects.order_by('board_id').reverse()
	context = {
		'latest_board_list': latest_board_list,
	}
	return render(request, 'alert/index.html', context)


def detail(request, b_id): 
	board_list = get_object_or_404(Board, board_id = b_id)
	context = {
		'board_text': board_list.board_text
	}
	return render(request, 'alert/detail.html', context)


def resetAlert(request):

	form = UnknownForm(request.POST)
	if 'chk_info' in request.POST:
		for item in request.POST.getlist('chk_info'):
			rQ = Board.objects.get(board_id = item)
			fQ = Board.objects.filter(board_id = item)
			if rQ.board_alert:
				fQ.update(board_alert = False)
			else:
				fQ.update(board_alert = True)

	return redirect(reverse('index'))



def scraping(request, page_id):
	## Chrome headless

	date_format = "%Y-%m-%d %H:%M:%S"
	print("################################")
	print(timezone.now().strftime(date_format))

	options = webdriver.ChromeOptions()
	options.add_argument('window-size=1280,1010')
	#options.add_argument('headless')
	
	driver = webdriver.Chrome(executable_path='alert/chromedriver.exe', chrome_options=options)
	idx = []
	link = []
	user = []
	date = []
	for page_id in range(1,6):
		url = "http://www.dongguk.edu/mbs/kr/jsp/board/list.jsp?boardId=3662&search=&column=&mcategoryId=0&boardType=01&listType=01&command=list&id=kr_010804000000&spage=" + str(page_id)
		print("# 페이지 로딩")
		driver.get(url)
		driver.implicitly_wait(2)

		print("# 페이지 파싱 시작")
		html = driver.page_source
		soup = BeautifulSoup(html, 'html.parser')

		print("# 데이터 테이블 만들기")
		all_board = soup.find('table', {'id' : 'board_list'})

		trs = all_board.tbody.find_all('tr')

		print("# 목록 크롤링 시작")

		for tr in trs[0:len(trs)]:
			tds = tr.find_all('td')
			id = tds[0].string
			if id == None:
				continue
			else:
				idx.append(id)
			
			tmp = tds[1].find('a', href = True)
			
			#링크이용해 게시글 내부로 이동
			link.append('http://www.dongguk.edu/mbs/kr/jsp/board/' + tmp['href'])
			
			user.append(tds[2].string.strip())
			date.append(tds[3].string.strip())
				
	print("# 목록 크롤링 완료")

	print("# 글 내용 크롤링 시작")
	title = []
	body = []
	update_date = []

	for urlTemp in link:
		driver.get(urlTemp)
		driver.implicitly_wait(1)
		htmlTemp = driver.page_source
		soupTemp = BeautifulSoup(htmlTemp, 'html.parser')
		TH = soupTemp.find('table', {'id' : 'board_view'})
		
		title.append(TH.thead.find('th').string.strip())
		
		bodyTmp = TH.tbody.find('div', {'id' : 'divView'}).get_text()
		body.append(bodyTmp.replace(u'\xa0', u' '))
		update_date.append(timezone.now().strftime(date_format))

	print("# 크롤링 완료")

	c1 = 0
	c2 = 0

	# 제목 필터링 ##############################################################
	white_list = []
	# 넣음
	black_list = ['합격', '발표']
	# 제외

	###########################################################################

	for i in reversed(range(len(idx))):
		if any(re.findall('|'.join(black_list), title[i])):
			dummy = idx.pop(i)
			dummy = title.pop(i)
			dummy = link.pop(i)
			dummy = body.pop(i)
			dummy = date.pop(i)

		
	for i in reversed(range(len(idx))):
		
		Q1 = Board.objects.filter(board_id = idx[i])

		if Q1.exists():
			Q1.update(board_title = title[i], board_url = link[i], board_text = body[i], board_date = date[i])
			c1 += 1
		
		else:
			Board.objects.create(board_id = idx[i], board_title = title[i], board_url = link[i], board_text = body[i], board_date = date[i], board_alert = False)
			c2 += 1

	driver.close()

	Q0 = Board.objects.all()
	v0 = Q0.count()

	print("## SQL ", c1, "건 갱신 완료 ##")
	print("## SQL ", c2, "건 추가 완료 ##")
	print("#### 장학공지 총 ", v0, "건")
	print("################################")


	return redirect(reverse('index'))
	

def kakao(request):

	def titling(text):
		if len(text) > 30:
			text = text[:26] + " ..."
		return text

	#카카오 플러스친구 관리자 계정 정보 #######################################
	kakao_admin_id = "ljyjh0117@naver.com"
	kakao_admin_pw = "dydrkfl7"
	#########################################################################

	today = timezone.now()
	date_format = "%Y-%m-%d %H:%M:%S"
	print("################################")
	print(today.strftime(date_format))

	options = webdriver.ChromeOptions()
	options.add_argument('window-size=1280,1010')
	#options.add_argument('headless')
	
	driver = webdriver.Chrome(executable_path='alert/chromedriver.exe', chrome_options=options)

	url = 'https://accounts.kakao.com/login?continue=https://center-pf.kakao.com/signup'
	url_1 = 'https://center-pf.kakao.com/_xaEAcxb/messages/new/widelist'
	post_number = Board.objects.filter(board_alert = False).count()
	post_howmuch = 1

	#while post_number != 0:
	#아래 #6 전까지 들여쓰기 해야함
	post_num = post_number//3
	post_ber = post_number%3

	print("# 1. 관리자 로그인 페이지 로딩")
	driver.get(url)
	driver.implicitly_wait(2)

	print("# 2. 로그인 실행")
	driver.find_element_by_id('id_email_2').send_keys(kakao_admin_id)
	driver.find_element_by_id('id_password_3').send_keys(kakao_admin_pw)

	driver.find_element_by_xpath('//*[@id="login-form"]/fieldset/div[8]/button[1]').click()
	driver.implicitly_wait(3)

	print("# 3. 장학금알림봇 관리 페이지")
	driver.find_element_by_xpath('//*[@id="mArticle"]/div[2]/div/div[2]/table/tbody/tr/td[5]/button').click()
	driver.implicitly_wait(3)

	if post_number == 1:
		print("# 4. post1번 실험")
		driver.find_element_by_xpath('//*[@id="mArticle"]/div[2]/ul/li[1]/button').click()

	else:
		print("# 4. post2번 실험")
		driver.get(url_1)
	driver.implicitly_wait(2)

	# post_number = 1 >> 기본 텍스트형 작성
	# post_number = 2, 3 >> 와이드 리스트형 작성

	#############################################################

	print("# 4. 사전 정보 편집")

	# board_id, board_title, board_url, board_text, board_date, board_alert
	bQ = Board.objects.filter(board_alert = False).order_by('board_id').first()

	if today.strftime('%p') == "AM":
		when = " 아침"
	else:
		when = " 저녁"

	post_title = '{d.month}월 {d.day}일'.format(d=today) + str(when) + " 장학공지 " + str(post_howmuch) + "차 알림"

	print(post_title)
	#테스트용
	
	###########################################################
	if post_number == 1:
		post_text = post_title + "\n\n▶ " + bQ.board_title
	# 이부분은 공지가 1개일때 텍스트로 안내하기위해 필요한 부분
	##########################################################        

	print("# 5-1. 정보 웹페이지에 입력")
	if post_number == 1:
		# 우선은 공지 1개인 경우부터 / IF문으로 경우 나누기
		driver.find_element_by_xpath('//*[@id="mArticle"]/div/form/div[1]/div[1]/div[2]/div[1]/div[2]/label/span').click()
		driver.find_element_by_xpath('//*[@id="mArticle"]/div/form/div[1]/div[1]/div[2]/div[2]/div[2]/input').send_keys("C:/information/post_image"+str(random.randrange(1,8))+".jpg")
		# 이미지 경로 수정 필요

		driver.find_element_by_xpath('//*[@id="messageWrite"]').send_keys(post_text)

		driver.find_element_by_xpath('//*[@id="mArticle"]/div/form/div[1]/div[1]/div[4]/div/div[4]/label/span').click()
		driver.find_element_by_xpath('//*[@id="btnName"]').send_keys("장학공지로 이동")
		driver.find_element_by_xpath('//*[@id="linkUpload"]').send_keys(bQ.board_url.strip('http://'))

		driver.find_element_by_xpath('//*[@id="mArticle"]/div/form/div[2]/span/button[2]').click()
		driver.implicitly_wait(2)

		post_ber = 0
		# 마지막에 num >= 1 인경우에만 리스트 3개씩 발송하게끔 작성하고 코드 끝부분에 num -= 1,
		# 그외에 num == 0 인 경우에는 리스느 1개, 2개 발송가능하게끔 중간에 IF문으로 발송하게 작성하고 코드 끝부분에 ber == 0

		bQ_id = bQ.board_id
		Board.objects.filter(board_id = bQ_id).update(board_alert = True)
		### Board.objects,~~.first() 의 board_alert => True로 전환

	else:
		post_random = random.sample(range(1,4), 3)

		if post_num >= 1:
			# 포스팅 3개인 경우 하여튼 역순으로 작성함
			driver.find_element_by_xpath('//*[@id="mArticle"]/div/form/div[1]/div[1]/div[3]/button/span').click()
			# 리스트 추가 & 리스트항목 4 작성

			driver.find_element_by_xpath('//*[@id="mArticle"]/div/form/div[1]/div[1]/div[3]/div[4]/dl/dd[1]/div[2]/div[2]/input').send_keys("C:/information/item_image"+str(post_random[0])+".jpg")
			driver.find_element_by_name('items[3].text').send_keys(titling(bQ.board_title))
			driver.implicitly_wait(1)

			driver.find_element_by_xpath('//*[@id="mArticle"]/div/form/div[1]/div[1]/div[3]/div[4]/dl/dd[3]/div[1]/div[3]/label/span').click()
			driver.implicitly_wait(1)
			driver.find_element_by_name('items[3].link.url').send_keys(bQ.board_url.strip('http://'))
			driver.implicitly_wait(2)

			post_num -= 1
			# 마지막에 num >= 1 인경우에만 리스트 3개씩 발송하게끔 작성하고 코드 끝부분에 num -= 1,
			# 그외에 num == 0 인 경우에는 리스느 1개, 2개 발송가능하게끔 중간에 IF문으로 발송하게 작성하고 코드 끝부분에 ber == 0

			bQ_id = bQ.board_id
			Board.objects.filter(board_id = bQ_id).update(board_alert = True)         
			bQ = Board.objects.filter(board_alert = False).order_by('board_id').first()
			### Board.objects,~~.first() 의 board_alert => True로 전환
			
		else:
			post_ber = 0
			# 마지막에 num >= 1 인경우에만 리스트 3개씩 발송하게끔 작성하고 코드 끝부분에 num -= 1,
			# 그외에 num == 0 인 경우에는 리스느 1개, 2개 발송가능하게끔 중간에 IF문으로 발송하게 작성하고 코드 끝부분에 ber == 0
				

		# 리스트 항목 3 작성
		driver.find_element_by_xpath('//*[@id="mArticle"]/div/form/div[1]/div[1]/div[3]/div[3]/dl/dd[1]/div[2]/div[2]/input').send_keys("C:/information/item_image"+str(post_random[1])+".jpg")
		driver.find_element_by_name('items[2].text').send_keys(titling(bQ.board_title))
		driver.implicitly_wait(1)

		driver.find_element_by_xpath('//*[@id="mArticle"]/div/form/div[1]/div[1]/div[3]/div[3]/dl/dd[3]/div[1]/div[3]/label/span').click()
		driver.implicitly_wait(1)
		driver.find_element_by_name('items[2].link.url').send_keys(bQ.board_url.strip('http://'))
		driver.implicitly_wait(2)
		
		bQ_id = bQ.board_id
		Board.objects.filter(board_id = bQ_id).update(board_alert = True)          
		bQ = Board.objects.filter(board_alert = False).order_by('board_id').first()
		### Board.objects,~~.first() 의 board_alert => True로 전환


		# 리스트 항목 2 작성
		driver.find_element_by_xpath('//*[@id="mArticle"]/div/form/div[1]/div[1]/div[3]/div[2]/dl/dd[1]/div[2]/div[2]/input').send_keys("C:/information/item_image"+str(post_random[2])+".jpg")
		driver.find_element_by_name('items[1].text').send_keys(titling(bQ.board_title))
		driver.implicitly_wait(1)

		driver.find_element_by_xpath('//*[@id="mArticle"]/div/form/div[1]/div[1]/div[3]/div[2]/dl/dd[3]/div[1]/div[3]/label/span').click()
		driver.implicitly_wait(1)
		driver.find_element_by_name('items[1].link.url').send_keys(bQ.board_url.strip('http://'))
		driver.implicitly_wait(2)


		# 리스트 항목 2를 그대로 이용해 리스트 항목 1작성
		driver.find_element_by_xpath('//*[@id="mArticle"]/div/form/div[1]/div[1]/div[3]/div[1]/dl/dd[1]/div[2]/div[2]/input').send_keys("C:/information/post_image"+str(random.randrange(1,4))+".jpg")
		driver.find_element_by_name('items[0].text').send_keys(titling(bQ.board_title))
		driver.implicitly_wait(1)

		driver.find_element_by_xpath('//*[@id="mArticle"]/div/form/div[1]/div[1]/div[3]/div[1]/dl/dd[3]/div[1]/div[3]/label/span').click()
		driver.implicitly_wait(1)
		driver.find_element_by_name('items[0].link.url').send_keys(bQ.board_url.strip('http://'))
		driver.implicitly_wait(2)

		bQ_id = bQ.board_id
		Board.objects.filter(board_id = bQ_id).update(board_alert = True)
		### Board.objects,~~.first() 의 board_alert => True로 전환

		# 제목 입력
		driver.find_element_by_id('listTitle').send_keys(post_title)
		driver.implicitly_wait(1)

		# 공유하기 버튼
		#driver.find_element_by_xpath('//*[@id="mArticle"]/div/form/div[1]/div[1]/div[5]/div/div[2]/label/span').click()

		driver.find_element_by_xpath('//*[@id="mArticle"]/div/form/div[2]/span/div/button[2]').click()
		driver.implicitly_wait(2)


	print("# 5-2. 2페이지 입력")
	driver.execute_script("window.scrollTo(0, 0)") 

	action = ActionChains(driver)
	driver.implicitly_wait(1)

	###########
	#RadiointoSpan = driver.find_element_by_xpath('//*[@id="mArticle"]/div/form/div[1]/div[1]/div[1]/div[1]/div[1]/div[1]/div/div[2]/div/label/span/span')
	#driver.implicitly_wait(1)
	#RadiointoSpan.click()
	#firstLevelMenu = driver.find_element_by_xpath('//*[@id="mArticle"]/div/form/div[1]/div[1]/div[1]/div[1]/div[1]/div[1]/div/div[2]/div[2]')
	#action.move_to_element(firstLevelMenu).perform()
	#driver.implicitly_wait(1)
	#secondLevelMenu = driver.find_element_by_xpath('//*[@id="mArticle"]/div/form/div[1]/div[1]/div[1]/div[1]/div[1]/div[1]/div/div[2]/div[2]/div[2]/ul/li/div/label/span').click()
	###### PICK! 1. 그룹지정 발송

	###########
	driver.find_element_by_xpath('//*[@id="mArticle"]/div/form/div[1]/div[1]/div[1]/div[2]/div[1]/div[2]/div/label/span/span').click()
	driver.implicitly_wait(1)
	driver.find_element_by_xpath('//*[@id="mArticle"]/div/form/div[1]/div[1]/div[1]/div[2]/div[2]/div[1]/div/div/div[2]/div/div/input').send_keys("300")
	###### PICK! 2. 전체 발송 (밑에 내려가서 새로등록한 친구 등록)

	driver.find_element_by_xpath('//*[@id="mArticle"]/div/form/div[2]/button[4]').click()
	driver.implicitly_wait(2)
	driver.find_element_by_xpath('/html/body/div[3]/div[2]/div/div/div[2]/button[2]').click()
	driver.implicitly_wait(3)

	print("# 5-3. 발송예약 완료")

	post_number = post_num*3 + post_ber
	post_howmuch += 1
	print("post_num : ", post_num, ", post_ber : ", post_ber)

	print("# 6. 웹드라이버 종료")
	driver.close()

	return HttpResponse("<script>window.open('','_parent','');window.close();window.opener.location.reload();</script>")