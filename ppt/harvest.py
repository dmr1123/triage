# -*- coding: utf-8 -*-
"""Harvest StructuredOutput objects from workflow agent transcripts -> papers.json.
Robust to the journal 'null' display quirk: reads the actual tool_use inputs."""
import json, glob, sys, os

WF_DIR = "/root/.claude/projects/-home-user-triage/81904d19-c7ea-558a-bc6f-a38da28e81b7/subagents/workflows/wf_1b318dad-de5"

def extract(f):
    obj = None
    for line in open(f):
        try:
            o = json.loads(line)
        except Exception:
            continue
        for c in (o.get('message', {}).get('content') or []):
            if isinstance(c, dict) and c.get('type') == 'tool_use' and c.get('name') == 'StructuredOutput':
                obj = c['input']  # keep last (final) one
    return obj

def main():
    papers = {}
    for f in sorted(glob.glob(os.path.join(WF_DIR, "agent-*.jsonl"))):
        d = extract(f)
        if d and d.get('paperKey'):
            papers[d['paperKey']] = d
    order = ['smart-triage', 'piers-on-the-move', 'e-covig', 'joseph-ed-dl', 'hoffman-camera-oximetry']
    out = [papers[k] for k in order if k in papers]
    # append any not in the known order
    for k, v in papers.items():
        if k not in order:
            out.append(v)
    dst = "/home/user/triage/ppt/papers.json"
    with open(dst, "w") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=2)
    print(f"harvested {len(out)} papers -> {dst}")
    for p in out:
        print(f"  - {p.get('paperKey')}: {len(json.dumps(p, ensure_ascii=False))} chars")

if __name__ == "__main__":
    main()
