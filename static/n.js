const API_URL =  "http://127.0.0.1:5000/process_image/"

document.getElementById('capture').addEventListener('click', async () => {
    const video = document.getElementById('video');
    const canvas = document.createElement('canvas');
    const ctx = canvas.getContext('2d');

    if (!video.videoWidth || !video.videoHeight) {
        alert("Камера еще не загрузилась. Попробуйте снова.");
        return;
    }

    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    ctx.drawImage(video, 0, 0, canvas.width, canvas.height);

    const imageData = canvas.toDataURL('image/png');

    try {
        const response = await fetch(API_URL, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ image: imageData })
        });

        const resultDiv = document.getElementById('result');
        const status = document.getElementById('status');

        if (!response.ok) {
            throw new Error(`Ошибка сервера: ${response.status}`);
        }

        const data = await response.json();

        resultDiv.textContent = `Русский: ${data.russian.join(" ")}\nАнглийский: ${data.english.join(" ")}`;
        status.textContent = "Распознавание завершено";
    } catch (error) {
        console.error("Ошибка:", error);
        document.getElementById('status').textContent = "Произошла ошибка.";
    }
});
