import os, struct, zlib
from kivy.app import App
from kivy.clock import Clock
from kivy.core.text import LabelBase
from kivy.core.window import Window
from kivy.lang import Builder
from kivy.utils import escape_markup, platform

if platform == "android":
    from androidstorage4kivy import Chooser, SharedStorage

BASE = os.path.dirname(os.path.abspath(__file__))
FONT = os.path.join(BASE, "assets", "Poins.ttf")  # ganti jika nama file fontmu beda
if os.path.exists(FONT):
    LabelBase.register(name="Roboto", fn_regular=FONT)  # jadi font default semua widget

Window.clearcolor = (1, 1, 1, 1)

KV = """
#:import dp kivy.metrics.dp

<PrimaryButton@Button>:
    background_normal: ''
    background_down: ''
    background_color: 0, 0, 0, 0
    color: 1, 1, 1, 1
    font_size: '16sp'
    canvas.before:
        Color:
            rgba: (0.145, 0.388, 0.922, 1) if self.state == 'normal' else (0.114, 0.306, 0.847, 1)
        RoundedRectangle:
            pos: self.pos
            size: self.size
            radius: [dp(14)]

<GhostButton@Button>:
    background_normal: ''
    background_down: ''
    background_color: 0, 0, 0, 0
    color: 0.22, 0.25, 0.32, 1
    font_size: '14sp'
    canvas.before:
        Color:
            rgba: 0.85, 0.87, 0.9, 1
        Line:
            rounded_rectangle: (self.x, self.y, self.width, self.height, dp(14))
            width: 1.2

BoxLayout:
    orientation: 'vertical'
    padding: dp(20), dp(36), dp(20), dp(20)
    spacing: dp(16)
    BoxLayout:
        orientation: 'vertical'
        size_hint_y: None
        height: dp(70)
        Label:
            text: 'CONVERTER'
            color: 0.07, 0.09, 0.15, 1
            font_size: '28sp'
            halign: 'left'
            valign: 'bottom'
            text_size: self.size
        Label:
            text: 'Konversi .pvr dan .pvr.ccz'
            color: 0.42, 0.45, 0.5, 1
            font_size: '14sp'
            halign: 'left'
            valign: 'top'
            text_size: self.size
    BoxLayout:
        padding: dp(16)
        canvas.before:
            Color:
                rgba: 0.953, 0.957, 0.965, 1
            RoundedRectangle:
                pos: self.pos
                size: self.size
                radius: [dp(18)]
        ScrollView:
            do_scroll_x: False
            Label:
                id: log
                markup: True
                size_hint_y: None
                height: max(self.texture_size[1], dp(24))
                text_size: self.width, None
                halign: 'left'
                valign: 'top'
                font_size: '14sp'
                color: 0.22, 0.25, 0.32, 1
    PrimaryButton:
        text: 'Pilih File'
        size_hint_y: None
        height: dp(56)
        on_release: app.pick()
    GhostButton:
        text: 'Bersihkan'
        size_hint_y: None
        height: dp(44)
        on_release: app.clear()
"""

COLOR = {"ok": "16A34A", "err": "DC2626", "skip": "6B7280"}
EMPTY = "[color=6B7280]Belum ada file. Tekan Pilih File untuk mulai.[/color]"


def convert(path):
    """Arah konversi otomatis dari nama file. Return (path_hasil, jenis, pesan)."""
    name = os.path.basename(path)
    folder = os.path.dirname(path)
    low = name.lower()
    with open(path, "rb") as f:
        d = f.read()
    if low.endswith(".pvr.ccz"):
        if d[:4] != b"CCZ!":
            return None, "skip", "Dilewati (bukan CCZ!, mungkin terenkripsi): " + name
        out = os.path.join(folder, name[:-4])
        data = zlib.decompress(d[16:])
    elif low.endswith(".pvr"):
        out = os.path.join(folder, name + ".ccz")
        data = b"CCZ!" + struct.pack(">HHII", 0, 2, 0, len(d)) + zlib.compress(d)
    else:
        return None, "skip", "Dilewati (bukan .pvr / .pvr.ccz): " + name
    with open(out, "wb") as f:
        f.write(data)
    return out, "ok", "%s  >  %s" % (name, os.path.basename(out))


class ConverterApp(App):
    title = "CONVERTER"

    def build(self):
        self.ui = Builder.load_string(KV)
        self.lines = []
        self.ui.ids.log.text = EMPTY
        if platform == "android":
            self.chooser = Chooser(self.on_chosen)
        return self.ui

    def add(self, kind, msg):
        self.lines.append("[color=%s]%s[/color]" % (COLOR[kind], escape_markup(msg)))
        self.ui.ids.log.text = "\n".join(self.lines)

    def clear(self):
        self.lines = []
        self.ui.ids.log.text = EMPTY

    def pick(self):
        if platform == "android":
            self.chooser.choose_content("*/*", multiple=True)
        else:
            self.add("err", "Aplikasi ini hanya untuk Android.")

    def on_chosen(self, uris):
        Clock.schedule_once(lambda dt: self.handle(uris))

    def handle(self, uris):
        ss = SharedStorage()
        ok = 0
        for uri in uris or []:
            try:
                out, kind, msg = convert(ss.copy_from_shared(uri))
                if out:
                    ss.copy_to_shared(out)
                    ok += 1
                self.add(kind, msg)
            except Exception as e:
                self.add("err", "Gagal: %s" % e)
        self.add("ok" if ok else "skip", "Selesai: %d file berhasil. Hasil di folder Documents." % ok)


ConverterApp().run()
