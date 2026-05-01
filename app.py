from flask import Flask, request, jsonify
from telethon import TelegramClient, functions
from telethon.sessions import StringSession
from telethon.tl.types import InputReportReasonSpam, InputReportReasonViolence, InputReportReasonPornography, InputReportReasonChildAbuse, InputReportReasonCopyright, InputReportReasonFake
import asyncio
import os
import random
import socks

app = Flask(__name__)

# ============================================
# CONFIGURATION
# ============================================
API_ID = int(os.environ.get('API_ID', '36879151'))
API_HASH = os.environ.get('API_HASH', '45360a236343352099ffa29570f48700')
SESSION_STRING = os.environ.get('SESSION_STRING', '')

# ============================================
# PROXY LIST
# ============================================
PROXY_LIST = [
    {"ip": "31.59.20.176", "port": 6754, "user": "uvvdpmaz", "pass": "bgjzombtih9j", "country": "UK"},
    {"ip": "198.23.239.134", "port": 6540, "user": "uvvdpmaz", "pass": "bgjzombtih9j", "country": "US"},
    {"ip": "45.38.107.97", "port": 6014, "user": "uvvdpmaz", "pass": "bgjzombtih9j", "country": "UK"},
    {"ip": "107.172.163.27", "port": 6543, "user": "uvvdpmaz", "pass": "bgjzombtih9j", "country": "US"},
    {"ip": "198.105.121.200", "port": 6462, "user": "uvvdpmaz", "pass": "bgjzombtih9j", "country": "UK"},
    {"ip": "216.10.27.159", "port": 6837, "user": "uvvdpmaz", "pass": "bgjzombtih9j", "country": "US"},
    {"ip": "142.111.67.146", "port": 5611, "user": "uvvdpmaz", "pass": "bgjzombtih9j", "country": "Japan"},
    {"ip": "191.96.254.138", "port": 6185, "user": "uvvdpmaz", "pass": "bgjzombtih9j", "country": "US"},
    {"ip": "31.58.9.4", "port": 6077, "user": "uvvdpmaz", "pass": "bgjzombtih9j", "country": "Germany"},
    {"ip": "104.239.107.47", "port": 5699, "user": "uvvdpmaz", "pass": "bgjzombtih9j", "country": "US"},
]

REPORT_REASONS = {
    "spam": InputReportReasonSpam(),
    "violence": InputReportReasonViolence(),
    "pornography": InputReportReasonPornography(),
    "child_abuse": InputReportReasonChildAbuse(),
    "copyright": InputReportReasonCopyright(),
    "fake": InputReportReasonFake()
}

# ============================================
# ROUTES
# ============================================
@app.route('/')
def home():
    return """
    <h1 style='color:#ff0000;background:#000;text-align:center;padding:50px;'>
    🚨 BRONX ULTRA PROXY REPORT<br>
    <small style='color:#888;'>/proxyreport?username=@target&reason=spam</small>
    </h1>
    """

@app.route('/proxyreport')
def proxy_report():
    username = request.args.get('username', '').strip()
    reason = request.args.get('reason', 'spam').strip().lower()
    count = int(request.args.get('count', str(len(PROXY_LIST))))
    
    if not username:
        return jsonify({"error": "Missing username"}), 400
    
    async def do_report():
        clean = username.replace("@", "").strip()
        report_reason = REPORT_REASONS.get(reason, REPORT_REASONS['spam'])
        results = []
        success = 0
        
        base_client = TelegramClient(StringSession(SESSION_STRING), API_ID, API_HASH)
        await base_client.connect()
        entity = await base_client.get_entity(clean)
        await base_client.disconnect()
        
        proxies_to_use = random.sample(PROXY_LIST, min(count, len(PROXY_LIST)))
        
        for i, proxy in enumerate(proxies_to_use):
            try:
                proxy_client = TelegramClient(
                    StringSession(SESSION_STRING),
                    API_ID, API_HASH,
                    proxy=(socks.SOCKS5, proxy["ip"], proxy["port"], True, proxy["user"], proxy["pass"])
                )
                await proxy_client.connect()
                await proxy_client(functions.messages.ReportRequest(
                    peer=entity, id=[0], reason=report_reason,
                    message=f"Report #{i+1} from {proxy['country']}"
                ))
                success += 1
                results.append({"report": f"#{i+1}", "country": proxy["country"], "ip": proxy["ip"], "status": "SENT"})
                await proxy_client.disconnect()
                await asyncio.sleep(0.5)
            except Exception as e:
                results.append({"report": f"#{i+1}", "country": proxy["country"], "status": str(e)[:30]})
        
        return {"status": "success", "target": clean, "total_sent": success, "results": results, "credit": "@BRONX_ULTRA"}
    
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    result = loop.run_until_complete(do_report())
    return jsonify(result)

@app.route('/health')
def health():
    return jsonify({"status": "ok", "credit": "@BRONX_ULTRA"})

# ============================================
# MAIN - FIXED PORT BINDING
# ============================================
if __name__ == "__main__":
    port = int(os.environ.get('PORT', 10000))
    print(f"Starting server on port {port}...")
    app.run(host='0.0.0.0', port=port)
