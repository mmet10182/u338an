import mimetypes

from django.template.backends import django
from django.utils.datastructures import MultiValueDictKeyError

from .services.settings import ROOT_CRT_PATH
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render
from .services import certificate
import os


def base(request):
    return render(request, 'base.html')


def download(request, file_name):
    pathcert = '{}{}'.format(ROOT_CRT_PATH, file_name)
    cert_content = open(pathcert, 'r')
    mime_type, _ = mimetypes.guess_type(pathcert)
    response = HttpResponse(cert_content, content_type=mime_type)
    response['Content-Disposition'] = 'attachment; filename={}'.format(file_name)
    return response


def content_dir(request):
    content_dir = certificate.get_content_dir()
    responce = {'content_dir': content_dir}
    return render(request, 'content_dir.html', responce)


def create_cert(request):
    pathcert = None
    if request.method == 'POST':
        try:
            cn = request.POST['cn']
            pathcert = certificate.create_cert(cn=cn)
            cert_content = open(pathcert['pathcert'], 'rb')
            mime_type, _ = mimetypes.guess_type(pathcert['pathcert'])
            response = HttpResponse(cert_content, content_type=mime_type)
            response['Content-Disposition'] = 'attachment; filename={}.cer'.format(cn)
            return response
        except KeyError:
            return render(request, 'messages.html', {'cert': pathcert})
    if request.method == 'GET':
        return render(request, 'create_cert.html')


def create_cert_p12(request):
    if request.method == 'GET':
        content_dir = certificate.get_content_dir()
        items = list()
        for v in content_dir.values():
            items.append(v['filename'])
        content_dir = set(items)
        responce = {'p12_file_name': content_dir}
        return render(request, "create_p12.html", responce)

    if request.method == 'POST':
        password = request.POST['password']
        certname = None
        try:
            certname = request.POST['cert']
        except KeyError:
            return render(request, "messages.html", {'cert_name_p12': certname})
        pathcert = certificate.create_pkcs12(certname, password)
        cert_content = open(pathcert['pathcert'], 'rb')
        mime_type, _ = mimetypes.guess_type(pathcert['pathcert'])
        response = HttpResponse(cert_content, content_type=mime_type)
        response['Content-Disposition'] = 'attachment; filename={}.p12'.format(certname)
        return response