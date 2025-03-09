""" text_elevator_cd_pdf.py - test Starr and xUML notation Elevator class diagram pdf output"""

import pytest
from pathlib import Path
from xcm_parser.class_model_parser import ClassModelParser

diagrams = [
    "elevator",
    "intersection",
    "sheet",
    "ego",
    "lane_reconfig",
    "crosswalk",
    "type"
]

@pytest.mark.parametrize("model", diagrams)
def test_Starr_pdf(model):

    input_path = Path(__file__).parent / f"models/{model}.xcm"
    result = ClassModelParser.parse_file(file_input=input_path, debug=False)
    assert result
