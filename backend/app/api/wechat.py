from fastapi import APIRouter, Request, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.models import User, Order
from app.utils.auth import get_current_user
from io import BytesIO
import hashlib
import random
import string
import xml.etree.ElementTree as ET
from datetime import datetime

router = APIRouter(prefix="/wechat", tags=["微信公众号"])

WECHAT_TOKEN = "smartdrill_wx_token_2025"

BIND_POINTS_REWARD = 50

def generate_bind_code(length=6):
    return ''.join(random.choices(string.digits, k=length))

@router.get("/mp")
async def wechat_verify(signature: str, timestamp: str, nonce: str, echostr: str):
    params = [WECHAT_TOKEN, timestamp, nonce]
    params.sort()
    tmp_str = ''.join(params)
    hash_str = hashlib.sha1(tmp_str.encode()).hexdigest()
    
    if hash_str == signature:
        return int(echostr)
    else:
        raise HTTPException(status_code=403, detail="Invalid signature")

def build_text_response(from_user, to_user, content):
    response = f"""<xml>
<ToUserName><![CDATA[{from_user}]]></ToUserName>
<FromUserName><![CDATA[{to_user}]]></FromUserName>
<CreateTime>{int(datetime.now().timestamp())}</CreateTime>
<MsgType><![CDATA[text]]></MsgType>
<Content><![CDATA[{content}]]></Content>
</xml>"""
    return response

@router.post("/mp")
async def wechat_message(request: Request, db: Session = Depends(get_db)):
    body = await request.body()
    
    try:
        root = ET.fromstring(body)
    except ET.ParseError:
        return "success"
    
    msg_type = root.findtext("MsgType", "")
    from_user = root.findtext("FromUserName", "")
    to_user = root.findtext("ToUserName", "")
    content = root.findtext("Content", "").strip()
    event = root.findtext("Event", "")
    
    if msg_type == "event":
        if event == "subscribe":
            return build_text_response(from_user, to_user, 
                "欢迎关注智练通！\n\n"
                "📚 中小学全科单元复习与强化训练\n"
                "点菜单「开始学习」进入学习\n\n"
                "回复「绑定」获取绑定码，在APP内绑定可领50积分哦～")
        
        elif event == "unsubscribe":
            user = db.query(User).filter(User.openid == from_user).first()
            if user:
                user.subscribed = None
                db.commit()
            return "success"
    
    if msg_type == "text":
        if content == "绑定" or content == "绑定微信":
            user = db.query(User).filter(User.openid == from_user).first()
            
            if user and user.bind_code:
                return build_text_response(from_user, to_user, 
                    f"您的绑定码：{user.bind_code}\n\n"
                    f"打开智练通 → 我的 → 绑定微信 → 输入绑定码\n"
                    f"绑定成功即可获得{BIND_POINTS_REWARD}积分奖励！")
            
            bind_code = generate_bind_code()
            
            while db.query(User).filter(User.bind_code == bind_code).first():
                bind_code = generate_bind_code()
            
            existing_user = db.query(User).filter(User.openid == from_user).first()
            if existing_user:
                existing_user.bind_code = bind_code
                existing_user.subscribed = datetime.utcnow()
                db.commit()
            else:
                new_user = User(
                    username=f"wx_{from_user[-8:]}",
                    password="wx_user_no_password",
                    openid=from_user,
                    bind_code=bind_code,
                    subscribed=datetime.utcnow(),
                    points=0
                )
                db.add(new_user)
                db.commit()
                db.refresh(new_user)
            
            return build_text_response(from_user, to_user, 
                f"您的绑定码：{bind_code}\n\n"
                f"打开智练通 → 我的 → 绑定微信 → 输入绑定码\n"
                f"绑定成功即可获得{BIND_POINTS_REWARD}积分奖励！")
    
    return "success"

@router.post("/bind")
def bind_wechat(
    data: dict,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    bind_code = data.get('bind_code', '').strip()
    
    if not bind_code:
        raise HTTPException(status_code=400, detail="绑定码不能为空")
    
    if user.openid:
        raise HTTPException(status_code=400, detail="您的账号已绑定微信")
    
    wx_user = db.query(User).filter(User.bind_code == bind_code).first()
    
    if not wx_user:
        raise HTTPException(status_code=400, detail="绑定码无效或已过期")
    
    if wx_user.id == user.id:
        raise HTTPException(status_code=400, detail="不能绑定自己")
    
    existing = db.query(User).filter(User.openid == wx_user.openid, User.id != wx_user.id).first()
    if existing:
        raise HTTPException(status_code=400, detail="该微信已绑定其他账号")
    
    user.openid = wx_user.openid
    user.nickname = wx_user.nickname
    user.avatar = wx_user.avatar
    user.subscribed = wx_user.subscribed
    
    wx_user.bind_code = None
    
    user.points += BIND_POINTS_REWARD
    
    order = Order(
        user_id=user.id,
        title="微信绑定奖励",
        order_type="reward",
        points=BIND_POINTS_REWARD
    )
    db.add(order)
    
    db.commit()
    db.refresh(user)
    
    return {
        "message": f"绑定成功，获得{BIND_POINTS_REWARD}积分",
        "points": user.points,
        "openid": user.openid,
        "nickname": user.nickname,
        "avatar": user.avatar
    }

@router.get("/bind-status")
def get_bind_status(user: User = Depends(get_current_user)):
    return {
        "is_bound": bool(user.openid),
        "nickname": user.nickname,
        "avatar": user.avatar,
        "subscribed": user.subscribed
    }
