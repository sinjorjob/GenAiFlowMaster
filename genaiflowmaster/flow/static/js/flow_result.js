let editor;

document.addEventListener('DOMContentLoaded', function() {
    const id = document.getElementById("drawflow");
    editor = new Drawflow(id);
    editor.start();
    editor.zoom_out();
    editor.zoom_out();
    editor.zoom_out();
    editor.zoom_out();

    loadFlowData();
    renderNodeDetails();
    setInitialNodeStatuses();
    startAutoUpdate();
    addAnimationToEdges();
});

function addAnimationToEdges() {
    const connections = document.querySelectorAll('.connection');
    connections.forEach(connection => {
        const path = connection.querySelector('.main-path');
        if (path) {
            path.setAttribute('marker-end', 'url(#arrowhead)');
        }
    });
}

function loadFlowData() {
    editor.import(flowData);
    Object.entries(editor.drawflow.drawflow.Home.data).forEach(([nodeId, node]) => {
        updateNodeDisplay(nodeId, node.data);
    });
    
    nodeRunLogs.forEach(log => {
        const nodeId = log.node_id;
        const sequence = log.sequence;
        addSequenceNumber(nodeId, sequence);
        addStatusBadge(nodeId, log.status);
    });
}

function updateNodeDisplay(nodeId, nodeData) {
    const nodeElement = document.getElementById(`node-${nodeId}`);
    if (nodeElement) {
        const titleElement = nodeElement.querySelector('.title-box');
        if (titleElement) {
            titleElement.textContent = nodeData.name || 'Untitled Node';
        }
    }
}

function addSequenceNumber(nodeId, sequence) {
    const nodeElement = document.getElementById(`node-${nodeId}`);
    if (nodeElement) {
        let sequenceElement = nodeElement.querySelector('.sequence-number');
        if (!sequenceElement) {
            sequenceElement = document.createElement('div');
            sequenceElement.className = 'sequence-number';
            nodeElement.insertBefore(sequenceElement, nodeElement.firstChild);
        }
        sequenceElement.textContent = sequence;
    }
}

function addStatusBadge(nodeId, status) {
    const nodeElement = document.getElementById(`node-${nodeId}`);
    if (nodeElement) {
        let statusElement = nodeElement.querySelector('.status-badge');
        if (!statusElement) {
            statusElement = document.createElement('div');
            statusElement.className = 'status-badge';
            nodeElement.appendChild(statusElement);
        }
        statusElement.textContent = getStatusJapanese(status);
        statusElement.className = `status-badge status-${status}`;
    }
}

function renderNodeDetails() {
    const nodeDetailsContainer = document.getElementById('node-details');
    nodeDetailsContainer.innerHTML = '<h2>ノード実行履歴</h2>';

    nodeRunLogs.sort((a, b) => a.sequence - b.sequence);

    nodeRunLogs.forEach(log => {
        const nodeDetail = document.createElement('div');
        nodeDetail.className = 'node-detail';
        nodeDetail.setAttribute('data-node-id', log.node_id);
        
        const statusBadge = `<span class="status-badge status-${log.status}">${getStatusJapanese(log.status)}</span>`;
        
        nodeDetail.innerHTML = `
            <div class="node-detail-header">
                <h3>
                    <span class="sequence-badge">実行順序: ${log.sequence}</span>
                    <span class="node-name">${log.node_name}</span>
                    ${statusBadge}
                </h3>
                <span class="expand-icon">▼</span>
            </div>
            <div class="node-detail-content">
                <div class="data-section">
                    <h4>入力データ:</h4>
                    ${renderInputData(log.input_data)}
                </div>
                <div class="data-section">
                    <h4>出力データ:</h4>
                    ${renderOutputData(log.output_data)}
                </div>
            </div>
        `;
        nodeDetailsContainer.appendChild(nodeDetail);

        nodeDetail.querySelector('.node-detail-header').addEventListener('click', function() {
            nodeDetail.classList.toggle('expanded');
        });
    });
}

function renderInputData(data) {
    const previousOutput = data.previous_output?.result || "データなし";
    const nodeData = data.node_data || {};
    
    return `
        <div class="data-item">
            <label>前のノードの出力:</label>
            <div class="value previous-output-value">${previousOutput}</div>
        </div>
        <div class="data-item">
            <label>ノード名:</label>
            <div class="value node-name-value">${nodeData.name || "未設定"}</div>
        </div>
        <div class="data-item">
            <label>システムプロンプト:</label>
            <div class="value system-prompt-value">${nodeData.system_prompt || "未設定"}</div>
        </div>
        <div class="data-item">
            <label>指示:</label>
            <div class="value instruction-value">${nodeData.instruction || "未設定"}</div>
        </div>
    `;
}

function renderOutputData(data) {
    let outputHtml = '';
    if (data.error) {
        outputHtml = `
            <div class="data-item">
                <label>エラー:</label>
                <div class="value error-message">${data.error}</div>
            </div>`;            
    } else {
        outputHtml = `
            <div class="data-item">
                <label>結果:</label>
                <div class="value output-result-value">${data.result || "データなし"}</div>
            </div>`;
    }
    outputHtml += `
        <div class="timestamp">
            実行日時: ${formatTimestamp(data.timestamp)}
        </div>`;
    return outputHtml;
}

function formatTimestamp(timestamp) {
    if (!timestamp) return "不明";
    const date = new Date(timestamp);
    return new Intl.DateTimeFormat('ja-JP', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit',
        timeZone: 'Asia/Tokyo'
    }).format(date) + ' JST';
}

function getStatusJapanese(status) {
    const statusMap = {
        'PENDING': '待機中',
        'RUNNING': '実行中',
        'COMPLETED': '完了',
        'FAILED': '失敗'
    };
    return statusMap[status] || status;
}

function startAutoUpdate() {
    setInterval(updateFlowStatus, 5000);  // 5秒ごとに更新
}

function updateFlowStatus() {
    fetch(`/get_flow_run_status/${flowRunId}/`)
        .then(response => response.json())
        .then(data => {
            updateNodeStatus(data.node_data);
            updateNodeDetails(data.node_data);
        })
        .catch(error => console.error('Error:', error));
}

function updateNodeStatus(nodeData) {
    nodeData.forEach(node => {
        const nodeElement = document.getElementById(`node-${node.node_id}`);
        if (nodeElement) {
            // ノードの状態を更新
            nodeElement.className = `drawflow-node node ${node.status === 'RUNNING' ? 'running' : ''}`;
            
            // ステータスバッジを更新
            let statusBadge = nodeElement.querySelector('.status-badge');
            if (statusBadge) {
                statusBadge.className = `status-badge status-${node.status}`;
                statusBadge.textContent = getStatusJapanese(node.status);
            }
        }
    });
}

function updateNodeDetails(nodeData) {
    nodeData.forEach(node => {
        const nodeDetail = document.querySelector(`.node-detail[data-node-id="${node.node_id}"]`);
        if (nodeDetail) {
            // ステータスバッジを更新
            const statusBadge = nodeDetail.querySelector('.status-badge');
            if (statusBadge) {
                statusBadge.className = `status-badge status-${node.status}`;
                statusBadge.textContent = getStatusJapanese(node.status);
            }

            // ノード名を更新
            const nodeNameElement = nodeDetail.querySelector('.node-name-value');
            if (nodeNameElement && node.input_data && node.input_data.node_data) {
                nodeNameElement.textContent = node.input_data.node_data.name || "未設定";
            }

            // システムプロンプトを更新
            const systemPromptElement = nodeDetail.querySelector('.system-prompt-value');
            if (systemPromptElement && node.input_data && node.input_data.node_data) {
                systemPromptElement.textContent = node.input_data.node_data.system_prompt || "未設定";
            }

            // 指示を更新
            const instructionElement = nodeDetail.querySelector('.instruction-value');
            if (instructionElement && node.input_data && node.input_data.node_data) {
                instructionElement.textContent = node.input_data.node_data.instruction || "未設定";
            }

            // 前のノードの出力を更新
            const previousOutputElement = nodeDetail.querySelector('.previous-output-value');
            if (previousOutputElement && node.input_data && node.input_data.previous_output) {
                previousOutputElement.textContent = node.input_data.previous_output.result || "データなし";
            }

            // 出力データを更新
            const outputContentElement = nodeDetail.querySelector('.node-detail-content');
            if (outputContentElement && node.output_data) {
                const outputSection = outputContentElement.querySelector('.data-section:last-child');
                if (outputSection) {
                    outputSection.innerHTML = `
                        <h4>出力データ:</h4>
                        ${renderOutputData(node.output_data)}
                    `;
                }
            }
        }
    });
}

function setInitialNodeStatuses() {
    nodeRunLogs.forEach(log => {
        const nodeElement = document.getElementById(`node-${log.node_id}`);
        if (nodeElement && log.status === 'RUNNING') {
            nodeElement.classList.add('running');
        }
    });
}