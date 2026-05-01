from flask import Flask, request, jsonify
from telethon import TelegramClient, functions
from telethon.sessions import StringSession
from telethon.tl.types import UserStatusOnline, UserStatusRecently, UserStatusOffline
import asyncio
import os
from datetime import datetime
import pytz

app = Flask(__name__)

# ============================================
# CONFIGURATION - FIXED
# ============================================
API_ID = int(os.environ.get('API_ID', '31968824'))
API_HASH = os.environ.get('API_HASH', '45360a236343352099ffa29570f48700')
SESSION_STRING = os.environ.get('SESSION_STRING', '')

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

def parse_status(status):
    if isinstance(status, UserStatusOnline):
        return {"status": "🟢 Online", "detail": "Currently online"}
    elif isinstance(status, UserStatusRecently):
        return {"status": "🟡 Recently", "detail": "Seen within last week"}
    elif isinstance(status, UserStatusOffline):
        return {
            "status": "🔴 Offline",
            "last_seen": status.was_online.strftime("%Y-%m-%d %H:%M:%S") if status.was_online else "Long time ago"
        }
    return {"status": "⚪ Unknown"}

def get_account_age(entity_id):
    """Calculate account age from Telegram ID"""
    creation_time = entity_id >> 32
    if creation_time > 0:
        created = datetime.fromtimestamp(creation_time)
        now = datetime.now()
        delta = now - created
        return {
            "created_date": created.strftime("%Y-%m-%d"),
            "created_time": created.strftime("%H:%M:%S"),
            "days_ago": delta.days,
            "months_ago": round(delta.days / 30, 1),
            "years_ago": round(delta.days / 365, 2)
        }
    return None

def format_photo(photo):
    if not photo:
        return None
    return {
        "has_photo": True,
        "photo_id": photo.photo_id,
        "has_video": photo.has_video
    }

# ============================================
# DASHBOARD
# ============================================
HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>BRONX ULTRA GOD API</title>
    <meta charset="UTF-8">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            background: linear-gradient(135deg, #0a0a0a, #1a0033);
            color: #bf00ff; 
            font-family: 'Courier New', monospace; 
            display: flex; 
            align-items: center; 
            justify-content: center; 
            min-height: 100vh; 
            padding: 20px;
        }
        .card { 
            border: 2px solid #bf00ff; 
            padding: 40px; 
            border-radius: 20px; 
            box-shadow: 0 0 40px #bf00ff66; 
            text-align: center; 
            max-width: 650px;
            background: #0a0a0a;
        }
        h1 { 
            font-size: 32px; 
            background: linear-gradient(135deg, #bf00ff, #ff0066);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        .badge { 
            background: linear-gradient(135deg, #bf00ff, #ff0066);
            color: #fff; 
            padding: 8px 25px; 
            border-radius: 30px; 
            font-weight: bold; 
            display: inline-block;
            margin: 15px 0;
        }
        .endpoint { 
            background: #111; 
            padding: 15px; 
            border-radius: 10px; 
            margin: 15px 0;
            border: 1px solid #333;
            text-align: left;
        }
        code { 
            background: #000; 
            padding: 8px 12px; 
            border-radius: 5px; 
            color: #00ff88; 
            font-size: 13px;
            display: block;
            margin: 8px 0;
        }
        .features {
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
            margin-top: 15px;
        }
        .feature-tag {
            background: #1a0033;
            border: 1px solid #bf00ff;
            padding: 3px 10px;
            border-radius: 15px;
            font-size: 11px;
            color: #bf00ff;
        }
        .footer { margin-top: 25px; color: #555; font-size: 12px; }
    </style>
</head>
<body>
    <div class="card">
        <h1>👑 BRONX ULTRA GOD API</h1>
        <span class="badge">⚡ GOD MODE ACTIVE</span>
        <p style="color:#ccc; margin:15px 0;">Telegram Full OSINT Extractor</p>
        
        <div class="endpoint">
            <b style="color:#bf00ff;">📌 USERNAME:</b>
            <code>/chatid?username=USERNAME</code>
        </div>
        <div class="endpoint">
            <b style="color:#bf00ff;">📌 ID:</b>
            <code>/chatid?id=123456789</code>
        </div>
        
        <div class="features">
            <span class="feature-tag">👤 Name</span>
            <span class="feature-tag">📱 Phone</span>
            <span class="feature-tag">🆔 Chat ID</span>
            <span class="feature-tag">📝 Bio</span>
            <span class="feature-tag">⭐ Premium</span>
            <span class="feature-tag">📸 Photo</span>
            <span class="feature-tag">🗓️ Account Age</span>
            <span class="feature-tag">👥 Groups</span>
            <span class="feature-tag">📢 Channels</span>
            <span class="feature-tag">🟢 Status</span>
            <span class="feature-tag">🔒 Restricted</span>
            <span class="feature-tag">✅ Verified</span>
            <span class="feature-tag">⚠️ Scam</span>
            <span class="feature-tag">🌐 Lang</span>
            <span class="feature-tag">📊 Messages</span>
        </div>
        
        <div class="footer">🔒 @BRONX_ULTRA | GOD LEVEL v3.0</div>
    </div>
</body>
</html>
"""

# ============================================
# ROUTES
# ============================================
@app.route('/chatid')
def chatid():
    username = request.args.get('username', '').strip()
    user_id = request.args.get('id', '').strip()
    
    if not username and not user_id:
        return jsonify({
            "status": "error",
            "message": "Missing 'username' or 'id' parameter",
            "credit": "@BRONX_ULTRA"
        }), 400
    
    async def get_full_info():
        await client.connect()
        
        # Get entity
        if user_id:
            clean = user_id.replace("@", "").strip()
            try:
                entity = await client.get_entity(int(clean))
            except:
                entity = await client.get_entity(f"@{clean}")
        else:
            clean = username.replace("@", "").strip()
            entity = await client.get_entity(f"@{clean}")
        
        # ============================================
        # BUILD GOD LEVEL RESULT
        # ============================================
        result = {
            "status": "success",
            "credit": "@BRONX_ULTRA",
            "developer": "@BRONX_ULTRA",
            "india_time": get_india_time()
        }
        
        # ============================================
        # 1. BASIC INFO
        # ============================================
        result["basic_info"] = {
            "id": entity.id,
            "username": getattr(entity, 'username', None),
            "first_name": getattr(entity, 'first_name', ''),
            "last_name": getattr(entity, 'last_name', ''),
            "type": "user" if not hasattr(entity, 'broadcast') else "channel"
        }
        
        if hasattr(entity, 'title'):
            result["basic_info"]["title"] = entity.title
        if hasattr(entity, 'participants_count'):
            result["basic_info"]["participants_count"] = entity.participants_count
        
        # ============================================
        # 2. USER SPECIFIC INFO
        # ============================================
        if not hasattr(entity, 'broadcast'):
            result["phone"] = getattr(entity, 'phone', None)
            result["premium"] = getattr(entity, 'premium', False)
            result["verified"] = getattr(entity, 'verified', False)
            result["scam"] = getattr(entity, 'scam', False)
            result["fake"] = getattr(entity, 'fake', False)
            result["restricted"] = getattr(entity, 'restricted', False)
            result["language"] = getattr(entity, 'lang_code', None)
            result["status"] = parse_status(entity.status) if entity.status else "Unknown"
            result["account_age"] = get_account_age(entity.id)
            
            # Full user info
            try:
                full = await client(functions.users.GetFullUserRequest(entity))
                result["bio"] = full.full_user.about or ""
                result["profile_photo"] = format_photo(full.full_user.profile_photo)
                result["common_chats_count"] = full.full_user.common_chats_count
                result["stories_count"] = getattr(full.full_user, 'stories_count', 0)
                
                if hasattr(full.full_user, 'premium_since') and full.full_user.premium_since:
                    result["premium_since"] = full.full_user.premium_since.strftime("%Y-%m-%d")
            except:
                pass
            
            # ============================================
            # GROUPS & CHANNELS (FIXED)
            # ============================================
            try:
                dialogs = await client.get_dialogs()
                groups_count = 0
                channels_count = 0
                groups_list = []
                channels_list = []
                
                if dialogs:
                    for d in dialogs:
                        try:
                            if d.is_group and not d.is_channel:
                                groups_count += 1
                                if len(groups_list) < 5:
                                    groups_list.append({
                                        "id": d.id,
                                        "name": d.name
                                    })
                            elif d.is_channel:
                                channels_count += 1
                                if len(channels_list) < 5:
                                    channels_list.append({
                                        "id": d.id,
                                        "name": d.name,
                                        "username": getattr(d.entity, 'username', None) if hasattr(d, 'entity') else None
                                    })
                        except:
                            continue
                
                result["groups_joined"] = {"count": groups_count, "list": groups_list}
                result["channels_joined"] = {"count": channels_count, "list": channels_list}
            except Exception as e:
                result["groups_joined"] = {"count": 0, "list": [], "note": str(e)}
                result["channels_joined"] = {"count": 0, "list": [], "note": str(e)}
        
        return result
    
    try:
        result = loop.run_until_complete(get_full_info())
        return jsonify(result)
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e),
            "credit": "@BRONX_ULTRA"
        }), 404

@app.route('/chatid')
def chatid():
    username = request.args.get('username', '').strip()
    user_id = request.args.get('id', '').strip()
    
    

@app.route('/health')
def health():
    return jsonify({
        "status": "healthy",
        "credit": "@BRONX_ULTRA",
        "india_time": get_india_time()
    })

# ============================================
# MAIN
# ============================================
if __name__ == "__main__":
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)
