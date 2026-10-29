const form = document.querySelector("#analyze-form");
const input = document.querySelector("#url-input");
const submitBtn = document.querySelector("#submit-btn");
const buttonLabel = document.querySelector("#button-label");
const results = document.querySelector("#results");
const loading = document.querySelector("#loading");
const stepsList = document.querySelector("#steps");
const resultTitle = document.querySelector("#result-title");
const stepCount = document.querySelector("#step-count");
const finalBox = document.querySelector("#final-box");
const finalUrl = document.querySelector("#final-url");
const resultNote = document.querySelector("#result-note");
const copyBtn = document.querySelector("#copy-btn");

function safeUrl(url) {
  try {
    const parsed = new URL(url);
    return ["http:", "https:"].includes(parsed.protocol);
  } catch { return false; }
}
function addStep(step, index) {
  const li = document.createElement("li");
  li.dataset.step = String(index + 1);
  const url = document.createElement("span");
  url.className = "step-url";
  url.textContent = step.url || "Không rõ URL";
  const meta = document.createElement("span");
  meta.className = "step-meta";
  meta.textContent = `Trạng thái: ${step.status ?? "N/A"} · ${step.note || ""}`;
  li.append(url, meta);
  if (step.next_url) {
    const next = document.createElement("span");
    next.className = "step-meta";
    next.textContent = `Tiếp theo: ${step.next_url}`;
    li.append(next);
  }
  stepsList.append(li);
}
form.addEventListener("submit", async (event) => {
  event.preventDefault();
  const url = input.value.trim();
  if (!safeUrl(url)) {
    input.setCustomValidity("Hãy nhập URL hợp lệ bắt đầu bằng http:// hoặc https://.");
    input.reportValidity();
    input.setCustomValidity("");
    return;
  }
  results.classList.remove("hidden");
  loading.classList.remove("hidden");
  stepsList.replaceChildren();
  finalBox.classList.add("hidden");
  resultNote.textContent = "";
  resultNote.classList.remove("error-note");
  resultTitle.textContent = "Đang phân tích";
  stepCount.textContent = "Đang chạy";
  submitBtn.disabled = true;
  buttonLabel.textContent = "Đang kiểm tra…";
  try {
    const response = await fetch("/api/analyze", {
      method: "POST",
      headers: {"Content-Type":"application/json"},
      body: JSON.stringify({url})
    });
    const data = await response.json();
    if (!response.ok) throw new Error(data.error || "Không thể phân tích liên kết.");
    (data.steps || []).forEach(addStep);
    resultTitle.textContent = data.ok ? "Đã kiểm tra xong" : "Chưa thể hoàn tất";
    stepCount.textContent = `${(data.steps || []).length} bước`;
    if (data.final_url) {
      finalBox.classList.remove("hidden");
      finalUrl.href = data.final_url;
      finalUrl.textContent = data.final_url;
    }
    resultNote.textContent = data.error || data.note || "";
    if (data.error) resultNote.classList.add("error-note");
  } catch (error) {
    resultTitle.textContent = "Có lỗi xảy ra";
    stepCount.textContent = "Lỗi";
    resultNote.textContent = error.message || "Không thể kết nối máy chủ.";
    resultNote.classList.add("error-note");
  } finally {
    loading.classList.add("hidden");
    submitBtn.disabled = false;
    buttonLabel.textContent = "Phân tích liên kết";
    results.scrollIntoView({behavior:"smooth", block:"start"});
  }
});
copyBtn.addEventListener("click", async () => {
  try {
    await navigator.clipboard.writeText(finalUrl.href);
    copyBtn.textContent = "Đã sao chép ✓";
    setTimeout(() => copyBtn.textContent = "Sao chép", 1600);
  } catch {
    copyBtn.textContent = "Không sao chép được";
  }
});
