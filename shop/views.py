import json
import requests
from math import ceil
from django.contrib import messages
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate, login, logout
from .PayTm import Checksum
from .models import Product, Contact, orders, orderUpdate
from django.views.decorators.common import no_append_slash

MERCHANT_KEY = 'T9dRDEmPnzoCfGWt'


# Function to show the items on the main page of the website
def index(request):

    # initialize an empty list of all prods
    allprods = []

    # fetching all types of categories with their id
    catprods = Product.objects.values('category', 'id')

    # extracting all categories with the help of set comprehension
    cats = {item['category'] for item in catprods}

    for cat in cats:
        prod = Product.objects.filter(category=cat)
        n = len(prod)
        number_of_slides = (n // 4) + ceil((n / 4) - (n // 4))
        allprods.append([prod, range(1, number_of_slides), number_of_slides])

    params = {
        'allprods': allprods
    }
    return render(request, "shop/index.html", params)


# Helper function to match the search query
def searchMatch(query, item):
    '''return true if query matches the item'''
    if query in item.desc.lower() or query in item.product_name.lower() or query in item.category.lower():
        return True
    else:
        return False


# Product searching function
def search(request):
    # when user presses on search then it is a get request, get the input of the search
    query = request.GET.get('search')
    query = query.lower()
    allprods = []
    catprods = Product.objects.values('category', 'id')
    cats = {item['category'] for item in catprods}

    for cat in cats:
        prodtemp = Product.objects.filter(category=cat)
        prod = [item for item in prodtemp if searchMatch(query, item)]
        n = len(prod)
        number_of_slides = (n // 4) + ceil((n / 4) - (n // 4))
        if n != 0:
            allprods.append([prod, range(1, number_of_slides), number_of_slides])

    params = {
        'allprods': allprods,
        'msg': ''
    }
    if len(allprods) == 0:
        params = {
            'msg': 'Please make sure to enter relevant search query'
        }
    return render(request, "shop/search.html", params)


# Renders the about page of the website
def about(request):
    return render(request, "shop/about.html")


# Renders the contact page of the website
def contact(request):
    if request.method == "POST":
        name = request.POST.get('name', 'xx')
        email = request.POST.get('email', 'xx')
        phone = request.POST.get('phone', 'xx')
        cust_query = request.POST.get('cust_query', 'xx')
        # saving an object of the contact model after the user enters the data in form

        if len(name) < 2 or len(email) < 3 or len(phone) < 10 or len(cust_query) < 4:
            messages.error(request, "Please fill the form correctly")
        else:
            contact = Contact(name=name, email=email, phone=phone, cust_query=cust_query)
            contact.save()
            messages.success(request, "Your message has been successfully sent")

        return render(request, "shop/contact.html")
    return render(request, "shop/contact.html")


# Tracker function, which helps the user to track their orders
def tracker(request):
    global response
    if request.method == 'POST':
        OrderId = request.POST.get('OrderId', 'default')
        email = request.POST.get('email', 'default')

        try:
            # retreive all objects from the orders database where the order_id=OrderId i.e the orderid entered
            # by the user

            order = orders.objects.filter(order_id=OrderId, email=email)

            if len(order) > 0:
                # if order present in the database, fetch the updates corresponding to that order
                update = orderUpdate.objects.filter(order_id=OrderId)
                updates = []

                for item in update:
                    updates.append({'text': item.update_desc, 'time': item.timestamp})

                    # converts py obj in json obj
                    # default=str so that date time can be json serializable, i.e so that it can be converted
                    # into a json object

                    response = json.dumps([updates, order[0].items_json], default=str)
                return HttpResponse(response)

            else:
                return HttpResponse('{}')

        except Exception as e:
            return HttpResponse(e)

    return render(request, "shop/tracker.html")


def products(request, myid):
    # fetch the product using the id
    # below is a list, so send the 0th item of the list in a dictionary as the third parameter
    product = Product.objects.filter(id=myid)
    return render(request, "shop/prodview.html", {'product': product[0]})


def checkout(request):
    global order, email
    if request.method == "POST":
        amount = request.POST.get('amount', '0')
        items_json = request.POST.get('itemsJson', 'null')
        name = request.POST.get('name', 'default')
        email = request.POST.get('email', 'default')
        address = request.POST.get('address', 'default')
        address2 = request.POST.get('address2', 'default')
        city = request.POST.get('city', 'default')
        state = request.POST.get('state', 'default')
        phone = request.POST.get('phone', 'default')
        zip_code = request.POST.get('zip_code', 'default')

        order = orders(name=name, email=email, address=address, address2=address2, city=city, state=state,
                       phone=phone, zip_code=zip_code, items_json=items_json, amount=amount)

        order.save()
        # when ordered item, create an object of the upateOrder class and inform the user
        # that order has been placed

        update = orderUpdate(order_id=order.order_id, update_desc="Your order has been placed")
        update.save()
        # REQUEST PAYTM TO GENERATE THE BILL AND MAKE THE USER PAY THE BILL AMOUNT AFTER THE FORM HAS BEEN SUBMITTED

        paytmParams = dict()

        paytmParams["body"] = {
            "requestType": "Payment",
            "mid": "gotSnQ74235192141604",
            "websiteName": "WEBSTAGING",
            "orderId": str(order.order_id),
            "callbackUrl": "http://127.0.0.1:8000/shop/handleRequest/",
            "txnAmount": {
                "value": str(order.amount).strip(),
                "currency": "INR",
            },

            "userInfo": {
                "custId": order.email,
            },
        }
        checksum = Checksum.generateSignature(json.dumps(paytmParams["body"]), "T9dRDEmPnzoCfGWt")

        paytmParams["head"] = {
            "signature": checksum
        }
        post_data = json.dumps(paytmParams)
        Paytm_id = 'gotSnQ74235192141604'
        ORDER_ID = order.order_id
        url = f"https://securegw-stage.paytm.in/theia/api/v1/initiateTransaction?mid={Paytm_id}&orderId={ORDER_ID}"

        response = requests.post(url, data=post_data, headers={"Content-type": "application/json"}).json()
        print(response)
        payment_page = {
            'mid': Paytm_id,
            'txnToken': response['body']['txnToken'],
            'orderId': paytmParams['body']['orderId'],
        }

        # show the user the paytm payment gateway html page
        return render(request, "shop/paytm.html", {'data': payment_page})

    return render(request, "shop/checkout.html")


@csrf_exempt
def handleRequest(request):
    # paytm will send u post request here
    # just put all post request details in a dictionary.
    # after this extract key CHECKSUMHASH and its value, check whether the CHECKSUM returned is true or not
    # from teh verify signature function in Checksum.py
    form = request.POST
    response_dict = {}

    for i in form.keys():
        response_dict[i] = form[i]
        if i == 'CHECKSUMHASH':
            checksum = form[i]

    verify = Checksum.verifySignature(response_dict, MERCHANT_KEY, checksum)
    if (verify):
        if (response_dict['RESPCODE'] == "01"):
            print("ORDER SUCCESSFUL")
        else:
            print("YOUR ORDER WAS NOT SUCCESSFUL BECAUSE:" + response_dict['RESPMSG'])
    return render(request, 'shop/paymentstatus.html', {'response': response_dict})

@no_append_slash
def signUp(request):
    print("you are trying to sign Up")
    if request.method == 'POST':
        print("POST RECEIVED")
        username = request.POST['username']
        email = request.POST['email']
        fname = request.POST['fname']
        lname = request.POST['lname']
        pass1 = request.POST['pass1']
        pass2 = request.POST['pass2']

        # applying checks
        if len(username) < 10:
            messages.error(request, " Your user name must be under 10 characters")
            return redirect('shop/')

        if not username.isalnum():
            messages.error(request, " User name should only contain letters and numbers")
            return redirect('shop/')
        if (pass1 != pass2):
            messages.error(request, " Passwords do not match")
            return redirect('shop/')

        myuser = User.objects.create_user(username, email, pass1)
        myuser.first_name = fname
        myuser.last_name = lname
        myuser.save()
        messages.success(request, "Your E-kart account has been created successfully ")
        return redirect('shop/')
    print("GET RECEIVED BYE")
    return render(request, 'shop/signUp.html')

@no_append_slash
def signIn(request):
    print("you are tring to sign in")
    if request.method == "POST":
        print("POST RECEIVED")
        # Get the post parameters
        loginusername = request.POST['loginusername']
        loginpassword = request.POST['loginpassword']
        user = authenticate(username=loginusername, password=loginpassword)
        if user is not None:
            print("valid user")
            login(request, user)
            messages.success(request, "Successfully Logged In")
            return redirect("shop/")
        else:
            print("no user")
            messages.error(request, "Invalid credentials! Please try again")
            return redirect("shop/")
    print("get received")
    return render(request, 'shop/signIn.html')


def logout_handler(request):
    logout(request)
    return redirect("/")
