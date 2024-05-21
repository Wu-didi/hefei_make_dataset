import xml.etree.ElementTree as ET  
from PIL import Image  
import os  

# 假设你的XML文件路径为xml_path  
xml_path = 'cvat_data/annotations_zyf.xml'  # 替换为你的XML文件路径  
img_root = 'cvat_data/images'  # 图像文件夹的根目录
save_image_root = 'attribute_images'  # 保存裁剪图像的根目录

# 如果存在就删除att_images文件夹
# if os.path.exists(save_image_root):
#     os.system(f"rm -rf {save_image_root}")
# 如果不存在就创建att_images文件夹
if not os.path.exists(save_image_root):
    os.makedirs(save_image_root)

# 解析XML文件  
tree = ET.parse(xml_path)  
root = tree.getroot()  

# 遍历所有的<image>元素  
for image in root.findall('.//image'):  
    # 提取图像ID和路径（假设路径在'name'属性中）  
    image_id = image.get('id')  
    image_name = image.get('name')  
    image_path = img_root + '/' + image_name  # 根据实际情况拼接图像路径  
    print(f"Processing image: {image_path}")
    # 打开原始图像  
    if os.path.exists(image_path):  
        img = Image.open(image_path)  
        # 转换为不带透明度的模式，例如RGB
        image_no_alpha = img.convert('RGB')
        # 遍历图像中的所有<box>元素  
        for box in image.findall('.//box'):  
            # 提取边界框坐标  
            xtl = int(float(box.get('xtl')))  
            ytl = int(float(box.get('ytl')))  
            xbr = int(float(box.get('xbr')))  
            ybr = int(float(box.get('ybr')))  

            # 裁剪图像  
            cropped_img = image_no_alpha.crop((xtl, ytl, xbr, ybr))  

            # 遍历所有的<attribute>元素，并为每个属性保存图像  
            for attribute in box.findall('attribute'):  
                attr_name = attribute.get('name')  
                attr_value = attribute.text  
                
                # 创建或检查属性对应的文件夹是否存在  
                folder_name = os.path.join('attribute_images', box.get('label'), attr_name, attr_value)  
                if not os.path.exists(folder_name):  
                    os.makedirs(folder_name)  
                    
                # 构造文件名并保存图像  
                file_name = f"{attr_name}_{attr_value}_{box.get('label')}_{image_id}.png"  
                file_path = os.path.join(folder_name, file_name)  
                cropped_img.save(file_path)  
    else:  
        print(f"Image not found: {image_path}")  
print("Processing complete.")
# 脚本结束