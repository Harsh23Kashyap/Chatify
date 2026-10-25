"""ISSUE-11 (hosted 2026-10-25): the documents-source freshness line claimed
"these sources show no dates" directly above a citation whose passage visibly
said "March 2026". Two rules now hold:
1. A document-level date is taken ONLY from explicit metadata (frontmatter
   date:/updated: or a leading Date:/Updated: header) - never from years
   mentioned in body text, which may be background, future, or multiple.
2. The freshness line distinguishes "no confirmed date" from "no dates": a
   passage that mentions years is described truthfully, and mentioned years
   are never promoted to confirmed freshness or date ordering."""
import os, sys, tempfile, unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from chatify.connectors.local_files import LocalFiles, document_date
from chatify.pipeline import Engine


class DocumentDateExtraction(unittest.TestCase):
    def test_frontmatter_date_iso(self):
        d, src = document_date('---\ntitle: Notes\ndate: 2026-03-04\n---\n# Body\nText.')
        self.assertEqual(d, "2026-03-04")
        self.assertEqual(src, "frontmatter date")

    def test_frontmatter_updated_month_name(self):
        d, src = document_date('---\nupdated: March 2026\n---\nBody text.')
        self.assertEqual(d, "2026-03")
        self.assertEqual(src, "frontmatter updated")

    def test_leading_date_header(self):
        d, src = document_date('# Cardiovascular outcomes notes\n\nDate: 2026-03\n\nSome text.')
        self.assertEqual(d, "2026-03")
        self.assertEqual(src, "header")

    def test_bare_year_frontmatter(self):
        d, _ = document_date('---\ndate: 2026\n---\nText.')
        self.assertEqual(d, "2026")

    def test_body_year_mention_not_promoted(self):
        # An old document mentioning a newer study year stays undated.
        d, src = document_date('# Notes from 2019\n\nA 2026 meta-analysis suggests otherwise.')
        self.assertEqual((d, src), ("", ""))

    def test_multiple_body_years_not_promoted(self):
        d, _ = document_date('# Review\n\nCompares the 2018, 2021 and 2026 trials.')
        self.assertEqual(d, "")

    def test_future_body_year_not_promoted(self):
        d, _ = document_date('# Plans\n\nWe target 2029 for the rollout.')
        self.assertEqual(d, "")

    def test_invalid_month_rejected(self):
        d, _ = document_date('---\ndate: 2026-13-01\n---\nText.')
        self.assertEqual(d, "")

    def test_late_date_line_not_a_header(self):
        body = "# Notes\n\n" + ("\n".join("Paragraph %d of context." % i for i in range(8))) + "\n\nDate: 2026-01\n"
        d, _ = document_date(body)
        self.assertEqual(d, "")


class LocalFilesDateFlow(unittest.TestCase):
    def _app(self, files):
        root = tempfile.mkdtemp()
        for name, text in files.items():
            with open(os.path.join(root, name), "w") as f:
                f.write(text)
        return LocalFiles({"id": "docs", "label": "Docs", "path": root})

    def test_frontmatter_date_reaches_evidence_year(self):
        lf = self._app({"notes.md": '---\ndate: 2026-03\n---\n# Cardio notes\n\nstatin dosage guidance'})
        ev = lf.search("statin dosage")
        self.assertTrue(ev)
        self.assertEqual(ev[0]["year"], "2026-03")

    def test_body_mention_keeps_evidence_undated(self):
        lf = self._app({"notes.md": '# Cardio notes (March 2026)\n\nstatin dosage guidance from a 2026 meta-analysis'})
        ev = lf.search("statin dosage")
        self.assertTrue(ev)
        self.assertEqual(ev[0]["year"], "")


class FreshnessLineWording(unittest.TestCase):
    RECENCY_Q = "What are the newest findings on statin cardiovascular outcomes?"

    def test_undated_with_mentioned_year_is_honest(self):
        evs = [{"n": 1, "text": "A 2026 meta-analysis reports outcomes.", "year": ""}]
        a = Engine.fallback_answer(evs, question=self.RECENCY_Q)
        self.assertIn("none of these sources carry a confirmed date", a)
        self.assertIn("not a confirmed publication date", a)
        self.assertIn("2026", a)
        self.assertNotIn("show no dates", a)

    def test_undated_without_any_year_keeps_no_dates_line(self):
        evs = [{"n": 1, "text": "A passage about outcomes.", "year": ""}]
        a = Engine.fallback_answer(evs, question=self.RECENCY_Q)
        self.assertIn("these sources show no dates", a)

    def test_mixed_dated_plus_mentioning_undated(self):
        evs = [{"n": 1, "text": "Dated trial.", "year": "2025"},
               {"n": 2, "text": "Owner note citing a 2026 meta-analysis.", "year": ""}]
        a = Engine.fallback_answer(evs, question=self.RECENCY_Q)
        self.assertIn("newest dated source found for this question is from 2025", a)
        self.assertIn("1 of the 2 sources for this answer carries no confirmed date", a)
        self.assertIn("not a confirmed publication date", a)

    def test_future_mentioned_year_still_unconfirmed(self):
        evs = [{"n": 1, "text": "We target 2029 for rollout.", "year": ""}]
        a = Engine.fallback_answer(evs, question=self.RECENCY_Q)
        self.assertIn("not a confirmed publication date", a)
        self.assertNotIn("newest dated source", a)


if __name__ == "__main__":
    unittest.main()
