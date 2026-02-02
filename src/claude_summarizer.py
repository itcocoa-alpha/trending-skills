"""
Claude Summarizer - AI 总结和分类技能
使用 Claude API 对技能进行分析、总结和分类
"""
import json
from typing import Dict, List, Optional
from zhipuai import ZhipuAI
import time  # 增加 time 模块

from src.config import ZHIPU_API_KEY, ANTHROPIC_BASE_URL, CLAUDE_MODEL, CLAUDE_MAX_TOKENS


# 分类定义
CATEGORIES = {
    "frontend": "前端开发",
    "backend": "后端开发",
    "mobile": "移动开发",
    "devops": "运维/部署",
    "video": "视频处理",
    "animation": "动画",
    "data": "数据处理",
    "ai": "AI/ML",
    "testing": "测试",
    "marketing": "营销/SEO",
    "documentation": "文档",
    "design": "设计",
    "database": "数据库",
    "security": "安全",
    "other": "其他"
}


class ClaudeSummarizer:
    """AI 总结和分类技能"""

    def __init__(self, api_key: str = None, base_url: str = None):
        """
        初始化 Claude 客户端

        Args:
            api_key: API 密钥，默认从环境变量读取
            base_url: API 基础 URL，默认从环境变量读取
        """
        self.api_key = api_key or ZHIPU_API_KEY
        self.base_url = base_url or ANTHROPIC_BASE_URL
        self.model = CLAUDE_MODEL
        self.max_tokens = CLAUDE_MAX_TOKENS

        if not self.api_key:
            raise ValueError("ZHIPU_API_KEY 环境变量未设置")

        try:
            self.client = ZhipuAI(
                base_url=self.base_url,
                api_key=self.api_key
            )
            print(f"✅ 智谱客户端初始化成功")
        except Exception as e:
            raise Exception(f"智谱客户端初始化失败: {e}")

    def summarize_and_classify(self, details: List[Dict]) -> List[Dict]:
        """
        批量总结和分类技能

        Args:
            details: 技能详情列表

        Returns:
            [
                {
                    "name": "remotion-best-practices",
                    "summary": "用 React 代码创建视频的最佳实践",
                    "description": "程序化视频生成框架 Remotion 的最佳实践集合",
                    "use_case": "视频自动化、个性化视频生成、数据可视化视频",
                    "solves": ["程序化视频", "字幕生成", "3D动效", "音频处理"],
                    "category": "video",
                    "category_zh": "视频处理"
                },
                ...
            ]
        """
        if not details:
            return []

        batch_size = 5
        total = len(details)
        total_batches = (total + batch_size - 1) // batch_size
        print(f"🤖 正在调用 智谱 分析 {total} 个技能（每批 {batch_size} 个）...")

        all_results: List[Dict] = []
        for batch_index in range(total_batches):
            start = batch_index * batch_size
            end = min(start + batch_size, total)
            batch_details = details[start:end]
            print(f"   批次 {batch_index + 1}/{total_batches}: {len(batch_details)} 个")

            batch_results = self._summarize_batch(batch_details)
            batch_results = self._fill_missing_results(batch_results, batch_details)
            all_results.extend(batch_results)

        return all_results

    def _summarize_batch(self, details: List[Dict]) -> List[Dict]:
        """单批次调用智谱分析"""
        # 构建批量分析 Prompt
        prompt = self._build_batch_prompt(details)

        # --- 优化点：增加重试逻辑 ---
        max_retries = 3
        retry_delay = 5  # 失败后等待 5 秒再重试

        for attempt in range(max_retries):
            try:
                # 显式增加 timeout 参数（单位：秒）
                response = self.client.chat.completions.create(
                    model=self.model,
                    max_tokens=self.max_tokens,
                    temperature=0.3,
                    timeout=60,  # 这里的 timeout 很重要
                    messages=[
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ]
                )

                result_text = response.choices[0].message.content
                print(f"✅ 智谱 响应成功 (尝试第 {attempt + 1} 次)")

                # 解析结果
                return self._parse_batch_response(result_text, details)

            except Exception as e:
                print(f"⚠️ 第 {attempt + 1} 次尝试失败: {e}")
                if attempt < max_retries - 1:
                    print(f"   将在 {retry_delay} 秒后重试...")
                    time.sleep(retry_delay)
                else:
                    print(f"❌ 智谱 API 最终调用失败，进入降级流程")
                    return self._fallback_summaries(details)

        return self._fallback_summaries(details)

    def _fill_missing_results(self, results: List[Dict], details: List[Dict]) -> List[Dict]:
        """确保每个技能都有结果，缺失则回退填充"""
        existing_names = {r.get("name") for r in results if isinstance(r, dict)}
        missing_details = [d for d in details if d.get("name") not in existing_names]
        if not missing_details:
            return results
        return results + self._fallback_summaries(missing_details)

    def _build_batch_prompt(self, details: List[Dict]) -> str:
        """
        构建批量分析的 Prompt

        Args:
            details: 技能详情列表

        Returns:
            Prompt 字符串
        """
        # 构建技能列表
        skills_text = ""
        for i, detail in enumerate(details, 1):
            skills_text += f"\n{'='*60}\n"
            skills_text += f"【技能 {i}】\n"
            skills_text += f"名称: {detail.get('name')}\n"
            skills_text += f"拥有者: {detail.get('owner')}\n"
            skills_text += f"URL: {detail.get('url')}\n"

            if detail.get("when_to_use"):
                skills_text += f"\n用途说明:\n{detail.get('when_to_use')}\n"

            if detail.get("rules"):
                skills_text += f"\n规则列表 ({len(detail.get('rules'))} 条):\n"
                for rule in detail.get("rules")[:5]:
                    skills_text += f"  - {rule.get('file')}: {rule.get('desc')}\n"
                if len(detail.get("rules")) > 5:
                    skills_text += f"  ... 还有 {len(detail.get('rules')) - 5} 条\n"

        # 构建分类说明
        category_text = "\n".join([
            f"  - {key}: {zh}"
            for key, zh in CATEGORIES.items()
        ])

        prompt = f"""你是一个技能分析专家。请分析以下 {len(details)} 个技能，为每个技能生成摘要和分类。

{skills_text}

---

【任务要求】

对每个技能提取以下信息：

1. **summary**: 一句话摘要（不超过30字）
   - 简洁描述这个技能是什么

2. **description**: 详细描述（50-100字）
   - 详细说明技能的功能和价值

3. **use_case**: 使用场景
   - 谁在什么情况下会用到这个技能

4. **solves**: 解决的问题列表
   - 3-5个关键词或短语
   - 描述这个技能解决什么具体问题

5. **category**: 选择一个分类
   可选分类:
{category_text}

6. **category_zh**: 中文分类名
   - 对应 category 的中文名称

【输出格式】

严格按照以下 JSON 数组格式输出，不要有任何其他文字说明：

```json
[
  {{
    "name": "skill-name",
    "summary": "一句话摘要",
    "description": "详细描述",
    "use_case": "使用场景",
    "solves": ["问题1", "问题2", "问题3"],
    "category": "frontend",
    "category_zh": "前端开发"
  }}
]
```

【重要】
- 只输出 JSON 数组，不要有任何其他说明文字
- 确保 JSON 格式正确有效
- name 必须与输入的技能名称完全一致
- solves 数组包含 3-5 个问题关键词
"""

        return prompt

    def _parse_batch_response(self, result_text: str, original_details: List[Dict]) -> List[Dict]:
        """
        解析 Claude 的批量响应

        Args:
            result_text: Claude 响应文本
            original_details: 原始技能详情

        Returns:
            解析后的技能列表
        """
        # 清理可能的 markdown 代码块标记
        result_text = result_text.strip()
        if result_text.startswith("```json"):
            result_text = result_text[7:]
        if result_text.startswith("```"):
            result_text = result_text[3:]
        if result_text.endswith("```"):
            result_text = result_text[:-3]
        result_text = result_text.strip()

        try:
            results = json.loads(result_text)

            if not isinstance(results, list):
                results = [results]

            # 验证并补充信息
            validated_results = []
            original_map = {d["name"]: d for d in original_details}

            for result in results:
                if not isinstance(result, dict):
                    continue

                name = result.get("name")

                # 确保 name 存在
                if not name:
                    continue

                # 从原始数据中获取额外信息
                original = original_map.get(name, {})

                validated_result = {
                    "name": name,
                    "summary": result.get("summary", f"{name} 技能"),
                    "description": result.get("description", ""),
                    "use_case": result.get("use_case", ""),
                    "solves": result.get("solves", []),
                    "category": result.get("category", "other"),
                    "category_zh": result.get("category_zh", CATEGORIES.get("other", "其他")),
                    "rules_count": original.get("rules_count", 0),
                    "owner": original.get("owner", ""),
                    "url": original.get("url", "")
                }

                validated_results.append(validated_result)

            print(f"✅ 成功解析 {len(validated_results)} 个技能的 AI 分析")
            return validated_results

        except json.JSONDecodeError as e:
            print(f"❌ JSON 解析失败: {e}")
            print(f"   原始响应: {result_text[:500]}...")
            return self._fallback_summaries(original_details)

    def _fallback_summaries(self, details: List[Dict]) -> List[Dict]:
        """
        降级方案：当 AI 分析失败时使用基本信息

        Args:
            details: 技能详情列表

        Returns:
            基本的技能摘要列表
        """
        results = []

        for detail in details:
            name = detail.get("name", "unknown")
            results.append({
                "name": name,
                "summary": f"{name} - AI 分析暂不可用",
                "description": f"技能名称: {name}",
                "use_case": "待分析",
                "solves": ["待分析"],
                "category": "other",
                "category_zh": "其他",
                "rules_count": detail.get("rules_count", 0),
                "owner": detail.get("owner", ""),
                "url": detail.get("url", ""),
                "fallback": True
            })

        return results


def summarize_skills(details: List[Dict]) -> List[Dict]:
    """便捷函数：总结和分类技能"""
    summarizer = ClaudeSummarizer()
    return summarizer.summarize_and_classify(details)
