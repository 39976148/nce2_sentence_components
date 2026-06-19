import json
from pathlib import Path

from nce2_core.batch import batch_import_book2


def test_batch_import_lesson1(tmp_path: Path):
    root = Path(__file__).resolve().parents[1]
    titles_path = root / "data" / "titles.json"
    txt_dir = root / "nce_txt" / "第二册"
    out_dir = tmp_path / "lessons"
    batch_import_book2(txt_dir, titles_path, out_dir, lessons=[1])
    out_file = out_dir / "01.json"
    assert out_file.exists()
    data = json.loads(out_file.read_text(encoding="utf-8"))
    assert data["lesson"] == 1
    assert len(data["sentences"]) >= 14
