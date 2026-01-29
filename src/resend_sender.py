"""
Resend Sender - Resend 邮件发送
使用 Resend API 发送 HTML 邮件
支持多个收件人（逗号分隔或列表）
"""
import resend
from typing import Dict, List, Union, Optional


class ResendSender:
    """Resend 邮件发送"""

    def __init__(self, api_key: str):
        """
        初始化

        Args:
            api_key: Resend API Key
        """
        self.api_key = api_key
        resend.api_key = api_key

    def _parse_recipients(self, to: Union[str, List[str]]) -> List[str]:
        """
        解析收件人列表

        Args:
            to: 收件人字符串或列表，支持：
                - 单个邮箱: "user@example.com"
                - 逗号分隔: "user1@example.com, user2@example.com"
                - 分号分隔: "user1@example.com; user2@example.com"
                - 列表: ["user1@example.com", "user2@example.com"]

        Returns:
            收件人邮箱列表
        """
        if isinstance(to, str):
            # 先尝试逗号分割，再尝试分号分割
            if ',' in to:
                recipients = [email.strip() for email in to.split(',') if email.strip()]
            elif ';' in to:
                recipients = [email.strip() for email in to.split(';') if email.strip()]
            else:
                recipients = [to.strip()]
        else:
            # 如果是列表，直接使用
            recipients = [email.strip() for email in to if email.strip()]

        # 过滤空值和无效邮箱
        valid_recipients = []
        for email in recipients:
            if email and '@' in email and '.' in email:
                valid_recipients.append(email)
            else:
                print(f"⚠️  跳过无效邮箱格式: {email}")

        return valid_recipients

    def send_email(
        self,
        to: Union[str, List[str]],
        subject: str,
        html_content: str,
        from_email: str = "onboarding@resend.dev"
    ) -> Dict:
        """
        发送邮件到多个收件人

        Args:
            to: 收件人邮箱（支持多种格式）
                - 字符串: "user@example.com"（单个）
                - 字符串: "user1@example.com, user2@example.com"（逗号分隔）
                - 字符串: "user1@example.com; user2@example.com"（分号分隔）
                - 列表: ["user1@example.com", "user2@example.com"]
            subject: 邮件标题
            html_content: HTML 内容
            from_email: 发件人邮箱

        Returns:
            {"success": bool, "message": str, "id": str, "recipients": List[str]}
        """
        # 解析收件人
        recipients = self._parse_recipients(to)

        if not recipients:
            return {
                "success": False,
                "message": "没有有效的收件人邮箱",
                "id": None,
                "recipients": []
            }

        try:
            print(f"📧 正在发送邮件到 {len(recipients)} 个收件人:")
            for i, email in enumerate(recipients, 1):
                print(f"  {i}. {email}")

            # Resend API 支持直接传列表
            params = {
                "from": from_email,
                "to": recipients,  # ✅ 直接传收件人列表
                "subject": subject,
                "html": html_content,
            }

            response = resend.Emails.send(params)

            print(f"✅ 邮件发送成功! ID: {response.get('id')}")
            print(f"   收件人: {len(recipients)} 个")

            return {
                "success": True,
                "message": f"邮件发送成功到 {len(recipients)} 个收件人",
                "id": response.get("id"),
                "recipients": recipients,
                "response": response
            }

        except Exception as e:
            error_msg = str(e)
            print(f"❌ 邮件发送失败: {error_msg}")

            return {
                "success": False,
                "message": error_msg,
                "id": None,
                "recipients": recipients
            }

    def send_batch_separate(
        self,
        to: Union[str, List[str]],
        subject: str,
        html_content: str,
        from_email: str = "onboarding@resend.dev"
    ) -> List[Dict]:
        """
        批量单独发送（每个收件人单独发送一封邮件）

        用于需要单独计费或追踪的场景

        Args:
            to: 收件人邮箱（支持多种格式）
            subject: 邮件标题
            html_content: HTML 内容
            from_email: 发件人邮箱

        Returns:
            每个收件人的发送结果列表
        """
        recipients = self._parse_recipients(to)

        if not recipients:
            print("⚠️  没有有效的收件人邮箱")
            return []

        results = []
        success_count = 0

        print(f"📧 开始批量单独发送，共 {len(recipients)} 个收件人...")

        for email in recipients:
            try:
                params = {
                    "from": from_email,
                    "to": [email],  # 每次只发送给一个人
                    "subject": subject,
                    "html": html_content,
                }

                response = resend.Emails.send(params)

                result = {
                    "success": True,
                    "email": email,
                    "id": response.get("id"),
                    "message": "发送成功"
                }
                success_count += 1
                print(f"  ✅ {email}: 发送成功")

            except Exception as e:
                result = {
                    "success": False,
                    "email": email,
                    "id": None,
                    "message": str(e)
                }
                print(f"  ❌ {email}: 发送失败 - {str(e)}")

            results.append(result)

        print(f"📊 批量发送完成: 成功 {success_count}/{len(recipients)}")

        return results


def send_email(
    api_key: str,
    to: Union[str, List[str]],
    subject: str,
    html_content: str,
    from_email: str = "onboarding@resend.dev"
) -> Dict:
    """便捷函数：发送邮件到多个收件人"""
    sender = ResendSender(api_key)
    return sender.send_email(to, subject, html_content, from_email)
