"""BibTeX and a dependency-free branded, multipage PDF for an answer."""
import re, textwrap


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


def _pdf_escape(s):
    return s.encode("cp1252", "replace").decode("cp1252").replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")


def snapshot(e):
    return " · ".join(str(x) for x in [e.get("document"), "page "+str(e["page"]) if e.get("page") else e.get("section"), "version "+str(e["version"]) if e.get("version") else "", "OCR" if e.get("ocr") else ""] if x)


def answer_markdown(app,turn):
    out=["# "+app.get("title","Chat"),app.get("tagline",""),"", "## Question",turn['question'],"", "## Answer",turn['answer'],"", "## Sources at answer time"]
    for i,e in enumerate(turn['evidence'],1):
        out += ["[%d] %s" % (e.get('n',i),e['title']),e.get('url') or '',snapshot(e),""]
    out += ["Source versions are snapshots at answer time. They are not a guarantee the linked document is unchanged."]
    return "\n".join(out)


def pdf_bytes(title, turn, accent="#173f35", tagline=""):
    # Latin-1 standard fonts; reject unsupported glyphs rather than losing text.
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
    blocks += [('space',''),('heading','Sources at answer time')]
    for i,e in enumerate(turn['evidence'],1):
        blocks += [('source','[%d] %s'%(e.get('n',i),e['title'])),('muted',snapshot(e).replace(' · ',' | ')),('muted',e.get('url') or ''),('space','')]
    blocks += [('muted','Source versions are snapshots. Linked documents may change.')]
    # WinAnsi (cp1252) covers typographic punctuation used by model answers; common
    # symbols outside it get readable text equivalents, everything else stays an
    # honest rejection instead of silent replacement.
    _PDF_TRANSLATE=str.maketrans({'\u20b9':'Rs. ','\u2192':'->','\u2190':'<-','\u2191':'^','\u2193':'v','\u2713':'[ok]','\u2714':'[ok]','\u2717':'[x]','\u2718':'[x]','\u26a0':'!','\u2605':'*','\u2606':'*','\u2026':'...','\u200d':'','\ufe0f':''})
    blocks=[(kind,value.translate(_PDF_TRANSLATE)) for kind,value in blocks]
    try:'\n'.join(v for _,v in blocks).encode('cp1252')
    except UnicodeEncodeError:raise ValueError('PDF font cannot represent this text. Download Markdown for full Unicode.') from None
    if not re.fullmatch(r'#[0-9a-fA-F]{6}',accent):accent='#173f35'
    rgb=' '.join('%.3f'%(int(accent[i:i+2],16)/255) for i in (1,3,5))
    styles={'label':('F3',8,36,rgb,88),'title':('F2',30,38,rgb,32),'heading':('F2',20,30,rgb,48),'question':('F2',16,24,'0.09 0.14 0.12',54),'body':('F1',11,17,'0.09 0.14 0.12',78),'source':('F3',10,17,rgb,80),'muted':('F1',9,14,'0.39 0.45 0.42',92)}
    pages=[];commands=[];y=762
    for kind,text in blocks:
        if kind=='space':y-=14;continue
        font,size,leading,color,width=styles[kind]
        rows=textwrap.wrap(text,width,replace_whitespace=False) or ['']
        # A character count alone overflows for wide glyphs. Conservative widths
        # keep arbitrary source titles and long unbroken words on the page.
        def points(value):
            return sum(size * (1 if c in "MW@%" or ord(c)>127 else .28 if c in " ilI.,:;!|'" else .6) for c in value)
        safe=[]
        for row in rows:
            while points(row)>495:
                cut=1
                while cut<len(row) and points(row[:cut+1])<=495:cut+=1
                space=row.rfind(' ',0,cut+1)
                if space>0:cut=space
                safe.append(row[:cut]);row=row[cut:].lstrip()
            safe.append(row)
        rows=safe
        if kind in ('heading','label') and y<130:pages.append(commands);commands=[];y=756
        for row in rows:
            if y<82:pages.append(commands);commands=[];y=756
            if kind=='heading' and row==rows[0]:commands.append('0.85 0.88 0.86 RG 0.5 w 50 %d m 545 %d l S'%(y+17,y+17))
            commands.append('%s rg BT /%s %d Tf 50 %d Td (%s) Tj ET'%(color,font,size,y,_pdf_escape(row)))
            y-=leading
    if commands:pages.append(commands)
    objs=['<< /Type /Catalog /Pages 2 0 R >>','', '<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica /Encoding /WinAnsiEncoding >>','<< /Type /Font /Subtype /Type1 /BaseFont /Times-Roman /Encoding /WinAnsiEncoding >>','<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica-Bold /Encoding /WinAnsiEncoding >>'];ids=[]
    for n,cmd in enumerate(pages,1):
        pid=len(objs)+1;cid=pid+1;ids.append(pid)
        stream='0.973 0.957 0.914 rg 0 0 595 842 re f\n'+rgb+' rg 50 795 36 3 re f\n'+'\n'.join(cmd)+'\n0.85 0.88 0.86 RG 0.5 w 50 59 m 545 59 l S\nBT /F1 8 Tf 0.39 0.45 0.42 rg 50 40 Td ('+_pdf_escape(title[:60])+' | '+str(n)+' / '+str(len(pages))+') Tj ET'
        objs.append('<< /Type /Page /Parent 2 0 R /MediaBox [0 0 595 842] /Contents %d 0 R /Resources << /Font << /F1 3 0 R /F2 4 0 R /F3 5 0 R >> >> >>'%cid)
        objs.append('<< /Length %d >>\nstream\n%s\nendstream'%(len(stream.encode('cp1252')),stream))
    objs[1]='<< /Type /Pages /Kids ['+' '.join('%d 0 R'%i for i in ids)+'] /Count %d >>'%len(ids)
    out,offs=b'%PDF-1.4\n',[]
    for i,o in enumerate(objs,1):offs.append(len(out));out+=('%d 0 obj\n%s\nendobj\n'%(i,o)).encode('cp1252')
    x=len(out);out+=('xref\n0 %d\n0000000000 65535 f \n'%(len(objs)+1)).encode()
    for o in offs:out+=('%010d 00000 n \n'%o).encode()
    out+=('trailer\n<< /Size %d /Root 1 0 R >>\nstartxref\n%d\n%%%%EOF'%(len(objs)+1,x)).encode()
    return out


def chat_markdown(title, turns):
    out = ["# " + title, ""]
    for t in turns:
        out += ["**Q:** " + t["question"], "", t["answer"], ""]
        for i, e in enumerate(t["evidence"], 1):
            out.append("%d. %s%s" % (i, e["title"], " <%s>" % e["url"] if e["url"] else ""))
        out.append("")
    return "\n".join(out)
