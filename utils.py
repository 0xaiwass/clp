from kavenegar import *

def send_otp_code(phone, code):
    try:
        api = KavenegarAPI('4C586D384C63776238427379694A73697930476B54495A37636258364655676371792F74616B4A727047413D')
        params = {
            'receptor':phone,
            'template':'template',
            'token':code,
            'type':'sms',
        }
        response = api.verify_lookup(params)
        print(response)
    except APIException as e:
        print(e)
    except HTTPException as e:
        print(e)