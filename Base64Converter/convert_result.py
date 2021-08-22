# coding=utf-8
import sys


def main():
    content = sys.argv[1]
    line_index = content.find("|")
    content = content[line_index + 1:]
    sys.stdout.write(content)
    sys.stdout.flush()


if __name__ == '__main__':
    main()
