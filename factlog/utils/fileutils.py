from .strutils import get_lines_at_point


def write_paths_and_lines(
        file, paths, points, showpaths=None, newline='\n', separator=':',
        pre_lines=0, post_lines=0):
    if showpaths is None:
        showpaths = paths
    for (path, point, show) in zip(paths, points, showpaths):
        with open(path) as f:
            lines = get_lines_at_point(f.read(), point, pre_lines, post_lines)
        for (lineno, line) in lines:
            file.write(show)
            file.write(separator)
            file.write(str(lineno))
            file.write(separator)
            file.write(line)
            file.write(newline)
