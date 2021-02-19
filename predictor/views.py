from django.shortcuts import render
from .apps import PredictorConfig, PredictorConfigExits
from django.http import JsonResponse
from rest_framework.views import APIView


class call_model(APIView):
	def get(self,request):
		if request.method == 'GET':


			temp = int(request.GET.get('temp'))
			precipitation = int(request.GET.get('precipitation'))
			hour = int(request.GET.get('hour'))	
			dayofweek = int(request.GET.get('dayofweek'))
			bank_holiday = int(request.GET.get('bank_holiday'))	

			prediction = [[temp, precipitation,hour,dayofweek,bank_holiday]]

			prediction_entrants = PredictorConfig.regressor.predict(prediction)[0]
			prediction_leavers = PredictorConfigExits.regressor.predict(prediction)[0]

			response = {'Expected Entrants': prediction_entrants, 'Expected Leavers': prediction_leavers}



			# return response
			return JsonResponse(response)
