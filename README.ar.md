
[![Discord](https://img.shields.io/discord/1026214085173461072)](https://discord.gg/Enf6Z3qhVr)
[![Supported Python Versions](https://img.shields.io/pypi/pyversions/textual)](https://pypi.org/project/textual/)
[![PyPI version](https://badge.fury.io/py/textual.svg?)](https://badge.fury.io/py/textual)
![OS support](https://img.shields.io/badge/OS-macOS%20Linux%20Windows-red)



![textual-splash](https://github.com/user-attachments/assets/4caeb77e-48c0-4cf7-b14d-c53ded855ffd)

# Textual

<img align="right" width="250" alt="clock" src="https://github.com/user-attachments/assets/63e839c3-5b8e-478d-b78e-cf7647eb85e8" />

ابني واجهات مستخدم متوافقة مع كل الأنظمة بـ API بايثون بسيط جداً. شغل تطبيقاتك جوّه التيرمينال (terminal) *أو* في متصفح الويب (web browser).

الـ API بتاع Textual بيجمع بين البايثون الحديث وأفضل التطورات من عالم الويب، عشان يقدملك تجربة تطوير تطبيقات خفيفة وسريعة.
مكونات منفصلة (De-coupled) وإطار عمل [اختبار (testing)](https://textual.textualize.io/guide/testing/) متقدم بيضمنوا لك إنك تقدر تطور وتصين تطبيقك على المدى البعيد بدون أي مشاكل.

عايز تشوف أمثلة أكتر؟ شيك على مجلد [الأمثلة (examples)](https://github.com/Textualize/textual/tree/main/examples).

```python
"""
تطبيق بسيط لعرض الوقت الحالي.
"""

from datetime import datetime

from textual.app import App, ComposeResult
from textual.widgets import Digits


class ClockApp(App):
    CSS = """
    Screen { align: center middle; }
    Digits { width: auto; }
    """

    def compose(self) -> ComposeResult:
        yield Digits("")

    def on_ready(self) -> None:
        self.update_clock()
        self.set_interval(1, self.update_clock)

    def update_clock(self) -> None:
        clock = datetime.now().time()
        self.query_one(Digits).update(f"{clock:%T}")


if __name__ == "__main__":
    app = ClockApp()
    app.run()
```

> [!TIP]
> من تحت الفروة (under the hood)، Textual هو إطار عمل غير متزامن (asynchronous framework). وده معناه إنك تقدر تدمج تطبيقاتك مع مكتبات async &mdash; لو بتحب أو محتاج ده.
> ولو مش عايز أو مش محتاج تستخدم async، Textual مش هتجبرك عليه خالص.



<img src="https://img.spacergif.org/spacer.gif" width="1" height="64"/>

## العناصر والويدجتس (Widgets)

مكتبة الـ [widgets](https://textual.textualize.io/widget_gallery/) الخاصة بـ Textual بتغطي كل حاجة ممكن تحتاجها؛ من الأزرار (buttons)، القوائم الشجرية (tree controls)، جداول البيانات (data tables)، حقول الإدخال (inputs)، مناطق النصوص (text areas)، وحاجات تانية كتير…
ومع نظام [تخطيط (layout)](https://textual.textualize.io/how-to/design-a-layout/) مرن جداً، تقدر تنفذ أي واجهة مستخدم تيجى في بالك.

الثيمات (Themes) المجهزة مسبقاً بتضمن إن شكل تطبيقك يطلع أنيق وجاهز فوراً من غير ما تبذل مجهود في التصميم.


<table>

<tr>

  <td>
    
  ![buttons](https://github.com/user-attachments/assets/2ac26387-aaa3-41ed-bc00-7d488600343c)
    
  </td>

  <td>
    
![tree](https://github.com/user-attachments/assets/61ccd6e9-97ea-4918-8eda-3ee0f0d3770e)
    
  </td>
  
</tr>


<tr>

  <td>
    
  ![datatables](https://github.com/user-attachments/assets/3e1f9f7a-f965-4901-a114-3c188bd17695)
    
  </td>

  <td>
    
![inputs](https://github.com/user-attachments/assets/b02aa203-7c37-42da-a1bb-2cb244b7d0d3)
    
  </td>
  
</tr>
<tr>

<td>

![listview](https://github.com/user-attachments/assets/963603bc-aa07-4688-bd24-379962ece871)

</td>

<td>

![textarea](https://github.com/user-attachments/assets/cd4ba787-5519-40e2-8d86-8224e1b7e506)
  
</td>

  
</tr>

</table>


<img src="https://img.spacergif.org/spacer.gif" width="1" height="32"/>

## التثبيت (Installing)

ثبّت Textual عن طريق pip:

```
pip install textual textual-dev
```

شوف [دليل البداية (getting started)](https://textual.textualize.io/getting_started/) عشان تعرف كل التفاصيل.


<img src="https://img.spacergif.org/spacer.gif" width="1" height="32"/>

## العرض التوضيحي (Demo)


شغّل الأمر ده عشان تشوف شوية من الحاجات الرهيبة اللي Textual تقدر تعملها:

```
python -m textual
```

أو جرب الـ [textual demo](https://github.com/textualize/textual-demo) *من غير ما تثبّت أي حاجة* (بيحتاج أداة [uv](https://docs.astral.sh/uv/)):

```bash
uvx --python 3.12 textual-demo
```

<img src="https://img.spacergif.org/spacer.gif" width="1" height="32"/>

## لوحة المطورين (Dev Console)

<img align="right" width="40%" alt="devtools" src="https://github.com/user-attachments/assets/12c60d65-e342-4b2f-9372-bae0459a7552" />


إزاي تعمل debug وتكتشف أخطاء تطبيق شغال في التيرمينال، وأنت اصلاً بتستخدم التيرمينال؟

حزمة `textual-dev` بتوفر لك لوحة مطورين (dev console) بتتصل بتطبيقك من نافذة تيرمينال تانية خالص!
بالإضافة لرسائل النظام والأحداث، كل السجلات (logs) وجمل الـ print بتاعتك هتظهر في لوحة المطورين دي مباشرة.

شيك على [الدليل (guide)](https://textual.textualize.io/guide/devtools/) عشان تشوف باقي الأدوات المفيدة اللي بتقدمها حزمة `textual-dev`.

<img src="https://img.spacergif.org/spacer.gif" width="1" height="32"/>

## لوحة الأوامر (Command Palette)


تطبيقات Textual فيها لوحة أوامر (command palette) بتدعم البحث الذكي (fuzzy search).
اضغط على `ctrl+p` عشان تفتح لوحة الأوامر.

ومن السهل جداً توسع لوحة الأوامر وتضيف ليها [أوامر مخصصة (custom commands)](https://textual.textualize.io/guide/command_palette/) الخاصة بتطبيقك.


![Command Palette](https://github.com/user-attachments/assets/94d8ec5d-b668-4033-a5cb-bf820e1b8d60)

<img src="https://img.spacergif.org/spacer.gif" width="1" height="32"/>

# Textual ❤️ Web

<img align="right" width="40%" alt="textual-serve" src="https://github.com/user-attachments/assets/a25820fb-87ae-433a-858b-ac3940169242">


تطبيقات Textual بتشتغل في المتصفح بنفس السلاسة والكفاءة اللي بتشتغل بيها جوّه التيرمينال. أي تطبيق Textual تقدر تشغله كخدمة باستخدام `textual serve` &mdash; عشان تقدر تشارك إبداعاتك على الويب.
وده إزاي تشغل تطبيق العرض التوضيحي (demo):

```
textual serve "python -m textual"
```

بالإضافة لتشغيل تطبيقاتك محلياً، تقدر تشغلها وتشاركها مع العالم باستخدام [Textual Web](https://github.com/Textualize/textual-web).

تقنية Textual Web القوية والمتخطية للجدران النارية (firewalls) تقدر تشغل وتستضيف عدد غير محدود من التطبيقات.

وعشان تطبيقات Textual متطلبات نظامها بسيطة جداً وخفيفة، تقدر تثبتها في أي مكان بيشتغل فيه بايثون. وده بيحول أي جهاز لجهاز متصل بالشبكة.
من غير ما تحتاج شاشة سطح مكتب حتى!


<img src="https://img.spacergif.org/spacer.gif" width="1" height="32"/>


## انضم لينا على Discord

انضم لمطوري ومجتمع Textual على [سيرفر Discord بتاعنا](https://discord.gg/Enf6Z3qhVr).
