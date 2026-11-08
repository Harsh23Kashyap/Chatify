"""arXiv Atom API (public). block.category narrows the search, e.g. eess.SP for signal processing."""
import re, time, threading, urllib.error, urllib.parse, urllib.request
import xml.etree.ElementTree as ET
from .base import Evidence

NS = {"a": "http://www.w3.org/2005/Atom"}


# One connection and at least three seconds between request starts, shared by
# all connector instances in this process, including retries and failed calls.
# Multiple processes/machines must additionally coordinate their combined rate.
_request_lock = threading.Lock()
_next_request_at = 0.0


def _request(url):
    global _next_request_at
    with _request_lock:
        delay = _next_request_at - time.monotonic()
        if delay > 0:
            time.sleep(delay)
        _next_request_at = time.monotonic() + 3.0
        with urllib.request.urlopen(url, timeout=25) as response:
            return ET.fromstring(response.read())


class Arxiv:
    def __init__(self, block):
        self.id, self.label, self.b = block["id"], block["label"], block

    def search(self, query, k=6, recent=False):
        # arXiv does not apply the field prefix to every unquoted word.
        # all:habitat fragmentation returned unrelated smart-home papers in live
        # qualification. Require each natural-language term; leave an explicit
        # arXiv field/Boolean expression intact for advanced callers.
        if re.search(r'\b[a-z_]+:|\b(?:AND|OR|ANDNOT)\b', query):
            expression = query
        else:
            terms = re.findall(r'"[^"\n]+"|[\w-]+', query)
            expression = " AND ".join("all:" + term for term in terms) or "all:" + query
        q = urllib.parse.quote(expression)
        if self.b.get("category"):
            q += "+AND+cat:" + urllib.parse.quote(self.b["category"])
        order = "sortBy=submittedDate&sortOrder=descending" if recent else "sortBy=relevance"
        url = "https://export.arxiv.org/api/query?search_query=%s&max_results=%d&%s" % (q, k, order)
        for attempt in range(3):
            try:
                root = _request(url)
                break
            except (TimeoutError, urllib.error.URLError) as error:
                if isinstance(error, urllib.error.HTTPError) and error.code not in (429, 500, 502, 503, 504):
                    raise
                if attempt == 2:
                    raise
                time.sleep(3 * (attempt + 1))
        out = []
        for i, e in enumerate(root.findall("a:entry", NS)):
            link = e.findtext("a:id", "", NS)
            out.append(Evidence(" ".join((e.findtext("a:title", "", NS) or "").split()),
                                " ".join((e.findtext("a:summary", "", NS) or "").split()), link,
                                [a.findtext("a:name", "", NS) for a in e.findall("a:author", NS)][:6],
                                (e.findtext("a:published", "", NS) or "")[:4], "arXiv", self.id, 1.0 / (i + 1),
                                "arXiv:" + link.rsplit("/", 1)[-1]))
        return out
