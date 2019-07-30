from alipay import AliPay
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
    out_trade_no="12345",#订单号
    total_amount=str(1000.01),#支付金额
    subject="生鲜交易",#交易主体
    return_url=None,
    notify_url=None,
)

print("https://openapi.alipaydev.com/gateway.do?"+order_string)