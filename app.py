import streamlit as st
import json
import os
import shutil
import tempfile
import zipfile
import time
import re
import requests
import base64
import glob
import random
from openai import OpenAI
from playwright.sync_api import sync_playwright
import pdfplumber
import docx

# ==========================================
# Streamlit Cloud: cache Playwright browser install
# ==========================================
@st.cache_resource
def _install_playwright_browser():
    import subprocess, sys
    subprocess.run([sys.executable, "-m", "playwright", "install", "chromium"], check=True)
    return True


# ==========================================
# 页面基础配置 (必须放在最前面)
# ==========================================
_install_playwright_browser()

st.set_page_config(page_title="AI NIUMA - AI牛马图文自动化", page_icon="🪄", layout="wide")

# ==========================================
# ????? CSS ?? (UI ??)
# ==========================================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;900&amp;family=Noto+Sans+SC:wght@400;500;700;900&amp;display=swap');

    /* —— 全局暗色主题 —— */
    html, body, [class*="css"], .stApp {
        font-family: 'Inter', 'Noto Sans SC', -apple-system, BlinkMacSystemFont, "Microsoft YaHei", sans-serif;
        background: #020617;
        color: #e2e8f0;
    }

    /* —— 滚动条 —— */
    ::-webkit-scrollbar { width: 6px; }
    ::-webkit-scrollbar-track { background: transparent; }
    ::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.08); border-radius: 3px; }
    ::-webkit-scrollbar-thumb:hover { background: rgba(99, 102, 241, 0.4); }

    /* —— 玻璃面板 —— */
    .glass-card {
        background: rgba(15, 23, 42, 0.65);
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        border: 1px solid rgba(255, 255, 255, 0.06);
        border-radius: 16px;
        box-shadow: 0 20px 50px rgba(0, 0, 0, 0.45);
    }

    /* —— 侧边栏—— */
    [data-testid="stSidebar"] {
        background: rgba(2, 6, 23, 0.9);
        backdrop-filter: blur(24px);
        -webkit-backdrop-filter: blur(24px);
        border-right: 1px solid rgba(255, 255, 255, 0.06);
    }
    [data-testid="stSidebar"] * {
        color: #cbd5e1 !important;
    }
    [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 {
        color: #f1f5f9 !important;
    }

    /* —— 进度条 —— */
    .stProgress > div > div > div > div {
        background: linear-gradient(90deg, #6366f1 0%, #8b5cf6 50%, #a78bfa 100%);
        border-radius: 8px;
    }

    /* —— 按钮 —— */
    .stButton > button {
        border-radius: 10px !important;
        font-weight: 600 !important;
        transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1) !important;
        background: rgba(99, 102, 241, 0.15) !important;
        color: #a5b4fc !important;
        border: 1px solid rgba(99, 102, 241, 0.3) !important;
    }
    .stButton > button:hover {
        background: rgba(99, 102, 241, 0.3) !important;
        border-color: rgba(129, 140, 248, 0.6) !important;
        transform: translateY(-1px);
        box-shadow: 0 8px 24px rgba(99, 102, 241, 0.25);
    }
    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%) !important;
        color: white !important;
        border: none !important;
    }
    .stButton > button[kind="primary"]:hover {
        box-shadow: 0 8px 32px rgba(99, 102, 241, 0.4);
        transform: translateY(-2px);
    }

    /* —— 文件上传区域 —— */
    [data-testid="stFileUploader"] {
        border-radius: 14px !important;
        border: 2px dashed rgba(99, 102, 241, 0.25) !important;
        background: rgba(15, 23, 42, 0.4) !important;
        transition: all 0.3s ease !important;
    }
    [data-testid="stFileUploader"]:hover {
        border-color: rgba(99, 102, 241, 0.6) !important;
        background: rgba(30, 41, 59, 0.6) !important;
        box-shadow: 0 0 30px rgba(99, 102, 241, 0.15);
    }

    /* —— 标题栏及文本 —— */
    h1, h2, h3 {
        color: #f1f5f9 !important;
        font-weight: 700 !important;
        letter-spacing: -0.02em;
    }
    p, span, div, label {
        color: #94a3b8;
    }

    /* —— info / success / warning 提示框 —— */
    [data-testid="stAlert"] {
        background: rgba(15, 23, 42, 0.6) !important;
        backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 255, 255, 0.06) !important;
        border-radius: 12px !important;
    }

    /* —— 表单输入框 —— */
    input, textarea, [data-baseweb="input"] {
        background: rgba(15, 23, 42, 0.5) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        color: #e2e8f0 !important;
        border-radius: 10px !important;
    }
    input:focus, textarea:focus, [data-baseweb="input"]:focus {
        border-color: rgba(99, 102, 241, 0.5) !important;
        box-shadow: 0 0 20px rgba(99, 102, 241, 0.15) !important;
    }

    /* —— 动画 —— */
    @keyframes fadeSlideIn {
        0% { opacity: 0; transform: translateY(16px); }
        100% { opacity: 1; transform: translateY(0); }
    }
    .hero-animate {
        animation: fadeSlideIn 0.7s cubic-bezier(0.16, 1, 0.3, 1) forwards;
    }

    /* —— Hero视频容器 —— */
    .hero-video-wrap video {
        border-radius: 10px;
        pointer-events: none;
        box-shadow: 0 0 30px rgba(99, 102, 241, 0.15);
    }

    /* —— 分割线美化 —— */
    hr, [data-testid="stDivider"] {
        border-color: rgba(255, 255, 255, 0.06) !important;
    }


</style>
""", unsafe_allow_html=True)

LOGO_VIDEO_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logo.mp4")


# ==========================================
# 核心功能模块 (AI 提炼与图文处理)
# ==========================================
SYSTEM_INSTRUCTION = """
你现在是一个顶尖的商业分析师和社交媒体（如小红书、微信公众号）内容策划专家。
你的任务是阅读用户提供的枯燥的官方政策文件，并将其提炼转化为吸引眼球的、结构清晰的、适合生成可视化长图的文案。

提取规则：
1. 语言必须精炼、接地气，把晦涩的官方术语转化为行业痛点解决方案。
2. 封面标题要有冲击力。
3. 将内容划分为几个核心板块。
4. 每个板块提炼出不超过3个要点，包含短标题和解释。
5. 为每个板块提供一个极度精简的英文配图搜索词。搜索词必须与该板块的主题高度契合（例如：工业主题用'factory'，教育用'school'，安全用'security'，农业用'farm'，科技用'technology'）。

你必须以 JSON 格式输出，并且完全遵循以下 JSON 结构：
{
  "cover": {
    "title": "主标题",
    "subtitle": "副标题",
    "policy_name": "政策原名",
    "short_policy_name": "智能缩写的政策简称（极度重要：必须去除所有标点符号，严格控制在25个字以内，语义连贯通顺，不漏关键信息。）",
    "highlights": "一句话核心亮点"
  },
  "pages": [
    {
      "page_number": 1,
      "section_title_black": "大标题的黑色前缀（如：'优化'、'创新'）",
      "section_title_yellow": "大标题的黄色强调（如：'规划管理'、'产权归集'）",
      "section_subtitle": "板块副标题",
      "image_search_keyword": "极度精简的纯英文配图关键词（极度重要：只能是1到2个极其通俗的常见名词，如 'factory', 'city', 'office', 'nature', 'meeting'。严禁使用长句、形容词或复杂词汇，否则会导致图库系统崩溃出默认错图！）",
      "bullet_points": [
        {
          "title": "要点短标题",
          "content": "要点详细解释"
        }
      ]
    }
  ],
  "outro": {
    "brand_name": "@文商旅小圆桌",
    "slogan": "文旅/策划/规划/投资/运营\\n欢迎合作交流"
  }
}
"""

STYLE_PROMPTS = {
    "1": "Professional business corporate style in China, Asian faces if people are included, highly realistic photography, Chinese elements, clear, minimalist, high quality. Theme: ",
    "2": "Apple minimalist style, 3D render, modern Chinese aesthetic, cold tones, sleek, premium, clean white or grey background. Theme: ",
    "3": "Traditional Chinese style, oriental elegance, ink wash painting, vermilion red accents, elegant Chinese architecture. Theme: ",
    "4": "Macaron color palette, glassmorphism, 3D cute style, modern Chinese lifestyle, bright and fresh, soft lighting, vibrant. Theme: ",
    "5": "Cyberpunk style, futuristic technology, neon lights, cyan and purple color palette, glowing holographic interface, high-tech vibe, highly detailed. Theme: ",
    "6": "Xiaohongshu lifestyle photography, aesthetic, warm tones, collage style, highly detailed, photorealistic, trendy, young vibe. Theme: ",
    "7": "Pastoral dopamine style, vibrant colors, nature inspired, sunny, cute, 3D render, pop mart style, colorful, happy mood. Theme: "
}

def read_document(file_obj, file_name):
    ext = file_name.lower().split('.')[-1]
    text = ""
    try:
        if ext == 'pdf':
            with pdfplumber.open(file_obj) as pdf:
                for page in pdf.pages:
                    extracted = page.extract_text()
                    if extracted: text += extracted + "\n"
        elif ext in ['doc', 'docx']:
            doc = docx.Document(file_obj)
            for para in doc.paragraphs:
                text += para.text + "\n"
        else: return None
        return text
    except Exception as e:
        st.error(f"读取文件出错: {e}")
        return None

def extract_policy_data(text, api_key):
    client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com")
    try:
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": SYSTEM_INSTRUCTION},
                {"role": "user", "content": f"请提取信息：\n\n{text[:15000]}"} 
            ],
            response_format={'type': 'json_object'},
            temperature=0.2
        )
        return json.loads(response.choices[0].message.content)
    except Exception as e:
        st.error(f"文本提炼 API 调用失败: {e}")
        return None

# --- 绘画引擎 1：OpenAI DALL·E 3 ---
def generate_ai_image_openai(prompt, api_key):
    try:
        client = OpenAI(api_key=api_key) 
        response = client.images.generate(
            model="dall-e-3",
            prompt=prompt,
            size="1024x1024",
            quality="standard",
            n=1,
        )
        return response.data[0].url
    except Exception as e:
        st.error(f"DALL·E 3 绘画失败: {e}")
        return None

# --- 绘画引擎 2：阿里云通义万相 2.7 ---
def generate_ai_image_aliyun(prompt, api_key):
    try:
        import dashscope
        from dashscope.aigc.image_generation import ImageGeneration
        from dashscope.api_entities.dashscope_response import Message
        
        dashscope.base_http_api_url = 'https://dashscope.aliyuncs.com/api/v1'
        message = Message(role="user", content=[{"text": prompt}])
        
        # 1. 提交任务
        rsp = ImageGeneration.call(
            model='wan2.7-image',
            api_key=api_key,
            messages=[message],
            enable_sequential=True,
            n=1,
            size="1024*1024" 
        )
        
        if rsp.status_code == 200:
            if 'task_id' in rsp.output:
                task_id = rsp.output.task_id
                for _ in range(20):
                    time.sleep(3)
                    fetch_rsp = ImageGeneration.fetch(task_id, api_key=api_key)
                    if fetch_rsp.status_code == 200:
                        status = fetch_rsp.output.task_status
                        if status == 'SUCCEEDED':
                            return fetch_rsp.output.results[0].url
                        elif status == 'FAILED':
                            st.error(f"万相生成失败: {fetch_rsp.output.message}")
                            return None
                    else:
                        st.error(f"获取任务状态失败: {fetch_rsp.message}")
                        return None
                st.error("万相生成超时，请稍后重试。")
                return None
            elif 'results' in rsp.output:
                return rsp.output.results[0].url
        else:
            st.error(f"阿里云万相 API 报错: Error {rsp.code} - {rsp.message}")
            return None
            
    except ImportError:
        st.error("缺少 dashscope 库，请先在命令行运行：pip install dashscope")
        return None
    except Exception as e:
        st.error(f"调用万相绘图发生异常: {e}")
        return None

def get_base64_image(image_source, source_type="url"):
    try:
        if source_type == "url":
            response = requests.get(image_source, timeout=15)
            content = response.content
            mime_type = response.headers.get('Content-Type', 'image/jpeg')
        else:
            content = image_source.read()
            mime_type = image_source.type
        b64_encoded = base64.b64encode(content).decode('utf-8')
        return f"data:{mime_type};base64,{b64_encoded}"
    except Exception as e:
        print(f"Base64 图片处理失败: {e}")
        return None

def get_loremflickr_url(keyword, index):
    """【极强过滤机制】确保关键词不超载，避免出现默认黑猫图"""
    lock_id = random.randint(1, 999999) + index
    
    # 如果含有中文或为空，直接降级为 Picsum 绝对随机高清图
    if not keyword or re.search(r'[\u4e00-\u9fa5]', keyword):
        return f"https://picsum.photos/seed/{lock_id}/800/500"
    
    # 1. 过滤所有非字母字符，只保留英文和空格
    clean_kw = re.sub(r'[^a-zA-Z\s]', ' ', keyword).strip()
    
    # 2. 将字符串拆分为单词列表
    words = [w for w in clean_kw.split() if w]
    
    # 3. 极度精简：只取前 2 个单词！防止复杂短语导致 LoremFlickr 找不到图而报错
    final_words = words[:2]
    
    # 如果过滤后没词了，依然降级为 Picsum
    if not final_words:
        return f"https://picsum.photos/seed/{lock_id}/800/500"
        
    kw_formatted = ','.join(final_words)
    return f"https://loremflickr.com/800/500/{kw_formatted}?lock={lock_id}"

def get_header_text(data):
    cover = data.get("cover", {})
    header = cover.get("short_policy_name")
    if not header: header = cover.get('policy_name') or cover.get('title') or "最新政策深度解读"
    header = re.sub(r'[^\w\u4e00-\u9fa5]', '', header) 
    if len(header) > 25: header = header[:25]
    return header

# ==========================================
# 4套多风格模板渲染引擎
# ==========================================
def render_style_default(data):
    header_text = get_header_text(data)
    html_content = f"""<!DOCTYPE html><html lang="zh-CN"><head><meta charset="UTF-8"><script src="https://cdn.tailwindcss.com"></script><style>body {{ font-family: 'Noto Sans SC', sans-serif; background-color: #f3f4f6; padding: 2rem; display: flex; flex-direction: column; align-items: center; gap: 2rem; }}.card {{ width: 800px; height: 1422px; background-color: white; box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1); overflow: hidden; position: relative; display: flex; flex-direction: column; }}.cover-bg {{ background: linear-gradient(135deg, #710000 0%, #4a0000 100%); color: white; }}.yellow-circle {{ width: 110px; height: 110px; background-color: #ffb800; border-radius: 50%; position: relative; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1); }}</style></head><body>"""
    cover = data.get("cover", {})
    html_content += f"""
        <div class="card cover-bg flex flex-col justify-center px-16 text-center relative">
            <div class="absolute inset-0 opacity-20 bg-[radial-gradient(ellipse_at_center,_var(--tw-gradient-stops))] from-white via-transparent to-transparent pointer-events-none"></div>
            <p class="text-right text-lg text-gray-200 mb-6 tracking-widest">—— {cover.get('subtitle', '')}</p>
            <h1 class="text-7xl font-black mb-8 leading-snug tracking-wider">{cover.get('title', '')}</h1>
            <div class="flex justify-center items-center mb-16 mt-4"><span class="text-4xl text-[#ffb800] font-black tracking-widest bg-black/20 px-6 py-3 rounded">{cover.get('policy_name', '')}</span></div>
            <div class="mt-20 text-center"><p class="text-5xl font-black italic tracking-widest text-white drop-shadow-lg">{cover.get('highlights', '')}</p></div>
            <div class="absolute bottom-12 left-0 w-full text-center"><p class="text-lg text-gray-300 tracking-widest">{data.get('outro', {}).get('brand_name', '')}</p></div>
        </div>
    """
    for page in data.get("pages", []):
        img_url = page.get('resolved_image_url')
        html_content += f"""
        <div class="card flex flex-col relative bg-white">
            <div class="w-full text-center py-6 border-b border-gray-200 mt-4 px-12 overflow-hidden">
                <span class="tracking-[0.8em] text-gray-400 text-sm ml-[0.8em] whitespace-nowrap block w-full">{header_text}</span>
            </div>
            <div class="flex items-start px-14 mt-16 mb-12">
                <div class="relative flex-shrink-0 mr-6 mt-1">
                    <div class="yellow-circle"><span class="text-[5.5rem] font-black italic absolute left-3 top-[-0.2rem] text-black leading-none">{page.get('page_number')}</span><span class="text-xl font-black italic absolute right-2 bottom-3 text-black leading-none">板块</span></div>
                </div>
                <div class="flex flex-col justify-center mt-[-6px]">
                    <h2 class="text-[4.2rem] font-black tracking-wide leading-tight mb-2"><span class="text-black">{page.get('section_title_black', '')}</span><span class="text-[#ffb800]">{page.get('section_title_yellow', '')}</span></h2>
                    <h3 class="text-[3.8rem] font-black tracking-wide text-black leading-tight">{page.get('section_subtitle')}</h3>
                </div>
            </div>
            <div class="px-16 flex-grow space-y-8">
        """
        for point in page.get("bullet_points", []):
            html_content += f"""<div class="flex items-start"><div class="w-3 h-3 bg-black rounded-full mt-2.5 mr-5 flex-shrink-0"></div><div class="text-xl leading-relaxed text-gray-600 tracking-wide"><span class="font-black text-black">{point.get('title')}：</span>{point.get('content')}</div></div>"""
        html_content += f"""
            </div>
            <div class="px-14 mt-12 mb-10 h-[400px]">
               <img src="{img_url}" class="w-full h-full object-cover rounded shadow-sm">
            </div>
            <div class="px-14 pb-10 flex justify-between items-center text-gray-400 text-sm mt-auto"><span class="tracking-widest">{data.get('outro', {}).get('brand_name', '')}</span><span class="tracking-widest">以上为部分要点梳理，具体政策内容请以正式发布的文件为准。</span></div>
        </div>
        """
    outro = data.get("outro", {})
    html_content += f"""<div class="card cover-bg flex flex-col justify-center items-center text-center px-12 relative"><div class="absolute inset-0 opacity-20 bg-[radial-gradient(ellipse_at_center,_var(--tw-gradient-stops))] from-white via-transparent to-transparent pointer-events-none"></div><p class="text-2xl mb-8 tracking-widest text-gray-300">{outro.get('brand_name', '')}</p><p class="text-5xl font-black tracking-widest whitespace-pre-line leading-relaxed drop-shadow-lg">{outro.get('slogan', '')}</p></div></body></html>"""
    return html_content

def render_style_apple(data):
    header_text = get_header_text(data)
    html_content = f"""<!DOCTYPE html><html lang="zh-CN"><head><meta charset="UTF-8"><script src="https://cdn.tailwindcss.com"></script><style>body {{ font-family: -apple-system, BlinkMacSystemFont, "SF Pro SC", "Helvetica Neue", Helvetica, Arial, sans-serif; background-color: #000; padding: 2rem; display: flex; flex-direction: column; align-items: center; gap: 2rem; }}.card {{ width: 800px; height: 1422px; background-color: #fbfbfd; overflow: hidden; position: relative; display: flex; flex-direction: column; }}</style></head><body>"""
    cover = data.get("cover", {})
    html_content += f"""
        <div class="card flex flex-col justify-center items-center px-20 text-center bg-white">
            <h1 class="text-6xl font-bold tracking-tight text-[#1d1d1f] mb-6">{cover.get('title', '')}</h1>
            <p class="text-2xl text-[#86868b] font-medium tracking-wide mb-16">{cover.get('subtitle', '')}</p>
            <div class="bg-[#1d1d1f] text-white rounded-full px-8 py-3 text-xl font-semibold mb-12">{cover.get('policy_name', '')}</div>
            <p class="text-4xl font-semibold bg-clip-text text-transparent bg-gradient-to-r from-blue-500 to-purple-500">{cover.get('highlights', '')}</p>
            <div class="absolute bottom-16 text-[#86868b] font-medium tracking-widest">{data.get('outro', {}).get('brand_name', '')}</div>
        </div>
    """
    for page in data.get("pages", []):
        img_url = page.get('resolved_image_url')
        html_content += f"""
        <div class="card flex flex-col relative">
            <div class="w-full text-center py-8 border-b border-[#d2d2d7] mt-8 px-12 overflow-hidden"><span class="tracking-[0.4em] text-[#86868b] text-xs font-semibold uppercase whitespace-nowrap block w-full">{header_text}</span></div>
            <div class="px-20 mt-20 mb-16">
                <p class="text-[#0066cc] font-semibold text-2xl mb-4">Section {page.get('page_number')}</p>
                <h2 class="text-6xl font-bold tracking-tight text-[#1d1d1f] leading-tight mb-4">{page.get('section_title_black', '')}{page.get('section_title_yellow', '')}</h2>
                <h3 class="text-3xl font-semibold text-[#86868b]">{page.get('section_subtitle')}</h3>
            </div>
            <div class="px-20 flex-grow space-y-10">
        """
        for point in page.get("bullet_points", []):
            html_content += f"""<div class="border-t border-[#d2d2d7] pt-6"><h4 class="text-2xl font-bold text-[#1d1d1f] mb-3">{point.get('title')}</h4><p class="text-xl leading-relaxed text-[#515154]">{point.get('content')}</p></div>"""
        html_content += f"""
            </div>
            <div class="px-20 mt-12 mb-16 h-[380px]"><img src="{img_url}" class="w-full h-full object-cover rounded-3xl"></div>
        </div>
        """
    outro = data.get("outro", {})
    html_content += f"""<div class="card flex flex-col justify-center items-center text-center px-20 bg-[#1d1d1f]"><p class="text-4xl font-semibold text-white tracking-wide mb-8">{outro.get('brand_name', '')}</p><p class="text-2xl text-[#86868b] font-medium leading-relaxed whitespace-pre-line">{outro.get('slogan', '')}</p></div></body></html>"""
    return html_content

def render_style_guofeng(data):
    header_text = get_header_text(data) 
    html_content = f"""<!DOCTYPE html><html lang="zh-CN"><head><meta charset="UTF-8"><script src="https://cdn.tailwindcss.com"></script><link href="https://fonts.googleapis.com/css2?family=Noto+Serif+SC:wght@400;700;900&display=swap" rel="stylesheet"><style>body {{ font-family: 'Noto Serif SC', serif; background-color: #e5e5e5; padding: 2rem; display: flex; flex-direction: column; align-items: center; gap: 2rem; }}.card {{ width: 800px; height: 1422px; background-color: #f7f4ed; overflow: hidden; position: relative; display: flex; flex-direction: column; border: 1px solid #d5c8b5; }}.red-stamp {{ border: 2px solid #8c222c; color: #8c222c; padding: 0.5rem 1rem; font-weight: bold; }}</style></head><body>"""
    cover = data.get("cover", {})
    html_content += f"""
        <div class="card p-4 relative">
            <div class="w-full h-full border-[12px] border-double border-[#d5c8b5] flex flex-col justify-center items-center px-16 text-center relative">
                <div class="absolute top-16 right-12 text-[#8c222c] text-xl font-bold tracking-widest" style="writing-mode: vertical-rl;">{cover.get('subtitle', '')}</div>
                <h1 class="text-7xl font-black text-[#8c222c] mb-12 leading-snug tracking-widest">{cover.get('title', '')}</h1>
                <div class="red-stamp text-2xl tracking-widest mb-20">{cover.get('policy_name', '')}</div>
                <p class="text-4xl font-bold text-[#333] tracking-widest bg-white/50 py-6 px-10 border border-[#d5c8b5] shadow-sm z-10">{cover.get('highlights', '')}</p>
                <div class="absolute bottom-16 text-[#666] tracking-widest"><span class="red-stamp text-sm mr-3">印</span>{data.get('outro', {}).get('brand_name', '')}</div>
            </div>
        </div>
    """
    for page in data.get("pages", []):
        img_url = page.get('resolved_image_url')
        html_content += f"""
        <div class="card flex flex-col relative">
            <div class="w-full text-center py-6 border-b-2 border-double border-[#8c222c] mt-8 mx-12 relative px-4 overflow-hidden" style="width: calc(100% - 6rem);"><span class="tracking-[0.4em] text-[#8c222c] font-bold text-lg whitespace-nowrap block w-full">{header_text}</span></div>
            <div class="px-16 mt-16 mb-12 flex items-center">
                <div class="text-[#8c222c] text-[6rem] leading-none font-black mr-8 border-r-4 border-[#8c222c] pr-8">{page.get('page_number')}</div>
                <div class="flex flex-col"><h2 class="text-[3.5rem] font-black text-[#333] tracking-wider mb-4">{page.get('section_title_black', '')}<span class="text-[#8c222c]">{page.get('section_title_yellow', '')}</span></h2><h3 class="text-3xl font-bold text-[#666] tracking-widest">{page.get('section_subtitle')}</h3></div>
            </div>
            <div class="px-16 flex-grow space-y-8">
        """
        for point in page.get("bullet_points", []):
            html_content += f"""<div class="flex items-start"><div class="text-[#8c222c] text-2xl mr-4 mt-1">◆</div><div class="text-xl leading-loose text-[#444] tracking-wide text-justify"><span class="font-bold text-[#8c222c] text-2xl border-b-2 border-[#8c222c] pb-1 mr-3">{point.get('title')}</span>{point.get('content')}</div></div>"""
        html_content += f"""
            </div>
            <div class="px-12 mt-12 mb-10 h-[380px] p-2 border border-[#d5c8b5] mx-12 bg-white"><img src="{img_url}" class="w-full h-full object-cover grayscale opacity-90"></div>
        </div>
        """
    outro = data.get("outro", {})
    html_content += f"""<div class="card flex flex-col justify-center items-center text-center px-16 relative"><div class="w-[400px] h-[400px] rounded-full border border-[#d5c8b5] absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 opacity-30 pointer-events-none"></div><h1 class="text-[4rem] font-black text-[#8c222c] mb-12 tracking-[0.3em]" style="writing-mode: vertical-rl;">{outro.get('brand_name', '')}</h1><p class="text-2xl text-[#333] tracking-widest leading-loose bg-white/60 py-6 px-10 border border-[#d5c8b5]">{outro.get('slogan', '')}</p></div></body></html>"""
    return html_content

def render_style_fresh(data):
    header_text = get_header_text(data)
    html_content = f"""<!DOCTYPE html><html lang="zh-CN"><head><meta charset="UTF-8"><script src="https://cdn.tailwindcss.com"></script><style>body {{ font-family: 'PingFang SC', 'Microsoft YaHei', sans-serif; background-color: #f3f4f6; padding: 2rem; display: flex; flex-direction: column; align-items: center; gap: 2rem; }}.card {{ width: 800px; height: 1422px; background: linear-gradient(135deg, #fff5f5 0%, #f0f9ff 100%); overflow: hidden; position: relative; display: flex; flex-direction: column; }}.glass-panel {{ background: rgba(255, 255, 255, 0.65); backdrop-filter: blur(16px); border: 1px solid rgba(255,255,255,0.8); border-radius: 2rem; box-shadow: 0 10px 30px rgba(0,0,0,0.05); }}</style></head><body>"""
    cover = data.get("cover", {})
    html_content += f"""
        <div class="card p-8 relative">
            <div class="absolute top-[-100px] right-[-100px] w-96 h-96 bg-pink-200 rounded-full mix-blend-multiply filter blur-3xl opacity-50 pointer-events-none"></div>
            <div class="absolute bottom-[-100px] left-[-100px] w-96 h-96 bg-blue-200 rounded-full mix-blend-multiply filter blur-3xl opacity-50 pointer-events-none"></div>
            <div class="glass-panel flex-grow flex flex-col justify-center items-center px-12 text-center z-10 relative">
                <span class="bg-white/80 text-pink-500 px-6 py-2 rounded-full text-xl font-bold mb-10 shadow-sm">✨ {cover.get('subtitle', '')}</span>
                <h1 class="text-7xl font-black text-gray-800 mb-10 leading-snug">{cover.get('title', '')}</h1>
                <div class="text-2xl text-gray-500 font-bold mb-20 px-8 py-3 bg-white/50 rounded-2xl">{cover.get('policy_name', '')}</div>
                <div class="bg-gradient-to-r from-pink-400 to-purple-400 text-white text-[2.5rem] font-bold py-8 px-12 rounded-[2rem] shadow-lg transform -rotate-2">{cover.get('highlights', '')}</div>
                <div class="absolute bottom-12 flex items-center bg-white/80 px-6 py-3 rounded-full shadow-sm"><div class="w-8 h-8 rounded-full bg-gradient-to-r from-pink-300 to-blue-300 mr-3"></div><span class="text-gray-500 font-bold tracking-wider">{data.get('outro', {}).get('brand_name', '')}</span></div>
            </div>
        </div>
    """
    for page in data.get("pages", []):
        img_url = page.get('resolved_image_url')
        html_content += f"""
        <div class="card p-8 relative">
            <div class="glass-panel flex-grow flex flex-col relative z-10 overflow-hidden">
                <div class="px-12 pt-12 pb-8 flex items-center justify-between">
                    <div class="flex items-center"><div class="w-20 h-20 bg-gradient-to-br from-pink-300 to-blue-300 text-white rounded-[1.5rem] shadow-md flex items-center justify-center text-4xl font-black mr-6">{page.get('page_number')}</div><h2 class="text-5xl font-black text-gray-800 tracking-wide">{page.get('section_title_black', '')}<span class="text-pink-400">{page.get('section_title_yellow', '')}</span></h2></div>
                    <span class="bg-blue-50 text-blue-400 px-5 py-2 rounded-full text-md font-bold shadow-sm">Hot 🔥</span>
                </div>
                <h3 class="px-12 text-3xl font-bold text-gray-500 mb-10 border-l-[6px] border-pink-400 ml-12 pl-6">{page.get('section_subtitle')}</h3>
                <div class="px-12 flex-grow space-y-6">
        """
        for point in page.get("bullet_points", []):
            html_content += f"""<div class="bg-white/80 p-6 rounded-[1.5rem] shadow-sm border border-white"><h4 class="text-[1.6rem] font-bold text-gray-800 mb-3 flex items-center"><span class="text-pink-400 mr-3 text-2xl">💡</span> {point.get('title')}</h4><p class="text-[1.3rem] text-gray-600 leading-relaxed ml-10">{point.get('content')}</p></div>"""
        html_content += f"""
                </div>
                <div class="px-8 pb-8 pt-6"><img src="{img_url}" class="w-full h-[360px] object-cover rounded-[2rem] shadow-md border-4 border-white"></div>
            </div>
        </div>
        """
    outro = data.get("outro", {})
    html_content += f"""<div class="card p-8 relative"><div class="glass-panel flex-grow flex flex-col justify-center items-center text-center px-16 z-10"><div class="w-32 h-32 bg-white rounded-[2rem] shadow-lg flex items-center justify-center text-6xl mb-12 transform rotate-12">🌸</div><h1 class="text-5xl font-black text-gray-800 mb-8 tracking-wider">{outro.get('brand_name', '')}</h1><p class="text-[1.8rem] text-gray-500 font-bold leading-relaxed bg-white/70 py-8 px-12 rounded-[2rem] shadow-sm whitespace-pre-line">{outro.get('slogan', '')}</p></div></div></body></html>"""
    return html_content

def render_style_tech(data):
    header_text = get_header_text(data)
    html_content = f"""<!DOCTYPE html><html lang="zh-CN"><head><meta charset="UTF-8"><script src="https://cdn.tailwindcss.com"></script><style>body {{ font-family: 'PingFang SC', sans-serif; background-color: #111827; padding: 2rem; display: flex; flex-direction: column; align-items: center; gap: 2rem; }}.card {{ width: 800px; height: 1422px; background-color: #030712; background-image: radial-gradient(rgba(6, 182, 212, 0.1) 2px, transparent 2px); background-size: 40px 40px; overflow: hidden; position: relative; display: flex; flex-direction: column; border: 1px solid rgba(6,182,212,0.4); box-shadow: 0 0 25px rgba(6,182,212,0.15); }}.glow-text {{ text-shadow: 0 0 15px rgba(6,182,212,0.8); }}.cyber-box {{ border-left: 4px solid #06b6d4; background: linear-gradient(90deg, rgba(6,182,212,0.1) 0%, transparent 100%); }}</style></head><body>"""
    cover = data.get("cover", {})
    html_content += f"""
        <div class="card flex flex-col justify-center px-16 relative">
            <div class="absolute top-0 left-0 w-full h-2 bg-gradient-to-r from-cyan-400 to-purple-600"></div>
            <div class="absolute bottom-[-100px] right-[-100px] w-96 h-96 bg-purple-600/20 rounded-full filter blur-[100px]"></div>
            <p class="text-cyan-400 text-2xl font-mono tracking-widest mb-6 uppercase">/// {cover.get('subtitle', '')}</p>
            <h1 class="text-7xl font-black text-white mb-12 leading-snug tracking-wider glow-text">{cover.get('title', '')}</h1>
            <div class="inline-block mb-16"><span class="text-4xl text-purple-400 font-bold tracking-widest border border-purple-500/50 bg-purple-500/10 px-8 py-4 backdrop-blur-sm">{cover.get('policy_name', '')}</span></div>
            <div class="mt-8"><p class="text-[2.5rem] leading-snug font-bold tracking-widest text-transparent bg-clip-text bg-gradient-to-r from-cyan-300 to-white">{cover.get('highlights', '')}</p></div>
            <div class="absolute bottom-16 left-16 flex items-center"><div class="w-4 h-4 bg-cyan-400 rounded-full mr-4 animate-pulse"></div><p class="text-xl text-cyan-500/70 tracking-widest font-mono">SYS.AUTHOR: {data.get('outro', {}).get('brand_name', '')}</p></div>
        </div>
    """
    for page in data.get("pages", []):
        img_url = page.get('resolved_image_url')
        html_content += f"""
        <div class="card flex flex-col relative">
            <div class="absolute top-0 left-0 w-full h-1 bg-cyan-500/40 shadow-[0_0_10px_#06b6d4]"></div>
            <div class="w-full py-8 border-b border-cyan-500/30 mt-4 px-12 flex justify-between items-center"><span class="text-cyan-500/60 font-mono text-lg tracking-widest">DATA_NODE: {header_text}</span><span class="text-purple-400/60 font-mono text-lg font-bold">SEC_{page.get('page_number')}</span></div>
            <div class="flex items-start px-14 mt-16 mb-12">
                <div class="text-[6.5rem] font-black text-transparent bg-clip-text bg-gradient-to-b from-cyan-400 to-blue-600 leading-none mr-6 glow-text">{page.get('page_number')}</div>
                <div class="flex flex-col justify-center mt-2">
                    <h2 class="text-[3.2rem] font-black tracking-wide leading-tight mb-3 text-white">{page.get('section_title_black', '')}<span class="text-cyan-400 ml-2">{page.get('section_title_yellow', '')}</span></h2>
                    <h3 class="text-3xl font-bold tracking-wider text-purple-400">{page.get('section_subtitle')}</h3>
                </div>
            </div>
            <div class="px-16 flex-grow space-y-8 z-10">
        """
        for point in page.get("bullet_points", []):
            html_content += f"""<div class="cyber-box p-6"><h4 class="text-[1.6rem] font-bold text-cyan-300 mb-3 flex items-center"><span class="mr-3 text-2xl font-mono">>_</span>{point.get('title')}</h4><p class="text-[1.3rem] text-gray-300 leading-relaxed ml-10">{point.get('content')}</p></div>"""
        html_content += f"""
            </div>
            <div class="px-14 mt-10 mb-12 h-[380px] relative">
                <div class="absolute inset-x-14 inset-y-0 border-2 border-cyan-500/50 z-20 pointer-events-none shadow-[inset_0_0_20px_rgba(6,182,212,0.3)]"></div>
                <div class="absolute top-0 left-14 w-8 h-8 border-t-4 border-l-4 border-cyan-400 z-30 pointer-events-none"></div>
                <div class="absolute bottom-0 right-14 w-8 h-8 border-b-4 border-r-4 border-cyan-400 z-30 pointer-events-none"></div>
                <img src="{img_url}" class="w-full h-full object-cover grayscale brightness-110 contrast-125 filter mix-blend-luminosity opacity-70">
            </div>
        </div>
        """
    outro = data.get("outro", {})
    html_content += f"""<div class="card flex flex-col justify-center items-center text-center px-16 relative"><div class="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-[600px] h-[600px] bg-cyan-600/10 rounded-full filter blur-[100px] pointer-events-none"></div><p class="text-4xl text-cyan-400 font-mono tracking-widest mb-12">> {outro.get('brand_name', '')} _</p><h1 class="text-5xl font-black text-transparent bg-clip-text bg-gradient-to-r from-white to-gray-400 tracking-widest leading-relaxed whitespace-pre-line">{outro.get('slogan', '')}</h1></div></body></html>"""
    return html_content

def render_style_xiaohongshu(data):
    header_text = get_header_text(data)
    html_content = f"""<!DOCTYPE html><html lang="zh-CN"><head><meta charset="UTF-8"><script src="https://cdn.tailwindcss.com"></script><style>body {{ font-family: 'PingFang SC', sans-serif; background-color: #f8f9fa; padding: 2rem; display: flex; flex-direction: column; align-items: center; gap: 2rem; }}.card {{ width: 800px; height: 1422px; background-color: #faf9f7; background-image: url('data:image/svg+xml;utf8,<svg width="100" height="100" xmlns="http://www.w3.org/2000/svg"><rect width="100" height="100" fill="none"/><circle cx="50" cy="50" r="1" fill="%23e5e5e5"/></svg>'); overflow: hidden; position: relative; display: flex; flex-direction: column; border-radius: 2.5rem; box-shadow: 0 20px 40px rgba(0,0,0,0.06); }}.polaroid {{ background: white; padding: 1.5rem 1.5rem 4rem 1.5rem; box-shadow: 0 10px 25px rgba(0,0,0,0.08); transform: rotate(-2deg); }}.tape {{ position: absolute; top: -15px; left: 50%; transform: translateX(-50%) rotate(-3deg); width: 120px; height: 35px; background-color: rgba(255, 255, 255, 0.6); backdrop-filter: blur(4px); box-shadow: 0 2px 5px rgba(0,0,0,0.05); }}</style></head><body>"""
    cover = data.get("cover", {})
    html_content += f"""
        <div class="card flex flex-col justify-center px-14 relative bg-[#fffdfa]">
            <div class="absolute top-10 right-10 text-6xl opacity-30 transform rotate-12">✨</div>
            <div class="absolute bottom-32 left-10 text-8xl opacity-20 transform -rotate-12">🌿</div>
            <p class="text-orange-500 text-2xl font-bold tracking-widest mb-6 px-6 py-2 bg-orange-100 rounded-full inline-block self-start"># {cover.get('subtitle', '')}</p>
            <h1 class="text-7xl font-black text-gray-800 mb-10 leading-tight z-10"><span class="bg-gradient-to-r from-orange-200 to-yellow-200 bg-[length:100%_40%] bg-no-repeat bg-bottom">{cover.get('title', '')}</span></h1>
            <div class="flex items-center mb-16"><span class="text-3xl text-gray-600 font-bold bg-white px-8 py-4 rounded-2xl shadow-sm border border-gray-100">{cover.get('policy_name', '')}</span></div>
            <div class="mt-8 bg-orange-400 text-white p-10 rounded-[2rem] transform rotate-1 shadow-lg"><p class="text-[2.2rem] leading-snug font-bold tracking-wider">{cover.get('highlights', '')}</p></div>
            <div class="absolute bottom-16 w-full text-center left-0"><p class="text-xl text-gray-400 font-bold tracking-widest">— {data.get('outro', {}).get('brand_name', '')} —</p></div>
        </div>
    """
    for page in data.get("pages", []):
        img_url = page.get('resolved_image_url')
        html_content += f"""
        <div class="card flex flex-col relative">
            <div class="w-full py-6 mt-6 px-12 flex justify-between items-center"><span class="text-gray-400 font-bold text-lg tracking-widest bg-gray-100 px-5 py-2 rounded-full">{header_text}</span><span class="text-orange-400 text-2xl font-black bg-orange-100 w-12 h-12 flex items-center justify-center rounded-full shadow-sm">{page.get('page_number')}</span></div>
            
            <div class="px-14 mt-8 h-[420px] relative z-10">
                <div class="polaroid relative">
                    <div class="tape"></div>
                    <img src="{img_url}" class="w-full h-full object-cover">
                </div>
            </div>

            <div class="px-14 mt-16 mb-8">
                <h2 class="text-[3rem] font-black tracking-wide leading-tight mb-4 text-gray-800">{page.get('section_title_black', '')}<span class="text-orange-500 ml-2">{page.get('section_title_yellow', '')}</span></h2>
                <h3 class="text-2xl font-bold tracking-wider text-gray-500 bg-gray-100 inline-block px-4 py-1 rounded-lg">{page.get('section_subtitle')}</h3>
            </div>
            
            <div class="px-14 flex-grow space-y-6 z-10">
        """
        for point in page.get("bullet_points", []):
            html_content += f"""<div class="bg-white p-6 rounded-3xl shadow-[0_5px_15px_rgba(0,0,0,0.03)] border border-gray-50"><h4 class="text-[1.5rem] font-bold text-gray-800 mb-2 flex items-center"><span class="text-orange-400 mr-2">📌</span>{point.get('title')}</h4><p class="text-[1.25rem] text-gray-600 leading-relaxed ml-8">{point.get('content')}</p></div>"""
        html_content += f"""
            </div>
        </div>
        """
    outro = data.get("outro", {})
    html_content += f"""<div class="card flex flex-col justify-center items-center text-center px-16 relative bg-[#fffdfa]"><div class="text-8xl mb-10 transform -rotate-12 drop-shadow-md">💌</div><p class="text-4xl text-gray-800 font-black tracking-widest mb-10">{outro.get('brand_name', '')}</p><div class="bg-orange-100 p-10 rounded-[3rem]"><h1 class="text-4xl font-bold text-orange-600 tracking-widest leading-relaxed whitespace-pre-line">{outro.get('slogan', '')}</h1></div></div></body></html>"""
    return html_content

def render_style_dopamine(data):
    header_text = get_header_text(data)
    html_content = f"""<!DOCTYPE html><html lang="zh-CN"><head><meta charset="UTF-8"><script src="https://cdn.tailwindcss.com"></script><style>body {{ font-family: 'PingFang SC', 'Comic Sans MS', sans-serif; background-color: #fdf2f8; padding: 2rem; display: flex; flex-direction: column; align-items: center; gap: 2rem; }}.card {{ width: 800px; height: 1422px; background: linear-gradient(135deg, #d9f99d 0%, #a7f3d0 100%); overflow: hidden; position: relative; display: flex; flex-direction: column; border-radius: 3rem; border: 8px solid #34d399; box-shadow: 15px 15px 0px #10b981; }}.bubble {{ background: white; border: 4px solid #10b981; border-radius: 2rem; box-shadow: 8px 8px 0px #34d399; }}</style></head><body>"""
    cover = data.get("cover", {})
    html_content += f"""
        <div class="card flex flex-col justify-center px-14 relative">
            <div class="absolute top-10 left-10 text-8xl">🌻</div>
            <div class="absolute top-20 right-10 text-8xl">☁️</div>
            <div class="absolute bottom-20 right-16 text-8xl">🦋</div>
            <div class="bubble px-8 py-4 inline-block self-start mb-8 transform -rotate-2"><p class="text-pink-500 text-2xl font-black tracking-widest uppercase">✨ {cover.get('subtitle', '')} ✨</p></div>
            <div class="bubble p-10 mb-10 transform rotate-1"><h1 class="text-[4.5rem] font-black text-gray-800 leading-snug">{cover.get('title', '')}</h1></div>
            <div class="mb-16 self-start bg-pink-400 text-white px-8 py-4 rounded-full font-black text-3xl border-4 border-pink-500 shadow-[6px_6px_0px_#be185d] transform -rotate-1">{cover.get('policy_name', '')}</div>
            <div class="bg-yellow-300 border-4 border-yellow-400 p-8 rounded-3xl shadow-[8px_8px_0px_#eab308] transform rotate-2"><p class="text-[2.2rem] leading-snug font-black text-gray-800">{cover.get('highlights', '')}</p></div>
            <div class="absolute bottom-12 w-full text-center left-0"><p class="text-2xl text-emerald-700 font-black tracking-widest bg-emerald-100 inline-block px-8 py-3 rounded-full border-4 border-emerald-300">👋 {data.get('outro', {}).get('brand_name', '')}</p></div>
        </div>
    """
    for page in data.get("pages", []):
        img_url = page.get('resolved_image_url')
        html_content += f"""
        <div class="card flex flex-col relative bg-emerald-50">
            <div class="w-full py-8 px-12 flex justify-between items-center"><span class="text-emerald-700 font-black text-xl tracking-widest bg-emerald-200 px-6 py-2 rounded-full border-2 border-emerald-400">{header_text}</span><div class="text-white text-4xl font-black bg-pink-500 w-16 h-16 flex items-center justify-center rounded-full border-4 border-pink-600 shadow-[4px_4px_0px_#be185d] transform rotate-12">{page.get('page_number')}</div></div>
            
            <div class="px-12 mt-6 mb-8 flex flex-col">
                <h2 class="text-[3.5rem] font-black tracking-wide leading-tight mb-4 text-gray-800 bubble px-8 py-6 transform -rotate-1">{page.get('section_title_black', '')}<span class="text-pink-500 ml-2">{page.get('section_title_yellow', '')}</span></h2>
                <h3 class="text-2xl font-black tracking-wider text-white bg-emerald-500 inline-block self-start px-6 py-2 rounded-full border-2 border-emerald-600 transform rotate-1">{page.get('section_subtitle')}</h3>
            </div>
            
            <div class="px-12 flex-grow space-y-6 z-10">
        """
        for point in page.get("bullet_points", []):
            html_content += f"""<div class="bubble p-6 transform transition-transform hover:scale-105"><h4 class="text-[1.6rem] font-black text-gray-800 mb-2 flex items-center"><span class="text-3xl mr-3">🎈</span>{point.get('title')}</h4><p class="text-[1.3rem] text-gray-600 font-bold leading-relaxed ml-10">{point.get('content')}</p></div>"""
        html_content += f"""
            </div>

            <div class="px-12 mt-8 mb-12 h-[380px] relative z-10">
                <div class="w-full h-full border-8 border-yellow-300 rounded-3xl overflow-hidden shadow-[10px_10px_0px_#facc15] bg-white">
                    <img src="{img_url}" class="w-full h-full object-cover">
                </div>
            </div>
        </div>
        """
    outro = data.get("outro", {})
    html_content += f"""<div class="card flex flex-col justify-center items-center text-center px-16 relative bg-gradient-to-br from-pink-200 to-purple-200 border-pink-400 shadow-[15px_15px_0px_#f472b6]"><div class="text-[10rem] mb-12 animate-bounce">🦄</div><div class="bubble px-12 py-6 mb-12 transform rotate-2 border-pink-500 shadow-[8px_8px_0px_#f472b6]"><p class="text-5xl text-pink-600 font-black tracking-widest">{outro.get('brand_name', '')}</p></div><div class="bg-white px-10 py-8 rounded-[3rem] border-8 border-purple-400 shadow-[10px_10px_0px_#c084fc] transform -rotate-1"><h1 class="text-4xl font-black text-purple-600 tracking-widest leading-relaxed whitespace-pre-line">{outro.get('slogan', '')}</h1></div></div></body></html>"""
    return html_content

def generate_html_report(data, style_id="1", output_file="output.html"):
    if style_id == "2": html_content = render_style_apple(data)
    elif style_id == "3": html_content = render_style_guofeng(data)
    elif style_id == "4": html_content = render_style_fresh(data)
    elif style_id == "5": html_content = render_style_tech(data)
    elif style_id == "6": html_content = render_style_xiaohongshu(data)
    elif style_id == "7": html_content = render_style_dopamine(data)
    else: html_content = render_style_default(data)
    with open(output_file, "w", encoding="utf-8") as f: f.write(html_content)

def cleanup_output_folder(folder_path):
    if os.path.exists(folder_path):
        try: shutil.rmtree(folder_path)
        except: pass
    os.makedirs(folder_path, exist_ok=True)

def take_screenshots(html_file, output_dir):
    cleanup_output_folder(output_dir)
    file_url = f"file://{os.path.abspath(html_file)}"
    generated_images = []
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page(viewport={"width": 1200, "height": 3000})
            page.goto(file_url, wait_until="networkidle") 
            cards = page.locator(".card").all()
            for index, card in enumerate(cards):
                filename = f"{index:02d}_page.png" if index > 0 else "00_封面.png"
                if index == len(cards) - 1: filename = f"{index:02d}_封底.png"
                output_path = os.path.join(output_dir, filename)
                card.screenshot(path=output_path)
                generated_images.append(output_path)
            browser.close()
            return generated_images
    except Exception as e:
        st.error(f"截图失败: {e}")
        return []

def create_zip(image_paths, zip_path):
    with zipfile.ZipFile(zip_path, 'w') as zipf:
        for img in image_paths:
            zipf.write(img, os.path.basename(img))

# ==========================================
# Web UI 构建 (Streamlit 核心)
# ==========================================
if 'step' not in st.session_state: st.session_state.step = 1
if 'json_data' not in st.session_state: st.session_state.json_data = None
if 'images' not in st.session_state: st.session_state.images = []

with st.sidebar:
    show_hero = st.checkbox("🎬 显示 Logo 动态横幅", value=st.session_state.get("show_hero", True), key="show_hero")
    st.divider()
    st.title("⚙️ 全局设置")
    api_key = st.text_input("文本提炼大模型 API Key", type="password")
    
    st.divider()
    st.markdown("### 🎨 品牌与视觉")
    selected_style = st.selectbox("排版风格", ["1-政商务风 (黑黄撞色)", "2-极简苹果风", "3-国风传统", "4-小红书清透风", "5-科技未来风 (深色赛博)", "6-小红书拼图风 (拍立得+手账)", "7-田园多巴胺风 (高饱和元气)"])
    style_id = selected_style.split("-")[0]
    brand_name = st.text_input("品牌名称", value="@文商旅小圆桌")
    slogan = st.text_area("Slogan / 标语", value="文旅/策划/规划/投资/运营\n欢迎合作交流")
    
    st.divider()
    st.markdown("### 🖼️ 配图引擎设置")
    image_mode = st.radio("默认配图模式", ["1. 无版权图库 (LoremFlickr)", "2. AIGC 专属配图"])
    
    aigc_model = None
    img_api_key = ""
    if image_mode.startswith("2"):
        aigc_model = st.selectbox("选择 AI 绘画大模型", ["通义万相 2.7 (阿里云)", "DALL·E 3 (OpenAI)"])
        img_api_key = st.text_input("对应绘画模型的 API Key", type="password")


# ==========================================
# ==========================================
# Hero区域 — Logo视频 + 主标题
# ==========================================
show_hero = st.session_state.get("show_hero", True)

if show_hero and LOGO_VIDEO_PATH and os.path.exists(LOGO_VIDEO_PATH):
    with open(LOGO_VIDEO_PATH, "rb") as vf:
        video_b64 = base64.b64encode(vf.read()).decode()
    st.markdown(f"""
    <div class="hero-animate" style="display:flex; align-items:center; gap:14px; margin-bottom:28px; padding:20px 0 8px 0;">
        <div class="hero-video-wrap" style="flex-shrink:0;">
            <video autoplay loop muted playsinline disablePictureInPicture
                   style="height:84px; width:auto; display:block;"
                   oncontextmenu="return false;"
                   controlsList="nodownload nofullscreen">
                <source src="data:video/mp4;base64,{video_b64}" type="video/mp4">
            </video>
        </div>
        <div style="flex:1; min-width:0;">
            <h1 style="font-size:2rem; font-weight:900; color:#f1f5f9; margin:0 0 4px 0; letter-spacing:-0.03em; line-height:1.15;">
                AI NIUMA - AI牛马图文自动化
            </h1>
            <p style="font-size:0.9rem; color:#94a3b8; margin:0 0 4px 0;">
                AI牛马图文自动化 · 政策一键转长图
            </p>
            <span style="display:inline-block; background:rgba(99,102,241,0.2); color:#a5b4fc; font-size:0.75rem; font-weight:600; padding:4px 12px; border-radius:20px; border:1px solid rgba(99,102,241,0.2);">
                DeepSeek + DALL·E / 通义万相 智能配图
            </span>
        </div>
    </div>
    """, unsafe_allow_html=True)
else:
    st.title("📄 AI NIUMA - AI牛马图文自动化")

steps_text = ["上传提炼", "内容确认", "预览下载"]
st.progress(st.session_state.step / 3, text=f"当前阶段：{steps_text[st.session_state.step-1]}")

if st.session_state.step == 1:
    st.header("1. 上传政策文件")
    uploaded_file = st.file_uploader("支持 .pdf 和 .docx 文件", type=['pdf', 'docx'])
    
    if st.button("🪄 开始 AI 提炼 (第一步)", type="primary"):
        if not api_key: st.warning("⚠️ 请先输入文本提炼 API Key！")
        elif not uploaded_file: st.warning("⚠️ 请上传文件！")
        else:
            with st.spinner('正在阅读文件并进行智能提炼，请稍候约 10-20 秒...'):
                # 【新增清理机制】每次重新开始时，彻底清理工作区缓存，防止占用硬盘空间
                cleanup_output_folder(os.path.join(os.getcwd(), "workspace_temp"))
                
                text = read_document(uploaded_file, uploaded_file.name)
                if text:
                    data = extract_policy_data(text, api_key)
                    if data:
                        st.session_state.json_data = data
                        st.session_state.step = 2
                        st.rerun() 

elif st.session_state.step == 2:
    st.header("2. 内容确认与高级配图设定")
    st.info("💡 您可以修改文字，或为指定板块上传【本地实景图】来覆盖默认配图。")
    data = st.session_state.json_data
    
    with st.form("edit_form"):
        st.subheader("🖼️ 封面及全局")
        c_title = st.text_input("主标题", value=data.get('cover', {}).get('title', ''))
        c_sub = st.text_input("副标题", value=data.get('cover', {}).get('subtitle', ''))
        c_policy = st.text_input("政策原名", value=data.get('cover', {}).get('policy_name', ''))
        c_short = st.text_input("智能页眉缩写", value=data.get('cover', {}).get('short_policy_name', ''))
        c_high = st.text_input("核心亮点", value=data.get('cover', {}).get('highlights', ''))
        
        st.subheader(f"📑 内页板块 (共 {len(data.get('pages', []))} 个)")
        updated_pages = []
        local_upload_files = [] 
        
        for i, page in enumerate(data.get('pages', [])):
            with st.expander(f"板块 {i+1}：{page.get('section_title_black', '')}{page.get('section_title_yellow', '')}", expanded=False):
                p_tb = st.text_input("黑色大标题", value=page.get('section_title_black', ''), key=f"tb_{i}")
                p_ty = st.text_input("黄色高亮字", value=page.get('section_title_yellow', ''), key=f"ty_{i}")
                p_sub = st.text_input("副标题", value=page.get('section_subtitle', ''), key=f"sub_{i}")
                
                st.markdown("---")
                st.markdown("📸 **配图设置**")
                p_img = st.text_input("AI 绘画 / 图库搜索关键词", value=page.get('image_search_keyword', ''), key=f"img_{i}")
                local_f = st.file_uploader("📂 使用本地实景图覆盖 (可选)", type=['png', 'jpg', 'jpeg'], key=f"local_img_{i}")
                local_upload_files.append(local_f)
                
                st.markdown("---")
                st.markdown("**核心要点 (Bullet Points)**")
                bp_texts = []
                for j, bp in enumerate(page.get('bullet_points', [])):
                    bp_val = st.text_input(f"要点 {j+1}", value=f"{bp.get('title')}：{bp.get('content')}", key=f"bp_{i}_{j}")
                    bp_texts.append(bp_val)
                    
                updated_pages.append({
                    "page_number": page.get('page_number', i+1),
                    "section_title_black": p_tb, "section_title_yellow": p_ty,
                    "section_subtitle": p_sub, "image_search_keyword": p_img,
                    "bullet_points": [{"title": b.split("：")[0] if "：" in b else "", "content": b.split("：")[1] if "：" in b else b} for b in bp_texts]
                })

        submitted = st.form_submit_button("🚀 确认排版 & 开始处理图像流 (第二步)", type="primary")
        
        if submitted:
            st.session_state.json_data['cover'] = {"title": c_title, "subtitle": c_sub, "policy_name": c_policy, "short_policy_name": c_short, "highlights": c_high}
            st.session_state.json_data['outro'] = {"brand_name": brand_name, "slogan": slogan}
            
            with st.spinner("正在处理底层图像流，使用 AI 绘画可能需要等待 10~60 秒，请耐心稍候..."):
                for i, page in enumerate(updated_pages):
                    local_file = local_upload_files[i]
                    old_page = data.get('pages', [])[i] if i < len(data.get('pages', [])) else {}
                    old_url = old_page.get('resolved_image_url')
                    keyword_changed = page['image_search_keyword'] != old_page.get('image_search_keyword', '')

                    if local_file:
                        page['resolved_image_url'] = get_base64_image(local_file, "file")
                    elif old_url and not keyword_changed:
                        page['resolved_image_url'] = old_url
                    elif image_mode.startswith("2") and img_api_key:
                        style_prefix = STYLE_PROMPTS.get(style_id, "")
                        final_prompt = f"{style_prefix}{page['image_search_keyword']}"
                        
                        if aigc_model.startswith("DALL"):
                            ai_url = generate_ai_image_openai(final_prompt, img_api_key)
                        else:
                            ai_url = generate_ai_image_aliyun(final_prompt, img_api_key)
                            
                        if ai_url:
                            page['resolved_image_url'] = get_base64_image(ai_url, "url")
                        else:
                            page['resolved_image_url'] = get_base64_image(get_loremflickr_url(page['image_search_keyword'], i), "url")
                    else:
                        page['resolved_image_url'] = get_base64_image(get_loremflickr_url(page['image_search_keyword'], i), "url")
                
                st.session_state.json_data['pages'] = updated_pages
                
            with st.spinner("排版就绪，正在打开无头浏览器出图中..."):
                # 【替换机制】弃用系统的 tempfile，改用项目本地的固定工作区，避免 C 盘爆满
                temp_dir = os.path.join(os.getcwd(), "workspace_temp")
                os.makedirs(temp_dir, exist_ok=True)
                
                html_path = os.path.join(temp_dir, "output.html")
                img_dir = os.path.join(temp_dir, "images")
                
                generate_html_report(st.session_state.json_data, style_id, html_path)
                images = take_screenshots(html_path, img_dir)
                
                if images:
                    st.session_state.images = images
                    st.session_state.step = 3
                    st.rerun()

elif st.session_state.step == 3:
    st.header("3. 效果预览与下载")
    st.success("🎉 生成成功！所有本地/AI图像均已完美植入！")
    
    zip_path = os.path.join(os.path.dirname(st.session_state.images[0]), "policy_images.zip")
    create_zip(st.session_state.images, zip_path)
    with open(zip_path, "rb") as fp:
        st.download_button("📦 一键下载所有高清长图 (ZIP包)", data=fp, file_name="政策图文包.zip", mime="application/zip", type="primary")
        
    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔙 发现错别字？返回上一步微调", use_container_width=True):
            st.session_state.step = 2
            st.rerun()
    with col2:
        if st.button("🔄 完成，重新制作下一篇", use_container_width=True):
            # 【新增清理机制】工作完成后，彻底释放硬盘空间
            cleanup_output_folder(os.path.join(os.getcwd(), "workspace_temp"))
            st.session_state.step = 1; st.session_state.json_data = None; st.session_state.images = []
            st.rerun()

    st.divider()
    st.markdown("### 画廊预览 (支持局部快捷换图)")
    
    need_rerender = False 
    
    cols = st.columns(3)
    for idx, img_path in enumerate(st.session_state.images):
        with cols[idx % 3]: 
            st.image(img_path, caption=os.path.basename(img_path), use_container_width=True)
            
            if 0 < idx < len(st.session_state.images) - 1:
                with st.expander("🔄 快捷替换该页配图"):
                    repl_img = st.file_uploader("上传新的图片", type=['png', 'jpg', 'jpeg'], key=f"quick_replace_{idx}", label_visibility="collapsed")
                    if repl_img and st.button("确认替换", key=f"confirm_btn_{idx}", use_container_width=True):
                        with st.spinner("正在将新图植入并局部重绘..."):
                            page_idx = idx - 1 
                            st.session_state.json_data['pages'][page_idx]['resolved_image_url'] = get_base64_image(repl_img, "file")
                            need_rerender = True
                            
    if need_rerender:
        # 【替换机制】复用本地工作区，不再无限创建新文件夹导致 C 盘碎片
        temp_dir = os.path.join(os.getcwd(), "workspace_temp")
        os.makedirs(temp_dir, exist_ok=True)
        html_path = os.path.join(temp_dir, "output.html")
        img_dir = os.path.join(temp_dir, "images")
        
        generate_html_report(st.session_state.json_data, style_id, html_path)
        new_images = take_screenshots(html_path, img_dir)
        
        if new_images:
            st.session_state.images = new_images
            st.rerun()