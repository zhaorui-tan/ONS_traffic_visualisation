from django.apps import AppConfig
from django.conf import settings

import os
import pickle


class DemoConfig(AppConfig):
    name = 'ADS.demo'


class PredictorConfig(AppConfig):
    # create path to models
    path = os.path.join(settings.MODELS_VIS, 'models.p')

    # load models into separate variables
    # these will be accessible via this class
    with open(path, 'rb') as pickled:
        data = pickle.load(pickled)
    regressor = data['regressor']


class PredictorConfigExits(AppConfig):
    # create path to models
    path = os.path.join(settings.MODELS_VIS, 'models_exits.p')

    # load models into separate variables
    # these will be accessible via this class
    with open(path, 'rb') as pickled:
        data = pickle.load(pickled)

    regressor = data['regressor']
