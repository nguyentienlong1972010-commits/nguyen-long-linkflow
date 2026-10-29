from flask import Flask, render_template, request, jsonify
from urllib.parse import urlparse, urljoin
import ipaddress
import socket
import requests

app = Flask(__name__)
MAX_REDIRECTS = 10
TIMEOUT = 8
USER_AGENT = "NguyenLong-LinkFlow/1.0 (redirect diagnostics)"

def validate_public_url(url):
    """Allow only public HTTP(S) destinations; reduce SSRF risk."""
    if not isinstance(url, str) or len(url) > 2048:
        raise ValueError("Liên kết không hợp lệ hoặc quá dài.")
    parsed = urlparse(url.strip())
    if parsed.scheme not in ("http", "https") or not parsed.hostname:
        raise ValueError("Chỉ hỗ trợ liên kết bắt đầu bằng http:// hoặc https://.")
    if parsed.username or parsed.password:
        raise ValueError("Không hỗ trợ URL chứa thông tin đăng nhập.")
    host = parsed.hostname
    try:
        ip = ipaddress.ip_address(host)
        if not ip.is_global:
            raise ValueError("Địa chỉ đích không phải địa chỉ công khai.")
    except ValueError as exc:
        # If host itself is not an IP literal, resolve it and reject private/reserved IPs.
        try:
            ipaddress.ip_address(host)
        except ValueError:
            try:
                addresses = socket.getaddrinfo(host, parsed.port or (443 if parsed.scheme == "https" else 80))
            except socket.gaierror:
                raise ValueError("Không phân giải được tên miền.")
            for item in addresses:
                resolved = ipaddress.ip_address(item[4][0])
                if not resolved.is_global:
                    raise ValueError("Tên miền phân giải tới địa chỉ không công khai.")
        else:
            raise exc
    return url.strip()

@app.get("/")
def index():
    return render_template("index.html")

@app.post("/api/analyze")
def analyze():
    payload = request.get_json(silent=True) or {}
    current = (payload.get("url") or "").strip()
    if not current:
        return jsonify(error="Vui lòng nhập liên kết."), 400

    steps = []
    seen = set()
    session = requests.Session()
    session.headers.update({"User-Agent": USER_AGENT})
    try:
        for index in range(MAX_REDIRECTS + 1):
            current = validate_public_url(current)
            if current in seen:
                return jsonify(ok=False, steps=steps, error="Phát hiện vòng lặp chuyển hướng."), 200
            seen.add(current)
            try:
                response = session.get(
                    current, allow_redirects=False, timeout=TIMEOUT,
                    stream=True, headers={"Range": "bytes=0-0"}
                )
            except requests.RequestException:
                # Some sites reject HEAD/range requests; report the last checked URL.
                steps.append({"url": current, "status": "Không thể truy cập", "note": "Trang không phản hồi hoặc chặn yêu cầu tự động."})
                return jsonify(ok=False, steps=steps, final_url=None, error="Không thể kiểm tra tiếp. Trang có thể yêu cầu JavaScript, cookie hoặc thao tác người dùng."), 200

            status = response.status_code
            location = response.headers.get("Location")
            response.close()
            step = {"url": current, "status": status}
            if location and status in (301, 302, 303, 307, 308):
                next_url = urljoin(current, location)
                step["note"] = "Có chuyển hướng"
                step["next_url"] = next_url
                steps.append(step)
                current = next_url
                continue
            step["note"] = "Không còn redirect HTTP tự động"
            steps.append(step)
            return jsonify(
                ok=True, steps=steps, final_url=current,
                note="Đã kiểm tra chuyển hướng HTTP. Các bước quảng cáo, CAPTCHA hoặc JavaScript có thể cần thao tác hợp lệ trên trang."
            ), 200

        return jsonify(ok=False, steps=steps, error=f"Đã chạm giới hạn {MAX_REDIRECTS} lần chuyển hướng."), 200
    finally:
        session.close()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
