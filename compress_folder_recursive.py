"""
compress_folder_recursive.py — フォルダ内（サブフォルダ含む）の PNG / JPEG を
WebP に一括変換・元ファイル削除。除外フォルダを指定可能。

使い方:
  python compress_folder_recursive.py "ルートフォルダ" "除外フォルダ1" "除外フォルダ2" ...
  （除外フォルダはルート以下の絶対パスで指定）
"""
import sys
from pathlib import Path
from PIL import Image

WEBP_QUALITY = 75

def convert_to_webp(path: Path) -> tuple[int, int, Path]:
    original_size = path.stat().st_size
    out_path = path.with_suffix(".webp")

    img = Image.open(path)
    if img.mode not in ("RGB", "RGBA"):
        img = img.convert("RGBA" if "transparency" in img.info else "RGB")

    img.save(out_path, format="WEBP", quality=WEBP_QUALITY, method=6)
    new_size = out_path.stat().st_size

    path.unlink()

    return original_size, new_size, out_path


def is_excluded(path: Path, excluded: list[Path]) -> bool:
    return any(path == ex or ex in path.parents for ex in excluded)


def main():
    if len(sys.argv) < 2:
        print('使い方: python compress_folder_recursive.py "ルートフォルダ" ["除外フォルダ1" ...]')
        sys.exit(1)

    root = Path(sys.argv[1])
    excluded = [Path(p).resolve() for p in sys.argv[2:]]

    if not root.is_dir():
        print(f"フォルダが見つかりません: {root}")
        sys.exit(1)

    targets = []
    for p in root.rglob("*"):
        if p.is_dir():
            continue
        if p.suffix.lower() not in (".png", ".jpg", ".jpeg"):
            continue
        if is_excluded(p.parent.resolve(), excluded):
            continue
        targets.append(p)

    if not targets:
        print("対象ファイルなし")
        sys.exit(0)

    print(f"対象: {len(targets)} ファイル  →  WebP変換・元ファイル削除開始\n")
    if excluded:
        print("除外フォルダ:")
        for e in excluded:
            print(f"  - {e}")
        print()

    total_before = total_after = 0

    for p in sorted(targets):
        before, after, out = convert_to_webp(p)
        total_before += before
        total_after  += after
        saved_pct = (1 - after / before) * 100 if before else 0
        rel = p.relative_to(root)
        print(f"  {str(rel):<60} {before/1024/1024:.2f}MB -> {after/1024/1024:.2f}MB  (-{saved_pct:.1f}%)")

    print(f"\n合計: {total_before/1024/1024:.1f}MB -> {total_after/1024/1024:.1f}MB "
          f"(-{(1 - total_after/total_before)*100:.1f}%)")


if __name__ == "__main__":
    main()
