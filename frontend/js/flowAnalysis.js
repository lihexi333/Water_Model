let flowChart = null;

function initFlowRateChart() {
    const chartDom = document.getElementById('flowRateChart');
    flowChart = echarts.init(chartDom);
}

function updateFlowChart(reservoirName, data) {
    const option = {
        title: {
            text: `${reservoirName}流量变化趋势`
        },
        tooltip: {
            trigger: 'axis',
            formatter: function (params) {
                const date = new Date(params[0].value[0]);
                return `${date.toLocaleString()}<br />
                        流量: ${params[0].value[1].toFixed(2)} m³/s`;
            }
        },
        xAxis: {
            type: 'time',
            splitLine: {
                show: false
            }
        },
        yAxis: {
            type: 'value',
            name: '流量 (m³/s)',
            splitLine: {
                show: true
            }
        },
        series: [{
            name: '流量',
            type: 'line',
            smooth: true,
            symbol: 'none',
            areaStyle: {
                opacity: 0.2
            },
            data: data
        }]
    };

    flowChart.setOption(option);
}

// 页面加载完成后初始化图表
document.addEventListener('DOMContentLoaded', () => {
    initFlowRateChart();

    // 监听表单提交
    document.getElementById('predictionForm').addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const reservoir = document.getElementById('reservoir').value;
        const startTime = new Date(document.getElementById('startTime').value);
        const endTime = new Date(document.getElementById('endTime').value);

        // 这里应该是从后端获取数据的API调用
        // 现在用模拟数据演示
        const mockData = generateMockData(startTime, endTime);
        
        updateFlowChart(reservoir, mockData);
    });
});

// 生成模拟数据的函数
function generateMockData(startTime, endTime) {
    const data = [];
    const timeSpan = endTime - startTime;
    const pointCount = 100; // 生成100个数据点
    
    for (let i = 0; i < pointCount; i++) {
        const time = new Date(startTime.getTime() + (timeSpan * i / pointCount));
        // 生成50到150之间的随机流量数据
        const flow = 50 + Math.random() * 100;
        data.push([time, flow]);
    }
    
    return data;
} 