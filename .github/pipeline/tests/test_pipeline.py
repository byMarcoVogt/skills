"""Offline tests for the rules and the guard. Run: python -m unittest discover -s .github/pipeline/tests"""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import git_guard  # noqa: E402
import rules  # noqa: E402

SHA, OTHER = "a" * 40, "b" * 40


def md(version, body="text"):
    v = f'metadata:\n  version: "{version}"\n' if version else ""
    return f"---\nname: demo\ndescription: d\n{v}---\n{body}\n"


def ev(kind, sha=SHA, result="pass", author="owner", report="looked at the diff"):
    return {"author": author, "body": f"<!-- pipeline-evidence kind={kind} sha={sha} result={result} -->\n{report}"}


class Title(unittest.TestCase):
    def test_kinds(self):
        self.assertEqual(rules.title_kind("fix: stop asking twice"), "fix")
        self.assertEqual(rules.title_kind("feat: teaching mode"), "feat")
        self.assertEqual(rules.title_kind("feat!: new call syntax"), "feat!")

    def test_rejected(self):
        for t in ("Fix: x", "fix:x", "fix: ", "chore: tidy", "update skill", "feat(scope): x", ""):
            self.assertIsNone(rules.title_kind(t), t)


class Version(unittest.TestCase):
    def test_bump(self):
        self.assertEqual(rules.bump((1, 4, 0), "fix"), (1, 4, 1))
        self.assertEqual(rules.bump((1, 4, 1), "feat"), (1, 5, 0))
        self.assertEqual(rules.bump((1, 5, 0), "feat!"), (2, 0, 0))

    def test_two_part_versions_read_as_three(self):
        self.assertEqual(rules.skill_version(md("2.0")), (2, 0, 0))
        self.assertEqual(rules.parse_version("0.7"), (0, 7, 0))

    def test_version_only_from_frontmatter(self):
        self.assertIsNone(rules.skill_version(md(None, 'version: "9.9.9"')))

    def test_set_version_keeps_the_rest(self):
        out = rules.set_skill_version(md("2.0", "body\nmore"), (2, 0, 1))
        self.assertEqual(rules.skill_version(out), (2, 0, 1))
        self.assertTrue(out.endswith("body\nmore\n"))
        self.assertEqual(rules.skill_version(rules.set_skill_version(md(None), (0, 1, 0))), (0, 1, 0))

    def test_right_bump_passes(self):
        self.assertTrue(rules.check_version("fix: x", {"demo": (md("1.4.0"), md("1.4.1"))})[0])
        self.assertTrue(rules.check_version("feat: x", {"demo": (md("2.0"), md("2.1.0"))})[0])

    def test_missing_or_wrong_bump_fails(self):
        self.assertFalse(rules.check_version("fix: x", {"demo": (md("1.4.0"), md("1.4.0"))})[0])
        self.assertFalse(rules.check_version("fix: x", {"demo": (md("1.4.0"), md("1.5.0"))})[0])
        self.assertFalse(rules.check_version("feat: x", {"demo": (md("1.4.0"), md("1.4.1"))})[0])
        self.assertFalse(rules.check_version("feat: x", {"demo": (md("1.4.0"), md(None))})[0])

    def test_one_skill_per_pr(self):
        two = {"a": (md("1.0.0"), md("1.0.1")), "b": (md("1.0.0"), md("1.0.1"))}
        self.assertFalse(rules.check_version("fix: x", two)[0])

    def test_no_skill_and_new_skill(self):
        self.assertTrue(rules.check_version("fix: readme", {})[0])
        self.assertTrue(rules.check_version("feat: new", {"demo": (None, md("0.1.0"))})[0])
        self.assertFalse(rules.check_version("feat: new", {"demo": (None, md(None))})[0])


class Evidence(unittest.TestCase):
    def test_both_kinds_for_this_commit(self):
        found = rules.find_evidence([ev("review"), ev("qa")], SHA, "owner")
        self.assertTrue(rules.check_evidence(found, True)[0])

    def test_missing(self):
        self.assertFalse(rules.check_evidence(rules.find_evidence([ev("review")], SHA, "owner"), True)[0])
        self.assertFalse(rules.check_evidence({}, True)[0])

    def test_a_new_commit_voids_it(self):
        found = rules.find_evidence([ev("review"), ev("qa")], OTHER, "owner")
        self.assertEqual(found, {})

    def test_only_the_owner_counts_and_a_report_is_needed(self):
        self.assertEqual(rules.find_evidence([ev("review", author="stranger")], SHA, "owner"), {})
        self.assertEqual(rules.find_evidence([ev("review", report="")], SHA, "owner"), {})

    def test_fail_blocks_and_newest_wins(self):
        self.assertFalse(rules.check_evidence(rules.find_evidence([ev("review"), ev("qa", result="fail")], SHA, "owner"), True)[0])
        found = rules.find_evidence([ev("qa", result="fail"), ev("qa"), ev("review")], SHA, "owner")
        self.assertTrue(rules.check_evidence(found, True)[0])

    def test_not_needed_without_skill_or_pipeline_change(self):
        self.assertTrue(rules.check_evidence({}, False)[0])
        self.assertTrue(rules.check_evidence({}, True, undo_of="demo--v1.0.0")[0])


class Protected(unittest.TestCase):
    def test_pipeline_files_need_the_owner(self):
        self.assertFalse(rules.check_protected([".github/pipeline/gate.py"], False)[0])
        self.assertTrue(rules.check_protected([".github/pipeline/gate.py"], True)[0])
        self.assertTrue(rules.check_protected(["demo/SKILL.md", "README.md"], False)[0])


class Undo(unittest.TestCase):
    def test_previous_release(self):
        tags = ["demo--v1.0.0", "demo--v1.1.0", "demo--v1.2.0", "other--v9.0.0", "demo--v2.0"]
        self.assertEqual(rules.previous_release(tags, "demo", (1, 2, 0)), ("demo--v1.1.0", (1, 1, 0)))
        self.assertEqual(rules.previous_release(tags, "demo", (2, 0, 1)), ("demo--v2.0", (2, 0, 0)))
        self.assertIsNone(rules.previous_release(tags, "demo", (1, 0, 0)))

    def test_same_except_version(self):
        self.assertEqual(rules.without_version(md("1.0.0")), rules.without_version(md("1.0.2")))
        self.assertNotEqual(rules.without_version(md("1.0.0", "a")), rules.without_version(md("1.0.2", "b")))

    def test_undo_title(self):
        m = rules.UNDO_TITLE.match("fix: undo think-it-through to v2.0")
        self.assertEqual((m.group("skill"), m.group("version")), ("think-it-through", "2.0"))


CFG = {"skills_dir": "C:/Users/x/.claude/skills", "worktrees": "C:/Claude/.worktrees",
       "repos": [{"slug": "me/skills", "path": "C:/Claude/skills"}, {"slug": "me/skills-private", "path": "C:/Claude/skills-private"}]}
TREE = "C:/Claude/.worktrees/skills/issue-3"


class Guard(unittest.TestCase):
    def deny(self, command, cwd=TREE, tool="Bash"):
        return git_guard.decide({"tool_name": tool, "tool_input": {"command": command}, "cwd": cwd}, CFG)

    def test_blocked_in_a_worktree(self):
        for c in ("git push --force", "git push -f origin issue-3", "git push origin main", "git push origin HEAD:main",
                  "git push origin HEAD:refs/heads/main", "git commit --no-verify -m x", "git config core.hooksPath /tmp",
                  "git tag demo--v9.9.9", "git push --tags", "gh release create demo--v1", "gh pr merge 3 --squash",
                  "gh pr merge 3 --admin", "gh api -X PUT repos/me/skills/branches/main/protection",
                  "gh api repos/me/skills/statuses/abc -f state=success", "gh pr edit 3 --add-label owner-approved",
                  "gh secret set X", "gh repo edit --visibility public", "git remote set-url origin x"):
            self.assertIsNotNone(self.deny(c), c)

    def test_allowed_in_a_worktree(self):
        for c in ("git status", "git add -A && git commit -m 'fix: x'", "git push -u origin issue-3",
                  "git push --force-with-lease origin issue-3", "git push origin fix/main-menu", "git tag --list 'demo--v*'",
                  "gh pr create --title 'fix: x' --body y", "gh pr view 3", "gh api repos/me/skills/pulls/3",
                  "python C:/Claude/skills/.github/pipeline/merge.py --repo me/skills --pr 3", "git rebase origin/main"):
            self.assertIsNone(self.deny(c), c)

    def test_live_clone_is_read_only(self):
        for c in ("git commit -m x", "git checkout -b work", "git reset --hard HEAD~1", "git stash", "git add ."):
            self.assertIsNotNone(self.deny(c, cwd="C:/Claude/skills"), c)
        self.assertIsNotNone(self.deny("git -C C:/Claude/skills-private checkout issue-3", cwd="C:/elsewhere"))
        self.assertIsNotNone(self.deny("cd C:\\Claude\\skills; git switch work", cwd="C:/elsewhere", tool="PowerShell"))
        for c in ("git status", "git log --oneline -5", "git pull --ff-only", "git worktree add ../x -b y origin/main"):
            self.assertIsNone(self.deny(c, cwd="C:/Claude/skills"), c)

    def test_git_bash_paths_and_stepping_out_of_the_live_clone(self):
        self.assertIsNotNone(self.deny("git -C /c/Claude/skills-private commit -m x", cwd="C:/elsewhere"))
        self.assertIsNotNone(self.deny("cd /c/Claude/skills && git add -A", cwd="C:/elsewhere"))
        self.assertIsNotNone(self.deny("rm -rf /c/Claude/skills/demo", cwd="C:/elsewhere"))
        self.assertIsNone(self.deny("cd /c/Claude/.worktrees/skills/issue-3 && git add -A && git commit -m 'fix: x'",
                                    cwd="C:/Claude/skills"))
        self.assertIsNone(self.deny("git -C /c/Claude/.worktrees/skills/issue-3 commit -m x", cwd="C:/Claude/skills"))

    def test_reading_github_is_fine_writing_is_not(self):
        self.assertIsNone(self.deny("gh api repos/me/skills/commits/abc/statuses --jq '.[].state'"))
        self.assertIsNone(self.deny("gh api repos/me/skills/branches/main/protection"))
        self.assertIsNotNone(self.deny("gh api repos/me/skills/statuses/abc -f state=success -f context=pipeline/title"))
        self.assertIsNotNone(self.deny("gh api -X DELETE repos/me/skills/branches/main/protection"))
        self.assertIsNotNone(self.deny("gh api repos/me/skills/pulls/3/merge -X PUT"))

    def test_live_paths_are_not_prefixes(self):
        self.assertIsNone(self.deny("git -C C:/Claude/skills-old commit -m x", cwd="C:/elsewhere"))

    def test_other_projects_are_untouched(self):
        for c in ("git push --force origin main", "gh pr merge 3", "git commit --no-verify -m x", "git tag v1"):
            self.assertIsNone(self.deny(c, cwd="C:/Claude/Jobby"), c)

    def test_edits(self):
        def edit(path):
            return git_guard.decide({"tool_name": "Edit", "tool_input": {"file_path": path}, "cwd": "C:/x"}, CFG)
        self.assertIsNotNone(edit("C:\\Claude\\skills\\demo\\SKILL.md"))
        self.assertIsNotNone(edit("C:/Claude/skills-private/.github/workflows/gate.yml"))
        self.assertIsNone(edit("C:/Claude/skills-private/plans/2026-11-plan.html"))
        self.assertIsNone(edit("C:/Claude/.worktrees/skills/issue-3/demo/SKILL.md"))
        self.assertIsNone(edit("C:/Claude/Jobby/app.py"))

    def test_removing_live_folders(self):
        self.assertIsNotNone(self.deny("rm -rf C:/Claude/skills/demo", cwd="C:/elsewhere"))
        self.assertIsNotNone(self.deny("Remove-Item -Recurse C:\\Claude\\skills-private", cwd="C:/elsewhere", tool="PowerShell"))
        self.assertIsNone(self.deny("rm -rf C:/Claude/.worktrees/skills/issue-3/tmp"))


class NoWindow(unittest.TestCase):
    def test_every_started_program_is_windowless(self):
        """The loop runs under pythonw; a call without the flag flashes a terminal window on the owner's screen."""
        import ast
        folder = Path(__file__).resolve().parent.parent
        for path in sorted(folder.glob("*.py")):
            for node in ast.walk(ast.parse(path.read_text(encoding="utf-8"))):
                if (isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
                        and isinstance(node.func.value, ast.Name) and node.func.value.id == "subprocess"
                        and node.func.attr in ("run", "Popen", "call", "check_call", "check_output")):
                    flags = [k for k in node.keywords if k.arg == "creationflags"]
                    self.assertTrue(flags, f"{path.name}:{node.lineno} starts a program without creationflags=NO_WINDOW")


class LoopPrompt(unittest.TestCase):
    def test_fills_in_with_what_the_loop_passes(self):
        """A stray brace in the prompt would crash the scheduled run after the issue is already taken."""
        import string
        text = (Path(__file__).resolve().parent.parent / "loop-prompt.md").read_text(encoding="utf-8")
        fields = {name for _, name, _, _ in string.Formatter().parse(text) if name is not None}
        self.assertEqual(fields, {"number", "slug", "title", "pipeline", "tree"})
        text.format(number=1, slug="owner/repo", title='a {b} "c"', pipeline="P", tree="T")


class Take(unittest.TestCase):
    """loop.take hands one issue to a builder. Nothing may be left half done."""
    REPO = {"slug": "owner/repo", "path": "C:/live"}
    ISSUE = {"number": 7, "title": 'a {b} "c"'}
    CFG = {"worktrees": "C:/trees"}

    def go(self, api_result=None, api_error=None, worktree_error=None):
        import loop
        from unittest import mock
        calls = []

        def run(args, cwd=None, check=True, stdin=None):
            calls.append(" ".join(args[:3]))
            if worktree_error and args[2] == "add":
                raise loop.Failed(worktree_error)
            return ""

        def api(path, method="GET", fields=None, raw=False):
            calls.append("label")
            if api_error:
                raise loop.Failed(api_error)
            return api_result

        with mock.patch.object(loop, "run", run), mock.patch.object(loop, "api", api):
            try:
                return calls, loop.take(self.REPO, self.ISSUE, self.CFG)
            except loop.Failed as e:
                return calls, e

    def test_worktree_first_then_label_then_prompt(self):
        calls, (tree, prompt) = self.go(api_result=[{"name": "ready"}, {"name": "in-progress"}])
        self.assertEqual(calls, ["git worktree add", "label"])
        self.assertEqual(tree.as_posix(), "C:/trees/repo/issue-7")
        self.assertIn("issue #7 in owner/repo", prompt)
        self.assertIn("C:/trees/repo/issue-7", prompt)

    def test_no_label_when_the_worktree_cannot_be_made(self):
        calls, result = self.go(worktree_error="folder exists")
        self.assertEqual(calls, ["git worktree add"])
        self.assertIsInstance(result, Exception)

    def test_worktree_removed_when_the_label_fails(self):
        calls, result = self.go(api_error="network")
        self.assertEqual(calls, ["git worktree add", "label", "git worktree remove"])
        self.assertIsInstance(result, Exception)

    def test_worktree_removed_when_github_does_not_confirm_the_label(self):
        for answer in (None, [], [{"name": "ready"}]):       # None is what a 404 gives
            calls, result = self.go(api_result=answer)
            self.assertEqual(calls, ["git worktree add", "label", "git worktree remove"], answer)
            self.assertIsInstance(result, Exception)


if __name__ == "__main__":
    unittest.main()
