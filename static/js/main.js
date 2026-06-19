/* 深蓝信息 - 前端交互脚本 */
document.addEventListener("DOMContentLoaded", function () {
  // 3 秒后自动淡出 flash 消息
  const flashes = document.querySelectorAll(".flash");
  flashes.forEach(function (el) {
    setTimeout(function () {
      el.style.transition = "opacity .5s, transform .5s";
      el.style.opacity = "0";
      el.style.transform = "translateY(-8px)";
      setTimeout(function () { el.remove(); }, 500);
    }, 4000);
  });

  // 详情页：正文里的 URL 自动转链接
  const body = document.querySelector(".detail-body");
  if (body) {
    const urlRegex = /(https?:\/\/[^\s<]+)/g;
    body.innerHTML = body.innerHTML.replace(urlRegex, function (m) {
      return '<a href="' + m + '" target="_blank" rel="noopener">' + m + "</a>";
    });
  }

  // 表单文件选择显示文件名
  const fileInput = document.querySelector('input[type="file"]');
  if (fileInput) {
    fileInput.addEventListener("change", function () {
      if (this.files && this.files[0]) {
        this.nextElementSibling &&
          (this.nextElementSibling.textContent = "已选择：" + this.files[0].name);
      }
    });
  }
});
