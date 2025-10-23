// Dashboard JavaScript for Internet Speed Monitor
class SpeedMonitorDashboard {
    constructor() {
        this.currentTimeRange = 24; // hours
        this.speedChart = null;
        this.pingChart = null;
        this.refreshInterval = null;
        
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.initializeCharts();
        this.loadInitialData();
        this.startAutoRefresh();
    }

    setupEventListeners() {
        // Time range buttons
        document.querySelectorAll('[data-hours]').forEach(btn => {
            btn.addEventListener('click', (e) => {
                this.changeTimeRange(parseInt(e.target.dataset.hours));
                
                // Update active button
                document.querySelectorAll('[data-hours]').forEach(b => b.classList.remove('active'));
                e.target.classList.add('active');
            });
        });

        // Refresh button
        window.refreshData = () => this.refreshData();
    }

    async loadInitialData() {
        this.updateStatus('Connecting...', 'warning');
        
        try {
            await Promise.all([
                this.loadStats(),
                this.loadChartData(),
                this.loadRecentTests(),
                this.loadSystemStatus()
            ]);
            
            this.updateStatus('Connected', 'online');
        } catch (error) {
            console.error('Failed to load initial data:', error);
            this.updateStatus('Connection Error', 'offline');
        }
    }

    async refreshData() {
        const refreshBtn = document.querySelector('[onclick="refreshData()"]');
        const refreshIndicator = document.getElementById('refresh-indicator');
        
        refreshBtn.disabled = true;
        refreshIndicator.style.display = 'inline';
        refreshIndicator.classList.add('spinning');
        
        try {
            await this.loadInitialData();
        } finally {
            refreshBtn.disabled = false;
            refreshIndicator.style.display = 'none';
            refreshIndicator.classList.remove('spinning');
        }
    }

    changeTimeRange(hours) {
        this.currentTimeRange = hours;
        this.loadStats();
        this.loadChartData();
    }

    updateStatus(text, status) {
        const statusIndicator = document.getElementById('status-indicator');
        const statusText = document.getElementById('status-text');
        
        statusIndicator.className = `status-indicator status-${status}`;
        statusText.textContent = text;
    }

    async loadStats() {
        try {
            const response = await fetch(`/api/stats?hours=${this.currentTimeRange}`);
            const stats = await response.json();
            
            document.getElementById('avg-download').textContent = 
                stats.download ? stats.download.avg.toFixed(1) : '--';
            document.getElementById('avg-upload').textContent = 
                stats.upload ? stats.upload.avg.toFixed(1) : '--';
            document.getElementById('avg-ping').textContent = 
                stats.ping ? stats.ping.avg.toFixed(1) : '--';
            document.getElementById('success-rate').textContent = 
                stats.success_rate ? stats.success_rate.toFixed(1) : '--';
                
        } catch (error) {
            console.error('Failed to load stats:', error);
        }
    }

    async loadChartData() {
        try {
            this.showChartLoading('speed-chart-loading');
            this.showChartLoading('ping-chart-loading');
            
            const response = await fetch(`/api/chart-data?hours=${this.currentTimeRange}`);
            const data = await response.json();
            
            this.updateSpeedChart(data);
            this.updatePingChart(data);
            
        } catch (error) {
            console.error('Failed to load chart data:', error);
        } finally {
            this.hideChartLoading('speed-chart-loading');
            this.hideChartLoading('ping-chart-loading');
        }
    }

    async loadRecentTests() {
        try {
            const response = await fetch('/api/recent?limit=20');
            const tests = await response.json();
            
            const container = document.getElementById('recent-tests');
            
            if (!tests || tests.length === 0) {
                container.innerHTML = '<p class="text-muted text-center">No recent tests found</p>';
                return;
            }
            
            const html = tests.map(test => {
                const timestamp = new Date(test.timestamp).toLocaleString();
                const isSuccess = !test.error_type && test.download_mbps;
                
                if (isSuccess) {
                    return `
                        <div class="test-item test-success">
                            <div class="d-flex justify-content-between align-items-center">
                                <div>
                                    <div class="speed-value">
                                        ↓ ${parseFloat(test.download_mbps).toFixed(1)} Mbps
                                        ↑ ${parseFloat(test.upload_mbps).toFixed(1)} Mbps
                                    </div>
                                    <div class="timestamp">${timestamp}</div>
                                </div>
                                <div class="text-end">
                                    <small class="text-muted">${parseFloat(test.ping_ms).toFixed(1)}ms</small>
                                    ${test.server_name ? `<br><small class="text-muted">${test.server_name}</small>` : ''}
                                </div>
                            </div>
                        </div>
                    `;
                } else {
                    return `
                        <div class="test-item test-failed">
                            <div class="d-flex justify-content-between align-items-center">
                                <div>
                                    <div class="speed-value text-danger">
                                        Test Failed
                                        <span class="failure-badge">${test.error_type || 'Unknown'}</span>
                                    </div>
                                    <div class="timestamp">${timestamp}</div>
                                </div>
                                <div class="text-end">
                                    <small class="text-muted">Error</small>
                                </div>
                            </div>
                        </div>
                    `;
                }
            }).join('');
            
            container.innerHTML = html;
            
        } catch (error) {
            console.error('Failed to load recent tests:', error);
            document.getElementById('recent-tests').innerHTML = 
                '<p class="text-danger text-center">Failed to load recent tests</p>';
        }
    }

    async loadSystemStatus() {
        try {
            const response = await fetch('/api/status');
            const status = await response.json();
            
            document.getElementById('data-source').textContent = status.data_source;
            
            const localStatus = status.local_data ? 
                `✓ Available (${(status.local_data_size / 1024).toFixed(1)} KB)` : 
                '✗ Not found';
            document.getElementById('local-status').textContent = localStatus;
            
            const smbStatus = status.smb_data ? 
                `✓ Available (${(status.smb_data_size / 1024).toFixed(1)} KB)` : 
                status.smb_mounted ? '⚠ Mount OK, no data' : '✗ Not mounted';
            document.getElementById('smb-status').textContent = smbStatus;
            
        } catch (error) {
            console.error('Failed to load system status:', error);
        }
    }

    initializeCharts() {
        // Speed Chart
        const speedCtx = document.getElementById('speedChart').getContext('2d');
        this.speedChart = new Chart(speedCtx, {
            type: 'line',
            data: {
                labels: [],
                datasets: [
                    {
                        label: 'Download Speed (Mbps)',
                        data: [],
                        borderColor: '#007bff',
                        backgroundColor: 'rgba(0, 123, 255, 0.1)',
                        fill: true,
                        tension: 0.4,
                        spanGaps: false  // Don't connect points across gaps
                    },
                    {
                        label: 'Upload Speed (Mbps)',
                        data: [],
                        borderColor: '#28a745',
                        backgroundColor: 'rgba(40, 167, 69, 0.1)',
                        fill: true,
                        tension: 0.4,
                        spanGaps: false  // Don't connect points across gaps
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: true,
                        position: 'top'
                    }
                },
                scales: {
                    x: {
                        type: 'time',
                        time: {
                            displayFormats: {
                                hour: 'MMM dd HH:mm',
                                day: 'MMM dd'
                            }
                        },
                        title: {
                            display: true,
                            text: 'Time'
                        },
                        ticks: {
                            source: 'data',  // Only show ticks where data points exist
                            autoSkip: true,
                            maxTicksLimit: 10
                        }
                    },
                    y: {
                        beginAtZero: true,
                        title: {
                            display: true,
                            text: 'Speed (Mbps)'
                        }
                    }
                },
                interaction: {
                    intersect: false,
                    mode: 'index'
                }
            }
        });

        // Ping Chart
        const pingCtx = document.getElementById('pingChart').getContext('2d');
        this.pingChart = new Chart(pingCtx, {
            type: 'line',
            data: {
                labels: [],
                datasets: [
                    {
                        label: 'Ping (ms)',
                        data: [],
                        borderColor: '#ffc107',
                        backgroundColor: 'rgba(255, 193, 7, 0.1)',
                        fill: true,
                        tension: 0.4,
                        spanGaps: false  // Don't connect points across gaps
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: true,
                        position: 'top'
                    }
                },
                scales: {
                    x: {
                        type: 'time',
                        time: {
                            displayFormats: {
                                hour: 'MMM dd HH:mm',
                                day: 'MMM dd'
                            }
                        },
                        title: {
                            display: true,
                            text: 'Time'
                        },
                        ticks: {
                            source: 'data',  // Only show ticks where data points exist
                            autoSkip: true,
                            maxTicksLimit: 10
                        }
                    },
                    y: {
                        beginAtZero: true,
                        title: {
                            display: true,
                            text: 'Latency (ms)'
                        }
                    }
                },
                interaction: {
                    intersect: false,
                    mode: 'index'
                }
            }
        });
    }

    updateSpeedChart(data) {
        if (!this.speedChart || !data.successful_tests) return;
        
        // Create data points for all tests (successful and failed as 0)
        const downloadData = [];
        const uploadData = [];
        
        data.successful_tests.forEach(test => {
            downloadData.push({
                x: test.timestamp,
                y: test.download_speed,
                isFailed: test.is_failed || false
            });
            uploadData.push({
                x: test.timestamp,
                y: test.upload_speed,
                isFailed: test.is_failed || false
            });
        });
        
        this.speedChart.data.datasets[0].data = downloadData;
        this.speedChart.data.datasets[1].data = uploadData;
        this.speedChart.update();
    }

    updatePingChart(data) {
        if (!this.pingChart || !data.successful_tests) return;
        
        // Create data points for all tests (successful and failed as 0)
        const pingData = [];
        
        data.successful_tests.forEach(test => {
            pingData.push({
                x: test.timestamp,
                y: test.ping_time,
                isFailed: test.is_failed || false
            });
        });
        
        this.pingChart.data.datasets[0].data = pingData;
        this.pingChart.update();
    }

    showChartLoading(elementId) {
        const loading = document.getElementById(elementId);
        if (loading) loading.style.display = 'flex';
    }

    hideChartLoading(elementId) {
        const loading = document.getElementById(elementId);
        if (loading) loading.style.display = 'none';
    }

    startAutoRefresh() {
        // Refresh data every 5 minutes
        this.refreshInterval = setInterval(() => {
            this.loadStats();
            this.loadRecentTests();
            this.loadSystemStatus();
            
            // Only refresh charts every 15 minutes to avoid too much load
            if (new Date().getMinutes() % 15 === 0) {
                this.loadChartData();
            }
        }, 5 * 60 * 1000);
    }

    stopAutoRefresh() {
        if (this.refreshInterval) {
            clearInterval(this.refreshInterval);
            this.refreshInterval = null;
        }
    }
}

// Initialize dashboard when page loads
document.addEventListener('DOMContentLoaded', () => {
    window.dashboard = new SpeedMonitorDashboard();
});

// Clean up on page unload
window.addEventListener('beforeunload', () => {
    if (window.dashboard) {
        window.dashboard.stopAutoRefresh();
    }
});