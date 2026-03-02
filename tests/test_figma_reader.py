"""Tests for the Figma Design-to-Code skill."""

import json
import sys
import unittest
from unittest.mock import MagicMock, patch

sys.path.insert(0, ".")
from skills.figma.figma_reader import FigmaReader, FigmaAPIError


# Sample Figma API responses for testing
SAMPLE_NODE = {
    "id": "1:2",
    "name": "Card",
    "type": "FRAME",
    "absoluteBoundingBox": {"x": 0, "y": 0, "width": 320, "height": 240},
    "fills": [{"type": "SOLID", "visible": True, "color": {"r": 1, "g": 1, "b": 1, "a": 1}}],
    "strokes": [],
    "cornerRadius": 12,
    "layoutMode": "VERTICAL",
    "itemSpacing": 16,
    "paddingTop": 24,
    "paddingRight": 24,
    "paddingBottom": 24,
    "paddingLeft": 24,
    "primaryAxisAlignItems": "MIN",
    "counterAxisAlignItems": "CENTER",
    "clipsContent": True,
    "effects": [
        {
            "type": "DROP_SHADOW",
            "visible": True,
            "color": {"r": 0, "g": 0, "b": 0, "a": 0.1},
            "offset": {"x": 0, "y": 4},
            "radius": 12,
        }
    ],
    "children": [
        {
            "id": "1:3",
            "name": "Title",
            "type": "TEXT",
            "characters": "Hello World",
            "fills": [{"type": "SOLID", "visible": True, "color": {"r": 0, "g": 0, "b": 0, "a": 1}}],
            "style": {
                "fontFamily": "Inter",
                "fontSize": 24,
                "fontWeight": 700,
                "lineHeightPx": 32,
                "textAlignHorizontal": "LEFT",
            },
            "absoluteBoundingBox": {"x": 24, "y": 24, "width": 272, "height": 32},
            "strokes": [],
            "effects": [],
            "children": [],
        },
        {
            "id": "1:4",
            "name": "Icon",
            "type": "VECTOR",
            "fills": [],
            "strokes": [],
            "effects": [],
            "absoluteBoundingBox": {"x": 24, "y": 64, "width": 24, "height": 24},
            "children": [],
        },
    ],
}

SAMPLE_FILE_RESPONSE = {
    "document": {
        "id": "0:0",
        "name": "Document",
        "type": "DOCUMENT",
        "children": [
            {
                "id": "0:1",
                "name": "Page 1",
                "type": "CANVAS",
                "children": [SAMPLE_NODE],
            }
        ],
    },
    "components": {
        "5:1": {"name": "Button/Primary", "description": "Primary action button", "key": "abc123"}
    },
    "styles": {
        "5:2": {"name": "Brand/Blue", "styleType": "FILL"},
        "5:3": {"name": "Heading/H1", "styleType": "TEXT"},
    },
}


class TestFigmaReader(unittest.TestCase):
    def setUp(self):
        self.reader = FigmaReader(token="test-token")

    def test_init_requires_token(self):
        with patch.dict("os.environ", {}, clear=True):
            with self.assertRaises(ValueError):
                FigmaReader(token="")

    def test_init_from_env(self):
        with patch.dict("os.environ", {"FIGMA_ACCESS_TOKEN": "env-token"}):
            r = FigmaReader()
            self.assertEqual(r.token, "env-token")

    @patch.object(FigmaReader, "_get_file", return_value=SAMPLE_FILE_RESPONSE)
    def test_extract_node_styles(self, mock_get):
        styles = self.reader.extract_node_styles("file123", "1:2")
        self.assertEqual(styles["width"], "320px")
        self.assertEqual(styles["height"], "240px")
        self.assertEqual(styles["background"], "#ffffff")
        self.assertEqual(styles["border-radius"], "12px")
        self.assertEqual(styles["display"], "flex")
        self.assertEqual(styles["flex-direction"], "column")
        self.assertEqual(styles["gap"], "16px")
        self.assertIn("box-shadow", styles)

    @patch.object(FigmaReader, "_get_file", return_value=SAMPLE_FILE_RESPONSE)
    def test_extract_text_styles(self, mock_get):
        styles = self.reader.extract_node_styles("file123", "1:3")
        self.assertEqual(styles["font-family"], "Inter")
        self.assertEqual(styles["font-size"], "24px")
        self.assertEqual(styles["font-weight"], "700")
        self.assertEqual(styles["color"], "#000000")

    @patch.object(FigmaReader, "_get_file", return_value=SAMPLE_FILE_RESPONSE)
    @patch.object(FigmaReader, "_get_images", return_value={
        "images": {"1:2": "https://figma.com/img1.png", "1:4": "https://figma.com/img2.png"}
    })
    def test_export_assets(self, mock_images, mock_get):
        assets = self.reader.export_assets("file123", "1:2", format="png", scale=2)
        self.assertEqual(len(assets), 2)
        self.assertEqual(assets[0]["format"], "png")
        self.assertTrue(assets[0]["url"].startswith("https://"))
        mock_images.assert_called_once()

    @patch.object(FigmaReader, "_get_file", return_value=SAMPLE_FILE_RESPONSE)
    def test_parse_design_tree(self, mock_get):
        dom = self.reader.parse_design_tree("file123", "1:2")
        self.assertEqual(dom["tag"], "div")
        self.assertIn("flex", dom["class"])
        self.assertIn("flex-col", dom["class"])
        self.assertIn("gap-4", dom["class"])
        self.assertIn("p-6", dom["class"])
        self.assertIn("rounded-xl", dom["class"])
        self.assertIn("overflow-hidden", dom["class"])
        self.assertEqual(len(dom["children"]), 2)
        # Text child
        text_child = dom["children"][0]
        self.assertEqual(text_child["tag"], "p")
        self.assertEqual(text_child["text"], "Hello World")
        self.assertIn("text-2xl", text_child["class"])
        self.assertIn("font-bold", text_child["class"])
        # Vector child
        svg_child = dom["children"][1]
        self.assertEqual(svg_child["tag"], "svg")

    @patch.object(FigmaReader, "_get_file", return_value=SAMPLE_FILE_RESPONSE)
    def test_list_components(self, mock_get):
        components = self.reader.list_components("file123")
        self.assertEqual(len(components), 1)
        self.assertEqual(components[0]["name"], "Button/Primary")
        self.assertEqual(components[0]["key"], "abc123")

    @patch.object(FigmaReader, "_get_file", return_value=SAMPLE_FILE_RESPONSE)
    def test_get_design_tokens(self, mock_get):
        tokens = self.reader.get_design_tokens("file123")
        self.assertIn("colors", tokens)
        self.assertIn("typography", tokens)
        self.assertIn("effects", tokens)

    def test_parse_color_solid(self):
        fill = {"type": "SOLID", "color": {"r": 1, "g": 0.337, "b": 0.2, "a": 1}}
        result = FigmaReader._parse_color(fill)
        self.assertEqual(result, "#ff5533")

    def test_parse_color_rgba(self):
        fill = {"type": "SOLID", "color": {"r": 0, "g": 0, "b": 0, "a": 0.5}}
        result = FigmaReader._parse_color(fill)
        self.assertEqual(result, "rgba(0, 0, 0, 0.50)")

    def test_parse_color_gradient(self):
        fill = {
            "type": "GRADIENT_LINEAR",
            "gradientStops": [
                {"color": {"r": 1, "g": 0, "b": 0, "a": 1}, "position": 0},
                {"color": {"r": 0, "g": 0, "b": 1, "a": 1}, "position": 1},
            ],
        }
        result = FigmaReader._parse_color(fill)
        self.assertTrue(result.startswith("linear-gradient("))

    def test_parse_typography(self):
        style = {
            "fontFamily": "Inter",
            "fontSize": 16,
            "fontWeight": 600,
            "lineHeightPx": 24,
            "letterSpacing": 0.5,
            "textAlignHorizontal": "CENTER",
        }
        result = FigmaReader._parse_typography(style)
        self.assertEqual(result["font-family"], "Inter")
        self.assertEqual(result["font-size"], "16px")
        self.assertEqual(result["text-align"], "center")

    def test_node_not_found_raises(self):
        with patch.object(self.reader, "_get_file", return_value=SAMPLE_FILE_RESPONSE):
            with self.assertRaises(ValueError):
                self.reader.extract_node_styles("file123", "nonexistent")

    def test_px_to_tw(self):
        self.assertEqual(FigmaReader._px_to_tw(16), "4")
        self.assertEqual(FigmaReader._px_to_tw(24), "6")
        self.assertEqual(FigmaReader._px_to_tw(0), "0")

    def test_color_to_tw(self):
        self.assertEqual(FigmaReader._color_to_tw("#ffffff"), "white")
        self.assertEqual(FigmaReader._color_to_tw("#000000"), "black")
        self.assertIsNone(FigmaReader._color_to_tw("#123456"))


if __name__ == "__main__":
    unittest.main()
