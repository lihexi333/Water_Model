"""
This code is the tool registration part. By registering the tool, the model can call the tool.
This code provides extended functionality to the model, enabling it to call and interact with a variety of utilities
through defined interfaces.
"""

import inspect
import traceback
import logging
from copy import deepcopy
from pprint import pformat
from types import GenericAlias
from typing import get_origin, Annotated
import urllib.parse
import urllib.request
import ssl
import json
import difflib
_TOOL_HOOKS = {}
_TOOL_DESCRIPTIONS = {}


def register_tool(func: callable):
    tool_name = func.__name__
    tool_description = inspect.getdoc(func).strip()
    python_params = inspect.signature(func).parameters
    tool_params = []
    for name, param in python_params.items():
        annotation = param.annotation
        if annotation is inspect.Parameter.empty:
            raise TypeError(f"Parameter `{name}` missing type annotation")
        if get_origin(annotation) != Annotated:
            raise TypeError(f"Annotation type for `{name}` must be typing.Annotated")

        typ, (description, required) = annotation.__origin__, annotation.__metadata__
        typ: str = str(typ) if isinstance(typ, GenericAlias) else typ.__name__
        if not isinstance(description, str):
            raise TypeError(f"Description for `{name}` must be a string")
        if not isinstance(required, bool):
            raise TypeError(f"Required for `{name}` must be a bool")

        tool_params.append({
            "name": name,
            "description": description,
            "type": typ,
            "required": required
        })
    tool_def = {
        "name": tool_name,
        "description": tool_description,
        "params": tool_params
    }

    print("[registered tool] " + pformat(tool_def))
    _TOOL_HOOKS[tool_name] = func
    _TOOL_DESCRIPTIONS[tool_name] = tool_def

    return func


def dispatch_tool(tool_name: str, tool_params: dict) -> str:
    if tool_name not in _TOOL_HOOKS:
        return f"Tool `{tool_name}` not found. Please use a provided tool."
    tool_call = _TOOL_HOOKS[tool_name]
    try:
        ret = tool_call(**tool_params)
    except:
        ret = traceback.format_exc()
    return str(ret)


def get_tools() -> dict:
    return deepcopy(_TOOL_DESCRIPTIONS)


# Tool Definitions

def find_best_match(input_str: str, candidates: list) -> str:
    """
    在候选列表中找到与输入字符串最匹配的项。

    参数:
    input_str (str): 用户输入的字符串。
    candidates (list): 候选项列表。

    返回:
    str: 最匹配的候选项。
    """
    match = difflib.get_close_matches(input_str, candidates, n=1, cutoff=0.6)
    if match:
        return match[0]
    else:
        return None


def getPageData(api_url:str,page: int) -> dict:
    full_url = api_url + f"&pageNum={page}&pageSize=100"
    try:
        request = urllib.request.Request(full_url)
        request.add_header('Authorization', 'APPCODE 2e3185ab512b49c5b0b0a42044341dc4')
        response = urllib.request.urlopen(request)

        # 处理响应
        content = response.read().decode('utf-8')
        logging.info(f"Received response: {content}")
        content_dict = json.loads(content)  # 字典类型，数据在键值data里面
        # 分页拼接
        # todo
        data = content_dict["data"]["rows"]
    except Exception as e:
        logging.error(e)
    return data

@register_tool
def get_stations_info(
        province: Annotated[str, '行政区', True],
        station_name: Annotated[str, '站点的名字', True],
) -> list:
    """
    根据时间，行政区，站名等相关参数按要求查询水库的库水位，蓄水量，入库流速，坝顶高度。

    参数；
    pubtime:记录的时间
    province:行政区
    stations_name:站点的名字

    """

    #  构建完整的URL
    encoded_province = urllib.parse.quote(province)  # 对province参数进行URL编码
    api_url = f"https://hydro.market.alicloudapi.com/api/water_rain/stations?province={encoded_province}"
    full_url = api_url + "&pageNum=1&pageSize=100"

    try:
        # 发起HTTP请求
        request = urllib.request.Request(full_url)
        request.add_header('Authorization', 'APPCODE 2e3185ab512b49c5b0b0a42044341dc4')
        response = urllib.request.urlopen(request)

        # 处理响应
        content = response.read().decode('utf-8')
        logging.info(f"Received response: {content}")
        content_dict = json.loads(content)  # 字典类型，数据在键值data里面
        # 分页拼接
        # todo
        data = content_dict["data"]["rows"]
        total = content_dict["data"]["totalNum"]
        size = content_dict["data"]["pageSize"]
        pages =  int(total/size) if total%size == 0 else int(total/size) + 1
        if pages >1 :
            for page in range(1,pages):
                data = [*data, *getPageData(api_url,page)]

        if (station_name != None):
            station_name = find_best_match(station_name, [d['站名'] for d in data])
        filtered_data = data
        if (station_name != None):
            filtered_data = [d for d in filtered_data if station_name == d['站名']]

        return filtered_data

    except urllib.error.URLError as e:
        logging.error(f"Error fetching data: {e.reason}")
        return []

    except json.JSONDecodeError:
        logging.error("Error decoding JSON response.")
        return []

    except Exception as e:
        logging.exception(e)
        return []



@register_tool
def get_rain_info(
        pubtime: Annotated[str, '记录的时间', True],
        station_name: Annotated[str, '站点的名字', True],
        admi_area: Annotated[str, '行政区', True],
) -> list:
    """
    根据时间，行政区，站名等相关参数按要求查询水库的日雨量。

    参数；
    pubtime:记录的时间
    admi_area:行政区
    station_name:站点的名字

    """

    #  构建完整的URL
    api_url = "https://hydro.market.alicloudapi.com/api/water_rain/rain"
    query = "pubtime=" + str(pubtime)
    full_url = api_url + '?' + query
    if admi_area == '':
        admi_area = None
    try:
        # 发起HTTP请求
        request = urllib.request.Request(full_url)
        request.add_header('Authorization', 'APPCODE ' + "2e3185ab512b49c5b0b0a42044341dc4")
        response = urllib.request.urlopen(request)

        # 处理响应
        content = response.read().decode('utf-8')
        logging.info(f"Received response: {content}")
        content_dict = json.loads(content)#字典类型，数据在键值data里面
        data = content_dict["data"]

        if (admi_area != None):
            admi_area = find_best_match(admi_area, [d['行政区'] for d in data])
        if (station_name != None):
            station_name = find_best_match(station_name, [d['站名'] for d in data])

        filtered_data = data
        if (admi_area != None):
            filtered_data = [d for d in filtered_data if admi_area == d['行政区']]
        if (station_name != None):
            filtered_data = [d for d in filtered_data if station_name == d['站名']]


        return filtered_data

    except urllib.error.URLError as e:
        logging.error(f"Error fetching data: {e.reason}")
        return []

    except json.JSONDecodeError:
        logging.error("Error decoding JSON response.")
        return []

    except Exception as e:
        logging.exception(e)
        return []


@register_tool
def get_reservoir_info(
        pubtime: Annotated[str, '记录的时间', True],
        reservoir_name: Annotated[str, '水库的名字', True],
        admi_area: Annotated[str, '行政区', True],
) -> list:
    """
    根据时间，行政区，水库名等相关参数按要求查询水库的库水位，蓄水量，入库流速，坝顶高度。

    参数；
    pubtime:记录的时间
    admi_area:行政区
    reservoir_name:水库的名字


    """

    #  构建完整的URL
    api_url = "https://hydro.market.alicloudapi.com/api/water_rain/reservoir"
    query = "pubtime=" + str(pubtime)
    full_url = api_url + '?' + query
    if admi_area == '':
        admi_area = None
    try:
        # 发起HTTP请求
        request = urllib.request.Request(full_url)
        request.add_header('Authorization', "APPCODE 2e3185ab512b49c5b0b0a42044341dc4")
        response = urllib.request.urlopen(request)

        # 处理响应
        content = response.read().decode('utf-8')
        logging.info(f"Received response: {content}")
        content_dict = json.loads(content)#字典类型，数据在键值data里面
        data = content_dict["data"]
        for d in data:
            if "(坝上)" in d['库名']:
                d['库名'] = d['库名'].replace("(坝上)", "")
            if "（坝上）" in d['库名']:
                d['库名'] = d['库名'].replace("（坝上）", "")
        if (admi_area != None):
            admi_area = find_best_match(admi_area, [d['行政区'] for d in data])
        if (reservoir_name != None):
            reservoir_name = find_best_match(reservoir_name, [d['库名'] for d in data])

        filtered_data = data
        if (admi_area != None):
            filtered_data = [d for d in filtered_data if admi_area == d['行政区']]
        if (reservoir_name != None):
            filtered_data = [d for d in filtered_data if reservoir_name == d['库名']]

        if len(filtered_data) != 0:
            filtered_data[0]['库水位'] = str(filtered_data[0]['库水位'])
            filtered_data[0]['库水位'] += '米'
            filtered_data[0]['蓄水量'] = str(filtered_data[0]['蓄水量'])
            filtered_data[0]['蓄水量'] += '亿立方米'
            filtered_data[0]['入库流速'] = str(filtered_data[0]['入库流速'])
            filtered_data[0]['入库流速'] += '米/秒'
            filtered_data[0]['坝顶高程'] = str(filtered_data[0]['坝顶高程'])
            filtered_data[0]['坝顶高程'] += '米'
        return filtered_data

    except urllib.error.URLError as e:
        logging.error(f"Error fetching data: {e.reason}")
        return []

    except json.JSONDecodeError:
        logging.error("Error decoding JSON response.")
        return []

    except Exception as e:
        logging.exception(e)
        return []


# 配置日志
# logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

if __name__ == "__main__":
    print(dispatch_tool("get_reservoir_info",
                        {"pubtime": "2021-07-15",
                        "admi_area": None,
                        "catchment": None,
                        "river_name": "青龙",
                        "reservoir_name": "桃林口",
                         }
                        )
          )

# print(get_tools()) #获取已经注册的工具信息







