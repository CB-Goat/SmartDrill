import asyncio
import httpx
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

APPID = "wx6032ec9465fc7483"
APPSECRET = ""
H5_BASE_URL = "https://smartdrill.handy.xin"

async def get_access_token():
    if not APPSECRET:
        print("错误：请先在脚本中配置 APPSECRET")
        return None
    
    url = f"https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid={APPID}&secret={APPSECRET}"
    async with httpx.AsyncClient() as client:
        resp = await client.get(url)
        data = resp.json()
    
    if "access_token" not in data:
        print(f"获取access_token失败: {data.get('errmsg', '未知错误')}")
        return None
    
    return data["access_token"]

async def create_menu():
    access_token = await get_access_token()
    if not access_token:
        return
    
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
        print("菜单创建成功！")
    else:
        print(f"创建菜单失败: {data.get('errmsg', '未知错误')}")
        print(f"错误码: {data.get('errcode')}")

async def get_menu():
    access_token = await get_access_token()
    if not access_token:
        return
    
    url = f"https://api.weixin.qq.com/cgi-bin/menu/get?access_token={access_token}"
    async with httpx.AsyncClient() as client:
        resp = await client.get(url)
        data = resp.json()
    
    print("当前菜单配置:")
    print(data)

async def delete_menu():
    access_token = await get_access_token()
    if not access_token:
        return
    
    url = f"https://api.weixin.qq.com/cgi-bin/menu/delete?access_token={access_token}"
    async with httpx.AsyncClient() as client:
        resp = await client.get(url)
        data = resp.json()
    
    if data.get("errcode") == 0:
        print("菜单删除成功！")
    else:
        print(f"删除菜单失败: {data.get('errmsg', '未知错误')}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法:")
        print("  python create_wechat_menu.py create   创建菜单")
        print("  python create_wechat_menu.py get      查看菜单")
        print("  python create_wechat_menu.py delete   删除菜单")
        sys.exit(1)
    
    action = sys.argv[1]
    
    if action == "create":
        asyncio.run(create_menu())
    elif action == "get":
        asyncio.run(get_menu())
    elif action == "delete":
        asyncio.run(delete_menu())
    else:
        print(f"未知操作: {action}")
