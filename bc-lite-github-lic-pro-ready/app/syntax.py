from PySide6.QtGui import QSyntaxHighlighter, QTextCharFormat, QColor, QFont
from PySide6.QtCore import QRegularExpression

def _fmt(color: str, bold: bool = False, italic: bool = False) -> QTextCharFormat:
    f = QTextCharFormat()
    f.setForeground(QColor(color))
    if bold:
        f.setFontWeight(QFont.Bold)
    if italic:
        f.setFontItalic(True)
    return f

def detect_language_from_suffix(suffix: str) -> str:
    s = suffix.lower().lstrip(".")
    if s in ("py", "pyw"):
        return "python"
    if s in ("c", "h"):
        return "c"
    if s in ("cpp", "cxx", "cc", "hpp", "hh"):
        return "cpp"
    if s in ("js", "jsx", "ts", "tsx"):
        return "js"
    if s in ("java",):
        return "java"
    if s in ("json",):
        return "json"
    if s in ("xml", "html", "htm"):
        return "xml"
    return "plain"

class CodeHighlighter(QSyntaxHighlighter):
    def __init__(self, document, language: str = "plain"):
        super().__init__(document)
        self.language = language
        self.rules = []
        self.comment_format = None
        self._build_rules()

    def _add_rules(self, patterns, fmt: QTextCharFormat):
        for pat in patterns:
            self.rules.append((QRegularExpression(pat), fmt))

    def _build_rules(self):
        lang = self.language

        if lang == "python":
            keyword_fmt = _fmt("#569CD6", bold=True)
            keywords = [
                r"\band\b", r"\bas\b", r"\bassert\b", r"\bbreak\b", r"\bclass\b",
                r"\bcontinue\b", r"\bdef\b", r"\bdel\b", r"\belif\b", r"\belse\b",
                r"\bexcept\b", r"\bFalse\b", r"\bfinally\b", r"\bfor\b", r"\bfrom\b",
                r"\bglobal\b", r"\bif\b", r"\bimport\b", r"\bin\b", r"\bis\b",
                r"\blambda\b", r"\bNone\b", r"\bnonlocal\b", r"\bnot\b", r"\bor\b",
                r"\bpass\b", r"\braise\b", r"\breturn\b", r"\bTrue\b", r"\btry\b",
                r"\bwhile\b", r"\bwith\b", r"\byield\b",
            ]
            self._add_rules(keywords, keyword_fmt)

            builtin_fmt = _fmt("#4EC9B0")
            builtins = [r"\bprint\b", r"\blen\b", r"\brange\b", r"\benumerate\b", r"\bopen\b"]
            self._add_rules(builtins, builtin_fmt)

            string_fmt = _fmt("#CE9178")
            self._add_rules([r"\".*?\"", r"'.*?'"], string_fmt)

            self.comment_format = _fmt("#6A9955", italic=True)

        elif lang in ("c", "cpp", "java", "js"):
            keyword_fmt = _fmt("#569CD6", bold=True)
            keywords = [
                r"\bauto\b", r"\bbool\b", r"\bbreak\b", r"\bcase\b", r"\bchar\b",
                r"\bconst\b", r"\bcontinue\b", r"\bdefault\b", r"\bdo\b", r"\bdouble\b",
                r"\belse\b", r"\benum\b", r"\bextern\b", r"\bfloat\b", r"\bfor\b",
                r"\bgoto\b", r"\bif\b", r"\binline\b", r"\bint\b", r"\blong\b",
                r"\bregister\b", r"\brestrict\b", r"\breturn\b", r"\bshort\b", r"\bsigned\b",
                r"\bsizeof\b", r"\bstatic\b", r"\bstruct\b", r"\bswitch\b", r"\btypedef\b",
                r"\bunion\b", r"\bunsigned\b", r"\bvoid\b", r"\bvolatile\b", r"\bwhile\b",
                r"\bclass\b", r"\bpublic\b", r"\bprivate\b", r"\bprotected\b", r"\btemplate\b",
                r"\busing\b", r"\bnamespace\b", r"\bnew\b", r"\bdelete\b", r"\bthis\b",
                r"\bvirtual\b", r"\boverride\b",
            ]
            self._add_rules(keywords, keyword_fmt)

            string_fmt = _fmt("#CE9178")
            self._add_rules([r"\".*?\"", r"'.*?'"], string_fmt)

            self.comment_format = _fmt("#6A9955", italic=True)

        elif lang == "json":
            key_fmt = _fmt("#9CDCFE", bold=True)
            self._add_rules([r'"[^"]*"\s*:'], key_fmt)
            str_fmt = _fmt("#CE9178")
            self._add_rules([r'".*?"'], str_fmt)

        elif lang == "xml":
            tag_fmt = _fmt("#569CD6", bold=True)
            self._add_rules([r"</?\\w+[^>]*>"], tag_fmt)

        # numbers
        num_fmt = _fmt("#B5CEA8")
        self._add_rules([r"\\b[0-9]+\\b"], num_fmt)

    def highlightBlock(self, text: str):
        for pattern, fmt in self.rules:
            it = pattern.globalMatch(text)
            while it.hasNext():
                m = it.next()
                self.setFormat(m.capturedStart(), m.capturedLength(), fmt)

        # simple line comments
        if self.comment_format and self.language in ("python", "c", "cpp", "java", "js"):
            if self.language == "python":
                idx = text.find("#")
            else:
                idx = text.find("//")
            if idx >= 0:
                self.setFormat(idx, len(text) - idx, self.comment_format)
