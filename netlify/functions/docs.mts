// Every hour: the document agent looks at one official page, the one that has waited longest (netlify/lib/docs.mts).
// Claude reads it only if its text changed. A scheduled function: Netlify calls it, nobody else can.
import type { Config } from "@netlify/functions";
import { refreshDocs } from "../lib/store.mts";

export default async () => {
  try { await refreshDocs(); } catch (e) { console.error("docs failed", String(e).slice(0, 300)); }
};

export const config: Config = { schedule: "17 * * * *" };
