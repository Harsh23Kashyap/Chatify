"""Branded multipage PDF and Markdown exports for an answer, plus BibTeX.

The PDF uses bundled Noto Sans, Noto Sans Devanagari, Noto Naskh Arabic,
Noto Sans Hebrew, Noto Sans Symbols, Noto Sans Symbols 2 and Noto Sans Math
fonts (SIL Open Font License 1.1, see web/fonts/OFL.txt) with HarfBuzz
shaping, so ordinary Unicode answer text - including Hindi, Arabic and Hebrew -
exports as itself instead of being folded or rejected. RTL-dominant paragraphs
render right-aligned with RTL shaping. Scripts outside the bundled fonts
(CJK, Thai, ...) are still rejected honestly.
"""
import os, re, unicodedata
try:
    from fpdf import FPDF
except ImportError:  # optional dependency: wheel installs without the pdf extra
    FPDF = None

from .pipeline import plain_text as _plain


def _k(e, i):
    a = (str(e.get("authors",[])[0]).split()[-1] if e.get("authors") and str(e["authors"][0]).split() else "anon")
    return re.sub(r"\W", "", a) + str(e.get("year") or "nd") + str(i)


def bibtex(evidence):
    out = []
    for i, e in enumerate(evidence, 1):
        f = {"title": e.get("title",""), "author": " and ".join(map(str,e.get("authors") or [])), "year": str(e.get("year") or ""), "journal": e.get("venue",""), "url": e.get("url","")}
        body = ",\n".join("  %s = {%s}" % (k, re.sub(r"[{}]", "", v)) for k, v in f.items() if v)
        out.append("@article{%s,\n%s\n}" % (_k(e, i), body))
    return "\n\n".join(out) + "\n"


def snapshot(e):
    return " · ".join(str(x) for x in [e.get("document"), "page "+str(e["page"]) if e.get("page") else e.get("section"), "version "+str(e["version"]) if e.get("version") else "", "OCR" if e.get("ocr") else ""] if x)


def source_note(errors, sources):
    """The source-skip explanation the chat UI shows, for exports: which sources
    could not search and why (live-demo gap 2026-10-25: exports showed passages
    without saying sources had been skipped)."""
    if not isinstance(errors, dict) or not errors:
        return ""
    labels = {str(s.get("id")): str(s.get("label") or s.get("id")) for s in (sources or []) if isinstance(s, dict)}
    items = [(str(k), v) for k, v in errors.items()]
    all_failed = len(items) >= max(1, len(sources or []))
    # A sentence-valued error names the concrete cause; a bare exception type
    # name stays behind the generic wording (mirrors the chat UI note).
    named = ["%s: %s" % (labels.get(sid, sid), str(msg).strip()) for sid, msg in items if isinstance(msg, str) and " " in msg]
    if named:
        return " ".join(named) + ("" if all_failed else " Answered from the other sources.")
    return ", ".join(labels.get(sid, sid) for sid, _ in items) + " could not be reached" + (" for this question." if all_failed else " - answered from the other sources.")


def answer_markdown(app,turn,sources=None):
    out=["# "+app.get("title","Chat"),app.get("tagline",""),"", "## Question",turn['question'],"", "## Answer",turn['answer']]
    note=source_note(turn.get('source_errors'),sources if sources is not None else app.get('sources'))
    if note:out+=["",note]
    out+=["", "## Sources at answer time"]
    for i,e in enumerate(turn['evidence'],1):
        out += ["[%d] %s" % (e.get('n',i),_plain(e['title'])),e.get('url') or '',snapshot(e),""]
    out += ["Source versions are snapshots at answer time. They are not a guarantee the linked document is unchanged."]
    return "\n".join(out)


_FONTS=os.path.join(os.path.dirname(os.path.abspath(__file__)),'web','fonts')
_COVERAGE=None
def _covered_chars():
    global _COVERAGE
    if _COVERAGE is None:
        from fontTools.ttLib import TTFont
        cov=set()
        for name in ('NotoSans-Regular.ttf','NotoSans-Bold.ttf','NotoSansDevanagari-Regular.ttf','NotoSansDevanagari-Bold.ttf','NotoNaskhArabic[wght].ttf','NotoSansHebrew[wdth,wght].ttf','NotoSansSymbols-Regular.ttf','NotoSansSymbols2-Regular.ttf','NotoSansMath-Regular.ttf'):
            cov|=set(TTFont(os.path.join(_FONTS,name)).getBestCmap())
        _COVERAGE=cov
    return _COVERAGE

# Joiners and variation selectors are consumed by the shaper, not drawn alone.
_EXEMPT={'\u200c','\u200d','\ufe0f','\ufeff','\u00ad'}
def _check_representable(blocks):
    cov=_covered_chars()
    for _,value in blocks:
        for ch in value:
            if ch in _EXEMPT or unicodedata.combining(ch):continue
            if ord(ch) not in cov:raise ValueError('PDF font cannot represent this text. Download Markdown for full Unicode.') from None

_RTL_STRONG = frozenset(("R", "AL"))
def _rtl_dominant(text):
    """Strong-direction vote: a paragraph whose strong characters are mostly
    Arabic/Hebrew renders right-aligned; the shaper guesses script/direction
    per run, so only alignment needs the vote here."""
    rtl = ltr = 0
    for ch in text:
        b = unicodedata.bidirectional(ch)
        if b in _RTL_STRONG:
            rtl += 1
        elif b == "L":
            ltr += 1
    return rtl > ltr


class _AnswerPDF(FPDF if FPDF is not None else object):
    def __init__(self,doc_title,accent):
        super().__init__(unit='pt',format='A4')
        self._doc_title=doc_title
        self._accent=accent
        self.set_margins(50,50,86)
        self.set_auto_page_break(True,82)
        for family,style,filename in [('noto','','NotoSans-Regular.ttf'),('noto','B','NotoSans-Bold.ttf'),('deva','','NotoSansDevanagari-Regular.ttf'),('deva','B','NotoSansDevanagari-Bold.ttf'),('symbols','','NotoSansSymbols-Regular.ttf'),('symbols2','','NotoSansSymbols2-Regular.ttf'),('math','','NotoSansMath-Regular.ttf')]:
            self.add_font(family,style,os.path.join(_FONTS,filename))
        # Arabic and Hebrew ship as variable fonts (leaner than static families);
        # instantiate regular/bold at load (fpdf2 variations=).
        self.add_font('arab','',os.path.join(_FONTS,'NotoNaskhArabic[wght].ttf'),variations={'wght':400})
        self.add_font('arab','B',os.path.join(_FONTS,'NotoNaskhArabic[wght].ttf'),variations={'wght':700})
        self.add_font('hebr','',os.path.join(_FONTS,'NotoSansHebrew[wdth,wght].ttf'),variations={'wght':400,'wdth':100})
        self.add_font('hebr','B',os.path.join(_FONTS,'NotoSansHebrew[wdth,wght].ttf'),variations={'wght':700,'wdth':100})
        self.set_fallback_fonts(['deva','arab','hebr','symbols','symbols2','math'])
        self.set_text_shaping(True)
        self.set_title(doc_title)
    def header(self):
        self.set_fill_color(248,244,233);self.rect(0,0,595,842,'F')
        self.set_fill_color(*self._accent);self.rect(50,44,36,3,'F')
    def footer(self):
        self.set_draw_color(217,224,214);self.set_line_width(0.5);self.line(50,783,545,783)
        self.set_font('noto','',8);self.set_text_color(99,115,107)
        self.set_xy(50,790);self.cell(0,12,'%s | %d / {nb}'%(self._doc_title[:60],self.page_no()))

def chat_markdown(title, turns, sources=None):
    out = ["# " + title, ""]
    for t in turns:
        out += ["**Q:** " + t["question"], "", t["answer"], ""]
        note = source_note(t.get("source_errors"), sources)
        if note:
            out += [note, ""]
        for i, e in enumerate(t["evidence"], 1):
            out.append("%d. %s%s" % (i, _plain(e["title"]), " <%s>" % e["url"] if e["url"] else ""))
        out.append("")
    return "\n".join(out)


def pdf_bytes(title, turn, accent="#173f35", tagline="", sources=None):
    if FPDF is None:
        raise RuntimeError("PDF export needs the pdf extra: pip install 'chatify[documents]'.")
    blocks=[('label','ANSWER NOTE'),('title',title),('muted',tagline),('space',''),('label','YOUR QUESTION'),('question',turn['question']),('space',''),('heading','Answer')]
    # Recompose markdown tables into readable labeled rows for narrow PDF pages.
    lines=turn['answer'].split('\n');i=0
    cells=lambda line:[x.strip().replace('\\|','|') for x in re.split(r'(?<!\\)\|',line.strip().strip('|'))]
    while i<len(lines):
        line=lines[i]
        if '|' in line and i+1<len(lines) and re.match(r'^\s*\|?\s*:?-{3,}',lines[i+1]):
            headers=cells(line);i+=2
            while i<len(lines) and '|' in lines[i]:
                values=cells(lines[i])
                # Malformed rows stay literal rather than dropping cells or prose.
                if len(values)!=len(headers):
                    blocks.append(('body',lines[i]));i+=1;break
                blocks.append(('body','; '.join('%s: %s'%(h,values[n]) for n,h in enumerate(headers))));i+=1
            continue
        blocks.append(('body',line) if line else ('space',''));i+=1
    note=source_note(turn.get('source_errors'),sources)
    if note:blocks += [('space',''),('muted',note)]
    blocks += [('space',''),('heading','Sources at answer time')]
    for i,e in enumerate(turn['evidence'],1):
        blocks += [('source','[%d] %s'%(e.get('n',i),_plain(e['title']))),('muted',snapshot(e).replace(' · ',' | ')),('muted',e.get('url') or ''),('space','')]
    blocks += [('muted','Source versions are snapshots. Linked documents may change.')]
    # Bundled Noto Sans + Noto Sans Devanagari (SIL OFL 1.1) with HarfBuzz
    # shaping cover ordinary generated answer text, including Hindi. Scripts the
    # bundled fonts do not cover stay an honest rejection rather than silent
    # .notdef boxes; Markdown keeps full Unicode for those.
    _check_representable(blocks)
    if not re.fullmatch(r'#[0-9a-fA-F]{6}',accent):accent='#173f35'
    rgb=tuple(int(accent[i:i+2],16) for i in (1,3,5))
    # (style, size, block line pitch, color) - mirrors the former hand-rolled
    # layout: same paper, margins, pitch and palette, now real Unicode fonts.
    ink=(23,36,31);mut=(99,115,107)
    styles={'label':('B',8,36,rgb),'title':('B',30,38,rgb),'heading':('B',20,30,rgb),'question':('B',16,24,ink),'body':('',11,17,ink),'source':('B',10,17,rgb),'muted':('',9,14,mut)}
    pdf=_AnswerPDF(str(title)[:120],rgb)
    pdf.add_page()
    for bi,(kind,text) in enumerate(blocks):
        if kind=='space':pdf.ln(14);continue
        style,size,pitch,color=styles[kind]
        pdf.set_font('noto',style,size);pdf.set_text_color(*color)
        if kind=='heading':
            # Keep a heading with what it introduces: when the heading plus the
            # first following block no longer fit, break before the heading
            # (live R5 review 2026-10-25: "Sources at answer time" sat orphaned
            # at the bottom of page 1 while its first source opened page 2).
            nxt=next((b for b in blocks[bi+1:] if b[0]!='space'),None)
            need=6+2*pitch
            if nxt:
                ns,nsz,npit,_=styles[nxt[0]]
                pdf.set_font('noto',ns,nsz)
                import math as _m
                need+=npit*max(1,_m.ceil(pdf.get_string_width(nxt[1] or ' ')/495))
                pdf.set_font('noto',style,size)
            if pdf.get_y()+need>pdf.page_break_trigger:pdf.add_page()
            y=pdf.get_y();pdf.set_draw_color(217,224,214);pdf.set_line_width(0.5);pdf.line(50,y+2,545,y+2);pdf.set_y(y+6)
        if kind=='source':
            # Keep one source entry (title + snapshot + URL) on a single page when
            # it fits: an orphaned title fragment reads as a broken export (hosted
            # R2 review 2026-10-25: "[2] ...boldly go where no other therapy has"
            # ended page 1 and "gone before." opened page 2).
            import math as _m
            need=0
            for bk,btxt in blocks[bi:]:
                if bk=='space':break
                bs,bsz,bpit,_=styles[bk]
                pdf.set_font('noto',bs,bsz)
                need+=bpit*max(1,_m.ceil(pdf.get_string_width(btxt or ' ')/495))
            pdf.set_font('noto',style,size)
            if need<=pdf.page_break_trigger-50 and pdf.get_y()+need>pdf.page_break_trigger:pdf.add_page()
        # Left-aligned text avoids the wide inter-word gaps justification opens
        # in narrow answer bullets (R5 PDF review 2026-10-25). RTL-dominant
        # paragraphs anchor right instead; the shaper reorders the runs.
        pdf.multi_cell(0,pitch,text,new_x='LMARGIN',new_y='NEXT',align='R' if _rtl_dominant(text) else 'L')
    return bytes(pdf.output())
