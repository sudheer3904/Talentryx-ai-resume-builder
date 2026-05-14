document.addEventListener('DOMContentLoaded', () => {
    const cfg = window.INTERVIEW_CONFIG || {};
    const total = cfg.totalQuestions || 1;

    const questionTextEl = document.getElementById('question-text');
    const answerInputEl = document.getElementById('answer-input');
    const counterEl = document.getElementById('question-counter');
    const progressEl = document.getElementById('question-progress');
    const scoreBadgeEl = document.getElementById('question-score');
    const feedbackBoxEl = document.getElementById('feedback-box');

    const btnPrev = document.getElementById('btn-prev');
    const btnNext = document.getElementById('btn-next');
    const btnSubmit = document.getElementById('btn-submit');
    const btnExit = document.getElementById('btn-exit');

    let currentIndex = 0; // 0-based
    let currentQuestion = '';
    const localAnswers = []; // {question, answer, score}

    async function fetchNextQuestion() {
        const res = await fetch(cfg.nextUrl, { method: 'POST' });
        const data = await res.json();
        if (data.status === 'continue') {
            currentQuestion = data.question;
            currentIndex = (data.index || 1) - 1;
            renderQuestion();
        } else {
            // No more questions -> finish
            await finishInterview();
        }
    }

    function renderQuestion() {
        questionTextEl.textContent = currentQuestion || 'No question.';
        counterEl.textContent = `Question ${currentIndex + 1} of ${total}`;
        const pct = Math.round(((currentIndex) / total) * 100);
        progressEl.style.width = `${pct}%`;
        progressEl.setAttribute('aria-valuenow', String(pct));

        // Restore previous answer if we have it locally
        const existing = localAnswers[currentIndex];
        answerInputEl.value = existing ? (existing.answer || '') : '';
        scoreBadgeEl.classList.add('d-none');
        feedbackBoxEl.classList.add('d-none');
        feedbackBoxEl.textContent = '';

        btnPrev.disabled = currentIndex === 0;
    }

    async function submitCurrentAnswer(moveNext = true) {
        const text = (answerInputEl.value || '').trim();
        if (!text) {
            if (moveNext) {
                // Allow skipping but warn
                feedbackBoxEl.classList.remove('d-none');
                feedbackBoxEl.classList.add('alert-warning');
                feedbackBoxEl.textContent = 'You left this answer empty. Consider adding at least a brief response.';
            }
            return;
        }

        const res = await fetch(cfg.submitUrl, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ answer: text, question: currentQuestion })
        });
        const data = await res.json();

        const score = data.score ?? null;
        localAnswers[currentIndex] = {
            question: currentQuestion,
            answer: text,
            score: score
        };

        if (score !== null && scoreBadgeEl) {
            scoreBadgeEl.textContent = `${score}%`;
            scoreBadgeEl.classList.remove('d-none');
        }
        if (data.feedback) {
            feedbackBoxEl.textContent = data.feedback;
            feedbackBoxEl.classList.remove('d-none');
            feedbackBoxEl.classList.remove('alert-warning');
            feedbackBoxEl.classList.add(score >= 60 ? 'alert-success' : 'alert-info');
        }

        if (moveNext) {
            await fetchNextQuestion();
        }
    }

    async function finishInterview() {
        const res = await fetch(cfg.finishUrl, { method: 'POST' });
        const data = await res.json();
        if (data.status === 'success') {
            window.location.href = cfg.resultUrl;
        } else {
            alert(data.message || 'Error finishing interview');
        }
    }

    btnNext.addEventListener('click', async () => {
        await submitCurrentAnswer(true);
    });

    btnSubmit.addEventListener('click', async () => {
        await submitCurrentAnswer(false);
        await finishInterview();
    });

    btnPrev.addEventListener('click', () => {
        if (currentIndex === 0) return;
        currentIndex -= 1;
        const prev = localAnswers[currentIndex];
        currentQuestion = prev ? prev.question : currentQuestion;
        renderQuestion();
    });

    btnExit.addEventListener('click', () => {
        if (confirm('End the mock interview and return to dashboard?')) {
            window.location.href = cfg.dashboardUrl;
        }
    });

    // Start
    fetchNextQuestion();
});

