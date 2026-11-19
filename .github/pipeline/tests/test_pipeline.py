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


if __name__ == "__main__":
    unittest.main()
