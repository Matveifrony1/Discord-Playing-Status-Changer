![Main Window](screenshots/it.png)
![overview](screenshots/yeah.jpg)
# Discord Playing Status Changer

A lightweight desktop application for managing Discord Rich Presence with custom statuses. Create unlimited profiles with personalized text, images, and clickable buttons that appear in your Discord profile.

## Features

- Create and save multiple status profiles
- Customize "Playing" text, state, and details
- Add large and small custom images
- Add 2 clickable buttons with URLs
- Auto-restore last active profile on startup
- System tray integration
- Autostart with Windows
- Bilingual interface (English/Russian)
- Built-in visual guides for setup

## How to Compile

### 1. Install dependencies
```bash
pip install pypresence customtkinter Pillow pystray
```

### 2. Prepare resources

Place in same folder as `app.py`:
- `icon.ico` (256x256 multi-size)
- `guide_1.png`, `guide_2.png`, `guide_3.png`
- `guide_image_1.png`, `guide_image_2.png`

### 3. Create `Discord_Status.spec` file

See spec file content in repository

### 4. Compile
```bash
pyinstaller Discord_Status.spec
```

### 5. Find executable

Compiled `.exe` will be in `dist/` folder

---

# Discord Playing Status Changer (Русский)

Легковесное приложение для управления Discord Rich Presence с кастомными статусами. Создавайте неограниченное количество профилей с персонализированным текстом, картинками и кликабельными кнопками, которые отображаются в вашем профиле Discord.

## Возможности

- Создание и сохранение множества профилей статусов
- Настройка текста "Playing", состояния и деталей
- Добавление больших и маленьких кастомных изображений
- Добавление 2 кликабельных кнопок с URL
- Автовосстановление последнего активного профиля при запуске
- Интеграция в системный трей
- Автозагрузка с Windows
- Двуязычный интерфейс (английский/русский)
- Встроенные визуальные гайды по настройке

## Как скомпилировать

### 1. Установите зависимости
```bash
pip install pypresence customtkinter Pillow pystray
```

### 2. Подготовьте ресурсы

Положите в папку с `app.py`:
- `icon.ico` (256x256 multi-size)
- `guide_1.png`, `guide_2.png`, `guide_3.png`
- `guide_image_1.png`, `guide_image_2.png`

### 3. Создайте файл `Discord_Status.spec`

См. содержимое spec файла в репозитории

### 4. Скомпилируйте
```bash
pyinstaller Discord_Status.spec
```

### 5. Готовый exe

Скомпилированный `.exe` будет в папке `dist/`
