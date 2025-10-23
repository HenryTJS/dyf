#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sqlite3

def test_new_limits():
    """测试新的类别限制设置"""
    try:
        conn = sqlite3.connect('instance/moral_score.db')
        cursor = conn.cursor()
        
        print("=== 新的德育分类别限制设置 ===\n")
        
        # 查询所有主类别
        cursor.execute("""
            SELECT id, name, description, max_score 
            FROM score_category 
            WHERE parent_id IS NULL 
            ORDER BY name
        """)
        main_categories = cursor.fetchall()
        
        print("主类别最高分限制:")
        for cat_id, name, description, max_score in main_categories:
            print(f"  {name}: {max_score}分 - {description}")
        
        print("\n" + "="*50 + "\n")
        
        # 查询工时子类别
        cursor.execute("""
            SELECT sc.name, sc.max_score, parent.name as parent_name
            FROM score_category sc
            LEFT JOIN score_category parent ON sc.parent_id = parent.id
            WHERE sc.name = '工时'
        """)
        work_hours = cursor.fetchone()
        
        if work_hours:
            print(f"特殊限制 - 工时: {work_hours[1]}分 (父类别: {work_hours[2]})")
        
        print("\n" + "="*50 + "\n")
        
        print("新的计算规则:")
        print("1. 思想政治理论分: 大类最高3分，小类不限")
        print("2. 社会服务分: 大类最高4分，工时最高1分，其它不限")
        print("3. 集体活动分: 大类最高3分，小类不限")
        print("4. 学术科研分: 大类最高10分，小类不限")
        print("5. 文体竞赛分: 大类最高6分，小类不限")
        print("6. 任职分: 大类最高4分，小类不限，只能取最高1项（不能叠加）")
        print("7. 奖励分: 大类最高5分，小类不限")
        print("8. 扣分: 无下限，但总分不能低于0分")
        print("9. 德育分满分35分，最终统计时最高不超过100分")
        
        conn.close()
        
    except Exception as e:
        print(f"测试失败: {e}")

if __name__ == "__main__":
    test_new_limits()

