from pathlib import Path
from app.core.util.paths import class_output_dir, new_learner_dir

def test_class_output_dir(tmp_path):
    path = class_output_dir(str(tmp_path), 'Standort', 'Klasse')
    assert path.exists()
    assert path == tmp_path / 'Standort' / 'Klasse'

def test_new_learner_dir(tmp_path):
    path = new_learner_dir(str(tmp_path), 'Standort', 'Klasse')
    assert path.exists()
    assert path == tmp_path / 'Neue Lernende' / 'Standort' / 'Klasse'
