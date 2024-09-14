# 文件对比工具

## 文件列表

- `folder_compare_wx.py` - 文件夹对比用户界面
- `hash_compare_wx.py` - 哈希对比用户界面
- `folder_compare.py` 和 `hash_compare.py` - 必要的函数文件，同时也是命令行版本

## 多种传参方式

1. **命令行参数**
    - 通过命令行传递一个或两个文件路径，将直接填入原文件（和新文件）路径。

2. **单实例传参**
    - 带有命令行参数的前提下，重复打开同一个程序，会自动把文件路径按照文件拖拽的逻辑处理。

3. **文件拖拽**
    - 支持将文件直接拖入 GUI 界面进行对比。可以拖拽一个或多个文件到输入框中，程序将会自动填充文件路径。（空值优先，然后交替填充）

4. **GUI 浏览选择**
    - 可以通过浏览按钮选择两个文件。


## 应用至Windows右键菜单快捷方式

### 自行修改参数填入注册表

- 可参考 https://blog.csdn.net/qq_31475993/article/details/107962270

注册表路径：

`HKEY_CLASSES_ROOT\*\shell\Hash Compare`
```
哈希对比
```

`HKEY_CLASSES_ROOT\*\shell\Hash Compare\command`
```
(你的Python解释器路径)\pythonw.exe (哈希对比路径)\hash_compare_wx.py) %1
```
    
`HKEY_CLASSES_ROOT\Directory\shell\Folder Compare`
```
文件夹对比
```

`HKEY_CLASSES_ROOT\Directory\shell\Folder Compare\command`
```
(你的Python解释器路径)\pythonw.exe (文件夹对比路径)\folder_compare_wx.py %1
```