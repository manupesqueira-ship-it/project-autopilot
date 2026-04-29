from __future__ import annotations

import json
import re
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from config import ProjectConfig


INSPECT_PATHS = [
    "supabase/schema.sql",
    "lib/supabase/client.ts",
    "lib/supabase/server.ts",
    "lib/generation-store.ts",
    "app/[locale]/(app)/onboarding/page.tsx",
    "app/[locale]/(app)/scan/page.tsx",
    "app/[locale]/(app)/tryon/[productId]/page.tsx",
    "app/[locale]/(app)/result/[generationId]/page.tsx",
    "app/api/tryon/jobs/route.ts",
    "app/api/tryon/status/[generationId]/route.ts",
    "package.json",
    "project_control/CUSTOMER_DATA_POLICY.md",
    "project_control/MIRA_E2E_VALIDATION_PLAN.md",
]

TABLE_PATTERN = re.compile(r"\.from\([\"']([^\"']+)[\"']\)|create\s+table\s+(?:if\s+not\s+exists\s+)?([a-zA-Z0-9_]+)", re.IGNORECASE)
BUCKET_PATTERN = re.compile(r"\.storage\s*\.\s*from\([\"']([^\"']+)[\"']\)", re.IGNORECASE)
LOCAL_STORAGE_PATTERN = re.compile(r"localStorage\.(?:getItem|setItem|removeItem)\([\"']([^\"']+)[\"']\)")
API_ROUTE_PATTERN = re.compile(r"fetch\([\"']([^\"']+)[\"']")
ENV_PATTERN = re.compile(r"process\.env\.([A-Z0-9_]+)")

KNOWN_TABLES = {
    "users_profile",
    "user_assets",
    "generations",
    "products",
    "sellers",
    "events",
}
KNOWN_BUCKETS = {
    "user-photos",
    "product-images",
    "generations",
}


@dataclass
class BackendAuditSummary:
    project_id: str
    readiness: str
    tables_referenced: list[str] = field(default_factory=list)
    tables_in_schema: list[str] = field(default_factory=list)
    missing_schema_tables: list[str] = field(default_factory=list)
    buckets_referenced: list[str] = field(default_factory=list)
    buckets_documented: list[str] = field(default_factory=list)
    missing_documented_buckets: list[str] = field(default_factory=list)
    local_storage_keys: list[str] = field(default_factory=list)
    api_routes_used: list[str] = field(default_factory=list)
    env_names_referenced: list[str] = field(default_factory=list)
    onboarding_writes_supabase: bool | None = None
    scan_uploads_storage: bool | None = None
    scan_inserts_user_assets: bool | None = None
    tryon_persists_generations: bool | None = None
    tryon_uses_in_memory_metadata: bool | None = None
    result_polling_uses_supabase: bool | None = None
    rls_present: bool | None = None
    rls_enabled: bool | None = None
    photo_privacy: str = "unknown"
    client_secret_risk: str = "unknown"
    findings: list[str] = field(default_factory=list)
    manual_verification_required: list[str] = field(default_factory=list)
    report_path: str | None = None


def _stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")


def _utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")


def _read(path: Path) -> str:
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8", errors="replace")


def _existing_files(project: ProjectConfig) -> dict[str, str]:
    files: dict[str, str] = {}
    for rel in INSPECT_PATHS:
        path = project.repo_path / rel
        if path.exists():
            files[rel] = _read(path)
    return files


def _matches(pattern: re.Pattern[str], text: str) -> list[str]:
    found: list[str] = []
    for match in pattern.finditer(text):
        for group in match.groups():
            if group:
                found.append(group)
    return found


def _unique(values: list[str]) -> list[str]:
    return sorted(dict.fromkeys(values))


def _schema_tables(schema: str) -> list[str]:
    tables: list[str] = []
    for match in re.finditer(r"create\s+table\s+(?:if\s+not\s+exists\s+)?([a-zA-Z0-9_]+)", schema, flags=re.IGNORECASE):
        tables.append(match.group(1))
    return _unique(tables)


def _schema_buckets(schema: str) -> list[str]:
    buckets: list[str] = []
    for known in KNOWN_BUCKETS:
        if known in schema:
            buckets.append(known)
    return _unique(buckets)


def _table_refs(files: dict[str, str]) -> list[str]:
    refs: list[str] = []
    for rel, text in files.items():
        if rel == "supabase/schema.sql":
            continue
        refs.extend(name for name in _matches(TABLE_PATTERN, text) if name in KNOWN_TABLES)
    return _unique(refs)


def _bucket_refs(files: dict[str, str]) -> list[str]:
    refs: list[str] = []
    for rel, text in files.items():
        if rel == "supabase/schema.sql" or rel.startswith("project_control/"):
            continue
        refs.extend(name for name in _matches(BUCKET_PATTERN, text) if name in KNOWN_BUCKETS)
    return _unique(refs)


def _env_risk(env_names: list[str]) -> str:
    server_only = [name for name in env_names if not name.startswith("NEXT_PUBLIC_")]
    if any(name in {"SUPABASE_SERVICE_ROLE_KEY", "DATABASE_URL"} for name in env_names):
        return "high: server-only secret names are referenced; verify they never appear in client code."
    if server_only:
        return "medium: server-only env names are referenced; static audit found no value exposure."
    return "low: only public client env names were detected in audited Supabase client/server code."


def _bool_text(value: bool | None) -> str:
    if value is None:
        return "unknown"
    return "yes" if value else "no"


def _privacy(schema: str, scan: str) -> str:
    if "user-photos" not in schema and "user-photos" not in scan:
        return "unknown: user photo bucket was not referenced."
    if "user-photos" in schema and "private" in schema.lower():
        return "documented_private_manual_verification_required"
    return "unclear_manual_verification_required"


def run_backend_audit(project: ProjectConfig) -> tuple[BackendAuditSummary, Path]:
    files = _existing_files(project)
    schema = files.get("supabase/schema.sql", "")
    onboarding = files.get("app/[locale]/(app)/onboarding/page.tsx", "")
    scan = files.get("app/[locale]/(app)/scan/page.tsx", "")
    tryon = files.get("app/[locale]/(app)/tryon/[productId]/page.tsx", "")
    result_page = files.get("app/[locale]/(app)/result/[generationId]/page.tsx", "")
    jobs_route = files.get("app/api/tryon/jobs/route.ts", "")
    status_route = files.get("app/api/tryon/status/[generationId]/route.ts", "")
    generation_store = files.get("lib/generation-store.ts", "")
    all_text = "\n".join(files.values())

    tables_in_schema = _schema_tables(schema)
    tables_referenced = _table_refs(files)
    buckets_documented = _schema_buckets(schema)
    buckets_referenced = _bucket_refs(files)
    missing_schema_tables = [table for table in tables_referenced if table not in tables_in_schema]
    missing_documented_buckets = [bucket for bucket in buckets_referenced if bucket not in buckets_documented]

    local_storage_keys = _unique(_matches(LOCAL_STORAGE_PATTERN, all_text))
    api_routes_used = _unique(_matches(API_ROUTE_PATTERN, all_text))
    env_names = _unique(_matches(ENV_PATTERN, all_text))

    summary = BackendAuditSummary(
        project_id=project.project_id,
        readiness="UNKNOWN",
        tables_referenced=tables_referenced,
        tables_in_schema=tables_in_schema,
        missing_schema_tables=missing_schema_tables,
        buckets_referenced=buckets_referenced,
        buckets_documented=buckets_documented,
        missing_documented_buckets=missing_documented_buckets,
        local_storage_keys=local_storage_keys,
        api_routes_used=api_routes_used,
        env_names_referenced=env_names,
        onboarding_writes_supabase=".from(\"users_profile\")" in onboarding or ".from('users_profile')" in onboarding,
        scan_uploads_storage=".storage" in scan and "user-photos" in scan and ".upload(" in scan,
        scan_inserts_user_assets=".from(\"user_assets\")" in scan or ".from('user_assets')" in scan,
        tryon_persists_generations="createGeneration" in jobs_route and "generations" in generation_store,
        tryon_uses_in_memory_metadata="metaCache" in generation_store or "new Map" in generation_store,
        result_polling_uses_supabase="getGeneration" in status_route and "generations" in generation_store,
        rls_present="row level security" in schema.lower(),
        rls_enabled=bool(re.search(r"^\s*alter\s+table\s+.*enable\s+row\s+level\s+security", schema, flags=re.IGNORECASE | re.MULTILINE)),
        photo_privacy=_privacy(schema, scan),
        client_secret_risk=_env_risk(env_names),
    )

    if not files:
        summary.findings.append("No inspected backend/product files were found.")
        summary.readiness = "UNKNOWN"
    else:
        _add_findings(summary, tryon, scan)
        summary.readiness = _readiness(summary)

    report_path = _write_report(project, summary, files)
    summary.report_path = str(report_path.relative_to(project.repo_path))
    _write_json_summary(project, summary)
    return summary, report_path


def _add_findings(summary: BackendAuditSummary, tryon: str, scan: str) -> None:
    if summary.onboarding_writes_supabase:
        summary.findings.append("Onboarding appears to insert a row into `users_profile` and stores `mira_profile_id` in localStorage.")
    else:
        summary.findings.append("Onboarding Supabase write could not be confirmed statically.")
        summary.manual_verification_required.append("Confirm onboarding creates `users_profile` rows.")

    if summary.scan_uploads_storage and summary.scan_inserts_user_assets:
        summary.findings.append("Scan appears to upload files to `user-photos` and insert rows into `user_assets`.")
    else:
        summary.findings.append("Scan upload and `user_assets` persistence are not fully confirmed by static audit.")
        summary.manual_verification_required.append("Confirm scan creates storage objects and `user_assets` rows.")

    if summary.tryon_persists_generations:
        summary.findings.append("Try-on jobs appear to create and update rows in `generations` through the server-side generation store.")
    else:
        summary.findings.append("Try-on generation persistence could not be confirmed statically.")
        summary.manual_verification_required.append("Confirm try-on creates `generations` rows.")

    if summary.tryon_uses_in_memory_metadata:
        summary.findings.append("Generation display metadata is partly in-memory, so product display fields can be lost across server restarts.")
        summary.manual_verification_required.append("Confirm result page behavior after a server restart or document the MVP limitation.")

    if "mira_profile" in tryon or "mira_photos" in tryon:
        summary.findings.append("Try-on reads `mira_profile` and `mira_photos`, while onboarding/scan persist `mira_profile_id` and Supabase rows; this looks like a flow-state mismatch.")
        summary.manual_verification_required.append("Verify try-on payload contains the intended profile/photo data, not only empty objects.")

    if not summary.rls_enabled:
        summary.findings.append("RLS statements are documented but not enabled in schema.sql.")
        summary.manual_verification_required.append("Confirm Supabase RLS/storage policies before real customer data.")

    if "user-photos" in scan:
        summary.manual_verification_required.append("Confirm `user-photos` bucket privacy and access policy in Supabase UI.")

    if summary.missing_schema_tables:
        summary.findings.append("Referenced tables missing from schema: " + ", ".join(summary.missing_schema_tables))
    if summary.missing_documented_buckets:
        summary.findings.append("Referenced buckets missing from schema docs: " + ", ".join(summary.missing_documented_buckets))


def _readiness(summary: BackendAuditSummary) -> str:
    if summary.missing_schema_tables or summary.missing_documented_buckets:
        return "BLOCKED"
    if not summary.tables_in_schema:
        return "UNKNOWN"
    partial_flags = [
        summary.tryon_uses_in_memory_metadata,
        not summary.rls_enabled,
        bool(summary.manual_verification_required),
    ]
    if any(partial_flags):
        return "PARTIAL_READY"
    required = [
        summary.onboarding_writes_supabase,
        summary.scan_uploads_storage,
        summary.scan_inserts_user_assets,
        summary.tryon_persists_generations,
        summary.result_polling_uses_supabase,
    ]
    return "READY_FOR_MANUAL_E2E" if all(required) else "PARTIAL_READY"


def _write_json_summary(project: ProjectConfig, summary: BackendAuditSummary) -> Path:
    path = project.repo_path / project.logs_dir / f"{project.project_id}_backend_audit_latest.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(asdict(summary), indent=2, sort_keys=True), encoding="utf-8")
    return path


def _write_report(project: ProjectConfig, summary: BackendAuditSummary, files: dict[str, str]) -> Path:
    logs_dir = project.repo_path / project.logs_dir
    logs_dir.mkdir(parents=True, exist_ok=True)
    latest_path = logs_dir / f"{project.project_id}_backend_audit_latest.md"
    run_path = logs_dir / f"{project.project_id}_backend_audit_{_stamp()}.md"

    missing_files = [path for path in INSPECT_PATHS if path not in files]
    content = "\n".join(
        [
            "# Backend Audit Report",
            "",
            f"Project: {project.project_name} ({project.project_id})",
            f"Timestamp: {_utc_now()}",
            f"BACKEND_READINESS: {summary.readiness}",
            "",
            "## Scope",
            "",
            "Static audit only. This command did not call Supabase, OpenAI, paid APIs, or the local dev server. It did not read `.env` or `.env.local` contents.",
            "",
            "## Files Inspected",
            "",
            _bullet(sorted(files.keys())) or "- None",
            "",
            "## Missing Or Unavailable Files",
            "",
            _bullet(missing_files) or "- None",
            "",
            "## Detected Data Surface",
            "",
            f"- Supabase tables referenced in code: {_inline(summary.tables_referenced)}",
            f"- Supabase tables present in schema.sql: {_inline(summary.tables_in_schema)}",
            f"- Storage buckets referenced in code: {_inline(summary.buckets_referenced)}",
            f"- Storage buckets documented in schema.sql: {_inline(summary.buckets_documented)}",
            f"- localStorage keys used: {_inline(summary.local_storage_keys)}",
            f"- API routes used by frontend: {_inline(summary.api_routes_used)}",
            f"- Environment variable names referenced: {_inline(summary.env_names_referenced)}",
            "",
            "## Persistence Checks",
            "",
            f"- Onboarding writes to Supabase `users_profile`: {_bool_text(summary.onboarding_writes_supabase)}",
            f"- Scan uploads to Supabase Storage `user-photos`: {_bool_text(summary.scan_uploads_storage)}",
            f"- Scan inserts into `user_assets`: {_bool_text(summary.scan_inserts_user_assets)}",
            f"- Try-on job persists `generations`: {_bool_text(summary.tryon_persists_generations)}",
            f"- Try-on/result uses in-memory metadata: {_bool_text(summary.tryon_uses_in_memory_metadata)}",
            f"- Result polling reads persisted generation status: {_bool_text(summary.result_polling_uses_supabase)}",
            "",
            "## Schema And Policy Alignment",
            "",
            f"- Missing referenced tables in schema.sql: {_inline(summary.missing_schema_tables)}",
            f"- Missing referenced buckets in schema docs: {_inline(summary.missing_documented_buckets)}",
            f"- RLS mentioned in schema.sql: {_bool_text(summary.rls_present)}",
            f"- RLS appears enabled by executable SQL: {_bool_text(summary.rls_enabled)}",
            f"- Customer photo privacy: {summary.photo_privacy}",
            f"- Client-side secret risk: {summary.client_secret_risk}",
            "",
            "## Findings",
            "",
            _bullet(summary.findings) or "- None",
            "",
            "## Manual Verification Required",
            "",
            _bullet(summary.manual_verification_required) or "- None",
            "",
            "## Recommended Next Action",
            "",
            _recommendation(summary),
            "",
        ]
    )
    latest_path.write_text(content, encoding="utf-8")
    run_path.write_text(content, encoding="utf-8")
    return latest_path


def _bullet(items: list[str]) -> str:
    return "\n".join(f"- {item}" for item in items)


def _inline(items: list[str]) -> str:
    return ", ".join(f"`{item}`" for item in items) if items else "none"


def _recommendation(summary: BackendAuditSummary) -> str:
    if summary.readiness == "BLOCKED":
        return "Fix schema/code mismatches before manual Supabase E2E validation."
    if summary.readiness == "UNKNOWN":
        return "Restore or point Project Autopilot at the expected backend files, then rerun backend audit."
    return (
        "Proceed to manual Supabase E2E validation with fake QA data. Treat generation display metadata, "
        "profile/photo payload alignment, RLS, and bucket privacy as required manual checks."
    )
