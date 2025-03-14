# NovelQ - 摸鱼阅读器

![NovelQ Logo](ikun.ico)

## 项目介绍

NovelQ（摸鱼阅读器）是一个轻量级的电子书阅读软件，支持多种格式的电子书文件，提供舒适的阅读体验。项目使用Python和PyQt6开发，支持Windows系统。

## 功能特点

- 支持多种文件格式：TXT、EPUB、PDF
- 自动检测文件编码，解决中文乱码问题
- 自动保存阅读进度，随时继续阅读
- 支持书签功能，方便标记重要内容
- 支持字体大小、行间距调整
- 支持明暗两种主题模式
- 支持无边框阅读模式，提供沉浸式体验
- 支持自动滚动功能，解放双手
- 支持章节导航，快速跳转

## 软件截图

<div align="center">
  <img src="img/demo1.png" alt="NovelQ界面截图1" width="600" />
  <p>图1：NovelQ阅读器主界面</p>
</div>

<div align="center">
  <img src="img/demo2.png" alt="NovelQ界面截图2" width="600" />
  <p>图2：NovelQ阅读设置界面</p>
</div>

## 安装方法

### 方法一：从源码运行

1. 克隆或下载本仓库
2. 安装依赖包：

```bash
pip install -r requirements.txt
```

3. 运行主程序：

```bash
python main.py
```

### 方法二：使用打包好的可执行文件

直接下载发布页面的exe文件，双击运行即可。

## 使用说明

1. 打开软件后，可以通过菜单栏的「文件」-「打开」选择要阅读的电子书文件
2. 使用工具栏上的按钮调整字体大小、切换主题等
3. 使用鼠标滚轮或键盘方向键翻页
4. 按F11可以切换无边框全屏模式，按ESC退出全屏
5. 在「设置」中可以设置默认小说文件夹，方便快速打开常读的书籍

## 如何打包成exe文件

本项目可以使用PyInstaller打包成Windows可执行文件，步骤如下：

1. 安装PyInstaller：

```bash
pip install pyinstaller
```

2. 在项目根目录下执行打包命令：

```bash
pyinstaller --name="NovelQ" --windowed --icon=ikun.ico --add-data="ikun.ico;." main.py
```

3. 打包完成后，可执行文件将位于`dist/NovelQ`目录下

4. 将`dist/NovelQ`目录下的所有文件复制到任意位置即可使用

### 打包注意事项

- 确保所有依赖已正确安装
- 如果使用了第三方资源文件（如图标），需要使用`--add-data`参数包含这些文件
- 使用`--windowed`参数可以避免启动时出现命令行窗口
- 使用`--icon`参数可以设置应用程序图标

## 许可证

本项目采用GNU通用公共许可证v3.0（GNU General Public License v3.0）进行许可。详情请参阅[LICENSE](LICENSE)文件。

## 作者

- **BBBQL2021**

## 贡献

欢迎提交问题和功能请求！如果您想贡献代码，请fork本仓库并提交拉取请求。

---

**NovelQ - 让阅读更轻松，摸鱼更自在！**