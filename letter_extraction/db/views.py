import datetime
from django.template import loader
from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import authenticate, login
from .forms import *
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render, redirect, render_to_response
from django.contrib.auth.decorators import login_required, permission_required
from django.db.models import Q
from db.services import query_service, account_service, upload_service, store_service,  results_service
from .models import *

#Testing import python function

# Create your views here.

from django.template import RequestContext

result = {}
indicator = 0
archive_number_list = []

@login_required
def index(request):
    if request.method == "POST":
        global result
        global indicator
        global archive_number_list
        store_service.deleteReplicates(archive_number_list)
        if indicator == 0:
            store_service.addToModel(result, request.user)
        elif indicator == 1:
            store_service.addToModel_xlsx(result, request.user)
            indicator = 0
    result = {}
    context = {}
    archive_number_list = []
    return render(request, 'db/index.html', context)


@login_required
def search(request):
    if not request.user.has_perm('db.can_search'):
        return render(request, 'db/index.html', {"message":"You do not have the permissions to perform this task!"})
    template = loader.get_template('db/search.html')
    context = {
    }
    return HttpResponse(template.render(context, request))


@login_required
def search_result(request):
    primary_keys = []
    if not request.user.has_perm('db.can_search'):
        return render(request, 'db/index.html', {"message":"You do not have the permissions to perform this task!"})
    search_type = str(request.GET['searchtype'])
    query_value = str(request.GET['query'])
    document_list = query_service.analyze_query_request(search_type, query_value, primary_keys)
    #categories = {}
    #metadata = {}
    #store_service.string_split(document_list, categories, metadata)
    header = ['archive_number', 'date_written', 'document_type', 'language', 'pk']
    values = query_service.get_values(document_list, header)
    #body = document_list
    context = {'header': header, 'values': values, 'archive' : primary_keys}
    return render(request, 'db/result.html', context)


@login_required
def upload(request):
    if not request.user.has_perm('db.can_upload'):
        return render(request, 'db/index.html', {"message":"You do not have the permissions to perform this task!"})
    if request.method == "POST" and  request.FILES.get('myfile',False):
        global indicator
        global result
        global archive_number_list
        result = upload_service.main(request.FILES['myfile'])
        results_service.archive_number_finder(result, archive_number_list) #checking for duplicates, duplicate archive numbers will be stored in archive_number_list
        indicator = 0 #docx files
        if (request.FILES['myfile'].name.endswith('.xlsx') or request.FILES['myfile'].name.endswith('.xls')):
            indicator = 1 #xlsx and xls files
        #storing(result)
        return render(request,'db/upload.html',{"list":result, "indic": indicator, "fname": request.FILES['myfile'].name})
    else:
        template = loader.get_template('db/upload.html')
        context = {}
    return render(request,'db/upload.html',context)

@login_required
def test(request, items):
    template = loader.get_template('db/test.html')
    document_object = Document.objects.filter(pk = items).first()
    if request.method == "POST":
        document_test_form = documentForm(request.POST, instance=document_object)
        if document_test_form.is_valid():
            instance = document_test_form.save(commit=False)
            instance.save()
            return redirect("db:index")
        else:
            document_test_form.errors()
            return HttpResponse("<p>Your Modification is invalid </p")
    document_test_form = documentForm(instance = document_object)
    return render(request, 'db/test.html', {'document_test_form' : document_test_form})


def login_user(request):
    message = None
    if request.method=="POST":
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            if account_service.login_user(request):
                return redirect('db:index')
        else:
            context = {'form':AuthenticationForm(), 'message':'Username or password incorrect!'}
    else:
        context =  {'form':AuthenticationForm(), 'message':message}
    return render(request, 'db/login.html', context)


def logout(request):
    account_service.logout_user(request)
    return redirect('db:login')

def drag_n_drop_test(request):
    context = {}
    return render(request, 'db/drag_n_drop_test.html', context)
