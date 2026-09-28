#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
backup_manager.py — inventory.db 자동 압축 백업 및 이메일 발송 관리자
"""

import os
import time
import sqlite3
import zipfile
import smtplib
import threading
from datetime import datetime, timezone, timedelta
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from pathlib import Path
import database

KST = timezone(timedelta(hours=9))
BASE_DIR = Path(__file__).parent
BACKUP_DIR = BASE_DIR / "backups"

_scheduler_running = False
_scheduler_lock = threading.Lock()


def ensure_backup_dir():
    if not BACKUP_DIR.exists():
        BACKUP_DIR.mkdir(parents=True, exist_ok=True)


def create_backup_zip():
    """
    inventory.db 파일을 atomic backup으로 복사한 후 날짜가 포함된 zip 파일로 압축 생성
    반환: (zip_path, zip_filename, filesize)
    """
    ensure_backup_dir()
    now_str = datetime.now(KST).strftime('%Y%m%d_%H%M%S')
    zip_filename = f"inventory_backup_{now_str}.zip"
    zip_path = BACKUP_DIR / zip_filename
    temp_db_path = BACKUP_DIR / f"temp_{now_str}.db"

    # SQLite backup API로 무결한 DB 복사
    src_conn = database.get_db()
    dest_conn = sqlite3.connect(str(temp_db_path))
    try:
        src_conn.backup(dest_conn)
    finally:
        dest_conn.close()
        src_conn.close()

    # ZIP 압축
    try:
        with zipfile.ZipFile(str(zip_path), 'w', zipfile.ZIP_DEFLATED) as zf:
            zf.write(str(temp_db_path), arcname="inventory.db")
        filesize = zip_path.stat().st_size
    finally:
        if temp_db_path.exists():
            try:
                temp_db_path.unlink()
            except Exception:
                pass

    return zip_path, zip_filename, filesize


import base64
import json
import urllib.request
import urllib.error


def send_backup_email(zip_path, zip_filename):
    """
    저장된 system_config를 불러와 설정된 방식(SMTP / Resend API / Brevo API)으로 ZIP 백업 파일 이메일 발송
    반환: (success_bool, message_str)
    """
    cfg = database.get_system_config()
    provider = cfg.get('email_provider', 'smtp').strip().lower()
    receiver = cfg.get('smtp_receiver', '').strip()
    sender = cfg.get('smtp_sender', '').strip() or cfg.get('smtp_user', '').strip()
    api_key = cfg.get('api_key', '').strip()

    if not receiver:
        return False, "수신 이메일 주소가 설정되지 않아 이메일 전송을 건너뛰었습니다."

    now_date = datetime.now(KST).strftime('%Y-%m-%d %H:%M')
    subject = f"[세한로보틱스 재고관리] DB 자동 백업 파일 ({now_date})"
    body_text = f"""안녕하세요. 세한로보틱스 용접로봇 재고관리 시스템입니다.

요청하신 데이터베이스(inventory.db) 백업 파일이 성공적으로 생성되었습니다.

- 백업 일시: {now_date} KST
- 파일명: {zip_filename}
- 파일 크기: {zip_path.stat().st_size / 1024:.1f} KB

본 메일은 시스템에 의해 자동 발송되었습니다.
"""

    # ── 1) Resend HTTPS API (PythonAnywhere 무료 계정 추천) ──
    if provider == 'resend':
        if not api_key:
            return False, "Resend API Key가 입력되지 않았습니다."
        
        with open(str(zip_path), 'rb') as f:
            b64_content = base64.b64encode(f.read()).decode('utf-8')
            
        # Resend 도메인 미인증 상태에서는 반드시 onboarding@resend.dev 를 발신자로 사용해야 함
        payload = {
            "from": "onboarding@resend.dev",
            "to": [receiver],
            "subject": subject,
            "text": body_text,
            "attachments": [
                {
                    "filename": zip_filename,
                    "content": b64_content
                }
            ]
        }
        
        req = urllib.request.Request(
            "https://api.resend.com/emails",
            data=json.dumps(payload).encode('utf-8'),
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
            },
            method="POST"
        )
        try:
            with urllib.request.urlopen(req, timeout=20) as resp:
                if resp.status in (200, 201):
                    return True, f"Resend HTTPS API를 통해 '{receiver}' 주소로 메일 발송 성공"
                return False, f"Resend API 응답 코드: {resp.status}"
        except urllib.error.HTTPError as e:
            err_body = e.read().decode('utf-8', errors='ignore')
            if e.code == 403:
                return False, f"Resend API (403): Resend 가입 이메일('{receiver}')로만 발송 가능합니다. (다른 메일로 보낼 경우 Brevo API 추천)"
            return False, f"Resend API 오류 ({e.code}): {err_body}"
        except Exception as e:
            return False, f"Resend 전송 실패: {str(e)}"

    # ── 2) Brevo (Sendinblue) HTTPS API (제한 없이 모든 이메일 발송 가능) ──
    elif provider == 'brevo':
        api_key = api_key.strip()
        if not api_key:
            return False, "Brevo API Key가 입력되지 않았습니다."
            
        with open(str(zip_path), 'rb') as f:
            b64_content = base64.b64encode(f.read()).decode('utf-8')

        sender_email = sender.strip() if (sender and '@' in sender) else receiver
        payload = {
            "sender": {"email": sender_email, "name": "Panasonic Inventory"},
            "to": [{"email": receiver}],
            "subject": subject,
            "textContent": body_text,
            "attachment": [
                {
                    "name": zip_filename,
                    "content": b64_content
                }
            ]
        }

        req = urllib.request.Request(
            "https://api.brevo.com/v3/smtp/email",
            data=json.dumps(payload).encode('utf-8'),
            headers={
                "api-key": api_key,
                "Content-Type": "application/json",
                "accept": "application/json",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
            },
            method="POST"
        )
        try:
            with urllib.request.urlopen(req, timeout=20) as resp:
                if resp.status in (200, 201):
                    return True, f"Brevo HTTPS API를 통해 '{receiver}' 주소로 메일 발송 성공"
                return False, f"Brevo API 응답 코드: {resp.status}"
        except urllib.error.HTTPError as e:
            err_body = e.read().decode('utf-8', errors='ignore')
            return False, f"Brevo API 오류 ({e.code}): {err_body}"
        except Exception as e:
            return False, f"Brevo 전송 실패: {str(e)}"

    # ── 3) 일반 SMTP (로컬 PC 또는 PythonAnywhere 유료 계정용) ──
    else:
        host = cfg.get('smtp_host', '').strip()
        port = int(cfg.get('smtp_port', '587') or '587')
        user = cfg.get('smtp_user', '').strip()
        password = cfg.get('smtp_pass', '').strip()
        use_tls = cfg.get('smtp_use_tls', '1') == '1'

        if not host or not user or not password:
            return False, "SMTP 설정(서버, 계정, 비밀번호)이 완료되지 않았습니다."

        msg = MIMEMultipart()
        msg['From'] = sender or user
        msg['To'] = receiver
        msg['Subject'] = subject
        msg.attach(MIMEText(body_text, 'plain', 'utf-8'))

        with open(str(zip_path), 'rb') as f:
            part = MIMEApplication(f.read(), Name=zip_filename)
            part['Content-Disposition'] = f'attachment; filename="{zip_filename}"'
            msg.attach(part)

        try:
            if port == 465:
                server = smtplib.SMTP_SSL(host, port, timeout=20)
            else:
                server = smtplib.SMTP(host, port, timeout=20)
                if use_tls:
                    server.starttls()

            server.login(user, password)
            server.send_message(msg)
            server.quit()
            return True, f"'{receiver}' 주소로 SMTP 이메일 발송 성공"
        except Exception as e:
            err_str = str(e)
            if "111" in err_str or "Connection refused" in err_str:
                return False, "PythonAnywhere 무료 계정은 포트 587/465 소켓 통신을 차단합니다. 상단 전송 방식을 [Resend API] 또는 [Brevo API]로 변경해 주세요."
            return False, f"SMTP 발송 실패: {err_str}"


def run_backup(send_email=True):
    """
    백업 수행 (압축 + 선택적 이메일 발송) 및 이력 DB 기록
    """
    try:
        zip_path, zip_filename, filesize = create_backup_zip()
        email_ok, email_msg = False, ""
        
        if send_email:
            email_ok, email_msg = send_backup_email(zip_path, zip_filename)
            if email_ok:
                status = "SUCCESS"
                msg = f"백업 및 이메일 발송 완료 ({email_msg})"
            else:
                status = "SUCCESS_NO_EMAIL"
                msg = f"ZIP 생성 완료 (이메일: {email_msg})"
        else:
            status = "SUCCESS"
            msg = "ZIP 파일 생성 완료 (이메일 수동 제외)"

        database.add_backup_history(zip_filename, str(zip_path), filesize, status, msg)
        return {
            'success': True,
            'filename': zip_filename,
            'filepath': str(zip_path),
            'filesize': filesize,
            'email_sent': email_ok,
            'message': msg
        }
    except Exception as e:
        err_msg = f"백업 처리 중 오류 발생: {str(e)}"
        database.add_backup_history("N/A", "", 0, "FAILED", err_msg)
        return {
            'success': False,
            'message': err_msg
        }


def _scheduler_loop():
    """
    매 분마다 확인하며 자정(또는 설정된 시간)에 자동 백업 실행
    """
    last_run_day = None
    print("[BackupScheduler] 자동 백업 스케줄러 스레드가 시작되었습니다.")

    while True:
        try:
            cfg = database.get_system_config()
            enabled = cfg.get('auto_backup_enabled', '1') == '1'
            target_time = cfg.get('auto_backup_time', '00:00').strip()
            
            if enabled:
                now = datetime.now(KST)
                current_time = now.strftime('%H:%M')
                current_day = now.strftime('%Y-%m-%d')

                # 하루에 한 번 설정된 시간에 실행
                if current_time == target_time and last_run_day != current_day:
                    print(f"[BackupScheduler] 자정 백업 실행 중... ({now.strftime('%Y-%m-%d %H:%M:%S')})")
                    res = run_backup(send_email=True)
                    print(f"[BackupScheduler] 백업 결과: {res['message']}")
                    last_run_day = current_day

        except Exception as e:
            print(f"[BackupScheduler] 오류 발생: {e}")

        # 30초 간격으로 체크
        time.sleep(30)


def start_scheduler():
    global _scheduler_running
    with _scheduler_lock:
        if _scheduler_running:
            return
        _scheduler_running = True
        t = threading.Thread(target=_scheduler_loop, daemon=True)
        t.start()
