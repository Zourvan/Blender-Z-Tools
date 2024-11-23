# 🧰 Z-Tools: Blender Material Management Add-on

## 🌟 Overview

Z-Tools is a powerful Blender add-on designed to streamline material management across objects and collections. With an intuitive interface, this tool simplifies the process of selecting, listing, and clearing materials in your 3D projects.

## ✨ Features

- 🎯 Dual Selection Mode

  - Object Mode: Manage materials for a specific object
  - Collection Mode: Manage materials across entire collections

- 📋 Dynamic Material Listing

  - Automatically lists materials when an object or collection is selected
  - No manual "List Materials" button required

- 🖱️ Advanced Selection
  - Shift-click to select multiple materials
  - Clear selected materials with a single click

## 📦 Installation

1. Download the Python script
2. In Blender, go to Edit > Preferences > Add-ons
3. Click "Install" and select the downloaded script
4. Enable the Z-Tools add-on

## 🚀 Usage

### Material Selection Mode

1. Open the "Z-Tools" panel in the 3D Viewport sidebar
2. Choose between "Object" or "Collection" mode

#### Object Mode

- Select a specific mesh object
- View and manage its materials

#### Collection Mode

- Select an entire collection
- View and manage materials for all mesh objects in the collection

### Selecting Materials

- Click the checkbox next to each material
- Use Shift-click to select multiple materials simultaneously

### Clearing Materials

- Select the materials you want to remove
- Click "Clear Selected Materials"
- Materials will be deleted from all relevant objects

## 🎨 Example Workflow

1. Switch to Collection mode
2. Select a scene collection
3. Review materials across all objects
4. Select unwanted materials
5. Click "Clear Selected Materials"

## 📝 Requirements

- Blender 2.90 or higher
- Python 3.7+

## 🤝 Contributing

Contributions are welcome! Please submit pull requests or open issues on GitHub.

## 📄 License

GPL

## 🐛 Bug Reports

Report issues on the GitHub repository with detailed steps to reproduce.

---

**Happy Blending! 🌈**

## AI Prompt

```
من میخوام یک ماژول جدید به Z-Tools اضافه کنم که:

1. قابلیت‌های مورد نیاز:
[لیست قابلیت‌های مورد نظر را اینجا بنویسید]

2. محل نمایش:
- در پنل Z-Tools در View3D > Sidebar
- ترجیحاً در کدام بخش از پنل قرار بگیرد

3. ویژگی‌های UI:
- نوع المان‌های مورد نیاز (دکمه، لیست، پراپرتی و...)
- چیدمان و ساختار پنل مطابق با استایل Z-Tools

4. عملکرد:
- توضیح دقیق عملکرد هر قابلیت
- ورودی و خروجی مورد انتظار
- محدودیت‌ها و شرایط خاص

5. سازگاری:
- سازگار با بلندر 3.3.0 و بالاتر
- سازگاری با سایر ماژول‌های Z-Tools

لطفا کد کامل ماژول را با ساختار زیر ارائه دهید:
1. فایل [module_name].py که در کنار سایر ماژول‌های Z-Tools قرار می‌گیرد
2. کلاس‌های مورد نیاز برای:
   - Properties
   - Operators
   - UI Panels
3. توابع register و unregister

در نهایت، نام ماژول را به لیست modulesNames در __init__.py اضافه خواهم کرد:

modulesNames = [
    'collection_scaler',
    'material_tools',
    'Blender_rename',
    'dissolvesFaces',
    'AdvancedVertexMerge',
    'transform_manager',
    '[module_name]'  # اضافه کردن ماژول جدید
]

```
