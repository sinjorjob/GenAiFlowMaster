function openFlowList() {
    const modal = document.getElementById("flowListModal");
    modal.style.display = "block";
    fetchFlows();
}

function fetchFlows() {
    fetch('/list_flows/')
        .then(response => response.json())
        .then(data => {
            const flowList = document.getElementById("flowList");
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

function openFlowEditor(flowUuid) {
    window.location.href = `/${flowUuid}/flow/`;
}

function openModelSettings() {
    document.getElementById("modelListModal").style.display = "block";
}

// フロー一覧モーダルを閉じる処理
const flowListModal = document.getElementById("flowListModal");
const flowListSpan = flowListModal.querySelector(".close");
flowListSpan.onclick = function() {
    flowListModal.style.display = "none";
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