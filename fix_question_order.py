#!/usr/bin/env python3
"""
문항의 order_num을 문항 코드 기준으로 올바르게 재설정하는 스크립트
"""
import sqlite3
import re

def fix_question_ordering():
    """문항 코드를 기준으로 order_num을 올바르게 설정"""
    
    conn = sqlite3.connect('aps_assessment.db')
    cursor = conn.cursor()
    
    try:
        print("문항 순서 재정렬을 시작합니다...")
        
        # 모든 문항을 카테고리별로 조회
        cursor.execute('''
            SELECT q.id, q.code, q.category_id, c.order_num as cat_order
            FROM questions q
            JOIN categories c ON q.category_id = c.id
            ORDER BY c.order_num, q.code
        ''')
        
        questions = cursor.fetchall()
        
        # 카테고리별로 order_num 재설정
        current_category = None
        category_order = 0
        
        for q_id, q_code, category_id, cat_order in questions:
            if category_id != current_category:
                current_category = category_id
                category_order = 1
            
            print(f"문항 {q_code} (ID: {q_id}) -> order_num: {category_order}")
            
            # order_num 업데이트
            cursor.execute('''
                UPDATE questions 
                SET order_num = ?
                WHERE id = ?
            ''', (category_order, q_id))
            
            category_order += 1
        
        conn.commit()
        print("문항 순서 재정렬이 완료되었습니다!")
        
        # 결과 확인
        print("\n=== 재정렬 결과 ===")
        cursor.execute('''
            SELECT q.id, q.code, q.title, q.order_num, c.name as category_name
            FROM questions q 
            JOIN categories c ON q.category_id = c.id 
            ORDER BY c.order_num, q.order_num
        ''')
        
        questions = cursor.fetchall()
        for q in questions[:10]:  # 처음 10개만 표시
            print(f'{q[1]:6s} | order_num:{q[3]:2d} | {q[4]} | {q[2]}')
        
        print(f"... (총 {len(questions)}개 문항)")
        
    except Exception as e:
        print(f"오류 발생: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    fix_question_ordering()