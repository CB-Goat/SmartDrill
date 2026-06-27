from fastapi import APIRouter, Request, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.models import User, Order
from app.utils.auth import get_current_user, get_current_admin
from io import BytesIO
import hashlib
import random
import string
import xml.etree.ElementTree as ET
from datetime import datetime
import httpx
import json

router = APIRouter(prefix="/wechat", tags=["微信公众号"])

WECHAT_TOKEN = "smartdrill_wx_token_2025"
WECHAT_APPID = "wx6032ec9465fc7483"
WECHAT_APPSECRET = ""

BIND_POINTS_REWARD = 50

H5_BASE_URL = "https://smartdrill.handy.xin"

_access_token = {"token": None, "expires_at": 0}

def generate_bind_code(length=6):
    return ''.join(random.choices(string.digits, k=length))

async def get_access_token():
    if _access_token["token"] and _access_token["expires_at"] > datetime.now().timestamp():
        return _access_token["token"]
    
    if not WECHAT_APPSECRET:
        raise HTTPException(status_code=400, detail="未配置AppSecret")
    
    url = f"https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid={WECHAT_APPID}&secret={WECHAT_APPSECRET}"
    async with httpx.AsyncClient() as client:
        resp = await client.get(url)
        data = resp.json()
    
    if "access_token" not in data:
        raise HTTPException(status_code=400, detail=f"获取access_token失败: {data.get('errmsg', '未知错误')}")
    
    _access_token["token"] = data["access_token"]
    _access_token["expires_at"] = datetime.now().timestamp() + data.get("expires_in", 7200) - 300
    
    return _access_token["token"]

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

def build_news_response(from_user, to_user, articles):
    items_xml = ""
    for art in articles:
        items_xml += f"""
    <item>
      <Title><![CDATA[{art.get('title', '')}]]></Title>
      <Description><![CDATA[{art.get('description', '')}]]></Description>
      <PicUrl><![CDATA[{art.get('picurl', '')}]]></PicUrl>
      <Url><![CDATA[{art.get('url', '')}]]></Url>
    </item>"""
    
    response = f"""<xml>
<ToUserName><![CDATA[{from_user}]]></ToUserName>
<FromUserName><![CDATA[{to_user}]]></FromUserName>
<CreateTime>{int(datetime.now().timestamp())}</CreateTime>
<MsgType><![CDATA[news]]></MsgType>
<ArticleCount>{len(articles)}</ArticleCount>
<Articles>{items_xml}
</Articles>
</xml>"""
    return response

def get_welcome_text():
    return ("欢迎关注智练通！\n\n"
            "📚 中小学全科单元复习与强化训练\n"
            "点下方菜单「开始学习」进入学习\n\n"
            "回复「绑定」获取绑定码，\n"
            "在APP内绑定可领50积分哦～")

def get_help_text():
    return ("【智练通使用指南】\n\n"
            "📖 单元复习：知识点+考点系统梳理\n"
            "✏️ 训练刷题：智能组卷，针对性练习\n\n"
            "回复「绑定」获取绑定码\n"
            "回复「学习」进入学习首页\n"
            "回复「我的」查看个人中心\n\n"
            "有问题请留言，我们会尽快回复～")

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
    event_key = root.findtext("EventKey", "")
    
    if msg_type == "event":
        if event == "subscribe":
            return build_text_response(from_user, to_user, get_welcome_text())
        
        elif event == "unsubscribe":
            user = db.query(User).filter(User.openid == from_user).first()
            if user:
                user.subscribed = None
                db.commit()
            return "success"
        
        elif event == "CLICK":
            if event_key == "BIND":
                return handle_bind_request(db, from_user, to_user)
            elif event_key == "HELP":
                return build_text_response(from_user, to_user, get_help_text())
        
        elif event == "VIEW":
            pass
    
    if msg_type == "text":
        text = content.lower()
        
        if text in ["绑定", "绑定微信", "bangding", "bd"]:
            return handle_bind_request(db, from_user, to_user)
        
        elif text in ["学习", "开始学习", "首页", "home"]:
            articles = [{
                "title": "📚 智练通 - 中小学全科学习助手",
                "description": "单元复习 + 智能刷题，助力孩子高效学习",
                "picurl": "",
                "url": H5_BASE_URL + "/"
            }]
            return build_news_response(from_user, to_user, articles)
        
        elif text in ["我的", "个人中心", "profile", "me"]:
            articles = [{
                "title": "👤 我的 - 智练通",
                "description": "查看积分、订单，绑定微信",
                "picurl": "",
                "url": H5_BASE_URL + "/#/profile"
            }]
            return build_news_response(from_user, to_user, articles)
        
        elif text in ["帮助", "help", "?", "？"]:
            return build_text_response(from_user, to_user, get_help_text())
        
        else:
            return build_text_response(from_user, to_user, get_help_text())
    
    return "success"

def handle_bind_request(db, from_user, to_user):
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

@router.post("/admin/create-menu")
async def create_wechat_menu(admin: User = Depends(get_current_admin)):
    if not WECHAT_APPSECRET:
        raise HTTPException(status_code=400, detail="未配置AppSecret")
    
    access_token = await get_access_token()
    
    menu_data = {
        "button": [
            {
                "type": "view",
                "name": "开始学习",
                "url": H5_BASE_URL + "/"
            },
            {
                "type": "view",
                "name": "我的",
                "url": H5_BASE_URL + "/#/profile"
            },
            {
                "type": "click",
                "name": "帮助",
                "key": "HELP"
            }
        ]
    }
    
    url = f"https://api.weixin.qq.com/cgi-bin/menu/create?access_token={access_token}"
    async with httpx.AsyncClient() as client:
        resp = await client.post(url, json=menu_data)
        data = resp.json()
    
    if data.get("errcode") == 0:
        return {"message": "菜单创建成功"}
    else:
        raise HTTPException(status_code=400, detail=f"创建菜单失败: {data.get('errmsg', '未知错误')}")

@router.post("/admin/delete-menu")
async def delete_wechat_menu(admin: User = Depends(get_current_admin)):
    if not WECHAT_APPSECRET:
        raise HTTPException(status_code=400, detail="未配置AppSecret")
    
    access_token = await get_access_token()
    
    url = f"https://api.weixin.qq.com/cgi-bin/menu/delete?access_token={access_token}"
    async with httpx.AsyncClient() as client:
        resp = await client.get(url)
        data = resp.json()
    
    if data.get("errcode") == 0:
        return {"message": "菜单删除成功"}
    else:
        raise HTTPException(status_code=400, detail=f"删除菜单失败: {data.get('errmsg', '未知错误')}")

@router.get("/admin/get-menu")
async def get_wechat_menu(admin: User = Depends(get_current_admin)):
    if not WECHAT_APPSECRET:
        raise HTTPException(status_code=400, detail="未配置AppSecret")
    
    access_token = await get_access_token()
    
    url = f"https://api.weixin.qq.com/cgi-bin/menu/get?access_token={access_token}"
    async with httpx.AsyncClient() as client:
        resp = await client.get(url)
        data = resp.json()
    
    return data
