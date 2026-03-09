"""修复数据库中 OCAP 步骤的错误数据"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import SessionLocal
from sqlalchemy import text

db = SessionLocal()
try:
    # 修复 phase 字段
    result1 = db.execute(text("UPDATE ocap_step SET phase = 'correction' WHERE phase = 'corrective'"))
    print(f"修复 phase 字段: {result1.rowcount} 行受影响")
    
    # 修复 action_type 字段
    result2 = db.execute(text("UPDATE ocap_step SET action_type = 'short_term' WHERE action_type = 'planned'"))
    print(f"修复 action_type 字段: {result2.rowcount} 行受影响")
    
    # 对于 containment 阶段的步骤，设置为 immediate
    result3 = db.execute(text("UPDATE ocap_step SET action_type = 'immediate' WHERE phase = 'containment'"))
    print(f"修复 containment 阶段的 action_type: {result3.rowcount} 行受影响")
    
    db.commit()
    print("数据库修复完成!")
    
    # 验证修复结果
    steps = db.execute(text("SELECT DISTINCT phase FROM ocap_step"))
    phases = [row[0] for row in steps]
    print(f"当前 phase 值: {phases}")
    
    steps2 = db.execute(text("SELECT DISTINCT action_type FROM ocap_step"))
    action_types = [row[0] for row in steps2]
    print(f"当前 action_type 值: {action_types}")
    
except Exception as e:
    print(f"错误: {e}")
    db.rollback()
finally:
    db.close()
