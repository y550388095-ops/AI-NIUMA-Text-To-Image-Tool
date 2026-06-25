import json
import os
from openai import OpenAI
from playwright.sync_api import sync_playwright
import pdfplumber
import docx

# ==========================================
# 配置你的 DeepSeek API Key
# ==========================================
# 请将 "YOUR_DEEPSEEK_API_KEY" 替换为你真实的 API Key
DEEPSEEK_API_KEY = os.environ.get("DEEPSEEK_API_KEY", "") 

# ==========================================
# 1. 文档解析功能
# ==========================================
def read_document(file_path):
    """读取 PDF 或 Word 文件的文字内容"""
    if not os.path.exists(file_path):
        print(f"❌ 错误：找不到文件 '{file_path}'，请检查路径是否正确！")
        return None

    # 获取文件后缀名
    ext = file_path.lower().split('.')[-1]
    text = ""

    print(f"📂 正在解析文件: {file_path} ...")
    try:
        if ext == 'pdf':
            with pdfplumber.open(file_path) as pdf:
                for page in pdf.pages:
                    extracted = page.extract_text()
                    if extracted:
                        text += extracted + "\n"
        elif ext in ['doc', 'docx']:
            doc = docx.Document(file_path)
            for para in doc.paragraphs:
                text += para.text + "\n"
        else:
            print(f"❌ 不支持的文件格式：.{ext}。请提供 PDF 或 Word (.docx) 文件。")
            return None
        
        print(f"📄 成功提取文件内容，共 {len(text)} 个字符。")
        return text
    except Exception as e:
        print(f"❌ 读取文件时发生错误: {e}")
        return None

# ==========================================
# 2. 定义 Prompt 和 强类型的 JSON Schema
# ==========================================
SYSTEM_INSTRUCTION = """
你现在是一个顶尖的商业分析师和社交媒体（如小红书、微信公众号）内容策划专家。
你的任务是阅读用户提供的枯燥的官方政策文件，并将其提炼转化为吸引眼球的、结构清晰的、适合生成可视化长图的文案。

提取规则：
1. 语言必须精炼、接地气，把晦涩的官方术语转化为行业痛点解决方案（例如，将“鼓励用地功能兼容”转化为“混合兼容开发，无需调整详规，且不增收土地价款”）。
2. 封面标题要有冲击力。
3. 将内容划分为几个核心板块（如：规划、土地、资金等）。
4. 每个板块提炼出不超过3个要点（bullet_points），包含一个短标题和一句解释。
5. 为每个板块提供一个用于在图库搜索配图的英文关键词（如 'architect meeting', 'financial investment', 'old factory building'）。

你必须以 JSON 格式输出，并且完全遵循以下 JSON 结构：
{
  "cover": {
    "title": "主标题",
    "subtitle": "副标题",
    "policy_name": "政策原名",
    "highlights": "一句话核心亮点"
  },
  "pages": [
    {
      "page_number": 1,
      "section_title_black": "板块大标题的黑色前缀（如：'优化'、'创新'）",
      "section_title_yellow": "板块大标题的黄色强调核心词（如：'规划管理'、'产权归集'）",
      "section_subtitle": "板块副标题（如：'强化弹性适配'）",
      "image_search_keyword": "english keyword for image search",
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
    "slogan": "文旅/策划/规划/设计/运营\\n欢迎合作交流"
  }
}
"""

def extract_policy_data(text):
    """调用 DeepSeek 提取政策数据"""
    print("🤖 正在调用 DeepSeek 提炼政策内容，请稍候...")
    
    if DEEPSEEK_API_KEY == "YOUR_DEEPSEEK_API_KEY":
        print("❌ 错误：请将 DEEPSEEK_API_KEY 替换为您真实的 DeepSeek API Key！")
        return None

    client = OpenAI(api_key=DEEPSEEK_API_KEY, base_url="https://api.deepseek.com")
    
    try:
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": SYSTEM_INSTRUCTION},
                {"role": "user", "content": f"请仔细阅读以下政策文本，并提取信息：\n\n{text}"}
            ],
            response_format={
                'type': 'json_object'
            },
            temperature=0.2
        )
        return json.loads(response.choices[0].message.content)
    except Exception as e:
        print(f"❌ DeepSeek API 调用失败: {e}")
        return None

# ==========================================
# 3. 多风格模板渲染引擎
# ==========================================

def render_style_default(data):
    """风格1：原版政商务风 (黑黄撞色)"""
    html_content = """
    <!DOCTYPE html>
    <html lang="zh-CN">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>政策图文预览</title>
        <script src="https://cdn.tailwindcss.com"></script>
        <link href="https://fonts.googleapis.com/css2?family=Noto+Sans+SC:wght@400;500;700;900&display=swap" rel="stylesheet">
        <style>
            body { font-family: 'Noto Sans SC', sans-serif; background-color: #f3f4f6; padding: 2rem; display: flex; flex-direction: column; align-items: center; gap: 2rem; }
            .card { width: 800px; height: 1422px; background-color: white; box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1); overflow: hidden; position: relative; display: flex; flex-direction: column; }
            .cover-bg { background: linear-gradient(135deg, #710000 0%, #4a0000 100%); color: white; }
            .header-line { border-bottom: 1px solid #e5e7eb; }
            .yellow-circle { width: 110px; height: 110px; background-color: #ffb800; border-radius: 50%; position: relative; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1); }
        </style>
    </head>
    <body>
    """

    cover = data.get("cover", {})
    # 动态获取页眉文字
    header_text = cover.get('policy_name') or cover.get('title') or "最新政策深度解读"
    header_text = header_text.replace('\n', '')[:20]

    html_content += f"""
        <!-- 封面 -->
        <div class="card cover-bg flex flex-col justify-center px-16 text-center relative">
            <div class="absolute inset-0 opacity-20 bg-[radial-gradient(ellipse_at_center,_var(--tw-gradient-stops))] from-white via-transparent to-transparent pointer-events-none"></div>
            <p class="text-right text-lg text-gray-200 mb-6 tracking-widest">—— {cover.get('subtitle', '')}</p>
            <h1 class="text-7xl font-black mb-8 leading-snug tracking-wider">{cover.get('title', '')}</h1>
            <div class="flex justify-center items-center mb-16 mt-4">
                <span class="text-4xl text-[#ffb800] font-black tracking-widest bg-black/20 px-6 py-3 rounded">{cover.get('policy_name', '')}</span>
            </div>
            <div class="mt-20 text-center">
                <p class="text-5xl font-black italic tracking-widest text-white drop-shadow-lg">{cover.get('highlights', '')}</p>
            </div>
            <div class="absolute bottom-12 left-0 w-full text-center">
                <p class="text-lg text-gray-300 tracking-widest">{data.get('outro', {}).get('brand_name', '@文商旅小圆桌')}</p>
            </div>
        </div>
    """

    for page in data.get("pages", []):
        keyword = page.get('image_search_keyword', 'business architecture').replace(' ', ',')
        import time
        img_url = f"https://loremflickr.com/800/500/{keyword}?lock={int(time.time()) + page.get('page_number', 0)}"
        
        title_black = page.get('section_title_black', '')
        title_yellow = page.get('section_title_yellow', '')
        if not title_black and not title_yellow: title_black = page.get('section_title', '')

        html_content += f"""
        <!-- 内页 {page.get('page_number')} -->
        <div class="card flex flex-col relative bg-white">
            <div class="w-full text-center py-6 header-line mt-4 px-12">
                <!-- 动态页眉 -->
                <span class="tracking-[0.8em] text-gray-400 text-sm ml-[0.8em] inline-block w-full truncate">{header_text}</span>
            </div>
            <div class="flex items-start px-14 mt-16 mb-12">
                <div class="relative flex-shrink-0 mr-6 mt-1">
                    <div class="yellow-circle">
                        <span class="text-[5.5rem] font-black italic absolute left-3 top-[-0.2rem] text-black leading-none">{page.get('page_number')}</span>
                        <span class="text-xl font-black italic absolute right-2 bottom-3 text-black leading-none">板块</span>
                    </div>
                </div>
                <div class="flex flex-col justify-center mt-[-6px]">
                    <h2 class="text-[4.2rem] font-black tracking-wide leading-tight mb-2">
                        <span class="text-black">{title_black}</span><span class="text-[#ffb800]">{title_yellow}</span>
                    </h2>
                    <h3 class="text-[3.8rem] font-black tracking-wide text-black leading-tight">{page.get('section_subtitle')}</h3>
                </div>
            </div>
            <div class="px-16 flex-grow space-y-8">
        """
        for point in page.get("bullet_points", []):
            html_content += f"""
                <div class="flex items-start">
                    <div class="w-3 h-3 bg-black rounded-full mt-2.5 mr-5 flex-shrink-0"></div>
                    <div class="text-xl leading-relaxed text-gray-600 tracking-wide">
                        <span class="font-black text-black">{point.get('title')}：</span>{point.get('content')}
                    </div>
                </div>
            """
        html_content += f"""
            </div>
            <div class="px-14 mt-12 mb-10 h-[400px]">
               <img src="{img_url}" alt="{keyword}" class="w-full h-full object-cover rounded shadow-sm" onerror="this.src='https://images.unsplash.com/photo-1486406146926-c627a92ad1ab?q=80&w=800&auto=format&fit=crop';">
            </div>
            <div class="px-14 pb-10 flex justify-between items-center text-gray-400 text-sm mt-auto">
                <span class="tracking-widest">{data.get('outro', {}).get('brand_name', '@文商旅小圆桌')}</span>
                <span class="tracking-widest">以上为部分要点梳理，具体政策内容请以正式发布的文件为准。</span>
            </div>
        </div>
        """

    outro = data.get("outro", {})
    html_content += f"""
        <!-- 封底 -->
        <div class="card cover-bg flex flex-col justify-center items-center text-center px-12 relative">
            <div class="absolute inset-0 opacity-20 bg-[radial-gradient(ellipse_at_center,_var(--tw-gradient-stops))] from-white via-transparent to-transparent pointer-events-none"></div>
            <p class="text-2xl mb-8 tracking-widest text-gray-300">{outro.get('brand_name', '')}</p>
            <p class="text-5xl font-black tracking-widest whitespace-pre-line leading-relaxed drop-shadow-lg">{outro.get('slogan', '')}</p>
        </div>
    </body>
    </html>
    """
    return html_content

def render_style_apple(data):
    """风格2：极简苹果风 (高冷灰白质感)"""
    html_content = """
    <!DOCTYPE html>
    <html lang="zh-CN">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <script src="https://cdn.tailwindcss.com"></script>
        <style>
            body { font-family: -apple-system, BlinkMacSystemFont, "SF Pro SC", "Helvetica Neue", Helvetica, Arial, sans-serif; background-color: #000; padding: 2rem; display: flex; flex-direction: column; align-items: center; gap: 2rem; }
            .card { width: 800px; height: 1422px; background-color: #fbfbfd; overflow: hidden; position: relative; display: flex; flex-direction: column; }
        </style>
    </head>
    <body>
    """
    cover = data.get("cover", {})
    header_text = cover.get('policy_name') or cover.get('title') or "Policy Document"
    header_text = header_text.replace('\n', '')[:20]

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
        keyword = page.get('image_search_keyword', 'modern minimal architecture').replace(' ', ',')
        import time
        img_url = f"https://loremflickr.com/800/500/{keyword}?lock={int(time.time()) + page.get('page_number', 0)}"
        t_black = page.get('section_title_black', '')
        t_yellow = page.get('section_title_yellow', '')
        if not t_black and not t_yellow: t_black = page.get('section_title', '')

        html_content += f"""
        <div class="card flex flex-col relative">
            <div class="w-full text-center py-8 border-b border-[#d2d2d7] mt-8 px-12">
                <span class="tracking-[0.2em] text-[#86868b] text-xs font-semibold uppercase inline-block w-full truncate">{header_text}</span>
            </div>
            <div class="px-20 mt-20 mb-16">
                <p class="text-[#0066cc] font-semibold text-2xl mb-4">Section {page.get('page_number')}</p>
                <h2 class="text-6xl font-bold tracking-tight text-[#1d1d1f] leading-tight mb-4">{t_black}{t_yellow}</h2>
                <h3 class="text-3xl font-semibold text-[#86868b]">{page.get('section_subtitle')}</h3>
            </div>
            <div class="px-20 flex-grow space-y-10">
        """
        for point in page.get("bullet_points", []):
            html_content += f"""
                <div class="border-t border-[#d2d2d7] pt-6">
                    <h4 class="text-2xl font-bold text-[#1d1d1f] mb-3">{point.get('title')}</h4>
                    <p class="text-xl leading-relaxed text-[#515154]">{point.get('content')}</p>
                </div>
            """
        html_content += f"""
            </div>
            <div class="px-20 mt-12 mb-16 h-[380px]">
               <img src="{img_url}" class="w-full h-full object-cover rounded-3xl" onerror="this.src='https://images.unsplash.com/photo-1491933382434-500287f9b54b?q=80&w=800&auto=format&fit=crop';">
            </div>
        </div>
        """
    outro = data.get("outro", {})
    html_content += f"""
        <div class="card flex flex-col justify-center items-center text-center px-20 bg-[#1d1d1f]">
            <p class="text-4xl font-semibold text-white tracking-wide mb-8">{outro.get('brand_name', '')}</p>
            <p class="text-2xl text-[#86868b] font-medium leading-relaxed whitespace-pre-line">{outro.get('slogan', '')}</p>
        </div>
    </body></html>
    """
    return html_content

def render_style_guofeng(data):
    """风格3：中国传统国风 (红砖黛瓦，宋体衬线)"""
    html_content = """
    <!DOCTYPE html>
    <html lang="zh-CN">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <script src="https://cdn.tailwindcss.com"></script>
        <link href="https://fonts.googleapis.com/css2?family=Noto+Serif+SC:wght@400;700;900&display=swap" rel="stylesheet">
        <style>
            body { font-family: 'Noto Serif SC', serif; background-color: #e5e5e5; padding: 2rem; display: flex; flex-direction: column; align-items: center; gap: 2rem; }
            .card { width: 800px; height: 1422px; background-color: #f7f4ed; overflow: hidden; position: relative; display: flex; flex-direction: column; border: 1px solid #d5c8b5; }
            .red-stamp { border: 2px solid #8c222c; color: #8c222c; padding: 0.5rem 1rem; font-weight: bold; }
        </style>
    </head>
    <body>
    """
    cover = data.get("cover", {})
    header_text = cover.get('title') or "政策汇编" 
    header_text = header_text.replace('\n', '')[:12]

    html_content += f"""
        <div class="card flex flex-col justify-center items-center px-16 text-center border-[12px] border-double border-[#d5c8b5] m-4 w-[calc(100%-32px)] h-[calc(100%-32px)] relative">
            <div class="absolute top-16 right-16 text-[#8c222c] text-xl font-bold tracking-widest" style="writing-mode: vertical-rl;">{cover.get('subtitle', '')}</div>
            <h1 class="text-7xl font-black text-[#8c222c] mb-12 leading-snug tracking-widest">{cover.get('title', '')}</h1>
            <div class="red-stamp text-2xl tracking-widest mb-20">{cover.get('policy_name', '')}</div>
            <p class="text-4xl font-bold text-[#333] tracking-widest bg-white/50 py-6 px-10 border border-[#d5c8b5] shadow-sm">{cover.get('highlights', '')}</p>
            <div class="absolute bottom-16 text-[#666] tracking-widest"><span class="red-stamp text-sm mr-3">印</span>{data.get('outro', {}).get('brand_name', '')}</div>
        </div>
    """
    for page in data.get("pages", []):
        keyword = page.get('image_search_keyword', 'traditional chinese architecture').replace(' ', ',')
        import time
        img_url = f"https://loremflickr.com/800/500/{keyword}?lock={int(time.time()) + page.get('page_number', 0)}"
        t_black = page.get('section_title_black', '')
        t_yellow = page.get('section_title_yellow', '')
        if not t_black and not t_yellow: t_black = page.get('section_title', '')

        html_content += f"""
        <div class="card flex flex-col relative">
            <div class="w-full text-center py-6 border-b-2 border-double border-[#8c222c] mt-8 mx-12 relative px-4" style="width: calc(100% - 6rem);">
                <span class="tracking-[0.6em] text-[#8c222c] font-bold text-lg truncate block">{header_text}卷</span>
            </div>
            <div class="px-16 mt-16 mb-12 flex items-center">
                <div class="text-[#8c222c] text-[6rem] leading-none font-black mr-8 border-r-4 border-[#8c222c] pr-8">{page.get('page_number')}</div>
                <div class="flex flex-col">
                    <h2 class="text-[3.5rem] font-black text-[#333] tracking-wider mb-4">{t_black}<span class="text-[#8c222c]">{t_yellow}</span></h2>
                    <h3 class="text-3xl font-bold text-[#666] tracking-widest">{page.get('section_subtitle')}</h3>
                </div>
            </div>
            <div class="px-16 flex-grow space-y-8">
        """
        for point in page.get("bullet_points", []):
            html_content += f"""
                <div class="flex items-start">
                    <div class="text-[#8c222c] text-2xl mr-4 mt-1">◆</div>
                    <div class="text-xl leading-loose text-[#444] tracking-wide text-justify">
                        <span class="font-bold text-[#8c222c] text-2xl border-b-2 border-[#8c222c] pb-1 mr-3">{point.get('title')}</span>{point.get('content')}
                    </div>
                </div>
            """
        html_content += f"""
            </div>
            <div class="px-12 mt-12 mb-10 h-[380px] p-2 border border-[#d5c8b5] mx-12 bg-white">
               <img src="{img_url}" class="w-full h-full object-cover grayscale opacity-90" onerror="this.src='https://images.unsplash.com/photo-1547638375-ebf04735d792?q=80&w=800&auto=format&fit=crop';">
            </div>
        </div>
        """
    outro = data.get("outro", {})
    html_content += f"""
        <div class="card flex flex-col justify-center items-center text-center px-16 relative">
            <div class="w-[400px] h-[400px] rounded-full border border-[#d5c8b5] absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 opacity-30 pointer-events-none"></div>
            <h1 class="text-[4rem] font-black text-[#8c222c] mb-12 tracking-[0.3em]" style="writing-mode: vertical-rl;">{outro.get('brand_name', '')}</h1>
            <p class="text-2xl text-[#333] tracking-widest leading-loose bg-white/60 py-6 px-10 border border-[#d5c8b5]">{outro.get('slogan', '')}</p>
        </div>
    </body></html>
    """
    return html_content

def render_style_fresh(data):
    """风格4：小红书清透风 (马卡龙渐变，玻璃拟物)"""
    html_content = """
    <!DOCTYPE html>
    <html lang="zh-CN">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <script src="https://cdn.tailwindcss.com"></script>
        <style>
            body { font-family: 'PingFang SC', 'Microsoft YaHei', sans-serif; background-color: #f3f4f6; padding: 2rem; display: flex; flex-direction: column; align-items: center; gap: 2rem; }
            .card { width: 800px; height: 1422px; background: linear-gradient(135deg, #fff5f5 0%, #f0f9ff 100%); overflow: hidden; position: relative; display: flex; flex-direction: column; }
            .glass-panel { background: rgba(255, 255, 255, 0.65); backdrop-filter: blur(16px); border: 1px solid rgba(255,255,255,0.8); border-radius: 2rem; box-shadow: 0 10px 30px rgba(0,0,0,0.05); }
        </style>
    </head>
    <body>
    """
    cover = data.get("cover", {})
    header_text = cover.get('title') or "🔥 热点政策速递"
    header_text = header_text.replace('\n', '')[:16]

    html_content += f"""
        <div class="card p-8 relative">
            <div class="absolute top-[-100px] right-[-100px] w-96 h-96 bg-pink-200 rounded-full mix-blend-multiply filter blur-3xl opacity-50 pointer-events-none"></div>
            <div class="absolute bottom-[-100px] left-[-100px] w-96 h-96 bg-blue-200 rounded-full mix-blend-multiply filter blur-3xl opacity-50 pointer-events-none"></div>
            
            <div class="glass-panel flex-grow flex flex-col justify-center items-center px-12 text-center z-10 relative">
                <span class="bg-white/80 text-pink-500 px-6 py-2 rounded-full text-xl font-bold mb-10 shadow-sm">✨ {cover.get('subtitle', '')}</span>
                <h1 class="text-7xl font-black text-gray-800 mb-10 leading-snug">{cover.get('title', '')}</h1>
                <div class="text-2xl text-gray-500 font-bold mb-20 px-8 py-3 bg-white/50 rounded-2xl">{cover.get('policy_name', '')}</div>
                <div class="bg-gradient-to-r from-pink-400 to-purple-400 text-white text-[2.5rem] font-bold py-8 px-12 rounded-[2rem] shadow-lg transform -rotate-2">{cover.get('highlights', '')}</div>
                
                <div class="absolute bottom-12 flex items-center bg-white/80 px-6 py-3 rounded-full shadow-sm">
                    <div class="w-8 h-8 rounded-full bg-gradient-to-r from-pink-300 to-blue-300 mr-3"></div>
                    <span class="text-gray-500 font-bold tracking-wider">{data.get('outro', {}).get('brand_name', '')}</span>
                </div>
            </div>
        </div>
    """
    for page in data.get("pages", []):
        keyword = page.get('image_search_keyword', 'aesthetic cozy room').replace(' ', ',')
        import time
        img_url = f"https://loremflickr.com/800/500/{keyword}?lock={int(time.time()) + page.get('page_number', 0)}"
        t_black = page.get('section_title_black', '')
        t_yellow = page.get('section_title_yellow', '')
        if not t_black and not t_yellow: t_black = page.get('section_title', '')

        html_content += f"""
        <div class="card p-8 relative">
            <div class="glass-panel flex-grow flex flex-col relative z-10 overflow-hidden">
                <div class="px-12 pt-12 pb-8 flex items-center justify-between">
                    <div class="flex items-center">
                        <div class="w-20 h-20 bg-gradient-to-br from-pink-300 to-blue-300 text-white rounded-[1.5rem] shadow-md flex items-center justify-center text-4xl font-black mr-6">{page.get('page_number')}</div>
                        <h2 class="text-5xl font-black text-gray-800 tracking-wide">{t_black}<span class="text-pink-400">{t_yellow}</span></h2>
                    </div>
                    <span class="bg-blue-50 text-blue-400 px-5 py-2 rounded-full text-md font-bold shadow-sm max-w-[200px] truncate">{header_text}</span>
                </div>
                
                <h3 class="px-12 text-3xl font-bold text-gray-500 mb-10 border-l-[6px] border-pink-400 ml-12 pl-6">{page.get('section_subtitle')}</h3>
                
                <div class="px-12 flex-grow space-y-6">
        """
        for point in page.get("bullet_points", []):
            html_content += f"""
                    <div class="bg-white/80 p-6 rounded-[1.5rem] shadow-sm border border-white">
                        <h4 class="text-[1.6rem] font-bold text-gray-800 mb-3 flex items-center">
                            <span class="text-pink-400 mr-3 text-2xl">💡</span> {point.get('title')}
                        </h4>
                        <p class="text-[1.3rem] text-gray-600 leading-relaxed ml-10">{point.get('content')}</p>
                    </div>
            """
        html_content += f"""
                </div>
                <div class="px-8 pb-8 pt-6">
                   <img src="{img_url}" class="w-full h-[360px] object-cover rounded-[2rem] shadow-md border-4 border-white" onerror="this.src='https://images.unsplash.com/photo-1515378791036-0648a3ef77b2?q=80&w=800&auto=format&fit=crop';">
                </div>
            </div>
        </div>
        """
    outro = data.get("outro", {})
    html_content += f"""
        <div class="card p-8 relative">
            <div class="glass-panel flex-grow flex flex-col justify-center items-center text-center px-16 z-10">
                <div class="w-32 h-32 bg-white rounded-[2rem] shadow-lg flex items-center justify-center text-6xl mb-12 transform rotate-12">🌸</div>
                <h1 class="text-5xl font-black text-gray-800 mb-8 tracking-wider">{outro.get('brand_name', '')}</h1>
                <p class="text-[1.8rem] text-gray-500 font-bold leading-relaxed bg-white/70 py-8 px-12 rounded-[2rem] shadow-sm whitespace-pre-line">{outro.get('slogan', '')}</p>
            </div>
        </div>
    </body></html>
    """
    return html_content

def generate_html_report(data, style="1", output_file="output.html"):
    """将 JSON 数据渲染为 HTML 页面，支持多套模板"""
    if not data:
        return

    print(f"\n🎨 正在生成 HTML 报告 (已选用模板 {style})...")
    
    if style == "2":
        html_content = render_style_apple(data)
    elif style == "3":
        html_content = render_style_guofeng(data)
    elif style == "4":
        html_content = render_style_fresh(data)
    else:
        html_content = render_style_default(data)

    with open(output_file, "w", encoding="utf-8") as f:
        f.write(html_content)
    
    print(f"✅ 成功！HTML 报告已生成并保存至: {os.path.abspath(output_file)}")

# ==========================================
# 4. 自动化截图功能
# ==========================================

def take_screenshots(html_file="output.html", output_dir="output_images"):
    """使用 Playwright 对生成的 HTML 页面进行分页截图"""
    print(f"\n🚀 正在启动 Playwright 截图引擎...")
    
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    file_url = f"file://{os.path.abspath(html_file)}"

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page(viewport={"width": 1200, "height": 3000})
            
            print(f"⏳ 正在加载页面以准备截图...")
            page.goto(file_url, wait_until="networkidle") 
            
            cards = page.locator(".card").all()
            total_cards = len(cards)
            print(f"📷 共发现 {total_cards} 张排版卡片，开始批量截图...")
            
            for index, card in enumerate(cards):
                if index == 0:
                    filename = "00_封面.png"
                elif index == total_cards - 1:
                    filename = f"{index:02d}_封底.png"
                else:
                    filename = f"{index:02d}_内页.png"
                    
                output_path = os.path.join(output_dir, filename)
                card.screenshot(path=output_path)
                print(f"🖼️ 已保存: {output_path}")
                
            browser.close()
            print(f"\n🎉 完美！所有高清切图已保存至文件夹: {os.path.abspath(output_dir)}")
    except Exception as e:
        print(f"❌ 截图过程中发生错误: {e}")
        print("提示：请确认是否已安装 Playwright 相关依赖。")

# ==========================================
# 5. 主执行流程
# ==========================================
if __name__ == "__main__":
    print("=== 开始自动化图文生成系统 ===")
    
    print("请输入需要解析的政策文件路径 (支持 .pdf 或 .docx)")
    print("提示: 可以直接将文件拖拽到这个黑色窗口里，然后按回车。")
    file_path = input("文件路径: ").strip()
    
    if file_path.startswith('"') and file_path.endswith('"'):
        file_path = file_path[1:-1]
    
    policy_text = read_document(file_path)
    
    if policy_text:
        extracted_json = extract_policy_data(policy_text)
        
        if extracted_json:
            print("\n✅ AI 成功提取出 JSON 数据！")
            
            print("\n🎨 请选择排版风格：")
            print("1. 政商务风 (默认，黑黄撞色)")
            print("2. 极简苹果风 (Apple 官网高冷质感)")
            print("3. 中国传统国风 (红砖黛瓦，宋体衬线)")
            print("4. 小红书清透风 (马卡龙渐变，玻璃拟物)")
            style_choice = input("请输入风格编号 (1/2/3/4) [按回车默认1]: ").strip()
            if style_choice not in ["1", "2", "3", "4"]:
                style_choice = "1"
            
            generate_html_report(extracted_json, style_choice)
            take_screenshots()
        else:
            print("流程中断：AI 提炼失败。")
    else:
        print("流程中断：文件读取失败。")