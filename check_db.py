# check_db.py - 데이터베이스 상태 확인 스크립트
import sqlite3
import os

def check_database():
    db_file = '/app/data/aps_assessment.db'
    
    # 데이터베이스 파일 존재 확인
    if not os.path.exists(db_file):
        print(f"❌ 데이터베이스 파일 '{db_file}'이 존재하지 않습니다.")
        return False
    
    try:
        conn = sqlite3.connect(db_file)
        c = conn.cursor()
        
        print(f"✅ 데이터베이스 파일 '{db_file}'이 존재합니다.")
        print("\n=== 테이블 확인 ===")
        
        # 모든 테이블 목록 가져오기
        c.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = c.fetchall()
        
        if not tables:
            print("❌ 테이블이 없습니다.")
            conn.close()
            return False
        
        # 각 테이블의 데이터 개수 확인
        table_info = {
            'categories': '평가 영역',
            'questions': '평가 문항',
            'question_options': '문항 선택지',
            'companies': '회사 정보',
            'assessments': '평가 이력',
            'assessment_results': '평가 상세 결과'
        }
        
        for table_name in table_info.keys():
            try:
                c.execute(f"SELECT COUNT(*) FROM {table_name}")
                count = c.fetchone()[0]
                print(f"✅ {table_name}: {count}개 ({table_info[table_name]})")
            except sqlite3.OperationalError:
                print(f"❌ {table_name}: 테이블이 존재하지 않습니다.")
        
        print("\n=== 초기 데이터 확인 ===")
        
        # 카테고리 데이터 확인
        c.execute("SELECT name FROM categories ORDER BY order_num")
        categories = c.fetchall()
        if categories:
            print("카테고리:")
            for i, cat in enumerate(categories, 1):
                print(f"  {i}. {cat[0]}")
        else:
            print("❌ 카테고리 데이터가 없습니다.")
        
        # 문항 수 확인
        c.execute("SELECT COUNT(*) FROM questions")
        question_count = c.fetchone()[0]
        print(f"\n총 평가 문항: {question_count}개")
        
        if question_count != 28:
            print(f"⚠️  예상 문항 수(28개)와 다릅니다.")
        
        conn.close()
        
        if question_count == 28 and len(categories) == 4:
            print("\n🎉 데이터베이스가 정상적으로 설정되었습니다!")
            return True
        else:
            print("\n⚠️  데이터베이스에 문제가 있을 수 있습니다.")
            return False
            
    except Exception as e:
        print(f"❌ 데이터베이스 확인 중 오류 발생: {e}")
        return False

def reset_database():
    """데이터베이스를 완전히 재설정합니다."""
    db_file = '/app/data/aps_assessment.db'
    
    if os.path.exists(db_file):
        os.remove(db_file)
        print(f"기존 데이터베이스 파일 '{db_file}'을 삭제했습니다.")
    
    # app.py에서 초기화 함수들을 임포트해서 실행
    try:
        from app import init_db, insert_initial_data
        print("데이터베이스를 다시 초기화합니다...")
        init_db()
        insert_initial_data()
        print("데이터베이스 재설정이 완료되었습니다!")
    except ImportError as e:
        print(f"❌ app.py를 찾을 수 없습니다: {e}")
    except Exception as e:
        print(f"❌ 데이터베이스 재설정 중 오류: {e}")

def show_sample_data():
    """샘플 데이터를 표시합니다."""
    try:
        conn = sqlite3.connect('aps_assessment.db')
        c = conn.cursor()
        
        print("\n=== 샘플 문항 확인 ===")
        c.execute('''SELECT q.code, q.title, c.name as category_name
                     FROM questions q 
                     JOIN categories c ON q.category_id = c.id 
                     ORDER BY c.order_num, q.order_num 
                     LIMIT 10''')
        
        questions = c.fetchall()
        for q in questions:
            print(f"{q[0]} - {q[1]} ({q[2]})")
        
        if len(questions) == 10:
            print("... (나머지 18개 문항)")
        
        print("\n=== 샘플 선택지 확인 ===")
        c.execute('''SELECT qo.score, qo.description 
                     FROM question_options qo 
                     WHERE qo.question_id = 1 
                     ORDER BY qo.score''')
        
        options = c.fetchall()
        print("1.1.1 생산계획 수립 주기 - 선택지:")
        for opt in options:
            print(f"  {opt[0]}점: {opt[1]}")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ 샘플 데이터 조회 중 오류: {e}")

if __name__ == '__main__':
    print("=== APS 진단 시스템 데이터베이스 확인 도구 ===\n")
    
    # 데이터베이스 상태 확인
    is_ok = check_database()
    
    if not is_ok:
        print("\n데이터베이스에 문제가 있습니다.")
        choice = input("\n데이터베이스를 재설정하시겠습니까? (y/N): ")
        if choice.lower() == 'y':
            reset_database()
            print("\n재설정 후 상태:")
            check_database()
    else:
        choice = input("\n샘플 데이터를 확인하시겠습니까? (y/N): ")
        if choice.lower() == 'y':
            show_sample_data()
    
    print("\n확인 완료!")