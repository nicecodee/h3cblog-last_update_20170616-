# -*- coding: UTF-8 -*-
from flask import Flask, render_template, flash, request, url_for, session,redirect, session, send_from_directory
#from flask.ext.sqlalchemy import SQLAlchemy
from wtforms import Form, BooleanField, TextField, PasswordField, validators, RadioField, SubmitField
from wtforms.validators import DataRequired, Length
from passlib.hash import sha256_crypt
from MySQLdb import escape_string as thwart
import gc
import datetime, time
from functools import wraps
import os
import requests
import sys 
import shutil
from werkzeug import secure_filename
from dbconnect import connection
from config import SECRET_KEY, instance_path, LOGS_PATH,SERVER_DOCS_PATH, NETWORK_DOCS_PATH, INVENTORY_DOCS_PATH, \
      DOCS_PATH, UPLOAD_FOLDER, ALLOWED_EXTENSIONS,WEEKLY_PATH,WEEKLY_NAMELIST_PATH


app = Flask(__name__)
# app.instance_path=instance_path
app.secret_key=SECRET_KEY         
app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024  #限制文件上传大小(10M)

#use SQLAlchemy to manage mysql
# app.config['SQLALCHEMY_DATABASE_URI'] =  'mysql://root:jxlgood@localhost/h3cblog'    
#app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
#db = SQLAlchemy(app)


#check if user has logged in(it needs to be defined before other functions)
def login_required(f):
	@wraps(f)
	def wrap(*args, **kwargs):
		if 'logged_in' in session:
			return f(*args, **kwargs)
		else:
			#record the url I want to access
			# session["want_url"] = request.url
			
			flash(u'请您先登陆！')
			return redirect(url_for('login_page'))			
			
	return wrap

	
class WhiteboardForm(Form):
	name = TextField(u'姓名', [validators.Required()])
	day6_am = TextField(u'周六上午' )
	day6_pm = TextField(u'周六下午' )
	day7_am = TextField(u'周日上午' )
	day7_pm = TextField(u'周日下午' )
	day1_am = TextField(u'周一上午' )
	day1_pm = TextField(u'周一下午' )
	day2_am = TextField(u'周二上午' )
	day2_pm = TextField(u'周二下午' )
	day3_am = TextField(u'周三上午' )
	day3_pm = TextField(u'周三下午' )	
	day4_am = TextField(u'周四上午' )
	day4_pm = TextField(u'周四下午' )	
	day5_am = TextField(u'周五上午' )
	day5_pm = TextField(u'周五下午' )
	submit1 = SubmitField('submit')

class AddmemberForm(Form):
	name = TextField(u'添加姓名(至最后一行)', [validators.Required()])
	
class DelmemberForm(Form):
	name = TextField(u'删除姓名', [validators.Required()])
	
@app.route("/wb-thisweek/")
def wb_thisweek():
	try:
		set_cn_encoding()	
		
		#calculate the weekdays based on today's date automatically
		today = datetime.date.today()
		start = today + datetime.timedelta(-2 - today.weekday())
		weekdays = []
		for i in range(7):
			tmp_weekday = start + datetime.timedelta(days = i)
			weekdays.append(tmp_weekday)
		
		#fillin the weekly form based on the record automatically
		path = WEEKLY_PATH + 'weekly_' + str(start)
		namelist_path = WEEKLY_NAMELIST_PATH + 'namelist'
		if not os.path.isfile(path):
			shutil.copy(namelist_path,  path)				
		with open(path, 'r') as file:
			name_lines = file.readlines()
		filedata = []
		num = len(name_lines)
		for x in range(num):
			filedata.append(name_lines[x].split(" "))		
		
		return render_template("wb-thisweek.html", title=u'本周白板',num=num, weekdays=weekdays,filedata=filedata)
		
	except Exception as e:
		return(str(e))

# 已弃用：独立页面的白板更新(不能通过点击人名跳转到更新页面，对应于wb-update(独立页面).html）
# @app.route("/wb-update/", methods = ['GET','POST'])  
# def wb_update():
	# try:
		# set_cn_encoding()	
		
		# #calculate the weekdays based on today's date automatically
		# today = datetime.date.today()
		# start = today + datetime.timedelta(-2 - today.weekday())
		# weekdays = []
		# for i in range(7):     #计算该周的所有日期
			# tmp_weekday = start + datetime.timedelta(days = i)
			# weekdays.append(tmp_weekday)
			
		# form = WhiteboardForm(request.form)
		# if request.method == "POST" and form.validate():
			# name = form.name.data
			# day6_am = form.day6_am.data
			# day6_pm = form.day6_pm.data
			# day7_am = form.day7_am.data
			# day7_pm = form.day7_pm.data
			# day1_am = form.day1_am.data
			# day1_pm = form.day1_pm.data
			# day2_am = form.day2_am.data
			# day2_pm = form.day2_pm.data
			# day3_am = form.day3_am.data
			# day3_pm = form.day3_pm.data
			# day4_am = form.day4_am.data
			# day4_pm = form.day4_pm.data
			# day5_am = form.day5_am.data
			# day5_pm = form.day5_pm.data
			
			# old_path = WEEKLY_PATH + 'weekly_' + str(start)
			# new_path = WEEKLY_PATH + 'tmp.log'			
			# data = name + ' ' + day6_am	 + ' ' + day6_pm  + ' ' + day7_am + ' ' + day7_pm  + ' ' \
			# + day1_am + ' ' + day1_pm + ' ' + day2_am + ' ' + day2_pm + ' ' + day3_am + ' ' \
			# + day3_pm + ' ' + day4_am + ' ' + day4_pm + ' ' + day5_am + ' ' + day5_pm
			
			# with open(old_path, 'r') as f, open(new_path, 'w') as fout:
				# NAME_EXIST = 0
				# for line in f:
					# if line.startswith(name):
						# line = data + '\n'
						# NAME_EXIST = 1
					# fout.write(line)  
				# if NAME_EXIST == 1:
					# os.rename(new_path, old_path)
					# return redirect(url_for('wb_thisweek')) #return to wb_thisweek if NAME_EXIST = 1
				# else:
					# return redirect(url_for('wb_update'))	#return to wb_update if NAME_EXIST = 0
		# return render_template("wb-update.html", title=u'更新白板', form=form, weekdays=weekdays)
		
	# except Exception as e:
		# return(str(e))		

#可通过点击人名，跳转到白板更新页面
@app.route('/wb-update/<name>/')
@app.route("/wb-update/") 
@app.route('/wb-update/<name>/', methods = ['GET','POST'])
def wb_update(name):
	try:
		set_cn_encoding()	
		
		#calculate the weekdays based on today's date automatically
		today = datetime.date.today()
		start = today + datetime.timedelta(-2 - today.weekday())
		weekdays = []
		for i in range(7):     #计算该周的所有日期
			tmp_weekday = start + datetime.timedelta(days = i)
			weekdays.append(tmp_weekday)

		#fillin the weekly form based on the name automatically
		path = WEEKLY_PATH + 'weekly_' + str(start)		
		with open(path, 'r') as file:
			for line in file:
				if line.startswith(name):
					data_line=line
					filedata = []
					filedata.append(data_line.split(" "))
					break

		#update personal whiteboard	
		form = WhiteboardForm(request.form)
		if request.method == "POST":
			halfday = range(14)		#用列表存储用户填入的数据		
			halfday[0] = request.form['halfday0']
			halfday[1] = request.form['halfday1']
			halfday[2] = request.form['halfday2']
			halfday[3] = request.form['halfday3']
			halfday[4] = request.form['halfday4']
			halfday[5] = request.form['halfday5']
			halfday[6] = request.form['halfday6']
			halfday[7] = request.form['halfday7']
			halfday[8] = request.form['halfday8']
			halfday[9] = request.form['halfday9']
			halfday[10] = request.form['halfday10']
			halfday[11] = request.form['halfday11']
			halfday[12] = request.form['halfday12']
			halfday[13] = request.form['halfday13']
			
			old_path = WEEKLY_PATH + 'weekly_' + str(start)
			new_path = WEEKLY_PATH + 'tmp.log'		
			
			#把空白内容转换为“- ”，非空白内容后面添加一个空格
			for i in range(14):
				if not halfday[i]:
					halfday[i] = "- "
				else:
					halfday[i] = halfday[i] + " "	
			#列表转换为字符串
			halfday="".join(halfday)
			#旧文件换行复制到新文件，遇到需更新的名字时，替换那一行，再写到新文件
			with open(old_path, 'r') as f, open(new_path, 'w') as fout:
				for line in f:
					if line.startswith(name):  #找到匹配的名字，用填在表格的data替换这一行
						line = name + " " + halfday + '\n'
					fout.write(line)  
				os.rename(new_path, old_path)  #新文件改回为原文件的名字
			return redirect(url_for('wb_update', name=name))	 
		return render_template("wb-update.html", title=u'更新白板', form=form, weekdays=weekdays, filedata=filedata)
		
	except Exception as e:
		return(str(e))			
		
		
		
@app.route("/wb-add-member/", methods = ['GET','POST'])
def wb_add_member():
	try:
		set_cn_encoding()	
		
		#取得weekly目录下的所有文件（列表）
		files = os.listdir(WEEKLY_PATH)
		#列表按文件名排序，让最新的weekly_xxxx-xx-xx成为列表第一个元素
		files.sort(reverse = True)  
		
		
		form = AddmemberForm(request.form)
		path = WEEKLY_NAMELIST_PATH + 'namelist'
		
		if request.method == "POST" and form.validate():
			name = form.name.data
			data = name + ' - - - - - - - - - - - - - -'
			#在namelist.log里添加该成员
			with open(path, 'ab') as f:
				f.write(data + '\n') 	
			#在最新的weekly_xxxx-xx-xx里添加该成员	
			with open(WEEKLY_PATH+files[0], 'ab') as f:
				f.write(data + '\n') 				
				
			return redirect(url_for('wb_thisweek'))	 

		return render_template("wb-add-member.html", title=u'增加成员', form=form)
		
	except Exception as e:
		return(str(e))	

@app.route("/wb-del-member/", methods = ['GET','POST'])
def wb_del_member():
	try:
		set_cn_encoding()	
		
		#取得weekly目录下的所有文件（列表）
		files = os.listdir(WEEKLY_PATH)
		#列表按文件名排序，让最新的weekly_xxxx-xx-xx成为列表第一个元素
		files.sort(reverse = True)  		
		
		form = DelmemberForm(request.form)
		old_path_namelist = WEEKLY_NAMELIST_PATH + 'namelist'
		new_path_namelist = WEEKLY_NAMELIST_PATH + 'tmpfile.log'
		
		old_path_weekly = WEEKLY_PATH + files[0]
		new_path_weekly = WEEKLY_PATH + 'tmp.log'		
		
					
		if request.method == "POST" and form.validate():
			name = form.name.data
			#删除namelist.log里的该成员
			with open(old_path_namelist, 'r') as f, open(new_path_namelist, 'w') as fout:
				for line in f:
					name_str = line.split()[0]  #截取姓名
					if not name == name_str:    #仅当姓名完全匹配时，执行以下步骤
						fout.write(line)  
			os.rename(new_path_namelist, old_path_namelist)  #新文件改名为旧文件（相当于覆盖旧文件）
			#删除最新的weekly_xxxx-xx-xx里的该成员		
			with open(old_path_weekly, 'r') as f, open(new_path_weekly, 'w') as fout:
				for line in f:
					name_str = line.split()[0]  #截取姓名
					if not name == name_str:    #仅当姓名完全匹配时，执行以下步骤
						fout.write(line)  
			os.rename(new_path_weekly, old_path_weekly)		#新文件改名为旧文件（相当于覆盖旧文件）		
				
			return redirect(url_for('wb_thisweek'))	 

		return render_template("wb-del-member.html", title=u'删除成员', form=form)
		
	except Exception as e:
		return(str(e))	

		
@app.route("/wb-list/")
def wb_list():

	#Get number of weekly whiteboards
	num_wb = (sysadm_badges_number())[3]

	list = []
	#取得weekly目录下的所有文件（列表）
	files = os.listdir(WEEKLY_PATH)
	#列表按文件名排序
	files.sort(reverse = True)  
	for weeklyfile in files:
		list.append(weeklyfile)
	return  render_template("wb-list.html", title=u'白板列表', num_wb=num_wb, list=list)		

@app.route('/wb-review/<filename>/')
@app.route("/wb-review/") 
def wb_review(filename):
	try:
		set_cn_encoding()	
		
		fn = filename
		#Get number of weekly whiteboards
		num_wb = (sysadm_badges_number())[3]
		
		
		list = []
		#取得weekly目录下的所有文件（列表）
		files = os.listdir(WEEKLY_PATH)
		#列表按文件名排序,显示在页面左栏
		files.sort(reverse = True)  
		for weeklyfile in files:
			list.append(weeklyfile)		
		
		#根据文件名（如：weekly_2017-03-21），截取得到该周起始日期（2017-03-21）
		start = filename.split("_")[1]
		start_day = datetime.datetime.strptime(start, '%Y-%m-%d')  #字符串转换为时间格式(2017-03-21 00:00:00)
		weekdays = []
		for i in range(7):     #计算该周的所有日期
			tmp_weekday = start_day + datetime.timedelta(days = i)
			tmp_weekday = (str(tmp_weekday)).split()[0]  #只截取日期（即只截取 2017-03-21 00:00:00 的部分)
			weekdays.append(tmp_weekday)
				
		#fillin the weekly form based on the record automatically
		path = WEEKLY_PATH + fn			
		with open(path, 'r') as file:
			name_lines = file.readlines()

		filedata = []
		num = len(name_lines)

		for x in range(num):
			filedata.append(name_lines[x].split(" "))		
		
		return render_template("wb-review.html", title=u'白板回顾', num=num, num_wb=num_wb, \
		       list=list, fn=fn, weekdays=weekdays, filedata=filedata)
		
	except Exception as e:
		return(str(e))

	
#get the location from user's ip
def get_ip_info(ip):
	
	ip_info = ''
	#淘宝IP地址库接口
	r = requests.get('http://ip.taobao.com/service/getIpInfo.php?ip=%s' %ip)
	if  r.json()['code'] == 0 :
		i = r.json()['data']

		country = i['country']  #国家 
		# area = i['area']        #区域
		region = i['region']    #地区
		city = i['city']        #城市
		isp = i['isp']          #运营商
		
		ip_info = country + '/' + region + '/' + city + '/' + isp
	return ip_info
		
	
#solve the chinese code problem
def	set_cn_encoding():
	reload(sys)
	sys.setdefaultencoding('utf-8')


#create dir tree-view
def make_tree(path):
    tree = dict(name=os.path.basename(path), children=[])
    try: lst = os.listdir(path)
    except OSError:
        pass #ignore errors
    else:
        for name in lst:
            fn = os.path.join(path, name)
            if os.path.isdir(fn):
                tree['children'].append(make_tree(fn))
            else:
                tree['children'].append(dict(name=name))
    return tree	
	
	
#calculate the number of docs of different type for badges displaying
def docs_badges_number():
	try:	
		server_list = []
		network_list = []
		inventory_list = []
		for server_file in os.listdir(SERVER_DOCS_PATH):
			server_list.append(server_file)
		for netowrk_file in os.listdir(NETWORK_DOCS_PATH):
			network_list.append(netowrk_file)
		for inventory_file in os.listdir(INVENTORY_DOCS_PATH):
			inventory_list.append(inventory_file)
		num_server = len(server_list)
		num_network = len(network_list)
		num_inventory = len(inventory_list)	
		
		return(num_server, num_network, num_inventory)
		
	except Exception as e:
		return str(e)
	
	
#calculate the number of logs/users/docs for 'sya-admim' badges displaying
def sysadm_badges_number():
	try:
		#Get number of logs and display it with "bootstrap badge"
		loglist = []
		for logfile in os.listdir(LOGS_PATH):
			loglist.append(logfile)
		num_logs = len(loglist)
		
		#Get number of users and display it with "bootstrap badge"
		c, conn = connection()
		c.execute("SELECT * from login_user;")
		num_users = int(c.rowcount)
		
		#Get number of docs and display it with "bootstrap badge"
		num_docs = sum([len(files) for root,dirs,files in os.walk(DOCS_PATH)])
		
		#Get number of weekly whiteboards and display it with "bootstrap badge"
		wblist = []
		for weeklyfile in os.listdir(WEEKLY_PATH):
			wblist.append(weeklyfile)
		num_weeklys = len(wblist)
		
		return(num_logs, num_users, num_docs, num_weeklys)
	except Exception as e:
		return str(e)
	
	
	
#do the logging when a user logs in
def write_log_info(info_type):
	try:
		c, conn = connection()
		
		timestr_filename = time.strftime("%Y%m%d", time.localtime())
		path = LOGS_PATH + 'user_accessed_' +  timestr_filename + '.log'
		timestr_logon = time.strftime("%Y/%m/%d-%H:%M:%S-%p", time.localtime())

		with open(path, 'ab') as file:
			if 'logged_in' in session:
				c.execute("select * from login_user where username = (%s)", [session['username']])
				
				ip_addr = request.remote_addr
				ip_loc = get_ip_info(ip_addr)
				
				#get the auth_type of first record
				username_db = c.fetchone()[1] 
				
				#write logs according to the info_type
				if 'login' == info_type:
					data = timestr_logon + ' ' + username_db + ' ' + ip_addr + '-' + ip_loc + u' 登入'
				elif 'register' == info_type:
					data = timestr_logon + ' ' + username_db + ' ' + ip_addr + '-' + ip_loc + u' 注册并登入'
				elif 'logout' == info_type:
					data = timestr_logon + ' ' + username_db + ' ' + ip_addr + '-' + ip_loc + u' 退出'
				elif 'server' == info_type:
					data = timestr_logon + ' ' + username_db + ' ' + ip_addr + '-' + ip_loc + u' 访问了服务器岗文档'
				elif 'serverDenied' == info_type:
					data = timestr_logon + ' ' + username_db + ' ' + ip_addr + '-' + ip_loc + u' 尝试访问服务器岗文档库被系统拒绝'
				elif 'network' == info_type:
					data = timestr_logon + ' ' + username_db + ' ' + ip_addr + '-' + ip_loc + u' 访问了网络岗文档库'
				elif 'networkDenied' == info_type:
					data = timestr_logon + ' ' + username_db + ' ' + ip_addr + '-' + ip_loc + u' 尝试访问网络岗文档库被系统拒绝'
				elif 'inventory' == info_type:
					data = timestr_logon + ' ' + username_db + ' ' + ip_addr + '-' + ip_loc + u' 访问了资产岗文档库'
				elif 'inventoryDenied' == info_type:
					data = timestr_logon + ' ' + username_db + ' ' + ip_addr + '-' + ip_loc + u' 尝试访问资产岗文档库被系统拒绝'
					
				file.write(data + '\n') 

	except Exception as e:
		return str(e)
		


	
	
#only logged in user(s) can access the protected directory
# @app.route('/protected_dir/<path:filename>')
# @login_required
# def protected(filename):
	# try:
		# return send_from_directory(os.path.join(app.instance_path, ''), filename)
	# except Exception as e:
		# return redirect(url_for('homepage'))

		
	
@app.route("/")
def homepage():
	return  render_template("main.html", title=u'首页')
	
@app.route("/about-team/")
def about_team():
	return  render_template("about-team.html", title=u'团队介绍')
	


@app.route('/user-auth-edit/<username>/', methods = ['GET','POST'])
@login_required
def user_auth_edit(username):
	error = ''
	try:
		set_cn_encoding()
		username=username 
		c, conn = connection()
		if request.method == "POST":
			permit = (request.values.get("user_auth")).encode('utf-8')
		
			#Be carefule!! Must use [] to quote username , otherwise it will
			#prompt a warning like: "not all arguments converted during string formatting"
			c.execute("update login_user set auth_type='%s' where username='%s'" % (permit,username) )
			conn.commit()
			
			c.close()
			conn.close()
			gc.collect()
			flash(u'用户权限更新成功！')
			return  redirect(url_for('users_list'))
		else:
			c, conn = connection()
			c.execute("select * from login_user where username = (%s)", [username])
			auth_type_db = c.fetchone()[5] 
			
			#Get number of logs/login_user/docs and display them with "bootstrap badge"
			num_logs = (sysadm_badges_number())[0]
			num_users = (sysadm_badges_number())[1]
			num_docs = (sysadm_badges_number())[2]
			
			return render_template("user-auth-edit.html", title=u'修改权限', auth_type_db=auth_type_db,username=username,
			num_logs=num_logs, num_users=num_users, num_docs=num_docs, error=error)
	
	except Exception as e:
		return str(e)

		
@app.route('/user-delete/<username>/')
@app.route('/user-delete/')
@login_required
def user_delete(username):
	try:
		set_cn_encoding()
		username=username 
		c, conn = connection()

		#Be carefule!! Must use [] to quote username , otherwise it will
		#prompt a warning like: "not all arguments converted during string formatting"
		# c.execute("delete from login_user where username='%s'" % (username) )
		c.execute("delete from login_user where username= (%s)", [username] )
		conn.commit()
		
		c.close()
		conn.close()
		gc.collect()
		flash('用户删除成功!')
		return  redirect(url_for('users_list'))
	
	except Exception as e:
		return str(e)		

	
		
@app.route("/users-list/")
@login_required
def users_list():
	try:
		c, conn = connection()

		#get all users
		c.execute("select `username`, `auth_type`, `email`, `regdate`  from login_user")
		users_db = c.fetchall()
		
		#Get number of logs/users/docs and display them with "bootstrap badge"
		num_logs = (sysadm_badges_number())[0]
		num_users = (sysadm_badges_number())[1]
		num_docs = (sysadm_badges_number())[2]
			
		return render_template("users-list.html", title=u'用户列表', users_db=users_db, num_logs=num_logs, num_users=num_users, num_docs=num_docs)	
	except Exception as e:
		return str(e)


@app.route('/log-delete/<filename>/')
@app.route('/log-delete/')
@login_required
def log_delete(filename):
	try:
		set_cn_encoding()
		filename = filename 
		filename = LOGS_PATH + filename
		os.remove(filename)

		flash(u'日志删除成功!')
		return  redirect(url_for('logs_list'))
	
	except Exception as e:
		return str(e)		
	
	
@app.route("/logs-list/")
@login_required
def logs_list():

	#Get number of logs
	num_logs = (sysadm_badges_number())[0]

	list = []
	#取得logs目录下的所有文件（列表）
	files = os.listdir(LOGS_PATH)
	#列表按文件名排序
	files.sort(reverse = True)  
	for logfile in files:
		list.append(logfile)
	return  render_template("logs-list.html", title=u'日志列表', num_logs=num_logs, list=list)	
		
		
@app.route('/log-show/<filename>/')
@app.route("/log-show/") 
@login_required
def log_show(filename):
	try:
		set_cn_encoding()
		filename = filename 
		
		#Get number of logs
		num_logs = (sysadm_badges_number())[0]
		
		list = []
		#取得logs目录下的所有文件（列表）
		files = os.listdir(LOGS_PATH)
		#列表按文件名排序
		files.sort(reverse = True)  
		for logfile in files:
			list.append(logfile)
			
		fn = filename
		
		path = LOGS_PATH + fn
		with open(path, 'r') as file:
			event_lines = file.readlines()

		data = []
		num = len(event_lines)

		for x in range(num):
			data.append(event_lines[x].split(" "))
		
		return  render_template("log-show.html", title=u'查看日志', num=num, data=data, list=list, fn=fn,num_logs=num_logs)
		
	except Exception as e: 
		return str(e)
	
	
@app.route("/comments/")
def comments():
	try:
		error = ''

		return  render_template("comments.html", title=u'留言板', error = error)
	except Exception as e:
		return str(e)

	
@app.route("/privacy/")
def privacy():
	return  render_template("privacy.html", title=u'网站规定和隐私协议')
	
	
	
@app.route("/role-error/")
@login_required
def role_error_page():
	try:
		auth_type_db = ''
		c, conn = connection()
		#Be carefule!! Must use [] to quote session['username'] , otherwise it will
		#prompt a warning like: "not all arguments converted during string formatting"
		c.execute("select * from login_user where username = (%s)", [session['username']])
		#get the auth_type of first record
		auth_type_db = c.fetchone()[5] 

		
		return  render_template("role-error.html", title=u'权限错误', auth_type_db=auth_type_db)	
	except Exception as e:
		return str(e)


# For a given file, return whether it's an allowed type or not
def doc_allowed(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS		
	
		
@app.route('/doc-upload/', methods=['GET', 'POST'])
@login_required
def doc_upload():
	try:
		filename = ''
		if request.method == 'POST':
			file = request.files['file']
			doc_type = (request.values.get("doc_type")).encode('utf-8')
			to_folder = DOCS_PATH + doc_type + '/'
		
			if file and doc_allowed(file.filename):
				# filename = secure_filename(file.filename)   ###由于secure_filename不能识别中文名，暂停使用
				filename = (file.filename).encode('utf-8')
				file.save(os.path.join(to_folder, filename))

			#start to upload
			send_from_directory(to_folder,filename)	
			
			flash(u'文件上传成功！')
			#redirect to the page of the doc_type
			if 'server' == doc_type:
				return redirect(url_for('doc_server_dashboard'))
			elif 'network' == doc_type:
				return redirect(url_for('doc_network_dashboard'))
			else:
				return redirect(url_for('doc_inventory_dashboard'))

		#Get number of docs and display it with "bootstrap badge"
		num_server = (docs_badges_number())[0]
		num_network = (docs_badges_number())[1]
		num_inventory = (docs_badges_number())[2]		
				
		return  render_template("doc-upload.html", title=u'文档上传', num_server=num_server, num_network=num_network, num_inventory=num_inventory)	
		
	except Exception as e:
		# return str(e)
		flash(u'上传失败！ 请检查上传的文件是否符合要求，再重新尝试!')
		return redirect(url_for('doc_upload'))


@app.route('/doc-type-edit/<filename>/', methods = ['GET','POST'])
@login_required
def doc_type_edit(filename):
	error = ''
	try:
		set_cn_encoding()
		filename = filename.encode('utf-8')
		old_doc_type = ''
		
		if request.method == "POST":
			new_doc_type = (request.values.get("doc_type")).encode('utf-8')
			#find the path by the filename
			for root, dirs, files in os.walk(DOCS_PATH):
				for file in files:
					if file == filename:
						old_path_file = "%s/%s" % (root,file)
						old_doc_type = (os.path.split(root))[1]
						break   #if we found it, exit the loop
						
			new_path_file = DOCS_PATH + new_doc_type + '/' + filename
			if old_path_file == new_path_file:
				flash(u'文件已存在，操作无效!')
				return  redirect(url_for('docs_list'))
			else:
				#copy the old_path_file to new_path_file of new type
				shutil.copy(old_path_file, new_path_file) 
				#remove the old_path_file
				os.remove(old_path_file)
		
				flash(u'文档类型更新成功!')
				return  redirect(url_for('docs_list'))
		else:
			
			#find the old_doc_type
			for root, dirs, files in os.walk(DOCS_PATH):
				for file in files:
					if file == filename:
						old_doc_type = (os.path.split(root))[1]
						
			#Get number of logs/users/docs and display them with "bootstrap badge"
			num_logs = (sysadm_badges_number())[0]
			num_users = (sysadm_badges_number())[1]
			num_docs = (sysadm_badges_number())[2]
			return render_template("doc-type-edit.html", title=u'修改类型', filename=filename, old_doc_type=old_doc_type, 
			num_logs=num_logs, num_users=num_users, num_docs=num_docs,error=error)

	
	except Exception as e:
		return str(e)	


@app.route('/doc-name-edit/<filename>/', methods = ['GET','POST'])
@login_required
def doc_name_edit(filename):
	error = ''
	try:
		set_cn_encoding()
		filename = filename.encode('utf-8')
		doc_type = ''
		
		if request.method == "POST":
			new_filename = (request.values.get("doc_name")).encode('utf-8')
			#find the path by the filename
			for root, dirs, files in os.walk(DOCS_PATH):
				for file in files:
					if file == filename:
						doc_path_file = "%s/%s" % (root,file)
						doc_type = (os.path.split(root))[1]
						break   #if we found it, exit the loop
						
			old_path_file = DOCS_PATH + doc_type + '/' + filename
			new_path_file = DOCS_PATH + doc_type + '/' + new_filename + '.pdf'
			#rename the file
			os.rename(old_path_file, new_path_file)
		
			flash(u'文档重命名成功!')
			return  redirect(url_for('docs_list'))
		else:
						
			#Get number of logs/users/docs and display them with "bootstrap badge"
			num_logs = (sysadm_badges_number())[0]
			num_users = (sysadm_badges_number())[1]
			num_docs = (sysadm_badges_number())[2]
			return render_template("doc-name-edit.html", title=u'修改文件名', filename=filename,
			num_logs=num_logs, num_users=num_users, num_docs=num_docs,error=error)

	
	except Exception as e:
		return str(e)			
		
		
		
		
@app.route('/doc-delete/<filename>/')
@app.route('/doc-delete/')
@login_required
def doc_delete(filename):
	try:
		filename = filename.encode('utf-8')
		
		#find the path by the filename
		for root, dirs, files in os.walk(DOCS_PATH):
			for file in files:
				if file == filename:
					filename = "%s/%s" % (root,file)
					break   #if we found it, exit the loop
		#delete the file
		os.remove(filename)

		flash(u'文档删除成功!')
		return  redirect(url_for('docs_list'))
	
	except Exception as e:
		return str(e)	

	
@app.route("/docs-list/")
@login_required
def docs_list():
	try:
		set_cn_encoding()
		fnlist = []
		dirlist = []
		for root,dirs,files in os.walk(DOCS_PATH):
			for i in files:	
				fnlist.append(i)
				dirlist.append((os.path.split(root))[1])
				
		num_file = len(fnlist)
		
		#Get number of logs/users/docs and display them with "bootstrap badge"
		num_logs = (sysadm_badges_number())[0]
		num_users = (sysadm_badges_number())[1]
		num_docs = (sysadm_badges_number())[2]
			
		return render_template("docs-list.html", title=u'文档列表', num_file=num_file, fnlist=fnlist, dirlist=dirlist, 
		num_logs=num_logs, num_users=num_users, num_docs=num_docs)	
	except Exception as e:
		return str(e)

	
#Server docs viewing
@app.route("/doc-server-dashboard/")
@login_required
def doc_server_dashboard():	
	c, conn = connection()
	#Be carefule!! Must use [] to quote session['username'] , otherwise it will
	#prompt a warning like: "not all arguments converted during string formatting"
	c.execute("select * from login_user where username = (%s)", [session['username']])
	
	#get the auth_type of first record
	auth_type_db = c.fetchone()[5]
	
	#check auth_type of the logged in user, if not matches, redirect to role_error_page
	if 'ser' == auth_type_db or 'adm' == auth_type_db or 'superadm' == auth_type_db:
		set_cn_encoding()
		write_log_info('server')
		
		doclist = []
		for docfile in os.listdir(SERVER_DOCS_PATH):
			doclist.append(docfile)

		#Get number of docs of server
		num_server = (docs_badges_number())[0]	
			
		return  render_template("doc-server-dashboard.html", title=u'服务器岗文档库', num_server=num_server,doclist = doclist)
	else:
		write_log_info('serverDenied')
		return redirect(url_for('role_error_page'))	

# @app.route("/doc-server-show/quote(<filename>)/")		
@app.route("/doc-server-show/<filename>/")
@app.route("/doc-server-show/")
@login_required
def doc_server_show(filename):	
	set_cn_encoding()
	filename = filename.encode('utf-8')
	
	doclist = []
	for docfile in os.listdir(SERVER_DOCS_PATH):
		doclist.append(docfile)
	return  render_template("doc-server-show.html", title=u'服务器岗文档', filename=filename, doclist=doclist)		
		

@app.route("/doc-network-show/<filename>/")
@app.route("/doc-network-show/")
@login_required
def doc_network_show(filename):
	set_cn_encoding()
	filename = filename.encode('utf-8')

	doclist = []
	for docfile in os.listdir(NETWORK_DOCS_PATH):
		doclist.append(docfile)
	return  render_template("doc-network-show.html", title=u'网络岗文档', filename=filename, doclist=doclist)	
	

@app.route("/doc-inventory-show/<filename>/")
@app.route("/doc-inventory-show/")
@login_required
def doc_inventory_show(filename):
	set_cn_encoding()
	filename = filename.encode('utf-8')
	
	doclist = []
	for docfile in os.listdir(INVENTORY_DOCS_PATH):
		doclist.append(docfile)
	return  render_template("doc-inventory-show.html", title=u'资产岗文档', filename=filename, doclist=doclist)

	
#Network docs viewing	
@app.route("/doc-network-dashboard/")
@login_required
def doc_network_dashboard():	
	c, conn = connection()
	#Be carefule!! Must use [] to quote session['username'] , otherwise it will
	#prompt a warning like: "not all arguments converted during string formatting"
	c.execute("select * from login_user where username = (%s)", [session['username']])
	
	#get the auth_type of first record
	auth_type_db = c.fetchone()[5]
	
	#check if auth_type matches
	if 'net' == auth_type_db or 'adm' == auth_type_db or 'superadm' == auth_type_db:
		set_cn_encoding()
		write_log_info('network')
		
		doclist = []
		for docfile in os.listdir(NETWORK_DOCS_PATH):
			doclist.append(docfile)
		
		#Get number of docs of network
		num_network = (docs_badges_number())[1]	
		
		return  render_template("doc-network-dashboard.html", title=u'网络岗文档库', num_network=num_network,doclist = doclist)	
	else:
		write_log_info('networkDenied')
		return redirect(url_for('role_error_page'))	
	


#Inventory docs viewing	
@app.route("/doc-inventory-dashboard/")
@login_required
def doc_inventory_dashboard():	
	c, conn = connection()
	#Be carefule!! Must use [] to quote session['username'] , otherwise it will
	#prompt a warning like: "not all arguments converted during string formatting"
	c.execute("select * from login_user where username = (%s)", [session['username']])
	
	#get the auth_type of first record
	auth_type_db = c.fetchone()[5]
	
	#check if auth_type matches
	if 'inv' == auth_type_db or 'adm' == auth_type_db or 'superadm' == auth_type_db:
		set_cn_encoding()
		write_log_info('inventory')
		
		doclist = []
		for docfile in os.listdir(INVENTORY_DOCS_PATH):
			doclist.append(docfile)
		
		#Get number of docs of inventory
		num_inventory = (docs_badges_number())[2]	
		
		return  render_template("doc-inventory-dashboard.html", title=u'资产岗文档库', num_inventory=num_inventory,doclist = doclist)			
	else:
		write_log_info('inventoryDenied')
		return redirect(url_for('role_error_page'))	
		
	
@app.errorhandler(404)
def page_not_found(e):
	return  render_template("404.html")
	

	
@app.route("/logout/")
@login_required
def logout():
	write_log_info('logout') #do the logging
	
	session.clear()
	flash(u"您已退出系统！")
	gc.collect()
	return redirect(url_for('homepage'))

	
@app.route("/login/", methods = ['GET','POST'])
def login_page():
	error = ''
	try:
		set_cn_encoding()	
		
		c, conn = connection()
		if request.method == "POST":
			#Be carefule!! Must use [] to quote thwart(request.form['username']), otherwise it will
			#prompt a warning like: "not all arguments converted during string formatting"
			c.execute("select * from login_user where username = (%s)", [thwart(request.form['username'])])
			#get the password of first record
			pwd_in_db = c.fetchone()[2]
			
			#get the auth_type_db of logged in user
			c.execute("select * from login_user where username = (%s)", [thwart(request.form['username'])])
			auth_type_db = c.fetchone()[5]
			
			#check if password matches
			if sha256_crypt.verify(request.form['password'], pwd_in_db):
				session['logged_in'] = True
				session['username'] = request.form['username']
				session['auth_type_db'] = auth_type_db
				
				write_log_info('login')  #do the logging
				flash(u"您已成功登陆!")
				
				#redirect to the exact url I want to access
				# return redirect(session["want_url"])
				
				return redirect(url_for('homepage'))

				
			else:
				error = u'身份验证失败，请重试!'
		
		gc.collect()	
		
		return render_template("login.html", title=u'登陆', error=error)
		
	except Exception as e:
		error = error = u'身份验证失败，请重试!'
		return  render_template("login.html", title=u'登陆', error = error)


class RegistrationForm(Form):
	username = TextField(u'用户名', [validators.Length(min=2, max=20)])
	email = TextField(u'邮箱', [validators.Length(min=8, max=50)])
	password = PasswordField(u'密码', [validators.Required(),validators.Length(min=6, max=30),
				validators.EqualTo('confirm', message=u'密码不匹配')])	
	confirm = PasswordField(u'重输一遍密码')
	accept_tos = BooleanField(u'我接受<a href="/privacy/">网站规定和隐私协议</a> (最后更新：2016年7月)', [validators.Required()])
	
@app.route("/register/", methods = ['GET','POST'])
def register_page():
	try:
		set_cn_encoding()	
		
		form = RegistrationForm(request.form)
		if request.method == "POST" and form.validate():
			username = form.username.data
			password = sha256_crypt.encrypt((str(form.password.data))) 
			email = form.email.data
			c, conn = connection()

			x = c.execute("select * from login_user where username = (%s)", [thwart(username)])
			if int(x) > 0:
				flash(u'用户名已被使用，请尝试其他用户名!')
				return render_template('register.html', title=u'注册', form=form)
			else:
				#get the date of registeration, use China time
				datenow = datetime.datetime.utcnow()
				
				c.execute("insert into login_user (username, password, email, regdate) values (%s,%s,%s,%s)", (thwart(username), thwart(password), thwart(email), datenow))
				conn.commit()
				
				flash(u'感谢您的注册！您已登陆系统！')
				c.close()
				conn.close()
				gc.collect()
				
				session['logged_in'] = True
				session['username'] = username

				
				write_log_info('register') #do the logging
				
				return redirect(url_for('homepage'))
		
		return render_template("register.html", title=u'注册', form=form)
		
	except Exception as e:
		return(str(e))


		
	
if __name__ == "__main__":
	app.run()