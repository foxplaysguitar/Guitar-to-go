import os
import re
import html2text as h2t
import scrapy
import requests as rq
from PIL import Image
from openai import OpenAI
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
import os

# 全域變數設定
ROOT_PATH = os.path.expanduser("~")
DESKTOP_PATH = os.path.join(ROOT_PATH, 'Desktop')
GTG_ARTICLES_FOLDER = os.path.join(DESKTOP_PATH, 'gtg-articles')

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
    
    # 放置 key（之後要換！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！）
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

# 文案存進檔案
def save_to_file(post_title, post_source_page, post_content, file_type , folder_path = "D:/guitar-articles"):
    # 檢查資料夾是否存在，若不存在則創建資料夾
    if not os.path.exists(folder_path):
        print("資料夾不存在，創建資料夾中...")
        os.makedirs(folder_path)
        print("資料夾創建成功！")
    else :
        print("確認資料夾存在，進入資料夾...")

    # 設定 txt 檔案的完整路徑，假設檔案名稱是 title.txt
    file_path = os.path.join(folder_path, f"{post_title}.{file_type}")

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
    name = "spider1"
    allowed_domains = ["guitargirlmag.com", "guitarworld.com"]
    start_urls = [
        'https://guitargirlmag.com/category/news/music-news/',
        'https://www.guitarworld.com/news'
    ]

    def parse(self, response):  # response 代表 requests 後回傳的內容

        # 確認主資料夾是否存在，若否，建立一個！
        if not os.path.exists(GTG_ARTICLES_FOLDER) :
            os.makedirs(GTG_ARTICLES_FOLDER)

        if "guitargirlmag.com" in response.url:

            site_folder = os.path.join(GTG_ARTICLES_FOLDER, "guitargirlmag.com")

            # 確認網站資料夾是否存在
            if not os.path.exists(site_folder):
                os.makedirs(site_folder)

            yield response.follow(      # 傳遞當前爬取的網站給對應function 處理，同時用 meta 傳遞資訊
                response.url,
                self.parse_href_guitargirlmag,
                meta={'site_folder': site_folder}
            )
        

    def parse_href_guitargirlmag(self, response):
        # 根據規則抓取內容頁的URL
        for href in response.css('a[href*="music-news"]::attr(href)').getall():
            if href != 'https://guitargirlmag.com/category/news/music-news/' :
                
                yield response.follow(
                    href, 
                    self.parse_content_guitargirlmag, 
                    meta={'site_folder':response.meta.get('site_folder')}   # 從 response 的 meta 中取得 site_folder 的資訊
                    )

    def parse_content_guitargirlmag(self, response):
        # 取得內容
        title = response.css('title::text').get()
        content = response.css('article .vc_column_container.td-pb-span8 .wpb_wrapper').get()
        source_page = response.css('link[rel="canonical"]::attr(href)').get()
        domain = re.findall('https?:\/\/[^\/]+', source_page)[0]
        slug = re.findall('([^\/]+)\/?$', source_page)[0]
        site_folder = response.meta.get('site_folder')

        # 標題防呆處理
        title = re.sub(r':','：',title)

        # 內容處理：轉化成 MarkDown
        md_content = html_to_md(content)

        # 內容處理：刪除連結
        md_content = delete_md_links(md_content)

        # 內容處理：下載圖檔
        img_reg = '\!\[[^\]]*\]\(([^\)]+)\)'
        img_hrefs = re.findall(img_reg, md_content)
        img_index = 0
        for href in img_hrefs :
            if rq.get(href).status_code == 200:     # 圖片連結可直接下載
                print(f'獲取圖檔成功，正在下載: {href}')
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
                print(f"獲取圖檔失敗： {href}")
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

        # 內容處理：翻譯
        trans_content = gpt_e2m(md_content)    # 翻譯文

        if title and md_content and trans_content and source_page :              # 若四者都存在，存進檔案中
            save_to_file(title, source_page, f'# 中文版：\n{trans_content}\n# 原文版：\n{md_content} ', folder_path=site_folder , file_type = 'txt')


if __name__ == '__main__':

    # 創建 CrawlerProcess 對象，並加載 Scrapy 的設置
    process = CrawlerProcess(get_project_settings())

    # 執行指定的蜘蛛 'spider1'
    process.crawl(Spider1Spider)

    # 開始運行
    process.start()  # 這行會阻塞，直到所有的蜘蛛完成運行
