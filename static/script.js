const recordBtn = document.getElementById('recordBtn');
const newSentenceBtn = document.getElementById('newSentenceBtn');
let sentence = document.querySelector('.text-primary').textContent;
let mediaRecorder;

navigator.mediaDevices.getUserMedia({ audio: true })
    .then(stream => {
        mediaRecorder = new MediaRecorder(stream);
        let chunks = [];
        mediaRecorder.ondataavailable = e => chunks.push(e.data);
        mediaRecorder.onstop = () => {
            const blob = new Blob(chunks, { type: 'audio/wav' });
            const formData = new FormData();
            formData.append('audio', blob, 'user_audio.wav');
            formData.append('target_text', sentence);
            fetch('/analyze', {
                method: 'POST',
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                document.getElementById('spoken_text').textContent = data.spoken_text;
                document.getElementById('score').textContent = `${data.score}%`;
                document.getElementById('feedback').textContent = data.feedback;
                document.getElementById('target_ipa').textContent = data.target_ipa;
                document.getElementById('user_ipa').textContent = data.user_ipa;
                document.getElementById('nativeAudio').src = data.audio;
                document.getElementById('result').classList.add('show');
            })
            .catch(err => console.error('Error:', err));
            chunks = [];
        };
    });

recordBtn.onclick = () => {
    mediaRecorder.start();
    recordBtn.textContent = 'Recording...';
    recordBtn.classList.replace('btn-success', 'btn-danger');
    setTimeout(() => {
        mediaRecorder.stop();
        recordBtn.textContent = 'Record';
        recordBtn.classList.replace('btn-danger', 'btn-success');
    }, 5000);  // 5-second recording
};

newSentenceBtn.onclick = () => location.reload();