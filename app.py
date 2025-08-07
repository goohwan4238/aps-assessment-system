# app.py
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
import sqlite3
import json
from datetime import datetime
import os

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'

# 데이터베이스 초기화
def init_db():
    try:
        conn = sqlite3.connect('aps_assessment.db')
        c = conn.cursor()
        
        print("데이터베이스 테이블 생성 중...")
        
        # 평가 영역 테이블
        c.execute('''CREATE TABLE IF NOT EXISTS categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            weight REAL NOT NULL,
            description TEXT,
            order_num INTEGER
        )''')
        
        # 평가 문항 테이블
        c.execute('''CREATE TABLE IF NOT EXISTS questions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category_id INTEGER,
            code TEXT NOT NULL,
            title TEXT NOT NULL,
            description TEXT,
            max_score INTEGER DEFAULT 5,
            order_num INTEGER,
            FOREIGN KEY (category_id) REFERENCES categories (id)
        )''')
        
        # 문항 선택지 테이블
        c.execute('''CREATE TABLE IF NOT EXISTS question_options (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            question_id INTEGER,
            score INTEGER,
            description TEXT,
            FOREIGN KEY (question_id) REFERENCES questions (id)
        )''')
        
        # 회사 테이블
        c.execute('''CREATE TABLE IF NOT EXISTS companies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            industry TEXT,
            size TEXT,
            contact_person TEXT,
            contact_email TEXT,
            created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )''')
        
        # 평가 이력 테이블
        c.execute('''CREATE TABLE IF NOT EXISTS assessments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company_id INTEGER,
            assessor_name TEXT,
            assessment_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            total_score REAL,
            maturity_level INTEGER,
            notes TEXT,
            FOREIGN KEY (company_id) REFERENCES companies (id)
        )''')
        
        # 평가 상세 결과 테이블
        c.execute('''CREATE TABLE IF NOT EXISTS assessment_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            assessment_id INTEGER,
            question_id INTEGER,
            score INTEGER,
            FOREIGN KEY (assessment_id) REFERENCES assessments (id),
            FOREIGN KEY (question_id) REFERENCES questions (id)
        )''')
        
        conn.commit()
        print("데이터베이스 테이블 생성 완료")
        conn.close()
        
    except Exception as e:
        print(f"데이터베이스 초기화 오류: {e}")
        if conn:
            conn.close()

# 초기 데이터 삽입
def insert_initial_data():
    try:
        conn = sqlite3.connect('aps_assessment.db')
        c = conn.cursor()
        
        # 기존 데이터 확인
        c.execute("SELECT COUNT(*) FROM categories")
        if c.fetchone()[0] > 0:
            print("초기 데이터가 이미 존재합니다.")
            conn.close()
            return
        
        print("초기 데이터 삽입 중...")
        
        # 카테고리 삽입
        categories = [
            (1, '현행 프로세스 평가', 0.35, '생산계획수립, 스케줄생성, 작업지시, 실행, 분석 프로세스 평가', 1),
            (2, '데이터 준비도 평가', 0.35, '기준정보, 판매계획, 계획수립용데이터, 실행실적 데이터 평가', 2),
            (3, '관련 시스템 평가', 0.15, 'ERP, MES, 연동 시스템 등 IT 시스템 평가', 3),
            (4, '거버넌스 평가', 0.15, '인력, 조직, 의사결정체계, 경영진 지원 평가', 4)
        ]
        
        c.executemany("INSERT INTO categories (id, name, weight, description, order_num) VALUES (?, ?, ?, ?, ?)", categories)
        
        # 문항 삽입
        questions = [
            # 현행 프로세스 평가
            (1, 1, '1.1.1', '생산계획 수립 주기', '생산계획을 얼마나 자주 수립하는지 평가', 5, 1),
            (2, 1, '1.1.2', '계획 수립 시 고려하는 제약조건', '계획 수립 시 고려하는 제약조건의 범위', 5, 2),
            (3, 1, '1.1.3', '계획 수립 방법론', '계획 수립에 사용하는 방법론과 도구', 5, 3),
            (4, 1, '1.2.1', '상세 스케줄링 수준', '스케줄링의 상세화 정도', 5, 4),
            (5, 1, '1.2.2', '스케줄 최적화 고려사항', '스케줄 최적화 시 고려하는 요소들', 5, 5),
            (6, 1, '1.3.1', '작업지시 전달 방식', '작업지시를 전달하는 방식', 5, 6),
            (7, 1, '1.3.2', '실행 모니터링 및 추적', '생산 실행 과정의 모니터링 수준', 5, 7),
            
            # 데이터 준비도 평가
            (8, 2, '2.1.1', 'BOM 정확도', 'Bill of Materials의 정확도 수준', 5, 1),
            (9, 2, '2.1.2', '공정정보 완성도', 'Routing 정보의 완성도', 5, 2),
            (10, 2, '2.1.3', '설비/자원 정보 관리', '설비 및 자원 정보 관리 수준', 5, 3),
            (11, 2, '2.2.1', '수요예측/판매계획 정확도', '수요 예측의 정확도', 5, 4),
            (12, 2, '2.2.2', '재고정보 실시간성', '재고 정보의 실시간성', 5, 5),
            (13, 2, '2.3.1', '생산실적 수집 방식', '생산 실적 데이터 수집 방법', 5, 6),
            (14, 2, '2.3.2', '품질/불량 데이터 관리', '품질 및 불량 데이터 관리 수준', 5, 7),
            
            # 관련 시스템 평가
            (15, 3, '3.1.1', 'ERP 시스템 활용도', 'ERP 시스템의 활용 수준', 5, 1),
            (16, 3, '3.1.2', 'MES 구축 수준', 'MES 시스템 구축 및 활용 수준', 5, 2),
            (17, 3, '3.1.3', '시스템 간 연동 수준', '시스템 간 데이터 연동 수준', 5, 3),
            (18, 3, '3.2.1', 'IT 인프라 준비도', 'IT 인프라의 준비 상태', 5, 4),
            (19, 3, '3.2.2', '데이터 관리 체계', '데이터 관리 시스템 및 체계', 5, 5),
            (20, 3, '3.3.1', '시스템 확장성', '시스템의 확장 가능성', 5, 6),
            (21, 3, '3.3.2', '외부 시스템 연동 능력', '외부 시스템과의 연동 능력', 5, 7),
            
            # 거버넌스 평가
            (22, 4, '4.1.1', 'APS 관련 전담 인력', 'APS 관련 전담 인력 현황', 5, 1),
            (23, 4, '4.1.2', '관련 업무 담당자의 전문성', '담당자의 전문성 수준', 5, 2),
            (24, 4, '4.1.3', '교육 및 역량 개발 체계', '교육 및 역량 개발 프로그램', 5, 3),
            (25, 4, '4.2.1', 'APS 도입/운영 의사결정 체계', '의사결정 체계의 완성도', 5, 4),
            (26, 4, '4.2.2', '변화 관리 프로세스', '변화 관리 프로세스의 체계화', 5, 5),
            (27, 4, '4.3.1', '경영진의 APS 도입 의지', '경영진의 지원 의지', 5, 6),
            (28, 4, '4.3.2', '투자 계획 및 예산 확보', '투자 계획 및 예산 확보 상태', 5, 7)
        ]
        
        c.executemany("INSERT INTO questions (id, category_id, code, title, description, max_score, order_num) VALUES (?, ?, ?, ?, ?, ?, ?)", questions)
        
        # 문항별 선택지 삽입
        options_data = {
            1: {  # 생산계획 수립 주기
                1: "불규칙적이며 수동으로 필요 시마다 수립",
                2: "월 단위로 정기적 수립",
                3: "주 단위로 정기적 수립",
                4: "일 단위로 정기적 수립",
                5: "실시간 또는 시간 단위로 동적 수립"
            },
            2: {  # 계획 수립 시 고려하는 제약조건
                1: "기본 생산 용량만 고려",
                2: "설비 용량 제약 고려",
                3: "설비 용량 + 인력 제약 고려",
                4: "설비 + 인력 + 자재 제약 고려",
                5: "모든 제약조건(설비, 인력, 자재, 품질, 납기 등) 종합 고려"
            },
            8: {  # BOM 정확도
                1: "60% 미만 (부정확한 정보 다수)",
                2: "60-70% (기본적 정보만 관리)",
                3: "70-85% (대부분 정확하나 일부 오류)",
                4: "85-95% (높은 정확도, 정기 검증)",
                5: "95% 이상 (매우 높은 정확도, 실시간 업데이트)"
            }
        }
        
        options = []
        for q_id in range(1, 29):
            for score in range(1, 6):
                if q_id in options_data:
                    description = options_data[q_id][score]
                else:
                    description = f"Level {score} - {['기본', '관리', '정의', '최적화', '혁신'][score-1]} 수준"
                
                options.append((q_id, score, description))
        
        c.executemany("INSERT INTO question_options (question_id, score, description) VALUES (?, ?, ?)", options)
        
        conn.commit()
        conn.close()
        print("초기 데이터 삽입 완료")
        
    except Exception as e:
        print(f"초기 데이터 삽입 오류: {e}")
        if conn:
            conn.close()

# 성숙도 레벨 계산
def calculate_maturity_level(total_score):
    max_score = 140  # 28문항 × 5점
    percentage = (total_score / max_score) * 100
    
    if percentage < 40:
        return 1
    elif percentage < 60:
        return 2
    elif percentage < 80:
        return 3
    elif percentage < 91:
        return 4
    else:
        return 5

# 라우트 정의
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/companies')
def companies():
    conn = sqlite3.connect('aps_assessment.db')
    c = conn.cursor()
    c.execute('''SELECT c.*, COUNT(a.id) as assessment_count 
                 FROM companies c 
                 LEFT JOIN assessments a ON c.id = a.company_id 
                 GROUP BY c.id
                 ORDER BY c.created_date DESC''')
    companies_data = c.fetchall()
    conn.close()
    return render_template('companies.html', companies=companies_data)

@app.route('/company/new', methods=['GET', 'POST'])
def new_company():
    if request.method == 'POST':
        conn = sqlite3.connect('aps_assessment.db')
        c = conn.cursor()
        c.execute('''INSERT INTO companies (name, industry, size, contact_person, contact_email)
                     VALUES (?, ?, ?, ?, ?)''',
                  (request.form['name'], request.form['industry'], request.form['size'],
                   request.form['contact_person'], request.form['contact_email']))
        conn.commit()
        conn.close()
        flash('회사가 성공적으로 등록되었습니다.')
        return redirect(url_for('companies'))
    return render_template('company_form.html')

@app.route('/assessment/new/<int:company_id>')
def new_assessment(company_id):
    conn = sqlite3.connect('aps_assessment.db')
    c = conn.cursor()
    
    # 회사 정보
    c.execute("SELECT * FROM companies WHERE id = ?", (company_id,))
    company = c.fetchone()
    
    # 카테고리별 질문
    c.execute('''SELECT c.*, q.* FROM categories c
                 LEFT JOIN questions q ON c.id = q.category_id
                 ORDER BY c.order_num, q.order_num''')
    data = c.fetchall()
    
    # 질문별 선택지
    c.execute('''SELECT qo.question_id, qo.score, qo.description 
                 FROM question_options qo
                 ORDER BY qo.question_id, qo.score''')
    options_data = c.fetchall()
    
    conn.close()
    
    # 데이터 구조화
    categories = {}
    options = {}
    
    for row in data:
        cat_id = row[0]
        if cat_id not in categories:
            categories[cat_id] = {
                'id': row[0], 'name': row[1], 'weight': row[2], 
                'description': row[3], 'questions': []
            }
        if row[5]:  # question exists
            categories[cat_id]['questions'].append({
                'id': row[5], 'code': row[7], 'title': row[8], 'description': row[9]
            })
    
    for option in options_data:
        q_id = option[0]
        if q_id not in options:
            options[q_id] = []
        options[q_id].append({'score': option[1], 'description': option[2]})
    
    return render_template('assessment_form.html', company=company, 
                         categories=categories, options=options)

@app.route('/assessment/submit', methods=['POST'])
def submit_assessment():
    company_id = request.form['company_id']
    assessor_name = request.form['assessor_name']
    notes = request.form.get('notes', '')
    
    # 점수 계산
    total_score = 0
    results = []
    
    for key, value in request.form.items():
        if key.startswith('question_'):
            question_id = int(key.split('_')[1])
            score = int(value)
            total_score += score
            results.append((question_id, score))
    
    maturity_level = calculate_maturity_level(total_score)
    
    # 데이터베이스 저장
    conn = sqlite3.connect('aps_assessment.db')
    c = conn.cursor()
    
    # 평가 기본 정보 저장
    c.execute('''INSERT INTO assessments (company_id, assessor_name, total_score, maturity_level, notes)
                 VALUES (?, ?, ?, ?, ?)''',
              (company_id, assessor_name, total_score, maturity_level, notes))
    
    assessment_id = c.lastrowid
    
    # 상세 결과 저장
    for question_id, score in results:
        c.execute('''INSERT INTO assessment_results (assessment_id, question_id, score)
                     VALUES (?, ?, ?)''', (assessment_id, question_id, score))
    
    conn.commit()
    conn.close()
    
    flash(f'평가가 완료되었습니다. 총점: {total_score}/140, 성숙도 Level: {maturity_level}')
    return redirect(url_for('assessment_detail', assessment_id=assessment_id))

@app.route('/assessment/<int:assessment_id>')
def assessment_detail(assessment_id):
    conn = sqlite3.connect('aps_assessment.db')
    c = conn.cursor()
    
    # 평가 기본 정보
    c.execute('''SELECT a.*, c.name as company_name FROM assessments a
                 JOIN companies c ON a.company_id = c.id
                 WHERE a.id = ?''', (assessment_id,))
    assessment = c.fetchone()
    
    # 카테고리별 점수
    c.execute('''SELECT cat.id, cat.name, cat.weight, SUM(ar.score) as category_score,
                        COUNT(ar.score) * 5 as max_category_score
                 FROM categories cat
                 JOIN questions q ON cat.id = q.category_id
                 JOIN assessment_results ar ON q.id = ar.question_id
                 WHERE ar.assessment_id = ?
                 GROUP BY cat.id, cat.name, cat.weight
                 ORDER BY cat.order_num''', (assessment_id,))
    category_scores = c.fetchall()
    
    # 상세 결과
    c.execute('''SELECT q.code, q.title, ar.score, qo.description
                 FROM assessment_results ar
                 JOIN questions q ON ar.question_id = q.id
                 JOIN question_options qo ON q.id = qo.question_id AND ar.score = qo.score
                 WHERE ar.assessment_id = ?
                 ORDER BY q.category_id, q.order_num''', (assessment_id,))
    detailed_results = c.fetchall()
    
    conn.close()
    
    return render_template('assessment_detail.html', assessment=assessment,
                         category_scores=category_scores, detailed_results=detailed_results)

@app.route('/assessments')
def assessments():
    conn = sqlite3.connect('aps_assessment.db')
    c = conn.cursor()
    c.execute('''SELECT a.id, c.name as company_name, a.assessor_name, 
                        a.assessment_date, a.total_score, a.maturity_level
                 FROM assessments a
                 JOIN companies c ON a.company_id = c.id
                 ORDER BY a.assessment_date DESC''')
    assessments_data = c.fetchall()
    conn.close()
    return render_template('assessments.html', assessments=assessments_data)

@app.route('/api/assessment/<int:assessment_id>/chart')
def assessment_chart_data(assessment_id):
    conn = sqlite3.connect('aps_assessment.db')
    c = conn.cursor()
    
    c.execute('''SELECT cat.name, SUM(ar.score) as score, COUNT(ar.score) * 5 as max_score
                 FROM categories cat
                 JOIN questions q ON cat.id = q.category_id
                 JOIN assessment_results ar ON q.id = ar.question_id
                 WHERE ar.assessment_id = ?
                 GROUP BY cat.id, cat.name
                 ORDER BY cat.order_num''', (assessment_id,))
    
    data = c.fetchall()
    conn.close()
    
    chart_data = {
        'categories': [row[0] for row in data],
        'scores': [row[1] for row in data],
        'maxScores': [row[2] for row in data],
        'percentages': [round((row[1]/row[2])*100, 1) for row in data]
    }
    
    return jsonify(chart_data)

@app.route('/questions')
def questions():
    conn = sqlite3.connect('aps_assessment.db')
    c = conn.cursor()
    c.execute('''SELECT q.id, c.name as category_name, q.code, q.title, q.description
                 FROM questions q
                 JOIN categories c ON q.category_id = c.id
                 ORDER BY c.order_num, q.order_num''')
    questions_data = c.fetchall()
    conn.close()
    return render_template('questions.html', questions=questions_data)

@app.route('/question/<int:question_id>/edit', methods=['GET', 'POST'])
def edit_question(question_id):
    conn = sqlite3.connect('aps_assessment.db')
    c = conn.cursor()
    
    if request.method == 'POST':
        # 문항 정보 업데이트
        c.execute('''UPDATE questions SET code = ?, title = ?, description = ? 
                     WHERE id = ?''',
                  (request.form['code'], request.form['title'], 
                   request.form['description'], question_id))
        
        # 선택지 업데이트
        for score in range(1, 6):
            option_desc = request.form.get(f'option_{score}', '')
            c.execute('''UPDATE question_options SET description = ? 
                         WHERE question_id = ? AND score = ?''',
                      (option_desc, question_id, score))
        
        conn.commit()
        conn.close()
        flash('문항이 성공적으로 수정되었습니다.')
        return redirect(url_for('questions'))
    
    # GET 요청 - 수정 폼 표시
    # 문항 정보 조회
    c.execute('''SELECT q.*, c.name as category_name, c.id as category_id
                 FROM questions q
                 JOIN categories c ON q.category_id = c.id
                 WHERE q.id = ?''', (question_id,))
    question = c.fetchone()
    
    # 카테고리 목록 조회
    c.execute('SELECT id, name FROM categories ORDER BY order_num')
    categories = c.fetchall()
    
    # 선택지 조회
    c.execute('''SELECT score, description FROM question_options 
                 WHERE question_id = ? ORDER BY score''', (question_id,))
    options = c.fetchall()
    
    conn.close()
    
    return render_template('question_edit.html', question=question, 
                         categories=categories, options=options)

@app.route('/question/<int:question_id>/delete', methods=['POST'])
def delete_question(question_id):
    conn = sqlite3.connect('aps_assessment.db')
    c = conn.cursor()
    
    # 선택지 먼저 삭제
    c.execute('DELETE FROM question_options WHERE question_id = ?', (question_id,))
    
    # 평가 결과 삭제 (만약 있다면)
    c.execute('DELETE FROM assessment_results WHERE question_id = ?', (question_id,))
    
    # 문항 삭제
    c.execute('DELETE FROM questions WHERE id = ?', (question_id,))
    
    conn.commit()
    conn.close()
    
    flash('문항이 성공적으로 삭제되었습니다.')
    return redirect(url_for('questions'))

@app.route('/question/new', methods=['GET', 'POST'])
def new_question():
    if request.method == 'POST':
        conn = sqlite3.connect('aps_assessment.db')
        c = conn.cursor()
        
        # 새 문항 추가
        c.execute('''INSERT INTO questions (category_id, code, title, description, max_score, order_num)
                     VALUES (?, ?, ?, ?, 5, 
                     (SELECT COALESCE(MAX(order_num), 0) + 1 FROM questions WHERE category_id = ?))''',
                  (request.form['category_id'], request.form['code'], request.form['title'],
                   request.form['description'], request.form['category_id']))
        
        question_id = c.lastrowid
        
        # 선택지 추가
        for score in range(1, 6):
            option_desc = request.form.get(f'option_{score}', f'Level {score}')
            c.execute('''INSERT INTO question_options (question_id, score, description)
                         VALUES (?, ?, ?)''', (question_id, score, option_desc))
        
        conn.commit()
        conn.close()
        
        flash('새 문항이 성공적으로 추가되었습니다.')
        return redirect(url_for('questions'))
    
    # GET 요청 - 새 문항 폼 표시
    conn = sqlite3.connect('aps_assessment.db')
    c = conn.cursor()
    c.execute('SELECT id, name FROM categories ORDER BY order_num')
    categories = c.fetchall()
    conn.close()
    
    return render_template('question_new.html', categories=categories)

@app.route('/categories')
def categories():
    conn = sqlite3.connect('aps_assessment.db')
    c = conn.cursor()
    c.execute('''SELECT c.*, COUNT(q.id) as question_count
                 FROM categories c
                 LEFT JOIN questions q ON c.id = q.category_id
                 GROUP BY c.id
                 ORDER BY c.order_num''')
    categories_data = c.fetchall()
    conn.close()
    return render_template('categories.html', categories=categories_data)

@app.route('/category/<int:category_id>/edit', methods=['GET', 'POST'])
def edit_category(category_id):
    conn = sqlite3.connect('aps_assessment.db')
    c = conn.cursor()
    
    if request.method == 'POST':
        c.execute('''UPDATE categories SET name = ?, weight = ?, description = ?
                     WHERE id = ?''',
                  (request.form['name'], float(request.form['weight']), 
                   request.form['description'], category_id))
        conn.commit()
        conn.close()
        flash('카테고리가 성공적으로 수정되었습니다.')
        return redirect(url_for('categories'))
    
    # GET 요청
    c.execute('SELECT * FROM categories WHERE id = ?', (category_id,))
    category = c.fetchone()
    conn.close()
    
    return render_template('category_edit.html', category=category)

if __name__ == '__main__':
    print("APS 준비도 진단 시스템을 시작합니다...")
    print("데이터베이스를 초기화합니다...")
    init_db()
    insert_initial_data()
    print("시스템이 준비되었습니다!")
    print("로컬 네트워크에서 접속 가능한 주소:")
    print("- http://localhost:5000")
    print("- http://127.0.0.1:5000")
    
    # 로컬 IP 주소 확인
    import socket
    try:
        # 로컬 IP 주소 가져오기
        hostname = socket.gethostname()
        local_ip = socket.gethostbyname(hostname)
        print(f"- http://{local_ip}:5000")
    except:
        print("- 로컬 IP 주소를 확인할 수 없습니다.")
    
    app.run(debug=True, host='0.0.0.0', port=5000)