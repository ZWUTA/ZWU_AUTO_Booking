调用方式:```demo.py```文件提供了

```
from zwulib import *
appoint_zwulib('账号', '密码',  room_id =3 ,dday =1, begin = 8, duration = 13)
```

参数分别为，账号，密码，自习室id，延后日期，开始时间，持续时间

需要在```notice.py```文件设置邮件发送，使用139/189邮箱可以获得移动/电信的短信推送。

核心代码```zwulib.py```的第102行实现了一个朴素的插座算法，偶数位置有插座（但这并不对任意位置成立，需要对规则进行优化）

```df = df[(df['room']==room(self.type)) & (df['ava'] == 0) & (df['title']%2  == 0)]```


# 致谢

[杭州电子科技大学图书馆预约](https://github.com/HaleyCH/HDU_AUTO_BOOK-public)

由于上述开源代码未设置开源协议，本项目表示非常感谢并标注来源。本项目采用MIT开源协议，建议引用本项目的同时标注上述项目。