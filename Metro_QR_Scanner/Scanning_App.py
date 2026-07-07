"""
File này CHẠY TRÊN LAPTOP, đặt trong folder Metro_QR_Scanner (ngang hàng với App/, UI/).
Điện thoại chỉ mở trình duyệt vào link ngrok để XEM giao diện quét QR.

Cách chạy:
    pip install flask
    python Scanning_App.py
"""

import os
import sys
import json
from datetime import datetime
from flask import Flask, render_template_string, request, jsonify

# SỬA: thêm thư mục gốc project (E:\HK3\Metro) vào sys.path để import được
# App.DB_Connection - vì file này nằm trong Metro_QR_Scanner/, thấp hơn 1 cấp
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from App.DB_Connection import get_connection

app = Flask(__name__)

# ============================================================
# LOGIC NGHIỆP VỤ THẬT - nối DB, xử lý IN/OUT, đổi status vé
# ============================================================
def handle_scan(conn, qr_code, station_id):
    cursor = conn.cursor()
    cursor.execute("""
        SELECT t.ticket_id, t.type_id, t.status, t.from_station_id, t.to_station_id, t.issued_at,
               tt.type_name, tt.validity_days,
               sf.station_name AS from_name, st.station_name AS to_name
        FROM TICKET t
        JOIN TICKET_TYPE tt ON t.type_id = tt.type_id
        LEFT JOIN STATION sf ON t.from_station_id = sf.station_id
        LEFT JOIN STATION st ON t.to_station_id = st.station_id
        WHERE t.qr_code = ?
    """, qr_code)
    row = cursor.fetchone()

    if not row:
        return {"ok": False, "message": "Vé không tồn tại trong hệ thống"}

    (ticket_id, type_id, status, from_id, to_id, issued_at,
     type_name, validity_days, from_name, to_name) = row

    print(f"[DEBUG] ticket_id={ticket_id}, type_id={type_id}, status HIỆN TẠI TRONG DB={status}")

    # --- Check hết hạn cho vé ngày/tháng (vé lượt validity_days = NULL, bỏ qua) ---
    if type_id != 1 and validity_days:
        cursor.execute("SELECT DATEDIFF(day, ?, GETDATE())", issued_at)
        days_passed = cursor.fetchone()[0]
        if days_passed > validity_days:
            if status != 'EXPIRED':
                cursor.execute("UPDATE TICKET SET status='EXPIRED' WHERE ticket_id=?", ticket_id)
                conn.commit()
            return {"ok": False, "message": "Vé đã hết hạn sử dụng"}

    if status == 'EXPIRED':
        return {"ok": False, "message": "Vé đã hết hạn sử dụng"}
    if status == 'CANCELLED':
        return {"ok": False, "message": "Vé đã bị hủy / hoàn tiền"}

    # --- Tự động xác định đây là lượt quét IN hay OUT dựa vào lịch sử trong ngày ---
    cursor.execute("""
        SELECT TOP 1 scan_type, scanned_at FROM SCANNING_HISTORY
        WHERE ticket_id = ? AND CAST(scanned_at AS DATE) = CAST(GETDATE() AS DATE)
        ORDER BY scanned_at DESC
    """, ticket_id)
    last_scan = cursor.fetchone()
    print(f"[DEBUG] Lần quét gần nhất hôm nay cho ticket_id={ticket_id}: {last_scan}")

    scan_type = "OUT" if last_scan and last_scan[0] == "IN" else "IN"
    print(f"[DEBUG] -> Xác định scan_type = {scan_type}")

    # --- Vé lượt (type_id=1): IN chuyển USED ngay, OUT chỉ log ---
    if type_id == 1:
        if scan_type == "IN":
            if status != 'UNUSED':
                print(f"[DEBUG] BỊ CHẶN: status hiện tại là '{status}', không phải UNUSED nên không cho quét IN")
                return {"ok": False, "message": "Vé đã được sử dụng, không thể quét IN lần nữa"}
            cursor.execute("UPDATE TICKET SET status='USED' WHERE ticket_id=?", ticket_id)
            rows_affected = cursor.rowcount
            print(f"[DEBUG] Đã UPDATE status='USED', số dòng bị ảnh hưởng: {rows_affected}")
        else:  # OUT
            if status != 'USED':
                return {"ok": False, "message": "Vé chưa được quét IN hợp lệ, không thể quét OUT"}
            # Không đổi status nữa, chỉ ghi log quét ra

    # --- Vé ngày/tháng: dùng được nhiều lần, chỉ cần còn hiệu lực là cho qua ---
    else:
        if status not in ('UNUSED', 'USED'):
            return {"ok": False, "message": "Vé không hợp lệ"}

    # --- Ghi log vào SCANNING_HISTORY ---
    cursor.execute("""
        INSERT INTO SCANNING_HISTORY (scan_id, ticket_id, station_id, scan_type, scanned_at)
        VALUES ((SELECT ISNULL(MAX(scan_id),0)+1 FROM SCANNING_HISTORY), ?, ?, ?, ?)
    """, ticket_id, station_id, scan_type, datetime.now())
    print(f"[DEBUG] Đã INSERT SCANNING_HISTORY: ticket_id={ticket_id}, scan_type={scan_type}")
    conn.commit()
    print(f"[DEBUG] Đã commit() xong")

    return {
        "ok": True,
        "scan_type": scan_type,
        "ticket": {
            "qr_code": qr_code,
            "type_name": type_name,
            "from_station": from_name,
            "to_station": to_name,
        }
    }


# ============================================================
# TRANG GIAO DIỆN QUÉT QR
# ============================================================
SCAN_PAGE = """
<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Quét vé Metro</title>
    <script src="https://unpkg.com/jsqr@1.4.0/dist/jsQR.js"></script>
    <style>
        * { box-sizing: border-box; }
        body {
            font-family: -apple-system, "Segoe UI", sans-serif;
            background: #0F172A; color: white; margin: 0; padding: 20px; text-align: center;
        }
        h2 { margin-bottom: 20px; font-size: 18px; }
        #video-container {
            position: relative; width: 100%; max-width: 400px; margin: 0 auto;
            border-radius: 16px; overflow: hidden;
        }
        video { width: 100%; display: block; }
        #status {
            margin-top: 16px; padding: 14px; border-radius: 12px;
            font-weight: 600; font-size: 14px; min-height: 20px;
        }
        .waiting { background: #334155; }
        .error   { background: #DC2626; }
        #result-card {
            display: none; max-width: 400px; margin: 16px auto 0;
            background: white; border-radius: 18px; overflow: hidden; text-align: left;
            box-shadow: 0 12px 30px rgba(0,0,0,0.35);
            animation: slideUp 0.3s ease-out;
        }
        @keyframes slideUp { from { opacity:0; transform:translateY(16px);} to {opacity:1; transform:translateY(0);} }
        .card-header { padding: 18px 20px 14px; display: flex; align-items: center; gap: 10px; }
        .card-header.ok  { background: linear-gradient(90deg, #16A34A, #22C55E); }
        .card-header.bad { background: linear-gradient(90deg, #DC2626, #EF4444); }
        .card-icon {
            width: 32px; height: 32px; border-radius: 50%; background: rgba(255,255,255,0.25);
            display: flex; align-items: center; justify-content: center; font-size: 18px; flex-shrink: 0;
        }
        .card-title { color: white; font-weight: 700; font-size: 16px; }
        .card-body { padding: 16px 20px 20px; color: #0F172A; }
        .card-row {
            display: flex; justify-content: space-between; align-items: flex-start;
            padding: 8px 0; border-bottom: 1px solid #F1F5F9; font-size: 13px; gap: 12px;
        }
        .card-row:last-child { border-bottom: none; }
        .card-row .label { color: #64748B; flex-shrink: 0; }
        .card-row .value { font-weight: 700; text-align: right; }
        .card-error-msg { color: #DC2626; font-size: 13px; font-weight: 600; }
        .btn-continue {
            display: block; width: 100%; margin-top: 14px; padding: 12px;
            border: none; border-radius: 10px; background: #0F172A; color: white;
            font-weight: 700; font-size: 14px; cursor: pointer;
        }
    </style>
</head>
<body>
    <h2>🎫 Quét vé Metro - Ga Bến Thành</h2>
    <div id="video-container">
        <video id="video" playsinline autoplay muted></video>
    </div>
    <div id="status" class="waiting">Đang mở camera...</div>

    <div id="result-card">
        <div id="card-header" class="card-header ok">
            <div class="card-icon" id="card-icon">✓</div>
            <div class="card-title" id="card-title">Quét thành công</div>
        </div>
        <div class="card-body" id="card-body"></div>
        <div class="card-body" style="padding-top:0;">
            <button class="btn-continue" onclick="continueScan()">Quét vé tiếp theo</button>
        </div>
    </div>

    <canvas id="canvas" style="display:none;"></canvas>

    <script>
        const video = document.getElementById('video');
        const videoContainer = document.getElementById('video-container');
        const canvas = document.getElementById('canvas');
        const ctx = canvas.getContext('2d');
        const statusDiv = document.getElementById('status');
        const resultCard = document.getElementById('result-card');
        const cardHeader = document.getElementById('card-header');
        const cardIcon = document.getElementById('card-icon');
        const cardTitle = document.getElementById('card-title');
        const cardBody = document.getElementById('card-body');

        let currentStream = null; // SỬA: lưu lại stream để tắt/mở camera theo ý muốn

        window.onerror = function(msg, url, line) {
            statusDiv.textContent = "LỖI: " + msg + " (dòng " + line + ")";
            statusDiv.className = "error";
        };

        let scanning = true;

        function startCamera() {
            navigator.mediaDevices.getUserMedia({ video: { facingMode: "environment" } })
                .then(function(stream) {
                    currentStream = stream;
                    video.srcObject = stream;
                    statusDiv.textContent = "Camera đã mở, đưa QR vào khung hình";
                    statusDiv.className = "waiting";
                    requestAnimationFrame(tick);
                })
                .catch(function(err) {
                    statusDiv.textContent = "Không mở được camera: " + err;
                    statusDiv.className = "error";
                });
        }

        function stopCamera() {
            // SỬA: tắt hẳn camera, giải phóng phần cứng thay vì chỉ ẩn video
            if (currentStream) {
                currentStream.getTracks().forEach(track => track.stop());
                currentStream = null;
            }
        }

        startCamera(); // mở camera ngay khi vào trang

        function tick() {
            if (!currentStream) return; // SỬA: camera đã tắt thì dừng vòng lặp luôn
            try {
                if (video.readyState === video.HAVE_ENOUGH_DATA && scanning) {
                    canvas.height = video.videoHeight;
                    canvas.width = video.videoWidth;
                    ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
                    const imageData = ctx.getImageData(0, 0, canvas.width, canvas.height);

                    if (typeof jsQR === "undefined") {
                        statusDiv.textContent = "LỖI: Thư viện jsQR chưa load được";
                        statusDiv.className = "error";
                        return;
                    }

                    const code = jsQR(imageData.data, imageData.width, imageData.height);
                    if (code) {
                        scanning = false;
                        handleScan(code.data);
                    }
                }
            } catch (e) {
                statusDiv.textContent = "LỖI trong tick(): " + e.message;
                statusDiv.className = "error";
            }
            requestAnimationFrame(tick);
        }

        function handleScan(qrText) {
            statusDiv.textContent = "Đang xử lý...";
            statusDiv.className = "waiting";

            fetch("/api/scan", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ qr_code: qrText, station_id: 1 })
            })
            .then(res => res.json())
            .then(data => renderResultCard(data))
            .catch(err => {
                renderResultCard({ ok: false, message: "Lỗi kết nối server: " + err });
            });
        }

        function renderResultCard(data) {
            statusDiv.textContent = "";
            resultCard.style.display = "block";
            videoContainer.style.display = "none"; // SỬA: ẩn khung camera đi
            stopCamera(); // SỬA: tắt hẳn camera để đỡ hao pin

            if (data.ok) {
                cardHeader.className = "card-header ok";
                cardIcon.textContent = "✓";
                cardTitle.textContent = data.scan_type === "OUT" ? "Quét ra thành công" : "Quét vào thành công";

                const t = data.ticket || {};
                cardBody.innerHTML = `
                    <div class="card-row"><span class="label">Loại vé</span><span class="value">${t.type_name || "-"}</span></div>
                    <div class="card-row"><span class="label">Hành trình</span><span class="value">${t.from_station || "-"} → ${t.to_station || "-"}</span></div>
                    <div class="card-row"><span class="label">Mã vé</span><span class="value">${t.qr_code || "-"}</span></div>
                    <div class="card-row"><span class="label">Lượt quét</span><span class="value">${data.scan_type || "-"}</span></div>
                `;
            } else {
                cardHeader.className = "card-header bad";
                cardIcon.textContent = "✕";
                cardTitle.textContent = "Quét không hợp lệ";
                cardBody.innerHTML = `<div class="card-error-msg">${data.message}</div>`;
            }
        }

        function continueScan() {
            resultCard.style.display = "none";
            videoContainer.style.display = "block"; // SỬA: hiện lại khung camera
            statusDiv.textContent = "Đưa QR vào khung hình";
            statusDiv.className = "waiting";
            scanning = true;
            startCamera(); // SỬA: mở lại camera vừa tắt lúc nãy
        }
    </script>
</body>
</html>
"""


@app.route("/")
def scan_page():
    return render_template_string(SCAN_PAGE)


@app.route("/api/scan", methods=["POST"])
def api_scan():
    data = request.get_json()
    raw_qr = data.get("qr_code")
    station_id = data.get("station_id")

    print(f"[DEBUG] Chuỗi QR nhận được: '{raw_qr}'")

    # QR trên vé chứa cả object JSON (ticket_id, qr_code, tên ga, giá...)
    try:
        ticket_json = json.loads(raw_qr)
        qr_code = ticket_json.get("qr_code")
    except (json.JSONDecodeError, TypeError):
        qr_code = raw_qr

    if not qr_code:
        return jsonify({"ok": False, "message": "Không đọc được mã QR"})

    try:
        conn = get_connection()
        result = handle_scan(conn, qr_code, station_id)
        conn.close()
        return jsonify(result)
    except Exception as e:
        print(f"[ERROR] {e}")
        return jsonify({"ok": False, "message": f"Lỗi hệ thống: {e}"})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)