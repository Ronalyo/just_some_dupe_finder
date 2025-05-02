
import argparse
import sys

def unique_lines(stream, dup_out=None):
    prev = None
    for raw in stream:
        line = raw.rstrip('\n')
        if line != prev:
            prev = line
            yield line
        elif dup_out:
            # this was a “self-dupe” in this file
            dup_out.write(line + '\n')

def merge_files(file1, file2, out_file, dup_file=None):
    with open(file1, 'r') as f1, open(file2, 'r') as f2, open(out_file, 'w') as fout:
        dup_out = open(dup_file, 'w') if dup_file else None

        it1 = unique_lines(f1, dup_out)
        it2 = unique_lines(f2, dup_out)

        line1 = next(it1, '')
        line2 = next(it2, '')

        while line1 and line2:
            if line1 == line2:
                fout.write(line1 + '\n')
                if dup_out: dup_out.write(line1 + '\n')
                line1 = next(it1, '')
                line2 = next(it2, '')
            elif line1 < line2:
                fout.write(line1 + '\n')
                line1 = next(it1, '')
            else:
                fout.write(line2 + '\n')
                line2 = next(it2, '')

        # flush what's left (no need to check for duplicates across files any more)
        for rem, it in ((line1, it1), (line2, it2)):
            while rem:
                fout.write(rem + '\n')
                rem = next(it, '')

        if dup_out:
            dup_out.close()

def parse_args():
    p = argparse.ArgumentParser(
        description="Merge two sorted files into one deduplicated file."
    )
    p.add_argument('file1', help="First sorted input file")
    p.add_argument('file2', help="Second sorted input file")
    p.add_argument('outfile', nargs='?', help="Merged output file (default: merged.txt)")
    p.add_argument('--output', '-o',
                   help="Merged output file (overrides positional outfile)")
    p.add_argument('--dups', '-d', nargs='?', const='duplicates.txt',
                   help="Write duplicates to this file (default: duplicates.txt)")
    return p.parse_args()

def main():
    args = parse_args()

    # Determine merged output path
    out_path = args.output or args.outfile or 'merged.txt'
    dup_path = args.dups  # None if not specified

    try:
        merge_files(args.file1, args.file2, out_path, dup_path)
    except IOError as e:
        sys.exit(f"I/O error: {e}")

    print(f"Merged into: {out_path}")
    if dup_path:
        print(f"Duplicates recorded in: {dup_path}")

if __name__ == '__main__':
    main()
