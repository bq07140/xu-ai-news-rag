import os
import pickle
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer
from typing import List, Tuple, Optional

class VectorStore:
    """FAISS向量存储管理类"""
    
    def __init__(self, model_name: str = 'all-MiniLM-L6-v2', index_path: str = 'faiss_index'):
        """
        初始化向量存储
        
        Args:
            model_name: 嵌入模型名称
            index_path: 索引存储路径
        """
        self.model_name = model_name
        self.index_path = index_path
        self.model = None
        self.index = None
        self.doc_ids = []  # 存储文档ID映射
        self.dimension = 384  # all-MiniLM-L6-v2的向量维度
        
        # 确保索引目录存在
        os.makedirs(index_path, exist_ok=True)
        
        # 加载模型
        self._load_model()
        
        # 加载或创建索引
        self._load_or_create_index()
    
    def _load_model(self):
        """加载嵌入模型"""
        print(f"Loading embedding model: {self.model_name}...")
        self.model = SentenceTransformer(self.model_name)
        print("Model loaded successfully.")
    
    def _load_or_create_index(self):
        """加载或创建FAISS索引"""
        index_file = os.path.join(self.index_path, 'faiss.index')
        mapping_file = os.path.join(self.index_path, 'doc_mapping.pkl')
        
        if os.path.exists(index_file) and os.path.exists(mapping_file):
            # 加载现有索引
            self.index = faiss.read_index(index_file)
            with open(mapping_file, 'rb') as f:
                self.doc_ids = pickle.load(f)
            print(f"Loaded existing index with {self.index.ntotal} vectors.")
        else:
            # 创建新索引 (使用L2距离)
            self.index = faiss.IndexFlatL2(self.dimension)
            self.doc_ids = []
            print("Created new FAISS index.")
    
    def save_index(self):
        """保存索引到磁盘"""
        index_file = os.path.join(self.index_path, 'faiss.index')
        mapping_file = os.path.join(self.index_path, 'doc_mapping.pkl')
        
        faiss.write_index(self.index, index_file)
        with open(mapping_file, 'wb') as f:
            pickle.dump(self.doc_ids, f)
        print(f"Index saved with {self.index.ntotal} vectors.")
    
    def encode_text(self, text: str) -> np.ndarray:
        """
        将文本编码为向量
        
        Args:
            text: 输入文本
            
        Returns:
            向量数组
        """
        return self.model.encode(text, convert_to_numpy=True)
    
    def encode_texts(self, texts: List[str]) -> np.ndarray:
        """
        批量编码文本
        
        Args:
            texts: 文本列表
            
        Returns:
            向量数组
        """
        return self.model.encode(texts, convert_to_numpy=True, show_progress_bar=True)
    
    def add_document(self, doc_id: int, text: str):
        """
        添加单个文档到索引
        
        Args:
            doc_id: 文档ID
            text: 文档文本内容
        """
        vector = self.encode_text(text)
        vector = vector.reshape(1, -1).astype('float32')
        
        self.index.add(vector)
        self.doc_ids.append(doc_id)
        self.save_index()
    
    def add_documents(self, doc_ids: List[int], texts: List[str]):
        """
        批量添加文档到索引
        
        Args:
            doc_ids: 文档ID列表
            texts: 文档文本列表
        """
        if len(doc_ids) != len(texts):
            raise ValueError("doc_ids and texts must have the same length")
        
        vectors = self.encode_texts(texts)
        vectors = vectors.astype('float32')
        
        self.index.add(vectors)
        self.doc_ids.extend(doc_ids)
        self.save_index()
    
    def search(self, query: str, k: int = 10) -> List[Tuple[int, float]]:
        """
        搜索最相似的文档
        
        Args:
            query: 查询文本
            k: 返回结果数量
            
        Returns:
            [(doc_id, similarity_score), ...] 列表
        """
        if self.index.ntotal == 0:
            return []
        
        # 编码查询
        query_vector = self.encode_text(query)
        query_vector = query_vector.reshape(1, -1).astype('float32')
        
        # 搜索
        k = min(k, self.index.ntotal)
        distances, indices = self.index.search(query_vector, k)
        
        # 将L2距离转换为相似度分数 (0-1之间，越大越相似)
        # 使用负指数函数转换: similarity = exp(-distance)
        similarities = np.exp(-distances[0])
        
        # 构建结果
        results = []
        for idx, similarity in zip(indices[0], similarities):
            if idx < len(self.doc_ids):
                doc_id = self.doc_ids[idx]
                results.append((doc_id, float(similarity)))
        
        return results
    
    def remove_document(self, doc_id: int) -> bool:
        """
        从索引中移除文档
        注意: FAISS不支持直接删除，需要重建索引
        
        Args:
            doc_id: 文档ID
            
        Returns:
            是否成功移除
        """
        if doc_id not in self.doc_ids:
            return False
        
        # 找到文档在列表中的所有位置
        indices_to_remove = [i for i, did in enumerate(self.doc_ids) if did == doc_id]
        
        # 重建索引（排除要删除的文档）
        if self.index.ntotal > 0:
            try:
                # 获取所有向量 - 使用正确的FAISS API
                vectors = []
                for i in range(self.index.ntotal):
                    vec = self.index.reconstruct(i)
                    vectors.append(vec)
                vectors = np.array(vectors, dtype='float32')
                
                # 创建新索引
                new_index = faiss.IndexFlatL2(self.dimension)
                new_doc_ids = []
                
                # 添加未删除的向量
                for i in range(len(vectors)):
                    if i not in indices_to_remove:
                        new_index.add(vectors[i:i+1])
                        new_doc_ids.append(self.doc_ids[i])
                
                self.index = new_index
                self.doc_ids = new_doc_ids
                self.save_index()
            except Exception as e:
                print(f"Error removing document: {str(e)}")
                return False
        
        return True
    
    def get_index_size(self) -> int:
        """获取索引中的文档数量"""
        return self.index.ntotal
    
    def clear_index(self):
        """清空索引"""
        self.index = faiss.IndexFlatL2(self.dimension)
        self.doc_ids = []
        self.save_index()


