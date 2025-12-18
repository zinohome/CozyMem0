"""测试语法错误修复"""
import sys

print("="*60)
print("测试语法错误修复")
print("="*60)

try:
    print("\n1. 测试导入 config...")
    from src.config import settings
    print("   ✅ config 导入成功")
except Exception as e:
    print(f"   ❌ config 导入失败: {e}")
    sys.exit(1)

try:
    print("\n2. 测试导入 clients...")
    from src.clients import CogneeClientWrapper, MemobaseClientWrapper, Mem0ClientWrapper
    print("   ✅ clients 导入成功")
except Exception as e:
    print(f"   ❌ clients 导入失败: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

try:
    print("\n3. 测试导入 services...")
    from src.services import KnowledgeService, ProfileService, MemoryService, ConversationEngine
    print("   ✅ services 导入成功")
except Exception as e:
    print(f"   ❌ services 导入失败: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

try:
    print("\n4. 测试导入 main...")
    from src.main import app
    print("   ✅ main 导入成功")
except Exception as e:
    print(f"   ❌ main 导入失败: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n" + "="*60)
print("✅ 所有模块导入成功！语法错误已修复")
print("="*60)

# 测试 MemobaseClientWrapper 的方法是否存在
print("\n5. 检查 MemobaseClientWrapper 方法...")
try:
    methods = ['get_user_profile', 'extract_and_update_profile', '_serialize_profile', '_serialize_value']
    for method in methods:
        if hasattr(MemobaseClientWrapper, method):
            print(f"   ✅ {method} 存在")
        else:
            print(f"   ❌ {method} 不存在")
except Exception as e:
    print(f"   ❌ 检查方法失败: {e}")

print("\n" + "="*60)
print("测试完成")
print("="*60)
print("\n💡 如果所有测试通过，说明语法错误已修复")
print("   现在可以尝试启动服务：")
print("   ./start_poc.sh")
print("   或")
print("   python3 -m src.main")
