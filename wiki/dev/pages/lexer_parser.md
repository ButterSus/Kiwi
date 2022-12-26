@page lexer_parser Лексер и Парсер

![](https://external-content.duckduckgo.com/iu/?u=http%3A%2F%2Fi.gyazo.com%2Fcd67bb2f01c3e47aa0f07dea2e2adcb8.png&f=1&nofb=1&ipt=bea3d5b742476a99be259f8162322ec645ae1df163c2c7469d9a182f762559fb&ipo=images)

Они официально зовутся как ***лексический анализатор*** и ***синтаксический анализатор / парсер***.
(см. в Wikipedia [Лексика](https://en.wikipedia.org/wiki/Lexical_analysis))
а так же [Синтаксис/Парсер](https://en.wikipedia.org/wiki/Parsing)

**Лексер** (синоним **токенайзер**) берёт строку, разделяет его на более детальные **токены**.
Если вам стало интересно узнать как он у меня работает, то могу сказать
что собственного лексера у меня нету, я использую _питоновский лексер_.
Можете кстати [поэксперементировать с ним](https://docs.python.org/3/library/tokenize.html#examples).

**Парсер** берёт **токены** и генерирует дерево. Кратко могу сказать, что
сейчас парсеры никто почти вручную не пишет, вместо этого используются
специальные языки описания грамматики, такие как **EBNF**.

Я же использую язык описания грамматики **pegen**, который по сути является
улучшенной грамматикой языка **Python**, эта фиговинка затем генерит такой [код](https://github.com/ButterSus/Kiwi/blob/master/Kiwi/kiwiAST.py).

Кому интересно вот [грамматика всего языка Kiwi](https://github.com/ButterSus/Kiwi/blob/master/Kiwi/components/kiwi.gram).
Она написана в **600 строк**.

В итоге вместе они генерят такую фиговинку:

![](assets/img.png)

из этого кода:

@kiwicode
namespace Math:
    a: score

    function sus():
        a: scoreboard
@endkiwicode

Согласитесь, эту штуку _несложно читать_. Она нужна чтобы потом из этого дерева (она так называется
потому что корнями углубляется вглубь, у меня глубина через отступы задаётся) сделать анализ (ниже описано).

Польза от этой штуковины огроменна, благодаря этому дереву вы можете не париться с обработкой ключевых
слов, париться с тем чтобы обрабатывать скобки, отступы и.т.д.

Все эти **элементы** (_давайте их так называть_) вместе составляют структуру.
Парочка возможно ~~полезных~~ может быть нужных фактов:
- Это **Python объекты**, наследуются от класса `AST`.
- Все они являются **датаклассами**.
- Для импорта этих фиговинок я обычно делаю так `import Kiwi.components.kiwiASO as kiwi`,
чтобы затем писать как-то так `some_elem: kiwi.FuncDef`

Вот пример одного из элементов:

```py
@dataclass  # Декоратор датаклассов
class FuncDef(Theme_CStatements, AST):  # Объявляем новый вид элемента
    name: Name
    params: List[Parameter | RefParameter]
    default: List[expression]
    returns: ReturnParameter | ReturnRefParameter
    promiser: expression
    body: List[statement]
# Theme_CStatements нужен просто чтобы в чате он был цветным)
```

Аналогичным образом написаны все остальные элементы

Надеюсь на этом этапе у вас возникло минимум вопросов, потому что с этой фиговиной вам даже работать
не придётся, *можете забить болт*!