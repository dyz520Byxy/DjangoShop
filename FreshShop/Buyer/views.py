import time

from django.shortcuts import render
from django.http import HttpResponse
from django.http import JsonResponse
from django.db.models import Sum
from django.shortcuts import HttpResponseRedirect


from Buyer.models import *
from Store.views import *
from Store.views import set_Password

from alipay import AliPay


def loginValid(fun):
    def inner(request,*args,**kwargs):
        c_user = request.COOKIES.get("username")
        s_user = request.session.get("username")
        if c_user and s_user and c_user == s_user:
            return fun(request,*args,**kwargs)
        else:
            return HttpResponseRedirect("Buyer/login")
    return inner

def register(request):
    if request.method == "POST":
        #获取前端post请求的数据
        username = request.POST.get("user_name")
        password = request.POST.get("pwd")
        email = request.POST.get("email")
        #将数据存入数据库
        buyer = Buyer()
        buyer.username = username
        buyer.password = set_Password(password)
        buyer.email = email
        buyer.save()
        #跳转到login页面
        return HttpResponseRedirect("/Buyer/login/")
    return render(request,"buyer/register.html")

def login(request):
    if request.method == "POST":
        #获取数据
        username = request.POST.get("username")
        password = request.POST.get("pwd")
        if username and password:
            user = Buyer.objects.filter(username=username).first()
            if user:
                #密码加密比对
                web_password = set_Password(password)
                if user.password == web_password:
                    response = HttpResponseRedirect("/Buyer/index")
                    #校验的登录
                    response.set_cookie("username",user.username)
                    request.session["username"] = user.username
                    #方便其他查询
                    response.set_cookie("user_id",user.id)
                    return response
    return render(request,"buyer/login.html")

@loginValid
def index(request):
    result_list = []
    goods_typelist = GoodsType.objects.all()
    for goods_type in goods_typelist:
        goods_list = goods_type.goods_set.values()[:4]
        if goods_list:
            goodsType = {
                "id":goods_type.id,
                "name":goods_type.name,
                "description":goods_type.description,
                "picture":goods_type.picture,
                "goods_list":goods_list,
            }
            result_list.append(goodsType)
    return render(request,"buyer/index.html",locals())

def logout(request):
    response = HttpResponseRedirect("/Buyer/login/")
    #删除所有的请求携带的cookie
    for key in request.COOKIES:
        response.delete_cookie(key)
    #删除session
    del request.session["username"]
    return response

def base(request):
    return render(request,"buyer/base.html")

@loginValid
def goods_list(request):
    goodsList = []
    type_id = request.GET.get("type_id")
    goods_type = GoodsType.objects.filter(id = type_id).first()
    if goods_type:
        goodsList = goods_type.goods_set.filter(goods_under = 1)
    return render(request,"buyer/goods_list.html",locals())

def pay_order(request):
    money = request.GET.get("money")#获取订单金额
    order_id = request.GET.get("order_id")#获取订单id
    alipay_public_key_string = """-----BEGIN PUBLIC KEY-----
    MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA6QQ6d2vJH2pVdpVbLd9phZfe9KFUptS0+zw+9Ir4IVElBtXGy9ykLFVplvlHfub+4+x1ZUY4Km5u9pTLn3BD1LnYs5/SkhBX35xK9sJGnNRke+xRj9NX5KYpgESFFx8qNuQAeaD9gnMcygTVvre7+hprAzt3FDpqlYgynjzmIRMHQbdZdCMJaZU12XDoz9FK5XWVxMeWSiMYbe5PON6L9tutW2E8CVb9VhFMNINUa4oybbm+pVwo99tBp7AnKZvzjhT9KOP+pdNyibUSiSHXAx7g+RMgT3gJv15QyWe9IDtejUQpDnsf77HbHtd/P8OC/IcJR88g2o6QX4gP+kBRJwIDAQAB
    -----END PUBLIC KEY-----"""

    app_private_key_string = """-----BEGIN RSA PRIVATE KEY-----
    MIIEowIBAAKCAQEA6QQ6d2vJH2pVdpVbLd9phZfe9KFUptS0+zw+9Ir4IVElBtXGy9ykLFVplvlHfub+4+x1ZUY4Km5u9pTLn3BD1LnYs5/SkhBX35xK9sJGnNRke+xRj9NX5KYpgESFFx8qNuQAeaD9gnMcygTVvre7+hprAzt3FDpqlYgynjzmIRMHQbdZdCMJaZU12XDoz9FK5XWVxMeWSiMYbe5PON6L9tutW2E8CVb9VhFMNINUa4oybbm+pVwo99tBp7AnKZvzjhT9KOP+pdNyibUSiSHXAx7g+RMgT3gJv15QyWe9IDtejUQpDnsf77HbHtd/P8OC/IcJR88g2o6QX4gP+kBRJwIDAQABAoIBAGYmPmM/0yl8ef7ENvaDLEUucMUZPHzuXnCM1qRpj6E7a1n1uXKBRU9SGjnfCeKt7SuJ62T8RX8EboyWajV5B6Nn3YHRHIR/uaYDZDGMtVvnGC3jSVYdtjg8R5E9eILMXLs3dKXdV4UqZYKCYBl9fmCD2EnQdcFeYn8u99G6rL/uO2h5RexQTsidZqCUnNd21fYqQd9YS7+CjD3kxd1ryml4J0pA01OqLJwia/HvdGS8INf0Z/9Tk640sJPspky7W230wv94N1qbxc/mk6QGaR5bRDg3GnEhRXiqHS/F2XanGjk4YCMQLWO/TZxUXer7WUPMboBpQQ7xXvCE+q4cebECgYEA9ipsdBB85wh450DkmEAIfO5CyD9xtXf984j34tuYplmaCJucLJha3LWWAtH68auEvZ9etOE1kBMXiba3RK4y7DvOSYlmPVoLZ41nJrURab838/apK/WIzZaBeU/3+z2UvVBzJXrd1GbAYzDu5w8B0bxPjhNrkEJcewY24OrJRLMCgYEA8lNTZKdCl/2GUEn/3y7k3C2NA0pmTK0FaC7SbUWAtUEiV8tDamVVlj5LxmD81/m9OywDG/tUI5RMirlFNd9aoLIiVo8oAqycd3KY6px2PxDuJ/LKcyoEIj+SB7MB3IqOYqWigbOVKiONiJPXSbrgaeutGQnetprrHvAH5I77g70CgYBAGx4xP5X3aIpr1sdxKsPLHRVBJtyK4Ju+zz2W0482SwFFGpkaN/b5oURWqa5LP1qLMzSrsDaNtZscnvutJBxYzt5S4jhA4/EyX22sc9z8B/MfUm4N55xfxcEkAYJX6FqSzp+d9BhO1w9lBXpBq/PSVdL18fLCF7YTx7OE8T/G5wKBgB+y8LzA+IAjZPeJxpPucXev6btddyZel896GIK8zcpoG9L6PvZjDSAbRBROSaUDAVMFPd7iMK56zsxy0e/rKNLOmplSHrzC0bD6Z7CBCSLU1yKYqw0HmQTV5gdlzj+ITHnxCuIGmOOrRO9xz37QmFyivMECvoSKnWktowqt/Y7NAoGBAKt/BLfyp2DuL6XmsJ8JqDyTt9wR5MYOFq13VFWxk4aWLqMrc2LtMqX7yObfky7a9cZ4Tn+Qvq6881qqc60kcI7rCIy+o4dc7KNVX0ufUBPosu4hPzF9yJErwbAHCQ/fnk6/fSTQYkZVLQC9v7OrLbbDPdEhUukNF3Hk/sGtzCOg
    -----END RSA PRIVATE KEY-----"""

#实例化支付应用
    alipay = AliPay(
        appid = "2016101000652502",
        app_notify_url = None,
        app_private_key_string = app_private_key_string,
        alipay_public_key_string = alipay_public_key_string,
        sign_type="RSA2"
    )

    #发起支付请求
    order_string = alipay.api_alipay_trade_page_pay(
        out_trade_no=order_id,#订单号
        total_amount=str(money),#支付金额
        subject="生鲜交易",#交易主体
        return_url="http://127.0.0.1:8000/Buyer/pay_result/",#支付完成要跳转的本地路由
        notify_url="http://127.0.0.1:8000/Buyer/pay_result/",#支付完成要跳转的异步路由
    )
    order = Order.objects.get(order_id = order_id)
    order.order_status = 2
    order.save()
    return HttpResponseRedirect("https://openapi.alipaydev.com/gateway.do?"+order_string)

def pay_result(request):
    """
    支付宝支付成功自动用get请求返回的参数
    #编码
    ?charset=utf-8
    #订单号
    out_trade_no=10001
    #订单类型
    method=alipay.trade.page.pay.return
    #订单金额
    total_amount=1000.01
    #校验值
    sign=i1tumAcbNGc0vt7CqDpY3fdOIXwdGeB5TY96ml9DkWiHWIaZoImYh76TeoqRZF80l%2Bq3MW0TnCy1wkgz10Jw2Z%2FnNcYL8Cl1lNUojxgALGMYmx5VyztUvqhkCnhrzwbOrYh%2Fiv4dQSJGDwVoPhEPueQZlX4pQqTQvp0iFyfkPoTq4N8kC%2BH7tC6tmQDZ5NcJaKbtJCxiZ%2Fgqj2709FDJM7o9YDv87398G%2FDKU6xSmNRKGDAdLG90iZDPJtoQNLg7NpNFCZau61DqBNmOFohWcqWNE%2BwxFCriu68pS%2F91%2Blq6VG%2BeDuFDKeRYzI3xBo96D1ECYc75UyTRrHDRQIp25Q%3D%3D
    #订单号
    trade_no=2019072622001411661000068009
    #用户的应用id
    auth_app_id=2016101000652502
    #版本
    version=1.0
    #商家的应用id
    app_id=2016101000652502
    #加密方式
    sign_type=RSA2
    #商家id
    seller_id=2088102178922590
    #时间
    timestamp=2019-07-26+19%3A31%3A36
    """
    return render(request,"buyer/pay_result.html",locals())

def goods_detail(request):
    goods_id = request.GET.get("goods_id")
    if goods_id:
        goods = Goods.objects.filter(id = goods_id).first()
        if goods:
            return render(request,"buyer/detail.html",locals())
    return HttpResponse("没有指定的商品")

def setOrderId(user_id,goods_id,store_id):
    """
    设置订单编号
    时间+用户id+商品的id+商铺id
    """
    strtime = time.strftime("%Y%m%d%H%M%S",time.localtime())
    return strtime+str(user_id)+str(goods_id)+str(store_id)

def place_order(request):
    if request.method == "POST":
        #post数据
        count = int(request.POST.get("count"))
        goods_id = request.POST.get("goods_id")
        #cookie的数据
        user_id = request.COOKIES.get("user_id")
        #数据库的数据
        goods = Goods.objects.get(id = goods_id)
        store_id=goods.store_id.id
        price = goods.goods_price
        #保存订单
        order = Order()
        order.order_id = setOrderId(str(user_id),str(goods_id),str(store_id))
        order.goods_count = count
        order.order_user = Buyer.objects.get(id = user_id)
        order.order_price = count*price
        order.order_status = 1
        order.save()
        #订单详情
        order_detail = OrderDetail()
        order_detail.order_id = order
        order_detail.goods_id = goods_id
        order_detail.goods_name = goods.goods_name
        order_detail.goods_price = goods.goods_price
        order_detail.goods_number = count
        order_detail.goods_total = count*goods.goods_price
        order_detail.goods_store = store_id
        order_detail.goods_image = goods.goods_image
        order_detail.save()

        detail = [order_detail]
        return render(request,"buyer/place_order.html",locals())
    else:
        order_id = request.GET.get("order_id")
        if order_id:
            order = Order.objects.get(id = order_id)
            detail = order.orderdetail_set.all()
            return render(request,"buyer/place_order.html",locals())
        else:
            return HttpResponse("非法请求")

def cart(request):
    user_id = request.COOKIES.get("user_id")
    goods_list = Cart.objects.filter(user_id = user_id)
    if request.method == "POST":
        post_data = request.POST
        cart_data = [] #收集前端传递过来的商品
        for k,v in post_data.items():
            if k.startswith("goods_"):
                cart_data.append(Cart.objects.get(id = int(v)))
        goods_count = len(cart_data) #提交过来的数据总的数量
        goods_total = sum([int(i.goods_total) for i in cart_data]) #订单的总价

        #修改使用聚类查询返回指定商品的总价
        #1.查询到所有商品
        cart_data = [] #收集前端传递过来的商品
        for k,v in post_data.items():
            if k.startswith("goods_"):
                cart_data.append(int(v))
        #2.使用in方法进行范围的划定，然后使用Sum方法进行计算
        cart_goods = Cart.objects.filter(id__in = cart_data).aggregate(Sum("goods_total")) #获取到总价

        order = Order()
        order.order_id = setOrderId(user_id,goods_count,"2")
        # 订单当中有多个商品或者多个店铺，使用goods_count来代替商品id，用2代替店铺id
        order.goods_count = goods_count
        order.order_user = Buyer.objects.get(id = user_id)
        order.order_price = goods_total
        order.order_status = 1
        order.save()
        #保存订单详情
        #这里的detail是购物车里的数据实例，不是商品的实例
        for detail in cart_data:
            order_detail = OrderDetail()
            order_detail.order_id = order #order是一条订单数据
            order_detail.goods_id = detail.goods_id
            order_detail.goods_name = detail.goods_name
            order_detail.goods_price = detail.goods_price
            order_detail.goods_number = detail.goods_number
            order_detail.goods_total = detail.goods_total
            order_detail.goods_store = detail.goods_store
            order_detail.goods_image = detail.goods_picture
            order_detail.save()
            #order是一条订单支付页
        url = "/Buyer/place_order/?order_id=%s"%order.id
        return HttpResponseRedirect(url)
    return render(request,"buyer/cart.html",locals())

def add_cart(request):
    result = {"state":"error","data":""}
    if request.method == "POST":
        count = int(request.POST.get("count")) #request请求
        goods_id = request.POST.get("goods_id")
        goods = Goods.objects.get(id = int(goods_id)) #数据库查询
        user_id = request.COOKIES.get("user_id") #cooikes数据
        cart = Cart()
        cart.goods_name = goods.goods_name
        cart.goods_price = goods.goods_price
        cart.goods_total = goods.goods_price*count
        cart.goods_number = count
        cart.goods_picture = goods.goods_image
        cart.goods_id = goods.id
        cart.goods_store = goods.store_id.id
        cart.user_id = user_id
        cart.save()
        result["state"] = "success"
        result["data"] = "商品添加成功"
    else:
        result["data"] = "请求错误"
    return JsonResponse(result)
# Create your views here.
