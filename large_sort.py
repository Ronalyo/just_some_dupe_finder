
import argparse
import os
import tempfile
import heapq
import shutil

def chunk_and_sort(input_path, mem_limit_bytes):
    runs = []
    tempdir = tempfile.mkdtemp(prefix="sort_runs_")
    try:
        with open(input_path, 'r', encoding='utf-8', errors='ignore') as inf:
            chunk = []
            chunk_bytes = 0
            for line in inf:
                chunk.append(line)
                chunk_bytes += len(line.encode('utf-8'))
                # if our accumulated size exceeds the budget, flush it
                if chunk_bytes >= mem_limit_bytes:
                    chunk.sort()
                    run_path = os.path.join(tempdir, f"run_{len(runs):04d}.txt")
                    with open(run_path, 'w', encoding='utf-8') as outf:
                        outf.writelines(chunk)
                    runs.append(run_path)
                    chunk, chunk_bytes = [], 0
            # final partial chunk
            if chunk:
                chunk.sort()
                run_path = os.path.join(tempdir, f"run_{len(runs):04d}.txt")
                with open(run_path, 'w', encoding='utf-8') as outf:
                    outf.writelines(chunk)
                runs.append(run_path)
    except Exception:
        # Clean up on error
        shutil.rmtree(tempdir, ignore_errors=True)
        raise
    return runs, tempdir

def merge_runs(run_paths, output_path):
    # open all runs and prime the heap
    files = [open(p, 'r', encoding='utf-8', errors='ignore') for p in run_paths]
    heap = []
    for idx, f in enumerate(files):
        line = f.readline()
        if line:
            heapq.heappush(heap, (line, idx))

    with open(output_path, 'w', encoding='utf-8') as outf:
        while heap:
            smallest, idx = heapq.heappop(heap)
            outf.write(smallest)
            nxt = files[idx].readline()
            if nxt:
                heapq.heappush(heap, (nxt, idx))

    for f in files:
        f.close()

def parse_args():
    p = argparse.ArgumentParser(description="External‐memory sort of a big text file.")
    p.add_argument('--input',      '-i', required=True, help="Path to unsorted input file")
    p.add_argument('--output',     '-o', required=True, help="Path to write sorted output")
    p.add_argument('--memory-limit','-m', type=int, default=100,
                   help="Approx max RAM to use for chunking, in MB (default: 100)")
    return p.parse_args()

def main():
    args = parse_args()
    mem_bytes = args.memory_limit * 1024 * 1024

    print(f"[+] Generating sorted runs (≤{args.memory_limit} MB each)…")
    run_paths, tempdir = chunk_and_sort(args.input, mem_bytes)
    print(f"[+] Created {len(run_paths)} runs in {tempdir!r}")

    print("[+] Merging runs into final output…")
    merge_runs(run_paths, args.output)
    print(f"[+] Sorted file written to {args.output!r}")

    # clean up temp files
    shutil.rmtree(tempdir)
    print(f"[+] Removed temporary directory {tempdir!r}")

if __name__ == '__main__':
    main()
