from django.shortcuts import get_object_or_404
from  rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib.auth.models import User
from rest_framework import status
from .models import File,encryption,shared_files
from .serializer import FileSerializer
from .serializer import FileSerializerNotData
from .serializer import UserSerializer
from .serializer import EncryptionSerializer
from .serializer import FileShareSerializer
from django.shortcuts import render
from .forms import UserForm
from django.http import HttpResponse
from django.contrib.auth import login, authenticate,logout
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render, redirect
#import MySQLdb, cPickle
def home(request):
    return render(request, 'home.html')


def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            login(request, user)
            return redirect('/spc')
    else:
        form = UserCreationForm()
    return render(request, 'signup.html', {'form': form})



#List all users, with their file paths and time-stamp
#user/filename
class FileList(APIView):

    def get(self, request):
        files = File.objects.all() #get all file objects
        serializer = FileSerializer(files, many=True)
        return Response(serializer.data)

    def post(self,request):
        j = request.data
        serializer = FileSerializer(data = j)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Create your views here.

class FileListNotData(APIView):

    def get(self, request):
        files = File.objects.all() #get all file objects
        serializer = FileSerializerNotData(files, many=True)
        return Response(serializer.data)

    def post(self):
        pass

class FileListNotDataUser(APIView):

    def get(self,request,user_id):
        user = User.objects.filter(username=user_id)
        files = File.objects.filter(user=user[0],safe='Y')
        serializer = FileSerializerNotData(files, many=True)
        return Response(serializer.data)

    def  post(self):
        pass

class FileListUserData(APIView):

    def get(self,request,user_id,path):
        new_path = "./"+path ## ASSUMPTION: ALL PATHS WILL BEGIN WITH "./"
        user = User.objects.filter(username=user_id)
        files = File.objects.filter(user=user[0], path=new_path)
        serializer = FileSerializer(files, many=True )
        return Response(serializer.data)

    def post(self,request,user_id,path):
        '''
            to resove conflicts and update file data
        '''
        new_path = "./"+path
        user = User.objects.filter(username=user_id)
        files = File.objects.filter(user=user[0], path=new_path).update(data=request.data["data"], timestamp=request.data["timestamp"],md5sum=request.data["md5sum"],safe=request.data["safe"])
        return Response(request.data, status=status.HTTP_201_CREATED)

class UserId(APIView):

    def get(self,request,user_id):
        user = User.objects.filter(username=user_id)
        # files = File.objects.filter(user=user[0])
        serializer = UserSerializer(user, many=True)
        return Response(serializer.data)

    def  post(self):
        pass

class getEnc(APIView):

    def get(self,request,user_id):
        user = User.objects.filter(username=user_id)
        # files = File.objects.filter(user=user[0])
        enc = encryption.objects.filter(user=user[0])
        serializer = EncryptionSerializer(enc, many=True)
        return Response(serializer.data)

    def  post(self,request,user_id):
        user = User.objects.filter(username=user_id)
        # files = File.objects.filter(user=user[0])
        data={"user":user[0].id,"encrypted":"T"}
        enc = EncryptionSerializer(data=data)
        if enc.is_valid():
            enc.save()
            return Response(request.data, status=status.HTTP_201_CREATED)
        return Response(enc.errors, status=status.HTTP_400_BAD_REQUEST)

class FileShareAPI(APIView):       
    def get(self,request,user_id,mode):
        files = shared_files.objects.filter(reciever=user_id)
        # files = File.objects.filter(user=user[0])
        # enc = encryption.objects.filter(user=user[0])
        serializer = FileShareSerializer(files, many=True)
        return Response(serializer.data)    #TODO deletion

    def  post(self,request,user_id,mode):
        '''
        Mode tells whether sending or recieving
        '''
        if(mode == "send"):
            j=request.data
            # files = File.objects.filter(user=user[0])
            # data={"user":user[0].id,"encrypted":"T"}
            enc = FileShareSerializer(data=j)
            if enc.is_valid():
                enc.save()
                return Response(request.data, status=status.HTTP_201_CREATED)
            return Response(enc.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            j = request.data
            file = shared_files.objects.filter(reciever=user_id,path=j["path"]).delete()
            return Response(request.data, status=status.HTTP_201_CREATED)
            # return Response(enc.errors, status=status.HTTP_400_BAD_REQUEST)
