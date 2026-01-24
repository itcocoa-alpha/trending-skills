"""
HTML Reporter - 生成 HTML 邮件报告
专业邮件排版，无 emoji，符合最佳实践
"""
from typing import Dict, List


class HTMLReporter:
    """生成 HTML 邮件报告"""

    def __init__(self):
        """初始化"""
        self.base_url = "https://skills.sh"

    def generate_email_html(self, trends: Dict, date: str) -> str:
        """
        生成完整的 HTML 邮件

        Args:
            trends: 趋势数据
            date: 日期

        Returns:
            HTML 字符串
        """
        html_parts = []

        # HTML 头部
        html_parts.append(self._get_header(date))

        # Top 20 榜单
        html_parts.append(self._render_top_20(trends.get("top_20", [])))

        # 上升 Top 5
        html_parts.append(self._render_rising_top5(trends.get("rising_top5", [])))

        # 下降 Top 5
        html_parts.append(self._render_falling_top5(trends.get("falling_top5", [])))

        # 新晋/掉榜
        html_parts.append(self._render_new_dropped(
            trends.get("new_entries", []),
            trends.get("dropped_entries", [])
        ))

        # 暴涨告警
        surging = trends.get("surging", [])
        if surging:
            html_parts.append(self._render_surging(surging))

        # HTML 尾部
        html_parts.append(self._get_footer(date))

        return "\n".join(html_parts)

    def _get_header(self, date: str) -> str:
        """生成 HTML 头部"""
        return """<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Skills Trending Daily</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            margin: 0;
            padding: 0;
            background-color: #f8f9fa;
            -webkit-font-smoothing: antialiased;
        }
        .container {
            max-width: 640px;
            margin: 0 auto;
            background-color: #ffffff;
        }
        .header {
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            color: white;
            padding: 40px 30px;
            text-align: center;
        }
        .header h1 {
            margin: 0;
            font-size: 26px;
            font-weight: 600;
            letter-spacing: -0.5px;
        }
        .header p {
            margin: 8px 0 0;
            font-size: 14px;
            opacity: 0.8;
            font-weight: 400;
        }
        .section {
            padding: 28px 30px;
            border-bottom: 1px solid #e9ecef;
        }
        .section:last-child {
            border-bottom: none;
        }
        .section-title {
            margin: 0 0 20px;
            font-size: 15px;
            font-weight: 600;
            color: #1a1a2e;
            text-transform: uppercase;
            letter-spacing: 1px;
            padding-bottom: 12px;
            border-bottom: 2px solid #1a1a2e;
        }
        .skill-card {
            margin-bottom: 16px;
            padding: 0;
            background-color: #ffffff;
        }
        .skill-card:last-child {
            margin-bottom: 0;
        }
        .skill-main {
            display: flex;
            align-items: baseline;
            padding: 14px 16px;
            background-color: #f8f9fa;
            border-radius: 6px;
            border-left: 3px solid #1a1a2e;
        }
        .skill-rank {
            font-size: 14px;
            font-weight: 700;
            color: #1a1a2e;
            min-width: 32px;
        }
        .skill-name {
            font-size: 15px;
            font-weight: 600;
            color: #1a1a2e;
            flex-grow: 1;
            margin: 0 10px;
        }
        .skill-name a {
            color: #1a1a2e;
            text-decoration: none;
        }
        .skill-name a:hover {
            text-decoration: underline;
        }
        .skill-stats {
            display: flex;
            align-items: center;
            gap: 12px;
            font-size: 13px;
        }
        .rank-change {
            font-weight: 600;
            padding: 2px 6px;
            border-radius: 3px;
            font-size: 12px;
        }
        .rank-up {
            color: #059669;
            background-color: #d1fae5;
        }
        .rank-down {
            color: #dc2626;
            background-color: #fee2e2;
        }
        .rank-same {
            color: #6b7280;
            background-color: #f3f4f6;
        }
        .installs {
            color: #6b7280;
            font-size: 13px;
        }
        .skill-content {
            padding: 12px 16px 0;
        }
        .skill-summary {
            color: #4b5563;
            font-size: 14px;
            line-height: 1.6;
            margin-bottom: 8px;
        }
        .skill-meta {
            font-size: 13px;
            color: #6b7280;
            margin-bottom: 10px;
        }
        .badge {
            display: inline-block;
            padding: 3px 8px;
            border-radius: 4px;
            font-size: 11px;
            font-weight: 500;
            margin-right: 6px;
            margin-bottom: 4px;
        }
        .badge-category {
            background-color: #e5e7eb;
            color: #374151;
        }
        .badge-new {
            background-color: #059669;
            color: white;
        }
        .badge-alert {
            background-color: #dc2626;
            color: white;
        }
        .badge-surging {
            background-color: #d97706;
            color: white;
        }
        .solves-list {
            display: flex;
            flex-wrap: wrap;
            gap: 6px;
        }
        .solve-tag {
            background-color: #f3f4f6;
            color: #4b5563;
            padding: 4px 10px;
            border-radius: 4px;
            font-size: 12px;
        }
        .divider {
            height: 1px;
            background-color: #e9ecef;
            margin: 0;
            border: none;
        }
        .footer {
            text-align: center;
            padding: 28px 20px;
            font-size: 12px;
            color: #6b7280;
            background-color: #f8f9fa;
        }
        .footer a {
            color: #1a1a2e;
            text-decoration: none;
            font-weight: 500;
        }
        .footer a:hover {
            text-decoration: underline;
        }
        .empty {
            text-align: center;
            color: #9ca3af;
            padding: 24px;
            font-size: 14px;
        }
        .compact-card {
            padding: 12px 14px;
            margin-bottom: 8px;
            background-color: #f8f9fa;
            border-radius: 6px;
            border-left: 3px solid #e5e7eb;
        }
        .compact-card:last-child {
            margin-bottom: 0;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Skills Trending Daily</h1>
            <p>""" + date + """</p>
        </div>"""

    def _get_footer(self, date: str) -> str:
        """生成 HTML 尾部"""
        return """        <div class="footer">
            <p>Powered by <a href="https://skills.sh/trending">Skills.sh</a></p>
            <p style="margin-top: 8px; color: #9ca3af;">Data source: skills.sh/trending</p>
        </div>
    </div>
</body>
</html>"""

    def _render_top_20(self, skills: List[Dict]) -> str:
        """渲染 Top 20 榜单"""
        if not skills:
            return self._section_html("Top 20 Leaderboard", '<p class="empty">No data available</p>')

        cards = []
        for skill in skills[:20]:
            cards.append(self._format_skill_card(skill, show_details=True))

        return self._section_html("Top 20 Leaderboard", "\n".join(cards))

    def _render_rising_top5(self, skills: List[Dict]) -> str:
        """渲染上升 Top 5"""
        if not skills:
            return ""

        cards = []
        for skill in skills:
            cards.append(self._format_compact_card(skill, trend="up"))

        return self._section_html("Rising Skills (Top 5)", "\n".join(cards))

    def _render_falling_top5(self, skills: List[Dict]) -> str:
        """渲染下降 Top 5"""
        if not skills:
            return ""

        cards = []
        for skill in skills:
            cards.append(self._format_compact_card(skill, trend="down"))

        return self._section_html("Declining Skills (Top 5)", "\n".join(cards))

    def _render_new_dropped(self, new_entries: List[Dict], dropped: List[Dict]) -> str:
        """渲染新晋/掉榜"""
        if not new_entries and not dropped:
            return ""

        html = ""

        # 新晋
        if new_entries:
            new_items = []
            for skill in new_entries:
                new_items.append(self._format_compact_card(skill, is_new=True))

            html += "<h3 style='margin: 0 0 12px; font-size: 13px; color: #059669; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px;'>New Entries</h3>"
            html += "\n".join(new_items)

        # 掉榜
        if dropped:
            if new_entries:
                html += "<hr class='divider' style='margin: 16px 0;'>"

            dropped_items = []
            for skill in dropped[:10]:
                dropped_items.append(self._format_dropped_card(skill))

            html += "<h3 style='margin: 0 0 12px; font-size: 13px; color: #dc2626; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px;'>Dropped From List</h3>"
            html += "\n".join(dropped_items)

        return self._section_html("New & Dropped", html)

    def _render_surging(self, skills: List[Dict]) -> str:
        """渲染暴涨告警"""
        if not skills:
            return ""

        cards = []
        for skill in skills:
            cards.append(self._format_compact_card(skill, is_surging=True))

        return self._section_html("Trending Up", "\n".join(cards))

    def _format_skill_card(self, skill: Dict, show_details: bool = True) -> str:
        """格式化单个技能卡片"""
        rank = skill.get("rank", 0)
        name = skill.get("name", "")
        rank_delta = skill.get("rank_delta", 0)
        installs = skill.get("installs", 0)
        installs_delta = skill.get("installs_delta", 0)
        url = skill.get("url", f"{self.base_url}/{skill.get('owner', '')}/{name}")

        # 排名变化指示
        if rank_delta > 0:
            rank_indicator = f'<span class="rank-change rank-up">+{rank_delta}</span>'
        elif rank_delta < 0:
            rank_indicator = f'<span class="rank-change rank-down">{rank_delta}</span>'
        else:
            rank_indicator = '<span class="rank-change rank-same">-</span>'

        # 安装量格式化
        if installs >= 1000:
            installs_display = f"{installs/1000:.1f}k"
        else:
            installs_display = f"{installs:,}"

        # 分类标签
        category_badge = ""
        if skill.get("category_zh"):
            category_badge = f'<span class="badge badge-category">{skill.get("category_zh")}</span>'

        # 解决的问题标签
        solves_html = ""
        if show_details and skill.get("solves"):
            solves_tags = [f'<span class="solve-tag">{s}</span>' for s in skill.get("solves", [])[:4]]
            solves_html = f'<div class="solves-list">{"".join(solves_tags)}</div>'

        # 详细信息
        details_html = ""
        if show_details:
            summary = skill.get("summary", "")
            description = skill.get("description", "")

            detail_parts = []
            if summary:
                detail_parts.append(f'<p style="margin: 0 0 8px; color: #4b5563; font-size: 14px; line-height: 1.5;">{summary}</p>')
            if description:
                detail_parts.append(f'<p style="margin: 0; color: #6b7280; font-size: 13px; line-height: 1.5;">{description}</p>')

            details_html = "\n".join(detail_parts)

        return f"""        <div class="skill-card">
            <div class="skill-main">
                <span class="skill-rank">#{rank}</span>
                <span class="skill-name"><a href="{url}">{name}</a></span>
                <div class="skill-stats">
                    {rank_indicator}
                    <span class="installs">{installs_display} installs</span>
                </div>
            </div>
            <div class="skill-content">
                {details_html}
                <div style="margin-top: 10px;">
                    {category_badge}
                    {solves_html}
                </div>
            </div>
        </div>"""

    def _format_compact_card(self, skill: Dict, trend: str = None, is_new: bool = False, is_surging: bool = False) -> str:
        """格式化紧凑卡片"""
        rank = skill.get("rank", 0)
        name = skill.get("name", "")
        url = skill.get("url", f"{self.base_url}/{skill.get('owner', '')}/{name}")
        installs = skill.get("installs", 0)

        if installs >= 1000:
            installs_display = f"{installs/1000:.1f}k"
        else:
            installs_display = f"{installs:,}"

        # 变化指示
        change_html = ""
        if is_new:
            change_html = '<span class="badge badge-new">NEW</span>'
        elif is_surging:
            rate = skill.get("installs_rate", 0)
            change_html = f'<span class="badge badge-surging">+{int(rate*100)}%</span>'
        elif trend == "up":
            rank_delta = skill.get("rank_delta", 0)
            change_html = f'<span class="rank-change rank-up">+{rank_delta}</span>'
        elif trend == "down":
            rank_delta = skill.get("rank_delta", 0)
            change_html = f'<span class="rank-change rank-down">{rank_delta}</span>'

        summary_html = ""
        if skill.get("summary"):
            summary_html = f'<div style="padding: 8px 14px 0; font-size: 13px; color: #6b7280; line-height: 1.5;">{skill.get("summary")}</div>'

        return f"""            <div class="compact-card">
                {change_html}
                <span style="font-weight: 600; min-width: 32px; font-size: 13px;">#{rank}</span>
                <span style="flex-grow: 1; margin: 0 10px;">
                    <a href="{url}" style="color: #1a1a2e; text-decoration: none; font-size: 14px; font-weight: 500;">{name}</a>
                </span>
                <span style="color: #6b7280; font-size: 12px;">{installs_display}</span>
            </div>{summary_html}"""

    def _format_dropped_card(self, skill: Dict) -> str:
        """格式化掉榜卡片"""
        name = skill.get("name", "")
        yesterday_rank = skill.get("yesterday_rank", 0)

        return f"""            <div class="compact-card" style="border-left-color: #dc2626; background-color: #fef2f2;">
                <span class="badge badge-alert">DROPPED</span>
                <span style="font-weight: 600; min-width: 32px; font-size: 13px;">#{yesterday_rank}</span>
                <span style="flex-grow: 1; margin: 0 10px; color: #6b7280; font-size: 14px;">{name}</span>
            </div>"""

    def _section_html(self, title: str, content: str) -> str:
        """生成一个完整的 section"""
        return f"""        <div class="section">
            <h2 class="section-title">{title}</h2>
            {content}
        </div>"""


def generate_email_html(trends: Dict, date: str) -> str:
    """便捷函数：生成邮件 HTML"""
    reporter = HTMLReporter()
    return reporter.generate_email_html(trends, date)
