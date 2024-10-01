import os
import re
import html2text as h2t
import scrapy
import requests as rq
from PIL import Image
from openai import OpenAI
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
import sys

# 動態獲取路徑
def get_base_path():
    if hasattr(sys, '_MEIPASS'):
        return sys._MEIPASS
    return os.path.dirname(os.path.abspath(__file__))

# 全域變數設定
ROOT_PATH = get_base_path()
DESKTOP_PATH = os.path.join(ROOT_PATH, 'Desktop')
GTG_ARTICLES_FOLDER = os.path.join(DESKTOP_PATH, 'gtg-articles')
HREF_CSS_RULES = {
    "guitargirlmag.com": {
        'sel': 'a[href*="music-news"]::attr(href)',
    },
    "www.guitarworld.com": {
        'sel': '.listingResult a.article-link::attr(href)'
    },
    "acousticguitarmagazine.jp": {
        'sel': '.post-wrap a::attr(href)',
    },
    "guitargearfinder.com": {
        'sel': '.post-image a::attr(href)'
    },
    "www.guitarplayer.com": {
        'sel': '.feature-block-item-wrapper a, .listingResult a::attr(href)'
    }
}
CONTENT_CSS_RULES = {
    # "example.com":{
    #     "title": ,   預設值 title::text
    #     "content":,
    #     "content_index":,
    #     "source_page": 預設值 link[rel="canonical"]::attr(href)
    # }
    "guitargirlmag.com": {
        "content": 'article .vc_column_container.td-pb-span8 .wpb_wrapper',
    },
    "www.guitarworld.com": {
        'content': '#article-body'
    },
    "acousticguitarmagazine.jp":{
        "content": "main",
    },
    "guitargearfinder.com": {
        'content': 'article'
    },
    "www.guitarplayer.com": {
        'content': 'article'
    }
}

# HTML 轉化為 MarkDown
def html_to_md(html):
    # 設定 Markdown 轉換器
    h = h2t.HTML2Text()
    h.ignore_links = False

    # 執行轉換，獲取Markdown內容
    md_content = h.handle(html)
    return md_content

# GPT 翻譯
def gpt_e2m(text):
    
    # 放置 key
    api_key = os.environ.get("OPENAI_API_KEY")

    # 確認 API 金鑰已設置
    if api_key is None:
        raise ValueError("API 金鑰未設置")


    client = OpenAI(api_key = api_key)

    # 開始翻譯
    
    mission = f"請將文案翻成繁體中文，語氣自然並保留Markdown格式"

    print("發送 GPT 請求！")
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": mission},
            {"role": "user", "content": text}
        ],
        # max_tokens=100
    )

    print(f'使用模型： {response.model}')

    # 得到翻譯內容
    output_text = str(response.choices[0].message.content)

    return output_text

# 下載圖片 & 壓縮 
def img_download_compress(image_url, slug, site_folder, image_index = 0, target_size = 100 ) :

    # 下載 & 界定圖檔
    if '.svg' in image_url :
        file_name = f'{slug}_{image_index}.svg'
    else :
        file_name = f'{slug}_{image_index}.webp'

    # 定位 /domain_name/img 位置
    img_folder = os.path.join(site_folder, 'img')
    
    # 若 Slug 資料夾不存在，創建一個
    if not os.path.exists(img_folder):
        os.makedirs(img_folder)
        
    file_path = os.path.join(img_folder, file_name)

    # 開始下載圖擋
    img_res = rq.get(image_url, stream = True)
    
    if img_res.status_code == 200 :
        with open(file_path, 'wb') as file :        #b代表以 2 進制方式打開文件
            for chunk in img_res.iter_content(chunk_size = 8192):
                file.write(chunk)
        print(f'Cover Image {file_name} Download Successful')

        #2. 壓縮

        print(f'目前圖檔大小 {os.path.getsize(file_path) // 1024}')

        while os.path.getsize(f'{file_path}') // 1024 > target_size :
            # 展示壓縮前質量
            size_before = os.path.getsize(f'{file_path}') // 1024
            print(f'Original Size : {size_before}')
            
            # 進行壓縮：改變質量
            img = Image.open(f'{file_path}')
            img.save(f'{file_path}','WEBP', quality = 90)
            print('Compressed Complete !')  

            # 展示壓縮後質量
            size_after = os.path.getsize(f'{file_path}') // 1024
            print(f'Current Size : {size_after}')

            # 如果壓縮前後質量相同，代表改變質量的方法到極限
            if size_before == size_after : break

        while os.path.getsize(f'{file_path}') // 1024 > target_size :
            # 展示壓縮前質量
            size_before = os.path.getsize(f'{file_path}')
            print(f'The Original Size : {size_before // 1024}')

            # 進行壓縮：改變長寬
            img = Image.open(f'{file_path}')
            width, height = img.size
            width = int(width * 0.9)
            height = int(height * 0.9)
            img = img.resize((width, height), Image.Resampling.LANCZOS) 
            img.save(file_path, 'WEBP', quality=90)  # 保存调整后的图像
            print('Resize Complete !')

            # 展示壓縮後質量
            size_after = os.path.getsize(f'{file_path}')
            print(f'The Current Size : {size_after // 1024}')

            # 如果壓縮前後質量相同，代表改變長寬的方法到極限
            if size_before == size_after : break

        print('圖檔下載 & 壓縮成功')

        return file_name

    else :
        print(f'獲取圖檔失敗，圖檔連結：{image_url}')

        return False

# 刪除純連結格式
def delete_md_links(markdown_text):

    md_content = markdown_text + ''

    # 刪除內部 / 外部連結
    href_with_img_reg = r'(?<!\!)\[\!\[[^\]]*\]\([^\)]*\)\]\([^\)]*\)'          #圖片為錨點
    md_content = re.sub(href_with_img_reg, '', md_content)

    href_with_text_reg = r'(?<!\!)\[[^\]]*\]\([^\)]*\)'                         #文字為錨點
    md_content = re.sub(href_with_text_reg, '', md_content)

    return md_content

# 文案存進檔案 (含覆蓋功能) 
def save_to_file(post_title, post_source_page, post_content, slug , file_type , folder_path = "D:/guitar-articles"):
    # 檢查資料夾是否存在，若不存在則創建資料夾
    if not os.path.exists(folder_path):
        print("資料夾不存在，創建資料夾中...")
        os.makedirs(folder_path)
        print("資料夾創建成功！")
    else :
        print("確認資料夾存在，進入資料夾...")

    # 設定 txt 檔案的完整路徑，假設檔案名稱是 title.txt
    file_path = os.path.join(folder_path, f"{slug}.{file_type}")

    # 確認檔案是否存在，如存在，取代掉
    if os.path.exists(file_path):
        os.remove(file_path)

    # 開啟 txt 檔案並寫入內容
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(f"Title: {post_title}\n")
        print("標題寫入完成")
        file.write(f"Source Page: {post_source_page}\n")
        print("來源網頁寫入完成")
        file.write(f"Content:\n{post_content}\n")
        print("內容寫入完成")

    print(f"{post_title}.{file_type}檔案建立完畢！")

class Spider1Spider(scrapy.Spider):
    
    # 蜘蛛基本設定
    name = "spider1"
    allowed_domains = ["guitargirlmag.com", "www.guitarworld.com", "acousticguitarmagazine.jp", "guitargearfinder.com", "www.guitarplayer.com"]

    # 爬取網域設定
    guitar_girl_start = [f"https://guitargirlmag.com/category/reviews/gear-reviews/page/{i}/" for i in range(1,6)]
    guitar_world_start = [f"https://www.guitarworld.com/news/page/{i}" for i in range(1,6)] + [f'https://www.guitarworld.com/features/page/{i}' for i in range(1,6)] 
    acoustic_guitar_jp_start = [f"https://acousticguitarmagazine.jp/gears/page/{i}/" for i in range(1, 6)]
    guitar_gear_start = [f"https://guitargearfinder.com/category/reviews/electric-guitars/", f"https://guitargearfinder.com/category/reviews/single-effect-pedals/", f"https://guitargearfinder.com/category/reviews/multi-effects-pedals/"]
    guitar_player_start = [f"https://www.guitarplayer.com/gear/page/{i}" for i in range(1, 6)] + [f"https://www.guitarplayer.com/news/page/{i}" for i in range(1,6)]
    start_urls = [] + guitar_girl_start + guitar_world_start  + acoustic_guitar_jp_start + guitar_gear_start + guitar_player_start

    # guitargirl 新版還沒測試！！！！！！！！！！！！！！！！！！！！！！！！

    def parse(self, response):  # response 代表 requests 後回傳的內容

        # 確認主資料夾是否存在，若否，建立一個！
        if not os.path.exists(GTG_ARTICLES_FOLDER) :
            print("確認網域資料夾不存在")
            os.makedirs(GTG_ARTICLES_FOLDER)
            print("已建立網域資料夾")

        else :
            print("確認網域資料夾已存在")

        # 開始丟入執行
        yield response.follow(      # 傳遞當前爬取的網站給對應function 處理，同時用 meta 傳遞資訊
            response.url,
            self.parse_href,
            meta = {"category_page": response.url}
        )
        
    # 抓取文章連結
    def parse_href(self, response):
        
        # 取得當前 domain
        category = response.meta.get("category_page")
        domain = re.findall(r'^https?:\/\/([^\/]+)', category)[0]
        domain_folder = os.path.join(GTG_ARTICLES_FOLDER, domain)
        print(f"當前Domain: {domain}")

        # 根據規則抓取內容頁的URL
        domain_rule = HREF_CSS_RULES[domain]
        css_rule = domain_rule['sel']
        try :
            must_have = domain_rule['must_have']
        except :
            must_have = ['']

        try :
            must_not = domain_rule['must_not']
        except :
            must_not = []

        print(f"domain_rule: {domain_rule}")
        print(f"css_rule: {css_rule}")
        print(f"must_have: {','.join(must_have)}")
        print(f"must_not: {','.join(must_not)}")

        for href in response.css(css_rule).getall():
            if href != category :

                must_have_pass = False      # 必須包含的內容
                for mh in must_have :       
                    if mh in href :
                        must_have_pass = True
                    
                if not must_have_pass :
                    continue
                
                for mn in must_not :        # 不可包含的內容
                    if mn in href :
                        continue
                
                yield response.follow(
                    href, 
                    self.parse_content, 
                    meta={
                        'site_folder':domain_folder,
                        'domain': domain
                        }   # 從 response 的 meta 中取得 site_folder 的資訊
                    )

    def parse_content(self, response):
        
        # 取得 domain
        domain = response.meta.get("domain")

        # 取出 CSS RULE
        R = CONTENT_CSS_RULES[domain]

        # 取得 CSS RULE Key
        R_KEYS = R.keys()

        # 取得標題，若無設定，擷取預設值
        if 'title' in R_KEYS :
            title = response.css(R["title"]).get()
        else :
            title = response.css("title::text").get()
        
        # 取得內容，content_index 預設為 0
        try :
            content_index = R["content_index"]
        except :
            content_index = 0
        content = response.css(R["content"])[content_index].get()

        # 取得 Source_page
        if 'source_page' in R_KEYS :
            source_page = response.css(R["source_page"]).get()
        else :
            source_page = response.css('link[rel="canonical"]::attr(href)').get()

        print(f"開始處理網頁...\nTitle：{title}\nSource_Page：{source_page}")

        # 取得 Slug
        slug = re.findall(r'([^\/]+)\/?$', source_page)[0]

        # 取得 Site Folder
        site_folder = response.meta.get('site_folder')

        # 取得 File_path
        file_path = os.path.join(site_folder, f"{slug}.txt")
        
        print(f"確認檔案連結：{file_path}")

        if os.path.exists(file_path):
            print("檔案已存在，不爬取")
            return None
        
        print(f"檔案不存在，將繼續處理")

        # 標題防呆處理
        title = re.sub(r':','：',title)

        # 內容處理：轉化成 MarkDown
        md_content = html_to_md(content)

        # 內容處理：刪除連結
        md_content = delete_md_links(md_content)

        # 內容處理：下載圖檔
        img_reg = r'\!\[[^\]]*\]\(([^\)]+)\)'
        img_hrefs = re.findall(img_reg, md_content)
        img_index = 0
        for h in img_hrefs :
            if '\n' in h :
                href = re.sub(r'\n', '', h)
            else :
                href = h
            print(f"獲取圖檔連結 => {href}")
            try:
                if rq.get(href).status_code == 200:     # 圖片連結可直接下載
                    print(f'獲取圖檔成功，正在下載')
                    file_name = img_download_compress(
                        image_url=href, 
                        slug = slug, 
                        image_index = img_index,
                        site_folder= site_folder
                        )
                    img_index += 1
                    
                    # 修正 MD 中連結
                    img_reg_revise = rf'(?>=\!\[[^\]]*\]\(){href}(?=\))'
                    md_content = re.sub(img_reg_revise, file_name, md_content)
            
                else :
                    print(f"獲取圖檔失敗")
                    print(f"嘗試圖檔連結加入 Domain")
                    if rq.get(f"{domain}{href}").status_code == 200 :   # 圖片連結需加上Domain
                        print(f"獲取圖檔成功，正在下載： {domain}{href}")
                        file_name = img_download_compress(image_url=f"{domain}{href}", slug = slug, image_index = img_index)
                        img_index += 1

                        # 修正 MD 中連結
                        img_reg_revise = rf'(?>=\!\[[^\]]*\]\(){href}(?=\))'
                        md_content = re.sub(img_reg_revise, file_name, md_content)

                    else :
                        print(f"獲取圖檔失敗: {domain}{href}")      # 圖片無法下載，刪除 Markdown 中的連結
                        print(f"刪除圖檔連結")
                        img_reg_del = rf'\!\[[^\]]*\]\({href}\)'
                        md_content = re.sub(img_reg_del, '', md_content)

            except :
                    print(f"獲取圖檔失敗: {domain}{href}")      # 圖片無法下載，刪除 Markdown 中的連結
                    print(f"刪除圖檔連結")
                    img_reg_del = rf'\!\[[^\]]*\]\({href}\)'
                    md_content = re.sub(img_reg_del, '', md_content)


        # 內容處理：翻譯
        trans_content = gpt_e2m(md_content)    # 翻譯文

        if title and md_content and trans_content and source_page :              # 若四者都存在，存進檔案中
            save_to_file(
                post_title=title, 
                post_source_page=source_page, 
                post_content=f'# 中文版：\n{trans_content}\n# 原文版：\n{md_content} ', 
                slug=slug,
                folder_path=site_folder , 
                file_type = 'txt')

if __name__ == '__main__':

    # 創建 CrawlerProcess 對象，並加載 Scrapy 的設置
    process = CrawlerProcess(get_project_settings())

    # 執行指定的蜘蛛 'spider1'
    process.crawl(Spider1Spider)

    # 開始運行
    process.start()  # 這行會阻塞，直到所有的蜘蛛完成運行

    input("按任意鍵以退出...")  # 這行會等待你按下按鍵後才會關閉窗口
