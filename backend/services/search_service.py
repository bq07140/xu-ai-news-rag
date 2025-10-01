import requests
import os
from typing import List, Dict, Optional

class WebSearchService:
    """百度千帆 AI 搜索服务"""
    
    def __init__(self, api_key: str = '', api_url: str = ''):
        """
        初始化百度千帆搜索服务
        
        Args:
            api_key: 百度 AppBuilder API Key
            api_url: 百度千帆搜索 API URL
        """
        self.api_key = api_key or os.getenv('SEARCH_API_KEY', '')
        # 默认使用百度千帆 AI 搜索接口
        self.api_url = api_url or os.getenv('SEARCH_API_URL', 'https://qianfan.baidubce.com/v2/ai_search/web_search')
        self.secret_key = os.getenv('BAIDU_SECRET_KEY', '')  # 可选
    
    def search(self, query: str, num_results: int = 3) -> List[Dict[str, str]]:
        """
        执行百度千帆 AI 搜索
        
        Args:
            query: 搜索查询
            num_results: 返回结果数量
            
        Returns:
            [{'title': str, 'url': str, 'snippet': str}, ...]
        """
        # 如果没有配置API，返回模拟数据
        if not self.api_key:
            print("未配置百度千帆 API Key，使用模拟数据")
            return self._mock_search(query, num_results)
        
        try:
            # 调用百度千帆 AI 搜索接口
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            }
            
            # 构建请求体
            payload = {
                'messages': [
                    {
                        'content': query,
                        'role': 'user'
                    }
                ],
                'search_source': 'baidu_search_v2',
                'resource_type_filter': [
                    {
                        'type': 'web',
                        'top_k': min(num_results, 20)  # 最多20个结果
                    }
                ],
                'search_recency_filter': 'year'  # 搜索最近一年的内容
            }
            
            print(f"调用百度千帆搜索: {query}")
            response = requests.post(self.api_url, json=payload, headers=headers, timeout=15)
            response.raise_for_status()
            
            data = response.json()
            results = []
            
            # 解析百度千帆返回的结果
            # 千帆AI搜索的返回格式：{'request_id': '...', 'references': [...]}
            search_results = data.get('references', [])
            
            # 如果没有找到 references，尝试其他可能的字段
            if not search_results:
                search_results = data.get('result', {}).get('search_results', [])
            if not search_results:
                search_results = data.get('search_results', data.get('results', []))
            
            for item in search_results[:num_results]:
                # 提取标题、链接和摘要
                title = item.get('title', item.get('Title', ''))
                url = item.get('url', item.get('link', item.get('Url', '')))
                # snippet优先，如果没有则用content
                snippet = item.get('snippet', item.get('abstract', item.get('content', item.get('desc', ''))))
                
                if isinstance(snippet, str):
                    snippet = snippet.replace('\n', ' ')
                    # 限制摘要长度
                    if len(snippet) > 200:
                        snippet = snippet[:200] + '...'
                
                results.append({
                    'title': title,
                    'url': url,
                    'snippet': snippet
                })
            
            print(f"百度千帆搜索成功：找到 {len(results)} 个结果")
            return results
            
        except requests.exceptions.HTTPError as e:
            error_msg = e.response.text if hasattr(e, 'response') else str(e)
            status_code = e.response.status_code if hasattr(e, 'response') else 'Unknown'
            print(f"百度千帆 API 错误 {status_code}: {error_msg}")
            return self._mock_search(query, num_results)
        except Exception as e:
            print(f"百度千帆搜索错误: {str(e)}")
            import traceback
            traceback.print_exc()
            return self._mock_search(query, num_results)
    
    def _mock_search(self, query: str, num_results: int) -> List[Dict[str, str]]:
        """
        模拟搜索结果（用于开发和测试）
        
        Args:
            query: 搜索查询
            num_results: 返回结果数量
            
        Returns:
            模拟的搜索结果列表
        """
        mock_results = [
            {
                'title': f'搜索结果 1：关于"{query}"的最新资讯',
                'url': 'https://example.com/news/1',
                'snippet': f'这是关于{query}的第一条模拟搜索结果。包含了相关的新闻内容和详细信息...'
            },
            {
                'title': f'深度解析：{query}的发展趋势',
                'url': 'https://example.com/analysis/2',
                'snippet': f'本文深入分析了{query}的最新发展动态，提供了专业的见解和预测...'
            },
            {
                'title': f'{query}专题报道 - 权威解读',
                'url': 'https://example.com/report/3',
                'snippet': f'权威媒体对{query}进行了全面报道，涵盖了各个方面的重要信息...'
            }
        ]
        
        return mock_results[:num_results]


class LLMService:
    """大语言模型服务（用于总结和理解）"""
    
    def __init__(self, model_url: str = 'http://localhost:11434'):
        """
        初始化LLM服务
        
        Args:
            model_url: Ollama服务地址
        """
        self.model_url = model_url
        self.model_name = 'qwen2.5:3b'
    
    def summarize_search_results(self, query: str, search_results: List[Dict[str, str]]) -> str:
        """
        总结搜索结果
        
        Args:
            query: 用户查询
            search_results: 搜索结果列表
            
        Returns:
            总结文本
        """
        # 构建提示词
        results_text = '\n\n'.join([
            f"标题：{r['title']}\n来源：{r['url']}\n内容：{r['snippet']}"
            for r in search_results
        ])
        
        prompt = f"""用户问题：{query}

以下是搜索到的相关信息：

{results_text}

请基于以上信息，用简洁的语言回答用户的问题。如果信息不足以回答问题，请说明。"""
        
        try:
            # 调用Ollama API
            response = requests.post(
                f"{self.model_url}/api/generate",
                json={
                    'model': self.model_name,
                    'prompt': prompt,
                    'stream': False
                },
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get('response', '抱歉，无法生成摘要。')
            else:
                return self._generate_simple_summary(search_results)
                
        except Exception as e:
            print(f"LLM service error: {str(e)}")
            return self._generate_simple_summary(search_results)
    
    def _generate_simple_summary(self, search_results: List[Dict[str, str]]) -> str:
        """
        生成简单的摘要（当LLM不可用时）
        
        Args:
            search_results: 搜索结果列表
            
        Returns:
            摘要文本
        """
        if not search_results:
            return "未找到相关信息。"
        
        summary_parts = ["根据网络搜索，我找到了以下信息：\n"]
        
        for i, result in enumerate(search_results, 1):
            summary_parts.append(f"{i}. {result['title']}")
            summary_parts.append(f"   {result['snippet']}\n")
        
        return '\n'.join(summary_parts)


