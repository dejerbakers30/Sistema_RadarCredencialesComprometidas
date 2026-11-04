import { AbilityBuilder, createMongoAbility, type MongoAbility } from "@casl/ability";

export type Action =
  | "read" | "write" | "export" | "generate" | "schedule"
  | "execute" | "admin" | "download";

export type Subject =
  | "dashboard" | "leaks" | "resets" | "reports"
  | "audit" | "users" | "roles" | "sources" | "config"
  | "notifications" | "profile";

export type AppAbility = MongoAbility<[Action, Subject]>;

const MATRIX: Record<string, [Action, Subject][]> = {
  admin: [
    ["read", "dashboard"], ["read", "leaks"], ["write", "leaks"], ["export", "leaks"],
    ["read", "resets"], ["execute", "resets"],
    ["read", "reports"], ["generate", "reports"], ["schedule", "reports"], ["download", "reports"],
    ["read", "audit"], ["export", "audit"],
    ["read", "users"], ["write", "users"], ["admin", "users"],
    ["read", "roles"], ["write", "roles"],
    ["read", "sources"], ["write", "sources"],
    ["admin", "config"],
    ["read", "notifications"], ["read", "profile"], ["write", "profile"],
  ],
  soc_analyst: [
    ["read", "dashboard"], ["read", "leaks"], ["write", "leaks"], ["export", "leaks"],
    ["read", "resets"], ["execute", "resets"],
    ["read", "reports"], ["generate", "reports"], ["download", "reports"],
    ["read", "audit"],
    ["read", "sources"],
    ["read", "notifications"], ["read", "profile"], ["write", "profile"],
  ],
  auditor: [
    ["read", "dashboard"], ["read", "leaks"], ["export", "leaks"],
    ["read", "resets"],
    ["read", "reports"], ["generate", "reports"], ["download", "reports"],
    ["read", "audit"], ["export", "audit"],
    ["read", "users"],
    ["read", "notifications"], ["read", "profile"], ["write", "profile"],
  ],
  end_user: [
    ["read", "dashboard"],
    ["read", "notifications"], ["read", "profile"], ["write", "profile"],
  ],
};

export function buildAbility(rol: string | undefined): AppAbility {
  const { can, build } = new AbilityBuilder<AppAbility>(createMongoAbility);
  const rules = MATRIX[rol ?? ""] ?? [];
  for (const [action, subject] of rules) {
    can(action, subject);
  }
  return build();
}
