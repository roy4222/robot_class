"""
把指定檔案塞進一份 ODT 的 attachments/ 資料夾，並更新 manifest.xml
讓 LibreOffice / Pages 能正確識別。

用法：
    python3 scripts/pack_odt_with_attachments.py

產出：
    reports/week08-pic-digits/交檔_week08_成果報告.odt
"""

import shutil
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REPORT_DIR = ROOT / "reports/week08-pic-digits"
SRC_ODT = REPORT_DIR / "week08_成果報告.odt"
OUT_ODT = REPORT_DIR / "交檔_week08_成果報告.odt"

ATTACHMENTS = [
    REPORT_DIR / "assets/pic_digits_dataset_v2.zip",
    REPORT_DIR / "assets/pic_digits_model_v2.mdl",
]

MEDIA_TYPES = {
    ".zip": "application/zip",
    ".mdl": "application/octet-stream",
    ".png": "image/png",
    ".jpg": "image/jpeg",
}


def media_type(path: Path) -> str:
    return MEDIA_TYPES.get(path.suffix.lower(), "application/octet-stream")


def main() -> None:
    if not SRC_ODT.exists():
        raise SystemExit(f"找不到來源 ODT: {SRC_ODT}")
    for a in ATTACHMENTS:
        if not a.exists():
            raise SystemExit(f"找不到附件: {a}")

    # 讀原 ODT 的所有 entries
    with zipfile.ZipFile(SRC_ODT, "r") as zf:
        entries = [(info, zf.read(info.filename)) for info in zf.infolist()]

    # 取出 manifest.xml 並插入附件宣告
    manifest_idx = next(i for i, (info, _) in enumerate(entries)
                         if info.filename == "META-INF/manifest.xml")
    manifest_xml = entries[manifest_idx][1].decode("utf-8")

    new_lines = []
    for a in ATTACHMENTS:
        arc = f"attachments/{a.name}"
        mt = media_type(a)
        new_lines.append(
            f' <manifest:file-entry manifest:full-path="{arc}" '
            f'manifest:media-type="{mt}"/>'
        )

    closing = "</manifest:manifest>"
    if closing not in manifest_xml:
        raise SystemExit("manifest.xml 格式異常，找不到結尾 tag")
    manifest_xml = manifest_xml.replace(
        closing, "\n" + "\n".join(new_lines) + "\n" + closing
    )
    entries[manifest_idx] = (entries[manifest_idx][0],
                             manifest_xml.encode("utf-8"))

    # 寫新 ODT：先寫 mimetype（ODF 規定要第一個、不壓縮），再寫其他
    with zipfile.ZipFile(OUT_ODT, "w", zipfile.ZIP_DEFLATED) as zf:
        # 先寫 mimetype（無壓縮，符合 ODF spec）
        for info, data in entries:
            if info.filename == "mimetype":
                zf.writestr(
                    zipfile.ZipInfo("mimetype"), data,
                    compress_type=zipfile.ZIP_STORED,
                )
                break

        # 寫其餘原始 entries
        for info, data in entries:
            if info.filename == "mimetype":
                continue
            zf.writestr(info, data)

        # 塞附件
        for a in ATTACHMENTS:
            arc = f"attachments/{a.name}"
            zf.write(a, arcname=arc)
            print(f"  + {arc}  ({a.stat().st_size:,} bytes)")

    size = OUT_ODT.stat().st_size
    print(f"\n[ok] {OUT_ODT.relative_to(ROOT)}  ({size:,} bytes)")


if __name__ == "__main__":
    main()
