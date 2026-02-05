import azure.functions as func
import logging
import json
import io
import base64
from psychrochart import PsychroChart
from psychrolib import SetUnitSystem, SI

app = func.FunctionApp(http_auth_level=func.AuthLevel.FUNCTION)

@app.route(route="generate_psychro_chart")
def generate_psychro_chart(req: func.HttpRequest) -> func.HttpResponse:
    """
    生成心理测量图表的Azure Function
    
    接收JSON参数:
    {
        "temp_min": 0,      # 最低温度 (°C)
        "temp_max": 40,     # 最高温度 (°C)
        "title": "My Chart" # 图表标题(可选)
    }
    """
    logging.info('开始处理心理测量图表生成请求')
    
    try:
        # 1. 解析输入参数
        try:
            req_body = req.get_json()
        except ValueError:
            # 如果没有传参数,使用默认值
            req_body = {}
        
        temp_min = req_body.get('temp_min', 0)
        temp_max = req_body.get('temp_max', 40)
        chart_title = req_body.get('title', 'Psychrometric Chart')
        
        logging.info(f'参数: temp_min={temp_min}, temp_max={temp_max}')
        
        # 2. 设置单位系统为SI (国际单位制)
        SetUnitSystem(SI)
        
        # 3. 创建基础图表配置
        chart_config = {
            "limits": {
                "range_temp_c": [temp_min, temp_max],
                "range_humidity_g_kg": [0, 30],
                "altitude_m": 0,
                "step_temp": 5.0
            },
            "saturation": {"color": [0, 0.3, 1.0], "linewidth": 2},
            "constant_rh": {"color": [0.0, 0.5, 1.0, 0.7], "linewidth": 1},
            "constant_v": {"color": [0.2, 0.2, 0.2, 0.7], "linewidth": 0.5},
            "constant_h": {"color": [1.0, 0.4, 0.0, 0.7], "linewidth": 1},
            "constant_wet_temp": {"color": [0.0, 0.4, 0.0, 0.7], "linewidth": 1},
            "chart_params": {
                "with_constant_rh": True,
                "with_constant_v": True,
                "with_constant_h": True,
                "with_constant_wet_temp": True,
                "with_zones": False
            }
        }
        
        # 4. 创建图表对象
        chart = PsychroChart(chart_config, figsize=(12, 8))
        
        # 5. 添加标题
        chart.plot()
        ax = chart.axes
        ax.set_title(chart_title, fontsize=16, fontweight='bold')
        
        # 6. 将图表保存为PNG (base64编码)
        img_buffer = io.BytesIO()
        chart.save(img_buffer, format='png', dpi=150, transparent=False)
        img_buffer.seek(0)
        
        # 转换为base64字符串
        img_base64 = base64.b64encode(img_buffer.read()).decode('utf-8')
        
        # 7. 返回结果
        response_data = {
            "status": "success",
            "message": "图表生成成功",
            "chart_format": "png",
            "image_base64": img_base64,
            "parameters": {
                "temp_min": temp_min,
                "temp_max": temp_max,
                "title": chart_title
            }
        }
        
        logging.info('图表生成成功')
        
        return func.HttpResponse(
            json.dumps(response_data, ensure_ascii=False),
            mimetype="application/json",
            status_code=200
        )
        
    except Exception as e:
        logging.error(f'生成图表时发生错误: {str(e)}')
        
        error_response = {
            "status": "error",
            "message": str(e)
        }
        
        return func.HttpResponse(
            json.dumps(error_response, ensure_ascii=False),
            mimetype="application/json",
            status_code=500
        )


# 添加一个测试端点(可选)
@app.route(route="health")
def health_check(req: func.HttpRequest) -> func.HttpResponse:
    """健康检查端点"""
    return func.HttpResponse(
        json.dumps({"status": "healthy", "service": "psychro-chart-generator"}),
        mimetype="application/json"
    )