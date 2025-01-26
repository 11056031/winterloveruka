document.getElementById("imageInput").addEventListener("change", function(event) {
    const preview = document.getElementById("imagePreview");
    const file = event.target.files[0];

    if (file) {
        const reader = new FileReader();

        reader.onload = function(e) {
            const imageData = e.target.result; // Base64圖片資料
            preview.src = imageData;
            preview.style.display = "block";

            // 將圖片數據存儲到 sessionStorage
            sessionStorage.setItem("uploadedImage", imageData);
        };

        reader.readAsDataURL(file);
    } else {
        preview.src = "";
        preview.style.display = "none";

        // 清除圖片數據
        sessionStorage.removeItem("uploadedImage");
    }
});

// 防止未選擇圖片時跳轉
document.getElementById("nextStep").addEventListener("click", function(event) {
    const storedImage = sessionStorage.getItem("uploadedImage");
    if (!storedImage) {
        alert("請先上傳圖片再進行下一步！");
        event.preventDefault(); // 阻止跳轉
    }
});
