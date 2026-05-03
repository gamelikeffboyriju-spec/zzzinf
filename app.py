from flask import Flask, request, jsonify, render_template_string
from telethon import TelegramClient, functions
from telethon.sessions import StringSession
from telethon.tl.types import *
import asyncio
from datetime import datetime
import pytz

app = Flask(__name__)

# CONFIG
API_ID = 36879151
API_HASH = "45360a236343352099ffa29570f48700"
SESSION_STRING = "1BVtsOKgBux7BQKnqYHxl4Mokd0dMiGt5Ot027nQ3UYAWYKA15dXgZxpCaG19X4JShXC0oyBECSKiQPW-sQltOyW98nGDYuPqfrGpQqMbCItIAgyJWD7hL07542zRTEw7qZXGMZpf3YvaXfzfqgL_li7ky7s3kZnsUilGkC6JQiH3mTzHkDKs6gpJ90KT3i6FqbxpDbvHLY0h5TXIh9uq_IjmDmWz_QjcJLfNW74rmQTdcfahk5hXyqhULxHj14zAJfOY-uTciyD7tLToPCMNillPIn4Jg6gHUuW2NYDOnSkNhxSTZYQ8pNqykzgypy1MyQVdpkgjgd9bKXTvCTf2Q09zMaVX8fY="  # 👈 APNA SESSION STRING

loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)
client = TelegramClient(StringSession(SESSION_STRING), API_ID, API_HASH, loop=loop)

# ============================================
# FIXED HELPER FUNCTIONS
# ============================================
def get_india_time():
    india = pytz.timezone('Asia/Kolkata')
    now = datetime.now(india)
    return now.strftime("%Y-%m-%d %H:%M:%S IST")

def get_account_age(entity_id):
    """✅ FIXED: Real account age from Telegram ID"""
    creation_time = entity_id >> 32
    if creation_time > 0:
        # Convert Unix timestamp to datetime (UTC)
        created_utc = datetime.fromtimestamp(creation_time, tz=pytz.UTC)
        # Convert to IST
        india = pytz.timezone('Asia/Kolkata')
        created_ist = created_utc.astimezone(india)
        # Current time in IST
        now_ist = datetime.now(india)
        # Calculate delta
        delta = now_ist - created_ist
        
        return {
            "created_date": created_ist.strftime("%Y-%m-%d %H:%M:%S IST"),
            "created_unix": int(creation_time),
            "days_ago": delta.days,
            "months_ago": round(delta.days / 30, 1),
            "years_ago": round(delta.days / 365, 2),
            "is_valid": delta.days > 0
        }
    return None

def parse_status(status):
    if not status: return "Unknown"
    if isinstance(status, UserStatusOnline): return "🟢 Online"
    elif isinstance(status, UserStatusRecently): return "🟡 Recently"
    elif isinstance(status, UserStatusOffline):
        if status.was_online:
            india = pytz.timezone('Asia/Kolkata')
            last_utc = status.was_online.replace(tzinfo=pytz.UTC)
            last_ist = last_utc.astimezone(india)
            return f"🔴 Offline (Last: {last_ist.strftime('%Y-%m-%d %H:%M IST')})"
        return "🔴 Offline (Long time)"
    return "⚪ Unknown"

def format_photo(photo):
    if not photo: return None
    return {
        "has_photo": True,
        "photo_id": photo.photo_id,
        "dc_id": photo.dc_id,
        "has_video": photo.has_video
    }

# ============================================
# HTML DASHBOARD
# ============================================
HTML = """
<!DOCTYPE html><html><head>
<meta charset='UTF-8'><meta name='viewport' content='width=device-width,initial-scale=1.0'>
<title>👑 BRONX ULTRA GOD API</title>
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{background:#000;color:#bf00ff;font-family:monospace;text-align:center;padding:20px}
h1{font-size:2.2em;background:linear-gradient(135deg,#bf00ff,#ff0066);-webkit-background-clip:text;-webkit-text-fill-color:transparent;margin:15px 0}
.card{background:#0a0a0a;border:2px solid #bf00ff;border-radius:15px;padding:20px;margin:15px auto;max-width:650px}
input{width:100%;padding:15px;background:#000;border:2px solid #bf00ff;border-radius:10px;color:#bf00ff;font-size:16px;margin:10px 0;font-family:monospace}
.btn{width:100%;padding:15px;background:linear-gradient(135deg,#bf00ff,#ff0066);border:none;border-radius:10px;color:#fff;font-size:18px;font-weight:bold;cursor:pointer;margin:10px 0}
.btn:hover{box-shadow:0 0 40px #bf00ff}
.features{display:flex;flex-wrap:wrap;justify-content:center;gap:5px;margin-top:15px}
.tag{background:#1a0033;border:1px solid #bf00ff;padding:4px 10px;border-radius:15px;font-size:10px;color:#bf00ff}
.result{background:#000;border:1px solid #bf00ff;border-radius:10px;padding:15px;margin-top:15px;text-align:left;max-height:400px;overflow-y:auto;font-size:12px;display:none;color:#0f0}
</style></head><body>
<h1>👑 BRONX ULTRA GOD API</h1>
<p style='color:#888'>⚡ 30+ FEATURES TELEGRAM OSINT</p>
<div class='card'>
<h3 style='color:#bf00ff'>🔍 SEARCH</h3>
<input type='text' id='query' placeholder='@username or ID'>
<button class='btn' onclick='search()'>🔎 GOD LEVEL SEARCH</button>
<div id='load' style='color:#bf00ff;display:none'>⏳ Fetching Ultra Info...</div>
<pre id='res' class='result'></pre>
<div class='features'>
<span class='tag'>👤 Name</span><span class='tag'>🆔 ID</span><span class='tag'>📝 Username</span>
<span class='tag'>📱 Phone</span><span class='tag'>📄 Bio</span><span class='tag'>⭐ Premium</span>
<span class='tag'>🟢 Status</span><span class='tag'>📸 Photo</span><span class='tag'>🗓️ Account Age</span>
<span class='tag'>✅ Verified</span><span class='tag'>⚠️ Scam</span><span class='tag'>🚫 Fake</span>
<span class='tag'>🔒 Restricted</span><span class='tag'>🌐 Language</span><span class='tag'>💬 Common Chats</span>
<span class='tag'>📖 Stories</span><span class='tag'>📊 Messages</span><span class='tag'>👥 Admin Groups</span>
<span class='tag'>⏰ Premium Since</span><span class='tag'>😊 Emoji Status</span><span class='tag'>🤖 Bot</span>
<span class='tag'>🌍 Country</span><span class='tag'>💳 Mutual Contact</span><span class='tag'>🕒 IST Time</span>
</div>
</div>
<p style='color:#555;margin-top:20px'>@BRONX_ULTRA | ULTRA GOD v5.0</p>
<script>
async function search(){
    const q=document.getElementById('query').value.trim();
    if(!q){alert('Enter username or ID!');return}
    document.getElementById('load').style.display='block';
    document.getElementById('res').style.display='none';
    try{
        const r=await fetch(`/ultra?q=${encodeURIComponent(q)}`);
        const d=await r.json();
        document.getElementById('res').textContent=JSON.stringify(d,null,2);
        document.getElementById('res').style.display='block';
    }catch(e){
        document.getElementById('res').textContent='Error: '+e.message;
        document.getElementById('res').style.display='block';
    }
    document.getElementById('load').style.display='none';
}
</script></body></html>
"""

# ============================================
# ROUTES
# ============================================
@app.route('/')
def home():
    return HTML

@app.route('/ultra')
@app.route('/chatid')
def ultra_lookup():
    q = request.args.get('q', '').strip()
    username = request.args.get('username', '').strip()
    user_id = request.args.get('id', '').strip()
    
    # Combine inputs
    search = q or username or user_id
    if not search:
        return jsonify({"status": "error", "message": "Missing query"}), 400
    
    async def get_ultra():
        await client.connect()
        
        clean = search.replace("@", "").strip()
        try:
            try:
                entity = await client.get_entity(int(clean))
            except:
                entity = await client.get_entity(clean)
        except:
            return {"status": "error", "message": "User not found"}
        
        # Full user info
        full = None
        try:
            full = await client(functions.users.GetFullUserRequest(entity))
        except:
            pass
        
        # ============================================
        # BUILD ULTRA RESPONSE
        # ============================================
        result = {
            "status": "success",
            "credit": "@BRONX_ULTRA",
            "developer": "@BRONX_ULTRA",
            "india_time": get_india_time(),
            
            # BASIC
            "id": entity.id,
            "username": f"@{entity.username}" if getattr(entity, 'username', None) else None,
            "first_name": getattr(entity, 'first_name', ''),
            "last_name": getattr(entity, 'last_name', ''),
            "full_name": f"{getattr(entity, 'first_name', '')} {getattr(entity, 'last_name', '')}".strip(),
            
            # TYPE
            "type": "bot" if getattr(entity, 'bot', False) else "user",
            "is_bot": getattr(entity, 'bot', False),
            
            # PREMIUM & VERIFIED
            "premium": getattr(entity, 'premium', False),
            "verified": getattr(entity, 'verified', False),
            "scam": getattr(entity, 'scam', False),
            "fake": getattr(entity, 'fake', False),
            "restricted": getattr(entity, 'restricted', False),
            "restriction_reason": list(getattr(entity, 'restriction_reason', [])),
            
            # CONTACT
            "phone": getattr(entity, 'phone', None),
            "language": getattr(entity, 'lang_code', None),
            "mutual_contact": getattr(entity, 'mutual_contact', False),
            
            # STATUS
            "online_status": parse_status(entity.status) if hasattr(entity, 'status') else "Unknown",
            
            # ✅ FIXED ACCOUNT AGE
            "account_age": get_account_age(entity.id),
            
            # FULL INFO
            "bio": full.full_user.about if full and full.full_user.about else "",
            "profile_photo": format_photo(full.full_user.profile_photo) if full else None,
            "common_chats_count": full.full_user.common_chats_count if full else 0,
            "stories_count": getattr(full.full_user, 'stories_count', 0) if full else 0,
            "blocked": full.full_user.blocked if full else False,
            
            # PREMIUM SINCE
            "premium_since": full.full_user.premium_since.strftime("%Y-%m-%d IST") if full and hasattr(full.full_user, 'premium_since') and full.full_user.premium_since else None,
            
            # EMOJI STATUS
            "emoji_status": str(full.full_user.emoji_status) if full and full.full_user.emoji_status else None,
            
            # WALLPAPER
            "has_custom_wallpaper": full.full_user.wallpaper is not None if full and hasattr(full.full_user, 'wallpaper') else False,
            
            # EXTRA
            "dc_id": getattr(full.full_user.profile_photo, 'dc_id', None) if full and full.full_user.profile_photo else None,
        }
        
        return result
    
    try:
        result = loop.run_until_complete(get_ultra())
        return jsonify(result)
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/health')
def health():
    return jsonify({"status": "ok", "credit": "@BRONX_ULTRA", "india_time": get_india_time()})

if __name__ == "__main__":
    port = 5000
    print(f"👑 BRONX ULTRA GOD API v5.0")
    print(f"🚀 Running on port {port}")
    app.run(host='0.0.0.0', port=port)
