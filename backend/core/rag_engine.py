from typing import List, Dict, Optional
from .vector_store import vector_store
from .llm_client import llm_client

class RAGEngine:
    def __init__(self):
        self.system_prompt = """你是一位专业的AI营养师,具备丰富的临床营养学知识和实践经验。
你的职责是根据用户的体检报告和口味偏好，提供科学、个性化的饮食建议。​
请遵循以下原则：​
1. 所有建议必须基于循证营养学，有科学依据​
2. 根据体检指标异常项给出针对性的饮食调整建议​
3. 充分考虑用户的口味偏好和饮食禁忌​
4. 食谱要实用、可操作，适合家庭烹饪​
5. 对于严重异常指标，建议用户就医，你只提供饮食辅助建议"""
    
    async def retrieve(self, query: str, filter_dict: Optional[Dict] = None, top_k: int = 5) -> List[Dict]:
        return await vector_store.search(query, top_k=top_k, filter_dict=filter_dict)
    
    def build_context(self, docs: List[Dict]) -> str:
        if not docs:
            return "未找到相关的专业知识，我将基于通用营养学知识提供建议。"
        context_parts = ["以下是相关的营养学知识参考：\n"]
        for i, doc in enumerate(docs, 1):
            context_parts.append(f"【知识{i}】\n{doc['content']}")
        return "\n\n".join(context_parts)
    
    async def generate_meal_plan(self, health_data: Dict, taste_preferences: Dict, user_info: Dict) -> str:
        # 分析健康问题​
        health_issues = []
        if health_data.get("fasting_glucose", 0) > 6.1: health_issues.append("高血糖")
        if health_data.get("total_cholesterol", 0) > 5.2: health_issues.append("高胆固醇")
        if health_data.get("triglycerides", 0) > 1.7: health_issues.append("高甘油三酯")
        if health_data.get("systolic_bp", 0) >= 140: health_issues.append("高血压")
        if health_data.get("uric_acid", 0) > 420: health_issues.append("高尿酸")
        
        # RAG检索​
        query = " ".join(["营养食谱设计"] + health_issues)
        docs = await self.retrieve(query, top_k=8)
        context = self.build_context(docs)
        
        # 构建提示词并调用LLM​
        prompt = self._build_prompt(health_data, taste_preferences, user_info, health_issues, context)
        messages = [{"role": "system", "content": self.system_prompt}, {"role": "user", "content": prompt}]
        return await llm_client.chat(messages, temperature=0.8, max_tokens=8192)
    
    async def chat(self, message: str, context_data: Optional[Dict] = None) -> str:
        docs = await self.retrieve(message, top_k=5)
        context = self.build_context(docs)
        messages = [{"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": f"用户咨询：{message}\n\n相关知识参考:{context}"}]
        return await llm_client.chat(messages, temperature=0.7, max_tokens=2048)

rag_engine = RAGEngine()