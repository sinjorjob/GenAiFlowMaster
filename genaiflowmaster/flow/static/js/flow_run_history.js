document.addEventListener('DOMContentLoaded', function() {
    const deleteButtons = document.querySelectorAll('.delete-button');
    deleteButtons.forEach(button => {
        button.addEventListener('click', function() {
            const runId = this.getAttribute('data-run-id');
            deleteRun(runId);
        });
    });
});

function deleteRun(runId) {
    if (confirm('この実行履歴を削除してもよろしいですか？')) {
        fetch(`/delete_flow_run/${runId}/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': csrfToken,
            },
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                const elementToRemove = document.getElementById(`run-${runId}`);
                if (elementToRemove) {
                    elementToRemove.remove();
                } else {
                    console.warn(`Element with id run-${runId} not found`);
                }
                alert('実行履歴が正常に削除されました。');
            } else {
                throw new Error(data.message || '削除に失敗しました。');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('エラーが発生しました: ' + error.message);
        });
    }
}