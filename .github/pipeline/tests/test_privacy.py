"""Offline tests for the privacy check. Every term and path in here is made up, and the private-looking strings
are put together at run time, so this file itself passes the check it tests."""
import contextlib
import io
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import common  # noqa: E402
import privacy  # noqa: E402

TERM = "zebra" + "-orchard-" + "17"                         # a made-up entry of the owner's list
WIN_HOME = "\\".join(["C:", "Users", "sample-person", "notes.md"])
UNIX_HOME = "/".join(["", "home", "sample-person", "x"])
BASH_HOME = "/".join(["", "c", "Users", "sample-person"])
APPDATA_ONLY = "\\".join(["%X%", "App" + "Data", "Roaming", "tool"])
TEMP = "/".join(["", "tmp", "build-1", "out.txt"])
SESSION = "-".join(["1a2b3c4d", "0000", "4000", "8000", "123456789abc"])


def terms_file(*lines) -> Path:
    path = Path(tempfile.mkdtemp()) / "terms.txt"
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path


class Scan(unittest.TestCase):
    def kinds(self, text, terms=()):
        return [h.kind for h in privacy.scan(text, list(terms))]

    def test_fixed_patterns(self):
        self.assertEqual(self.kinds(f"see {WIN_HOME} now"), ["home path"])
        self.assertEqual(self.kinds(f"see {UNIX_HOME}"), ["home path"])
        self.assertEqual(self.kinds(f"in Git Bash: {BASH_HOME}"), ["home path"])
        self.assertIn("app-data path", self.kinds(APPDATA_ONLY))
        self.assertEqual(self.kinds(f"wrote {TEMP}"), ["temp path"])
        self.assertEqual(self.kinds(f"session {SESSION}"), ["session id"])

    def test_owner_terms_ignore_case(self):
        self.assertEqual(self.kinds(f"the {TERM.upper()} repo", [TERM]), ["owner's term"])

    def test_clean_text_passes(self):
        text = ("Ran python -m unittest in .github/pipeline: 80 tests ok. Commit " + "a" * 40 + ". "
                "See https://github.com/owner/repo/pull/3 and ~/.claude/skill-pipeline/loop.log, "
                "C:/Claude/.worktrees/skills/issue-3, the users/ folder, api/users/42, LOCALAPPDATA.")
        self.assertEqual(self.kinds(text, [TERM]), [])

    def test_position_and_never_the_term(self):
        hits = privacy.scan(f"line one\nfoo {TERM} bar", [TERM])
        self.assertEqual((hits[0].line, hits[0].column), (2, 5))
        message = privacy.describe(hits, "the text")
        self.assertIn("owner's term", message)
        self.assertIn("line 2, column 5", message)
        self.assertNotIn(TERM.lower(), message.lower())
        self.assertNotIn("sample-person", privacy.describe(privacy.scan(WIN_HOME, []), "the text"))


class Terms(unittest.TestCase):
    def test_list_is_read_at_run_time(self):
        path = terms_file("# a comment", "", f"  {TERM}  ", "Other-Word")
        with mock.patch.object(privacy, "TERMS", path):
            self.assertEqual(privacy.load_terms(), [TERM, "Other-Word"])

    def test_missing_list_says_so_once_and_fixed_patterns_still_apply(self):
        err = io.StringIO()
        with mock.patch.object(privacy, "TERMS", Path(tempfile.mkdtemp()) / "none.txt"), \
                mock.patch.object(privacy, "_said_missing", False), contextlib.redirect_stderr(err):
            self.assertEqual(privacy.load_terms(), [])
            self.assertEqual(privacy.load_terms(), [])
            with self.assertRaises(common.Failed):
                privacy.guard("owner/repo", {"body": f"see {WIN_HOME}"}, public=True)
        self.assertEqual(err.getvalue().count("no owner list"), 1)


class Posting(unittest.TestCase):
    """Evidence, issue comments and pull request texts all go through common.api: the check sits there."""
    def go(self, body, private=False, path="repos/owner/repo/issues/3/comments"):
        sent = []

        def fake_run(args, input=None, **kw):
            sent.append(args)
            if "POST" in args:
                return subprocess.CompletedProcess(args, 0, json.dumps({"html_url": "url"}), "")
            return subprocess.CompletedProcess(args, 0, json.dumps({"private": private}), "")

        with mock.patch.object(privacy, "TERMS", terms_file(TERM)), mock.patch.object(privacy, "_public", {}), \
                mock.patch.object(common.subprocess, "run", fake_run):
            try:
                common.api(path, "POST", {"body": body})
            except common.Failed as e:
                return e, sent
        return None, sent

    def test_a_hit_stops_the_post_to_a_public_repo(self):
        for body in (f"report\nmentions {TERM}", f"log at {WIN_HOME}", f"session {SESSION}"):
            error, sent = self.go(body)
            self.assertIsInstance(error, common.Failed, body)
            self.assertFalse([a for a in sent if "POST" in a], "nothing may be posted")
            self.assertNotIn(TERM, str(error))

    def test_clean_text_goes_through(self):
        error, sent = self.go("Review: 12 tests ran, all passed.")
        self.assertIsNone(error)
        self.assertTrue([a for a in sent if "POST" in a])

    def test_a_private_repo_is_not_affected(self):
        error, sent = self.go(f"mentions {TERM}", private=True)
        self.assertIsNone(error)

    def test_pull_request_titles_and_texts_are_checked(self):
        with self.assertRaises(common.Failed):
            privacy.guard("owner/repo", {"title": f"fix: {TERM}", "body": "x"}, public=True, terms=[TERM])
        privacy.guard("owner/repo", {"labels": [TERM]}, public=True, terms=[TERM])   # labels are not text

    def test_evidence_command_is_refused(self):
        import evidence
        folder = Path(tempfile.mkdtemp())
        (folder / "report.md").write_text(f"Looked at it.\nFound {TERM} in the diff.", encoding="utf-8")
        calls = []

        def fake_run(args, input=None, **kw):
            calls.append(args)
            if args[2].endswith("/pulls/1"):
                return subprocess.CompletedProcess(args, 0, json.dumps({"head": {"sha": "a" * 40}}), "")
            if "POST" in args:
                return subprocess.CompletedProcess(args, 0, json.dumps({"html_url": "url"}), "")
            return subprocess.CompletedProcess(args, 0, json.dumps({"private": False}), "")

        argv = ["evidence.py", "--repo", "owner/repo", "--pr", "1", "--kind", "qa", "--result", "pass",
                "--file", str(folder / "report.md"), "--model", "m", "--effort", "low"]
        with mock.patch.object(privacy, "TERMS", terms_file(TERM)), mock.patch.object(privacy, "_public", {}), \
                mock.patch.object(common.subprocess, "run", fake_run), mock.patch("sys.argv", argv), \
                mock.patch("builtins.print"):
            with self.assertRaises(common.Failed) as caught:
                evidence.cli()
        self.assertFalse([a for a in calls if "POST" in a])
        self.assertIn("line", str(caught.exception))


class Push(unittest.TestCase):
    """What a push adds to a public repo: the added lines and the commit messages."""
    def repo(self, added: str, message: str = "fix: something", name: str = "new.md") -> tuple[Path, str]:
        root = Path(tempfile.mkdtemp())
        git = lambda *a: subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@example.com",
                                         "-c", "core.hooksPath=" + os.devnull, *a], cwd=root, check=True,
                                        capture_output=True, text=True, creationflags=common.NO_WINDOW).stdout
        git("init", "-q", "-b", "main")
        (root / "old.md").write_text(f"already there: {TERM}\n", encoding="utf-8")
        git("add", "-A")
        git("commit", "-q", "-m", "start")
        git("checkout", "-q", "-b", "work")
        (root / name).parent.mkdir(parents=True, exist_ok=True)
        (root / name).write_text(f"one\ntwo\n{added}\n", encoding="utf-8")
        git("add", "-A")
        git("commit", "-q", "-m", message)
        return root, git("rev-parse", "HEAD").strip()

    def test_added_content_with_a_hit_is_refused(self):
        root, head = self.repo(f"three {TERM}")
        hits = privacy.scan_push("main", head, [TERM], cwd=root)
        self.assertEqual([(h.kind, h.where, h.line) for h in hits], [("owner's term", "new.md", 3)])

    def test_file_names_are_checked_and_never_printed(self):
        root, head = self.repo("three", name=f"{TERM}/SKILL.md")
        hits = privacy.scan_push("main", head, [TERM], cwd=root)
        self.assertEqual([h.kind for h in hits], ["owner's term"])
        root, head = self.repo(f"three {TERM}", name=f"{TERM}/SKILL.md")
        message = privacy.describe(privacy.scan_push("main", head, [TERM], cwd=root), "This push")
        self.assertEqual(message.count("owner's term"), 2)
        self.assertNotIn(TERM, message)
        self.assertIn("file 1 of the push", message)

    def test_an_added_line_that_looks_like_a_header_is_content(self):
        root, head = self.repo(f"++ {TERM}")
        hits = privacy.scan_push("main", head, [TERM], cwd=root)
        self.assertEqual([(h.where, h.line) for h in hits], [("new.md", 3)])

    def test_commit_messages_are_checked(self):
        root, head = self.repo("three", message=f"fix: path {WIN_HOME}")
        hits = privacy.scan_push("main", head, [TERM], cwd=root)
        self.assertEqual([h.kind for h in hits], ["home path"])
        self.assertIn("commit message", hits[0].where)

    def test_clean_push_and_old_content_pass(self):
        root, head = self.repo("three")
        self.assertEqual(privacy.scan_push("main", head, [TERM], cwd=root), [])

    def test_remote_urls(self):
        for url in ("https://github.com/owner/repo.git", "git@github.com:owner/repo.git", "https://github.com/owner/repo"):
            self.assertEqual(privacy.slug_of(url), "owner/repo", url)
        self.assertIsNone(privacy.slug_of("https://example.com/x.git"))

    def test_the_hook_runs_the_check(self):
        hook = (Path(__file__).resolve().parent.parent / "hooks" / "pre-push").read_text(encoding="utf-8")
        self.assertIn("privacy.py", hook)


class ThisChange(unittest.TestCase):
    def test_the_files_of_this_check_pass_it(self):
        """No real or made-up private string is written literally into the check, its tests or its docs."""
        folder = Path(__file__).resolve().parent.parent
        for path in (folder / "privacy.py", Path(__file__), folder / "README.md", folder / "hooks" / "pre-push"):
            self.assertEqual(privacy.scan(path.read_text(encoding="utf-8"), []), [], path.name)


if __name__ == "__main__":
    unittest.main()
