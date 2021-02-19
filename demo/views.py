import json
import pandas as pd
from django.http import HttpResponse
from rest_framework.views import APIView

from pyecharts.charts import Bar, Grid, Line, Pie, Tab
from pyecharts.faker import Faker
from pyecharts import options as opts
from pyecharts.globals import ThemeType
from .apps import PredictorConfig
from . import models


def get_tree_data():
    '''
    :return json
    '''

    name, data = models.tree_model_predict()
    return name, data


def get_historical_data():
    '''
    get historical data
    :return: retrieve useful data
    '''
    path = 'demo/data/cleaned_data.csv'
    history_data = pd.read_csv(path)
    print('read stat_data successfully')
    trans = history_data[['value', 'status', 'Date', 'Hour', 'Date_Time', 'Category', 'Lane Name']]
    trans.index = pd.to_datetime(trans['Date_Time'])

    exit_data = trans[trans['status'] == 'exit']['value'].resample('H').sum().fillna(0)
    enter_data = trans[trans['status'] == 'enter']['value'].resample('H').sum().fillna(0)
    hour_trans = exit_data + enter_data

    category = trans['Category'].value_counts()

    lane = trans['Lane Name'].value_counts()

    return hour_trans, exit_data, enter_data, category, lane


def response_as_json(data):
    '''
    :param data:
    :return: jason response
    '''
    json_str = json.dumps(data)
    response = HttpResponse(
        json_str,
        content_type="application/json",
    )
    response["Access-Control-Allow-Origin"] = "*"
    return response


def json_response(data, code=200):
    '''
    response to successful access
    :param data:
    :param code:
    :return: 200
    '''
    data = {
        "code": code,
        "msg": "success",
        "data": data,
    }
    return response_as_json(data)


def json_error(error_string="error", code=500, **kwargs):
    '''
    respose to unsuccessful access
    :param error_string:
    :param code:
    :param kwargs:
    :return: 500
    '''
    data = {
        "code": code,
        "msg": error_string,
        "data": {}
    }
    data.update(kwargs)
    return response_as_json(data)


JsonResponse = json_response
JsonError = json_error


# global tool box setting for chats
ToolBoxFeatureOpts = opts.global_options.ToolBoxFeatureOpts(
    save_as_image=opts.global_options.ToolBoxFeatureSaveAsImageOpts(title='download'),
    restore=opts.global_options.ToolBoxFeatureRestoreOpts(is_show=False),
    data_view=opts.global_options.ToolBoxFeatureDataViewOpts(is_show=False),
    data_zoom=opts.global_options.ToolBoxFeatureDataZoomOpts(is_show=True,
                                                             zoom_title='zoom',
                                                             back_title='clear selection'
                                                             ),
    magic_type=opts.global_options.ToolBoxFeatureMagicTypeOpts(line_title='line chart',
                                                               bar_title='bar chart',
                                                               stack_title='stack',
                                                               tiled_title='tiled'
                                                               ),
    brush=opts.global_options.ToolBoxFeatureBrushOpts(type_='clear')
)


def tree_bar_base():
    '''
    create bar chart for decision tree model
    :return: rendered chart as json file
    '''
    name, data = get_tree_data()

    bars = data.columns.values
    _index = data.index.values

    c = Bar(
        init_opts=opts.InitOpts(theme=ThemeType.WALDEN)).set_global_opts(
        title_opts=opts.TitleOpts(title=name),
        toolbox_opts=opts.ToolboxOpts(feature=ToolBoxFeatureOpts),
        datazoom_opts=opts.DataZoomOpts(),
    )

    for bar in bars:
        c.add_yaxis(bar, data[bar].tolist(), yaxis_index=None,
                    label_opts=opts.LabelOpts(is_show=False)
                    )

    c.add_xaxis(_index.tolist())
    c = (c.dump_options_with_quotes())
    return c


# get historical data
HourTrans, ExitData, EnterData, Category, Lane = get_historical_data()


def history_trans_base(hour_trans=HourTrans, exit_data=ExitData, enter_data=EnterData, ):
    '''
    create chart for historical transport data
    :param hour_trans: transport column of historical data
    :param exit_data: exit  column of historical data
    :param enter_data: enter column of historical data
    :return: rendered chart as json file
    '''
    _index = exit_data.index
    c = Line(
        init_opts=opts.InitOpts(theme=ThemeType.WALDEN)).set_global_opts(
        title_opts=opts.TitleOpts(title='Historical Entry and Exit Data'),
        toolbox_opts=opts.ToolboxOpts(feature=ToolBoxFeatureOpts),
        datazoom_opts=opts.DataZoomOpts(),
    )

    c.add_xaxis(_index.tolist())
    c.add_yaxis('Enter', enter_data.tolist(), label_opts=opts.LabelOpts(is_show=False))
    c.add_yaxis('Exit', exit_data.tolist(), label_opts=opts.LabelOpts(is_show=False))
    c.add_yaxis('Balance', hour_trans.tolist(), label_opts=opts.LabelOpts(is_show=False))
    c = c.dump_options_with_quotes()
    return c


def history_cate_base():
    '''
    create chart for historical category data
    :return: rendered chart as json file
    '''
    data_pair = [['A', 52], ['Contractors', 13962], ['Unknown', 219838], ['Employees', 970644]]
    c = Pie(
        init_opts=opts.InitOpts(theme=ThemeType.WALDEN)).set_global_opts(
        title_opts=opts.TitleOpts(title='Category of Entry and Exit Bar Chart'),
        toolbox_opts=opts.ToolboxOpts(feature=ToolBoxFeatureOpts),
    )
    c.add(
        series_name='',
        data_pair = data_pair,
    )
    c.set_series_opts(label_opts=opts.LabelOpts(formatter="{b}: {c}"))
    c = c.dump_options_with_quotes()
    return c


def history_lane_base():
    data_pair = [['Bollard Camera', 222934], ['Entrance Barrier', 386281], ['Exit Barrier', 595281]]
    c = Pie(
        init_opts=opts.InitOpts(theme=ThemeType.WALDEN)).set_global_opts(
        title_opts=opts.TitleOpts(title='Category of Entry and Exit Bar Chart'),
        toolbox_opts=opts.ToolboxOpts(feature=ToolBoxFeatureOpts),
    )
    c.add(
        series_name='',
        data_pair=data_pair,
    )
    c.set_series_opts(label_opts=opts.LabelOpts(formatter="{b}: {c}"))
    c = c.dump_options_with_quotes()
    return c


# classes for APIView
class TreeBarView(APIView):
    def get(self, request, *args, **kwargs):
        return JsonResponse(json.loads(tree_bar_base()))


class HistoryEView(APIView):
    def get(self, request, *args, **kwargs):
        return JsonResponse(json.loads(history_trans_base()))

class HistoryCView(APIView):
    def get(self, request, *args, **kwargs):
        return JsonResponse(json.loads(history_cate_base()))

class HistoryLView(APIView):
    def get(self, request, *args, **kwargs):
        return JsonResponse(json.loads(history_lane_base()))

class IndexView(APIView):
    def get(self, request, *args, **kwargs):
        return HttpResponse(content=open("./templates/index.html").read())
