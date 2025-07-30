#!/usr/bin/env python3
"""
测试吉卜力风格转换功能
"""

import os
import sys
from PIL import Image
import io

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def create_test_image():
    """创建一个测试图像"""
    # 创建一个简单的测试图像
    img = Image.new('RGB', (512, 512), color=(100, 150, 200))
    
    # 保存到临时文件
    test_image_path = "test_input.png"
    img.save(test_image_path)
    print(f"✅ 创建测试图像: {test_image_path}")
    return test_image_path

def test_ghibli_processor():
    """测试吉卜力风格处理器"""
    print("🎨 测试吉卜力风格处理器")
    print("=" * 50)
    
    try:
        from app.services.image_processing import image_processing_service
        
        # 创建测试图像
        test_image_path = create_test_image()
        
        # 读取图像数据
        with open(test_image_path, 'rb') as f:
            image_data = f.read()
        
        print("🔄 开始吉卜力风格转换...")
        print("⏳ 这可能需要几分钟时间...")
        
        # 调用处理服务
        try:
            processed_data, processing_time = image_processing_service.process_image(
                image_data=image_data,
                processing_type="ghibli_style",
                parameters=None
            )
            
            # 保存结果
            output_path = "test_ghibli_output.png"
            with open(output_path, 'wb') as f:
                f.write(processed_data)
            
            print(f"✅ 吉卜力风格转换成功!")
            print(f"📁 输出文件: {output_path}")
            print(f"⏱️ 处理时间: {processing_time:.2f}秒")
            
            # 清理临时文件
            if os.path.exists(test_image_path):
                os.remove(test_image_path)
            
            return True
            
        except Exception as e:
            print(f"❌ 吉卜力风格转换失败: {e}")
            
            # 检查是否是降级方案
            if "ComfyUI" in str(e):
                print("🔄 尝试使用降级方案...")
                # 这里会自动使用降级方案
                return False
            else:
                return False
        
    except Exception as e:
        print(f"❌ 处理器测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主测试函数"""
    print("🚀 吉卜力风格转换测试")
    print("=" * 50)
    
    # 测试处理器
    success = test_ghibli_processor()
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 吉卜力风格转换测试成功!")
        print("你的ComfyUI配置工作正常。")
    else:
        print("⚠️ 吉卜力风格转换测试失败")
        print("可能的原因:")
        print("1. ComfyUI服务器连接问题")
        print("2. TOKEN认证问题") 
        print("3. 工作流配置问题")
        print("4. 模型文件缺失")
        print("\n建议检查ComfyUI服务器状态和日志。")

if __name__ == "__main__":
    main()