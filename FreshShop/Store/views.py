import hashlib
from Store.models import *
from django.core.paginator import Paginator
from django.shortcuts import render,HttpResponseRedirect

from Store.models import *
from Buyer.models import *

def loginValid(fun):
    def inner(request,*args,**kwargs):
        c_user = request.COOKIES.get("username") #获取登录成功后的cookie和session
        s_user = request.session.get("username")
        if c_user and s_user and c_user == s_user: #如果cookie和session都存在并且值相同
            return fun(request,*args,**kwargs)
        else:
            return HttpResponseRedirect("/Store/login/") #否则重定向到登录页面
    return inner
#密码加密功能
def set_Password(password):
    md5 = hashlib.md5()
    md5.update(password.encode())
    return md5.hexdigest()
#注册功能
def register(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        if username and password:
            seller = Seller()
            seller.username = username
            seller.password = set_Password(password)
            seller.nickname = username
            seller.save()
            return HttpResponseRedirect("/Store/login/")
    return render(request,"store/register.html")

def login(request):
    """
    登录功能，如果登录成功，跳转到首页
    否则，跳转到登录页
    """
    # 进入登录页下发来源合法的cookie
    response = render(request,"store/login.html")
    response.set_cookie("login_from","login_page")
    #判断用户请求的方式
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        if username and password:   #  用户密码都存在
            #校验用户是否存在
            user = Seller.objects.filter(username = username).first() #数据库查询该用户
            if user:
                web_password = set_Password(password) #将前端获取到的密码加密，同数据库进行验证
                cookies = request.COOKIES.get("login_from") #校验请求是否来源于登录页面
                #校验密码是否正确
                if user.password == web_password and cookies == "login_page":
                    response = HttpResponseRedirect("/Store/index/") #登录成功，则跳转到首页并下发cookie和session
                    response.set_cookie("username",username)
                    response.set_cookie("user_id",user.id)  #cooike提供用户id方便其他功能查询 下发user_id的cookie
                    request.session["username"] = username
                    store = Store.objects.filter(user_id=user.id).first() # (接下来做的事)新增下发是否有店铺的cookie 先查询店铺是否存在
                    if store:
                        response.set_cookie("has_store",store.id) #再下发cookie
                    else:
                        response.set_cookie("has_store","")
                    return response
    return response



@loginValid
def index(request):
    # user_id = request.COOKIES.get("user_id")
    #     # if user_id:
    #     #     user_id = int(user_id)
    #     # else:
    #     #     user_id = 0
    #     # # 通过用户查询店铺是否存在（店铺和用户通过用户的id进行关联）
    #     # store = Store.objects.filter(user_id=user_id).first()
    #     # if store:
    #     #     is_store = store.id
    #     # else:
    #     #     is_store = ""
    return render(request,"store/index.html")

@loginValid
def register_store(request):
    type_list = StoreType.objects.all()
    if request.method == "POST":
        post_data = request.POST #接受post数据
        store_name = post_data.get("store_name")
        store_description = post_data.get("store_description")
        store_phone = post_data.get("store_phone")
        store_money = post_data.get("store_money")
        store_address = post_data.get("store_address")

        user_id = int(request.COOKIES.get("user_id")) #通过cookies来得到user_id
        type_lists = post_data.getlist("type") #通过request.post 得到类型，但是是一个列表

        store_logo = request.FILES.get("store_logo") #通过request.FILES得到
        #保存非多对多数据

        store = Store()
        store.store_name = store_name
        store.store_description = store_description
        store.store_phone = store_phone
        store.store_money = store_money
        store.store_address = store_address
        store.user_id = user_id
        store.store_logo = store_logo #django1.8之后图片可以直接保存
        store.save()   #保存，生成了数据库当中的一条数据
        #在生成的数据当中添加多对多字段。
        for i in type_lists:
            store_type = StoreType.objects.get(id = i)#查询类型数据
            store.type.add(store_type)#添加到类型字段，多对多的映射表
        store.save() #保存数据
        response = HttpResponseRedirect("/Store/index/")
        response.set_cookie("has_store",store.id)
        return response
    return render(request,"store/register_store.html",locals())

def base(request):
    return render(request,"store/base.html")

@loginValid
def add_goods(request):
    """
    负责添加商品
    """
    goods_typelist = GoodsType.objects.all()
    if request.method == "POST":
        #获取post请求
        goods_name = request.POST.get("goods_name") #通过前端name字段获取实际的值存储起来
        goods_price = request.POST.get("goods_price")
        goods_number = request.POST.get("goods_number")
        goods_description = request.POST.get("goods_description")
        goods_date = request.POST.get("goods_date")
        goods_safeDate = request.POST.get("goods_safeDate")
        goods_type = request.POST.get("goods_type")
        #使用cookie当中的店铺id
        goods_store = request.COOKIES.get("has_store")
        goods_image = request.FILES.get("goods_image") #图片是通过FILES方式获取
        #开始保存数据
        goods = Goods()
        goods.goods_name = goods_name
        goods.goods_price = goods_price
        goods.goods_number = goods_number
        goods.goods_description = goods_description
        goods.goods_date = goods_date
        goods.goods_safeDate = goods_safeDate
        goods.goods_image = goods_image
        goods.goods_type = GoodsType.objects.get(id = int(goods_type))
        goods.store_id = Store.objects.get(id = int(goods_store))
        goods.save()
        return HttpResponseRedirect("/Store/list_goods/up/")
    return render(request,"store/add_goods.html",locals())

@loginValid
def list_goods(request,state):
    """
    商品的列表页
    up 在售 down 下架
    """
    if state == "up":
        state_num = 1
    else:
        state_num = 0
    #获取两个关键字
    keywords = request.GET.get("keywords","")#查询关键词，用户前端搜索
    page_num = request.GET.get("page_num",1)#页码
    #查询店铺
    store_id = request.COOKIES.get("has_store")
    store = Store.objects.get(id=int(store_id))
    if keywords:#判断关键词是否存在
        goods_list = store.goods_set.filter(goods_name__contains=keywords,goods_under=state_num) #完成了模糊查询
    else: #如果关键字不存在，查询所有
        goods_list = store.goods_set.filter(goods_under=state_num)
    #分页 每页三条
    paginator = Paginator(goods_list,3)
    page = paginator.page(int(page_num))
    page_range = paginator.page_range
    #返回分页数据
    return render(request,"store/list_goods.html",{"page":page,"page_range":page_range,"keywords":keywords,"state":state,})

@loginValid
def goods(request,goods_id=1):
    goods_data = Goods.objects.filter(id = goods_id).first() #通过前端传递一个商品id来查询该商品信息
    return render(request,"store/goods.html",locals())

@loginValid
def update_goods(request,goods_id):
    goods_data = Goods.objects.filter(id=goods_id).first()
    if request.method == "POST":
        # 获取post请求
        goods_name = request.POST.get("goods_name")
        goods_price = request.POST.get("goods_price")
        goods_number = request.POST.get("goods_number")
        goods_description = request.POST.get("goods_description")
        goods_date = request.POST.get("goods_date")
        goods_safeDate = request.POST.get("goods_safeDate")
        # goods_store = request.POST.get("goods_store")
        goods_image = request.FILES.get("goods_image")
        # 开始修改商品信息
        goods = Goods.objects.get(id = int(goods_id)) #获取当前商品
        goods.goods_name = goods_name
        goods.goods_price = goods_price
        goods.goods_number = goods_number
        goods.goods_description = goods_description
        goods.goods_date = goods_date
        goods.goods_safeDate = goods_safeDate
        if goods_image:#如果有上传图片再发起修改
            goods.goods_image = goods_image
        goods.save()
        return HttpResponseRedirect("/Store/goods/%s/"%goods_id) #修改成功后重定向商品页面详情
    return render(request, "store/update_goods.html", locals())

def CooikeTest(request):
    #查询拥有的指定的商品的所有店铺
    goods = Goods.objects.get(id = 1)
    store_list = goods.store_id.all() #返回列表
    store_list = goods.store_id.filter() #返回列表
    store_list = goods.store_id.get() #返回的是具体的对象
    #查询指定店铺拥有的所有商品
    store = Store.objects.get(id = 11)
    #gooods第多对多表的名称的小写_set是固定写法
    store.goods_set.get()
    store.goods_set.filter()
    store.goods_set.all()

    response  = render(request,"store/Test.html",locals())
    response.set_cookie("valid","")
    return response
# Create your views here.

def set_goods(request,state):
    if state == "up":
        state_num = 1
    else:
        state_num = 0
    id = request.GET.get("id") #get获取id
    referer = request.META.get("HTTP_REFERER")
    if id:
        goods = Goods.objects.filter(id = id).first() #获取指定id的商品
        if state == "delete":
            goods.delete()
        else:
            goods.goods_under = state_num #修改状态
            goods.save() #保存
    return HttpResponseRedirect(referer) #跳转到请求来源页

def goods_typelist(request):
    # response = HttpResponseRedirect("/Store/goods_typelist")
    return render(request,"store/goods_typelist.html")

def order_list(request):
    store_id = request.COOKIES.get("has_store")
    order_list = OrderDetail.objects.filter(goods_store=store_id) #order_id_order_status=2,
    return render(request,"store/order_list.html",locals())

def logout(request):
    response = HttpResponseRedirect("/Store/login/")
    for key in request.COOKIES: #获取当前所有cookie
        response.delete_cookie(key)
    return response