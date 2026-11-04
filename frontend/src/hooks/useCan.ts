import { createContext, useContext } from "react";
import { buildAbility, type AppAbility } from "@/lib/abilities";

export const AbilityContext = createContext<AppAbility>(buildAbility(undefined));

export function useAbility(): AppAbility {
  return useContext(AbilityContext);
}

export function useCan(action: Parameters<AppAbility["can"]>[0], subject: Parameters<AppAbility["can"]>[1]) {
  const ability = useAbility();
  return ability.can(action, subject);
}
