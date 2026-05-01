from flask import Flask, request, jsonify
from telethon import TelegramClient, functions
from telethon.sessions import StringSession
from telethon.tl.types import UserStatusOnline, UserStatusRecently, UserStatusOffline
import asyncio
import os
from datetime import datetime

app = Flask(__name__)

# ============================================
# CONFIGURATION
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
    now = datetime.now()
    return now.strftime("%Y-%m-%d %H:%M:%S") + " IST"

def parse_status(status):
    if not status:
        return "Unknown"
    if isinstance(status, UserStatusOnline):
        return "Online"
    elif isinstance(status, UserStatusRecently):
        return "Recently"
    elif isinstance(status, UserStatusOffline):
        if status.was_online:
            return f"Offline (Last seen: {status.was_online.strftime('%Y-%m-%d %H:%M:%S')})"
        return "Offline"
    return "Unknown"

def get_account_age(entity_id):
    creation_time = entity_id >> 32
    if creation_time > 0:
        created = datetime.fromtimestamp(creation_time)
        now = datetime.now()
        delta = now - created
        return {
            "created_date": created.strftime("%Y-%m-%d"),
            "days_ago": delta.days,
            "months_ago": round(delta.days / 30, 1),
            "years_ago": round(delta.days / 365, 2)
        }
    return None

def format_photo(photo):
    if not photo:
        return None
    return {"has_photo": True, "photo_id": photo.photo_id}

# ============================================
# ROUTES
# ============================================
@app.route('/')
def home():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>BRONX ULTRA API</title>
        <style>
            body { background: #000; color: #0ff; font-family: monospace; text-align: center; padding: 50px; }
            code { background: #111; padding: 10px; color: #fa0; border-radius: 5px; display: inline-block; margin: 10px; }
            .features { color: #888; font-size: 12px; margin-top: 20px; }
        </style>
    </head>
    <body>
        <h1>👑 BRONX ULTRA GOD API</h1>
        <h3>✅ ONLINE</h3>
        <code>GET /chatid?username=USERNAME</code>
        <code>GET /chatid?id=123456789</code>
        <p class="features">15+ Features: Name, ID, Username, Bio, Phone, Premium, Status, Groups, Channels, Account Age, Photos & More!</p>
        <p style="color:#555; margin-top:30px;">@BRONX_ULTRA | GOD LEVEL v3.0</p>
    </body>
    </html>
    """

@app.route('/chatid')
def chatid():
    username = request.args.get('username', '').strip()
    user_id = request.args.get('id', '').strip()
    
    if not username and not user_id:
        return jsonify({"status": "error", "message": "Missing username or id", "credit": "@BRONX_ULTRA"}), 400
    
    async def get_full_info():
        await client.connect()
        
        # Resolve entity
        try:
            if user_id:
                clean = user_id.replace("@", "").strip()
                try:
                    entity = await client.get_entity(int(clean))
                except:
                    entity = await client.get_entity(clean) if clean else None
            else:
                clean = username.replace("@", "").strip()
                entity = await client.get_entity(clean)
        except Exception as e:
            return {"status": "error", "message": f"Cannot find: {username or user_id}", "credit": "@BRONX_ULTRA"}
        
        result = {
            "status": "success",
            "credit": "@BRONX_ULTRA",
            "developer": "@BRONX_ULTRA",
            "india_time": get_india_time()
        }
        
        # Basic Info
        result["id"] = entity.id
        result["username"] = getattr(entity, 'username', None)
        result["first_name"] = getattr(entity, 'first_name', '')
        result["last_name"] = getattr(entity, 'last_name', '')
        
        if hasattr(entity, 'title'):
            result["title"] = entity.title
            result["type"] = "channel" if getattr(entity, 'broadcast', False) else "group"
        else:
            result["type"] = "user"
        
        # User-specific info
        if not hasattr(entity, 'broadcast'):
            result["phone"] = getattr(entity, 'phone', None)
            result["premium"] = getattr(entity, 'premium', False)
            result["verified"] = getattr(entity, 'verified', False)
            result["scam"] = getattr(entity, 'scam', False)
            result["fake"] = getattr(entity, 'fake', False)
            result["restricted"] = getattr(entity, 'restricted', False)
            result["language"] = getattr(entity, 'lang_code', None)
            result["online_status"] = parse_status(getattr(entity, 'status', None))
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
            
            # Groups & Channels list
            try:
                dialogs = await client.get_dialogs()
                groups = []
                channels = []
                
                for d in dialogs:
                    try:
                        if d.is_group and not getattr(d, 'is_channel', False):
                            groups.append({"id": d.id, "name": d.name})
                        elif getattr(d, 'is_channel', False):
                            channels.append({"id": d.id, "name": d.name})
                    except:
                        continue
                
                result["groups_count"] = len(groups)
                result["groups_list"] = groups[:10]
                result["channels_count"] = len(channels)
                result["channels_list"] = channels[:10]
            except Exception as e:
                result["groups_count"] = 0
                result["channels_count"] = 0
        
        return result
    
    try:
        result = loop.run_until_complete(get_full_info())
        return jsonify(result)
    except Exception as e:
        return jsonify({"status": "error", "message": str(e), "credit": "@BRONX_ULTRA"}), 500

@app.route('/health')
def health():
    return jsonify({"status": "ok", "credit": "@BRONX_ULTRA"})

# ============================================
# MAIN
# ============================================
if __name__ == "__main__":
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)
