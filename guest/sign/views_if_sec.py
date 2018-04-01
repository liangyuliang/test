from django.contrib import auth as django_auth
import hashlib
import base64
from django.http import JsonResponse
from models import Event
from models import Guest
from django.core.exceptions import ValidationError , ObjectDoesNotExist
from django.db.utils import IntegrityError
import time


def user_auth(request):
    get_http_auth = request.META.get('HTTP_AUTHORIZATION',b'')
    auth = str(get_http_auth).split()
    try:
        auth_parts = base64.b64decode(auth[1]).decode('iso-8859-1').partition(':')
    except IndexError:
        return "null"
    userid,password = auth_parts[0],auth_parts[2]
    user = django_auth.authenticate(username=userid,password=password)
    if user is not None and user.is_active:
        django_auth.login(request,user)
        return "success"
    else:
        return "fail"


def user_sign(request):

    client_time = request.POST.get('time','')
    client_sign = request.POST.get('sign','')

    if client_time == '' or client_sign == '':
        return "sign null"

    now_time = time.time()
    server_time = str(now_time).split("+")[0].split(".")[0]
    time_difference = int(server_time)-int(client_time)
    if time_difference >= 60:
        return "timeout"

    md = hashlib.md5()
    sign_str = client_time + "&Guest-Bugmaster"
    sign_bytes_utf8 = str(sign_str).encode(encoding="utf-8")
    md.update(sign_bytes_utf8)
    server_sign = md.hexdigest()

    if server_sign != client_sign:
        return "sign error"
    else:
        return "sign right"


def add_event(request):

    sign_result = user_sign(request)
    if sign_result == "sign null":
        return JsonResponse({'status':10011,'message':'user sign null'})
    if sign_result == "timeout":
        return JsonResponse({'status':10012, 'message':'user sign timeout'})
    if sign_result == "sign error":
        return JsonResponse({'status':10013,'message':'user sign error'})

    eid = request.POST.get('eid','')
    name = request.POST.get('name','')
    limit = request.POST.get('limit','')
    status = request.POST.get('status','')
    address = request.POST.get('address','')
    start_time = request.POST.get('start_time','')
    if eid == '' or name == '' or limit == '' or status == '' or address == '' or start_time == '':
        return JsonResponse({ 'status':10021,'message':'parameter error' })
    result = Event.objects.filter(id = eid)
    if result:
        return JsonResponse({ 'status':10022,'message':'event id already exists'})
    result = Event.objects.filter(name = name)
    if result:
        return JsonResponse({ 'status':10023,'message':'event name already exists'})
    if status == '':
        status = 1
    try:
        Event.objects.create(id=eid,name=name,limit=limit,address=address,status=int(status),start_time=start_time)
    except ValidationError as e:
        error = 'start_time format error . It must be in YYYY-MM-DD HH:MM:SS format'
        return JsonResponse({ 'status':10024,'message':error})
    return JsonResponse({'status':200,'message':'add event success'})


def get_event_list(request):

    auth_result = user_auth(request)
    if auth_result == "null":
        return JsonResponse({'status':10011,'message':'user auth null'})
    if auth_result == "fail":
        return JsonResponse({'status':10012,'message':'user auth fail'})

    eid = request.GET.get("eid","")
    name = request.GET.get("name","")
    if eid == '' and name == '':
        return JsonResponse({ 'status':10021,'message':'parameter error'})
    if eid != '':
        event = {}
        try:
            result = Event.objects.get(id=eid)
        except ObjectDoesNotExist:
            return JsonResponse({'status':10022,'message':'query result is empty'})
        event['name'] = result.name
        event['limit'] = result.limit
        event['status'] = result.status
        event['address'] = result.address
        event['start_time'] = result.start_time
        return JsonResponse({ 'status':200,'message':'success','data':event})
    if name != '':
        datas = []
        results = Event.objects.filter(name__contains=name)
        if results:
            for r in results:
                event = {}
                event['name'] = r.name
                event['limit'] = r.limit
                event['status'] = r.status
                event['address'] = r.address
                event['start_time'] = r.start_time
                datas.append(event)
            return JsonResponse({'status':200,'message':'success','data':datas})
        else:
            return JsonResponse({'status':10022,'message':'query result is empty'})

