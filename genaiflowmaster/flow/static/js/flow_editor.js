let editor;
let selectedNodeId = null;

document.addEventListener('DOMContentLoaded', function () {
    const id = document.getElementById("drawflow");
    editor = new Drawflow(id);
    
    editor.on('connectionCreated', function(connection) {
        const { input_id, input_class } = connection;
        const node = editor.getNodeFromId(input_id);
        const inputConnections = node.inputs[input_class].connections;
        
        if (inputConnections.length > 1) {
            const oldConnection = inputConnections[0];
            editor.removeSingleConnection(oldConnection.node, input_id, oldConnection.input, input_class);
            console.log('古い接続を削除しました');
        }
    });

    editor.start();
    editor.zoom_out();
    editor.zoom_out();
    editor.zoom_out();
    editor.zoom_out();

    editor.on('nodeCreated', function (nodeId) {
        addEditButton(nodeId);
        addAnimationToEdges();
    });
    editor.on('nodeSelected', function (nodeId) {
        selectedNodeId = nodeId;
    });

    editor.on('nodeUnselected', function () {
        selectedNodeId = null;
    });

    editor.on('nodeDataChanged', function (nodeId) {
        addEditButton(nodeId);
    });

    editor.on('connectionCreated', function (connection) {
        addAnimationToEdges();
    });

    loadFlowData();

    // ノード編集モーダルの設定
    const modal = document.getElementById("nodeEditModal");
    const span = modal.querySelector(".close");
    span.onclick = function () {
        modal.style.display = "none";
    }
    window.onclick = function (event) {
        if (event.target == modal) {
            modal.style.display = "none";
        }
    }

    // イベントリスナーを追加
    document.getElementById("temperatureSlider").addEventListener("input", function () {
        document.getElementById("temperatureValue").value = this.value;
    });

    document.getElementById("temperatureValue").addEventListener("change", function () {
        document.getElementById("temperatureSlider").value = this.value;
    });
    // ノード編集フォームの送信ハンドラ
    document.getElementById("nodeEditForm").onsubmit = function (e) {
        e.preventDefault();
        const nodeId = document.getElementById("nodeId").value;
        const nodeName = document.getElementById("nodeName").value;
        const systemPrompt = document.getElementById("systemPrompt").value;
        const instruction = document.getElementById("instruction").value;
        const sequence = document.getElementById("sequence").value;
        const aiModelId = document.getElementById("aiModel").value;
        const temperature = document.getElementById("temperatureValue").value;
        const nodeData = editor.getNodeFromId(nodeId).data;
        nodeData.name = nodeName;
        nodeData.system_prompt = systemPrompt;
        nodeData.instruction = instruction;
        nodeData.sequence = sequence;
        nodeData.ai_model_id = aiModelId;
        nodeData.temperature = temperature;
        console.log("Saving node data:", nodeData);

        editor.updateNodeDataFromId(nodeId, nodeData);
        updateNodeDisplay(nodeId, nodeData);
        document.getElementById("nodeEditModal").style.display = "none";
    }

    // 指示内容フィールドのイベントリスナーを追加
    const instructionTextArea = document.getElementById("instruction");
    const instructionOverlay = document.getElementById("instruction-overlay");

    instructionTextArea.addEventListener('input', function (e) {
        updateOverlay();
    });

    instructionTextArea.addEventListener('scroll', function (e) {
        syncScroll();
    });

    window.addEventListener('resize', updateOverlay);

    // エッジにアニメーションと矢印を追加
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

function addNode() {
    const nodeName = 'New Node';
    const posX = Math.random() * 600;
    const posY = Math.random() * 400;
    const nodeId = editor.addNode('node', 1, 1, posX, posY, 'node', {
        name: nodeName,
        temperature: 0.5
    }, `
        <div class="sequence-number"></div>
        <div class="title-box">${nodeName}</div>
    `);

    addEditButton(nodeId);
    updateNodeDisplay(nodeId, { name: nodeName });
    addSequenceNumber(nodeId, '');
}

function deleteSelectedNode() {
    if (selectedNodeId !== null) {
        editor.removeNodeId('node-' + selectedNodeId);
        selectedNodeId = null;
    } else {
        alert('ノードが選択されていません');
    }
}

function addEditButton(nodeId) {
    setTimeout(() => {
        const nodeElement = document.getElementById(`node-${nodeId}`);
        if (nodeElement && !nodeElement.querySelector('.edit-button')) {
            const editButton = document.createElement('button');
            editButton.innerHTML = '<i class="material-icons">edit</i>';
            editButton.className = 'edit-button';
            editButton.onclick = function (e) {
                e.stopPropagation();
                openNodeEditModal(nodeId);
            };
            nodeElement.appendChild(editButton);
        }
    }, 0);
}

function openNodeEditModal(nodeId) {
    const node = editor.getNodeFromId(nodeId);
    document.getElementById("nodeId").value = node.data.df_id || nodeId;
    document.getElementById("nodeName").value = node.data.name || '';
    document.getElementById("systemPrompt").value = node.data.system_prompt || '';
    document.getElementById("instruction").value = node.data.instruction || '';
    updateOverlay();
    document.getElementById("sequence").value = node.data.sequence || '';

    const temperatureValue = node.data.temperature !== undefined ? node.data.temperature : 0.5;
    document.getElementById("temperatureSlider").value = temperatureValue;
    document.getElementById("temperatureValue").value = temperatureValue;

    console.log("Set temperature values:", {
        slider: document.getElementById("temperatureSlider").value,
        input: document.getElementById("temperatureValue").value
    });

    axios.get('/get_ai_models/')
        .then(response => {
            const modelSelect = document.getElementById("aiModel");
            modelSelect.innerHTML = '<option value="">選択してください</option>';
            response.data.models.forEach(model => {
                const option = document.createElement('option');
                option.value = model.id;
                option.textContent = `${model.model_type} - ${model.name}`;
                if (node.data.ai_model_id == model.id) {
                    option.selected = true;
                }
                modelSelect.appendChild(option);
            });
        })
        .catch(error => {
            console.error('Error fetching AI models:', error);
        });

    document.getElementById("nodeEditModal").style.display = "block";

    document.getElementById("temperatureValue").value = node.data.temperature;

    updateTemperatureControl();
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

function updateNodeDisplay(nodeId, nodeData) {
    const nodeElement = document.getElementById(`node-${nodeId}`);
    if (nodeElement) {
        const titleElement = nodeElement.querySelector('.title-box');
        if (titleElement) {
            titleElement.textContent = nodeData.name || 'Untitled Node';
        }

        addSequenceNumber(nodeId, nodeData.sequence);
    }
}

function saveFlow() {
    const data = editor.export();
    Object.values(data.drawflow.Home.data).forEach(node => {
        if (!node.data.name) {
            node.data.name = node.name;
        }
        if (node.data.temperature !== undefined) {
            node.data.temperature = parseFloat(node.data.temperature);
        } else {
            node.data.temperature = 0.5;
        }
    });
    console.log('Saving flow data:', data);

   // 先行ノードがないノードの数をチェック
   const nodesWithoutInputs = countNodesWithoutInputs(data);
   
   if (nodesWithoutInputs > 1) {
       alert('先行ノードが定義されてないノードが２つ以上あります。\n先行ノードがないノードは１つのみ定義可能です。');
       return; // 保存を中止
   }

    axios.post(`/save_flow/${flowId}/`, data)
        .then(response => {
            if (response.data.status === 'success') {
                alert('フローが保存されました');

                updateNodesWithLatestData(response.data.nodes);            
            } else {
                throw new Error('保存に失敗しました');
            }
        })
        .catch(error => {
            console.error('Error saving flow:', error);
            alert('フローの保存中にエラーが発生しました');
        });
}

function loadFlowData() {
    axios.get(`/get_flow_data/${flowId}/`)
        .then(response => {
            const data = response.data;
            if (data.drawflow && data.drawflow.Home && data.drawflow.Home.data) {
                editor.import(data);
                Object.entries(editor.drawflow.drawflow.Home.data).forEach(([nodeId, node]) => {
                    updateNodeDisplay(nodeId, node.data);
                    addEditButton(nodeId);
                });
            } else {
                console.log('No flow data available');
            }
        })
        .catch(error => {
            console.error('Error loading flow data:', error);
        });
}

function executeFlow() {
    window.location.href = `/${flowId}/chat_input/`;
}

function showRunHistory() {
    window.location.href = `/${flowId}/flow_run_history/`;
}

function formatInstruction(text) {
    return text.replace(/\{\{input\}\}/g, function (match) {
        return '<span class="pill-batch">' + match + '</span>';
    });
}

function updateOverlay() {
    const instructionTextArea = document.getElementById("instruction");
    const instructionOverlay = document.getElementById("instruction-overlay");
    const text = instructionTextArea.value;
    const formattedText = formatInstruction(text);
    instructionOverlay.innerHTML = formattedText;
    syncScroll();
}

function syncScroll() {
    const instructionTextArea = document.getElementById("instruction");
    const instructionOverlay = document.getElementById("instruction-overlay");
    instructionOverlay.scrollTop = instructionTextArea.scrollTop;
    instructionOverlay.scrollLeft = instructionTextArea.scrollLeft;
}

function getCSRFToken() {
    const cookieValue = document.cookie
        .split('; ')
        .find(row => row.startsWith('csrftoken='))
        ?.split('=')[1];
    return cookieValue;
}

function updateTemperatureControl() {
    const slider = document.getElementById("temperatureSlider");
    const valueInput = document.getElementById("temperatureValue");

    console.log("Temperature control updated:", {
        sliderValue: slider.value,
        inputValue: valueInput.value
    });
}

function updateNodesWithLatestData(nodes) {
    nodes.forEach(nodeData => {
        const nodeId = nodeData.df_id;
        editor.updateNodeDataFromId(nodeId, nodeData);
        updateNodeDisplay(nodeId, nodeData);
    });
}

function countNodesWithoutInputs(data) {
    let count = 0;
    Object.values(data.drawflow.Home.data).forEach(node => {
        if (node.inputs && node.inputs.input_1 && node.inputs.input_1.connections.length === 0) {
            count++;
        }
    });
    return count;
}