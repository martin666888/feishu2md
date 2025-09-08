# PyQt6重构实施计划

## 项目分析总结

### 当前架构
- **GUI层**: 使用Tkinter实现（MainWindow, PreviewWindow, SettingsWindow）
- **控制器层**: AppController使用回调机制与GUI通信
- **业务逻辑层**: API客户端、转换器、文件管理器（保持不变）
- **依赖**: 已包含PyQt6>=6.7.1

### 重构目标
- 完全替换Tkinter为PyQt6
- 将回调机制改为信号槽机制
- 保持所有现有功能不变
- 保持所有业务逻辑不变

## 详细实施步骤

### 阶段1: 准备工作和依赖检查
- [ ] 验证PyQt6依赖已正确安装
- [ ] 更新main.py中的依赖检查逻辑
- [ ] 替换main.py中的tkinter导入为PyQt6
- [ ] 更新main.py中的应用程序初始化逻辑

### 阶段2: 重构MainWindow类
- [ ] 创建新的PyQt6-based MainWindow类
  - [ ] 继承自QMainWindow
  - [ ] 实现init_ui()方法设置界面
  - [ ] 实现setup_connections()方法连接信号槽
  - [ ] 定义所有需要的信号:
    - [ ] conversion_started: pyqtSignal(str, str)
    - [ ] preview_requested: pyqtSignal()
    - [ ] settings_requested: pyqtSignal()
  - [ ] 实现所有输入控件（token, doc_id, output_path）
  - [ ] 实现进度条和状态显示
  - [ ] 实现输入验证逻辑
  - [ ] 实现文件浏览功能
  - [ ] 实现按钮功能（转换、预览、设置）
  - [ ] 实现状态日志功能
- [ ] 替换src/gui/main_window.py中的完整实现

### 阶段3: 重构PreviewWindow类
- [ ] 创建新的PyQt6-based PreviewWindow类
  - [ ] 继承自QDialog
  - [ ] 实现init_ui()方法设置界面
  - [ ] 实现setup_connections()方法连接信号槽
  - [ ] 实现QTabWidget用于源码和预览切换
  - [ ] 实现语法高亮功能
  - [ ] 实现文件操作功能（保存、另存为、复制）
  - [ ] 实现统计信息显示
- [ ] 替换src/gui/preview_window.py中的完整实现

### 阶段4: 重构SettingsWindow类
- [ ] 创建新的PyQt6-based SettingsWindow类
  - [ ] 继承自QDialog
  - [ ] 实现init_ui()方法设置界面
  - [ ] 实现setup_connections()方法连接信号槽
  - [ ] 实现QTabWidget用于设置分类
  - [ ] 实现所有设置控件
  - [ ] 实现设置保存和重置功能
- [ ] 将SettingsWindow从app_controller.py移出到独立文件
- [ ] 创建src/gui/settings_window.py

### 阶段5: 重构AppController类
- [ ] 修改AppController类以适配PyQt6
  - [ ] 替换Tkinter root为QApplication
  - [ ] 替换回调机制为信号槽连接
  - [ ] 实现槽函数:
    - [ ] handle_conversion_started()
    - [ ] handle_preview_requested()
    - [ ] handle_settings_requested()
  - [ ] 修改run()方法适配PyQt6事件循环
  - [ ] 修改shutdown()方法适配PyQt6
  - [ ] 确保线程安全更新GUI
- [ ] 更新src/app_controller.py中的实现

### 阶段6: 更新主程序入口
- [ ] 完全重写main.py
  - [ ] 导入PyQt6相关模块
  - [ ] 创建QApplication实例
  - [ ] 更新异常处理逻辑
  - [ ] 更新依赖检查包含PyQt6
  - [ ] 更新应用程序启动逻辑

### 阶段7: 更新模块导入和初始化
- [ ] 更新src/gui/__init__.py
  - [ ] 移除tkinter相关导入
  - [ ] 添加PyQt6相关导入
  - [ ] 更新导出类

### 阶段8: 测试和验证
- [ ] 功能测试
  - [ ] 测试输入验证功能
  - [ ] 测试转换流程
  - [ ] 测试预览功能
  - [ ] 测试设置功能
  - [ ] 测试文件操作功能
- [ ] 界面测试
  - [ ] 验证界面布局与原版一致
  - [ ] 验证所有控件功能正常
  - [ ] 验证信号槽连接正确
- [ ] 错误处理测试
  - [ ] 测试网络错误处理
  - [ ] 测试文件操作错误处理
  - [ ] 测试输入验证错误处理
- [ ] 集成测试
  - [ ] 测试完整的转换工作流
  - [ ] 测试应用程序启动和关闭

### 阶段9: 清理和优化
- [ ] 清理未使用的导入
- [ ] 优化代码结构和注释
- [ ] 验证代码质量
- [ ] 更新相关文档（如需要）

## 关键技术点

### 信号槽机制
- 将所有回调函数替换为PyQt6信号槽
- 确保线程安全的GUI更新
- 正确处理信号连接和断开

### 界面布局
- 使用QVBoxLayout, QHBoxLayout, QFormLayout替代Tkinter的grid/pack
- 保持界面外观与原版一致
- 确保控件大小和位置合理

### 文件操作
- 使用QFileDialog替代tkinter.filedialog
- 保持文件操作逻辑不变
- 确保跨平台兼容性

### 线程安全
- 使用QThread或QTimer进行线程安全的GUI更新
- 确保长时间运行的操作不阻塞界面

## 风险评估

### 高风险项
- 信号槽连接错误导致功能失效
- 线程安全问题导致程序崩溃
- 界面布局与原版差异过大

### 中风险项
- PyQt6特定API使用不当
- 文件操作路径处理问题
- 依赖版本兼容性问题

### 低风险项
- 代码风格不一致
- 注释更新不及时
- 测试覆盖不完整

## 成功标准

### 功能完整性
- [ ] 所有原有功能正常工作
- [ ] 用户操作流程完全一致
- [ ] 错误处理机制完整

### 界面一致性
- [ ] 界面布局与原版基本一致
- [ ] 控件行为与原版一致
- [ ] 用户体验无明显差异

### 代码质量
- [ ] 代码结构清晰
- [ ] 符合PyQt6最佳实践
- [ ] 无明显性能问题

### 稳定性
- [ ] 程序运行稳定
- [ ] 无内存泄漏
- [ ] 异常处理完善
