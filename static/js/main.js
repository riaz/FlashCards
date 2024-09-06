document.addEventListener('DOMContentLoaded', function() {
    const uploadForm = document.getElementById('upload-form');
    const uploadStatus = document.getElementById('upload-status');
    const flashcardsContainer = document.getElementById('flashcards-container');

    if (uploadForm) {
        uploadForm.addEventListener('submit', function(e) {
            e.preventDefault();
            const formData = new FormData(uploadForm);
            
            fetch('/upload', {
                method: 'POST',
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                uploadStatus.textContent = data.message;
                setTimeout(() => {
                    window.location.href = '/flashcards';
                }, 2000);
            })
            .catch(error => {
                console.error('Error:', error);
                uploadStatus.textContent = 'An error occurred while uploading the file.';
            });
        });
    }

    if (flashcardsContainer) {
        flashcardsContainer.addEventListener('click', function(e) {
            if (e.target.classList.contains('like-btn')) {
                const id = e.target.dataset.id;
                fetch(`/flashcard/${id}/like`, { method: 'POST' })
                    .then(response => response.json())
                    .then(data => {
                        e.target.textContent = `Like (${data.likes})`;
                    });
            } else if (e.target.classList.contains('dislike-btn')) {
                const id = e.target.dataset.id;
                fetch(`/flashcard/${id}/dislike`, { method: 'POST' })
                    .then(response => response.json())
                    .then(data => {
                        e.target.textContent = `Dislike (${data.dislikes})`;
                    });
            } else if (e.target.classList.contains('delete-btn')) {
                const id = e.target.dataset.id;
                fetch(`/flashcard/${id}`, { method: 'DELETE' })
                    .then(response => response.json())
                    .then(data => {
                        const flashcardElement = e.target.closest('.flashcard');
                        flashcardElement.remove();
                    });
            }
        });
    }
});
