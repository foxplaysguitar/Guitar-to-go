import os
import re
import html2text as h2t
import scrapy
from openai import OpenAI
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

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
    api_key = 'my-api-key'

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

    def parse(self, response):
        if "guitargirlmag.com" in response.url:
            yield from self.parse_href_guitargirlmag(response)
        # elif "guitarworld.com" in response.url:
        #     yield from self.parse_guitarworld(response)

    def parse_href_guitargirlmag(self, response):
        # 根據規則抓取內容頁的URL
        for href in response.css('a[href*="music-news"]::attr(href)').getall():
            if href != 'https://guitargirlmag.com/category/news/music-news/' :
                yield response.follow(href, self.parse_content_guitargirlmag)
                break

    def parse_content_guitargirlmag(self, response):
        # 取得內容
        title = response.css('title::text').get()
        content = response.css('article .vc_column_container.td-pb-span8 .wpb_wrapper').get()
        source_page = response.css('link[rel="canonical"]::attr(href)').get()

        # 標題防呆處理
        title = re.sub(r':','：',title)

        # 內容處理：轉化成 MarkDown
        content_prev = html_to_md(content)      # 原文
        content_next = gpt_e2m(content_prev)    # 翻譯文

        # 內容處理：刪除連結
        content_prev = delete_md_links(content_prev)
        content_next = delete_md_links(content_next)
        
        if title and content_prev and content_next and source_page :              # 若四者都存在，存進檔案中
            save_to_file(title, source_page, f'# 中文版：\n{content_next}\n# 原文版：\n{content_prev} ' , file_type = 'txt')


if __name__ == '__main__':

    # 創建 CrawlerProcess 對象，並加載 Scrapy 的設置
    process = CrawlerProcess(get_project_settings())

    # 執行指定的蜘蛛 'spider1'
    process.crawl(Spider1Spider)

    # 開始運行
    process.start()  # 這行會阻塞，直到所有的蜘蛛完成運行
