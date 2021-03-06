#-*- coding: UTF-8 -*- 
'''
from django.shortcuts import render,render_to_response
from django.http import HttpResponse,HttpResponseRedirect
from django.contrib.auth import login as auth_login
from django.contrib.auth import logout as auth_logout
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from blog.models import Blog
from data.models import Data
from home.models import UserProfile
from django.http import Http404
from django.forms.formsets import formset_factory



from .forms import RegisterForm,LoginForm,CareerForm,PicForm
from django.contrib.auth.decorators import login_required,permission_required
from django.views.decorators.csrf import csrf_exempt

# Create your views here.

def index(request):
    return render(request,'home_index.html')
    
def register(request):
    
    if request.method=="POST":
        form=RegisterForm(request.POST)
        if form.is_valid():
            user=User.objects.create_user(
                username=form.cleaned_data['name'],
                password=form.cleaned_data['password1'],
                email=form.cleaned_data['email'],
                )
            user.save()
            user_profile=UserProfile.objects.create(user=user,has_profile='1')    
            return HttpResponseRedirect('/login')
    else:
        form=RegisterForm()
    
    return render(request,'home_register.html',{'form':form})
    
def login(request):
    errors=[]
    if request.method=="POST":
        form=LoginForm(request.POST)
        if form.is_valid():
            email=form.cleaned_data['email']
            try:
                username=User.objects.get(email=form.cleaned_data['email']).username
            except User.DoesNotExist:
                errors.append('这个邮箱没有用户')
            else:
                user=authenticate(username=username,password=form.cleaned_data['password'])
                if user is not None:
                    if user.is_active:
                        auth_login(request,user)
                        return HttpResponseRedirect('/')
                    else:
                        errors.append('你的用户没有激活')
                else:
                    errors.append('错误的用户名或密码')
            
                
    else:
        form=LoginForm()
    return render(request,'home_login.html',{'form':form,'errors':errors})
     
def person(request,id):
    try:
        the_user=User.objects.get(id=id)
    except User.DoesNotExist:
        raise Http404

       
    blogs=the_user.blog_set.all()[::-1]
    datas=the_user.data_set.all()[::-1]
    return render(request,"home_person.html",{"the_user":the_user,"datas":datas,"blogs":blogs})



                    
def logout(request):
    auth_logout(request)
    return HttpResponseRedirect('/')            
        

def my_404_view(request):
    return render(request,'my_404.html')

#@csrf_exempt
#@login_required(login_url='/login')
#def career(request):
#   if request.user.is_superuser:
#            return HttpResponseRedirect('/')
#    if request.user.userprofile.has_avatar:
#        avatar_existed=True
#    else:
#        avatar_existed=False
#    if request.method=="POST":
#        form=CareerForm(request.POST,request.FILES)
#        if form.is_valid():
#            if request.user.userprofile.has_profile:
#                user_profile=request.user.userprofile
#                user_profile.name=form.cleaned_data['name']
#                user_profile.sex=form.cleaned_data['sex']
#                user_profile.subject=form.cleaned_data['subject']
#                user_profile.classname=form.cleaned_data['classname']
#                user_profile.birthday=form.cleaned_data['birthday']
#                user_profile.race=form.cleaned_data['race']
#                user_profile.avatar=form.cleaned_data['avatar']
#                user_profile.has_avatar='1'
#                user_profile.introduction=form.cleaned_data['introduction']
#                user_profile.something=form.cleaned_data['something']
#                user_profile.make_sure_to_join=form.cleaned_data['make_sure_to_join']
#                user_profile.team=form.cleaned_data['team']
#                user_profile.save()
#            else:
#                user_profile=request.user.userprofile
#                user_profile.has_profile='1'
#                user_profile.name=form.cleaned_data['name']
#                user_profile.sex=form.cleaned_data['sex']
#                user_profile.subject=form.cleaned_data['subject']
#                user_profile.classname=form.cleaned_data['classname']
#                user_profile.birthday=form.cleaned_data['birthday']
#                user_profile.race=form.cleaned_data['race']
#                user_profile.avatar=form.cleaned_data['avatar']
#                user_profile.has_avatar='1'
#                user_profile.introduction=form.cleaned_data['introduction']
#                user_profile.something=form.cleaned_data['something']
#                user_profile.make_sure_to_join=form.cleaned_data['make_sure_to_join']
#                user_profile.team=form.cleaned_data['team']
#                user_profile.save()
#                
#            return HttpResponseRedirect('/')
#        else:
#        	if request.user.userprofile.avatar:
#                 avatar_existed=True
            
#            return render(request,"home_career.html",{"form":form,"avatar_existed":avatar_existed})
#    else:
        
        
#        if request.user.userprofile.has_avatar:
#            user_profile=request.user.userprofile
#            form_data={"name":user_profile.name,
#                                "sex":user_profile.sex,
#                                "subject":user_profile.subject,
#                                "classname":user_profile.classname,
#                                "birthday":user_profile.birthday,
#                                "race":user_profile.race,
#                                "contact":user_profile.contact,
#                                "introduction":user_profile.introduction,
#                                "something":user_profile.something,
#                                "make_sure_to_join":user_profile.make_sure_to_join,
#                                "team":user_profile.team}
#            form=CareerForm(form_data)
#            avatar_existed=True
#        else:
#            form=CareerForm()

#    return render(request,"home_career.html",{"form":form,"avatar_existed":avatar_existed})

@permission_required("can_check_the_table",login_url='/')
def join_show(request):
    try:
        user_profile=UserProfile.objects.filter(make_sure_to_join='1').filter(has_been_deal_with=False).order_by("team");
    except UserProfile.DoesNotExist:
        user_profile=[]
    return render(request,"home_join_show.html",{"user_profile":user_profile})



@csrf_exempt
@login_required(login_url='/login')
def career(request):
    if request.user.is_superuser:
            return HttpResponseRedirect('/')

    

   
    if request.method=='POST':
        careerform=CareerForm(request.POST,prefix='career')
        picform=PicForm(request.POST,request.FILES,prefix='pic')
        if careerform.is_valid():
              user_profile=request.user.userprofile
              user_profile.name=careerform.cleaned_data['name']
              user_profile.sex=careerform.cleaned_data['sex']
              user_profile.subject=careerform.cleaned_data['subject']
              user_profile.classname=careerform.cleaned_data['classname']
              user_profile.birthday=careerform.cleaned_data['birthday']
              user_profile.race=careerform.cleaned_data['race']
                
                
              user_profile.introduction=careerform.cleaned_data['introduction']
              user_profile.something=careerform.cleaned_data['something']
              user_profile.contact=careerform.cleaned_data['contact']
              user_profile.make_sure_to_join=careerform.cleaned_data['make_sure_to_join']
              user_profile.team=careerform.cleaned_data['team']
              user_profile.save()
        else:
             return render(request,'home_career.html',{'careerform':careerform,'picform':picform})
        if not request.user.userprofile.has_avatar:
              
              if picform.is_valid():
                    user_profile.avatar=picform.cleaned_data['avatar']
                    user_profile.has_avatar='1'
                    user_profile.save()

              else:
                 return render(request,'home_career.html',{'careerform':careerform,'picform':picform})
        return HttpResponseRedirect('/')

    else:
        user_profile=request.user.userprofile
        form_data={
                            "name":user_profile.name,
                            "sex":user_profile.sex,
                            "subject":user_profile.subject,
                            "classname":user_profile.classname,
                            "birthday":user_profile.birthday,
                            "race":user_profile.race,
                            "contact":user_profile.contact,
                            "introduction":user_profile.introduction,
                            "something":user_profile.something,
                            "make_sure_to_join":user_profile.make_sure_to_join,
                            "team":user_profile.team,
        }
        careerform=CareerForm(initial=form_data,prefix='career')
        picform=PicForm(prefix='pic')

        return render(request,'home_career.html',{'careerform':careerform,'picform':picform})


@permission_required("can_check_the_table",login_url='/')
def  NewManShow(request,id):
    try:
        user_profile=UserProfile.objects.get(id=id)
    except UserProfile.DoesNotExist:
        raise Http404
    return render(request,"home_personal_data.html",{"userprofile":user_profile})

def howtojoin(request):
    return render(request,"home_how_to_join.html")

    '''
    #-*- coding: UTF-8 -*- 

from django.shortcuts import render,render_to_response
from django.http import HttpResponse,HttpResponseRedirect
from django.contrib.auth import login as auth_login
from django.contrib.auth import logout as auth_logout
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from blog.models import Blog
from data.models import Data
from home.models import UserProfile,UserAvatar
from django.http import Http404
from django.forms.formsets import formset_factory



from .forms import RegisterForm,LoginForm,CareerForm,PicForm
from django.contrib.auth.decorators import login_required,permission_required
from django.views.decorators.csrf import csrf_exempt

# Create your views here.

def index(request):
    return render(request,'home_index.html')
    
def register(request):
    
    if request.method=="POST":
        form=RegisterForm(request.POST)
        if form.is_valid():
            user=User.objects.create_user(
                username=form.cleaned_data['name'],
                password=form.cleaned_data['password1'],
                email=form.cleaned_data['email'],
                )
            user.save()
            user_profile=UserProfile.objects.create(user=user,has_profile='1') 
            user_avatar=UserAvatar.objects.create(user=user)   
            return HttpResponseRedirect('/login')
    else:
        form=RegisterForm()
    
    return render(request,'home_register.html',{'form':form})
    
def login(request):
    errors=[]
    if request.method=="POST":
        form=LoginForm(request.POST)
        if form.is_valid():
            email=form.cleaned_data['email']
            try:
                username=User.objects.get(email=form.cleaned_data['email']).username
            except User.DoesNotExist:
                errors.append('这个邮箱没有用户')
            else:
                user=authenticate(username=username,password=form.cleaned_data['password'])
                if user is not None:
                    if user.is_active:
                        auth_login(request,user)
                        return HttpResponseRedirect('/')
                    else:
                        errors.append('你的用户没有激活')
                else:
                    errors.append('错误的用户名或密码')
            
                
    else:
        form=LoginForm()
    return render(request,'home_login.html',{'form':form,'errors':errors})
     
def person(request,id):
    try:
        the_user=User.objects.get(id=id)
    except User.DoesNotExist:
        raise Http404

       
    blogs=the_user.blog_set.all()[::-1]
    datas=the_user.data_set.all()[::-1]
    return render(request,"home_person.html",{"the_user":the_user,"datas":datas,"blogs":blogs})



                    
def logout(request):
    auth_logout(request)
    return HttpResponseRedirect('/')            
        

def my_404_view(request):
    return render(request,'my_404.html')

#@csrf_exempt
#@login_required(login_url='/login')
#def career(request):
#   if request.user.is_superuser:
#            return HttpResponseRedirect('/')
#    if request.user.userprofile.has_avatar:
#        avatar_existed=True
#    else:
#        avatar_existed=False
#    if request.method=="POST":
#        form=CareerForm(request.POST,request.FILES)
#        if form.is_valid():
#            if request.user.userprofile.has_profile:
#                user_profile=request.user.userprofile
#                user_profile.name=form.cleaned_data['name']
#                user_profile.sex=form.cleaned_data['sex']
#                user_profile.subject=form.cleaned_data['subject']
#                user_profile.classname=form.cleaned_data['classname']
#                user_profile.birthday=form.cleaned_data['birthday']
#                user_profile.race=form.cleaned_data['race']
#                user_profile.avatar=form.cleaned_data['avatar']
#                user_profile.has_avatar='1'
#                user_profile.introduction=form.cleaned_data['introduction']
#                user_profile.something=form.cleaned_data['something']
#                user_profile.make_sure_to_join=form.cleaned_data['make_sure_to_join']
#                user_profile.team=form.cleaned_data['team']
#                user_profile.save()
#            else:
#                user_profile=request.user.userprofile
#                user_profile.has_profile='1'
#                user_profile.name=form.cleaned_data['name']
#                user_profile.sex=form.cleaned_data['sex']
#                user_profile.subject=form.cleaned_data['subject']
#                user_profile.classname=form.cleaned_data['classname']
#                user_profile.birthday=form.cleaned_data['birthday']
#                user_profile.race=form.cleaned_data['race']
#                user_profile.avatar=form.cleaned_data['avatar']
#                user_profile.has_avatar='1'
#                user_profile.introduction=form.cleaned_data['introduction']
#                user_profile.something=form.cleaned_data['something']
#                user_profile.make_sure_to_join=form.cleaned_data['make_sure_to_join']
#                user_profile.team=form.cleaned_data['team']
#                user_profile.save()
#                
#            return HttpResponseRedirect('/')
#        else:
#           if request.user.userprofile.avatar:
#                 avatar_existed=True
            
#            return render(request,"home_career.html",{"form":form,"avatar_existed":avatar_existed})
#    else:
        
        
#        if request.user.userprofile.has_avatar:
#            user_profile=request.user.userprofile
#            form_data={"name":user_profile.name,
#                                "sex":user_profile.sex,
#                                "subject":user_profile.subject,
#                                "classname":user_profile.classname,
#                                "birthday":user_profile.birthday,
#                                "race":user_profile.race,
#                                "contact":user_profile.contact,
#                                "introduction":user_profile.introduction,
#                                "something":user_profile.something,
#                                "make_sure_to_join":user_profile.make_sure_to_join,
#                                "team":user_profile.team}
#            form=CareerForm(form_data)
#            avatar_existed=True
#        else:
#            form=CareerForm()

#    return render(request,"home_career.html",{"form":form,"avatar_existed":avatar_existed})

@permission_required("home.can_check_the_table",login_url='/')
def join_show(request):
    try:
        user_profile=UserProfile.objects.filter(make_sure_to_join='1').filter(has_been_deal_with=False).order_by("team");
    except UserProfile.DoesNotExist:
        user_profile=[]
    return render(request,"home_join_show.html",{"user_profile":user_profile})



@csrf_exempt
@login_required(login_url='/login')
def career(request):
    if request.user.is_superuser:
            return HttpResponseRedirect('/')
    if request.method=="GET":
        user_profile=request.user.userprofile
        form_data={
                            "name":user_profile.name,
                            "sex":user_profile.sex,
                            "subject":user_profile.subject,
                            "classname":user_profile.classname,
                            "birthday":user_profile.birthday,
                            "race":user_profile.race,
                            "contact":user_profile.contact,
                            "introduction":user_profile.introduction,
                            "something":user_profile.something,
                            "make_sure_to_join":user_profile.make_sure_to_join,
                            "team":user_profile.team,
        }
        careerform=CareerForm(initial=form_data)
        return render(request,'home_career.html',{'careerform':careerform})

   
    if request.method=='POST':
        careerform=CareerForm(request.POST)
#        picform=PicForm(request.POST,request.FILES,prefix='pic')
        if careerform.is_valid():
              user_profile=request.user.userprofile
              user_profile.name=careerform.cleaned_data['name']
              user_profile.sex=careerform.cleaned_data['sex']
              user_profile.subject=careerform.cleaned_data['subject']
              user_profile.classname=careerform.cleaned_data['classname']
              user_profile.birthday=careerform.cleaned_data['birthday']
              user_profile.race=careerform.cleaned_data['race']
                
                
              user_profile.introduction=careerform.cleaned_data['introduction']
              user_profile.something=careerform.cleaned_data['something']
              user_profile.contact=careerform.cleaned_data['contact']
              user_profile.make_sure_to_join=careerform.cleaned_data['make_sure_to_join']
              user_profile.team=careerform.cleaned_data['team']
              user_profile.save()
              return HttpResponseRedirect("/")
        else:
             return render(request,'home_career.html',{'careerform':careerform})
        return render(request,'home_career.html',{'careerform':careerform})
        '''
        if not request.user.userprofile.has_avatar:
              
              if picform.is_valid():
                    user_profile.avatar=picform.cleaned_data['avatar']
                    user_profile.has_avatar='1'
                    user_profile.save()

              else:
                 return render(request,'home_career.html',{'careerform':careerform,'picform':picform})
        return HttpResponseRedirect('/')

    else:
        user_profile=request.user.userprofile
        form_data={
                            "name":user_profile.name,
                            "sex":user_profile.sex,
                            "subject":user_profile.subject,
                            "classname":user_profile.classname,
                            "birthday":user_profile.birthday,
                            "race":user_profile.race,
                            "contact":user_profile.contact,
                            "introduction":user_profile.introduction,
                            "something":user_profile.something,
                            "make_sure_to_join":user_profile.make_sure_to_join,
                            "team":user_profile.team,
        }
        careerform=CareerForm(initial=form_data,prefix='career')
        picform=PicForm(prefix='pic')
        '''
        

@login_required(login_url='/login')
@permission_required("home.can_check_the_table",login_url='/')
def  NewManShow(request,id):
    try:
        user_profile=UserProfile.objects.get(id=id)
    except UserProfile.DoesNotExist:
        raise Http404
    return render(request,"home_personal_data.html",{"userprofile":user_profile})

def howtojoin(request):
    return render(request,"home_how_to_join.html")


@login_required(login_url='/login')
def PicChange(request):
    if request.method=="POST":
        picform=PicForm(request.POST)
        if picform.is_valid():
            request.user.useravatar=picform.cleaned_data['avatar']
            return HttpResponseRedirect("/")
        else:
            return render(request,"home_avatar_change.html",{'picform':picform})
    else:

        form_data={
          "avatar":request.user.useravatar.avatar
        }
        picform=PicForm(initial=form_data)
        return render(render,"home_avatar_change.html",{'picform':picform})