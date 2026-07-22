#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
update_db_prices.py - 부품가격표.xlsx 데이터를 참고하여 DB의 단가(price)를 업데이트하는 스크립트
"""

import sys
import openpyxl
import sqlite3
from pathlib import Path

WORKSPACE_DIR = Path(__file__).parent
DB_PATH = WORKSPACE_DIR / "inventory.db"
EXCEL_PATH = WORKSPACE_DIR / "부품가격표.xlsx"

def main():
    if not EXCEL_PATH.exists():
        print(f"[오류] 가격표 엑셀 파일을 찾을 수 없습니다: {EXCEL_PATH}")
        sys.exit(1)
        
    print(f"[*] 엑셀 파일 로딩 중: {EXCEL_PATH.name}...")
    try:
        wb = openpyxl.load_workbook(EXCEL_PATH, data_only=True)
        sheet = wb.active
        print(f"[*] 활성 시트: {sheet.title}")
    except Exception as e:
        print(f"[오류] 엑셀 파일을 읽는 도중 오류가 발생했습니다: {e}")
        sys.exit(1)

    # 가격표 파싱 (상품코드 -> 단가)
    excel_prices = {}
    for idx, row in enumerate(sheet.iter_rows(values_only=True)):
        if idx <= 1:  # 첫 번째 빈 행 및 두 번째 헤더 행 스킵
            continue
        item_code = str(row[0]).strip() if row[0] is not None else ""
        price = row[2]
        if item_code and price is not None:
            try:
                excel_prices[item_code] = int(price)
            except (ValueError, TypeError):
                pass

    print(f"[*] 가격표에서 총 {len(excel_prices)}개의 단가 항목을 로드했습니다.")

    # DB 연결
    if not DB_PATH.exists():
        print(f"[오류] DB 파일을 찾을 수 없습니다: {DB_PATH}")
        sys.exit(1)

    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    try:
        # DB 내 모든 상품 목록 조회
        cursor.execute("SELECT id, item_code, name, price FROM products")
        products = cursor.fetchall()
        
        updated_count = 0
        no_match_count = 0
        no_change_count = 0

        print("[*] DB 내 상품 단가 업데이트 진행 중...")
        for p in products:
            pid = p['id']
            item_code = p['item_code'].strip() if p['item_code'] else ""
            old_price = p['price']
            
            if not item_code:
                no_match_count += 1
                continue
                
            if item_code in excel_prices:
                new_price = excel_prices[item_code]
                if old_price != new_price:
                    cursor.execute(
                        "UPDATE products SET price=?, updated_at=datetime('now', '+9 hours') WHERE id=?",
                        (new_price, pid)
                    )
                    updated_count += 1
                else:
                    no_change_count += 1
            else:
                no_match_count += 1

        if updated_count > 0:
            # 감사 로그 기록
            cursor.execute(
                """INSERT INTO audit_log 
                   (user_id, user_name, action, target_type, note, created_at) 
                   VALUES (?, ?, ?, ?, ?, datetime('now', '+9 hours'))""",
                (0, "시스템(CLI)", "EDIT", "product", f"부품가격표.xlsx 기준 단가 일괄 업데이트 완료 ({updated_count}건 수정, 변경없음 {no_change_count}건, 미매칭 {no_match_count}건)")
            )
            conn.commit()
            print(f"[+] 완료: 총 {updated_count}개 상품의 단가를 업데이트했습니다.")
            print(f"    - 변경 없음 (가격 일치): {no_change_count}건")
            print(f"    - 미매칭 (코드 없음 또는 엑셀 누락): {no_match_count}건")
        else:
            print("[*] 업데이트할 단가 변경 내역이 없습니다.")

    except Exception as e:
        conn.rollback()
        print(f"[오류] 데이터베이스 처리 중 오류가 발생하여 롤백했습니다: {e}")
        sys.exit(1)
    finally:
        conn.close()

if __name__ == "__main__":
    main()
