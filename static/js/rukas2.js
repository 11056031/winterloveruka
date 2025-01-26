// 從 sessionStorage 中獲取圖片數據
const storedImage = sessionStorage.getItem("uploadedImage");
if (storedImage) {
    const preview = document.getElementById("imagePreview");
    preview.src = storedImage;
    preview.style.display = "block";
} else {
    alert("未找到圖片，請返回上一步重新上傳！");
    window.location.href = "/rukapic/step1";
}
