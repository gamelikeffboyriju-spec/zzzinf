from flask import Flask, request, jsonify
from telethon import TelegramClient, functions
from telethon.sessions import StringSession
from telethon.tl.types import InputReportReasonSpam, InputReportReasonViolence, InputReportReasonPornography, InputReportReasonChildAbuse, InputReportReasonCopyright, InputReportReasonFake
import asyncio
import os
import random
import socks
import time

app = Flask(__name__)

# ============================================
# CONFIGURATION
# ============================================
API_ID = int(os.environ.get('API_ID', '36879151'))
API_HASH = os.environ.get('API_HASH', '45360a236343352099ffa29570f48700')
SESSION_STRING = os.environ.get('SESSION_STRING', '')

# ============================================
# YOUR PROXY LIST (IP:PORT:USERNAME:PASSWORD)
# ============================================
PROXY_LIST = [
    {"ip": "31.59.20.176", "port": 6754, "user": "uvvdpmaz", "pass": "bgjzombtih9j", "country": "🇬🇧 UK"},
    {"ip": "198.23.239.134", "port": 6540, "user": "uvvdpmaz", "pass": "bgjzombtih9j", "country": "🇺🇸 US"},
    {"ip": "45.38.107.97", "port": 6014, "user": "uvvdpmaz", "pass": "bgjzombtih9j", "country": "🇬🇧 UK"},
    {"ip": "107.172.163.27", "port": 6543, "user": "uvvdpmaz", "pass": "bgjzombtih9j", "country": "🇺🇸 US"},
    {"ip": "198.105.121.200", "port": 6462, "user": "uvvdpmaz", "pass": "bgjzombtih9j", "country": "🇬🇧 UK"},
    {"ip": "216.10.27.159", "port": 6837, "user": "uvvdpmaz", "pass": "bgjzombtih9j", "country": "🇺🇸 US"},
    {"ip": "142.111.67.146", "port": 5611, "user": "uvvdpmaz", "pass": "bgjzombtih9j", "country": "🇯🇵 Japan"},
    {"ip": "191.96.254.138", "port": 6185, "user": "uvvdpmaz", "pass": "bgjzombtih9j", "country": "🇺🇸 US"},
    {"ip": "31.58.9.4", "port": 6077, "user": "uvvdpmaz", "pass": "bgjzombtih9j", "country": "🇩🇪 Germany"},
    {"ip": "104.239.107.47", "port": 5699, "user": "uvvdpmaz", "pass": "bgjzombtih9j", "country": "🇺🇸 US"},
]

# ============================================
# REPORT REASONS
# ============================================
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
    <!DOCTYPE html>
    <html>
    <head>
        <title>BRONX ULTRA PROXY REPORT</title>
        <style>
            body { background: #000; color: #ff4444; font-family: monospace; padding: 30px; }
            h1 { color: #ff0000; text-shadow: 0 0 30px #ff0000; text-align: center; }
            .card { background: #111; border: 1px solid #ff0000; border-radius: 15px; padding: 20px; margin: 15px 0; }
            code { background: #000; padding: 10px; color: #0f0; display: block; margin: 10px 0; border-radius: 8px; font-size: 12px; }
            .proxy-count { color: #ff00ff; font-size: 24px; font-weight: bold; }
        </style>
    </head>
    <body>
        <h1>🌍 BRONX ULTRA PROXY REPORT</h1>
        <p style="text-align:center; color:#888;">
            <span class="proxy-count">10 PROXIES</span> | 
            <span style="color:#ffaa00;">6 COUNTRIES</span>
        </p>
        
        <div class="card">
            <h3 style="color:#ff00ff;">🔥 PROXY REPORT:</h3>
            <code>/proxyreport?username=@target&reason=spam&count=10</code>
            <p style="color:#888;">
                Har report <span style="color:#ff00ff;">DIFFERENT COUNTRY</span> se!
            </p>
        </div>
        
        <div class="card">
            <h3 style="color:#ff0000;">💀 MASS PROXY REPORT:</h3>
            <code>/massproxy?username=@target&reason=child_abuse&rounds=5</code>
            <p style="color:#888;">
                10 proxies × 5 rounds = <span style="color:#ff0000;">50 REPORTS!</span>
            </p>
        </div>
        
        <div class="card">
            <h3 style="color:#ffaa00;">📊 PROXY STATUS:</h3>
            <code>/proxystatus</code>
        </div>
    </body>
    </html>
    """

@app.route('/proxystatus')
def proxy_status():
    return jsonify({
        "total_proxies": len(PROXY_LIST),
        "countries": list(set(p["country"] for p in PROXY_LIST)),
        "proxy_list": [{
            "ip": p["ip"],
            "country": p["country"],
            "port": p["port"]
        } for p in PROXY_LIST],
        "credit": "@BRONX_ULTRA"
    })

@app.route('/proxyreport')
def proxy_report():
    """Har proxy se ek report - Different IPs!"""
    username = request.args.get('username', '').strip()
    reason = request.args.get('reason', 'spam').strip().lower()
    count = int(request.args.get('count', str(len(PROXY_LIST))))
    
    if not username:
        return jsonify({"error": "Missing username"}), 400
    
    async def do_proxy_report():
        clean = username.replace("@", "").strip()
        report_reason = REPORT_REASONS.get(reason, REPORT_REASONS['spam'])
        results = []
        success = 0
        
        # Base client se entity lo
        base_client = TelegramClient(StringSession(SESSION_STRING), API_ID, API_HASH)
        await base_client.connect()
        entity = await base_client.get_entity(clean)
        await base_client.disconnect()
        
        # Ab har proxy se alag client banao
        proxies_to_use = random.sample(PROXY_LIST, min(count, len(PROXY_LIST)))
        
        for i, proxy in enumerate(proxies_to_use):
            try:
                # Proxy client
                proxy_client = TelegramClient(
                    StringSession(SESSION_STRING),
                    API_ID,
                    API_HASH,
                    proxy=(
                        socks.SOCKS5,
                        proxy["ip"],
                        proxy["port"],
                        True,
                        proxy["user"],
                        proxy["pass"]
                    )
                )
                
                await proxy_client.connect()
                
                # Report with proxy IP
                await proxy_client(functions.messages.ReportRequest(
                    peer=entity,
                    id=[0],
                    reason=report_reason,
                    message=f"Report #{i+1} from {proxy['country']} - {reason}"
                ))
                
                success += 1
                results.append({
                    "report": f"#{i+1}",
                    "country": proxy["country"],
                    "ip": proxy["ip"],
                    "status": "✅ SENT"
                })
                
                await proxy_client.disconnect()
                await asyncio.sleep(random.uniform(0.5, 1.5))
                
            except Exception as e:
                results.append({
                    "report": f"#{i+1}",
                    "country": proxy["country"],
                    "ip": proxy["ip"],
                    "status": f"❌ {str(e)[:40]}"
                })
        
        return {
            "status": "success",
            "target": clean,
            "reason": reason,
            "total_proxies_used": len(proxies_to_use),
            "total_sent": success,
            "countries_used": list(set(r["country"] for r in results if "✅" in r.get("status", ""))),
            "ban_probability": get_ban_prob(success, reason),
            "results": results,
            "credit": "@BRONX_ULTRA"
        }
    
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(do_proxy_report())
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/massproxy')
def mass_proxy():
    """Multiple rounds with all proxies"""
    username = request.args.get('username', '').strip()
    reason = request.args.get('reason', 'spam').strip().lower()
    rounds = int(request.args.get('rounds', '5'))
    
    if not username:
        return jsonify({"error": "Missing username"}), 400
    
    async def do_mass():
        clean = username.replace("@", "").strip()
        report_reason = REPORT_REASONS.get(reason, REPORT_REASONS['spam'])
        total_sent = 0
        
        # Base client
        base_client = TelegramClient(StringSession(SESSION_STRING), API_ID, API_HASH)
        await base_client.connect()
        entity = await base_client.get_entity(clean)
        await base_client.disconnect()
        
        for round_num in range(rounds):
            proxy = random.choice(PROXY_LIST)
            
            try:
                proxy_client = TelegramClient(
                    StringSession(SESSION_STRING),
                    API_ID,
                    API_HASH,
                    proxy=(
                        socks.SOCKS5,
                        proxy["ip"],
                        proxy["port"],
                        True,
                        proxy["user"],
                        proxy["pass"]
                    )
                )
                
                await proxy_client.connect()
                
                await proxy_client(functions.messages.ReportRequest(
                    peer=entity,
                    id=[0],
                    reason=report_reason,
                    message=f"Mass Round {round_num+1} from {proxy['country']}"
                ))
                
                total_sent += 1
                await proxy_client.disconnect()
                await asyncio.sleep(random.uniform(0.3, 1.0))
                
            except:
                pass
        
        return {
            "status": "success",
            "target": clean,
            "reason": reason,
            "total_rounds": rounds,
            "total_sent": total_sent,
            "ban_probability": get_ban_prob(total_sent, reason),
            "credit": "@BRONX_ULTRA"
        }
    
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(do_mass())
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

def get_ban_prob(count, reason):
    if count >= 50: return "☠️ 99% BAN"
    elif count >= 30: return "💀 80% BAN"
    elif count >= 20: return "🔴 60% SUSPENSION"
    elif count >= 10: return "🟠 35% RESTRICTED"
    else: return "🟡 15% FLAGGED"

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=10000)
