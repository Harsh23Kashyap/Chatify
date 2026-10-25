import sys, unittest

from chatify.exports import pdf_bytes, _covered_chars, _rtl_dominant

AR = "الجرعة اليومية من الدواء آمنة"  # Arabic: the daily dose of the medicine is safe
HE = "המינון היומיומי של התרופה בטוח"  # Hebrew: the daily dose of the medicine is safe

class RtlPdfTest(unittest.TestCase):
    def turn(self, q, a):
        return {"question": q, "answer": a, "evidence": [{"n": 1, "title": "T " + AR, "url": "http://x", "authors": [], "year": "2026", "venue": "J"}]}

    def test_arabic_hebrew_answer_exports(self):
        data = pdf_bytes("RTL check", self.turn("ما الجرعة؟ " + HE, AR + " " + HE + " dosing notes."))
        self.assertTrue(data.startswith(b"%PDF"))
        self.assertGreater(len(data), 3000)

    def test_coverage_includes_arabic_and_hebrew(self):
        cov = _covered_chars()
        self.assertIn(0x0627, cov)  # Arabic alef
        self.assertIn(0x05D0, cov)  # Hebrew alef

    def test_rtl_vote(self):
        self.assertTrue(_rtl_dominant(AR))
        self.assertTrue(_rtl_dominant(HE))
        self.assertFalse(_rtl_dominant("English with كلمة one word"))
        self.assertFalse(_rtl_dominant("plain english"))

    def test_uncovered_script_still_rejected(self):
        with self.assertRaises(ValueError):
            pdf_bytes("CJK", self.turn("用量是多少", "每日用量安全"))  # CJK still honest rejection

    def test_latin_unchanged(self):
        data = pdf_bytes("Plain", self.turn("What dose?", "The daily dose is safe."))
        self.assertTrue(data.startswith(b"%PDF"))

if __name__ == "__main__":
    unittest.main()
