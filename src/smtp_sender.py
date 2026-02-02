"""
SMTP Sender - SMTP 邮件发送
使用 SMTP 发送 HTML 邮件，支持腾讯邮箱等
支持多个收件人（逗号分隔或列表）
"""
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import Header
from email.utils import parseaddr, formataddr
from typing import Dict, List, Union, Optional


class SMTPSender:
    """SMTP 邮件发送"""

    def __init__(self, smtp_host: str, smtp_port: int, smtp_user: str, smtp_password: str):
        """
        初始化

        Args:
            smtp_host: SMTP 服务器地址
            smtp_port: SMTP 服务器端口
            smtp_user: SMTP 用户名（邮箱地址）
            smtp_password: SMTP 密码（授权码）
        """
        self.smtp_host = smtp_host
        self.smtp_port = smtp_port
        self.smtp_user = smtp_user
        self.smtp_password = smtp_password

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
            _, addr = parseaddr(email)
            if addr and '@' in addr and '.' in addr:
                valid_recipients.append(addr)
            else:
                print(f"⚠️  跳过无效邮箱格式: {email}")

        return valid_recipients

    def _format_from_header(self, from_email: str) -> Optional[str]:
        """格式化 From 头部，确保符合 RFC 格式"""
        name, addr = parseaddr(from_email)
        if not addr or '@' not in addr or '.' not in addr:
            return None
        if name:
            return formataddr((name, addr), charset='utf-8')
        return addr

    def send_email(
        self,
        to: Union[str, List[str]],
        subject: str,
        html_content: str,
        from_email: str
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
            {"success": bool, "message": str, "recipients": List[str]}
        """
        # 解析收件人
        recipients = self._parse_recipients(to)

        if not recipients:
            return {
                "success": False,
                "message": "没有有效的收件人邮箱",
                "recipients": []
            }

        try:
            print(f"📧 正在通过 SMTP 发送邮件到 {len(recipients)} 个收件人:")
            for i, email in enumerate(recipients, 1):
                print(f"  {i}. {email}")

            # 创建邮件
            msg = MIMEMultipart('alternative')
            formatted_from = self._format_from_header(from_email)
            if not formatted_from:
                return {
                    "success": False,
                    "message": "无效的发件人邮箱",
                    "recipients": recipients
                }
            _, from_addr = parseaddr(from_email)
            msg['From'] = formatted_from
            msg['To'] = ", ".join(recipients)
            msg['Subject'] = Header(subject, 'utf-8')

            # 添加 HTML 内容
            html_part = MIMEText(html_content, 'html', 'utf-8')
            msg.attach(html_part)

            # 连接 SMTP 服务器
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()  # 启用 TLS
                server.login(self.smtp_user, self.smtp_password)
                
                # 发送邮件
                server.send_message(msg, from_addr=from_addr, to_addrs=recipients)

            print(f"✅ SMTP 邮件发送成功!")
            print(f"   收件人: {len(recipients)} 个")

            return {
                "success": True,
                "message": f"邮件发送成功到 {len(recipients)} 个收件人",
                "recipients": recipients
            }

        except Exception as e:
            error_msg = str(e)
            print(f"❌ SMTP 邮件发送失败: {error_msg}")

            return {
                "success": False,
                "message": error_msg,
                "recipients": recipients
            }

    def send_batch_separate(
        self,
        to: Union[str, List[str]],
        subject: str,
        html_content: str,
        from_email: str
    ) -> List[Dict]:
        """
        批量单独发送（每个收件人单独发送一封邮件）

        用于需要单独发送的场景

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
                # 创建邮件
                msg = MIMEMultipart('alternative')
                formatted_from = self._format_from_header(from_email)
                if not formatted_from:
                    raise ValueError("无效的发件人邮箱")
                _, from_addr = parseaddr(from_email)
                msg['From'] = formatted_from
                msg['To'] = email
                msg['Subject'] = Header(subject, 'utf-8')

                # 添加 HTML 内容
                html_part = MIMEText(html_content, 'html', 'utf-8')
                msg.attach(html_part)

                # 连接 SMTP 服务器
                with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                    server.starttls()  # 启用 TLS
                    server.login(self.smtp_user, self.smtp_password)
                    
                    # 发送邮件
                    server.send_message(msg, from_addr=from_addr, to_addrs=[email])

                result = {
                    "success": True,
                    "email": email,
                    "message": "发送成功"
                }
                success_count += 1
                print(f"  ✅ {email}: 发送成功")

            except Exception as e:
                result = {
                    "success": False,
                    "email": email,
                    "message": str(e)
                }
                print(f"  ❌ {email}: 发送失败 - {str(e)}")

            results.append(result)

        print(f"📊 批量发送完成: 成功 {success_count}/{len(recipients)}")

        return results


def send_email(
    smtp_host: str,
    smtp_port: int,
    smtp_user: str,
    smtp_password: str,
    to: Union[str, List[str]],
    subject: str,
    html_content: str,
    from_email: str
) -> Dict:
    """便捷函数：发送邮件到多个收件人"""
    sender = SMTPSender(smtp_host, smtp_port, smtp_user, smtp_password)
    return sender.send_email(to, subject, html_content, from_email)
