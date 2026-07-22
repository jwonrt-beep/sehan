#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
재고관리 시스템 (Inventory Management System)
====================================================
기능:
  - 상품 등록 / 수정 / 삭제
  - 재고 입고 / 출고
  - 검색 및 필터링
  - 재고 부족 경고
  - CSV 파일 저장/불러오기
  - 대시보드 요약 통계
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json
import csv
import os
import datetime
from pathlib import Path


# ─────────────────────────────────────────────
#  색상 팔레트 & 스타일 상수
# ─────────────────────────────────────────────
BG_DARK      = "#0F1117"
BG_CARD      = "#1A1D27"
BG_SIDEBAR   = "#13151F"
BG_ROW_ALT  = "#1E2130"
ACCENT_BLUE  = "#4F8EF7"
ACCENT_GREEN = "#2ECC85"
ACCENT_RED   = "#FF5C5C"
ACCENT_AMBER = "#F5A623"
ACCENT_PURPLE= "#9B59B6"
TEXT_PRIMARY = "#EAEAEA"
TEXT_MUTED   = "#8B90A0"
BORDER_COLOR = "#2A2D3E"
HOVER_COLOR  = "#252840"

LOW_STOCK_THRESHOLD = 10  # 재고 부족 기준 수량


# ─────────────────────────────────────────────
#  데이터 모델
# ─────────────────────────────────────────────
class InventoryData:
    """재고 데이터 관리 클래스"""

    def __init__(self):
        self.items: list[dict] = []
        self.transactions: list[dict] = []
        self.next_id = 1
        self._load_defaults()

    def _load_defaults(self):
        """샘플 초기 데이터"""
        samples = [
            {"name": "노트북 (LG그램)", "category": "전자제품", "price": 1_590_000, "quantity": 25, "unit": "대", "supplier": "LG전자"},
            {"name": "무선 마우스",      "category": "전자제품", "price": 35_000,   "quantity": 80, "unit": "개", "supplier": "로지텍"},
            {"name": "A4 복사용지",      "category": "사무용품", "price": 4_500,    "quantity": 7,  "unit": "권", "supplier": "이마트"},
            {"name": "볼펜 (파란색)",    "category": "사무용품", "price": 800,      "quantity": 150,"unit": "자루","supplier": "모나미"},
            {"name": "USB 허브 4포트",   "category": "전자제품", "price": 18_000,   "quantity": 3,  "unit": "개", "supplier": "삼성전자"},
            {"name": "노트 (A5)",        "category": "사무용품", "price": 3_200,    "quantity": 60, "unit": "권", "supplier": "모닝글로리"},
            {"name": "커피 (원두 500g)", "category": "식품",     "price": 14_000,   "quantity": 12, "unit": "봉", "supplier": "스타벅스"},
            {"name": "생수 (2L 6개입)",  "category": "식품",     "price": 5_400,    "quantity": 5,  "unit": "박스","supplier": "제주삼다수"},
            {"name": "청소기 필터",      "category": "생활용품", "price": 12_000,   "quantity": 9,  "unit": "개", "supplier": "다이슨"},
            {"name": "손 세정제",        "category": "생활용품", "price": 6_500,    "quantity": 45, "unit": "개", "supplier": "퓨렐"},
        ]
        for s in samples:
            self.add_item(**s)

    # ── CRUD ──────────────────────────────────
    def add_item(self, name, category, price, quantity, unit="개", supplier=""):
        item = {
            "id": self.next_id,
            "name": name,
            "category": category,
            "price": int(price),
            "quantity": int(quantity),
            "unit": unit,
            "supplier": supplier,
            "created_at": datetime.datetime.now().strftime("%Y-%m-%d"),
        }
        self.items.append(item)
        self.next_id += 1
        return item

    def update_item(self, item_id, **kwargs):
        for item in self.items:
            if item["id"] == item_id:
                for k, v in kwargs.items():
                    if k in item:
                        item[k] = v
                return True
        return False

    def delete_item(self, item_id):
        self.items = [i for i in self.items if i["id"] != item_id]

    def get_item(self, item_id):
        for item in self.items:
            if item["id"] == item_id:
                return item
        return None

    # ── 입출고 ────────────────────────────────
    def stock_in(self, item_id, qty, note=""):
        item = self.get_item(item_id)
        if not item:
            return False
        item["quantity"] += qty
        self._record_tx(item_id, item["name"], "입고", qty, note)
        return True

    def stock_out(self, item_id, qty, note=""):
        item = self.get_item(item_id)
        if not item:
            return False
        if item["quantity"] < qty:
            return False
        item["quantity"] -= qty
        self._record_tx(item_id, item["name"], "출고", qty, note)
        return True

    def _record_tx(self, item_id, name, tx_type, qty, note):
        self.transactions.append({
            "datetime": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
            "item_id": item_id,
            "name": name,
            "type": tx_type,
            "quantity": qty,
            "note": note,
        })

    # ── 검색/필터 ─────────────────────────────
    def search(self, keyword="", category="전체"):
        result = self.items
        if keyword:
            kw = keyword.lower()
            result = [i for i in result if kw in i["name"].lower()
                      or kw in i["supplier"].lower()]
        if category and category != "전체":
            result = [i for i in result if i["category"] == category]
        return result

    @property
    def categories(self):
        return ["전체"] + sorted(set(i["category"] for i in self.items))

    # ── 통계 ──────────────────────────────────
    @property
    def total_value(self):
        return sum(i["price"] * i["quantity"] for i in self.items)

    @property
    def low_stock_items(self):
        return [i for i in self.items if i["quantity"] <= LOW_STOCK_THRESHOLD]

    # ── CSV 저장/불러오기 ─────────────────────
    def export_csv(self, filepath):
        with open(filepath, "w", newline="", encoding="utf-8-sig") as f:
            writer = csv.DictWriter(f, fieldnames=["id","name","category","price","quantity","unit","supplier","created_at"])
            writer.writeheader()
            writer.writerows(self.items)

    def import_csv(self, filepath):
        with open(filepath, "r", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            for row in reader:
                self.add_item(
                    name=row["name"], category=row["category"],
                    price=row["price"], quantity=row["quantity"],
                    unit=row.get("unit","개"), supplier=row.get("supplier","")
                )


# ─────────────────────────────────────────────
#  메인 애플리케이션
# ─────────────────────────────────────────────
class InventoryApp(tk.Tk):

    def __init__(self):
        super().__init__()
        self.data = InventoryData()
        self._setup_window()
        self._apply_theme()
        self._build_ui()
        self.refresh_table()
        self.refresh_dashboard()

    # ─── 초기화 ───────────────────────────────
    def _setup_window(self):
        self.title("📦  재고관리 시스템  v1.0")
        self.geometry("1200x780")
        self.minsize(1000, 640)
        self.configure(bg=BG_DARK)
        # 창 중앙 배치
        self.update_idletasks()
        sw, sh = self.winfo_screenwidth(), self.winfo_screenheight()
        x = (sw - 1200) // 2
        y = (sh - 780) // 2
        self.geometry(f"1200x780+{x}+{y}")

    def _apply_theme(self):
        style = ttk.Style(self)
        style.theme_use("clam")

        # Treeview
        style.configure("Inv.Treeview",
            background=BG_CARD, foreground=TEXT_PRIMARY,
            fieldbackground=BG_CARD, rowheight=36,
            borderwidth=0, relief="flat",
            font=("Malgun Gothic", 10))
        style.configure("Inv.Treeview.Heading",
            background=BG_SIDEBAR, foreground=ACCENT_BLUE,
            relief="flat", font=("Malgun Gothic", 10, "bold"))
        style.map("Inv.Treeview",
            background=[("selected", ACCENT_BLUE)],
            foreground=[("selected", "#FFFFFF")])

        # Combobox
        style.configure("TCombobox",
            fieldbackground=BG_CARD, background=BG_CARD,
            foreground=TEXT_PRIMARY, arrowcolor=ACCENT_BLUE,
            bordercolor=BORDER_COLOR)

        # Scrollbar
        style.configure("TScrollbar",
            background=BG_CARD, troughcolor=BG_DARK,
            arrowcolor=TEXT_MUTED, bordercolor=BG_DARK)

    # ─── UI 구성 ──────────────────────────────
    def _build_ui(self):
        # 타이틀바
        self._build_titlebar()
        # 본문 = 사이드바 + 메인
        body = tk.Frame(self, bg=BG_DARK)
        body.pack(fill="both", expand=True, padx=0, pady=0)
        self._build_sidebar(body)
        self._build_main(body)

    def _build_titlebar(self):
        bar = tk.Frame(self, bg=BG_SIDEBAR, height=56)
        bar.pack(fill="x")
        bar.pack_propagate(False)

        # 로고
        tk.Label(bar, text="📦  재고관리 시스템",
                 bg=BG_SIDEBAR, fg=TEXT_PRIMARY,
                 font=("Malgun Gothic", 15, "bold")).pack(side="left", padx=20)

        # 날짜
        now = datetime.datetime.now().strftime("%Y년 %m월 %d일 (%a)")
        tk.Label(bar, text=now, bg=BG_SIDEBAR, fg=TEXT_MUTED,
                 font=("Malgun Gothic", 10)).pack(side="right", padx=20)

    def _build_sidebar(self, parent):
        sb = tk.Frame(parent, bg=BG_SIDEBAR, width=200)
        sb.pack(side="left", fill="y")
        sb.pack_propagate(False)

        tk.Label(sb, text="메뉴", bg=BG_SIDEBAR, fg=TEXT_MUTED,
                 font=("Malgun Gothic", 9, "bold")).pack(anchor="w", padx=16, pady=(20,8))

        nav_items = [
            ("📊  대시보드",    self._show_dashboard),
            ("📋  재고 목록",   self._show_inventory),
            ("🔄  입출고 내역", self._show_transactions),
            ("⚠️  재고 부족",   self._show_low_stock),
        ]
        self._nav_btns = {}
        for label, cmd in nav_items:
            btn = tk.Button(sb, text=label, bg=BG_SIDEBAR, fg=TEXT_PRIMARY,
                            activebackground=HOVER_COLOR, activeforeground=TEXT_PRIMARY,
                            relief="flat", anchor="w", padx=16, pady=10,
                            font=("Malgun Gothic", 10), cursor="hand2",
                            command=cmd)
            btn.pack(fill="x")
            btn.bind("<Enter>", lambda e, b=btn: b.configure(bg=HOVER_COLOR))
            btn.bind("<Leave>", lambda e, b=btn: b.configure(bg=BG_SIDEBAR))
            self._nav_btns[label] = btn

        # 구분선
        tk.Frame(sb, bg=BORDER_COLOR, height=1).pack(fill="x", padx=16, pady=16)

        # 저장/불러오기
        for txt, cmd in [("💾  CSV 내보내기", self._export_csv),
                         ("📂  CSV 가져오기", self._import_csv)]:
            btn = tk.Button(sb, text=txt, bg=BG_SIDEBAR, fg=TEXT_MUTED,
                            activebackground=HOVER_COLOR, activeforeground=TEXT_PRIMARY,
                            relief="flat", anchor="w", padx=16, pady=8,
                            font=("Malgun Gothic", 9), cursor="hand2", command=cmd)
            btn.pack(fill="x")
            btn.bind("<Enter>", lambda e, b=btn: b.configure(fg=TEXT_PRIMARY, bg=HOVER_COLOR))
            btn.bind("<Leave>", lambda e, b=btn: b.configure(fg=TEXT_MUTED, bg=BG_SIDEBAR))

    def _build_main(self, parent):
        self._main = tk.Frame(parent, bg=BG_DARK)
        self._main.pack(side="left", fill="both", expand=True, padx=12, pady=12)

        # ── 대시보드 프레임 ──
        self._dash_frame = tk.Frame(self._main, bg=BG_DARK)
        self._build_dashboard(self._dash_frame)

        # ── 재고 목록 프레임 ──
        self._inv_frame = tk.Frame(self._main, bg=BG_DARK)
        self._build_inventory_panel(self._inv_frame)

        # ── 입출고 내역 프레임 ──
        self._tx_frame = tk.Frame(self._main, bg=BG_DARK)
        self._build_transaction_panel(self._tx_frame)

        # ── 재고 부족 프레임 ──
        self._low_frame = tk.Frame(self._main, bg=BG_DARK)
        self._build_low_stock_panel(self._low_frame)

        self._show_dashboard()

    # ─── 뷰 전환 ──────────────────────────────
    def _hide_all(self):
        for f in [self._dash_frame, self._inv_frame, self._tx_frame, self._low_frame]:
            f.pack_forget()

    def _show_dashboard(self):
        self._hide_all()
        self.refresh_dashboard()
        self._dash_frame.pack(fill="both", expand=True)

    def _show_inventory(self):
        self._hide_all()
        self.refresh_table()
        self._inv_frame.pack(fill="both", expand=True)

    def _show_transactions(self):
        self._hide_all()
        self.refresh_tx_table()
        self._tx_frame.pack(fill="both", expand=True)

    def _show_low_stock(self):
        self._hide_all()
        self.refresh_low_stock()
        self._low_frame.pack(fill="both", expand=True)

    # ─── 대시보드 ─────────────────────────────
    def _build_dashboard(self, parent):
        tk.Label(parent, text="📊  대시보드", bg=BG_DARK, fg=TEXT_PRIMARY,
                 font=("Malgun Gothic", 14, "bold")).pack(anchor="w", pady=(0,16))

        self._stat_cards_frame = tk.Frame(parent, bg=BG_DARK)
        self._stat_cards_frame.pack(fill="x")

        # 하단: 재고 부족 미리보기
        tk.Label(parent, text="⚠️  재고 부족 알림", bg=BG_DARK, fg=ACCENT_AMBER,
                 font=("Malgun Gothic", 11, "bold")).pack(anchor="w", pady=(20,8))

        self._low_preview_frame = tk.Frame(parent, bg=BG_CARD,
                                           highlightthickness=1,
                                           highlightbackground=BORDER_COLOR)
        self._low_preview_frame.pack(fill="x")

    def refresh_dashboard(self):
        # 통계 카드 다시 그리기
        for w in self._stat_cards_frame.winfo_children():
            w.destroy()

        cards = [
            ("전체 품목 수",   f"{len(self.data.items)} 개",  ACCENT_BLUE,   "📦"),
            ("총 재고 자산",   f"¥{self.data.total_value:,}", ACCENT_GREEN,  "💰"),
            ("재고 부족 품목", f"{len(self.data.low_stock_items)} 개", ACCENT_RED, "⚠️"),
            ("입출고 건수",    f"{len(self.data.transactions)} 건", ACCENT_PURPLE,"🔄"),
        ]

        for i, (title, value, color, icon) in enumerate(cards):
            card = tk.Frame(self._stat_cards_frame, bg=BG_CARD,
                            highlightthickness=1,
                            highlightbackground=BORDER_COLOR,
                            padx=20, pady=16)
            card.grid(row=0, column=i, padx=6, sticky="nsew")
            self._stat_cards_frame.columnconfigure(i, weight=1)

            tk.Label(card, text=icon, bg=BG_CARD, fg=color,
                     font=("Malgun Gothic", 22)).pack(anchor="w")
            tk.Label(card, text=value, bg=BG_CARD, fg=color,
                     font=("Malgun Gothic", 18, "bold")).pack(anchor="w", pady=(4,2))
            tk.Label(card, text=title, bg=BG_CARD, fg=TEXT_MUTED,
                     font=("Malgun Gothic", 9)).pack(anchor="w")

        # 재고 부족 미리보기
        for w in self._low_preview_frame.winfo_children():
            w.destroy()

        low = self.data.low_stock_items
        if not low:
            tk.Label(self._low_preview_frame, text="✅  현재 재고 부족 품목이 없습니다.",
                     bg=BG_CARD, fg=ACCENT_GREEN,
                     font=("Malgun Gothic", 10), pady=12).pack()
        else:
            for item in low[:6]:
                row = tk.Frame(self._low_preview_frame, bg=BG_CARD)
                row.pack(fill="x", padx=12, pady=4)
                color = ACCENT_RED if item["quantity"] == 0 else ACCENT_AMBER
                tk.Label(row, text=f"  {item['name']}",
                         bg=BG_CARD, fg=TEXT_PRIMARY,
                         font=("Malgun Gothic", 10), width=30, anchor="w").pack(side="left")
                tk.Label(row, text=f"재고: {item['quantity']} {item['unit']}",
                         bg=BG_CARD, fg=color,
                         font=("Malgun Gothic", 10, "bold")).pack(side="right")

    # ─── 재고 목록 패널 ───────────────────────
    def _build_inventory_panel(self, parent):
        # 헤더
        hdr = tk.Frame(parent, bg=BG_DARK)
        hdr.pack(fill="x", pady=(0,10))
        tk.Label(hdr, text="📋  재고 목록", bg=BG_DARK, fg=TEXT_PRIMARY,
                 font=("Malgun Gothic", 14, "bold")).pack(side="left")

        # 액션 버튼들
        btn_frame = tk.Frame(hdr, bg=BG_DARK)
        btn_frame.pack(side="right")
        self._make_btn(btn_frame, "➕ 상품 추가", ACCENT_BLUE,   self._open_add_dialog).pack(side="left", padx=4)
        self._make_btn(btn_frame, "✏️  수정",     ACCENT_AMBER,  self._open_edit_dialog).pack(side="left", padx=4)
        self._make_btn(btn_frame, "🗑  삭제",      ACCENT_RED,    self._delete_item).pack(side="left", padx=4)
        self._make_btn(btn_frame, "📥 입고",       ACCENT_GREEN,  self._stock_in).pack(side="left", padx=4)
        self._make_btn(btn_frame, "📤 출고",       ACCENT_PURPLE, self._stock_out).pack(side="left", padx=4)

        # 검색바
        search_row = tk.Frame(parent, bg=BG_DARK)
        search_row.pack(fill="x", pady=(0,8))

        tk.Label(search_row, text="🔍", bg=BG_DARK, fg=TEXT_MUTED,
                 font=("Malgun Gothic", 12)).pack(side="left")

        self._search_var = tk.StringVar()
        search_entry = tk.Entry(search_row, textvariable=self._search_var,
                                bg=BG_CARD, fg=TEXT_PRIMARY, insertbackground=TEXT_PRIMARY,
                                relief="flat", font=("Malgun Gothic", 10),
                                width=28)
        search_entry.pack(side="left", padx=8, ipady=6)
        search_entry.insert(0, "상품명 또는 공급업체 검색...")
        search_entry.bind("<FocusIn>",  lambda e: self._clear_placeholder(search_entry))
        search_entry.bind("<FocusOut>", lambda e: self._restore_placeholder(search_entry))
        self._search_var.trace_add("write", lambda *_: self.refresh_table())

        # 카테고리 필터
        tk.Label(search_row, text="카테고리:", bg=BG_DARK, fg=TEXT_MUTED,
                 font=("Malgun Gothic", 9)).pack(side="left", padx=(12,4))
        self._cat_var = tk.StringVar(value="전체")
        self._cat_combo = ttk.Combobox(search_row, textvariable=self._cat_var,
                                        state="readonly", width=12,
                                        font=("Malgun Gothic", 9))
        self._cat_combo["values"] = self.data.categories
        self._cat_combo.pack(side="left")
        self._cat_combo.bind("<<ComboboxSelected>>", lambda _: self.refresh_table())

        # Treeview
        cols = ("id","name","category","price","quantity","unit","supplier","created_at")
        col_names = ("ID","상품명","카테고리","단가(¥)","재고","단위","공급업체","등록일")
        col_widths = (45, 200, 90, 110, 70, 60, 120, 95)

        tree_frame = tk.Frame(parent, bg=BG_DARK)
        tree_frame.pack(fill="both", expand=True)

        self._tree = ttk.Treeview(tree_frame, columns=cols, show="headings",
                                   style="Inv.Treeview", selectmode="browse")
        for col, name, w in zip(cols, col_names, col_widths):
            self._tree.heading(col, text=name,
                               command=lambda c=col: self._sort_tree(c))
            self._tree.column(col, width=w, minwidth=40)

        vsb = ttk.Scrollbar(tree_frame, orient="vertical",
                            command=self._tree.yview)
        self._tree.configure(yscrollcommand=vsb.set)
        self._tree.pack(side="left", fill="both", expand=True)
        vsb.pack(side="right", fill="y")

        # 태그 (재고 부족 강조)
        self._tree.tag_configure("low",  background="#2D1A1A", foreground=ACCENT_RED)
        self._tree.tag_configure("warn", background="#2D2A1A", foreground=ACCENT_AMBER)
        self._tree.tag_configure("even", background=BG_ROW_ALT)

        # 더블클릭 = 수정
        self._tree.bind("<Double-1>", lambda _: self._open_edit_dialog())

    def _make_btn(self, parent, text, color, cmd):
        return tk.Button(parent, text=text, bg=color, fg="#FFFFFF",
                         activebackground=color, activeforeground="#FFFFFF",
                         relief="flat", padx=10, pady=6,
                         font=("Malgun Gothic", 9, "bold"),
                         cursor="hand2", command=cmd)

    def _clear_placeholder(self, entry):
        if entry.get() == "상품명 또는 공급업체 검색...":
            entry.delete(0, "end")
            entry.configure(fg=TEXT_PRIMARY)

    def _restore_placeholder(self, entry):
        if not entry.get():
            entry.insert(0, "상품명 또는 공급업체 검색...")
            entry.configure(fg=TEXT_MUTED)

    def refresh_table(self):
        kw = self._search_var.get()
        if kw == "상품명 또는 공급업체 검색...":
            kw = ""
        cat = self._cat_var.get() if hasattr(self, "_cat_var") else "전체"
        items = self.data.search(kw, cat)

        # 카테고리 목록 갱신
        if hasattr(self, "_cat_combo"):
            self._cat_combo["values"] = self.data.categories

        self._tree.delete(*self._tree.get_children())
        for i, item in enumerate(items):
            tag = "low" if item["quantity"] == 0 else \
                  "warn" if item["quantity"] <= LOW_STOCK_THRESHOLD else \
                  ("even" if i % 2 else "")
            self._tree.insert("", "end", iid=str(item["id"]),
                values=(
                    item["id"],
                    item["name"],
                    item["category"],
                    f"{item['price']:,}",
                    item["quantity"],
                    item["unit"],
                    item["supplier"],
                    item["created_at"],
                ),
                tags=(tag,))

    def _sort_tree(self, col):
        data = [(self._tree.set(k, col), k) for k in self._tree.get_children("")]
        try:
            data.sort(key=lambda t: int(t[0].replace(",","")))
        except ValueError:
            data.sort()
        for idx, (_, k) in enumerate(data):
            self._tree.move(k, "", idx)

    def _selected_id(self):
        sel = self._tree.selection()
        if not sel:
            messagebox.showwarning("선택 필요", "먼저 목록에서 항목을 선택해 주세요.")
            return None
        return int(sel[0])

    # ─── 입출고 내역 패널 ─────────────────────
    def _build_transaction_panel(self, parent):
        tk.Label(parent, text="🔄  입출고 내역", bg=BG_DARK, fg=TEXT_PRIMARY,
                 font=("Malgun Gothic", 14, "bold")).pack(anchor="w", pady=(0,12))

        cols = ("datetime","name","type","quantity","note")
        col_names = ("날짜/시간","상품명","구분","수량","비고")
        col_widths = (140, 240, 70, 70, 300)

        frame = tk.Frame(parent, bg=BG_DARK)
        frame.pack(fill="both", expand=True)

        self._tx_tree = ttk.Treeview(frame, columns=cols, show="headings",
                                      style="Inv.Treeview")
        for col, name, w in zip(cols, col_names, col_widths):
            self._tx_tree.heading(col, text=name)
            self._tx_tree.column(col, width=w, minwidth=40)

        self._tx_tree.tag_configure("in",  foreground=ACCENT_GREEN)
        self._tx_tree.tag_configure("out", foreground=ACCENT_RED)

        vsb = ttk.Scrollbar(frame, orient="vertical", command=self._tx_tree.yview)
        self._tx_tree.configure(yscrollcommand=vsb.set)
        self._tx_tree.pack(side="left", fill="both", expand=True)
        vsb.pack(side="right", fill="y")

    def refresh_tx_table(self):
        self._tx_tree.delete(*self._tx_tree.get_children())
        for tx in reversed(self.data.transactions):
            tag = "in" if tx["type"] == "입고" else "out"
            self._tx_tree.insert("", "end",
                values=(tx["datetime"], tx["name"], tx["type"],
                        tx["quantity"], tx["note"]),
                tags=(tag,))

    # ─── 재고 부족 패널 ───────────────────────
    def _build_low_stock_panel(self, parent):
        tk.Label(parent, text="⚠️  재고 부족 품목", bg=BG_DARK, fg=ACCENT_AMBER,
                 font=("Malgun Gothic", 14, "bold")).pack(anchor="w", pady=(0,12))

        self._low_tree_frame = tk.Frame(parent, bg=BG_DARK)
        self._low_tree_frame.pack(fill="both", expand=True)

        cols = ("name","category","quantity","unit","supplier")
        col_names = ("상품명","카테고리","현재 재고","단위","공급업체")
        col_widths = (240, 110, 100, 60, 160)

        self._low_tree = ttk.Treeview(self._low_tree_frame, columns=cols,
                                       show="headings", style="Inv.Treeview")
        for col, name, w in zip(cols, col_names, col_widths):
            self._low_tree.heading(col, text=name)
            self._low_tree.column(col, width=w, minwidth=40)

        self._low_tree.tag_configure("zero", foreground=ACCENT_RED)
        self._low_tree.tag_configure("low",  foreground=ACCENT_AMBER)

        vsb = ttk.Scrollbar(self._low_tree_frame, orient="vertical",
                            command=self._low_tree.yview)
        self._low_tree.configure(yscrollcommand=vsb.set)
        self._low_tree.pack(side="left", fill="both", expand=True)
        vsb.pack(side="right", fill="y")

    def refresh_low_stock(self):
        self._low_tree.delete(*self._low_tree.get_children())
        for item in self.data.low_stock_items:
            tag = "zero" if item["quantity"] == 0 else "low"
            self._low_tree.insert("", "end",
                values=(item["name"], item["category"],
                        item["quantity"], item["unit"], item["supplier"]),
                tags=(tag,))

    # ─── 다이얼로그: 상품 추가/수정 ──────────
    def _open_add_dialog(self):
        self._item_dialog(title="➕  상품 추가", item=None)

    def _open_edit_dialog(self):
        iid = self._selected_id()
        if iid is None:
            return
        item = self.data.get_item(iid)
        if item:
            self._item_dialog(title="✏️  상품 수정", item=item)

    def _item_dialog(self, title, item=None):
        dlg = tk.Toplevel(self)
        dlg.title(title)
        dlg.geometry("420x440")
        dlg.configure(bg=BG_CARD)
        dlg.grab_set()
        dlg.resizable(False, False)
        # 중앙 배치
        dlg.update_idletasks()
        x = self.winfo_x() + (self.winfo_width() - 420) // 2
        y = self.winfo_y() + (self.winfo_height() - 440) // 2
        dlg.geometry(f"420x440+{x}+{y}")

        tk.Label(dlg, text=title, bg=BG_CARD, fg=TEXT_PRIMARY,
                 font=("Malgun Gothic", 13, "bold")).pack(pady=(20,16))

        fields = [
            ("상품명",     "name",     item["name"]     if item else ""),
            ("카테고리",   "category", item["category"] if item else ""),
            ("단가 (¥)",  "price",    str(item["price"]) if item else ""),
            ("수량",       "quantity", str(item["quantity"]) if item else ""),
            ("단위",       "unit",     item["unit"]     if item else "개"),
            ("공급업체",   "supplier", item["supplier"] if item else ""),
        ]

        vars_ = {}
        for label, key, default in fields:
            row = tk.Frame(dlg, bg=BG_CARD)
            row.pack(fill="x", padx=24, pady=4)
            tk.Label(row, text=label, bg=BG_CARD, fg=TEXT_MUTED,
                     font=("Malgun Gothic", 9), width=10, anchor="w").pack(side="left")
            var = tk.StringVar(value=default)
            vars_[key] = var
            tk.Entry(row, textvariable=var, bg=BG_DARK, fg=TEXT_PRIMARY,
                     insertbackground=TEXT_PRIMARY, relief="flat",
                     font=("Malgun Gothic", 10),
                     highlightthickness=1, highlightcolor=ACCENT_BLUE,
                     highlightbackground=BORDER_COLOR).pack(side="left", fill="x",
                                                             expand=True, ipady=5)

        def _save():
            try:
                name     = vars_["name"].get().strip()
                category = vars_["category"].get().strip()
                price    = int(vars_["price"].get().replace(",",""))
                quantity = int(vars_["quantity"].get())
                unit     = vars_["unit"].get().strip() or "개"
                supplier = vars_["supplier"].get().strip()
            except ValueError:
                messagebox.showerror("입력 오류", "단가와 수량은 숫자로 입력해 주세요.", parent=dlg)
                return
            if not name or not category:
                messagebox.showerror("입력 오류", "상품명과 카테고리는 필수입니다.", parent=dlg)
                return

            if item:
                self.data.update_item(item["id"], name=name, category=category,
                                      price=price, quantity=quantity,
                                      unit=unit, supplier=supplier)
            else:
                self.data.add_item(name, category, price, quantity, unit, supplier)

            self.refresh_table()
            self.refresh_dashboard()
            dlg.destroy()

        btn_row = tk.Frame(dlg, bg=BG_CARD)
        btn_row.pack(pady=16)
        tk.Button(btn_row, text="저장", bg=ACCENT_BLUE, fg="#FFF",
                  relief="flat", padx=20, pady=8,
                  font=("Malgun Gothic", 10, "bold"),
                  cursor="hand2", command=_save).pack(side="left", padx=8)
        tk.Button(btn_row, text="취소", bg=BORDER_COLOR, fg=TEXT_MUTED,
                  relief="flat", padx=20, pady=8,
                  font=("Malgun Gothic", 10),
                  cursor="hand2", command=dlg.destroy).pack(side="left", padx=8)

    def _delete_item(self):
        iid = self._selected_id()
        if iid is None:
            return
        item = self.data.get_item(iid)
        if not item:
            return
        if messagebox.askyesno("삭제 확인",
                               f"'{item['name']}' 을(를) 삭제하시겠습니까?\n이 작업은 되돌릴 수 없습니다.",
                               icon="warning"):
            self.data.delete_item(iid)
            self.refresh_table()
            self.refresh_dashboard()

    # ─── 입출고 다이얼로그 ────────────────────
    def _stock_dialog(self, tx_type: str):
        iid = self._selected_id()
        if iid is None:
            return
        item = self.data.get_item(iid)
        if not item:
            return

        dlg = tk.Toplevel(self)
        dlg.title(f"{'📥 입고' if tx_type == 'in' else '📤 출고'} - {item['name']}")
        dlg.geometry("360x260")
        dlg.configure(bg=BG_CARD)
        dlg.grab_set()
        dlg.resizable(False, False)
        x = self.winfo_x() + (self.winfo_width() - 360) // 2
        y = self.winfo_y() + (self.winfo_height() - 260) // 2
        dlg.geometry(f"360x260+{x}+{y}")

        color = ACCENT_GREEN if tx_type == "in" else ACCENT_RED
        label = "입고" if tx_type == "in" else "출고"

        tk.Label(dlg, text=f"{item['name']} — {label}",
                 bg=BG_CARD, fg=color,
                 font=("Malgun Gothic", 12, "bold")).pack(pady=(20,4))
        tk.Label(dlg, text=f"현재 재고: {item['quantity']} {item['unit']}",
                 bg=BG_CARD, fg=TEXT_MUTED,
                 font=("Malgun Gothic", 10)).pack()

        for lbl, key in [("수량", "qty"), ("비고", "note")]:
            row = tk.Frame(dlg, bg=BG_CARD)
            row.pack(fill="x", padx=24, pady=6)
            tk.Label(row, text=lbl, bg=BG_CARD, fg=TEXT_MUTED,
                     font=("Malgun Gothic", 9), width=5, anchor="w").pack(side="left")

        qty_var  = tk.StringVar(value="1")
        note_var = tk.StringVar()

        for var, lbl in [(qty_var,"수량"), (note_var,"비고")]:
            row = tk.Frame(dlg, bg=BG_CARD)
            row.pack(fill="x", padx=24, pady=4)
            tk.Label(row, text=lbl, bg=BG_CARD, fg=TEXT_MUTED,
                     font=("Malgun Gothic", 9), width=5, anchor="w").pack(side="left")
            tk.Entry(row, textvariable=var, bg=BG_DARK, fg=TEXT_PRIMARY,
                     insertbackground=TEXT_PRIMARY, relief="flat",
                     font=("Malgun Gothic", 10),
                     highlightthickness=1, highlightcolor=color,
                     highlightbackground=BORDER_COLOR).pack(side="left", fill="x",
                                                             expand=True, ipady=5)

        def _apply():
            try:
                qty = int(qty_var.get())
                if qty <= 0:
                    raise ValueError
            except ValueError:
                messagebox.showerror("오류", "수량을 올바르게 입력해 주세요.", parent=dlg)
                return

            note = note_var.get().strip()
            if tx_type == "in":
                self.data.stock_in(iid, qty, note)
            else:
                if not self.data.stock_out(iid, qty, note):
                    messagebox.showerror("오류", "재고가 부족합니다.", parent=dlg)
                    return

            self.refresh_table()
            self.refresh_dashboard()
            dlg.destroy()
            messagebox.showinfo("완료", f"{label} 처리가 완료되었습니다.\n수량: {qty} {item['unit']}")

        btn_row = tk.Frame(dlg, bg=BG_CARD)
        btn_row.pack(pady=12)
        tk.Button(btn_row, text=f"  {label} 처리  ", bg=color, fg="#FFF",
                  relief="flat", padx=16, pady=8,
                  font=("Malgun Gothic", 10, "bold"),
                  cursor="hand2", command=_apply).pack(side="left", padx=8)
        tk.Button(btn_row, text="취소", bg=BORDER_COLOR, fg=TEXT_MUTED,
                  relief="flat", padx=16, pady=8,
                  font=("Malgun Gothic", 10),
                  cursor="hand2", command=dlg.destroy).pack(side="left", padx=8)

    def _stock_in(self):
        self._stock_dialog("in")

    def _stock_out(self):
        self._stock_dialog("out")

    # ─── CSV 가져오기/내보내기 ────────────────
    def _export_csv(self):
        path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV 파일", "*.csv")],
            title="CSV 내보내기",
            initialfile="재고목록.csv",
        )
        if path:
            self.data.export_csv(path)
            messagebox.showinfo("내보내기 완료", f"파일이 저장되었습니다:\n{path}")

    def _import_csv(self):
        path = filedialog.askopenfilename(
            filetypes=[("CSV 파일", "*.csv")],
            title="CSV 가져오기",
        )
        if path:
            self.data.import_csv(path)
            self.refresh_table()
            self.refresh_dashboard()
            messagebox.showinfo("가져오기 완료", "CSV 파일을 불러왔습니다.")


# ─────────────────────────────────────────────
#  진입점
# ─────────────────────────────────────────────
if __name__ == "__main__":
    app = InventoryApp()
    app.mainloop()
