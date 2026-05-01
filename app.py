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
@app.route('/')
def home():
    return render_template_string(HTML)

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
        
        # Channel/Group Info
        if hasattr(entity, 'broadcast') and entity.broadcast:
            result["basic_info"]["type"] = "channel"
            result["basic_info"]["title"] = getattr(entity, 'title', '')
            result["basic_info"]["participants_count"] = getattr(entity, 'participants_count', None)
        elif hasattr(entity, 'megagroup') and entity.megagroup:
            result["basic_info"]["type"] = "supergroup"
            result["basic_info"]["title"] = getattr(entity, 'title', '')
        elif hasattr(entity, 'title'):
            result["basic_info"]["type"] = "group"
            result["basic_info"]["title"] = entity.title
        
        # ============================================
        # 2. VIP INFO (User specific)
        # ============================================
        if result["basic_info"]["type"] == "user":
            # Phone
            result["phone"] = getattr(entity, 'phone', None)
            
            # Premium
            result["premium"] = getattr(entity, 'premium', False)
            
            # Verification
            result["verified"] = getattr(entity, 'verified', False)
            
            # Scam/Fake
            result["scam"] = getattr(entity, 'scam', False)
            result["fake"] = getattr(entity, 'fake', False)
            
            # Restricted
            result["restricted"] = getattr(entity, 'restricted', False)
            result["restriction_reason"] = list(getattr(entity, 'restriction_reason', []))
            
            # Language
            result["language"] = getattr(entity, 'lang_code', None)
            
            # Status
            result["status"] = parse_status(entity.status)
            
            # Account Age
            result["account_age"] = get_account_age(entity.id)
            
            # ============================================
            # 3. FULL USER INFO (Bio, Photos, etc)
            # ============================================
            try:
                full = await client(functions.users.GetFullUserRequest(entity))
                
                # Bio
                result["bio"] = full.full_user.about or ""
                
                # Profile Photo
                result["profile_photo"] = format_photo(full.full_user.profile_photo)
                
                # Common Chats Count
                result["common_chats_count"] = full.full_user.common_chats_count
                
                # Blocked
                result["blocked"] = full.full_user.blocked
                
                # Stories
                result["stories_count"] = getattr(full.full_user, 'stories_count', 0)
                
                # Premium Since
                if hasattr(full.full_user, 'premium_since') and full.full_user.premium_since:
                    result["premium_since"] = full.full_user.premium_since.strftime("%Y-%m-%d")
                
                # Emoji Status
                if full.full_user.emoji_status:
                    result["emoji_status"] = str(full.full_user.emoji_status)
                
                # Wallpaper
                if full.full_user.wallpaper:
                    result["has_custom_wallpaper"] = True
                    
            except Exception as e:
                result["full_user_error"] = str(e)
            
            # ============================================
            # 4. GROUPS & CHANNELS COUNT
            # ============================================
            try:
                dialogs = await client.get_dialogs()
                groups_count = 0
                channels_count = 0
                groups_list = []
                channels_list = []
                
                for d in dialogs:
                    if d.is_group and not d.is_channel:
                        groups_count += 1
                        groups_list.append({
                            "id": d.id,
                            "name": d.name,
                            "participants": getattr(d.entity, 'participants_count', None)
                        })
                    elif d.is_channel:
                        channels_count += 1
                        channels_list.append({
                            "id": d.id,
                            "name": d.name,
                            "username": getattr(d.entity, 'username', None),
                            "participants": getattr(d.entity, 'participants_count', None)
                        })
                
                result["groups_joined"] = {
                    "count": groups_count,
                    "list": groups_list[:5]  # Top 5 only
                }
                result["channels_joined"] = {
                    "count": channels_count,
                    "list": channels_list[:5]  # Top 5 only
                }
            except Exception as e:
                result["dialogs_error"] = str(e)
        
        # ============================================
        # 5. CHANNEL INFO (if channel)
        # ============================================
        if result["basic_info"]["type"] in ["channel", "supergroup"]:
            try:
                full = await client(functions.channels.GetFullChannelRequest(entity))
                result["channel_info"] = {
                    "about": full.full_chat.about or "",
                    "participants_count": full.full_chat.participants_count,
                    "admins_count": getattr(full.full_chat, 'admins_count', None),
                    "kicked_count": getattr(full.full_chat, 'kicked_count', None),
                }
            except:
                pass
        
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
