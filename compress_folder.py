"""
compress_folder.py  —  フォルダ内の PNG / JPEG を WebP に一括変換・元ファイル削除
使い方: python compress_folder.py "D:\フォルダパス"
"""
import sys
from pathlib import Path
from PIL import Image

WEBP_QUALITY = 75  # 品質 (1-100)。低いほど小さく。75 で約70-80%削減が目安。

def convert_to_webp(path: Path) -> tuple[int, int, Path]:
    original_size = path.stat().st_size
    out_path = path.with_suffix(".webp")

    img = Image.open(path)
    if img.mode not in ("RGB", "RGBA"):
        img = img.convert("RGBA" if "transparency" in img.info else "RGB")

    img.save(out_path, format="WEBP", quality=WEBP_QUALITY, method=6)
    new_size = out_path.stat().st_size

    path.unlink()  # 元ファイル削除

    return original_size, new_size, out_path


def main():
    if len(sys.argv) < 2:
        print("使い方: python compress_folder.py \"フォルダパス\"")
        sys.exit(1)

    folder = Path(sys.argv[1])
    if not folder.is_dir():
        print(f"フォルダが見つかりません: {folder}")
        sys.exit(1)

    targets = [p for p in folder.iterdir()
               if p.is_file() and p.suffix.lower() in (".png", ".jpg", ".jpeg")]

    if not targets:
        print("対象ファイルなし")
        sys.exit(0)

    print(f"対象: {len(targets)} ファイル  →  WebP変換・元ファイル削除開始\n")
    total_before = total_after = 0

    for p in sorted(targets):
        before, after, out = convert_to_webp(p)
        total_before += before
        total_after  += after
        saved_pct = (1 - after / before) * 100 if before else 0
        print(f"  {p.name:<40} {before/1024/1024:.2f}MB → {after/1024/1024:.2f}MB  (-{saved_pct:.1f}%)  → {out.name}")

    print(f"\n合計: {total_before/1024/1024:.1f}MB → {total_after/1024/1024:.1f}MB "
          f"(-{(1 - total_after/total_before)*100:.1f}%)")


if __name__ == "__main__":
    main()
