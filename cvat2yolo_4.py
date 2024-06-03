# Description: 将CVAT标注的XML文件转换为YOLO格式
# Author: wudi
# Date: 2024-05-18
# Usage: python cvat2yolo.py

import xml.etree.ElementTree as ET
import os
import shutil
import random
import tqdm


# 定义类别映射关系
# classes = {
#     "ignore": 0,
#     "traffic-signal-system_good": 1,
#     "traffic-signal-system_bad": 2,
#     "traffic-guidance-system_good": 3,
#     "traffic-guidance-system_bad": 4,
#     "restricted-elevated_good": 5,
#     "restricted-elevated_bad": 6,
#     "cabinet_good": 7,
#     "cabinet_bad": 8,
#     "backpack-box_good": 9,
#     "backpack-box_bad": 10,
#     "off-site": 11,
#     "Gun-type-Camera": 12,
#     "Dome-Camera": 13,
#     "Flashlight": 14,
#     "off-site-other": 15,
#     "b-Flashlight": 16
# }

# 定义类别映射关系
train_classes = {
    "ignore": 0,
    "traffic-signal-system_good": 1,
    "traffic-signal-system_bad": 2,
    "traffic-guidance-system_good": 3,
    "traffic-guidance-system_bad": 4,
    "restricted-elevated_good": 5,
    "restricted-elevated_bad": 6,
    "cabinet_good": 7,
    "cabinet_bad": 8,
    "backpack-box_good": 9,
    "backpack-box_bad": 10,
    "off-site": 11,
    "Gun-type-Camera": 12,
    "Dome-Camera": 13,
    "Flashlight": 14,
    "b-Flashlight": 15
}

# 定义类别映射关系
val_classes = {
    "traffic-signal-system_good": 1,
    "traffic-signal-system_bad": 2,
    "traffic-guidance-system_good": 3,
    "traffic-guidance-system_bad": 4,
    "restricted-elevated_good": 5,
    "restricted-elevated_bad": 6,
    "cabinet_good": 7,
    "cabinet_bad": 8,
    "backpack-box_good": 9,
    "backpack-box_bad": 10,
    "off-site": 11,
    "Gun-type-Camera": 12,
    "Dome-Camera": 13,
    "Flashlight": 14,
    "b-Flashlight": 15
}

class_state_dict = {
    'traffic-guidance-system': ('traffic-guidance-system_good', 'traffic-guidance-system_bad'),
    'restricted-elevated': ('restricted-elevated_good', 'restricted-elevated_bad'),
    'cabinet': ('cabinet_good', 'cabinet_bad'),
    'backpack-box': ('backpack-box_good', 'backpack-box_bad')
}


#定义为一个函数 check_AND_make_path 如果不存在目标文件夹则创建
def check_AND_make_path(path):
    if not os.path.exists(path):
        os.makedirs(path)

# 定义函数将XML标签转换为YOLO格式
def convert_annotations(xml_file, dest_folder):
    tree = ET.parse(xml_file)
    root = tree.getroot()

    split = "train"
    save_train_root_labels_path = os.path.join(dest_folder, split, "labels")
    save_train_root_images_path = os.path.join(dest_folder, split, "images")
    # check
    check_AND_make_path(save_train_root_labels_path)
    check_AND_make_path(save_train_root_images_path)
    
    
    split = "val"
    save_val_root_labels_path = os.path.join(dest_folder, split, "labels")
    save_val_root_images_path = os.path.join(dest_folder, split, "images")
    # check
    check_AND_make_path(save_val_root_labels_path)
    check_AND_make_path(save_val_root_images_path)
    
    validation_count = int(len(root.findall('image')) * 0.2)
    
    # 随机选择文件名
    validation_files = random.sample(root.findall('image'), validation_count)
    
    train_files = [file for file in root.findall('image') if file not in validation_files]
    
    
    
    for image in tqdm.tqdm(root.findall('image')):
        if image in train_files:
            save_root_labels_path = save_train_root_labels_path
            save_root_images_path = save_train_root_images_path
        else:
            save_root_labels_path = save_val_root_labels_path
            save_root_images_path = save_val_root_images_path
        
        img_name = image.get('name')
        img_width = float(image.get('width'))
        img_height = float(image.get('height'))

        yolo_file = os.path.join(save_root_labels_path, os.path.splitext(img_name)[0].split("/")[-1] + ".txt")

        with open(yolo_file, 'w') as f:
            for obj in image.findall('box'):
                cls = obj.get('label')
                
                # 获取状态属性
                state_element = obj.find('./attribute[@name="state"]')
                state = state_element.text if state_element is not None else None

                if cls == 'traffic-signal-system':
                    if state == 'normal':
                        cls = 'traffic-signal-system_good'
                    elif state in ['all-off', 'all-on', 'abnormal']:
                        cls = 'traffic-signal-system_bad'
                elif cls == "traffic-guidance-system":
                    if state == 'normal':
                        cls = 'traffic-guidance-system_good'
                    elif state in ['black-screen', 'abnormal']:
                        cls = 'traffic-guidance-system_bad'
                elif cls in class_state_dict:
                    if state == 'normal':
                        cls = class_state_dict[cls][0]
                    elif state == 'abnormal':
                        cls = class_state_dict[cls][1]
                
                if image in train_files:
                    if cls not in train_classes:
                        continue
                    cls_id = train_classes[cls]
                    
                else:
                    if cls not in val_classes:
                        continue
                    cls_id = val_classes[cls]
                    


                xmin = float(obj.get('xtl'))
                ymin = float(obj.get('ytl'))
                xmax = float(obj.get('xbr'))
                ymax = float(obj.get('ybr'))

                # 计算中心点坐标和宽高的相对值
                x_center = (xmin + xmax) / (2 * img_width)
                y_center = (ymin + ymax) / (2 * img_height)
                width = (xmax - xmin) / img_width
                height = (ymax - ymin) / img_height

                f.write(f"{cls_id} {x_center} {y_center} {width} {height}\n")

        # 复制图像到目标文件夹
        img_src = os.path.join("images", os.path.dirname(xml_file), img_name)
        pure_img_name = os.path.splitext(img_name)[0].split("/")[-1] + '.jpg'
        img_dest = os.path.join(save_root_images_path, pure_img_name)
        shutil.copy(img_src, img_dest)

# 执行转换
xml_files = ["annotations_lcx.xml", "annotations_lyy.xml", "annotations_wjk.xml", "annotations_wsj0.xml", 
             "annotations_wsj2.xml", "annotations_xk0.xml", "annotations_xk1.xml", "annotations_xk2.xml",
             "annotations_yjc.xml",]
dest_folder = "./hefei_yolo_format_v2.5"
for xml_file in xml_files:
    print(f"Processing {xml_file}")
    convert_annotations(xml_file, dest_folder)
    print(f"Processing {xml_file} complete.")
    
