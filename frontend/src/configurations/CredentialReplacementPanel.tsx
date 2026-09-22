import { CredentialIncidentPanel } from "./CredentialIncidentPanel";
import { Configuration } from "./api";

/** Dedicated boundary for credential replacement UI; incident handling remains shared. */
export function CredentialReplacementPanel({ configuration, onChanged }: { configuration: Configuration; onChanged: () => void }) {
  return <CredentialIncidentPanel configuration={configuration} onChanged={onChanged} />;
}
