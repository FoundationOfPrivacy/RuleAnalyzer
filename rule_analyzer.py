from pydriller import RepositoryMining

import argparse
import os
import datetime
import json


def should_ignore(line):
    return line.startswith('@@') or \
            line.startswith('##') or \
            '#?#' in line or \
            '#@#' in line


def parse_by_date(repo, bgn, end):
    lines = []

    miner = RepositoryMining(repo, since=bgn, to=end)
    for commit in miner.traverse_commits():
        for modification in commit.modifications:
            added = modification.diff_parsed['added']
            for item in added:
                line = item[1]
                if should_ignore(line):
                    continue
                lines.append(line)

    return lines


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--repo')
    parser.add_argument('--output')
    parser.add_argument('--month')
    parser.add_argument('--period')

    args = parser.parse_args()
    if not args.repo or not args.output or not args.month or not args.period:
        parser.print_help()
        return

    month = int(args.month)
    period = int(args.period)

    ranges = []
    bgn = 1
    while bgn < period:
        end = min(bgn + 6, period)
        ranges.append([bgn, end])
        bgn += 7

    report = {}
    index = 1
    for range in ranges:
        bgn = range[0]
        end = range[1]
        begin = datetime.datetime(2020, month, bgn, 0, 0)
        end = datetime.datetime(2020, month, end, 23, 59)
        print(f'Process the {index}th week...')
        lines = parse_by_date(args.repo, begin, end)

        path = os.path.join(args.output, f'{index}th.txt')
        with open(path, 'w') as hdle:
            for line in lines:
                out_line = f'{line}\n'
                hdle.write(out_line)

        report[index] = len(lines)
        index += 1

    path = os.path.join(args.output, 'report.json')
    with open(path, 'w') as hdle:
        json.dump(report, hdle)


if __name__ == "__main__":
    main()

