document.addEventListener("DOMContentLoaded", () => {
  const form = document.getElementById("upload-form");
  const fileInput = document.getElementById("pdf-file");
  const downloadLink = document.getElementById("download-link");
  const downloadSection = document.getElementById("download-section");

  form.addEventListener("submit", function (e) {
    e.preventDefault();

    const file = fileInput.files[0];
    if (!file) {
      alert("PDF 파일을 선택해주세요.");
      return;
    }

    const formData = new FormData();
    formData.append("pdf", file);

    fetch("/convert", {
      method: "POST",
      body: formData,
    })
      .then((res) => res.json())
      .then((data) => {
        if (data.download_url) {
          downloadLink.href = data.download_url;
          downloadLink.setAttribute("download", "");
          downloadSection.style.display = "block";
        } else {
          alert("변환된 파일이 없습니다.");
        }
      })
      .catch((err) => {
        console.error(err);
        alert("변환 중 오류가 발생했습니다.");
      });
  });
});
