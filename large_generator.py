
import argparse
import random
import string
import sys

def generate_large_file(
    filename: str,
    total_lines: int,
    min_len: int,
    max_len: int,
    chunk_size: int
) -> None:
    letters = string.ascii_lowercase
    written = 0

    with open(filename, 'w') as f:
        while written < total_lines:
            batch = min(chunk_size, total_lines - written)
            # build one chunk in memory
            chunk = [
                ''.join(random.choices(letters, k=random.randint(min_len, max_len)))
                for _ in range(batch)
            ]
            f.write('\n'.join(chunk))
            f.write('\n')
            written += batch

            # optional progress to stderr
            print(f"\rWritten {written}/{total_lines} lines", end='', file=sys.stderr)
    print("\nDone.", file=sys.stderr)

def parse_args():
    p = argparse.ArgumentParser(
        description="Generate a huge file of random alphabetical strings, one per line."
    )
    p.add_argument(
        '-o', '--output', required=True,
        help="Path to the output text file."
    )
    p.add_argument(
        '-n', '--lines', type=int, required=True,
        help="Total number of lines (strings) to generate."
    )
    p.add_argument(
        '--min-len', type=int, default=5,
        help="Minimum length of each random string (default: 5)."
    )
    p.add_argument(
        '--max-len', type=int, default=20,
        help="Maximum length of each random string (default: 20)."
    )
    p.add_argument(
        '-c', '--chunk-size', type=int,
        help="Number of lines to buffer before writing."
    )

    return p.parse_args()

def main():
    args = parse_args()

    if args.chunk_size is not None:
        chunk_size = args.chunk_size
    else:
        # default chunk size
        chunk_size = 10_000

    if args.min_len < 1 or args.max_len < args.min_len:
        print("ERROR: --max-len must be >= --min-len >= 1", file=sys.stderr)
        sys.exit(1)

    print(f"Generating {args.lines} lines of length [{args.min_len}, {args.max_len}],",
          f"buffer={chunk_size} lines per write...", file=sys.stderr)

    generate_large_file(
        filename=args.output,
        total_lines=args.lines,
        min_len=args.min_len,
        max_len=args.max_len,
        chunk_size=chunk_size
    )

if __name__ == '__main__':
    main()
