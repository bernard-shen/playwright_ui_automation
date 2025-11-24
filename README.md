# UI 自动化测试框架

一个基于 Python + Playwright 的 传统(相比AI而言) WEB UI 自动化测试框架，使用BasePage、BaseAssert、BaseExecutor来组成UI自动化执行的核心部分。其中使用关键字映射来复用页面元素操作，以特定用例规范来简化用例的编写形式。
该框架的目的是极大简化测试代码的编写，使用功能测试用例驱动UI自动化测试，使ui自动化从传统的编写代码，重心迁移到组织xpath和编写功能用例中；
这是一个 传统UI自动化工具的尝试，且该框架完成了自动化测试的主体功能。xpath提取和确认部分可以使用AI大模型来快速进行，并未包含在本框架之中。

## ✨ 主要特点

-   **YAML 驱动测试**: 将测试步骤、操作和数据定义在 YAML 文件中，非开发人员也能轻松编写和维护自动化用例。
-   **数据驱动**: 支持在 YAML 的 `input` 操作中使用列表，`BaseExecutor` 会自动为每个数据点循环执行完整的测试用例。
-   **页面元素分离**: 使用独立的 YAML 文件 (`adts_locations.yaml`) 集中管理页面元素的定位器 (Locators)，提高可维护性。
-   **自动报告**: 测试执行后，自动生成并打开 Allure Report，提供详细、可视化的测试结果。
-   **容器化支持**: 提供 `Dockerfile`，可轻松在容器环境中构建和运行自动化测试，便于集成到 CI/CD 流程。
-   **高度封装**: `BasePage` 封装了 Playwright 的常用操作，`BaseExecutor` 负责解析和执行，让测试用例脚本更简洁。

## ✨ 优缺点
-   **优点**: 通过数据驱动，极大简化了UI自动化测试用例的编写。
-   **确定**: 部分特性，没有pytest那么灵活，比如数据驱动时，会在一个用例中执行，而非pyetst.parametrize能自动识别多个用例。

## 📁 项目结构

```
ui_autotest_new/
├── base/                   # 核心封装（BaseExecutor, BasePage, BaseAssert）
├── config/                 # 配置文件（pytest.ini, web_ui.conf, adts_locations.yaml）
├── test_cases/             # Pytest 测试用例
├── test_data/              # YAML 测试数据和步骤
├── test-results/           # 测试输出目录
│   ├── logs/               # 日志文件
│   ├── screenshot/         # 截图文件
│   └── report/             # Allure 原始报告数据
│   └── allure-report/      # 生成的 Allure HTML 报告
├── utils/                  # 工具类（配置读取、登录等）
├── Dockerfile              # Docker 容器化配置文件
├── requirements.txt        # Python 依赖
└── run_web_ui_test.py      # 主运行脚本
```

## 🚀 环境设置

### 1. 安装 Python 依赖

```bash
pip install -r requirements.txt
```

### 2. 安装 Playwright 浏览器驱动

```bash
playwright install
```

### 3. 安装 Allure 命令行工具

Allure 用于生成测试报告。请确保它已安装并在系统 PATH 中。

-   **Windows (使用 Scoop)**:
    ```powershell
    scoop install allure
    ```
-   **macOS (使用 Homebrew)**:
    ```bash
    brew install allure
    ```
-   **手动安装**: 从 [GitHub Releases](https://github.com/allure-framework/allure2/releases) 下载并解压，然后将其 `bin` 目录添加到系统环境变量 `PATH`。

验证安装成功：
```bash
allure --version
```

## ⚡️ 如何运行测试

使用 `run_web_ui_test.py` 脚本来执行测试，它提供了丰富的命令行参数。

### 1. 运行所有测试

直接执行脚本，将运行 `test_cases/` 目录下的所有测试。

```bash
python run_web_ui_test.py
```

### 2. 根据标记 (Marker) 运行

例如，只运行标记为 `P0` 的高优先级用例。

```bash
python run_web_ui_test.py -m P0
```

### 3. 根据关键字运行

运行文件名、类名或方法名中包含特定关键字的用例。

```bash
python run_web_ui_test.py -k "search"
```

测试完成后，Allure 报告将自动生成并打开。

## 📝 编写 YAML 测试用例

测试的核心逻辑和数据位于 `test_data/` 目录的 YAML 文件中。

### 1. 基本结构

一个测试用例由唯一的名称和 `steps` 列表组成。 steps关键字包含页面操作关键字和断言关键字，定义在BaseExecutor __init__关键字映射中；

```yaml
search_task:
  case_name: "查询ALKKK"
  description: "查询ALKKK，查看各种ALLI是否存在"
  steps:
    - navigate: anliku_page
    - click: Path(ALKKK.查询.输入框)
    - wait: 1000
    - input:
        selector: Path(ALKKK.查询.输入框)
        value: CZtest06
    - take_screenshot: "search_task01.png"
```

### 2. 元素定位 `Path()`

-   **`Path(页面.模块.元素)`**: 这种语法用于从 `config/adts_locations.yaml` 文件中查找对应的 CSS 或 XPath 选择器。
-   **动态传参**: 使用 `.f()` 方法可以向选择器动态传递参数，例如：
    ```yaml
    - click: Path(ALKKK.左侧树.名称).f(SPACENAME1)
    ```

### 3. 数据驱动测试

当 `input` 操作的 `value` 是一个列表时，`BaseExecutor` 会为列表中的每个值完整地执行一次测试用例。

```yaml
search_task:
  case_name: "查询ALKKK"
  steps:
    - navigate: anliku_page
    - click: Path(ALKKK.查询.输入框)
    - input:
        selector: Path(ALKKK.查询.输入框)
        value:
          - abc123456      # 第一次循环的值
          - abc12345678    # 第二次循环的值
          - abc123456789   # 第三次循环的值
    - wait: 1000
```
当输入不同值，后续的操作和预期不同时，可以使用loop_step来为每个输入值定义后续操作；当然如果你不喜欢复杂的功能用例，也可以把循环拆成单个用例；
```yaml
search_task:
  case_name: "查询ALKKK"
  description: "查询ALKKK，查看各种ALLI是否存在"
  steps:
    - navigate: anliku_page
    - click: Path(ALKKK.查询.输入框)
    - input:
        selector: Path(ALKKK.查询.输入框)
        value:
          - CZtest06
          - test001
    - navigate: test_task_page
    - wait: 1000

  # 为每个循环值定义额外的步骤
  loop_steps:
    CZtest06:
      - press_key: enter
      - wait: 1000
      - take_screenshot: "test-results/screenshot/search_task_test06.png"
      - assert:
          selector: Path(ALKKK.列表.ALLI名称-首个)
          expected: 包含
          value: test06
    test001:
      - press_key: enter
      - wait: 1000
      - take_screenshot: "screenshot/search_task_test001.png"

```


## 🐳 Docker 支持

项目提供了 `Dockerfile`，可以方便地在容器中运行测试。

### 1. 构建 Docker 镜像

```bash
docker build -t ui-autotest .
```

### 2. 运行测试

使用 `-v` 参数将测试报告挂载到宿主机，以便在本地查看。

```bash
# --rm 会在容器停止后自动删除容器
docker run --rm -v "$(pwd)/test-results:/app/test-results" ui-autotest
```
**注意**: 在 Windows PowerShell 中，请使用 `${pwd}` 替代 `$(pwd)`。

### 3. 运行特定测试

```bash
docker run --rm -v "$(pwd)/test-results:/app/test-results" ui-autotest python run_web_ui_test.py -m P1
```

## ⚙️ 配置文件

-   `config/web_ui.conf`: 配置浏览器类型（chromium, firefox, webkit）、是否无头模式 (`is_headed`)、执行速度 (`slowmo`) 和基础 URL 等。
-   `config/adts_locations.yaml`: 集中管理所有页面的元素定位器。
-   `config/pytest.ini`: pytest 的配置文件，用于定义 `addopts`（如 Allure 报告目录）和 `markers`。

---

# BaseExecutor 优化记录

## 新增功能

### 1. Hover 操作支持
- 修复了 `hover: Path(...)` 步骤执行失败的问题
- 在 `_execute_single_step` 中添加了 hover 分支
- 更新了步骤描述和 selector 验证

### 2. 智能等待机制
- **解决异步加载问题**: 自动等待页面数据刷新完成，避免断言时页面还是旧数据
- **智能内容检测**: 检测元素内容是否稳定，确保断言前数据已更新
- **网络空闲等待**: 等待接口请求完成后再执行断言
- **可配置参数**: 支持启用/禁用、超时时间、检查间隔等配置

#### 智能等待触发场景
- **断言操作**: 执行 `assert` 步骤前自动等待页面稳定
- **Enter 键操作**: 按下 Enter 键后等待页面数据刷新
- **输入操作**: 输入完成后等待输入事件处理完成

#### 配置方法
```python
# 配置智能等待
executor.configure_smart_wait(
    enable=True,           # 启用智能等待
    timeout=15000,         # 超时时间15秒
    interval=0.3           # 检查间隔0.3秒
)

# 获取当前配置
config = executor.get_smart_wait_config()
print(config)
```

### 3. 完整的 BasePage 操作支持
现在 BaseExecutor 完全支持 BasePage 中定义的所有操作：

#### 基础操作方法
- `navigate` - 导航到页面
- `click` - 点击元素
- `input` - 输入文本
- `clear_and_input` - 清空并输入文本
- `select` - 选择下拉框选项
- `select_option_by_label` - 通过标签选择下拉框选项
- `check` - 勾选复选框
- `uncheck` - 取消勾选复选框
- `upload` - 上传文件
- `hover` - 鼠标悬停
- `double_click` - 双击元素
- `right_click` - 右键点击元素

#### 等待方法
- `wait` - 等待指定时间
- `wait_for_element` - 等待元素出现
- `wait_for_element_hidden` - 等待元素隐藏
- `wait_for_load_state` - 等待页面加载状态
- `wait_for_network_idle` - 等待网络空闲

#### 滚动方法
- `scroll_to_element` - 滚动到指定元素
- `scroll_to_bottom` - 滚动到页面底部
- `scroll_to_top` - 滚动到页面顶部

#### 键盘操作方法
- `press_key` - 按下指定按键
- `press_enter` - 按下Enter键
- `press_tab` - 按下Tab键
- `press_escape` - 按下Escape键
- `type_text` - 输入文本（当前焦点位置）

#### 页面操作方法
- `refresh_page` - 刷新页面
- `go_back` - 返回上一页
- `go_forward` - 前进到下一页
- `take_screenshot` - 截图
- `execute_script` - 执行JavaScript脚本

#### 对话框操作方法
- `accept_dialog` - 接受对话框
- `dismiss_dialog` - 取消对话框
- `get_dialog_text` - 获取对话框文本

#### 获取信息类操作
- `get_text` - 获取元素文本内容
- `get_attribute` - 获取元素属性值
- `get_value` - 获取输入框的值
- `is_visible` - 检查元素是否可见
- `is_enabled` - 检查元素是否启用
- `get_page_title` - 获取页面标题
- `get_current_url` - 获取当前URL

#### 断言方法
- `assert` - 支持多种断言类型（包含、等于、可见、不可见、启用、禁用、已勾选、未勾选等）

## 技术实现

### 1. Action Handlers 映射
- 在 `__init__` 方法中定义了完整的 `action_handlers` 字典
- 每个操作都对应一个处理方法

### 2. 步骤描述支持
- 在 `_get_step_description` 方法中为所有操作提供了中文描述
- 支持 Allure 报告中的步骤显示

### 3. Selector 验证
- 为需要 selector 的操作添加了验证逻辑
- 确保关键操作不会因为 selector 为空而失败

### 4. 执行逻辑
- 在 `_execute_single_step` 方法中添加了所有新操作的分支
- 每个操作都有相应的日志记录

## 使用示例

### YAML 测试用例格式
```yaml
test_case:
  case_name: "测试用例"
  steps:
    - navigate: page_url
    - click: Path(页面.按钮)
    - input:
        selector: Path(页面.输入框)
        value: "测试文本"
    - press_key: Enter
    # 智能等待会自动触发，无需手动添加等待步骤
    - assert:
        selector: Path(页面.结果)
        expected: 包含
        value: "期望结果"
```

### 智能等待使用说明

#### 1. 自动触发场景
以下操作会自动触发智能等待，无需手动配置：

```yaml
# 断言前自动等待页面稳定
- assert:
    selector: Path(ALKKK.列表.ALLI名称-首个)
    expected: 包含
    value: CZtest06

# Enter键后自动等待数据刷新
- press_key: Enter
# 自动等待网络空闲和DOM更新

# 输入后自动等待事件处理
- input:
    selector: Path(ALKKK.查询.输入框)
    value: CZtest06
# 自动等待输入事件处理完成
```

#### 2. 手动配置智能等待
```python
# 在测试用例中配置智能等待参数
def test_example(self):
    # 配置智能等待
    self.executor.configure_smart_wait(
        enable=True,           # 启用智能等待
        timeout=20000,         # 超时时间20秒
        interval=0.2           # 检查间隔0.2秒
    )

    # 执行测试用例
    result = self.executor.execute_test_case('test_name', test_data)
    assert result['success'] is True
```

#### 3. 禁用智能等待
```python
# 如果不需要智能等待，可以禁用它
self.executor.configure_smart_wait(enable=False)

# 或者使用更短的超时时间
self.executor.configure_smart_wait(timeout=5000)
```

### 新增操作说明
1. **clear_and_input**: 先清空输入框，再输入新文本
2. **select_option_by_label**: 通过选项的显示文本选择下拉框选项
3. **wait_for_network_idle**: 等待网络请求完成，适用于动态加载内容
4. **press_enter/tab/escape**: 常用的键盘操作
5. **get_text/attribute/value**: 获取元素信息，可用于验证或记录
6. **is_visible/enabled**: 检查元素状态，可用于条件判断

## 注意事项

1. 所有需要 selector 的操作都会进行验证，确保不会因为选择器为空而失败
2. 新增的操作都支持 timeout 参数，默认为 30000 毫秒
3. 获取信息类操作如果提供了 value 参数，会自动进行断言验证
4. 所有操作都有详细的日志记录，便于调试和问题排查

## 兼容性

- 保持了与现有测试用例的完全兼容性
- 新增功能不会影响现有功能

- 支持渐进式升级，可以逐步使用新功能
