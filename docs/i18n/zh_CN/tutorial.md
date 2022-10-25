---
hide:
  - navigation
---

# 快速上手

欢迎来到 Textual 快速上手环节！

在本节内容结束之际，您将会搞懂如何使用 Textual 开发一个应用。

!!! quote

    If you want people to build things, make it fun.

    &mdash; **Will McGugan** (creator of Rich and Textual)

## 计时器应用

我们将以开发一个有关计时器应用为例。该应用会展示一批拥有开始、结束和重置的按钮功能的计时器，用户能够根据自己的需要添加和移除这些计时器。

这将会是一个简单却功能完备的应用，如果乐意的话，您也可以分发此应用。

以下将会是应用最终完成时的样子：

```{.textual path="docs/examples/tutorial/stopwatch.py" press="tab,enter,_,tab,enter,_,tab,_,enter,_,tab,enter,_,_"}
```

### 下载代码

如果您想尝试完整的计时器应用，并保持后续代码保持一致的步调，请确保您已经参考 [起步](getting_started.md) 一节并将 [Textual](https://github.com/Textualize/textual) 的项目代码下载到本地：

=== "HTTPS"

    ```bash
    git clone https://github.com/Textualize/textual.git
    ```

=== "SSH"

    ```bash
    git clone git@github.com:Textualize/textual.git
    ```

=== "GitHub CLI"

    ```bash
    gh repo clone Textualize/textual
    ```

将项目克隆之后，就可以切换到 `docs/examples/tutorial` 目录下并运行 `stopwatch.py`。

```bash
cd textual/docs/examples/tutorial
python stopwatch.py
```

## 类型注解（可选）

!!! tip inline end

    Textual 并不会强制您使用类型注解，因为它们是可选的；尽管我们在示例代码中用到了类型注解，但是否在项目中使用也完全取决于您。

在 Textualize 的每一个人都超爱 Python 的类型注解。如果您到目前为止还没接触过类型注解，那么是时候可以尝试为您的代码、参数以及返回值添加类型。为代码添加类型注解能让类似于 [mypy](https://mypy.readthedocs.io/en/stable/) 这样的工具在您的代码运行前事先捕获到 Bug。

比如包含类型注解的函数看起来就像这样：

```python
def repeat(text: str, count: int) -> str:
    """Repeat a string a given number of times."""
    return text * count
```

每个参数后面都紧跟着一个英文冒号并紧挨着一个类型。所以 `text: str` 表示 `text` 参数需要一个字符串类型的值，而 `count: int` 则表示 `count` 参数需要一个整数类型的值。

在 `->` 之后表示返回值的类型。于是乎 `-> str:` 就表示这个函数最终会返回一个字符串类型的值。

## App 类

构建一个 Textual 应用的第一步就是导入并扩展 `App` 类。在如下示例中，我们会基于 `App` 类构造一个基础的应用类，将其作为我们计时器应用例子的开端。

```python title="stopwatch01.py"
--8<-- "docs/examples/tutorial/stopwatch01.py"
```

运行上述代码之后，您会将会看到如下内容：

```{.textual path="docs/examples/tutorial/stopwatch01.py"}
```

我们可以按下 ++d++ 键在浅色与深色模式间进行切换：

```{.textual path="docs/examples/tutorial/stopwatch01.py" press="d" title="TimerApp + dark"}
```

按下 ++ctrl+c++ 组合键则退出应用并回到终端控制台。

### 细说 App 类

现在让我们进一步深入 `stopwatch01.py` 中的代码。

```python title="stopwatch01.py" hl_lines="1 2"
--8<-- "docs/examples/tutorial/stopwatch01.py"
```

第一行是从 Textual 中导入 `App` 类，它是我们构建应用的基础。

紧接着下一行则是导入两个内置的部件，其中：

- `Footer` 部件会在应用界面底部用展示一个包含可用按键的状态栏；
- `Header` 部件会在应用界面顶部展示标题和当前时间。

所有部件都是可被重复使用的组件，会占据应用界面的一部分区域。在本节内容中我们也将会学习到如何构造部件。

下面几行代码则表示应用是如何被定义的：

```python title="stopwatch01.py" hl_lines="5-17"
--8<-- "docs/examples/tutorial/stopwatch01.py"
```

继承了 `App` 类的应用类是包含大部分业务逻辑的地方，它会用来加载配置、设置部件、处理案件等等。

前面的代码就包含了几部分内容：

- `BINDINGS` 是一个包含了若干将键位与行为映射（或绑定）元组的列表。当中每个元组的第一个值表示按键，而第二个值则表示行为名称，最后一个值则表示行为简述。所以上述例子中我们设定了一个键位映射，即将 ++d++ 键与「toggle_dark」这一行为相绑定。可以查阅 [key bindings](./guide/input.md#bindings) 一节获取更多内容。

- `compose()` 是我们使用 UI 部件的地方。`compose()` 方法可以使用 `return` 关键字返回用到的部件，但在 Textual 中通常更偏向于使用 `yield` 关键字来代替 `return`（因为它会将整个方法转换成一个生成器）。在示例代码中我们使用了 `yield` 将每个我们导入了的部件以生成器的方式返回，例如 `Header()` 和 `Footer()`。

- `action_toggle_dark()` 定义了一个*行为*方法。行为通常都是用以 `action_` 前缀开头并紧接着行为名称命名的方法。上述 `BINDINGS` 列表则告诉 Textual 当 ++d++ 键被按下时则运行对应方法。可以查阅 [actions](./guide/actions.md) 一节获取更多内容。

```python title="stopwatch01.py" hl_lines="20-22"
--8<-- "docs/examples/tutorial/stopwatch01.py"
```

剩余的几行代码则表示创建一个应用类实例，并调用 [run()][textual.app.App.run] 方法在您的终端上以 *应用模式* 运行直到按下 ++ctrl+c++ 组合键退出为止。将代码置于 `__name__ == "__main__"` 下后，我们就可以通过 `python stopwatch01.py` 运行应用。

## 基于部件设计 UI

Textual 由多个部件构成，比如前面的首部和尾部，它们都是通用且可重复使用的。所以接下来我们会计时器自定义一些部件。

但在动手编码之前，先让我们为应用设计一个原型图，以便能清楚地知道我们打算干什么。

<div class="excalidraw">
--8<-- "docs/images/stopwatch.excalidraw.svg"
</div>

### 自定义部件

我们需要一个 `Stopwatch` 部件，而它又以下几个部分组成：

- 一个「Start」按钮
- 一个「Stop」按钮
- 一个「Reset」按钮
- 一个时间展示区域

Textual 内置了一个 `Button` 部件能够满足我们前三个按钮的需要。所以唯一一个需要我们去自定义的就是用于展示时间的部件，在这个部件中我们可以看到时间流逝以及对应的计时器。

现在就让我们将它们以代码形式添加到应用中。不过到目前为止也仅仅也只是做出了一个雏形，我们将在后续向当中添加更多功能。

```python title="stopwatch02.py" hl_lines="2-3 6-7 10-18 30"
--8<-- "docs/examples/tutorial/stopwatch02.py"
```

我们为代码导入了两个新的部件：`Button` 和 `Static`。前者会创建一个可被点击的按钮，而后者则是表示简单控制行为基础类。同时，我们还顺便从 `textual.containers` 中导入了 `Container`，它是一个 `Widget` 类型，可用于包含其他部件。

除此之外，我们暂时在继承 `Static` 类的基础上定义了一个空的 `TimeDisplay` 部件，我们也将在后续操作中完成它。

`Stopwatch` 部件也继承自 `Static` 类，它当中包含了 `compose()` 方法以便生成子部件，对应了三个表示的按钮 `Button` 对象以及一个展示时间的 `TimeDisplay` 对象。这些部分共同构成了我们原型图中的计时器。

#### 计时器按钮

构造按钮对象时用于展示在按钮之上的标签（`"Start"`、`"Stop"` 或者 `"Reset"`）参数；另外，构造按钮对象可能还需要如下参数：

- `id` is an identifier we can use to tell the buttons apart in code and apply styles. More on that later.
- `id` 即表示按钮对象的唯一标识，我们基于它来对按钮应用样式。稍后我们会进一步展开这部分内容。
- `variant` is a string which selects a default style. The "success" variant makes the button green, and the "error" variant makes it red.
- `variant` 即一个表示默认样式的字符串。比如 `"success"` 会默认为按钮填充绿色，而 `"error"` 则会为填充红色。

### 组合部件

为了能将部件添加到我们的应用中，我们首先需要在应用类的 `compose()` 方法中将其生成。

在前面 `Stopwatch.compose()` 方法的最后一行代码中，我们生成了一个 `Container` 对象，它表示包含了一组计时器的可滚动列表。当类包含了其他部件时（就像 `Container` 一样），它们就会通常会将其他子部件作为位置参数传递。所以当我们希望在应用启动时能自带三个计时器，那么我们就需要构造三个 `Stopwatch` 实例并将其传入到容器的构造器中。

### 无样式的应用

现在暂时让我们看看当运行 `stopwatch02.py` 时会发生什么。

```{.textual path="docs/examples/tutorial/stopwatch02.py" title="stopwatch02.py"}
```

计时器应用的所有元素显现了出来：按钮们都是可以点击的，您也可以通过滚轮滚动整个容器。不过这并如我们原型图预期设计的那样，因为到目前为止，我们还没为新部件添加*样式*。

## 编写 Textual CSS

每个部件都有一个 `styles` 对象，它包括一系列属性以控制部件会以怎样的样貌呈现。假设现在您打算设置为一个部件设置白色字体以及填充蓝色背景，那将会进行如下操作：

```python
self.styles.background = "blue"
self.styles.color = "white"
```

当然为一个应用设置所有样式是可以的，但没必要。

Textual 支持 CSS (Cascading Style Sheets)——一种常用于 Web 浏览器的技术。CSS 文件包含了所有应用于您的部件的样式内容，它也通常也会被您的 Textual 应用作为数据文件所加载。

!!! info

    Textual 中的 CSS 会比 Web 版本的 CSS 更易学易用。

CSS 可以让应用的迭代设计和 [实时编辑](./guide/devtools.md#live-editing) 的过程变得更加容易，即您可以直接编辑 CSS 并查看更爱效果而无需重新启动应用程序！

现在就让我们为应用添加一个 CSS 文件。

```python title="stopwatch03.py" hl_lines="24"
--8<-- "docs/examples/tutorial/stopwatch03.py"
```

接着，在代码中添加一个 `CSS_PATH` 类属性，这会告诉 Textual 当启动应用时加载给定的文件内容。

```sass title="stopwatch03.css"
--8<-- "docs/examples/tutorial/stopwatch03.css"
```

当我们启动应用时，它就变得与众不同。

```{.textual path="docs/examples/tutorial/stopwatch03.py" title="stopwatch03.py"}
```

此时应用看起来比我们原型图所设计的要好上不少。

现在让我们来看看 Textual 是如何使用 `stopwatch03.css` 样式文件的。

### CSS 基础

CSS 文件包含了许多 *声明块*。这里我们又再次看到 `stopwatch03.css` 文件中的第一个声明块：

```sass
Stopwatch {
    layout: horizontal;
    background: $boost;
    height: 5;
    padding: 1;
    margin: 1;
}
```

在上述代码中，第一行告诉 Textual 将样式作用于 `Stopwatch` 部件，而在由一对花括号包裹的几行内容，则表示具体样式。

现在让我们看看 CSS 代码如何改变 `Stopwatch` 部件的呈现方式：

<div class="excalidraw">
--8<-- "docs/images/stopwatch_widgets.excalidraw.svg"
</div>

- `layout: horizontal` 样式将子部件按从左到右的横向方式排列；
- `background: $boost` 样式将背景颜色设置为 `$boost`. 其中 `$` 前缀表示从内置主题配色中选择一个预定义的颜色。不过「条条大路通罗马」，我们也还有其他选择颜色的方式，比如直接指定颜色名称 `"blue"` 或者使用 RGB 表示的 `rgb(20,46,210)`；
- `height: 5` 样式将我们的部件高度设置为 5 行文本高度；
- `padding: 1` 样式将子部件旁边的内边距设置为 1 单元格；
- `margin: 1` 样式则会在 `Stopwatch` 部件周围创造一个 1 单元格大小的空间。

在 `stopwatch03.css` 其他的声明块中：

```sass
TimeDisplay {
    content-align: center middle;
    opacity: 60%;
    height: 3;
}

Button {
    width: 16;
}

#start {
    dock: left;
}

#stop {
    dock: left;
    display: none;
}

#reset {
    dock: right;
}
```

`TimeDisplay` 块会让文本内容居中对齐（`content-align`），并设置了一点点不透明度（`opacity`），同时还设置了其高度为 3 行文本高度。

而 `Button` 块则为按钮设置了 16 个单元格的宽度（`width`，也即字符宽度）。

剩下三个代码块的格式稍微有点不同。当我们以 `#` 开头声明时，样式只会作用于具有同名 `id` 属性的部件。即我们在 `compose()` 方法中为 `Button` 部件们设置了 ID，所以在示例中第一个 `id="start"` 的按钮就会匹配到 `#start` 所表示的 CSS。

所有按钮都有一个 `dock` 样式，它用于在给既定的边缘下对齐部件。基于样式，`start` 按钮和 `stop` 按钮将会设置在左侧，而 `reset` 按钮则会设置在右侧。

您可能注意到了 `stop` 按钮（对应着 CSS 中的 `#stop` 部分）有一个 `display: none;` 样式，这是在告诉 Textual 隐藏该按钮。之所以这么做，原因在于我们不想在计时器没有运行的情况下展现该按钮；类似地，我们也不想在计时器运行的情况下展示开始按钮。

所以，在接下来的一小节中，我们会学习到如何管理动态 UI。

### 动态 CSS

我们期望 `Stopwatch` 部件有两个状态：

1. 默认状态下只展示开始和重置按钮；
2. 而计时状态下则有一个停止按钮。

相应地，当计时器开始时会拥有一个绿色背景，其文字内容会被设置为粗体。

<div class="excalidraw">
--8<-- "docs/images/css_stopwatch.excalidraw.svg"
</div>

我们可以通过 CSS 类来实现这一目标。注意，不要将其与 Python 类相混淆，CSS 类就像是标签一样，您可以将其修改以作用于一个部件。

于是我们就有了新的 CSS 样式：

```sass title="stopwatch04.css" hl_lines="33-53"
--8<-- "docs/examples/tutorial/stopwatch04.css"
```

这些新出现的规则都带有 `.started` 开头的前缀，其中 `.` 表示 CSS 类的用法，而 `.started` 则代指名为 `stared` 的 CSS 类。所以新样式仅会用于包含了该 CSS 类名的部件。

有些样式可能还有多个由空格分隔的选择器，空格表示在匹配第一个选择器之后还应该要匹配第二个选择器。现在让我们看看当中的一个样式：

```sass
.started #start {
    display: none
}
```

`.started` 选择器会匹配任何一个拥有 `"started"` CSS 类名的部件，而 `#start` 则会进一步匹配器 ID 为 `"start"` 的子部件，当计时器处于计时状态时，开始按钮就会匹配上该样式；而 `"display: none;"` 样式规则则会告诉 Textual 隐藏该按钮。

### 操作 CSS 类

调整一个部件的 CSS 类是更新视觉效果的一种便捷方式，这样我们就无需引入大量用于表现的代码。

您可以通过 [add_class()][textual.dom.DOMNode.add_class] 和 [remove_class()][textual.dom.DOMNode.remove_class] 方法来添加或移除 CSS 类。我们也会使用这些方法来与计时状态下的开始（或停止）按钮相连接。

如下代码会让计时器开始计时或停止计时，以作为点击按钮时的回应：

```python title="stopwatch04.py" hl_lines="13-18"
--8<-- "docs/examples/tutorial/stopwatch04.py"
```

`on_button_pressed` 方法是一个*事件处理器*。事件处理器是 Textual 在回应*事件*时所调用的方法，例如按下某个键、点击鼠标等等。事件处理器常常以 `on_` 前缀开头并紧接着事件名称命名，因此 `on_button_pressed` 会处理当按钮被点击时的事件。

如果您现在运行 `stopwatch04.py`，那么当您点击第一个按钮时，将可以在两种状态之间来回切换。

```{.textual path="docs/examples/tutorial/stopwatch04.py" title="stopwatch04.py" press="tab,tab,tab,_,enter,_,_,_"}
```

## 响应式属性

在 Textual 中经常出现的主题配色通常都是很少需要您去显示更新的部件，当然您也可以通过 [refresh()][textual.widget.Widget.refresh] 去展示新数据。但是在 Textual 中，我们更倾向于依赖 *响应式* 属性来自动完成更新操作。

您可以通过 [reactive][textual.reactive.reactive] 来声明一个响应式属性。现在让我们利用这个特性去创建一个用以显示流逝时间的时间对象，并让其持续刷新。

```python title="stopwatch05.py" hl_lines="1 5 12-27"
--8<-- "docs/examples/tutorial/stopwatch05.py"
```

现在我们拥有了两个响应式属性：

- `start_time` 包含了计时器开始之后的秒数时间；
- `time` 则包含展示于 `Stopwatch` 之上的时间。

两个属性对于 `self` 而言都是可用的，尤其当您在 `__init__` 初始化赋值时。当您写入二者其一时，部件会自动完成更新操作。

!!! info

    在这个例子中的 `monotonic` 函数是从 `time` 标准库模块导入，它类似于 `time.time`；但当系统时钟变化时它不会回退。

`reactive` 的第一个参数默认是一个值或能返回默认值的可调用对象。

由于 `start_time` 的默认参数是 `monotoic`，所以当 `TimeDisplay` 被添加到应用时，`start_time` 属性就会被设置为 `monotonic()` 的调用结果。

而 `time` 属性则是传入了一个简单的浮点数默认值，因此 `self.time` 将从 `0` 开始。

`on_mount` 方法是一个事件处理器，它会在部件被第一次添加（或*挂载*）到应用时被调用。在这个方法中，我们调用 [set_interval()][textual.message_pump.MessagePump.set_interval] 去创建一个时间对象，该时间对象会每秒钟调用一次 `update_time`，而 `update_time` 方法会计算从部件运行时的流逝时间，然后将其赋值到 `self.time` 中。上述操作会让我们见识到响应式特性的强大之处。

如果您实现了一个以 `watch_` 前缀开头（让其成为一个*监听方法*）并紧接着响应式属性名称命名的方法，该方法会在响应式属性被修改时调用。

因为 `watch_time` 监听 `time` 属性，当我们每秒更新 `self.time` 时，也隐式地调用了 `watch_time`，从将流逝时间转换成一个字符串并更新到拥有 `self.update` 方法的部件中。

最终 `Stopwatch` 部件会展示自从部件被生成时的流逝时间。

```{.textual path="docs/examples/tutorial/stopwatch05.py" title="stopwatch05.py"}
```

到目前为止，我们已经了解了如何去更新部件的时间对象，但我们还需要连接按钮，以便我们单独操作计时器。

### 连接按钮

我们希望能单独地为计时器进行开启计时、停止或重置，我们可以通过为 `TimeDisplay` 类添加一小部分方法来实现这些操作。

```python title="stopwatch06.py" hl_lines="14 18 22 30-44 50-61"
--8<-- "docs/examples/tutorial/stopwatch06.py"
```

总的来说，我们为 `TimeDisplay` 加了点料：

- 我们新增了一个 `total` 响应式属性以保存在从点击开始计时到停止按钮时总共流逝时间；
- 调用 `set_interval` 时多了一个 `pause=True` 参数，它能够在时间对象开始时处于暂停模式（除非调用 [resume()][textual.timer.Timer.resume]，否则当时间对象处于暂停状态时，计时器不会工作。），因为我们不想让时间在用户还没有点击开始按钮时就更新；
- `update_time` 方法也将 `total` 属性添加到了当前时间中，用以计算之前每次一点击开始计时按钮和停止按钮时的用时；
- 我们也会将 `set_interval` 所返回的时间对象结果进行存储，并在我们启动计时器时的晚些时间 *恢复* 时间对象；
- 最后，我们还添加了 `start()`、`stop()` 和 `reset()` 方法。

另外，在 `Stopwatch` 中的 `on_button_pressed` 方法也补充了一些代码以管理当用户点击按钮时的时间展示情况。让我们进一步深入地说明一下：

```python
    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Event handler called when a button is pressed."""
        button_id = event.button.id
        time_display = self.query_one(TimeDisplay)
        if button_id == "start":
            time_display.start()
            self.add_class("started")
        elif button_id == "stop":
            time_display.stop()
            self.remove_class("started")
        elif button_id == "reset":
            time_display.reset()
```

上述代码又增添了额外的功能，让我们的应用变得更加实用。当中的逻辑主要是：

- 首先，第一行代码会获取到被点击的按钮的 `id` 属性，我们借此以决定最终的响应效果；
- 其次，第二行代码调用了 `query_one` 去获取 `TimeDisplay` 部件的引用；
- 接着，当匹配到对应的被点击的按钮时，我们会则调用 `TimeDisplay` 中对应的方法。具体而言就是，当计时器处于开始状态是，我们就添加一个 `"started"` 类（即使用 `self_add_class("started")`），当处停止状态时，就会将该类移除（即使用 `self.remove_class("started")`），通过 CSS 来改变计时器的视觉效果。

所以当您运行 `stopwatch06.py`，您就能够独立操作每个计时器：

```{.textual path="docs/examples/tutorial/stopwatch06.py" title="stopwatch06.py" press="tab,enter,_,_,tab,enter,_,tab"}
```

最后就让我们实现计时器应用仅剩的一个功能，即：添加和移除计时器。

## 动态部件

当计时器应用运行时会调用 `compose()` 方法来创建部件，但我们也需要在应用运行的过程中创建新的或是移除掉我们不再需要的部件。

我们可以通过调用 [mount()][textual.widget.Widget.mount] 方法来添加一个部件，而使用 [remove()][textual.widget.Widget.remove] 方法来移除一个部件。

所以我们就使用这两个方法来为我们的应用新增添加和移除计时器的功能：

```python title="stopwatch.py" hl_lines="78-79 88-92 94-98"
--8<-- "docs/examples/tutorial/stopwatch.py"
```

以上新增代码详解：

- `StopwatchApp` 类中的 `Container` 对象多加了一个 `"timers"` ID；
- 新增一个 `action_add_stopwatch` 以添加新的计时器；
- 新增一个 `action_remove_stopwatch` 以移除一个计时器；
- 新增额外的行为按键映射绑定。

`action_add_stopwatch` 方法会创建并挂载一个新的计时器。注意，调用基于 `"#timers"` 调用 [query_one()][textual.dom.DOMNode.query_one] 会通过 ID 获取到对应包含了时间对象的容器，一旦挂载了之后，新的计时器就会在终端显现；最后调用 [scroll_visible()][textual.widget.Widget.scroll_visible] 会让容器滚当使得新的 `Stopwatch` 计时器可见（如果需要的话）。

而在 `action_remove_stopwatch` 方法中，基于 `"Stopwatch"` CSS 选择器调用 [query()][textual.dom.DOMNode.query] 则会获取到所有 `Stopwatch` 部件。在这些部件存在的情况下，会调用 [last()][textual.css.query.DOMQuery.last] 方法以获取到最后一个计时器，然后再通过 [remove()][textual.css.query.DOMQuery.remove] 方法将其移除。

至此，当您运行 `stopwatch.py` 时，您就能通过 ++a++ 键添加一个新的计时器；反之，则通过 ++r++ 键移除一个计时器。

```{.textual path="docs/examples/tutorial/stopwatch.py" press="d,a,a,a,a,a,a,a,tab,enter,_,_,_,_,tab,_"}
```

## 接下来该做什么？

恭喜您构建了第一个 Textual 应用！

本教程涵盖了许多 Textual 的内容。如果您属于那种喜欢通过编码来学习一个框架类型的人，请悉随尊便；您也可以「魔改」`stopwatch.py` 或是再从头到尾浏览一遍所有例子。

您也可以阅读使用指南以获得更多有关如何基于 Textual 去构建一个复杂的 TUI 应用程序的细节内容。
