async function uploadVideo() {
    const fileInput = document.getElementById('videoUpload');
    const file = fileInput.files[0];
    
    if (!file) {
        alert('Выберите файл!');
        return;
    }

    console.log(file.name)
    console.log(file.type)

    const response = await fetch('http://localhost:8000/generate-presigned-url', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            fileName: file.name,
            fileType: file.type,
        }),
    });

    if (!response.ok) {
        alert('Ошибка при получении URL для загрузки');
        return;
    }

    const data = await response.json();     // 2. Парсим JSON
    console.log("Распарсенный ответ:", data); // 3. Смотрим, что внутри

    const presignedUrl = data.presigned_url;
    console.log("URL", presignedUrl);

    const uploadResponse = await fetch(presignedUrl, {
        method: 'PUT',
        body: file,
        headers: { 'Content-Type': "video/mp4" },
    });

    if (uploadResponse.ok) {
        alert('✅ Файл успешно загружен!');
    } else {
        alert('❌ Ошибка загрузки');
    }
}