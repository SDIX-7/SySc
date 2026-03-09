"""修复数据库中 OCAP signal_type 的错误数据"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import SessionLocal
from sqlalchemy import text

db = SessionLocal()
try:
    # 修复 ocap 表的 signal_type 字段
    result = db.execute(text("UPDATE ocap SET signal_type = 'point_beyond_3sigma' WHERE signal_type = 'point_beyond_limits'"))
    print(f"修复 ocap.signal_type: {result.rowcount} 行受影响")
    
    # 修复 ocap_signal 表的 signal_type 字段
    result2 = db.execute(text("UPDATE ocap_signal SET signal_type = 'point_beyond_3sigma' WHERE signal_type = 'point_beyond_limits'"))
    print(f"修复 ocap_signal.signal_type: {result2.rowcount} 行受影响")
    
    # 修复 trend 类型
    result3 = db.execute(text("UPDATE ocap SET signal_type = 'trend_6' WHERE signal_type = 'trend'"))
    print(f"修复 ocap.signal_type (trend): {result3.rowcount} 行受影响")
    
    result4 = db.execute(text("UPDATE ocap_signal SET signal_type = 'trend_6' WHERE signal_type = 'trend'"))
    print(f"修复 ocap_signal.signal_type (trend): {result4.rowcount} 行受影响")
    
    db.commit()
    print("数据库修复完成!")
    
    # 验证
    signals = db.execute(text("SELECT DISTINCT signal_type FROM ocap"))
    types = [row[0] for row in signals]
    print(f"当前 ocap.signal_type 值: {types}")
    
    signals2 = db.execute(text("SELECT DISTINCT signal_type FROM ocap_signal"))
    types2 = [row[0] for row in signals2]
    print(f"当前 ocap_signal.signal_type 值: {types2}")
    
except Exception as e:
    print(f"错误: {e}")
    db.rollback()
finally:
    db.close()
