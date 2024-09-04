import os
import re
import html2text as h2t
import scrapy
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

def html_to_md(html):
    # 設定 Markdown 轉換器
    h = h2t.HTML2Text()
    h.ignore_links = False

    # 執行轉換，獲取Markdown內容
    md_content = h.handle(html)
    return md_content

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

    def parse_content_guitargirlmag(self, response):
        # 取得內容
        title = response.css('title::text').get()
        content = response.css('article .vc_column_container.td-pb-span8 .wpb_wrapper').get()
        source_page = response.css('link[rel="canonical"]::attr(href)').get()

        # 防呆處理
        title = re.sub(r':','：',title)

        if title and content and source_page :              # 若三者都存在，存進檔案中
            save_to_file(title, source_page, html_to_md(content), file_type = 'txt')


if __name__ == '__main__':

    # 創建 CrawlerProcess 對象，並加載 Scrapy 的設置
    process = CrawlerProcess(get_project_settings())

    # 執行指定的蜘蛛 'spider1'
    process.crawl(Spider1Spider)

    # 開始運行
    process.start()  # 這行會阻塞，直到所有的蜘蛛完成運行
