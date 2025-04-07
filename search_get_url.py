import requests
import json
import re
from urllib.parse import quote
import os
import time

# Common headers and cookies
headers = {
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
    'cache-control': 'max-age=0',
    'priority': 'u=0, i',
    'referer': 'https://www.zhihu.com/search',
    'sec-ch-ua': '"Chromium";v="134", "Not:A-Brand";v="24", "Microsoft Edge";v="134"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'document',
    'sec-fetch-mode': 'navigate',
    'sec-fetch-site': 'same-origin',
    'sec-fetch-user': '?1',
    'upgrade-insecure-requests': '1',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36'
}

# Cookies
cookies = {
    'd_c0': 'AZBevr07URWPTleg9YveEN_B78Fj9e0Xu2M=|1659008731',
    '_9755xjdesxxd_': '32',
    'YD00517437729195%3AWM_TID': '6aojNfFMktVFRRRBARKUCXQwiBQiwwsg',
    'YD00517437729195%3AWM_NI': 'iCw0jAQPbTD0%2B%2FV7hbR46BNIDYYOoFRZVKLD0AkR%2Foafd1FPeuYlgTIwbbZ7dtnbqys3wL4IowouzjxWHD72EsxHJjcYisqcikihhAEyApa3s05Wuo3Z0o504cWvzSJZSDQ%3D',
    'YD00517437729195%3AWM_NIKE': '9ca17ae2e6ffcda170e2e6eeaedb46979c87aac950f2968eb2d85f829e8aacc5338798af8eee4aba93a1d2ed2af0fea7c3b92aab9db9d1e94b9390aeb5c73ce9f19ad8eb6a92ecfaa3cd43888797b0ee4e92869aaccf50f49fa5b3ae65a3baacd2c55ca7ab978de6608ba9ae83d93da8aca283f473b1edb9adb743ada9a196f962bc8988a5b63a87adb8a9c962a187a794f469abb5a789eb4b87a78f91e439b1f0fbb8f865f1860090b83cf8bd9997f9598a869da5d437e2a3',
    'q_c1': '1458c23b7f2042c795b2667c0f9ac4a2|1701005520000|1701005520000',
    '_zap': '2fedd565-085d-4c78-8bb1-c4f1ce0dca9e',
    'z_c0': '2|1:0|10:1741952821|4:z_c0|80:MS4xYllOY1RRQUFBQUFtQUFBQVlBSlZUWkRzdG1pbTA3ZFhKQjd5R0QxMVdPYTk0U3ZUWWdnc2hBPT0=|6bdc6b73d3ac0ce8bfe569a16ca34cc2cdffbd6e9e16f5a693fc48a958335803',
    '_xsrf': 'T7oOTDECXKunrZU3Ak3jL8GzblypbSew',
    'Hm_lvt_98beee57fd2ef70ccdd5ca52b9740c49': '1741008685,1743320377',
    'HMACCOUNT': 'AF1F7EAE7652BBE1',
    'Hm_lpvt_98beee57fd2ef70ccdd5ca52b9740c49': '1743321054',
    '__zse_ck': '004_49JPncXTcUpQGklyUCeFW3mE/bUU2ZmJ8uSYM=dk2czGgcsCNvtXZYoZJGGJ4u2bq2upQbDW6yyXHYQ1j6/C2VkpOG6G7N5R3CmRqjATqSmlQJogFP6fd1SP0Ou7anTh-xoFBQ8Kd/5Nfcfv2jaAWXjjziYcKK5n4M7W9FnfUn47GmBvPqk64mYj1hClDR+1hmDhunhqT7VaIDsX/v+GEqqwYRNdcFU6Tszw1SwAEo7Y/mqw67H0wt0MpAYNsqRKu',
    'tst': 'r',
    'BEC': '6c53268835aec2199978cd4b4f988f8c'
}

def search_zhihu(keyword, offset, search_type='article',the_url=''):
    # URL encode the keyword
    encoded_keyword = quote(keyword)
    # offset = 0

    # Search API URL with offset parameter
    if(the_url == ''):
        search_url = (f"https://www.zhihu.com/api/v4/search_v3?gk_version=gz-gaokao&t=general&q="
                  f"{encoded_keyword}&correction=1&offset={offset}&limit=20&filter_fields=&lc_idx="
                  f"{offset}&show_all_topics=0&search_source=Filter&vertical={search_type}&sort=created_time")
    else :
        search_url = the_url


    # Additional headers for API request
    api_headers = {
        'x-api-version': '3.0.91',
        'x-app-za': 'OS=Web',
        'x-requested-with': 'fetch',
        'x-zse-93': '101_3_3.0',
        'x-zse-96': '2.0_JJZDu1/IoDUSiK3GBxg9hikIA7/RH2LoLUflWivJ56Asb6qO=eToDaOpp8/95XJl'
    }

    # Combine headers
    final_headers = {**headers, **api_headers}

    try:
        # Make the request
        response = requests.get(
            search_url,
            headers=final_headers,
            cookies=cookies
        )

        # Check if the request was successful
        if response.status_code == 200:
            # Parse the JSON response
            data = response.json()
            return data
        else:
            print(f"Request failed with status code: {response.status_code}")
            return None

    except Exception as e:
        print(f"An error occurred: {e}")
        return None

def load_existing_urls(file_path):
    existing_urls = set()
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                url = line.split(' ')[0]
                existing_urls.add(url)
    return existing_urls

def save_results_to_file(results, article_file_path, answer_file_path, existing_article_urls, existing_answer_urls):
    with open(article_file_path, 'a', encoding='utf-8') as article_file, \
         open(answer_file_path, 'a', encoding='utf-8') as answer_file:
        for item in results.get('data', []):
            title = item.get('highlight', {}).get('title', '')
            # Remove <em> and </em> tags
            clean_title = re.sub(r'<\/?em>', '', title)
            obj = item.get('object', {})
            obj_type = obj.get('type', '')
            obj_id = obj.get('id', '')
            url = ''
            if obj_type == 'article':
                url = f"https://zhuanlan.zhihu.com/p/{obj_id}"
                if url and clean_title:
                    if url in existing_article_urls:
                        print(f"Article URL already exists: {url}")
                    else:
                        article_file.write(f"{url} {clean_title}\n")
                        existing_article_urls.add(url)
            elif obj_type == 'answer':
                question_id = obj.get('question', {}).get('id', '')
                url = f"https://www.zhihu.com/question/{question_id}/answer/{obj_id}"
                if url and clean_title:
                    if url in existing_answer_urls:
                        print(f"Answer URL already exists: {url}")
                    else:
                        answer_file.write(f"{url} {clean_title}\n")
                        existing_answer_urls.add(url)

def main():
    # Search keyword
    keyword = "求职"
    offset = 0  # Initial offset value
    article_file_path = 'zhihu_article_results.txt'
    answer_file_path = 'zhihu_answer_results.txt'
    search_type = 'article'
    # search_type = 'answer'
    # search_type = ''

    # Load existing URLs
    existing_article_urls = load_existing_urls(article_file_path)
    existing_answer_urls = load_existing_urls(answer_file_path)
    next_url = ''

    while True:
        print(f"Current offset: {offset}，existing article URLs: {len(existing_article_urls)}, existing answer URLs: {len(existing_answer_urls)}")
        # Perform the search
        results = search_zhihu(keyword, offset, search_type, next_url)
        # results = search_zhihu(keyword, offset, search_type)
        if not results or not results.get('data'):
            print(f"Error or no data returned: {results}")
            break

        # Save results to file
        save_results_to_file(results, article_file_path, answer_file_path, existing_article_urls, existing_answer_urls)


        # Get next page URL
        # next_url = results.get('paging', {}).get('next', '')
        #   从the_url中获取offset
        # offset = int(re.findall(r'offset=(\d+)', next_url)[0])
        # is_end = results.get('paging', {}).get('is_end', False)

        # TODO：从next_url中获取search_hash_id,且搞清楚滑动浏览器时发送的batch是什么
        if offset == 0:
            offset += 9
        else:
            offset += 10

        # if is_end:
        #     print("No more results.")
        #     break


        # Sleep for 2 seconds
        time.sleep(2)

if __name__ == "__main__":
    main()