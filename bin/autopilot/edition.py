"""Identity of this edition of the plugin.

Every name that could collide with a separately named copy of the plugin lives in this
file, manifest.json and lib/Edition.js. Everything else reads these constants.
"""

PLUGIN_ID = "oliwier.auto-pilot4agents"
DISPLAY_NAME = "Auto Pilot"
UNIT_PREFIX = "ap4a"
UNIT_DESCRIPTION = "Auto Pilot job"
SYSLOG_IDENTIFIER = "ap4a"
STATE_DIR_NAME = "auto-pilot4agents"      # $HOME/.local/state/omarchy/<name>
RUNTIME_DIR_NAME = "auto-pilot4agents"    # $XDG_RUNTIME_DIR/<name>
CONFIG_DIR_NAME = "auto-pilot4agents"     # $HOME/.config/omarchy/<name>
KILL_SWITCH_NAME = "DISABLED"             # $HOME/.config/omarchy/<name>/DISABLED
WIDGET_IPC_TARGET = "oliwier.auto-pilot4agents"
SERVICE_IPC_TARGET = "oliwier.auto-pilot4agents.jobs"
NOTIFY_APP_NAME = "Auto Pilot"
SESSION_NAME_PREFIX = "autopilot-"        # Claude --name / OpenCode --title for new sessions
DEMO_STATE_ENV = "AP4A_STATE_DIR"         # honoured only while the kill switch exists (R0 C14)
SCHEMA_VERSION = 1

HARNESS_IDS = ("claude", "opencode", "codex", "cursor", "pi", "gemini")

# Claude Code loads a folder's .claude/settings.json, .mcp.json and agents unprompted under -p,
# and that config can run hooks, redirect the login with ANTHROPIC_BASE_URL or widen what a run
# may do. A cloned folder is the user's own, so the private-folder check does not stop it. Every
# Claude run is pinned to the user's own settings only, takes no MCP from a folder, and never
# writes the durable auto-memory or scheduled-task files that a later run would reload.
_CLAUDE_ISOLATION = ("--setting-sources", "user", "--strict-mcp-config")
_CLAUDE_ISOLATION_ENV = {"CLAUDE_CODE_DISABLE_AUTO_MEMORY": "1", "CLAUDE_CODE_DISABLE_CRON": "1"}

_OPENCODE_PLAN = ('{"edit":"deny","bash":"deny","webfetch":"deny","websearch":"deny",'
                  '"task":"deny","external_directory":"deny","doom_loop":"deny"}')
# Unattended turns the same tools off as Plan rather than leaving them to ask. Nobody is there to
# answer either way, but a tool that is off is never offered to the model, while one left to ask
# is offered and checked call by call, which OpenCode does not do for every command.
_OPENCODE_UNATTENDED = ('{"edit":"deny","bash":"deny","webfetch":"deny","websearch":"deny",'
                        '"task":"deny","external_directory":"deny","doom_loop":"deny"}')

# Closed enum. The helper refuses any level id that is not a key of this table,
# whether it comes from stdin, jobs.json or IPC (R0 D8).
LEVELS = (
    {
        "id": "plan",
        "label": "Plan",
        "default": True,
        "summary": "Reads and plans only.",
        "defaultMaxTurns": 15,
        "harness": {
            "claude": {
                "caption": "Plan mode. Claude reads and proposes a plan. It does not edit files or run commands.",
                "argv": ["--permission-mode", "plan", "--permission-prompts", "none"] + list(_CLAUDE_ISOLATION),
                "env": dict(_CLAUDE_ISOLATION_ENV),
                "initPermissionMode": "plan",
            },
            "opencode": {
                "caption": "Built-in plan agent without plugins. Edits, shell, web and subagents are denied.",
                "argv": ["--pure", "--agent", "plan"],
                "env": {"OPENCODE_PERMISSION": _OPENCODE_PLAN},
                "initPermissionMode": None,
            },
            "codex": {
                "caption": "Read-only sandbox. Codex can read files but cannot write or reach the network.",
                "argv": ["-s", "read-only"],
                "env": {},
                "initPermissionMode": None,
            },
            "gemini": {
                "caption": "Plan mode. Gemini reads and plans. It does not edit files or run commands.",
                "argv": ["--approval-mode", "plan"],
                "env": {},
                "initPermissionMode": None,
            },
            "cursor": {
                # Cursor's own sandbox cannot start inside the job's hardened unit (it needs privileges
                # NoNewPrivileges denies), so the boundary here is ask mode: every tool that would ask
                # for approval is denied, and no edit is applied.
                "caption": ("Ask mode. Cursor reads and answers, and anything that would need your approval is "
                            "denied, so no file is edited."),
                "argv": ["--mode", "ask"],
                "env": {},
                "initPermissionMode": None,
            },
            "pi": {
                "caption": "Pi runs read-only here: read, grep, find and ls. It cannot edit files or run commands.",
                "argv": ["--offline", "--no-extensions", "--no-skills", "--no-prompt-templates", "--no-themes",
                         "--no-approve", "--tools", "read,grep,find,ls"],
                "env": {"PI_OFFLINE": "1", "PI_TELEMETRY": "0", "PI_SKIP_VERSION_CHECK": "1"},
                "initPermissionMode": None,
            },
        },
        "unavailable": {},
    },
    {
        "id": "unattended",
        "label": "Unattended",
        "default": False,
        "summary": "Runs without you. Anything that would ask is denied.",
        "defaultMaxTurns": 30,
        "harness": {
            "claude": {
                "caption": "Only what your own Claude permission rules already allow. Anything that would ask is denied.",
                "argv": ["--permission-mode", "dontAsk", "--permission-prompts", "none"] + list(_CLAUDE_ISOLATION),
                "env": dict(_CLAUDE_ISOLATION_ENV),
                "initPermissionMode": "dontAsk",
            },
            "opencode": {
                "caption": "Edits, shell, web and subagents are off, since nobody is there to approve them. Reads still work.",
                "argv": [],
                "env": {"OPENCODE_PERMISSION": _OPENCODE_UNATTENDED},
                "initPermissionMode": None,
            },
            "codex": {
                "caption": "Workspace-write sandbox. Codex can edit inside the working folder. Network stays off.",
                "argv": ["-s", "workspace-write"],
                "env": {},
                "initPermissionMode": None,
            },
            "gemini": {
                "caption": "Default approval. Tools that would ask are denied because nobody is there to answer.",
                "argv": ["--approval-mode", "default"],
                "env": {},
                "initPermissionMode": None,
            },
        },
        # Harness id -> the fixed reason this level is not offered for it.
        "unavailable": {
            "cursor": "Cursor applies file edits headless only with --force, which Auto Pilot never passes.",
            "pi": "Pi has no approval prompts, so only Plan is offered.",
        },
    },
)

LEVEL_IDS = tuple(level["id"] for level in LEVELS)
DEFAULT_LEVEL = "plan"


def level(level_id):
    """Return the LEVELS entry for level_id, or None when it is not in the closed enum."""
    for entry in LEVELS:
        if entry["id"] == level_id:
            return entry
    return None
