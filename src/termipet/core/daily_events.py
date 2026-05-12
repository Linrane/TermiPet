"""日常事件系统 — 离线期间宠物自主行动（旅行青蛙风格）"""
from __future__ import annotations

import random
from datetime import datetime, timezone, timedelta
from typing import Any

from sqlalchemy.orm import Session

from termipet.models.pet import Pet
from termipet.models.item import Item, Inventory
from termipet.models.daily_event import DailyEventLog


# ── 事件定义（6大类，~30个事件） ─────────────────────────────────────────────────

DAILY_EVENTS: list[dict[str, Any]] = [
    # ═══ 大类 A：外出探索 (6个) ═══
    {
        "key": "garden_bug_hunt", "category": "外出探索",
        "title": "花园捉虫记",
        "summary": "{name} 在花园里追逐蝴蝶，结果捉到了一只数据虫！",
        "detail": "{name} 偷偷溜到花园，在花丛中匍匐潜行了整整一刻钟。终于，它猛地扑向一只闪闪发光的蝴蝶——结果蝴蝶飞走了，但它爪子底下压着一只蓝色的数据虫！",
        "weight": 10,
        "effect": {"happiness": 5, "intelligence": 2},
        "condition": lambda p: p.stage != "蛋",
    },
    {
        "key": "stream_walk", "category": "外出探索",
        "title": "数据溪边散步",
        "summary": "{name} 去数据溪边散步，捡到了几枚闪亮的金币。",
        "detail": "{name} 沿着数据溪慢慢走着，清澈的数据流倒映着它的身影。突然，溪水中闪烁起金色的光点——原来是一小堆金币卡在了数据石缝里！{name} 费了好大劲才把它们抠出来。",
        "weight": 8,
        "effect": {"coins": 8, "happiness": 3},
        "condition": lambda p: p.stage not in ("蛋", "幼年"),
    },
    {
        "key": "wall_escape", "category": "外出探索",
        "title": "翻墙历险",
        "summary": "{name} 偷偷翻墙出去了！虽然被你发现了，但它看起来很得意。",
        "detail": "趁你不注意，{name} 找了个数据裂缝，一溜烟翻了出去。等它回来时，毛发上沾着奇怪的碎片，但眼神里满是探险的兴奋——它说自己在墙外看到了从未见过的景象。",
        "weight": 5,
        "effect": {"happiness": 10, "energy": -5, "bond": -2},
        "condition": lambda p: p.stage in ("少年", "成年", "巅峰", "传奇", "远古"),
    },
    {
        "key": "neighbor_visit", "category": "外出探索",
        "title": "邻居家串门",
        "summary": "{name} 跑去隔壁灵兽家串门，还带回来一包小零食。",
        "detail": "{name} 敲开了隔壁灵兽的门。两家主人聊得正欢，{name} 和邻居在角落里交换了各自珍藏的小零食。回来时它的腮帮子鼓鼓的，显然吃了不少。",
        "weight": 7,
        "effect": {"hunger": 5, "happiness": 8, "bond": 3},
        "condition": lambda p: p.stage not in ("蛋",),
    },
    {
        "key": "chase_butterfly", "category": "外出探索",
        "title": "追逐蝴蝶",
        "summary": "{name} 追着一只数据蝴蝶满院子跑，累得气喘吁吁但笑得很开心。",
        "detail": "一只蓝色的数据蝴蝶飞过院子，{name} 的眼睛瞬间亮了起来。它上蹿下跳、左扑右闪，虽然一次都没抓到，但笑声回荡在整个家园上空。最后它躺在草地上，看着蝴蝶远去的背影，满足地叹了口气。",
        "weight": 9,
        "effect": {"happiness": 8, "energy": -8},
        "condition": lambda p: p.stage not in ("蛋",),
    },
    {
        "key": "data_rift_edge", "category": "外出探索",
        "title": "数据裂缝边缘",
        "summary": "{name} 好奇地靠近了家园边界的数据裂缝，感受到了奇异的力量波动。",
        "detail": "家园边界有一道若隐若现的数据裂缝，平时被结界遮蔽。{name} 悄悄走近，感受到裂缝中传来的微弱脉冲。它伸出爪子试探性地碰了碰——一道淡蓝色的光芒闪过，它的智力似乎有所提升。",
        "weight": 4,
        "effect": {"intelligence": 5, "energy": -3},
        "condition": lambda p: p.stage in ("成年", "巅峰", "传奇", "远古") and p.intelligence < 80,
    },

    # ═══ 大类 B：家园日常 (5个) ═══
    {
        "key": "kitchen_snack", "category": "家园日常",
        "title": "厨房偷吃",
        "summary": "{name} 偷偷溜进厨房，从柜子里翻出了一包零食。",
        "detail": "趁你不注意，{name} 蹑手蹑脚地溜进了厨房。它闻到了柜子里藏着的零食香气，凭着顽强的毅力（和灵活的爪子）打开了柜门。美美地吃了一顿之后，它心满意足地擦了擦嘴——还贴心地帮你把柜门关上了。",
        "weight": 8,
        "effect": {"hunger": 10, "happiness": 5},
        "condition": lambda p: p.stage not in ("蛋",) and p.hunger < 60,
    },
    {
        "key": "bedroom_roll", "category": "家园日常",
        "title": "卧室打滚",
        "summary": "{name} 在卧室的地毯上开心地打滚，把地毯弄得乱七八糟。",
        "detail": "{name} 趁卧室没人，在柔软的地毯上翻来覆去地打滚。左滚三圈、右滚三圈，最后干脆肚皮朝上摊成一张饼。等你回来时，地毯已经被滚成了一个抽象艺术品。",
        "weight": 9,
        "effect": {"happiness": 6, "cleanliness": -8},
        "condition": lambda p: p.stage not in ("蛋",),
    },
    {
        "key": "garden_mess", "category": "家园日常",
        "title": "花园被弄乱了",
        "summary": "{name} 在花园里玩耍，不小心踩倒了好几盆花。",
        "detail": "{name} 在花园里追蝴蝶时太投入了，完全没注意到脚下的花盆。'啪嗒'——一盆、两盆、三盆……等它反应过来时，花园已经一片狼藉。{name} 愧疚地低下了头，小心翼翼地把花扶了回去。",
        "weight": 5,
        "effect": {"happiness": 2, "cleanliness": -5, "bond": -2},
        "condition": lambda p: p.stage not in ("蛋",) and p.personality == "顽皮",
    },
    {
        "key": "workshop_invent", "category": "家园日常",
        "title": "工坊小发明",
        "summary": "{name} 在工坊里捣鼓了半天，声称自己发明了'自动喂食器'。",
        "detail": "{name} 不知道什么时候学会了使用工坊的工具。它把几个废零件和材料拼凑在一起，做出了一个造型奇特的装置。虽然它信心满满地称之为'自动喂食器'，但测试时装置只发出了'嘎吱'一声就散架了……不过{name}看起来并不气馁。",
        "weight": 4,
        "effect": {"intelligence": 4, "energy": -6},
        "condition": lambda p: p.stage in ("少年", "成年", "巅峰", "传奇", "远古"),
    },
    {
        "key": "library_nap", "category": "家园日常",
        "title": "图书室打瞌睡",
        "summary": "{name} 在图书室看书看着看着就睡着了，脸上还压着一本技能书。",
        "detail": "{name} 抱着一本厚厚的技能书进了图书室，信誓旦旦地表示要'充实自己'。然而不到十分钟，它的眼皮就开始打架了……最后它趴在书上呼呼大睡，口水把书页浸湿了一小块。",
        "weight": 7,
        "effect": {"energy": 5, "intelligence": 2, "cleanliness": -3},
        "condition": lambda p: p.stage not in ("蛋",) and p.energy < 50,
    },

    # ═══ 大类 C：社交互动 (5个) ═══
    {
        "key": "neighbor_fight", "category": "社交互动",
        "title": "和隔壁吵架了",
        "summary": "{name} 和隔壁灵兽因为一块领地的问题吵了一架。",
        "detail": "一只野生灵兽侵入了家园附近的区域，{name} 立刻竖起耳朵冲了出去。隔壁灵兽也闻声赶来，双方为了这块'领地'大声争论了很久。最后它们达成了一个复杂的边界协议——但第二天{name}就忘了自己同意了什么。",
        "weight": 4,
        "effect": {"happiness": -5, "bond": 2, "constitution": 2},
        "condition": lambda p: p.stage in ("少年", "成年", "巅峰", "传奇", "远古"),
    },
    {
        "key": "neighbor_makeup", "category": "社交互动",
        "title": "和隔壁和好了",
        "summary": "{name} 主动去找隔壁灵兽道歉，还带了一小袋金币当礼物。",
        "detail": "经过上次吵架后，{name} 意识到自己态度太冲了。它从自己的小金库里数出一小袋金币，叼着来到隔壁灵兽家门口。两只灵兽面对面站了好一会儿，然后同时笑了——友谊就这样在夕阳下修复了。",
        "weight": 3,
        "effect": {"coins": -5, "happiness": 8, "bond": 5},
        "condition": lambda p: p.stage in ("少年", "成年", "巅峰", "传奇", "远古") and p.coins >= 5,
    },
    {
        "key": "gift_from_neighbor", "category": "社交互动",
        "title": "收到邻居的礼物",
        "summary": "隔壁灵兽给 {name} 送来了一份小礼物。",
        "detail": "门口出现了一个小包裹，上面系着隔壁灵兽系的蝴蝶结。{name} 小心翼翼地打开——里面是一块打磨精致的数据碎片，附了一张纸条：'上次吵架的赔礼！别再抢我的地盘啦！'",
        "weight": 5,
        "effect": {"happiness": 6, "item": "data_shard", "qty": 1},
        "condition": lambda p: p.stage not in ("蛋",),
    },
    {
        "key": "teach_dance", "category": "社交互动",
        "title": "教小动物跳舞",
        "summary": "{name} 自告奋勇当起了舞蹈老师，教花园里的小动物们跳舞。",
        "detail": "{name} 在花园里扭来扭去，旁边围了一圈好奇的小动物。虽然它的舞姿……只能说'独特'，但小动物们看得津津有味，还笨拙地跟着学了起来。场面一度非常欢乐。",
        "weight": 6,
        "effect": {"happiness": 7, "bond": 4, "energy": -5},
        "condition": lambda p: p.stage not in ("蛋",),
    },
    {
        "key": "data_plaza_perform", "category": "社交互动",
        "title": "数据广场表演",
        "summary": "{name} 在数据广场即兴表演，吸引了不少围观者。",
        "detail": "数据广场今天特别热闹——{name} 不知从哪里冒了出来，站在广场中央开始了即兴表演。它一会儿翻跟头，一会儿模仿各种动物的叫声，引来一片喝彩。结束时它得意地鞠了一躬。",
        "weight": 3,
        "effect": {"happiness": 12, "bond": 3, "coins": 5, "energy": -8},
        "condition": lambda p: p.stage in ("成年", "巅峰", "传奇", "远古"),
    },

    # ═══ 大类 D：天气事件 (4个) ═══
    {
        "key": "rainy_cold", "category": "天气事件",
        "title": "雨天感冒了",
        "summary": "下了一场数据雨，{name} 没来得及躲，淋了个透心凉。",
        "detail": "突然下起了冰蓝色的数据雨。{name} 正在花园里玩，没来得及跑回屋就被淋透了。它打了个喷嚏，缩成一团发抖。你回来时它用可怜巴巴的眼神看着你，鼻子上还挂着数据雨滴。",
        "weight": 5,
        "effect": {"health": -8, "happiness": -3, "cleanliness": -10},
        "condition": lambda p: p.stage not in ("蛋",),
    },
    {
        "key": "sunny_charge", "category": "天气事件",
        "title": "晒太阳充电",
        "summary": "难得的好天气，{name} 趴在窗台上舒舒服服地晒了半天太阳。",
        "detail": "阳光透过数据结界洒进来，形成一片金色的光斑。{name} 发现了这个完美的位置，趴在上面一动不动地晒了好几个小时。它的毛皮在阳光下闪闪发光，看起来像重新上过油一样锃亮。",
        "weight": 7,
        "effect": {"energy": 10, "happiness": 5, "health": 3},
        "condition": lambda p: p.stage not in ("蛋",),
    },
    {
        "key": "thunder_scared", "category": "天气事件",
        "title": "打雷被吓到了",
        "summary": "一声巨响的雷声把 {name} 吓得钻进了被子里。",
        "detail": "数据世界中突然响起一声惊天动地的雷鸣——是数据风暴过境了。{name} 被吓得跳起来三尺高，然后以光速冲进了卧室，把自己连头带尾地卷进了被子里。它缩在被子里瑟瑟发抖，直到雷声完全消失。",
        "weight": 4,
        "effect": {"happiness": -5, "bond": 3},
        "condition": lambda p: p.stage not in ("蛋",) and p.personality in ("胆小", "温柔"),
    },
    {
        "key": "snow_snowman", "category": "天气事件",
        "title": "堆雪灵兽",
        "summary": "下了一场数据雪，{name} 在院子里堆了一个小小的雪灵兽。",
        "detail": "纯白色的数据雪花纷纷扬扬地飘落，{name} 兴奋极了。它滚了两个大小不一的雪球，拼在一起，又用两颗数据石做眼睛——一个迷你版雪灵兽诞生了！{name} 围着自己的作品转了好几圈，看起来非常自豪。",
        "weight": 4,
        "effect": {"happiness": 10, "energy": -5},
        "condition": lambda p: p.stage not in ("蛋",),
    },

    # ═══ 大类 E：成长事件 (5个) ═══
    {
        "key": "weird_dream", "category": "成长事件",
        "title": "奇怪的梦",
        "summary": "{name} 做了一个很奇怪的梦，醒来后愣了好一会儿。",
        "detail": "{name} 在睡梦中发出了一些奇怪的声音——时而低沉、时而尖细。醒来后它迷迷糊糊地看着四周，仿佛还沉浸在梦中。虽然它说不清梦到了什么，但你能感觉到它的眼神里多了一丝深邃。",
        "weight": 6,
        "effect": {"intelligence": 3, "energy": 3},
        "condition": lambda p: p.stage not in ("蛋",),
    },
    {
        "key": "learn_new_trick", "category": "成长事件",
        "title": "自学成才",
        "summary": "{name} 自己琢磨出了一个新动作！虽然有点笨拙但很可爱。",
        "detail": "你不在的时候，{name} 对着镜子反复练习。它先是试着站起来走路，失败了；然后尝试旋转跳跃，也失败了。最后它发明了一个独一无二的动作——原地转圈三圈后假装晕倒。虽然简单，但它看起来对'自己的原创技能'非常满意。",
        "weight": 5,
        "effect": {"happiness": 6, "intelligence": 3, "bond": 2},
        "condition": lambda p: p.stage not in ("蛋",),
    },
    {
        "key": "mirror_practice", "category": "成长事件",
        "title": "对着镜子练表情",
        "summary": "{name} 不知道从哪里弄来一面镜子，对着镜子练习各种表情。",
        "detail": "你回来时发现 {name} 正对着镜子做鬼脸。它一会儿微笑、一会儿瞪眼、一会儿又把舌头伸出来——然后在镜子里看到了自己的样子后自己也吓了一跳。这台自发的'表情管理课'让它看起来更加有灵气了。",
        "weight": 6,
        "effect": {"happiness": 4, "bond": 2, "intelligence": 2},
        "condition": lambda p: p.stage not in ("蛋",),
    },
    {
        "key": "diary_writing", "category": "成长事件",
        "title": "偷偷写日记",
        "summary": "你发现 {name} 正用歪歪扭扭的字迹在纸上写东西。",
        "detail": "你悄悄走近，发现 {name} 正趴在桌上，用爪子笨拙地握着笔，在纸上写着什么。你凑近一看——上面画着一个歪歪扭扭的你和它，旁边写着（大概是）'今天主人不在，但是我要做一个乖孩子'。看完了，你决定不打扰它。",
        "weight": 5,
        "effect": {"bond": 5, "intelligence": 3},
        "condition": lambda p: p.stage in ("少年", "成年", "巅峰", "传奇", "远古") and p.bond < 70,
    },
    {
        "key": "peek_code", "category": "成长事件",
        "title": "偷看你的代码",
        "summary": "{name} 蹲在屏幕前看了半天你的代码，表情严肃得像个审查员。",
        "detail": "{name} 跳上了你的工作台，目不转睛地盯着屏幕上滚动的代码。它歪着脑袋看了好一会儿，然后用爪子敲了敲键盘——光标刚好停在了一个 bug 旁边。{name} 转头看了你一眼，眼神里满是'你的代码需要优化'的意味。",
        "weight": 4,
        "effect": {"intelligence": 5, "bond": 3, "happiness": 2},
        "condition": lambda p: p.stage in ("成年", "巅峰", "传奇", "远古") and p.intelligence < 70,
    },

    # ═══ 大类 F：物种特色 (5物种各1个，通过 condition 筛选) ═══
    {
        "key": "cat_catch_mouse", "category": "物种特色",
        "title": "抓到了一只数据老鼠！",
        "summary": "{name} 展现了猫型灵兽的本能，成功捕获了一只数据老鼠。",
        "detail": "凌晨三点，{name} 的瞳孔突然放大——它发现了入侵者！一只通体绿色的数据老鼠正在偷吃厨房的零食。{name} 压低身体，尾巴轻轻摆动，然后以惊人的速度扑了上去。战斗持续了五秒钟，最终以数据老鼠被叼到你面前告终。{name} 看起来非常自豪。",
        "weight": 6,
        "effect": {"happiness": 8, "bond": 3, "intelligence": 2},
        "condition": lambda p: p.species_key == "cat" and p.stage not in ("蛋",),
    },
    {
        "key": "cat_keyboard_nest", "category": "物种特色",
        "title": "把键盘当猫窝了",
        "summary": "{name} 趴在了你的键盘上不肯走，说是'这里最暖和'。",
        "detail": "你的键盘散发着微微的热量，对于 {name} 来说简直是完美的猫窝。它跳上去转了三圈，然后把自己卷成一个完美的圆球，闭上了眼睛。你尝试过把它抱走，但它立刻睁开眼睛发出了一声不满的'喵'。最终你只能在旁边用手机打字。",
        "weight": 7,
        "effect": {"happiness": 10, "bond": 5},
        "condition": lambda p: p.species_key == "cat" and p.stage not in ("蛋",),
    },
    {
        "key": "dog_dig_hole", "category": "物种特色",
        "title": "挖了个大坑",
        "summary": "{name} 在花园里挖了一个很深的洞，然后一脸无辜地看着你。",
        "detail": "犬型灵兽的挖掘本能不可阻挡。{name} 在花园角落发现了'宝藏'的气息（实际上是数据线缆），然后开始了疯狂的挖掘。等它停下来时，面前已经出现了一个半米深的大坑。它蹲在坑边，尾巴疯狂摇摆，眼神里写满了'快夸我'。",
        "weight": 6,
        "effect": {"happiness": 8, "energy": -10, "constitution": 2},
        "condition": lambda p: p.species_key == "dog" and p.stage not in ("蛋",),
    },
    {
        "key": "dog_steal_slipper", "category": "物种特色",
        "title": "叼走了你的拖鞋",
        "summary": "你的拖鞋不见了，最后在 {name} 的窝里找到了，已经被当成了枕头。",
        "detail": "又来了。你明确记得拖鞋放在门口，但现在只剩下一只。循着气味，你找到了 {name} 的窝——两只拖鞋整整齐齐地摆在它的枕头旁边，被它当作了某种珍贵收藏品。{name} 看到你发现了它的秘密，立刻用爪子把拖鞋往自己身下藏。",
        "weight": 7,
        "effect": {"happiness": 8, "bond": 4},
        "condition": lambda p: p.species_key == "dog" and p.stage not in ("蛋",),
    },
    {
        "key": "bird_roof_sing", "category": "物种特色",
        "title": "在屋顶唱歌",
        "summary": "{name} 飞到屋顶上，对着夕阳唱了一首'歌'。",
        "detail": "傍晚时分，{name} 扑棱着翅膀飞上了家园的最高处。它仰起头，发出了悠长的鸣叫——虽然用'歌'来形容有点勉强（更像是数据噪音和鸟叫的混合体），但夕阳下的剪影确实很美。邻居灵兽们都安静下来，'欣赏'着这场即兴音乐会。",
        "weight": 6,
        "effect": {"happiness": 10, "bond": 3, "energy": -3},
        "condition": lambda p: p.species_key == "bird" and p.stage not in ("蛋",),
    },
    {
        "key": "bird_steal_seed", "category": "物种特色",
        "title": "偷吃了种子",
        "summary": "{name} 把花园里刚种下的种子啄了个精光。",
        "detail": "你精心播下的种子还没来得及发芽，{name} 就发现了它们。'多好的零食啊！'它心想。于是它一颗一颗地把种子全啄了出来。等它心满意足地打了个饱嗝时，花园的花圃已经被翻了个底朝天。",
        "weight": 5,
        "effect": {"hunger": 12, "happiness": 3, "cleanliness": -5},
        "condition": lambda p: p.species_key == "bird" and p.stage not in ("蛋",) and p.hunger < 50,
    },
    {
        "key": "mech_selfcheck", "category": "物种特色",
        "title": "系统自检完成",
        "summary": "{name} 进行了全面的自检，顺便给自己做了个系统升级。",
        "detail": "{name} 启动了内置诊断程序。一个个检测项在它的屏幕上滚动：机体完整性 ✓、动力系统 ✓、数据存储 ✓、逻辑单元 ✓……所有项目全部通过。它满意地点了点头，然后偷偷给自己打了一个小补丁——'自我优化'完成。",
        "weight": 6,
        "effect": {"intelligence": 5, "constitution": 3, "energy": -5},
        "condition": lambda p: p.species_key == "mech" and p.stage not in ("蛋",),
    },
    {
        "key": "mech_short_circuit", "category": "物种特色",
        "title": "短路了！",
        "summary": "{name} 不小心碰到了水，身体闪了几下火花——但很快就修好了自己。",
        "detail": "{name} 在花园浇水时没注意，数据水流进了它的关节缝隙。'滋滋——啪！'一道蓝白色的火花闪过，{name} 的左眼短暂地熄灭了。但它迅速启动了自我修复程序，三分钟后就恢复了正常。虽然它假装什么都没发生，但你能看到它偷偷避开了所有水源。",
        "weight": 4,
        "effect": {"health": -5, "happiness": -3, "intelligence": 2},
        "condition": lambda p: p.species_key == "mech" and p.stage not in ("蛋",),
    },
    {
        "key": "mystery_portal", "category": "物种特色",
        "title": "打开传送门",
        "summary": "{name} 短暂地打开了一道传送门，窥见了另一个维度的景象。",
        "detail": "{name} 闭上眼睛，额头上的符文开始发出微弱的光芒。空间在它面前扭曲、折叠——一道紫色的裂缝出现了。透过裂缝，隐约可以看到一个由纯数据构成的奇异世界。然而裂缝只持续了几秒就闭合了。{name} 睁开眼，若有所思。",
        "weight": 3,
        "effect": {"intelligence": 8, "energy": -10, "bond": 2},
        "condition": lambda p: p.species_key == "mystery" and p.stage in ("成年", "巅峰", "传奇", "远古"),
    },
    {
        "key": "mystery_future", "category": "物种特色",
        "title": "读取了未来碎片",
        "summary": "{name} 的天赋让它捕捉到了来自未来的数据碎片。",
        "detail": "时间之流在 {name} 的感知中偶尔会出现裂痕。今天它触碰到了其中一道——碎片般的未来影像在它脑海中闪过：你和它在星空下并肩而立，周围漂浮着无数光点。画面转瞬即逝，但那份温暖的感觉留了下来。",
        "weight": 2,
        "effect": {"intelligence": 5, "bond": 5, "happiness": 5},
        "condition": lambda p: p.species_key == "mystery" and p.stage in ("巅峰", "传奇", "远古"),
    },
]


class DailyEventSystem:
    """日常事件系统 — 离线事件生成与应用"""

    def __init__(self, session: Session):
        self.session = session

    def check_and_generate(self, pet: Pet) -> list[dict]:
        """
        检查离线时长，生成日常事件。
        - 离线超过30分钟才有事件
        - 最多积累24小时的离线时间
        - 每小时最多1个事件
        - 最多生成5个未读事件

        返回本次新生成的事件列表。
        """
        now = datetime.now(timezone.utc)
        last = pet.last_updated
        if last.tzinfo is None:
            last = last.replace(tzinfo=timezone.utc)

        offline_minutes = (now - last).total_seconds() / 60.0

        # 离线不足30分钟不触发
        if offline_minutes < 30:
            return []

        # 最多24小时
        offline_minutes = min(offline_minutes, 24 * 60)

        # 已有未读事件数
        existing_unread = (
            self.session.query(DailyEventLog)
            .filter_by(pet_id=pet.id, read=False)
            .count()
        )

        # 最多积累5个未读
        remaining_slots = 5 - existing_unread
        if remaining_slots <= 0:
            return []

        # 每小时1个事件
        event_count = int(offline_minutes // 60)
        event_count = min(event_count, remaining_slots)

        events = []
        for _ in range(event_count):
            event = self.generate_event(pet)
            if event:
                events.append(event)

        return events

    def generate_event(self, pet: Pet) -> dict | None:
        """根据条件加权随机选择一个事件，应用效果并记录日志"""
        # 筛选满足条件的事件
        eligible = []
        for ev in DAILY_EVENTS:
            cond = ev.get("condition", lambda p: True)
            try:
                if cond(pet):
                    eligible.append(ev)
            except Exception:
                continue

        if not eligible:
            return None

        # 加权随机选择
        weights = [e.get("weight", 5) for e in eligible]
        chosen = random.choices(eligible, weights=weights, k=1)[0]

        # 应用效果
        result = self._apply_event(pet, chosen)

        # 记录日志
        log = DailyEventLog(
            pet_id=pet.id,
            event_key=chosen["key"],
            category=chosen["category"],
            title=chosen["title"],
            summary=chosen["summary"].format(name=pet.name),
            detail=chosen["detail"].format(name=pet.name),
            result=result,
            occurred_at=datetime.now(timezone.utc),
        )
        self.session.add(log)
        self.session.commit()

        return {
            "key": chosen["key"],
            "category": chosen["category"],
            "title": chosen["title"],
            "summary": chosen["summary"].format(name=pet.name),
            "detail": chosen["detail"].format(name=pet.name),
            "result": result,
        }

    def _apply_event(self, pet: Pet, event: dict) -> dict:
        """应用事件效果到宠物属性"""
        effect = event["effect"]
        actual = {}

        if "coins" in effect:
            amt = effect["coins"]
            pet.coins = max(0, pet.coins + amt)
            actual["coins"] = amt
        if "stardust" in effect:
            amt = effect["stardust"]
            pet.stardust = max(0, pet.stardust + amt)
            actual["stardust"] = amt

        # 属性变化
        stat_map = {
            "hunger": "hunger", "happiness": "happiness",
            "cleanliness": "cleanliness", "health": "health",
            "energy": "energy", "intelligence": "intelligence",
            "bond": "bond", "constitution": "constitution",
        }
        for stat_key, attr in stat_map.items():
            if stat_key in effect:
                val = effect[stat_key]
                cur = getattr(pet, attr, 0.0)
                setattr(pet, attr, max(0.0, min(100.0, cur + val)))
                actual[stat_key] = val

        # 物品
        if "item" in effect:
            item = self.session.query(Item).filter_by(key=effect["item"]).first()
            if item:
                qty = effect.get("qty", 1)
                inv = self.session.query(Inventory).filter_by(
                    pet_id=pet.id, item_id=item.id
                ).first()
                if inv:
                    inv.quantity += qty
                else:
                    inv = Inventory(pet_id=pet.id, item_id=item.id, quantity=qty)
                    self.session.add(inv)
                actual["item"] = f"{item.name}×{qty}"

        return actual

    def get_unread_events(self, pet: Pet) -> list[DailyEventLog]:
        """获取未读的日常事件"""
        return (
            self.session.query(DailyEventLog)
            .filter_by(pet_id=pet.id, read=False)
            .order_by(DailyEventLog.occurred_at.desc())
            .all()
        )

    def get_all_events(self, pet: Pet, limit: int = 20) -> list[DailyEventLog]:
        """获取最近的日常事件"""
        return (
            self.session.query(DailyEventLog)
            .filter_by(pet_id=pet.id)
            .order_by(DailyEventLog.occurred_at.desc())
            .limit(limit)
            .all()
        )

    def mark_read(self, pet: Pet, event_id: int) -> DailyEventLog | None:
        """标记指定事件为已读"""
        log = self.session.query(DailyEventLog).filter_by(
            id=event_id, pet_id=pet.id
        ).first()
        if log:
            log.read = True
            self.session.commit()
        return log

    def mark_all_read(self, pet: Pet) -> int:
        """标记所有未读事件为已读，返回标记数量"""
        count = (
            self.session.query(DailyEventLog)
            .filter_by(pet_id=pet.id, read=False)
            .update({DailyEventLog.read: True})
        )
        self.session.commit()
        return count
