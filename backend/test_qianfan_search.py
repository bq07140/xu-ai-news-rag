import os
import requests
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv('SEARCH_API_KEY')
api_url = 'https://qianfan.baidubce.com/v2/ai_search/web_search'

print("=" * 60)
print("百度千帆 AI 搜索测试")
print("=" * 60)

if not api_key:
    print("未配置 SEARCH_API_KEY")
    print("\n请在 backend/.env 文件中添加:")
    print("SEARCH_API_KEY=你的_AppBuilder_API_Key")
    exit(1)

print(f"API Key: {api_key[:20]}...")
print(f"API URL: {api_url}")

# 测试搜索
headers = {
    'Authorization': f'Bearer {api_key}',
    'Content-Type': 'application/json'
}

payload = {
    'messages': [
        {
            'content': '人工智能最新进展',
            'role': 'user'
        }
    ],
    'search_source': 'baidu_search_v2',
    'resource_type_filter': [
        {
            'type': 'web',
            'top_k': 5
        }
    ],
    'search_recency_filter': 'year'
}

print("\n" + "=" * 60)
print("发送搜索请求...")
print("=" * 60)
print(f"查询: {payload['messages'][0]['content']}")
print(f"返回数量: {payload['resource_type_filter'][0]['top_k']}")
print(f"时间范围: {payload['search_recency_filter']}")

try:
    response = requests.post(api_url, json=payload, headers=headers, timeout=15)
    
    print(f"\n状态码: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print("\n搜索成功!")
        
        # 尝试提取搜索结果
        # 百度千帆AI搜索的返回格式：{'request_id': '...', 'references': [...]}
        search_results = data.get('references', [])
        
        if not search_results:
            # 尝试其他可能的字段
            search_results = data.get('result', {}).get('search_results', [])
        if not search_results:
            search_results = data.get('search_results', data.get('results', []))
        
        if search_results:
            print(f"\n找到 {len(search_results)} 个结果:\n")
            for i, item in enumerate(search_results, 1):
                title = item.get('title', 'N/A')
                url = item.get('url', item.get('link', 'N/A'))
                abstract = item.get('abstract', item.get('snippet', item.get('content', 'N/A')))
                
                if isinstance(abstract, str) and len(abstract) > 100:
                    abstract = abstract[:100] + '...'
                
                print(f"{i}. {title}")
                print(f"   URL: {url}")
                print(f"   摘要: {abstract}\n")
        else:
            print("\n未找到搜索结果")
            print(f"完整响应结构: {list(data.keys())}")
            print(f"\n完整响应:\n{data}")
    else:
        print(f"\nAPI 错误 {response.status_code}:")
        print(response.text)
        
except requests.exceptions.Timeout:
    print("\n请求超时，请检查网络连接")
except requests.exceptions.HTTPError as e:
    print(f"\nHTTP 错误: {e}")
    if hasattr(e, 'response'):
        print(f"响应内容: {e.response.text}")
except Exception as e:
    print(f"\n请求失败: {str(e)}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 60)
print("测试完成")
print("=" * 60)

