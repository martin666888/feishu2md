#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""创建多尺寸 ICO 图标文件"""

from PIL import Image
import os

def create_multi_size_ico():
    """将多个单尺寸 ICO 文件合并为一个多尺寸 ICO 文件"""
    
    # 定义输入文件和对应尺寸
    ico_files = {
        'img/16x16.ico': (16, 16),
        'img/32x32.ico': (32, 32),
        'img/48x48.ico': (48, 48),
        'img/256x256.ico': (256, 256)
    }
    
    # 检查文件是否存在
    missing_files = []
    for file_path in ico_files.keys():
        if not os.path.exists(file_path):
            missing_files.append(file_path)
    
    if missing_files:
        print("❌ 缺少以下文件:")
        for file in missing_files:
            print(f"   - {file}")
        return False
    
    print("📁 找到所有 ICO 文件，开始合并...")
    
    # 加载所有图像
    images = []
    sizes = []
    
    for file_path, size in ico_files.items():
        try:
            img = Image.open(file_path)
            # 确保图像尺寸正确
            if img.size != size:
                print(f"⚠️  调整 {file_path} 尺寸: {img.size} -> {size}")
                img = img.resize(size, Image.Resampling.LANCZOS)
            
            images.append(img)
            sizes.append(size)
            print(f"✅ 加载: {file_path} ({size[0]}x{size[1]})")
            
        except Exception as e:
            print(f"❌ 无法加载 {file_path}: {e}")
            return False
    
    # 保存为多尺寸 ICO 文件
    output_path = 'icon.ico'
    try:
        images[0].save(
            output_path,
            format='ICO',
            sizes=sizes
        )
        print(f"\n🎉 成功创建多尺寸 ICO 文件: {output_path}")
        
        # 显示文件信息
        file_size = os.path.getsize(output_path)
        print(f"📊 文件大小: {file_size:,} 字节 ({file_size/1024:.1f} KB)")
        print(f"📐 包含尺寸: {', '.join([f'{s[0]}x{s[1]}' for s in sizes])}")
        
        return True
        
    except Exception as e:
        print(f"❌ 创建 ICO 文件失败: {e}")
        return False

def main():
    """主函数"""
    print("🔧 飞书文档转Markdown - ICO 图标创建工具")
    print("=" * 50)
    
    success = create_multi_size_ico()
    
    if success:
        print("\n✨ 现在你可以使用以下命令打包程序:")
        print("pyinstaller --onefile --windowed --icon=icon.ico --name=\"飞书文档转Markdown\" main.py")
    else:
        print("\n❌ 图标创建失败，请检查错误信息")
    
    print("\n" + "=" * 50)

if __name__ == '__main__':
    main()