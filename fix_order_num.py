#!/usr/bin/env python3
"""
평가 문항의 order_num을 올바르게 수정하는 스크립트
"""
import sqlite3

def fix_question_order():
    conn = sqlite3.connect('aps_assessment.db')
    c = conn.cursor()
    
    print("현재 문항 순서 확인...")
    c.execute('''SELECT q.id, c.name, q.code, q.title, q.order_num 
                 FROM questions q 
                 JOIN categories c ON q.category_id = c.id 
                 ORDER BY c.order_num, q.code''')
    
    questions = c.fetchall()
    
    # 카테고리별로 문항을 그룹화하고 코드 순서로 정렬
    category_questions = {}
    for q in questions:
        cat_name = q[1]
        if cat_name not in category_questions:
            category_questions[cat_name] = []
        category_questions[cat_name].append(q)
    
    print("\n문항 순서를 수정합니다...")
    
    # 각 카테고리별로 순서를 1부터 다시 매기기
    for cat_name, cat_questions in category_questions.items():
        # 코드 순서로 정렬 (1.1.1, 1.1.2, 1.2.1, ...)
        cat_questions.sort(key=lambda x: x[2])  # code 기준 정렬
        
        for order, question in enumerate(cat_questions, 1):
            question_id = question[0]
            current_order = question[4]
            
            if current_order != order:
                c.execute('UPDATE questions SET order_num = ? WHERE id = ?', (order, question_id))
                print(f"문항 ID {question_id} ({question[2]}): order_num {current_order} → {order}")
    
    # 변경사항 커밋
    conn.commit()
    
    print("\n수정 완료! 현재 순서 확인:")
    c.execute('''SELECT q.id, c.name, q.code, q.title, q.order_num 
                 FROM questions q 
                 JOIN categories c ON q.category_id = c.id 
                 ORDER BY c.order_num, q.order_num''')
    
    for row in c.fetchall():
        print(f"ID: {row[0]}, Category: {row[1]}, Code: {row[2]}, Order: {row[4]}")
    
    conn.close()
    print("\n문항 순서 수정이 완료되었습니다!")

if __name__ == '__main__':
    fix_question_order()