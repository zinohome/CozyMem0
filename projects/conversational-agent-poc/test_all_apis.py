#!/usr/bin/env python3
"""
API端点完整测试脚本
测试所有外部服务和POC项目的API端点，并生成完整的测试文档
"""
import asyncio
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, List
import httpx

# 配置
COGNEE_API_URL = "http://192.168.66.11:8000"
MEMOBASE_PROJECT_URL = "http://192.168.66.11:8019"
MEM0_API_URL = "http://192.168.66.11:8888"
POC_API_URL = "http://localhost:8080"

DATASET_NAME = "kb_tech"
TEST_USER_ID = "test_user_001"
TEST_SESSION_ID = "test_session_001"

# 输出目录
OUTPUT_DIR = Path("test_results")
OUTPUT_DIR.mkdir(exist_ok=True)

# 测试结果存储
test_results: List[Dict[str, Any]] = []


def print_colored(text: str, color: str = "blue"):
    """简单的彩色输出"""
    colors = {
        "blue": "\033[0;34m",
        "green": "\033[0;32m",
        "red": "\033[0;31m",
        "yellow": "\033[1;33m",
        "cyan": "\033[0;36m",
        "magenta": "\033[0;35m",
        "reset": "\033[0m"
    }
    print(f"{colors.get(color, '')}{text}{colors['reset']}")


def print_panel(content: str, title: str = "", border_color: str = "green"):
    """简单的面板输出"""
    colors = {
        "green": "\033[0;32m",
        "red": "\033[0;31m",
        "reset": "\033[0m"
    }
    color = colors.get(border_color, "")
    reset = colors["reset"]
    if title:
        print(f"{color}=== {title} ==={reset}")
    print(content)
    if title:
        print(f"{color}=========={reset}")


class APITester:
    """API测试类"""
    
    def __init__(self):
        self.client = httpx.AsyncClient(timeout=30.0)
        self.results = []
    
    async def test_endpoint(
        self,
        name: str,
        method: str,
        url: str,
        description: str,
        data: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        测试API端点
        
        Args:
            name: 测试名称
            method: HTTP方法
            url: 请求URL
            description: 测试描述
            data: 请求数据
            headers: 请求头
        
        Returns:
            测试结果字典
        """
        print_colored(f"\n测试: {name}", "blue")
        print(f"  描述: {description}")
        print(f"  方法: {method}")
        print(f"  URL: {url}")
        
        if data:
            print(f"  数据: {json.dumps(data, ensure_ascii=False, indent=2)}")
        
        result = {
            "name": name,
            "description": description,
            "method": method,
            "url": url,
            "request_data": data,
            "timestamp": datetime.now().isoformat(),
            "success": False,
            "status_code": None,
            "response": None,
            "error": None
        }
        
        try:
            # 执行请求
            if method.upper() == "GET":
                response = await self.client.get(url, headers=headers)
            elif method.upper() == "POST":
                response = await self.client.post(url, json=data, headers=headers)
            elif method.upper() == "PUT":
                response = await self.client.put(url, json=data, headers=headers)
            elif method.upper() == "DELETE":
                response = await self.client.delete(url, headers=headers)
            else:
                raise ValueError(f"不支持的HTTP方法: {method}")
            
            result["status_code"] = response.status_code
            
            # 尝试解析JSON响应
            try:
                result["response"] = response.json()
            except:
                result["response"] = response.text
            
            # 判断是否成功
            if 200 <= response.status_code < 300:
                result["success"] = True
                print_colored(f"  ✓ 成功 HTTP {response.status_code}", "green")
                print_panel(
                    json.dumps(result["response"], ensure_ascii=False, indent=2),
                    title="响应",
                    border_color="green"
                )
            else:
                result["success"] = False
                result["error"] = f"HTTP {response.status_code}"
                print_colored(f"  ✗ 失败 HTTP {response.status_code}", "red")
                print_panel(
                    json.dumps(result["response"], ensure_ascii=False, indent=2),
                    title="错误响应",
                    border_color="red"
                )
        
        except httpx.TimeoutException:
            result["success"] = False
            result["error"] = "请求超时"
            print_colored(f"  ✗ 失败 请求超时", "red")
        except httpx.ConnectError:
            result["success"] = False
            result["error"] = "连接失败"
            print_colored(f"  ✗ 失败 连接失败", "red")
        except Exception as e:
            result["success"] = False
            result["error"] = str(e)
            print_colored(f"  ✗ 失败 {str(e)}", "red")
        
        self.results.append(result)
        return result
    
    async def close(self):
        """关闭客户端"""
        await self.client.aclose()


async def test_cognee_apis(tester: APITester):
    """测试Cognee API"""
    print_colored("\n==========================================", "cyan")
    print_colored("1. 测试 Cognee API", "cyan")
    print_colored("==========================================", "cyan")
    
    # 1.1 健康检查
    await tester.test_endpoint(
        name="Cognee Health Check",
        method="GET",
        url=f"{COGNEE_API_URL}/health",
        description="Cognee服务健康检查"
    )
    
    # 1.2 搜索知识
    await tester.test_endpoint(
        name="Cognee Search Knowledge",
        method="POST",
        url=f"{COGNEE_API_URL}/api/v1/search",
        description=f"从Cognee知识库搜索知识（数据集: {DATASET_NAME}）",
        data={
            "query": "Python编程基础",
            "datasets": [DATASET_NAME],
            "search_type": "GRAPH_COMPLETION",
            "top_k": 5
        }
    )
    
    # 1.3 列出数据集
    await tester.test_endpoint(
        name="Cognee List Datasets",
        method="GET",
        url=f"{COGNEE_API_URL}/api/v1/datasets",
        description="列出Cognee中的所有数据集"
    )


async def test_memobase_apis(tester: APITester):
    """测试Memobase API"""
    print_colored("\n==========================================", "cyan")
    print_colored("2. 测试 Memobase API", "cyan")
    print_colored("==========================================", "cyan")
    
    import uuid
    test_uuid = str(uuid.uuid5(uuid.NAMESPACE_DNS, TEST_USER_ID))
    
    # 准备请求头（如果需要API key）
    headers = {}
    try:
        from src.config import settings
        if hasattr(settings, 'memobase_api_key') and settings.memobase_api_key:
            headers["Authorization"] = f"Bearer {settings.memobase_api_key}"
    except:
        pass
    
    # 2.1 健康检查
    await tester.test_endpoint(
        name="Memobase Health Check",
        method="GET",
        url=f"{MEMOBASE_PROJECT_URL}/api/v1/healthcheck",
        description="Memobase服务健康检查"
    )
    
    # 2.2 获取用户（可能不存在）
    await tester.test_endpoint(
        name="Memobase Get User (Before Create)",
        method="GET",
        url=f"{MEMOBASE_PROJECT_URL}/api/v1/users/{test_uuid}",
        description=f"获取用户信息（UUID: {test_uuid}，可能不存在）",
        headers=headers if headers else None
    )
    
    # 2.3 创建用户
    await tester.test_endpoint(
        name="Memobase Create User",
        method="POST",
        url=f"{MEMOBASE_PROJECT_URL}/api/v1/users",
        description=f"创建新用户（UUID: {test_uuid}）",
        data={"id": test_uuid, "data": {}},
        headers=headers if headers else None
    )
    
    # 2.4 再次获取用户（验证创建）
    await tester.test_endpoint(
        name="Memobase Get User (After Create)",
        method="GET",
        url=f"{MEMOBASE_PROJECT_URL}/api/v1/users/{test_uuid}",
        description="获取用户信息（验证创建是否成功）",
        headers=headers if headers else None
    )
    
    # 2.5 再次获取用户信息（查看完整信息）
    await tester.test_endpoint(
        name="Memobase Get User (Final)",
        method="GET",
        url=f"{MEMOBASE_PROJECT_URL}/api/v1/users/{test_uuid}",
        description="获取用户信息（最终状态）",
        headers=headers if headers else None
    )
    
    # 注意：Memobase的其他功能（如profile、blobs、flush）主要通过Python SDK使用
    # 这些功能在POC项目中通过SDK正常使用，但REST API端点可能不直接暴露
    print_colored("\n注意: Memobase的用户画像、对话数据插入等功能主要通过Python SDK使用", "yellow")
    print_colored("这些功能在POC项目中通过SDK正常使用，但REST API端点可能不直接暴露", "yellow")


async def test_mem0_apis(tester: APITester):
    """测试Mem0 API"""
    print_colored("\n==========================================", "cyan")
    print_colored("3. 测试 Mem0 API", "cyan")
    print_colored("==========================================", "cyan")
    
    # 3.1 健康检查
    await tester.test_endpoint(
        name="Mem0 Health Check",
        method="GET",
        url=f"{MEM0_API_URL}/health",
        description="Mem0服务健康检查"
    )
    
    # 3.2 搜索记忆（当前会话）
    await tester.test_endpoint(
        name="Mem0 Search Memories (Current Session)",
        method="POST",
        url=f"{MEM0_API_URL}/api/v1/search",
        description="搜索当前会话的记忆",
        data={
            "query": "用户信息",
            "user_id": TEST_USER_ID,
            "agent_id": TEST_SESSION_ID
        }
    )
    
    # 3.3 搜索记忆（跨会话）
    await tester.test_endpoint(
        name="Mem0 Search Memories (Cross Session)",
        method="POST",
        url=f"{MEM0_API_URL}/api/v1/search",
        description="搜索跨会话的记忆",
        data={
            "query": "用户信息",
            "user_id": TEST_USER_ID
        }
    )
    
    # 3.4 创建记忆
    await tester.test_endpoint(
        name="Mem0 Create Memory",
        method="POST",
        url=f"{MEM0_API_URL}/api/v1/memories",
        description="创建新的记忆",
        data={
            "messages": [
                {"role": "user", "content": "我是测试用户，喜欢Python编程"},
                {"role": "assistant", "content": "好的，我记住了"}
            ],
            "user_id": TEST_USER_ID,
            "agent_id": TEST_SESSION_ID
        }
    )
    
    # 3.5 再次搜索记忆（验证创建是否成功）
    await tester.test_endpoint(
        name="Mem0 Search Memories (After Create)",
        method="POST",
        url=f"{MEM0_API_URL}/api/v1/search",
        description="创建记忆后再次搜索，验证记忆是否保存成功",
        data={
            "query": "Python编程",
            "user_id": TEST_USER_ID,
            "agent_id": TEST_SESSION_ID
        }
    )


async def test_poc_apis(tester: APITester):
    """测试POC项目API"""
    print_colored("\n==========================================", "cyan")
    print_colored("4. 测试 POC 项目 API", "cyan")
    print_colored("==========================================", "cyan")
    
    # 4.1 根路径
    await tester.test_endpoint(
        name="POC Root",
        method="GET",
        url=f"{POC_API_URL}/",
        description="POC项目根路径"
    )
    
    # 4.2 健康检查
    await tester.test_endpoint(
        name="POC Health Check",
        method="GET",
        url=f"{POC_API_URL}/health",
        description="POC服务健康检查"
    )
    
    # 4.3 调试状态
    await tester.test_endpoint(
        name="POC Debug Status",
        method="GET",
        url=f"{POC_API_URL}/api/v1/debug/status",
        description="查看POC服务状态和配置"
    )
    
    # 4.4 第一次对话（创建用户画像和记忆）
    await tester.test_endpoint(
        name="POC First Conversation",
        method="POST",
        url=f"{POC_API_URL}/api/v1/test/conversation",
        description="第一次对话，创建用户画像和记忆",
        data={
            "user_id": TEST_USER_ID,
            "session_id": TEST_SESSION_ID,
            "message": "你好，我是测试用户，我是一名软件工程师，对Python很感兴趣",
            "dataset_names": [DATASET_NAME]
        }
    )
    
    # 等待一下，确保异步保存完成
    await asyncio.sleep(2)
    
    # 4.5 获取用户画像
    await tester.test_endpoint(
        name="POC Get User Profile",
        method="GET",
        url=f"{POC_API_URL}/api/v1/users/{TEST_USER_ID}/profile",
        description="获取用户画像"
    )
    
    # 4.6 第二次对话（测试记忆功能）
    await tester.test_endpoint(
        name="POC Second Conversation (Memory Test)",
        method="POST",
        url=f"{POC_API_URL}/api/v1/test/conversation",
        description="第二次对话，测试记忆功能",
        data={
            "user_id": TEST_USER_ID,
            "session_id": TEST_SESSION_ID,
            "message": "我之前说过我的职业是什么？",
            "dataset_names": [DATASET_NAME]
        }
    )
    
    # 4.7 新会话（跨会话记忆测试）
    await tester.test_endpoint(
        name="POC New Session (Cross-Session Memory)",
        method="POST",
        url=f"{POC_API_URL}/api/v1/test/conversation",
        description="新会话，测试跨会话记忆",
        data={
            "user_id": TEST_USER_ID,
            "session_id": "test_session_002",
            "message": "你还记得我的职业吗？",
            "dataset_names": [DATASET_NAME]
        }
    )
    
    # 4.8 发送消息（标准接口）
    await tester.test_endpoint(
        name="POC Send Message (Standard API)",
        method="POST",
        url=f"{POC_API_URL}/api/v1/conversations/{TEST_SESSION_ID}/messages",
        description="发送消息并获取响应（标准接口）",
        data={
            "message": "Python有哪些常用的数据结构？",
            "user_id": TEST_USER_ID,
            "session_id": TEST_SESSION_ID,
            "dataset_names": [DATASET_NAME]
        }
    )


def generate_report(tester: APITester):
    """生成测试报告"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # 保存JSON结果
    json_file = OUTPUT_DIR / f"api_test_results_{timestamp}.json"
    with open(json_file, "w", encoding="utf-8") as f:
        json.dump({
            "test_time": datetime.now().isoformat(),
            "total_tests": len(tester.results),
            "success_count": sum(1 for r in tester.results if r["success"]),
            "failure_count": sum(1 for r in tester.results if not r["success"]),
            "results": tester.results
        }, f, ensure_ascii=False, indent=2)
    
    # 生成Markdown报告
    md_file = OUTPUT_DIR / f"api_test_report_{timestamp}.md"
    with open(md_file, "w", encoding="utf-8") as f:
        f.write("# API端点测试报告\n\n")
        f.write(f"**测试时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write(f"**总测试数**: {len(tester.results)}\n\n")
        f.write(f"**成功**: {sum(1 for r in tester.results if r['success'])}\n\n")
        f.write(f"**失败**: {sum(1 for r in tester.results if not r['success'])}\n\n")
        f.write("---\n\n")
        
        # 按服务分组
        services = {
            "Cognee": [],
            "Memobase": [],
            "Mem0": [],
            "POC": []
        }
        
        for result in tester.results:
            name = result["name"]
            if name.startswith("Cognee"):
                services["Cognee"].append(result)
            elif name.startswith("Memobase"):
                services["Memobase"].append(result)
            elif name.startswith("Mem0"):
                services["Mem0"].append(result)
            else:
                services["POC"].append(result)
        
        for service_name, results in services.items():
            if not results:
                continue
            
            f.write(f"## {service_name} API\n\n")
            
            for result in results:
                status = "✅ 成功" if result["success"] else "❌ 失败"
                f.write(f"### {result['name']} {status}\n\n")
                f.write(f"**描述**: {result['description']}\n\n")
                f.write(f"**方法**: {result['method']}\n\n")
                f.write(f"**URL**: `{result['url']}`\n\n")
                
                if result.get("request_data"):
                    f.write("**请求数据**:\n\n")
                    f.write("```json\n")
                    f.write(json.dumps(result["request_data"], ensure_ascii=False, indent=2))
                    f.write("\n```\n\n")
                
                f.write(f"**HTTP状态码**: {result.get('status_code', 'N/A')}\n\n")
                
                if result.get("error"):
                    f.write(f"**错误**: {result['error']}\n\n")
                
                if result.get("response"):
                    f.write("**响应**:\n\n")
                    f.write("```json\n")
                    if isinstance(result["response"], dict):
                        f.write(json.dumps(result["response"], ensure_ascii=False, indent=2))
                    else:
                        f.write(str(result["response"]))
                    f.write("\n```\n\n")
                
                f.write("---\n\n")
    
    print_colored(f"\n测试报告已生成:", "green")
    print(f"  JSON: {json_file}")
    print(f"  Markdown: {md_file}")


async def main():
    """主函数"""
    print_colored("==========================================", "cyan")
    print_colored("API端点完整测试", "cyan")
    print_colored(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", "cyan")
    print_colored("==========================================", "cyan")
    
    tester = APITester()
    
    try:
        # 测试所有API
        await test_cognee_apis(tester)
        await test_memobase_apis(tester)
        await test_mem0_apis(tester)
        await test_poc_apis(tester)
        
        # 生成报告
        generate_report(tester)
        
        # 显示总结
        print_colored("\n==========================================", "cyan")
        print_colored("测试完成", "cyan")
        print_colored("==========================================", "cyan")
        
        total = len(tester.results)
        success = sum(1 for r in tester.results if r["success"])
        failure = total - success
        
        print("\n测试总结:")
        print(f"  总测试数: {total}")
        print_colored(f"  成功: {success}", "green")
        print_colored(f"  失败: {failure}", "red")
        print(f"  成功率: {success/total*100:.1f}%")
        
    finally:
        await tester.close()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print_colored("\n测试被用户中断", "yellow")
        sys.exit(1)
    except Exception as e:
        print_colored(f"\n测试出错: {e}", "red")
        import traceback
        traceback.print_exc()
        sys.exit(1)
