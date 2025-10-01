import jieba
import jieba.analyse
from collections import Counter
from typing import List, Dict
from datetime import datetime, timedelta

class AnalysisService:
    """数据分析服务"""
    
    @staticmethod
    def extract_keywords(texts: List[str], topK: int = 10) -> List[Dict[str, any]]:
        """
        提取关键词
        
        Args:
            texts: 文本列表
            topK: 返回top K个关键词
            
        Returns:
            [{'keyword': str, 'count': int, 'weight': float}, ...]
        """
        if not texts:
            return []
        
        # 合并所有文本
        combined_text = ' '.join(texts)
        
        # 使用jieba的TF-IDF提取关键词
        keywords_with_weight = jieba.analyse.extract_tags(
            combined_text,
            topK=topK,
            withWeight=True
        )
        
        # 统计每个关键词的出现次数
        all_words = []
        for text in texts:
            words = jieba.cut(text)
            all_words.extend(words)
        
        word_counter = Counter(all_words)
        
        # 构建结果
        results = []
        for keyword, weight in keywords_with_weight:
            results.append({
                'keyword': keyword,
                'count': word_counter.get(keyword, 0),
                'weight': float(weight)
            })
        
        return results
    
    @staticmethod
    def analyze_category_distribution(documents: List[Dict]) -> Dict[str, int]:
        """
        分析分类分布
        
        Args:
            documents: 文档列表
            
        Returns:
            {'category': count, ...}
        """
        categories = [doc.get('category', '未分类') for doc in documents]
        return dict(Counter(categories))
    
    @staticmethod
    def analyze_source_distribution(documents: List[Dict]) -> Dict[str, int]:
        """
        分析来源分布
        
        Args:
            documents: 文档列表
            
        Returns:
            {'source': count, ...}
        """
        sources = [doc.get('source', '未知') for doc in documents]
        return dict(Counter(sources))
    
    @staticmethod
    def analyze_time_trend(documents: List[Dict], days: int = 7) -> Dict[str, int]:
        """
        分析时间趋势
        
        Args:
            documents: 文档列表
            days: 统计最近N天
            
        Returns:
            {'date': count, ...}
        """
        # 计算日期范围
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        # 按日期统计
        date_counter = Counter()
        
        for doc in documents:
            created_at = doc.get('created_at')
            if created_at:
                # 解析ISO格式日期
                if isinstance(created_at, str):
                    doc_date = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                else:
                    doc_date = created_at
                
                if start_date <= doc_date <= end_date:
                    date_str = doc_date.strftime('%Y-%m-%d')
                    date_counter[date_str] += 1
        
        return dict(date_counter)
    
    @staticmethod
    def generate_summary_report(documents: List[Dict], time_range: str = 'all') -> Dict:
        """
        生成综合分析报告
        
        Args:
            documents: 文档列表
            time_range: 时间范围 (7days, 30days, all)
            
        Returns:
            完整的分析报告
        """
        # 根据时间范围过滤文档
        if time_range == '7days':
            cutoff_date = datetime.utcnow() - timedelta(days=7)
            filtered_docs = [
                doc for doc in documents
                if datetime.fromisoformat(doc['created_at'].replace('Z', '+00:00')) >= cutoff_date
            ]
        elif time_range == '30days':
            cutoff_date = datetime.utcnow() - timedelta(days=30)
            filtered_docs = [
                doc for doc in documents
                if datetime.fromisoformat(doc['created_at'].replace('Z', '+00:00')) >= cutoff_date
            ]
        else:
            filtered_docs = documents
        
        # 提取所有文本内容
        texts = []
        for doc in filtered_docs:
            title = doc.get('title', '')
            summary = doc.get('summary', '')
            content = doc.get('content', '')
            texts.append(f"{title} {summary} {content}")
        
        # 生成报告
        report = {
            'total_documents': len(filtered_docs),
            'time_range': time_range,
            'generated_at': datetime.utcnow().isoformat(),
            'top_keywords': AnalysisService.extract_keywords(texts, topK=10),
            'category_distribution': AnalysisService.analyze_category_distribution(filtered_docs),
            'source_distribution': AnalysisService.analyze_source_distribution(filtered_docs),
        }
        
        # 如果是限定时间范围，添加时间趋势
        if time_range in ['7days', '30days']:
            days = 7 if time_range == '7days' else 30
            report['time_trend'] = AnalysisService.analyze_time_trend(filtered_docs, days=days)
        
        return report


