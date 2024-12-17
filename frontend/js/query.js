document.addEventListener('DOMContentLoaded', function() {
    const searchBtn = document.querySelector('.search-btn');
    
    searchBtn.addEventListener('click', function() {
        const queryType = document.getElementById('query-type').value;
        const resultsTable = document.querySelector('.results-table');
        const noResults = document.querySelector('.no-results');
        const tableBody = resultsTable.querySelector('tbody');
        
        // 根据查询类型执行不同的查询
        if (queryType === 'location') {
            // 地理位置查询
            const province = document.querySelector('#location-filters input[placeholder="行政区"]').value;
            const valley = document.querySelector('#location-filters input[placeholder="流域"]').value;
            const stationName = document.querySelector('#location-filters input[placeholder="站名"]').value;
            
            const params = new URLSearchParams({
                province: province,
                valley: valley,
                target_station: stationName,
                queried_variable: 'station_name'
            });
            
            fetchAndDisplayResults(`http://localhost:5000/api/stations?${params}`, 'location');
            
        } else if (queryType === 'real-time') {
            // 实时信息查询
            const river = document.querySelector('#real-time-filters input[placeholder="河名"]').value;
            const stationName = document.querySelector('#real-time-filters input[placeholder="库名"]').value;
            const pubtime = document.querySelector('#real-time-filters input[type="date"]').value;
            
            // 验证必填字段
            if (!river || !stationName) {
                alert('河名和库名为必填项！');
                return;
            }
            
            const params = new URLSearchParams({
                river: river,
                station_name: stationName,
                pubtime: pubtime || ''
            });
            
            fetchAndDisplayResults(`http://localhost:5000/api/reservoir?${params}`, 'real-time');
        }
        
        // 通用的获取和显示结果函数
        function fetchAndDisplayResults(apiUrl, type) {
            fetch(apiUrl)
                .then(response => {
                    if (!response.ok) {
                        throw new Error('网络响应错误: ' + response.status);
                    }
                    return response.json();
                })
                .then(data => {
                    console.log('API返回数据:', data);
                    console.log('查询类型:', type);
                    console.log('errCode:', data.errCode);
                    console.log('data属性:', data.data);
                    
                    tableBody.innerHTML = '';
                    
                    // 更新表头
                    const thead = resultsTable.querySelector('thead tr');
                    thead.innerHTML = type === 'location' ? `
                        <th>站名</th>
                        <th>行政区</th>
                        <th>地址</th>
                        <th>流域</th>
                        <th>水系</th>
                        <th>河名</th>
                        <th>测站类型</th>
                        <th>经度</th>
                        <th>纬度</th>
                    ` : `
                        <th>河名</th>
                        <th>库名</th>
                        <th>水位(m)</th>
                        <th>入库流量(m³/s)</th>
                        <th>出库流量(m³/s)</th>
                        <th>蓄水量(亿m³)</th>
                        <th>更新时间</th>
                    `;
                    
                    if (type === 'location') {
                        // 处理地理位置查询结果
                        const results = data.data || [];
                        console.log('处理的地理位置数据:', results);
                        
                        if (results && results.length > 0) {
                            resultsTable.style.display = 'table';
                            noResults.style.display = 'none';
                            
                            results.forEach(item => {
                                console.log('处理的单条数据:', item);
                                const row = document.createElement('tr');
                                row.innerHTML = `
                                    <td>${item.站名 || item.name || '暂无数据'}</td>
                                    <td>${item.行政区 || item.district || '暂无数据'}</td>
                                    <td>${item.地址 || item.address || '暂无数据'}</td>
                                    <td>${item.流域 || item.basin || '暂无数据'}</td>
                                    <td>${item.水系 || item.waterSystem || '暂无数据'}</td>
                                    <td>${item.河名 || item.river || '暂无数据'}</td>
                                    <td>${item.测站类型 || item.stationType || '暂无数据'}</td>
                                    <td>${item.经度 || item.longitude || '暂无数据'}</td>
                                    <td>${item.纬度 || item.latitude || '暂无数据'}</td>
                                `;
                                tableBody.appendChild(row);
                            });
                        } else {
                            console.log('没有找到地理位置数据');
                            resultsTable.style.display = 'none';
                            noResults.style.display = 'block';
                        }
                    } else {
                        // 处理实时信息查询结果
                        if (data.errCode === 0 && data.data && data.data.length > 0) {
                            resultsTable.style.display = 'table';
                            noResults.style.display = 'none';
                            
                            const item = data.data[0];
                            const row = document.createElement('tr');
                            row.innerHTML = `
                                <td>${item.河名 || '暂无数据'}</td>
                                <td>${item.库名 || '暂无数据'}</td>
                                <td>${item.库水位 || '暂无数据'}</td>
                                <td>${item.入库流速 || '暂无数据'}</td>
                                <td>${item.出库流速 || '暂无数据'}</td>
                                <td>${item.蓄水量 || '暂无数据'}</td>
                                <td>${item.同步时间 || '暂无数据'}</td>
                            `;
                            tableBody.appendChild(row);
                        } else {
                            resultsTable.style.display = 'none';
                            noResults.style.display = 'block';
                        }
                    }
                })
                .catch(error => {
                    console.error('查询出错:', error);
                    resultsTable.style.display = 'none';
                    noResults.style.display = 'block';
                    noResults.querySelector('p').textContent = `查询出错: ${error.message}`;
                });
        }
    });
}); 