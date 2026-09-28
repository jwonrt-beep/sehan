#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
app.py — 파나소닉 용접로봇 재고관리 Flask 앱
"""

import socket
from functools import wraps
from flask import (Flask, render_template, request, redirect,
                   url_for, session, jsonify, send_from_directory)
from werkzeug.security import check_password_hash
import database as db
import backup_manager

app = Flask(__name__)
app.secret_key = 'panasonic_inv_secret_2024_change_me!'
db.init_db()  # Ensure database schema is initialized on WSGI startup (e.g. PythonAnywhere)
backup_manager.start_scheduler()  # 자정 자동 백업 스케줄러 실행


# ─── Auth 데코레이터 ─────────────────────────
def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated


def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        if session.get('role') != 'admin':
            return jsonify({'success': False, 'message': '관리자 권한이 필요합니다.'}), 403
        return f(*args, **kwargs)
    return decorated


def client_ip():
    return request.headers.get('X-Forwarded-For', request.remote_addr or '')


def audit(action, target_type, target_id, target_name,
          before=None, after=None, note=''):
    db.add_audit_log(
        user_id=session.get('user_id'),
        user_name=session.get('user_name', ''),
        action=action,
        target_type=target_type,
        target_id=target_id,
        target_name=target_name,
        before_data=before,
        after_data=after,
        note=note,
        ip_address=client_ip()
    )


# ─── 로그인 / 로그아웃 ───────────────────────
@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    error = None
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        user = db.get_user_by_username(username)
        if user and user['is_active'] and check_password_hash(user['password_hash'], password):
            session.update({
                'user_id':   user['id'],
                'user_name': user['name'],
                'username':  user['username'],
                'role':      user['role'],
            })
            audit('LOGIN', 'user', user['id'], user['name'])
            return redirect(url_for('dashboard'))
        error = '아이디 또는 비밀번호가 올바르지 않거나 비활성화된 계정입니다.'
    return render_template('login.html', error=error)


@app.route('/logout')
def logout():
    if 'user_id' in session:
        audit('LOGOUT', 'user', session['user_id'], session['user_name'])
    session.clear()
    return redirect(url_for('login'))


# ─── 대시보드 ────────────────────────────────
@app.route('/')
@login_required
def index():
    return redirect(url_for('dashboard'))


@app.route('/dashboard')
@login_required
def dashboard():
    stats     = db.get_stats()
    low_items = [p for p in db.get_all_products()
                 if p['quantity'] <= p['low_stock_alert']]
    recent    = db.get_audit_logs(limit=10)
    return render_template('dashboard.html',
                           stats=stats,
                           low_items=low_items,
                           recent=recent,
                           active='dashboard')


# ─── 로봇 메뉴얼 보기 ─────────────────────────
@app.route('/manual')
@login_required
def manual():
    search_query = request.args.get('search', '').strip()
    return render_template('manual.html', active='manual', search_query=search_query)


# ─── 재고 목록 ──────────────────────────────
@app.route('/products')
@login_required
def products():
    search   = request.args.get('search', '').strip()
    category = request.args.get('category', '전체')
    items      = db.get_all_products(search=search, category=category)
    categories = db.get_categories()
    return render_template('products.html',
                           items=items,
                           categories=categories,
                           search=search,
                           category=category,
                           active='products')


# ─── 상품 API ───────────────────────────────
@app.route('/api/product', methods=['POST'])
@login_required
def api_add_product():
    d = request.get_json(silent=True) or {}
    try:
        pid = db.add_product(
            item_code=d.get('item_code', '').strip(),
            name=d['name'].strip(),
            category=d['category'].strip(),
            model_spec=d.get('model_spec', '').strip(),
            price=int(d.get('price', 0)),
            quantity=int(d.get('quantity', 0)),
            unit=d.get('unit', '개').strip(),
            location=d.get('location', '').strip(),
            supplier=d.get('supplier', '').strip(),
            low_stock_alert=int(d.get('low_stock_alert', 10))
        )
        product = db.get_product(pid)
        audit('ADD', 'product', pid, d['name'], after=product)
        return jsonify({'success': True, 'message': f"'{d['name']}' 품목이 등록되었습니다."})
    except (KeyError, ValueError) as e:
        return jsonify({'success': False, 'message': f'입력 오류: {e}'}), 400


@app.route('/api/product/import-excel', methods=['POST'])
@login_required
def api_import_excel():
    if 'file' not in request.files:
        return jsonify({'success': False, 'message': '파일이 전송되지 않았습니다.'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'success': False, 'message': '선택된 파일이 없습니다.'}), 400
    if not file.filename.lower().endswith(('.xlsx', '.xls')):
        return jsonify({'success': False, 'message': '엑셀 파일(.xlsx, .xls)만 업로드할 수 있습니다.'}), 400
    
    try:
        inserted, skipped = db.import_excel_to_db(
            file.stream,
            user_id=session.get('user_id'),
            user_name=session.get('user_name', '시스템')
        )
        return jsonify({
            'success': True,
            'message': f'엑셀 가져오기가 완료되었습니다. (등록: {inserted}건, 스킵: {skipped}건)'
        })
    except Exception as e:
        return jsonify({'success': False, 'message': f'엑셀 처리 중 오류 발생: {str(e)}'}), 500


@app.route('/api/product/update-prices-excel', methods=['POST'])
@login_required
def api_update_prices_excel():
    if 'file' not in request.files:
        return jsonify({'success': False, 'message': '파일이 전송되지 않았습니다.'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'success': False, 'message': '선택된 파일이 없습니다.'}), 400
    if not file.filename.lower().endswith(('.xlsx', '.xls')):
        return jsonify({'success': False, 'message': '엑셀 파일(.xlsx, .xls)만 업로드할 수 있습니다.'}), 400
    
    try:
        updated, no_change, no_match = db.update_prices_from_excel(
            file.stream,
            user_id=session.get('user_id', 0),
            user_name=session.get('user_name', '시스템')
        )
        return jsonify({
            'success': True,
            'message': f'단가 업데이트가 완료되었습니다. (업데이트: {updated}건, 변경없음: {no_change}건, 미매칭: {no_match}건)'
        })
    except Exception as e:
        return jsonify({'success': False, 'message': f'단가 업데이트 중 오류 발생: {str(e)}'}), 500



@app.route('/api/product/<int:pid>', methods=['GET'])
@login_required
def api_get_product(pid):
    p = db.get_product(pid)
    if not p:
        return jsonify({'success': False}), 404
    return jsonify({'success': True, 'product': p})


@app.route('/api/product/<int:pid>', methods=['PUT'])
@login_required
def api_edit_product(pid):
    before = db.get_product(pid)
    if not before:
        return jsonify({'success': False, 'message': '품목을 찾을 수 없습니다.'}), 404
    d = request.get_json(silent=True) or {}
    try:
        db.update_product(pid,
            item_code=d.get('item_code', '').strip(),
            name=d['name'].strip(),
            category=d['category'].strip(),
            model_spec=d.get('model_spec', '').strip(),
            price=int(d.get('price', 0)),
            quantity=int(d.get('quantity', 0)),
            unit=d.get('unit', '개').strip(),
            location=d.get('location', '').strip(),
            supplier=d.get('supplier', '').strip(),
            low_stock_alert=int(d.get('low_stock_alert', 10))
        )
        after = db.get_product(pid)
        audit('EDIT', 'product', pid, d['name'], before=before, after=after)
        return jsonify({'success': True, 'message': f"'{d['name']}' 품목이 수정되었습니다."})
    except (KeyError, ValueError) as e:
        return jsonify({'success': False, 'message': f'입력 오류: {e}'}), 400


@app.route('/api/product/<int:pid>', methods=['DELETE'])
@login_required
def api_delete_product(pid):
    product = db.get_product(pid)
    if not product:
        return jsonify({'success': False, 'message': '품목을 찾을 수 없습니다.'}), 404
    db.delete_product(pid)
    audit('DELETE', 'product', pid, product['name'], before=product)
    return jsonify({'success': True, 'message': f"'{product['name']}' 품목이 삭제되었습니다."})


@app.route('/api/product/<int:pid>/stock-in', methods=['POST'])
@login_required
def api_stock_in(pid):
    product = db.get_product(pid)
    if not product:
        return jsonify({'success': False, 'message': '품목 없음'}), 404
    d = request.get_json(silent=True) or {}
    try:
        qty  = int(d.get('quantity', 0))
        note = d.get('note', '').strip()
        if qty <= 0: raise ValueError
    except (TypeError, ValueError):
        return jsonify({'success': False, 'message': '수량을 올바르게 입력해 주세요.'}), 400

    before_qty = product['quantity']
    db.stock_in(pid, qty)
    after = db.get_product(pid)
    audit('STOCK_IN', 'product', pid,
          f"[{product['item_code']}] {product['name']}",
          before={'quantity': before_qty},
          after={'quantity': after['quantity']},
          note=f"+{qty} {note}".strip())
    return jsonify({'success': True,
                    'message': f"입고 완료: +{qty}",
                    'new_qty': after['quantity']})


@app.route('/api/product/<int:pid>/stock-out', methods=['POST'])
@login_required
def api_stock_out(pid):
    product = db.get_product(pid)
    if not product:
        return jsonify({'success': False, 'message': '품목 없음'}), 404
    d = request.get_json(silent=True) or {}
    try:
        qty  = int(d.get('quantity', 0))
        note = d.get('note', '').strip()
        if qty <= 0: raise ValueError
    except (TypeError, ValueError):
        return jsonify({'success': False, 'message': '수량을 올바르게 입력해 주세요.'}), 400

    before_qty = product['quantity']
    ok = db.stock_out(pid, qty)
    if not ok:
        return jsonify({'success': False,
                        'message': f"재고 부족! 현재 재고: {product['quantity']} {product['unit']}"}), 400

    after = db.get_product(pid)
    audit('STOCK_OUT', 'product', pid,
          f"[{product['item_code']}] {product['name']}",
          before={'quantity': before_qty},
          after={'quantity': after['quantity']},
          note=f"-{qty} {note}".strip())
    return jsonify({'success': True,
                    'message': f"출고 완료: -{qty}",
                    'new_qty': after['quantity']})


# ─── 입출고 내역 ─────────────────────────────
@app.route('/history')
@login_required
def history():
    action = request.args.get('action', '')
    search = request.args.get('search', '').strip()
    raw  = db.get_audit_logs(limit=500, action_filter=action, search=search)
    import json
    logs = []
    for l in raw:
        if l['action'] not in ('STOCK_IN', 'STOCK_OUT'):
            continue
        try:
            if l['before_data']:
                b = json.loads(l['before_data'])
                if isinstance(b, dict) and 'quantity' in b:
                    l['before_data'] = b['quantity']
        except: pass
        try:
            if l['after_data']:
                a = json.loads(l['after_data'])
                if isinstance(a, dict) and 'quantity' in a:
                    l['after_data'] = a['quantity']
        except: pass
        
        try:
            b_qty = int(l['before_data'])
            a_qty = int(l['after_data'])
            diff = a_qty - b_qty
            sign = '+' if diff > 0 else ''
            
            note_str = l['note']
            if note_str.startswith('+') or note_str.startswith('-'):
                space_idx = note_str.find(' ')
                real_note = note_str[space_idx:].strip() if space_idx != -1 else ''
                l['note'] = f"{sign}{diff} {real_note}".strip()
        except:
            pass
        
        logs.append(l)

    return render_template('history.html',
                           logs=logs,
                           action_filter=action,
                           search=search,
                           active='history')


# ─── 업무일지 ────────────────────────────────
@app.route('/work_logs')
@login_required
def work_logs():
    today_str = db.datetime.now(db.KST).strftime('%Y-%m-%d')
    default_start = (db.datetime.now(db.KST) - db.timedelta(days=7)).strftime('%Y-%m-%d')
    
    start_date = request.args.get('start_date', default_start)
    end_date = request.args.get('end_date', today_str)
    search_keyword = request.args.get('search', '').strip()
    
    # 대표/팀장(admin, manager)인 경우에만 다른 직원의 일지를 볼 수 있음
    role = session.get('role', 'staff')
    if role in ['admin', 'manager']:
        user_filter = request.args.get('user', '')
    else:
        user_filter = str(session.get('user_id'))
    
    logs = db.get_work_logs(
        user_id=int(user_filter) if user_filter.isdigit() else None,
        work_date_start=start_date if start_date else None,
        work_date_end=end_date if end_date else None,
        search_keyword=search_keyword if search_keyword else None
    )
    users = db.get_all_users()
    
    return render_template('work_logs.html',
                           logs=logs,
                           users=users,
                           start_date=start_date,
                           end_date=end_date,
                           search=search_keyword,
                           user_filter=user_filter,
                           active='work_logs')

@app.route('/api/work_log', methods=['POST'])
@login_required
def api_add_work_log():
    d = request.get_json(silent=True) or {}
    try:
        work_date = d.get('work_date', '').strip()
        today_work = d.get('today_work', '').strip()
        tomorrow_work = d.get('tomorrow_work', '').strip()
        memo = d.get('memo', '').strip()
        
        if not work_date:
            raise ValueError("날짜를 입력하세요.")
        if not today_work and not tomorrow_work and not memo:
            raise ValueError("내용을 한 칸 이상 입력하세요.")
            
        log_id = db.add_work_log(
            user_id=session.get('user_id'),
            user_name=session.get('user_name'),
            work_date=work_date,
            today_work=today_work,
            tomorrow_work=tomorrow_work,
            memo=memo
        )
        audit('ADD_WORK_LOG', 'work_log', log_id, f"{work_date} 업무일지")
        return jsonify({'success': True, 'message': "업무일지가 등록되었습니다."})
    except ValueError as e:
        return jsonify({'success': False, 'message': str(e)}), 400

@app.route('/api/work_log/<int:log_id>', methods=['PUT'])
@login_required
def api_edit_work_log(log_id):
    log = db.get_work_log(log_id)
    if not log:
        return jsonify({'success': False, 'message': '업무일지를 찾을 수 없습니다.'}), 404
        
    role = session.get('role', 'staff')
    if log['user_id'] != session.get('user_id') and role not in ['admin', 'manager']:
        return jsonify({'success': False, 'message': '본인의 업무일지만 수정할 수 있습니다.'}), 403
        
    d = request.get_json(silent=True) or {}
    try:
        new_today = d.get('today_work', '').strip()
        new_tomorrow = d.get('tomorrow_work', '').strip()
        new_memo = d.get('memo', '').strip()
        
        if not new_today and not new_tomorrow and not new_memo:
            raise ValueError("추가할 내용을 한 칸 이상 입력하세요.")
            
        timestamp = db.datetime.now(db.KST).strftime('%m-%d %H:%M')
        
        final_today = log['today_work'] + (f"\n\n[{timestamp} 추가]\n{new_today}" if new_today else "")
        final_tomorrow = log['tomorrow_work'] + (f"\n\n[{timestamp} 추가]\n{new_tomorrow}" if new_tomorrow else "")
        final_memo = log['memo'] + (f"\n\n[{timestamp} 추가]\n{new_memo}" if new_memo else "")
        
        db.update_work_log(log_id, final_today.strip(), final_tomorrow.strip(), final_memo.strip())
        audit('EDIT_WORK_LOG', 'work_log', log_id, f"{log['work_date']} 업무일지 내용 추가")
        return jsonify({'success': True, 'message': "기존 일지에 내용이 추가되었습니다."})
    except ValueError as e:
        return jsonify({'success': False, 'message': str(e)}), 400

@app.route('/api/work_log/<int:log_id>', methods=['DELETE'])
@login_required
def api_delete_work_log(log_id):
    log = db.get_work_log(log_id)
    if not log:
        return jsonify({'success': False, 'message': '업무일지를 찾을 수 없습니다.'}), 404
        
    role = session.get('role', 'staff')
    if log['user_id'] != session.get('user_id') and role not in ['admin', 'manager']:
        return jsonify({'success': False, 'message': '본인의 업무일지만 삭제할 수 있습니다.'}), 403
        
    db.delete_work_log(log_id)
    audit('DELETE_WORK_LOG', 'work_log', log_id, f"{log['work_date']} 업무일지 삭제")
    return jsonify({'success': True, 'message': "업무일지가 삭제되었습니다."})


# ─── 관리자 — 직원 관리 ─────────────────────
@app.route('/admin/users')
@login_required
def admin_users():
    if session.get('role') != 'admin':
        return redirect(url_for('dashboard'))
    users = db.get_all_users()
    return render_template('admin_users.html', users=users, active='admin_users')


@app.route('/api/admin/user', methods=['POST'])
@admin_required
def api_add_user():
    d = request.get_json(silent=True) or {}
    ok = db.create_user(
        username=d.get('username', '').strip(),
        password=d.get('password', ''),
        name=d.get('name', '').strip(),
        role=d.get('role', 'staff')
    )
    if ok:
        audit('ADD', 'user', None, d.get('name'))
        return jsonify({'success': True, 'message': f"'{d['name']}' 계정이 생성되었습니다."})
    return jsonify({'success': False, 'message': '이미 사용 중인 아이디입니다.'}), 400


@app.route('/api/admin/user/<int:uid>/toggle', methods=['POST'])
@admin_required
def api_toggle_user(uid):
    if uid == session.get('user_id'):
        return jsonify({'success': False, 'message': '본인 계정은 비활성화할 수 없습니다.'}), 400
    user = db.get_user_by_id(uid)
    if not user:
        return jsonify({'success': False, 'message': '사용자 없음'}), 404
    db.toggle_user_active(uid)
    state = '비활성화' if user['is_active'] else '활성화'
    audit('TOGGLE_USER', 'user', uid, user['name'], note=state)
    return jsonify({'success': True, 'message': f"'{user['name']}' 계정을 {state}했습니다."})


@app.route('/api/admin/user/<int:uid>/password', methods=['POST'])
@admin_required
def api_reset_password(uid):
    d    = request.get_json(silent=True) or {}
    user = db.get_user_by_id(uid)
    if not user:
        return jsonify({'success': False, 'message': '사용자 없음'}), 404
    db.update_user(uid, password=d.get('password', ''))
    audit('RESET_PW', 'user', uid, user['name'])
    return jsonify({'success': True, 'message': f"'{user['name']}' 비밀번호가 변경되었습니다."})


# ─── 관리자 — 감사 로그 ─────────────────────
@app.route('/admin/audit')
@login_required
def admin_audit():
    if session.get('role') != 'admin':
        return redirect(url_for('dashboard'))
    action_f = request.args.get('action', '')
    user_f   = request.args.get('user', '')
    search   = request.args.get('search', '').strip()
    logs     = db.get_audit_logs(limit=500, action_filter=action_f,
                                 user_filter=user_f, search=search)
    users    = db.get_all_users()
    return render_template('admin_audit.html',
                           logs=logs,
                           action_filter=action_f,
                           user_filter=user_f,
                           search=search,
                           users=users,
                           active='admin_audit')


# ─── 관리자 — DB 백업 및 이메일 설정 ───────────
@app.route('/admin/backup')
@login_required
def admin_backup():
    if session.get('role') != 'admin':
        return redirect(url_for('dashboard'))
    config = db.get_system_config()
    history = db.get_backup_history(limit=50)
    return render_template('admin_backup.html',
                           config=config,
                           history=history,
                           active='admin_backup')


@app.route('/api/admin/backup/config', methods=['POST'])
@admin_required
def api_save_backup_config():
    d = request.get_json(silent=True) or {}
    db.set_system_config(d)
    audit('UPDATE_CONFIG', 'system', None, '백업 및 메일 설정 변경')
    return jsonify({'success': True, 'message': '백업 및 이메일 설정이 저장되었습니다.'})


@app.route('/api/admin/backup/run', methods=['POST'])
@admin_required
def api_run_backup_now():
    d = request.get_json(silent=True) or {}
    send_email = d.get('send_email', True)
    res = backup_manager.run_backup(send_email=send_email)
    audit('MANUAL_BACKUP', 'system', None, '수동 DB 백업 실행', note=res.get('message', ''))
    return jsonify(res)


@app.route('/admin/backup/download/<filename>')
@admin_required
def download_backup_file(filename):
    file_path = backup_manager.BACKUP_DIR / filename
    if not file_path.exists():
        return "파일을 찾을 수 없습니다.", 404
    return send_from_directory(backup_manager.BACKUP_DIR, filename, as_attachment=True)


# ─── 에러 핸들러 ─────────────────────────────
@app.errorhandler(404)
def not_found(e):
    return render_template('login.html', error='페이지를 찾을 수 없습니다.'), 404


# ─── 진입점 ──────────────────────────────────
if __name__ == '__main__':
    db.init_db()
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        local_ip = s.getsockname()[0]
        s.close()
    except Exception:
        local_ip = '127.0.0.1'

    print()
    print("=" * 52)
    print("  [파나소닉 용접로봇 재고관리 시스템 시작]")
    print("=" * 52)
    print(f"  PC 접속:     http://127.0.0.1:8080")
    print(f"  스마트폰:    http://{local_ip}:8080")
    print(f"  초기 계정:   admin / admin1234")
    print("=" * 52)
    print()

    app.run(host='0.0.0.0', port=8080, debug=False)
