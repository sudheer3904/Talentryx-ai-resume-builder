document.addEventListener('DOMContentLoaded', () => {
    const feedbackBtn = document.getElementById('feedback-btn');
    const feedbackOverlay = document.getElementById('feedback-overlay');
    const feedbackClose = document.getElementById('feedback-close');
    const feedbackForm = document.getElementById('feedback-form');
    const submitBtn = document.getElementById('feedback-submit-btn');
    const successView = document.getElementById('feedback-success');
    const formView = document.getElementById('feedback-form-view');
    
    // Open Modal
    const openFeedback = () => {
        feedbackOverlay.classList.add('active');
        document.body.style.overflow = 'hidden'; // Prevent scrolling
    };
    
    // Close Modal
    const closeFeedback = () => {
        feedbackOverlay.classList.remove('active');
        document.body.style.overflow = '';
        
        // Reset form after closing animation
        setTimeout(() => {
            feedbackForm.reset();
            formView.style.display = 'block';
            successView.classList.remove('active');
            submitBtn.classList.remove('loading');
        }, 300);
    };

    if (feedbackBtn) {
        feedbackBtn.addEventListener('click', openFeedback);
    }
    
    if (feedbackClose) {
        feedbackClose.addEventListener('click', closeFeedback);
    }
    
    if (feedbackOverlay) {
        feedbackOverlay.addEventListener('click', (e) => {
            if (e.target === feedbackOverlay) {
                closeFeedback();
            }
        });
    }

    // Submit Form
    if (feedbackForm) {
        feedbackForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            
            // Get data
            const formData = new FormData(feedbackForm);
            const data = {
                rating: parseInt(formData.get('rating') || 0),
                category: formData.get('category'),
                message: formData.get('message'),
                email: formData.get('email') || ''
            };
            
            // Validation
            if (!data.rating || !data.category || !data.message) {
                alert('Please provide a rating, category, and message.');
                return;
            }
            
            // Start Loading
            submitBtn.classList.add('loading');
            
            try {
                const response = await fetch('/api/ai/feedback', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(data)
                });
                
                if (response.ok) {
                    // Show success animation
                    formView.style.display = 'none';
                    successView.classList.add('active');
                    
                    // Auto-close after 1.5s
                    setTimeout(closeFeedback, 1500);
                } else {
                    alert('Failed to submit feedback. Please try again.');
                    submitBtn.classList.remove('loading');
                }
            } catch (error) {
                console.error('Feedback Error:', error);
                alert('An error occurred. Please try again.');
                submitBtn.classList.remove('loading');
            }
        });
    }
    
    // Smart Touch: expose function globally for downloads or triggers
    window.TalentryxFeedback = {
        open: openFeedback,
        promptAfterAction: (delay = 2000) => {
            setTimeout(openFeedback, delay);
        }
    };
});
