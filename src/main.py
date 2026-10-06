import sys


# ---------------------------------------------------------------- reading
def read_lines(path):
    """Read raw bytes, split on b'\\n', drop a final empty piece."""
    with open(path, "rb") as f:
        data = f.read()
    parts = data.split(b"\n")
    if parts and parts[-1] == b"":
        parts.pop()
    return parts


# ---------------------------------------------------------------- Myers core
def myers_core(a, b):
    """Classic Myers O(ND). Returns matched index pairs (i, j), increasing.

    Forward pass stores a copy of the V slice for each d (the 'trace'),
    then we walk back from (n, m) to (0, 0) to recover the snakes.
    """
    n, m = len(a), len(b)
    mx = n + m
    off = mx + 1
    V = [0] * (2 * mx + 3)
    trace = []
    found_d = -1
    for d in range(mx + 1):
        trace.append(V[off - d: off + d + 1])      # V as it was after round d-1
        for k in range(-d, d + 1, 2):
            if k == -d or (k != d and V[off + k - 1] < V[off + k + 1]):
                x = V[off + k + 1]                 # move down  (insertion)
            else:
                x = V[off + k - 1] + 1             # move right (deletion)
            y = x - k
            while x < n and y < m and a[x] == b[y]:  # follow the snake
                x += 1
                y += 1
            V[off + k] = x
            if x >= n and y >= m:
                found_d = d
                break
        if found_d >= 0:
            break

    # backtrack
    pairs = []
    x, y = n, m
    for d in range(found_d, 0, -1):
        vs = trace[d]                              # index = k + d
        k = x - y
        if k == -d or (k != d and vs[k - 1 + d] < vs[k + 1 + d]):
            pk = k + 1
            px = vs[pk + d]
            py = px - pk
            mxx, myy = px, py + 1
        else:
            pk = k - 1
            px = vs[pk + d]
            py = px - pk
            mxx, myy = px + 1, py
        for t in range(x - mxx - 1, -1, -1):       # reversed; list is reversed later
            pairs.append((mxx + t, myy + t))
        x, y = px, py
    for t in range(x - 1, -1, -1):                 # d == 0 leading snake
        pairs.append((t, t))
    pairs.reverse()
    return pairs


def lcs_pairs(a, b):
    """Matched pairs for any two sequences, with cheap speed-ups:
    strip common prefix/suffix, and drop elements that occur only in one side
    (they must be deleted/inserted anyway, so minimality is unaffected)."""
    n, m = len(a), len(b)
    p = 0
    while p < n and p < m and a[p] == b[p]:
        p += 1
    s = 0
    while s < n - p and s < m - p and a[n - 1 - s] == b[m - 1 - s]:
        s += 1
    pairs = [(i, i) for i in range(p)]

    ia, ib = a[p:n - s], b[p:m - s]
    if ia and ib:
        sa, sb = set(ia), set(ib)
        fa = [i for i, v in enumerate(ia) if v in sb]
        fb = [j for j, v in enumerate(ib) if v in sa]
        if fa and fb:
            xa = [ia[i] for i in fa]
            xb = [ib[j] for j in fb]
            for i, j in myers_core(xa, xb):
                pairs.append((p + fa[i], p + fb[j]))

    for t in range(s):
        pairs.append((n - s + t, m - s + t))
    return pairs


# ---------------------------------------------------------------- Part B
def gaps(length, matched):
    """Ranges NOT in `matched` (sorted indices) as 'a-b,c-d' or '.'"""
    out = []
    prev = 0
    for i in matched:
        if i > prev:
            out.append("%d-%d" % (prev, i))
        prev = i + 1
    if length > prev:
        out.append("%d-%d" % (prev, length))
    return ",".join(out) if out else "."


def highlight_line(old, new):
    x = old.decode("utf-8")
    y = new.decode("utf-8")
    pr = lcs_pairs(x, y)
    left = gaps(len(x), [i for i, _ in pr])
    right = gaps(len(y), [j for _, j in pr])
    return ("? %s | %s\n" % (left, right)).encode("ascii")


# ---------------------------------------------------------------- output
def build_output(A, B, hl):
    out = []
    pa = pb = 0

    def block(ai, bj):
        dels = A[pa:ai]
        ins = B[pb:bj]
        for l in dels:
            out.append(b"-" + l + b"\n")           # all '-' first
        for t, l in enumerate(ins):
            out.append(b"+" + l + b"\n")
            if hl and t < len(dels):               # pair 1st-1st, 2nd-2nd...
                out.append(highlight_line(dels[t], l))

    for ai, bj in lcs_pairs(A, B):
        block(ai, bj)
        out.append(b" " + A[ai] + b"\n")
        pa, pb = ai + 1, bj + 1
    block(len(A), len(B))
    return out


def main():
    if len(sys.argv) != 4 or sys.argv[1] not in ("lines", "highlight"):
        sys.stderr.write("usage: main.py lines|highlight A B\n")
        sys.exit(2)
    mode = sys.argv[1]
    try:
        A = read_lines(sys.argv[2])
        B = read_lines(sys.argv[3])
    except OSError as e:
        sys.stderr.write("error: %s\n" % e)
        sys.exit(2)
    out = build_output(A, B, mode == "highlight")
    sys.stdout.buffer.write(b"".join(out))


if __name__ == "__main__":
    main()
