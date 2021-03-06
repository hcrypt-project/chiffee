#!/usr/bin/env python
# encoding=utf8

from django.shortcuts import get_object_or_404, render
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.views import generic
from django.contrib.auth.models import User
from django.core.mail import EmailMessage
from django.contrib.auth import authenticate
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import Group

from pprint import pprint

from .models import Product, Buy, CATEGORIES, Employee, Deposit
import sys


fromaddr = "kaffeekasse@luis.uni-hannover.de"
subject  = "Kauf an der Kaffeekasse"

@login_required(login_url='chiffee:login')
def showhistory(request):
	context = {}
	context['users'] = User.objects.all()
	try:
		context['buys'] = Buy.objects.filter(buy_user=request.user)
	except Buy.DoesNotExist:
		pass
	try:
		u2 = request.user.employee
	except Employee.DoesNotExist:
		u2 = Employee(user=request.user)
		u2.save()
	context['balance'] = u2.balance
	return render(request, 'chiffee/history.html', context)

@login_required(login_url='chiffee:login')
def showoverview(request):
	context = {}
	context['users'] = User.objects.all()

	if "POST" == request.method and "neu1" in request._post.keys():
		user = authenticate(username=request.user.username, password=request._post["old"])
		if user is not None:
			# A backend authenticated the cred
			if request._post["neu1"] == request._post["neu2"]:
				user.set_password(request._post["neu1"])
				user.save()
				context["error"] = "Passwort geändert"
			else:
				context["error"] = "Die neuen Passwörter stimmen nicht überein!"
		else:
			# No backend authenticated the credentials
			context['error'] = "Passwort nicht korrekt!"

	if request.user.is_superuser and "POST" == request.method and "nutzer" in request._post.keys():
		try:
			profiteer = User.objects.get(username=request._post["nutzer"])
			money = float(request._post["value"])
			d = Deposit(deposit_user = profiteer, deposit_value = money)
			d.save()
			try:
				u2 = profiteer.employee
			except Employee.DoesNotExist:
				u2 = Employee(user=profiteer)
			u2.balance = u2.balance + money
			u2.save()
			context['payment'] = d
			msg = ("From: %s\r\nTo: %s\r\nSubject: %s\r\n\r\n" % (fromaddr,profiteer.email,"Gutschrift Kaffeekasse"))
			msg = ("Hallo %s %s.\n\r\n\r" % (profiteer.first_name, profiteer.last_name))
			msg = msg + ("Du hast soeben %0.2f Euro gut geschrieben bekommen.\n\r" % (money))
			msg = msg + ("Aktueller Kontostand: %7.2f Euro.\n\r\n\r" % (u2.balance))
			msg = msg + ("Es dankt,\n\rKarlo Kaffeekasse\n\r")
			email = EmailMessage("Gutschrift Kaffeekasse", msg, fromaddr, [profiteer.email])
			email.send()
		except:
			context['error'] = "Irgendwas lief schief beim einzahlen"
	try:
		u2 = request.user.employee
	except Employee.DoesNotExist:
		u2 = Employee(user=request.user)
		u2.save()
	context['balance'] = u2.balance
	return render(request, 'chiffee/overview.html', context)

@login_required(login_url='chiffee:login')
def showmoney(request):
	context = {}
	context['users'] = []
	if request.user.is_superuser:
		for u in User.objects.order_by('last_name', 'first_name'):
			try:
				u2 = {};
				u2['first_name'] = u.first_name
				u2['last_name'] = u.last_name
				u2['balance'] = u.employee.balance
				if u.employee.balance != 0:
					context['users'].append(u2)
			except:
				pass
	return render(request, 'chiffee/money.html', context)

@login_required(login_url='chiffee:login')
def balance(request):
#	print('balance()')
	sys.stdout.flush()

	context = {}
	context['users'] = []
	if request.user.is_superuser:
		for u in User.objects.order_by('last_name', 'first_name'):
#			print(' '+str(u.id)+' '+u.username+' '+u.first_name+' '+u.last_name)
			sys.stdout.flush()

			e = Employee.objects.get(user_id = u.id)

			buys = {}
			buys = Buy.objects.filter(buy_user = u.id)

			buys2 = {}

#			print ('type of buys is '+str(type(buys)))
#			print ('type of buys2 is '+str(type(buys2)))

			for b in buys:
#				print (b)
#				print ('type of b is '+str(type(b)))
				if b.buy_product.product_name not in buys2:
#					print('buy '+str(b.buy_product)+' ist neu:'+str(b.buy_count))
					buys2[b.buy_product.product_name]=Buy(buy_count=b.buy_count, 
														  buy_product=b.buy_product, 
														  buy_total=b.buy_total,
														  buy_user=b.buy_user)
				else:
#					print('buy '+str(b.buy_product)+' gibts schon: '+str(buys2[b.buy_product.product_name].buy_count)+'; '+str(b.buy_count)+' dazu')
					buys2[b.buy_product.product_name].buy_total+=b.buy_total
					buys2[b.buy_product.product_name].buy_count+=b.buy_count
			
#			print(buys2.keys())
#			print(buys2.values())
			
			
			u2 = {}
			u2['last_name'] = u.last_name
			u2['first_name'] = u.first_name
			u2['balance'] = e.balance
			u2['buys'] = buys2
			context['users'].append(u2)	

	return render(request, 'chiffee/balance.html', context)

@login_required(login_url='chiffee:login')
@user_passes_test(lambda u: u.is_superuser)
def showproducts(request):
	context = {}
	context['categories'] = CATEGORIES
	context['products'] = Product.objects.order_by('product_categorie')
	return render(request, 'chiffee/productoverview.html', context)

def products(request,userID):
	context = {}
	try:
		user = User.objects.get(username=userID)	
		context['user'] = userID
		context['categories'] = CATEGORIES
		context['products'] = Product.objects.order_by('product_categorie')
		return render(request, 'chiffee/products.html', context)
	except User.DoesNotExist:
		return render(request, 'chiffee/unknown.html', context)

def users(request):
	context = {}
	#context['product'] = productID
	#context['profs'] = Group.objects.get(name="prof").user_set.all().order_by('username')
	#context['wimi'] = Group.objects.get(name="wimi").user_set.all().order_by('username')
	#context['stud'] = Group.objects.get(name="stud").user_set.all().order_by('username')
	#context['users'] = Employee.objects.order_by('card_id')
	return render(request, 'chiffee/user.html', context)


def timeout(request):
	context = {}
	return render(request, 'chiffee/timeout.html',context)

def confirm(request, userID,productID):
	get_object_or_404(Product, id=productID)
	user = get_object_or_404(User, username=userID)
	context = {}
	context['product'] = Product.objects.get(id=productID).product_name
	#context['product_id'] = productID
	context['user'] = userID
	context['username'] = user.first_name + " " + user.last_name
	return render(request, 'chiffee/confirm.html', context)

def confirmed(request, userID,productID,count):
	product = get_object_or_404(Product, product_name=productID)
	user = get_object_or_404(User, username=userID)
	context = {}
	b = Buy(buy_count = count, buy_product = product, buy_user = user, buy_address=request.environ['REMOTE_ADDR'], buy_total=(product.product_price * int(count)))
	b.save()
	try:
		u2 = user.employee
	except Employee.DoesNotExist:
		u2 = Employee(user=user)
		u2.save()
	u2.balance = u2.balance - (product.product_price * int(count))
	u2.save()
	if u2.allMails:
		msg = ("From: %s\r\nTo: %s\r\nSubject: %s\r\n\r\n" % (fromaddr,user.email,subject))
		msg = ("Hallo %s %s.\n\r\n\r" % (user.first_name, user.last_name))
		msg = msg + ("Du hast soeben %d %s zu je %0.2f Euro gekauft.\n\r" % (int(count), product.product_name, product.product_price))
		msg = msg + ("Das macht insgesamt:  %7.2f Euro.\n\r" % (product.product_price * int(count)))
		msg = msg + ("Aktueller Kontostand: %7.2f Euro.\n\r\n\r" % (u2.balance))
		msg = msg + ("Es dankt,\n\rKarlo Kaffeekasse\n\r")
		email = EmailMessage(subject, msg, fromaddr, [user.email])
		email.send()
	return render(request, 'chiffee/confirmed.html', context)

