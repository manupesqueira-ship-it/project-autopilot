/**
 * Supabase Live Dev Check — Node.js helper
 *
 * Performs a minimal anonymous auth + fake profile insert against the
 * local/dev Supabase instance. Uses the same client libraries as the app.
 *
 * Usage (called by supabase_auth_verify.py --live-dev-check):
 *   node project_autopilot/helpers/supabase_live_dev_check.mjs [--no-insert] [--cleanup-dev-row]
 *
 * Safety:
 * - Loads env from .env and .env.local WITHOUT printing values
 * - Uses only fake/dev-only data (qa+mira-autopilot-*@example.com)
 * - Never prints tokens, keys, or JWTs
 * - Never uploads photos
 * - Never calls paid APIs
 * - Never changes schema/RLS/policies/buckets
 */

import { readFileSync, existsSync } from "fs";
import { resolve, dirname } from "path";
import { fileURLToPath } from "url";
import { createClient } from "@supabase/supabase-js";

const __dirname = dirname(fileURLToPath(import.meta.url));
const REPO_ROOT = resolve(__dirname, "..", "..");

// ---------------------------------------------------------------------------
// Env loading (mirrors project_autopilot/env_loader.py logic)
// ---------------------------------------------------------------------------

function loadDotenv(filePath) {
  if (!existsSync(filePath)) return;
  const content = readFileSync(filePath, "utf-8");
  for (const rawLine of content.split("\n")) {
    const line = rawLine.trim();
    if (!line || line.startsWith("#")) continue;
    const eq = line.indexOf("=");
    if (eq < 0) continue;
    const key = line.slice(0, eq).trim();
    let value = line.slice(eq + 1).trim();
    // Strip surrounding quotes
    if (value.length >= 2 && value[0] === value[value.length - 1] && (value[0] === '"' || value[0] === "'")) {
      value = value.slice(1, -1);
    }
    // Never let empty value clobber a real one
    if (!value && process.env[key]) continue;
    process.env[key] = value;
  }
}

loadDotenv(resolve(REPO_ROOT, ".env"));
loadDotenv(resolve(REPO_ROOT, ".env.local"));

// ---------------------------------------------------------------------------
// Validate env (never print values)
// ---------------------------------------------------------------------------

const url = process.env.NEXT_PUBLIC_SUPABASE_URL;
const anonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY;

if (!url || !anonKey) {
  console.log(JSON.stringify({
    ok: false,
    error: "MISSING_ENV",
    detail: "NEXT_PUBLIC_SUPABASE_URL or NEXT_PUBLIC_SUPABASE_ANON_KEY not found after loading .env/.env.local",
    authOk: false,
    insertOk: false,
  }));
  process.exit(1);
}

// ---------------------------------------------------------------------------
// Args
// ---------------------------------------------------------------------------

const args = process.argv.slice(2);
const noInsert = args.includes("--no-insert");
const cleanupRow = args.includes("--cleanup-dev-row");

// ---------------------------------------------------------------------------
// Run checks
// ---------------------------------------------------------------------------

const supabase = createClient(url, anonKey);

const result = {
  ok: false,
  authOk: false,
  userId: null,
  insertOk: false,
  insertedRowId: null,
  cleanupOk: null,
  fakeEmail: null,
  error: null,
  detail: null,
};

try {
  // 1. Anonymous sign-in
  const { data: authData, error: authError } = await supabase.auth.signInAnonymously();

  if (authError || !authData?.user) {
    result.error = "AUTH_FAILED";
    result.detail = authError?.message ?? "No user returned from signInAnonymously";
    console.log(JSON.stringify(result));
    process.exit(1);
  }

  result.authOk = true;
  result.userId = authData.user.id;

  if (noInsert) {
    result.ok = true;
    result.detail = "Auth succeeded, insert skipped (--no-insert)";
    console.log(JSON.stringify(result));
    process.exit(0);
  }

  // 2. Insert fake profile
  const ts = Date.now();
  const fakeEmail = `qa+mira-autopilot-${ts}@example.com`;
  result.fakeEmail = fakeEmail;

  const fakeProfile = {
    name: "MIRA Autopilot Dev Check",
    email: fakeEmail,
    height_cm: 180,
    weight_kg: 75,
    usual_size: "M",
    build: "regular",
    gender: "skip",
    auth_user_id: authData.user.id,
  };

  const { data: insertData, error: insertError } = await supabase
    .from("users_profile")
    .insert(fakeProfile)
    .select("id, auth_user_id")
    .single();

  if (insertError || !insertData) {
    result.error = "INSERT_FAILED";
    result.detail = insertError?.message ?? "No row returned from insert";
    console.log(JSON.stringify(result));
    process.exit(1);
  }

  result.insertOk = true;
  result.insertedRowId = insertData.id;

  // Verify auth_user_id
  if (insertData.auth_user_id !== authData.user.id) {
    result.error = "AUTH_USER_ID_MISMATCH";
    result.detail = "Inserted row auth_user_id does not match auth user id";
    console.log(JSON.stringify(result));
    process.exit(1);
  }

  // 3. Optional cleanup
  if (cleanupRow && insertData.id) {
    const { error: deleteError } = await supabase
      .from("users_profile")
      .delete()
      .eq("id", insertData.id);
    result.cleanupOk = !deleteError;
  }

  result.ok = true;
  result.detail = "Anonymous auth + fake profile insert succeeded";

} catch (err) {
  result.error = "UNEXPECTED";
  result.detail = err instanceof Error ? err.message : String(err);
}

console.log(JSON.stringify(result));
process.exit(result.ok ? 0 : 1);
