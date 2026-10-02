"""Build an immutable local ADHD-02 corpus. Author: Codex / GPT-6, 2026-10-02.
No downloads, source/frozen changes, exam text inspection or model training.
"""
import datetime as dt
import json
from pathlib import Path
import subprocess
import sys

from common import ROOT, atomic_json, assert_space, sha256

STYLES = ['summary', 'plain', 'facts', 'news']
OUT = ROOT / 'data/train/adhd-02/train_original_plus_rewrites.jsonl'
RECORD = ROOT / 'experiments/adhd-02/dataset_manifest.json'


def read(path):
    return json.loads(path.read_text(encoding='utf-8'))


def build_rows(source, entries, eligible):
    if set(entries) != set(eligible):
        raise ValueError('rewrite PMCID set differs from frozen eligible papers')
    rows = [json.loads(line) for line in source.splitlines() if line.strip()]
    if not rows or any(set(r) != {'text'} or not r['text'] for r in rows):
        raise ValueError('original training corpus has an unexpected schema')
    for pmcid in sorted(eligible):
        entry = entries[pmcid]
        if entry.get('pmcid') != pmcid or not entry.get('generator') or not entry.get('created'):
            raise ValueError('invalid source author/PMCID/date metadata')
        rewrites = entry.get('rewrites', [])
        if [r.get('style') for r in rewrites] != STYLES:
            raise ValueError('rewrite styles differ from declared order')
        for rewrite in rewrites:
            text = rewrite.get('text', '')
            if not 250 <= len(text.split()) <= 600 or '2026' not in text:
                raise ValueError('rewrite fails declared word/year constraints')
            rows.append({'text': text, 'pmcid': pmcid, 'style': rewrite['style'],
                         'generator': entry['generator'], 'kind': 'blind_rewrite'})
    return rows


def main():
    roles = read(ROOT / 'eval/pmc_roles.json')
    split = read(ROOT / 'experiments/adhd-01/split.json')
    eligible = set(split['train_new_pmcids'])
    assert len(eligible) == 269 and eligible == set(roles['new_train'])
    assert eligible.isdisjoint(split['valid_pmcids'])
    heldout = set(roles['new_heldout'])
    assert eligible.isdisjoint(heldout)
    source = ROOT / split['outputs']['train_new']['path']
    valid = ROOT / split['outputs']['valid']['path']
    assert sha256(source) == split['outputs']['train_new']['sha256']
    assert sha256(valid) == split['outputs']['valid']['sha256']
    outdir = ROOT / 'data/augment/adhd-02/rewrites'
    paths = {p.stem: p for p in outdir.glob('PMC*.json')}
    assert set(paths) == eligible
    checked = subprocess.run([sys.executable, 'scripts/augment_check.py', 'stats'],
                             cwd=ROOT, capture_output=True, text=True, check=True)
    print(checked.stdout, end='', flush=True)
    assert checked.stdout.strip() == '269 / 269 written; 269 pass, 0 fail'
    rows = build_rows(source.read_text(encoding='utf-8'), {k: read(v) for k,v in paths.items()}, eligible)
    payload = ''.join(json.dumps(row, ensure_ascii=False) + '\n' for row in rows)
    assert_space(len(payload.encode('utf-8')))
    OUT.parent.mkdir(parents=True, exist_ok=True)
    if OUT.exists():
        assert OUT.read_text(encoding='utf-8') == payload, 'refuse to overwrite an existing different corpus'
    else:
        with OUT.open('x', encoding='utf-8') as stream:
            stream.write(payload)
    from transformers import AutoTokenizer
    tok = AutoTokenizer.from_pretrained(ROOT / 'models/qwen3-0.6b-base', local_files_only=True)
    original_count = split['outputs']['train_new']['chunks']
    assert len(rows) == original_count + 1076
    counts = {kind: sum(len(tok.encode(r['text'], add_special_tokens=False)) + 1 for r in selection)
              for kind, selection in [('original',rows[:original_count]),('rewrites',rows[original_count:])]}
    downloads = {d['path']: d for d in read(ROOT / 'manifest.json')['downloads']}
    sources = []
    for pmcid in sorted(eligible):
        source_path = f'data/raw/pmc/{pmcid}.xml'
        d = downloads[source_path]
        assert sha256(ROOT / source_path) == d['sha256'], 'raw licensed source changed'
        sources.append({'pmcid':pmcid,'raw_path':source_path,'raw_sha256':d['sha256'],
                        'source_license':d.get('license'),'source_url':d.get('url'),
                        'rewrite_path':str(paths[pmcid].relative_to(ROOT)),
                        'rewrite_sha256':sha256(paths[pmcid]),'generator':read(paths[pmcid])['generator']})
    inputs = {str(p.relative_to(ROOT)):sha256(p) for p in [source,valid,ROOT/'eval/pmc_roles.json',
              ROOT/'eval/benchmark_exclusions.json',ROOT/'experiments/adhd-01/split.json']}
    record = {'experiment_id':'ADHD-02','author':'Codex / GPT-6 (root)',
              'created':dt.datetime.now(dt.timezone.utc).isoformat(),'purpose':'DAPT',
              'artifact':{'path':str(OUT.relative_to(ROOT)),'sha256':sha256(OUT),'bytes':OUT.stat().st_size,
                          'papers':len(eligible),'original_chunks':original_count,'rewrite_texts':1076,
                          'rows':len(rows),'token_stream_counts_including_eos':counts,
                          'total_stream_tokens':sum(counts.values()),'packed_1024_windows':sum(counts.values())//1024},
              'inputs':inputs,'source_papers':sources,'filter':'same frozen new_train papers only; 269/269 approved checker PASS; 250-600 words; four fixed styles; no held-out/validation/exam input',
              'downloaded':False,'local_derivative':True,'license_note':'Source-paper licenses remain applicable; preserve actual synthetic-text authorship. This local derivative is not approved for public redistribution and is not relicensed as project code.',
              'safe_to_delete':'Generated combined JSONL is regenerable from frozen original chunks and retained rewrites; preserve this manifest and original rewrite files.',
              'rebuild':'.venv/bin/python scripts/prepare_adhd02.py','no_network_required':True}
    if RECORD.exists():
        old = read(RECORD)
        assert old['artifact'] == record['artifact'] and old['inputs'] == inputs and old['source_papers'] == sources
    else:
        atomic_json(RECORD, record)
    print(json.dumps(record['artifact'], indent=2))


if __name__ == '__main__':
    main()
