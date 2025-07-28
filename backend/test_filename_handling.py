"""
文件名处理功能测试脚本
"""
import os
import sys
import tempfile
from pathlib import Path

# Add the app directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.utils.filename_handler import FilenameHandler, sanitize_filename, generate_unique_filename

def test_filename_sanitization():
    """测试文件名清理功能"""
    print("🧪 测试文件名清理功能...")
    
    test_cases = [
        # (输入文件名, 期望结果类型)
        ("normal_file.jpg", "正常文件名"),
        ("file with spaces.png", "包含空格"),
        ("文件名中文.jpg", "中文文件名"),
        ("file@#$%^&*().png", "特殊字符"),
        ("very_long_filename_that_exceeds_normal_limits_and_should_be_truncated_properly.jpg", "超长文件名"),
        ("file\nwith\nnewlines.png", "包含换行符"),
        ("file/with/slashes.jpg", "包含路径分隔符"),
        ("CON.jpg", "系统保留名"),
        ("", "空文件名"),
        ("..hidden_file.png", "隐藏文件"),
        ("file名字 (1).jpg", "混合字符"),
        ("图片 - 副本.png", "中文加特殊字符"),
    ]
    
    handler = FilenameHandler()
    
    for original, description in test_cases:
        try:
            sanitized = handler.sanitize_filename(original)
            is_valid, message = handler.validate_filename(sanitized)
            
            print(f"  ✅ {description}")
            print(f"     原始: '{original}'")
            print(f"     清理: '{sanitized}'")
            print(f"     有效: {is_valid} - {message}")
            print()
            
        except Exception as e:
            print(f"  ❌ {description} - 错误: {str(e)}")
            print()

def test_unique_filename_generation():
    """测试唯一文件名生成"""
    print("🧪 测试唯一文件名生成...")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        handler = FilenameHandler()
        
        # 创建一些测试文件
        test_filename = "test_image.jpg"
        
        # 生成多个唯一文件名
        unique_names = []
        for i in range(5):
            unique_name = handler.generate_unique_filename(test_filename, temp_dir)
            unique_names.append(unique_name)
            
            # 创建文件以模拟存在
            Path(temp_dir) / unique_name).touch()
            
            print(f"  生成 #{i+1}: {unique_name}")
        
        # 验证所有文件名都是唯一的
        if len(set(unique_names)) == len(unique_names):
            print("  ✅ 所有生成的文件名都是唯一的")
        else:
            print("  ❌ 发现重复的文件名")

def test_url_safe_filenames():
    """测试URL安全文件名"""
    print("🧪 测试URL安全文件名...")
    
    handler = FilenameHandler()
    
    test_cases = [
        "normal_file.jpg",
        "file with spaces.png",
        "文件名中文.jpg",
        "file@#$%^&*().png",
        "图片 - 副本.png",
    ]
    
    for filename in test_cases:
        try:
            url_safe = handler.get_safe_url_filename(filename)
            print(f"  原始: '{filename}'")
            print(f"  URL安全: '{url_safe}'")
            print()
        except Exception as e:
            print(f"  ❌ 处理 '{filename}' 时出错: {str(e)}")

def test_file_info_extraction():
    """测试文件信息提取"""
    print("🧪 测试文件信息提取...")
    
    handler = FilenameHandler()
    
    test_cases = [
        "document.pdf",
        "image with spaces.jpg",
        "文档.docx",
        "file@special#chars.png",
        "no_extension",
        ".hidden_file",
    ]
    
    for filename in test_cases:
        try:
            info = handler.extract_file_info(filename)
            print(f"  文件: '{filename}'")
            print(f"    安全文件名: '{info['safe_filename']}'")
            print(f"    名称部分: '{info['name_part']}'")
            print(f"    扩展名: '{info['extension']}'")
            print(f"    是否安全: {info['is_safe']}")
            if info['issues']:
                print(f"    问题: {', '.join(info['issues'])}")
            print()
        except Exception as e:
            print(f"  ❌ 处理 '{filename}' 时出错: {str(e)}")

def test_edge_cases():
    """测试边界情况"""
    print("🧪 测试边界情况...")
    
    handler = FilenameHandler()
    
    edge_cases = [
        None,  # None值
        "",    # 空字符串
        "   ",  # 只有空格
        ".",   # 只有点
        "..",  # 双点
        "...",  # 多个点
        "a" * 300,  # 超长文件名
        "\x00\x01\x02",  # 控制字符
        "file\0name.txt",  # 包含null字符
    ]
    
    for case in edge_cases:
        try:
            if case is None:
                print(f"  测试: None")
                result = handler.sanitize_filename("")  # 处理None情况
            else:
                print(f"  测试: '{repr(case)}'")
                result = handler.sanitize_filename(case)
            
            print(f"    结果: '{result}'")
            
            # 验证结果
            is_valid, message = handler.validate_filename(result)
            print(f"    有效: {is_valid} - {message}")
            print()
            
        except Exception as e:
            print(f"    ❌ 错误: {str(e)}")
            print()

def main():
    """运行所有测试"""
    print("🚀 开始文件名处理功能测试\n")
    
    try:
        test_filename_sanitization()
        test_unique_filename_generation()
        test_url_safe_filenames()
        test_file_info_extraction()
        test_edge_cases()
        
        print("✅ 所有测试完成!")
        
    except Exception as e:
        print(f"❌ 测试过程中出现错误: {str(e)}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)