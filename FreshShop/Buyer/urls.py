from django.urls import path,include
from Buyer.views import *
urlpatterns = [
    path("register/",register),
    path("login/",login),
    path("index/",index),
    path("register/",register),
    path("goods_list/",goods_list),
    path("goods_detail/",goods_detail),
    path("place_order/",place_order),
    path(r"cart/",cart),
    path(r"add_cart/",add_cart),
]
urlpatterns += [
    path("base/",base),
    path("pay_order/",pay_order),
    path("pay_result/",pay_result),
    # path("base/",base),
]