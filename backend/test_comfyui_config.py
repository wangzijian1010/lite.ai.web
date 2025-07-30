#!/usr/bin/env python3
"""
测试ComfyUI配置和连接
"""

import os
import sys
import requests
import json
from pathlib import Path

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_comfyui_connection():
    """测试ComfyUI连接"""
    print("🔍 测试ComfyUI连接配置")
    print("=" * 50)
    
    try:
        from app.config import settings
        
        # 显示配置
        print(f"📊 ComfyUI服务器地址: {settings.comfyui_server_address}")
        print(f"🔑 ComfyUI TOKEN: {'已设置' if settings.comfyui_token else '未设置'}")
        print(f"📁 工作流目录: {settings.comfyui_text_to_image_workflow}")
        print(f"⏱️ 超时时间: {settings.comfyui_timeout}秒")
        
        # 测试基本连接
        print(f"\n🔗 测试基本连接...")
        server_address = settings.comfyui_server_address
        
        # 准备认证头
        headers = {}
        if settings.comfyui_token:
            headers['Authorization'] = f'Bearer {settings.comfyui_token}'
        
        # 测试队列端点
        try:
            response = requests.get(f"http://{server_address}/queue", headers=headers, timeout=10)
            if response.status_code == 200:
                print("✅ 队列端点连接成功")
                queue_data = response.json()
                print(f"   运行中任务: {len(queue_data.get('queue_running', []))}")
                print(f"   等待中任务: {len(queue_data.get('queue_pending', []))}")
            else:
                print(f"❌ 队列端点连接失败: HTTP {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ 队列端点连接失败: {e}")
            return False
        
        # 检查工作流文件
        print(f"\n📋 检查工作流文件...")
        
        # 检查吉卜力工作流
        ghibli_workflow_path = Path("workflow/ghibli.json")
        if ghibli_workflow_path.exists():
            print("✅ 吉卜力工作流文件存在")
            try:
                with open(ghibli_workflow_path, 'r', encoding='utf-8') as f:
                    workflow = json.load(f)
                print(f"   节点数量: {len(workflow)}")
                
                # 检查关键节点
                key_nodes = {
                    "192": "LoadImage",
                    "136": "SaveImage", 
                    "197": "LoraLoader",
                    "37": "UNETLoader"
                }
                
                for node_id, node_type in key_nodes.items():
                    if node_id in workflow:
                        print(f"   ✅ 找到{node_type}节点({node_id})")
                    else:
                        print(f"   ⚠️ 缺少{node_type}节点({node_id})")
                        
            except json.JSONDecodeError:
                print("❌ 吉卜力工作流JSON格式错误")
                return False
        else:
            print("❌ 吉卜力工作流文件不存在")
            return False
        
        # 检查其他工作流文件
        other_workflows = [
            ("backend/workflow/text_to_image_workflow.json", "文生图工作流"),
            ("backend/workflow/upscale_workflow.json", "放大工作流")
        ]
        
        for workflow_path, description in other_workflows:
            if Path(workflow_path).exists():
                print(f"✅ {description}文件存在")
            else:
                print(f"⚠️ {description}文件不存在")
        
        # 检查临时目录
        print(f"\n📁 检查临时目录...")
        temp_dir = Path(settings.comfyui_input_dir)
        if not temp_dir.exists():
            temp_dir.mkdir(parents=True, exist_ok=True)
            print(f"✅ 创建临时目录: {temp_dir}")
        else:
            print(f"✅ 临时目录已存在: {temp_dir}")
        
        return True
        
    except Exception as e:
        print(f"❌ 配置测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_image_processing_service():
    """测试图像处理服务"""
    print(f"\n🎨 测试图像处理服务...")
    
    try:
        from app.services.image_processing import image_processing_service
        
        # 获取可用处理器
        processors = image_processing_service.get_available_processors()
        print(f"✅ 图像处理服务加载成功")
        print(f"📋 可用处理器:")
        
        for name, description in processors.items():
            print(f"   - {name}: {description}")
        
        # 检查吉卜力处理器
        if 'ghibli_style' in processors:
            print("✅ 吉卜力风格处理器已注册")
        else:
            print("❌ 吉卜力风格处理器未找到")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ 图像处理服务测试失败: {e}")
        return False

def main():
    """主测试函数"""
    print("🚀 ComfyUI配置测试工具")
    print("=" * 50)
    
    # 测试连接
    connection_ok = test_comfyui_connection()
    
    # 测试服务
    service_ok = test_image_processing_service()
    
    print("\n" + "=" * 50)
    print("📊 测试结果:")
    print(f"   ComfyUI连接: {'✅ 正常' if connection_ok else '❌ 失败'}")
    print(f"   图像处理服务: {'✅ 正常' if service_ok else '❌ 失败'}")
    
    if connection_ok and service_ok:
        print("\n🎉 所有测试通过！ComfyUI配置正常。")
        print("\n📋 Railway部署提醒:")
        print("   请确保在Railway环境变量中设置:")
        print("   - COMFYUI_SERVER_ADDRESS=77.48.24.250:45794")
        print("   - COMFYUI_TOKEN=fd11c05a551f25120bf6d3a15db16147c480547b565ea41b4d23b410a862fdca")
    else:
        print("\n💥 存在配置问题，请检查上述错误信息！")

if __name__ == "__main__":
    main()