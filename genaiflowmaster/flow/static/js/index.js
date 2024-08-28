// シャボン玉のアニメーション
function createBubble() {
    const bubble = document.createElement('div');
    bubble.classList.add('bubble');
    
    const size = Math.random() * 60 + 20;
    bubble.style.width = `${size}px`;
    bubble.style.height = `${size}px`;
    
    const positionX = Math.random() * 100;
    bubble.style.left = `${positionX}%`;
    
    bubble.style.animationDuration = `${Math.random() * 4 + 4}s`;
    
    document.body.appendChild(bubble);
    
    setTimeout(() => {
        bubble.remove();
    }, 8000);
}

setInterval(createBubble, 500);

// モーダル関連の処理
const modal = document.getElementById("flowModal");
const btn = document.getElementById("createFlowBtn");
const span = document.getElementsByClassName("close")[0];
const submitBtn = document.getElementById("submitFlow");

btn.onclick = function() {
    modal.style.display = "block";
}

span.onclick = function() {
    modal.style.display = "none";
}

window.onclick = function(event) {
    if (event.target == modal) {
        modal.style.display = "none";
    }
}

submitBtn.onclick = function() {
    const flowName = document.getElementById("flowName").value;
    if (flowName) {
        fetch('/create_flow/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
            },
            body: `name=${encodeURIComponent(flowName)}`
        })
        .then(response => response.json())
        .then(data => {
            if (data.id) {
                window.location.href = `/${data.uuid}/flow/`;
            } else {
                alert('フローの作成に失敗しました。もう一度お試しください。');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('エラーが発生しました。もう一度お試しください。');
        });
    } else {
        alert('フロー名を入力してください。');
    }
}

const listFlowsBtn = document.getElementById("listFlowsBtn");
const flowListModal = document.getElementById("flowListModal");
const flowList = document.getElementById("flowList");

listFlowsBtn.onclick = function() {
    flowListModal.style.display = "block";
    fetchFlows();
}

function fetchFlows() {
    fetch('/list_flows/')
        .then(response => response.json())
        .then(data => {
            flowList.innerHTML = '';
            data.flows.forEach(flow => {
                const li = document.createElement('li');
                li.className = 'flow-item';
                li.innerHTML = `
                    <span>${flow.name}</span>
                    <div class="button-group">
                        <button onclick="openFlowEditor('${flow.uuid}')" class="edit-btn">編集</button>
                        <button onclick="deleteFlow('${flow.uuid}')" class="delete-btn">削除</button>
                    </div>
                `;
                flowList.appendChild(li);
            });
        })
        .catch(error => {
            console.error('Error:', error);
            alert('フロー一覧の取得に失敗しました。');
        });
}

function openFlowEditor(flowId) {
    window.location.href = `/${flowId}/flow/`;
}

// モーダルを閉じる処理を全てのモーダルに適用
const modals = document.getElementsByClassName("modal");
const closes = document.getElementsByClassName("close");

for (let i = 0; i < closes.length; i++) {
    closes[i].onclick = function() {
        modals[i].style.display = "none";
    }
}

window.onclick = function(event) {
    for (let i = 0; i < modals.length; i++) {
        if (event.target == modals[i]) {
            modals[i].style.display = "none";
        }
    }
}


function deleteFlow(flowUuid) {
    if (confirm('本当にこのフローを削除しますか？')) {
        fetch(`/delete_flow/${flowUuid}/`, {
            method: 'DELETE',
        })
        .then(response => {
            if (response.ok) {
                fetchFlows(); // フロー一覧を再取得して表示を更新
            } else {
                throw new Error('フローの削除に失敗しました。');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert(error.message);
        });
    }
}