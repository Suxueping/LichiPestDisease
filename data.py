import os
import shutil
from PIL import Image, ImageEnhance

# 增强类型配置（添加英文别名）
ENHANCE_CONFIG = {
    '顺光': {
        'brightness': 1.4,
        'contrast': 1.0,
        'alias': 'shun_guang'
    },
    '逆光': {
        'brightness': 0.6,
        'contrast': 1.2,
        'alias': 'ni_guang'
    },
    '侧光': {
        'brightness': 1.2,
        'contrast': 1.3,
        'alias': 'side_light'
    }
}

def apply_enhancement(image, enhance_type):
    """应用指定的增强操作"""
    if enhance_type == '顺光':
        return ImageEnhance.Brightness(image).enhance(ENHANCE_CONFIG['顺光']['brightness'])
    elif enhance_type == '逆光':
        img = ImageEnhance.Brightness(image).enhance(ENHANCE_CONFIG['逆光']['brightness'])
        return ImageEnhance.Contrast(img).enhance(ENHANCE_CONFIG['逆光']['contrast'])
    elif enhance_type == '侧光':
        img = ImageEnhance.Brightness(image).enhance(ENHANCE_CONFIG['侧光']['brightness'])
        return ImageEnhance.Contrast(img).enhance(ENHANCE_CONFIG['侧光']['contrast'])
    return image

def process_dataset(image_dir, label_dir, output_root):
    """处理数据集并生成分类型目录结构"""
    # 为每个增强类型创建输出目录
    for enhance_type in ENHANCE_CONFIG.keys():
        alias = ENHANCE_CONFIG[enhance_type]['alias']
        img_type_dir = os.path.join(output_root, f'images_{alias}')
        label_type_dir = os.path.join(output_root, f'labels_{alias}')
        os.makedirs(img_type_dir, exist_ok=True)
        os.makedirs(label_type_dir, exist_ok=True)

    # 遍历原始图片
    for img_file in os.listdir(image_dir):
        if not img_file.lower().endswith(('.png', '.jpg', '.jpeg')):
            continue

        base_name = os.path.splitext(img_file)[0]
        ext = os.path.splitext(img_file)[1]

        # 原始文件路径
        img_path = os.path.join(image_dir, img_file)
        label_path = os.path.join(label_dir, f"{base_name}.txt")

        if not os.path.exists(label_path):
            print(f"跳过无标注文件: {img_file}")
            continue

        try:
            with Image.open(img_path) as img:
                # 保存原图的EXIF信息
                exif = img.info.get('exif')

                # 统一转换为RGB格式
                if img.mode != 'RGB':
                    img = img.convert('RGB')

                # 对每种增强类型进行处理
                for enhance_type in ENHANCE_CONFIG.keys():
                    alias = ENHANCE_CONFIG[enhance_type]['alias']

                    # 应用增强
                    enhanced_img = apply_enhancement(img.copy(), enhance_type)

                    # 生成新文件名（使用英文别名）
                    new_base = f"{base_name}_{alias}"
                    new_img_name = f"{new_base}{ext}"
                    new_label_name = f"{new_base}.txt"

                    # 确定输出目录
                    img_output_dir = os.path.join(output_root, f'images_{alias}')
                    label_output_dir = os.path.join(output_root, f'labels_{alias}')

                    # 保存增强图片，保留EXIF信息
                    enhanced_img.save(
                        os.path.join(img_output_dir, new_img_name),
                        exif=exif
                    )

                    # 复制标签文件（YOLO格式的txt文件不需要修改内容）
                    try:
                        shutil.copy2(label_path, os.path.join(label_output_dir, new_label_name))
                    except Exception as e:
                        print(f"复制标签文件 {label_path} 失败: {str(e)}")
                        continue

                print(f"已处理: {img_file} -> 生成{len(ENHANCE_CONFIG)}种增强版本")

        except Exception as e:
            print(f"处理 {img_file} 时出错: {str(e)}")

if __name__ == "__main__":
    # ========== 请根据您的实际路径修改以下三个变量 ==========
    SOURCE_IMAGE_DIR = r"××地址"   # 原始图片目录，例如：r"C:\dataset\images"
    SOURCE_LABEL_DIR = r"××地址"   # 原始标签目录，例如：r"C:\dataset\labels"
    OUTPUT_ROOT = r"××地址"        # 输出根目录，例如：r"C:\output"
    # =====================================================

    # 执行处理
    process_dataset(
        image_dir=SOURCE_IMAGE_DIR,
        label_dir=SOURCE_LABEL_DIR,
        output_root=OUTPUT_ROOT
    )
    print("处理完成！")
