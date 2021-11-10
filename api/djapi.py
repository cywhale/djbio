from django.shortcuts import render
from django.contrib.auth.models import User
from django.db.models import Q
from .models import apitest
from ninja import NinjaAPI
#from fastapi.responses import JSONResponse
import requests
import requests_cache

#from functools import reduce
#import operator

import logging
logger = logging.getLogger(__file__)

requests_cache.install_cache('api_cache', backend='sqlite', expire_after=604800)
djapi = NinjaAPI()

def op_or_query(qry):
#   reduce(operator.or_, **{*args})
    or_op = Q()
    for key, value in qry.items():
        or_op.add(Q(**{key: value}), Q.OR)

    return or_op

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
            if apis.exists():
                dt = getattr(apis[0], "gjson")
                url= getattr(apis[0], "url")
                if dt==None and url is not None:
                    try:
                        with requests_cache.enabled():
                            res = requests.get(url) #, headers={'Cache-Control': 'public, max-age=604800'})

                        logger.info(requests_cache.get_cache())
                        #logger.info('Cached URLS: %s', requests_cache.get_cache().urls)
                        return res.json() #JSONResponse(res.json(), 'application/json')

                    except requests.exceptions.HTTPError as err:
                        return {"Error": err}

                elif dt==None and url==None:
                    return {"Warning": "No data content..."}

                else:
                    return dt #{"Warning": "No data found..."} if not apis.exists() else getattr(apis[0], "gjson")

            else:
                return {"Warning": "No data found..."}

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

@djapi.get("/search/{layer}")
def search(request, layer: str):
    data = auth_getgjson(request, False,
        op_or_query({"name":layer , "uid":layer}),
        Q(owner__username=request.user.username)
    )
    return data


