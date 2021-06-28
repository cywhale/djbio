from django.shortcuts import render
from django.contrib.auth.models import User
from django.db.models import Q
from .models import apitest
from ninja import NinjaAPI

import logging
logger = logging.getLogger(__file__)


djapi = NinjaAPI()

def gjson_as_dict(qrylist):
    out = []
    for qry in qrylist:
        name = getattr(qry, "name")
        data = getattr(qry, "gjson")
        out.append({name: data})

    return out

def auth_getgjson(request, first=False, *args):
    data = {"Warning": "Not an authenticated user. Please login in."}
    if request.user.is_authenticated:
        apis=apitest.objects.filter(*args)
        if first:
            data = {"Warning": "No data found..."} if not apis.exists() else getattr(apis[0], "gjson")
        else:
            data = {"Warning": "No data found..."} if not apis.exists() else {"data": gjson_as_dict(apis)}

    return data

@djapi.get("/")
def dboard(request):
    records = apitest.objects.count()
    #username = request.GET.get("name") #or "guest" #request.GET["name"] #request.GET.getlist("name")
    #return HttpResponse("Hello, {}!".format(name)) #"{vname1} {vname2}".format(vname1=var1,vname2=var2)
    return render(request, "api/dboard.html", {"records": records})

@djapi.get("/list")
def list(request):
    data = auth_getgjson(request, False, Q(owner__username=request.user.username))
    return data


@djapi.get("/gjson/{uid}") #, response={ HTTPStatus.OK: List[definedSchema], }
def gjson(request, uid: str): #filters: apitest = Query(...) used in async def
    data = auth_getgjson(request, True, Q(owner__username=request.user.username), Q(uid=uid))
    return data

