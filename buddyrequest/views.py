from django.shortcuts import render,redirect,get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from buddyrequest.models import BuddyRequest
import pandas
import csv
from .email import mail
from .matching_algorithm import get_matches
# Create your views here.

@login_required(login_url='/accounts/signup')
def database(request):
    buddyrequests=BuddyRequest.objects
    return render(request,'buddyrequest/database.html',{'buddyrequests':buddyrequests})
def remove(request):
    BuddyRequest.objects.get(user=request.user).delete()
    return redirect('home')
@login_required(login_url='/accounts/signup')
def profile(request,request_id):
    partner=BuddyRequest.objects.get(id=request_id)
    days=partner.days.strip('][\'')
    workout_type=partner.workout_type.strip('][\'')
    return render(request,'buddyrequest/profile.html',{'profile_details':partner,'days':days,'workout_type':workout_type})


def partner_match(request,partner_id):
    if request.method=="POST":
        #partner object for current user
        user_request=BuddyRequest.objects.get(user=request.user)
        matched_user=User.objects.get(pk=partner_id)
        partner_request=BuddyRequest.objects.get(user=matched_user)

        #match the two users in the database
        user_request.partner=matched_user
        partner_request.partner=request.user
        user_request.save()
        partner_request.save()

        #email both user and matched partner about the match
        mail(user_request.name,user_request.netID,partner_request.netID,user=True)
        mail(partner_request.name,partner_request.netID,user_request.netID,user=False)
        return redirect('partner')
@login_required(login_url='/accounts/signup')
def matches(request):
    if request.method=='POST':
        #if the user already has a request or partner in the database, go back to home page
        requestsList=list(BuddyRequest.objects.all().values())
        for entry in requestsList:
            print(request.user)
            if request.user.id==(entry['user_id']):
                return redirect('home')

        #get data about USER, if user isn't in studentdata.csv, send them back to home page
        try:
            userdatadf=pandas.read_csv('WorkoutBuddy\studentdata.csv',index_col=('netID'))
            netID=request.user.username
            userdata=userdatadf.loc[netID]
        except KeyError:
            return redirect('home')
        # preferences=request.POST['preferences']
        preferences=[0,1,2]
        print(preferences)
        name=userdata['name']
        major=userdata['major']
        year=userdata['year']
        rescollege=userdata['residentialcollege']
        days=request.POST.getlist('day')
        duration=request.POST['duration']
        workout_type=[]
        workout_type.append(request.POST['workout_type'])
        time_zone=request.POST['time_zone']
        profile_picture=request.POST['profile_picture']
        user=request.user

        #data used for match
        user_data_list=[preferences,days,duration,workout_type,time_zone]

        #if there is no profile picture, use the default one from the constructor
        if profile_picture=='':
            req_user=BuddyRequest(netID=netID,name=name,major=major,year=year,rescollege=rescollege,
            days=days,duration=duration,workout_type=workout_type,time_zone=time_zone,user=user)
        else:
            req_user=BuddyRequest(netID=netID,name=name,major=major,year=year,rescollege=rescollege,profile_picture=profile_picture,
            days=days,duration=duration,workout_type=workout_type,time_zone=time_zone,user=user)
        req_user.save()

        #if there are no active requests, don't run matching algorithm
        if len(requestsList) < 1:
            return render(request,'buddyrequest/matches.html')
        else:
            matched_people=get_matches(user_data_list, requestsList)
            if matched_people==[]:
                return render(request,'buddyrequest/matches.html')

        return render(request,'buddyrequest/matches.html',{'matched_people':matched_people})

@login_required(login_url='/accounts/signup')
def partner(request):
    #Get the current user's partner by finding the user who's partner is the current user
    partner=BuddyRequest.objects.get(partner=request.user)
    days=partner.days.strip('][\'')
    workout_type=partner.workout_type.strip('][\'')
    return render(request,'buddyrequest/profile.html',{'profile_details':partner,'days':days,'workout_type':workout_type})
