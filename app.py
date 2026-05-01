from flask import Flask, request, jsonify, render_template_string
from telethon import TelegramClient, functions
from telethon.sessions import StringSession
from telethon.tl.types import *
import asyncio
from datetime import datetime
import pytz

app = Flask(__name__)

# ============================================
# CONFIG
# ============================================
API_ID = 36879151
API_HASH = "45360a236343352099ffa29570f48700"
SESSION_STRING = ""  # 👈 APNA SESSION STRING DAALO

loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)
client = TelegramClient(StringSession(SESSION_STRING), API_ID, API_HASH, loop=loop)

# ============================================
# HELPER FUNCTIONS
# ============================================
def get_india_time():
    india = pytz.timezone('Asia/Kolkata')
    now = datetime.now(india)
    return now.strftime("%Y-%m-%d %H:%M:%S IST")

def get_account_age(entity_id):
    creation_time = entity_id >> 32
    if creation_time > 0:
        created = datetime.fromtimestamp(creation_time)
        delta = datetime.now() - created
        return {
            "created_date": created.strftime("%Y-%m-%d %H:%M:%S"),
            "days_ago": delta.days,
            "months_ago": round(delta.days / 30, 1),
            "years_ago": round(delta.days / 365, 2)
        }
    return None

def parse_status(status):
    if not status: return "Unknown"
    if isinstance(status, UserStatusOnline): return "🟢 Online"
    elif isinstance(status, UserStatusRecently): return "🟡 Recently"
    elif isinstance(status, UserStatusOffline):
        return f"🔴 Offline (Last: {status.was_online.strftime('%Y-%m-%d %H:%M')})" if status.was_online else "🔴 Offline"
    return "⚪ Unknown"

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
.card{background:#0a0a0a;border:2px solid #bf00ff;border-radius:15px;padding:20px;margin:15px auto;max-width:600px}
input{width:100%;padding:15px;background:#000;border:2px solid #bf00ff;border-radius:10px;color:#bf00ff;font-size:16px;margin:10px 0;font-family:monospace}
.btn{width:100%;padding:15px;background:linear-gradient(135deg,#bf00ff,#ff0066);border:none;border-radius:10px;color:#fff;font-size:18px;font-weight:bold;cursor:pointer;margin:10px 0}
.btn:hover{box-shadow:0 0 40px #bf00ff}
.features{display:flex;flex-wrap:wrap;justify-content:center;gap:5px;margin-top:15px}
.tag{background:#1a0033;border:1px solid #bf00ff;padding:4px 10px;border-radius:15px;font-size:10px;color:#bf00ff}
.result{background:#000;border:1px solid #bf00ff;border-radius:10px;padding:15px;margin-top:15px;text-align:left;max-height:400px;overflow-y:auto;font-size:12px;display:none;color:#0f0}
.key{color:#ff0}.val{color:#0ff}
</style></head><body>
<h1>👑 BRONX ULTRA GOD API</h1>
<p style='color:#888'>⚡ 30+ FEATURES TELEGRAM OSINT</p>
<div class='card'>
<h3 style='color:#bf00ff'>🔍 SEARCH</h3>
<input type='text' id='query' placeholder='@username or ID'>
<button class='btn' onclick='search()'>🔎 GOD LEVEL SEARCH</button>
<div id='load' style='color:#bf00ff;display:none'>⏳ Fetching Ultra Info...</div>
<div id='res' class='result'></div>
<div class='features'>
<span class='tag'>👤 Name</span><span class='tag'>🆔 ID</span><span class='tag'>📝 Username</span>
<span class='tag'>📱 Phone</span><span class='tag'>📄 Bio</span><span class='tag'>⭐ Premium</span>
<span class='tag'>🟢 Status</span><span class='tag'>📸 Photo</span><span class='tag'>🗓️ Account Age</span>
<span class='tag'>✅ Verified</span><span class='tag'>⚠️ Scam</span><span class='tag'>🚫 Fake</span>
<span class='tag'>🔒 Restricted</span><span class='tag'>🌐 Language</span><span class='tag'>💬 Common Chats</span>
<span class='tag'>📖 Stories</span><span class='tag'>📊 Messages</span><span class='tag'>👥 Admin Groups</span>
<span class='tag'>🔗 Last Seen</span><span class='tag'>⏰ Premium Since</span><span class='tag'>🎨 Wallpaper</span>
<span class='tag'>😊 Emoji Status</span><span class='tag'>📋 Username Count</span><span class='tag'>📛 Name Count</span>
<span class='tag'>🤖 Bot</span><span class='tag'>🔢 DC ID</span><span class='tag'>📅 First Message</span>
<span class='tag'>📨 Last Message</span><span class='tag'>🌍 Country</span><span class='tag'>💳 Mutual Contact</span>
<span class='tag'>⛔ Blocked</span><span class='tag'>🕒 IST Time</span>
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
        if(d.status=='success'){
            let h='';
            for(const[k,v] of Object.entries(d)){
                if(k=='status'||k=='credit'||k=='developer'||k=='india_time')continue;
                if(typeof v=='object'&&v!=null){
                    h+=`<div style='color:#bf00ff;margin-top:10px'>▸ ${k.replace(/_/g,' ').toUpperCase()}:</div>`;
                    for(const[sk,sv] of Object.entries(v)){
                        h+=`<span class='key'>  ${sk}:</span> <span class='val'>${JSON.stringify(sv)}</span><br>`;
                    }
                }else{
                    h+=`<span class='key'>▸ ${k}:</span> <span class='val'>${v!=null?v:'N/A'}</span><br>`;
                }
            }
            h+=`<br><span style='color:#bf00ff'>⚡ @BRONX_ULTRA</span>`;
            document.getElementById('res').innerHTML=h;
        }else{
            document.getElementById('res').innerHTML=`<span style='color:red'>❌ ${d.message}</span>`;
        }
        document.getElementById('res').style.display='block';
    }catch(e){
        document.getElementById('res').innerHTML='<span style="color:red">❌ Error</span>';
        document.getElementById('res').style.display='block';
    }
    document.getElementById('load').style.display='none';
}
</script></body></html>
"""

# ============================================
# ULTRA GOD ROUTE - 30 FEATURES
# ============================================
@app.route('/')
def home():
    return HTML

@app.route('/ultra')
def ultra():
    query = request.args.get('q', '').strip()
    
    if not query:
        return jsonify({"status": "error", "message": "Missing query"}), 400
    
    async def get_ultra():
        await client.connect()
        clean = query.replace("@", "").strip()
        
        # Resolve entity
        try:
            try:
                entity = await client.get_entity(int(clean))
            except:
                entity = await client.get_entity(clean)
        except:
            return {"status": "error", "message": f"User not found: {clean}"}
        
        result = {
            "status": "success",
            "credit": "@BRONX_ULTRA",
            "developer": "@BRONX_ULTRA",
            "india_time": get_india_time()
        }
        
        # 1-5: Basic Identity
        result["name"] = f"{getattr(entity, 'first_name', '')} {getattr(entity, 'last_name', '')}".strip()
        result["first_name"] = getattr(entity, 'first_name', '')
        result["last_name"] = getattr(entity, 'last_name', '')
        result["user_id"] = entity.id
        result["username"] = getattr(entity, 'username', None)
        
        # 6-10: Type & Flags
        result["is_bot"] = getattr(entity, 'bot', False)
        result["is_verified"] = getattr(entity, 'verified', False)
        result["is_premium"] = getattr(entity, 'premium', False)
        result["is_scam"] = getattr(entity, 'scam', False)
        result["is_fake"] = getattr(entity, 'fake', False)
        
        # 11-15: Contact & Status
        result["phone"] = getattr(entity, 'phone', None)
        result["is_restricted"] = getattr(entity, 'restricted', False)
        result["restriction_reason"] = list(getattr(entity, 'restriction_reason', [])) if entity.restricted else []
        result["language"] = getattr(entity, 'lang_code', None)
        result["online_status"] = parse_status(getattr(entity, 'status', None))
        
        # 16-20: Account Info
        result["account_age"] = get_account_age(entity.id)
        result["dc_id"] = getattr(entity, 'photo', None).dc_id if getattr(entity, 'photo', None) else None
        result["mutual_contact"] = getattr(entity, 'mutual_contact', False)
        result["is_support"] = getattr(entity, 'support', False)
        
        # Full User Info
        try:
            full = await client(functions.users.GetFullUserRequest(entity))
            
            # 21-25: Advanced Profile
            result["bio"] = full.full_user.about or ""
            result["common_chats_count"] = full.full_user.common_chats_count
            result["stories_count"] = getattr(full.full_user, 'stories_count', 0)
            result["has_profile_photo"] = full.full_user.profile_photo is not None
            result["has_personal_photo"] = full.full_user.personal_photo is not None
            
            # 26-30: Premium & Settings
            result["blocked"] = full.full_user.blocked
            result["bot_inline_geo"] = getattr(full.full_user, 'bot_inline_geo', False)
            result["can_pin_message"] = getattr(full.full_user, 'can_pin_message', False)
            result["has_wallpaper"] = full.full_user.wallpaper is not None if full.full_user.wallpaper else False
            result["emoji_status"] = str(full.full_user.emoji_status) if full.full_user.emoji_status else None
            
            if hasattr(full.full_user, 'premium_since') and full.full_user.premium_since:
                result["premium_since"] = full.full_user.premium_since.strftime("%Y-%m-%d %H:%M:%S")
            
            # Settings
            result["settings"] = {
                "sensitive_enabled": getattr(full.full_user.settings, 'sensitive_enabled', False) if full.full_user.settings else False,
                "can_change_info": getattr(full.full_user.settings, 'can_change_info', False) if full.full_user.settings else False,
            }
            
            # Business
            result["business_info"] = {
                "has_business": full.full_user.business_info is not None if hasattr(full.full_user, 'business_info') else False
            }
            
        except Exception as e:
            result["full_user_error"] = str(e)
        
        return result
    
    try:
        result = loop.run_until_complete(get_ultra())
        return jsonify(result)
    except Exception as e:
        return jsonify({"status": "error", "message": str(e), "credit": "@BRONX_ULTRA"}), 500

# ============================================
# MAIN
# ============================================
if __name__ == "__main__":
    print("👑 BRONX ULTRA GOD API")
    print("🚀 30+ Features Ready!")
    app.run(host='0.0.0.0', port=5000)
