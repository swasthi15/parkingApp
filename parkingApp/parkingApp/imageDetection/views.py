import warnings
warnings.simplefilter(action="ignore", category=FutureWarning)
from django.shortcuts import render
from django.core.files.storage import FileSystemStorage
from django.http import HttpResponse
from django.conf import settings

# keras imports
from keras.applications.resnet50 import ResNet50, preprocess_input
from keras.preprocessing import image
from keras.models import Model
from keras.models import model_from_json
# from keras.models import model_from_json
from keras.layers import Input

# other imports
from sklearn.preprocessing import LabelEncoder
import numpy as np
import glob
# import cv2
import h5py
import os
import json
import datetime
import time
import pickle
import requests
from random import randint


from django.http import HttpResponse
from django.shortcuts import render, redirect
#from . import templates
from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.contrib import auth
from imageDetection.models import MapLocation, Images
import time
from background_task import background

@background(schedule=240)
def job():
	image_size = (224, 224)
	imageObj = Images.objects.order_by('?').first()
	print("Fetched",imageObj.image_name)
	is_free = imageObj.is_free

	image_name = imageObj.image_name
	locationObj = imageObj.location
	#print(locationObj.location_name)
	

	if is_free:
		locationObj.total_free = locationObj.total_free - 1
		locationObj.save()
		print("location obj reduced", locationObj.total_free)

	print("Deleting image ",image_name)
	imageObj.delete()
	randomInt = randint(0, 9)
	
	already_exists = 1
	print("Current image",image_name)
	while already_exists:
		randomInt = randint(0, 9)
		image_path = locationObj.location_name + str(randomInt) + '.jpg'
		print("Checking ",image_path)
		if image_path == image_name:
			already_exists = 1
			continue
		already_exists = Images.objects.filter(image_name=image_path).count()
		print(image_path)
		#print(already_exists)
	
	# if is_free:
	# 	locationObj.total_free = locationObj.total_free - 1

	img = image.load_img(os.path.join(settings.BASE_DIR, 'media/'+image_path), target_size=image_size)
	print(img)
	
	json_file = open(os.path.join(settings.BASE_DIR, 'ResnetModel.json'),'r')
	loaded_model_json = json_file.read()
	json_file.close()
	Resnetmodel = model_from_json(loaded_model_json)
	# load weights into new model
	Resnetmodel.load_weights(os.path.join(settings.BASE_DIR, 'ResnetModel.h5'))
	filename = os.path.join(settings.BASE_DIR, 'finalized_model.sav')
	loaded_model = pickle.load(open(filename, 'rb'))
	x = image.img_to_array(img)
	x = np.expand_dims(x, axis=0)
	x = preprocess_input(x)
	feature = Resnetmodel.predict(x)
	ans = loaded_model.predict(feature)
	result = ans[0].item()

	
	Images.objects.create(location=locationObj, image_name=image_path, is_free=result)
	print("Added image ",image_path, result)
	if result:
		locationObj.total_free = locationObj.total_free + 1
		print("location obj increased,", locationObj.total_free)
	print("*"*70)

	locationObj.save()
	time.sleep(60)
	# print(imageObj.location.location_name)



# def about(request):
#     return render(request,'about.html')

def signup(request):
	print("signup")
	return render(request,'signup1.html')

def signup_submit(request):
    username = request.POST.get('username')
    password = request.POST.get('password')
    email = request.POST.get('email')
    print(username)
    print(password,email)
    user = User.objects.create_user(username, email,password)
    user.save()

    return redirect('/login')

	
def login(request):
	print(request.user)

	#return HttpResponse("Done and dusted")
	return render(request,'login.html')

def logging_in(request):
    username = request.POST['username']
    password = request.POST['password']
    user = authenticate(request, username=username, password=password)
    print(user)
    print("login")
    if user is not None:
        auth.login(request,user)
        print("Successfull")

        print(username)
        return redirect('/')
        # Redirect to a success page.
        ...
    else:
        return redirect('/')

def logout(request):
    auth.logout(request)
    return redirect('/')

# Create your views here.
def index(request):
	print(type(request.user))

	print("Hitting Home Page Successfull")
	job(repeat=240)
	if(request.user.is_authenticated)	:
		print(request.user)	
		return redirect('/location/')
	else:
		return redirect('/login/')



def access_location(request):

	return render(request,'location.html')

def fetchLocation():
	mapObj = MapLocation.objects.all().filter(total_free__gte = 0)
	mapList = []
	destination = ""
	for i in mapObj:

		di = {}
		di['latitude'] = float(i.latitude)
		di['longitude'] =float(i.longitude)
		di['location_name'] = (i.location_name)
		destination = destination+i.latitude+','+i.longitude+'|'
		mapList.append(di)
	return (mapList,destination)


def user_location(request):
	latitude=request.POST.get('latitude')
	longitude=request.POST.get('longitude')
	print(latitude,longitude)

	(mapList, destination) = fetchLocation()
	print(mapList,destination)
	payload = {'origins': latitude+','+longitude,
			'destinations':destination[:-1],
			'key': 'AIzaSyD0C7fhZWNux7H5rPqyeLkZnePnMFYDfVY',
			'units':'metric'}

	r = requests.get('https://maps.googleapis.com/maps/api/distancematrix/json', params=payload)
	print(r.json())
	distance_list=[]
	response_obj = r.json()
	for obj in response_obj['rows'][0]['elements']:
		distance_list.append(obj['distance']['value'])
	#return values.index(min(values))
	
	min_index = (distance_list.index(min(distance_list)))
	print(response_obj['destination_addresses'][min_index])

	tempList = [ mapList[min_index] ]
	return render(request,'location.html',{'mapList' : tempList })

def fetch_all_locations(request):
	(mapList, destination) = fetchLocation()
	print(mapList,destination)
	return render(request,'location.html',{'mapList' : mapList })


	# def uploadImage(request):
	# json_file = open(os.path.join(settings.BASE_DIR, 'ResnetModel.json'),'r')
	# loaded_model_json = json_file.read()
	# json_file.close()
	# Resnetmodel = model_from_json(loaded_model_json)
	# # load weights into new model
	# Resnetmodel.load_weights(os.path.join(settings.BASE_DIR, 'ResnetModel.h5'))
	# filename = os.path.join(settings.BASE_DIR, 'finalized_model.sav')
	# loaded_model = pickle.load(open(filename, 'rb'))
	# image_size = (224, 224)
	# if request.method == 'POST' and request.FILES['myfile1']:
		
	# 	myfile = request.FILES['myfile1']
	# 	img = image.load_img(myfile, target_size=image_size)
	# 	x = image.img_to_array(img)
	# 	x = np.expand_dims(x, axis=0)
	# 	x = preprocess_input(x)
	# 	feature = Resnetmodel.predict(x)
	# 	flat = feature.flatten()
	# 	ans = loaded_model.predict(feature)
	# 	print(ans)
	# 	result = ans[0].item()
	# if(result==0):
	# 	finalResponse = "<h1>Parking spot not available</h1>"
	# else:
	# 	finalResponse = "<h1>Parking spot available</h1>"

	# return HttpResponse(finalResponse)

# def viewMap(request):
# 	print(request.user)
# 	print("Hitting Home Page Successfull")

# 	#return HttpResponse("Done and dusted")
# 	return render(request,'map.html',{'user':request.user})
