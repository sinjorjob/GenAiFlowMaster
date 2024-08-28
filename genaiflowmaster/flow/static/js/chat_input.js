document.addEventListener('DOMContentLoaded', function() {
    const executeButton = document.getElementById('executeButton');
    const backButton = document.getElementById('backButton');
    const chatInput = document.getElementById('chatInput');

    executeButton.addEventListener('click', function() {
        const input = chatInput.value;
        if (input.trim() === '') {
            alert('入力を入力してください。');
            return;
        }
        
        // HTMLで定義されたflowIdを使用
        const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
        
        fetch(`/execute_flow/${flowId}/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken,
            },
            body: JSON.stringify({ input: input }),
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                window.location.href = `/${data.flow_uuid}/flow_result/${data.flow_run_id}/`;
            } else {
                alert('フローの実行に失敗しました: ' + data.message);
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('フローの実行中にエラーが発生しました。');
        });
    });

    backButton.addEventListener('click', function() {
        window.history.back();
    });
});