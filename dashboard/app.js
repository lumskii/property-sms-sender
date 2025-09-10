const API_BASE = 'http://localhost:5000/api';

let countChart = null;

async function fetchData(endpoint) {
    try {
        const response = await fetch(`${API_BASE}${endpoint}`);
        return await response.json();
    } catch (error) {
        console.error(`Error fetching ${endpoint}:`, error);
        return null;
    }
}

function updateStats(statistics) {
    document.getElementById('total-dealers').textContent = statistics.total_dealers || 0;
    document.getElementById('whatsapp-sent').textContent = statistics.whatsapp_sent || 0;
    document.getElementById('sms-sent').textContent = statistics.sms_sent || 0;
    document.getElementById('both-sent').textContent = statistics.both_sent || 0;
}

function updateAgentStatus(status) {
    const agents = ['retrieval', 'whatsapp', 'sms'];
    
    agents.forEach(agent => {
        const agentData = status[`${agent}_agent`];
        if (agentData) {
            const card = document.getElementById(`${agent}-agent`);
            const statusIndicator = card.querySelector('.status-indicator');
            const statusText = card.querySelector('.status-text');
            const lastRun = card.querySelector('.last-run');
            const runBtn = card.querySelector('.run-btn');
            
            statusIndicator.setAttribute('data-status', agentData.status);
            statusText.textContent = agentData.status.charAt(0).toUpperCase() + agentData.status.slice(1);
            
            if (agentData.last_run) {
                const date = new Date(agentData.last_run);
                lastRun.textContent = `Last run: ${date.toLocaleString()}`;
            }
            
            runBtn.disabled = agentData.status === 'running';
        }
    });
}

function updateDealersTable(dealers) {
    const tbody = document.querySelector('#dealers-table tbody');
    
    if (!dealers || dealers.length === 0) {
        tbody.innerHTML = '<tr><td colspan="6" class="no-data">No dealers found</td></tr>';
        return;
    }
    
    const recentDealers = dealers.slice(-20).reverse();
    
    tbody.innerHTML = recentDealers.map(dealer => `
        <tr>
            <td>${dealer.name || 'N/A'}</td>
            <td>${dealer.mobile || 'N/A'}</td>
            <td>${dealer.source || 'N/A'}</td>
            <td>
                ${dealer.whatsapp_sent 
                    ? '<span class="success-badge">Sent</span>' 
                    : '<span class="pending-badge">Pending</span>'}
            </td>
            <td>
                ${dealer.sms_sent 
                    ? '<span class="success-badge">Sent</span>' 
                    : '<span class="pending-badge">Pending</span>'}
            </td>
            <td>${new Date(dealer.added_on).toLocaleDateString()}</td>
        </tr>
    `).join('');
}

function updateCountChart(statistics) {
    const ctx = document.getElementById('count-chart').getContext('2d');
    
    const countHistory = statistics.count_history || [];
    
    const labels = countHistory.map(item => {
        const date = new Date(item.timestamp);
        return date.toLocaleDateString() + ' ' + date.toLocaleTimeString();
    });
    
    const data = countHistory.map(item => item.count);
    
    if (countChart) {
        countChart.destroy();
    }
    
    countChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: 'Total Dealers',
                data: data,
                borderColor: '#3498db',
                backgroundColor: 'rgba(52, 152, 219, 0.1)',
                tension: 0.1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true
                }
            }
        }
    });
}

async function runAgent(agentType) {
    const response = await fetch(`${API_BASE}/run/${agentType}`);
    const result = await response.json();
    
    if (result.message) {
        alert(result.message);
        setTimeout(updateDashboard, 2000);
    }
}

async function updateDashboard() {
    const [status, statistics, dealers] = await Promise.all([
        fetchData('/status'),
        fetchData('/statistics'),
        fetchData('/dealers')
    ]);
    
    if (status) {
        updateAgentStatus(status);
        if (status.statistics) {
            updateStats(status.statistics);
            updateCountChart(status.statistics);
        }
    }
    
    if (statistics) {
        updateStats(statistics);
        updateCountChart(statistics);
    }
    
    if (dealers) {
        updateDealersTable(dealers);
    }
    
    document.querySelector('#last-update span').textContent = new Date().toLocaleString();
}

updateDashboard();

setInterval(updateDashboard, 5000);

window.runAgent = runAgent;