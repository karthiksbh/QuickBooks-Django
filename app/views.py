import requests
from rest_framework.views import APIView
from rest_framework.response import Response
from .client import AuthClient
from . import tokens as tokens
import uuid
from .models import Transaction

# Create your views here.
auth_client = AuthClient(**tokens.client_secrets)

def refresh_token():
    response = auth_client.refresh(refresh_token=tokens.refreshToken)
    return response


class QuickbooksCreatePaymentView(APIView):
    def post(self, request):
        try:
            response = refresh_token()
            accessToken = response["access_token"]
            base_url = 'https://sandbox.api.intuit.com/quickbooks/v4/payments/charges/'
            auth_header = 'Bearer {0}'.format(accessToken)
            headers = {
                'Authorization': auth_header,
                'Request-Id': str(uuid.uuid4()),
                'Content-Type': 'application/json',
                'User-Agent': 'Mozilla/5.0',
                'Accept-Encoding': 'gzip, deflate, br'
            }
            data = request.data
            amount = data.get('amount')
            payment_method = data.get('payment_method')

            if payment_method == 'card':    
                payment_data = {
                    'amount': float(amount),
                    'currency': data.get('currency'),
                    'card': {
                        'name': data.get('card_name'),
                        'address':data.get('address'),
                        'expYear': data.get('exp_year'),
                        'expMonth': data.get('exp_month'),
                        'number': data.get('number'),
                        'cvc': data.get('cvc')
                    },
                    'context': {
                        'mobile': False,
                        'isEcommerce': True
                    }
                }
            elif payment_method == 'digital_wallet':
                payment_data = {
                    'amount': float(amount),
                    'currency': data.get('currency'),
                    'digitalWallet': {
                        'type': data.get('digital_wallet_type'),
                        'id': data.get('digital_wallet_id')
                    },
                    'context': {
                        'mobile': False,
                        'isEcommerce': True
                    }
                }
            elif payment_method == 'internet_banking':
                payment_data = {
                    'amount': float(amount),
                    'currency': data.get('currency'),
                    'bankTransfer': {
                        'account': data.get('bank_account_number'),
                        'routingNumber': data.get('bank_routing_number')
                    },
                    'context': {
                        'mobile': False,
                        'isEcommerce': True
                    }
                }
            else:
                return Response({'error': 'Invalid payment method'})

            response = requests.post(base_url, headers=headers, json=payment_data)
            if response.status_code == 201:
                response_data = response.json()
                charge_id = response_data.get('id')
                Transaction.objects.create(order_id=charge_id,amount=amount)
                return Response({'message':'Payment Success','charge_id': charge_id,'success':True})
            else:
                return Response({'error': 'Failed to create a payment','success':False})
        except Exception as e:
            return Response({'error': str(e)})


class QuickbooksVerifyPaymentView(APIView):
    def post(self, request):
        try:
            response = refresh_token()
            accessToken = response["access_token"]
            data = request.data
            charge_id = data.get('charge_id')
            headers = {'Authorization': f'Bearer {accessToken}'}
            response = requests.get(f'https://sandbox.api.intuit.com/quickbooks/v4/payments/charges/{charge_id}', headers=headers)

            if response.status_code == 200:
                response_data = response.json()
                status = response_data.get('status')
                transaction = Transaction.objects.get(order_id=charge_id)
                transaction.payment_status = 'success'
                transaction.save()
                return Response({'status': status,'message':'Payment Successfully verified','success':True})
            else:
                return Response({'error': 'Failed to verify payment','success':False})
        except Exception as e:
            return Response({'error': str(e)})
