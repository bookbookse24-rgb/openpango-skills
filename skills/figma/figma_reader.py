"""
Figma API Design-to-Code Integration

Reads Figma files via the REST API and translates design data into
code-ready formats: CSS-like style dicts, simplified DOM trees with
Tailwind classes, and exportable assets.

Bounty: openpango/openpango-skills#37
"""

import json
import os
import sys
import urllib.error
import urllib.request
from typing import Any, Optional


FIGMA_API_BASE = "https://api.figma.com/v1"


class FigmaAPIError(Exception):
    """Raised when a Figma API call fails."""

    def __init__(self, status: int, message: str):
        self.status = status
        super().__init__(f"Figma API error {status}: {message}")


class FigmaReader:
    """Client for reading Figma files and converting designs to code."""

    def __init__(self, token: Optional[str] = None):
        self.token = token or os.environ.get("FIGMA_ACCESS_TOKEN", "")
        if not self.token:
            raise ValueError(
                "Figma access token required. Set FIGMA_ACCESS_TOKEN or pass token= argument."
            )

    # ------------------------------------------------------------------ #
    #  Low-level API helpers
    # ------------------------------------------------------------------ #

    def _request(self, path: str, params: Optional[dict] = None) -> dict:
        """Make an authenticated GET request to the Figma API."""
        url = f"{FIGMA_API_BASE}/{path}"
        if params:
            qs = "&".join(f"{k}={v}" for k, v in params.items() if v is not None)
            if qs:
                url = f"{url}?{qs}"

        req = urllib.request.Request(url, headers={"X-Figma-Token": self.token})
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                return json.loads(resp.read().decode())
        except urllib.error.HTTPError as exc:
            body = exc.read().decode() if exc.fp else ""
            raise FigmaAPIError(exc.code, body) from exc

    def _get_file(self, file_id: str) -> dict:
        """Fetch the full Figma file document."""
        return self._request(f"files/{file_id}")

    def _get_file_nodes(self, file_id: str, node_ids: list[str]) -> dict:
        """Fetch specific nodes from a Figma file."""
        ids = ",".join(node_ids)
        return self._request(f"files/{file_id}/nodes", {"ids": ids})

    def _get_images(
        self,
        file_id: str,
        node_ids: list[str],
        fmt: str = "png",
        scale: float = 1,
    ) -> dict:
        """Request rendered image exports for nodes."""
        ids = ",".join(node_ids)
        return self._request(
            f"images/{file_id}",
            {"ids": ids, "format": fmt, "scale": str(scale)},
        )

    # ------------------------------------------------------------------ #
    #  Node traversal
    # ------------------------------------------------------------------ #

    @staticmethod
    def _find_node(root: dict, node_id: str) -> Optional[dict]:
        """DFS to find a node by its id within a tree."""
        if root.get("id") == node_id:
            return root
        for child in root.get("children", []):
            found = FigmaReader._find_node(child, node_id)
            if found:
                return found
        return None

    def _resolve_node(self, file_id: str, node_id: Optional[str]) -> dict:
        """Return the Figma node dict, fetching the file if needed."""
        data = self._get_file(file_id)
        document = data.get("document", {})
        if node_id is None:
            return document
        node = self._find_node(document, node_id)
        if node is None:
            raise ValueError(f"Node {node_id!r} not found in file {file_id!r}")
        return node

    # ------------------------------------------------------------------ #
    #  Public tools
    # ------------------------------------------------------------------ #

    def extract_node_styles(self, file_id: str, node_id: str) -> dict:
        """
        Extract CSS-like styles from a Figma node.

        Returns a flat dict like:
            {"width": "320px", "height": "240px", "background": "#FF5733", ...}
        """
        node = self._resolve_node(file_id, node_id)
        return self._node_to_css(node)

    def export_assets(
        self,
        file_id: str,
        node_id: str,
        format: str = "png",
        scale: float = 2,
    ) -> list[dict]:
        """
        Export rendered images/SVGs for a node and its direct children.

        Returns a list of dicts:
            [{"node_id": "1:23", "url": "https://...", "format": "png"}, ...]
        """
        node = self._resolve_node(file_id, node_id)
        ids = [node["id"]]
        for child in node.get("children", []):
            if child.get("type") in (
                "COMPONENT",
                "INSTANCE",
                "VECTOR",
                "BOOLEAN_OPERATION",
                "STAR",
                "LINE",
                "ELLIPSE",
                "REGULAR_POLYGON",
            ):
                ids.append(child["id"])

        resp = self._get_images(file_id, ids, fmt=format, scale=scale)
        images = resp.get("images", {})
        return [
            {"node_id": nid, "url": url, "format": format}
            for nid, url in images.items()
            if url
        ]

    def parse_design_tree(
        self, file_id: str, node_id: Optional[str] = None
    ) -> dict:
        """
        Convert a Figma subtree into a simplified DOM-like structure.

        Each element has:
            {"tag": "div", "class": "flex gap-4 p-6 ...", "styles": {...},
             "text": "...", "children": [...]}
        """
        node = self._resolve_node(file_id, node_id)
        return self._node_to_dom(node)

    def list_components(self, file_id: str) -> list[dict]:
        """
        List all reusable components defined in a Figma file.

        Returns:
            [{"id": "1:23", "name": "Button/Primary", "description": "..."}, ...]
        """
        data = self._get_file(file_id)
        components = data.get("components", {})
        return [
            {
                "id": cid,
                "name": meta.get("name", ""),
                "description": meta.get("description", ""),
                "key": meta.get("key", ""),
            }
            for cid, meta in components.items()
        ]

    def get_design_tokens(self, file_id: str) -> dict:
        """
        Extract design tokens (colors, typography, spacing) from a file's styles.

        Returns:
            {"colors": {...}, "typography": {...}, "effects": {...}}
        """
        data = self._get_file(file_id)
        styles = data.get("styles", {})
        document = data.get("document", {})

        tokens: dict[str, dict] = {"colors": {}, "typography": {}, "effects": {}}

        for style_id, style_meta in styles.items():
            name = style_meta.get("name", style_id)
            stype = style_meta.get("styleType", "")

            # Find the node that defines this style to extract actual values
            node = self._find_node(document, style_id)

            if stype == "FILL":
                fills = (node or {}).get("fills", [])
                if fills:
                    tokens["colors"][name] = self._parse_color(fills[0])
            elif stype == "TEXT":
                ts = (node or {}).get("style", {})
                tokens["typography"][name] = self._parse_typography(ts)
            elif stype == "EFFECT":
                effects = (node or {}).get("effects", [])
                tokens["effects"][name] = [
                    self._parse_effect(e) for e in effects
                ]

        return tokens

    # ------------------------------------------------------------------ #
    #  Style extraction helpers
    # ------------------------------------------------------------------ #

    @staticmethod
    def _parse_color(fill: dict) -> str:
        """Convert a Figma fill to a CSS color string."""
        if fill.get("type") == "SOLID":
            c = fill.get("color", {})
            r = int(c.get("r", 0) * 255)
            g = int(c.get("g", 0) * 255)
            b = int(c.get("b", 0) * 255)
            a = c.get("a", 1)
            if a < 1:
                return f"rgba({r}, {g}, {b}, {a:.2f})"
            return f"#{r:02x}{g:02x}{b:02x}"
        if fill.get("type") in ("GRADIENT_LINEAR", "GRADIENT_RADIAL"):
            stops = fill.get("gradientStops", [])
            parts = []
            for s in stops:
                col = FigmaReader._parse_color({"type": "SOLID", "color": s.get("color", {})})
                pos = s.get("position", 0)
                parts.append(f"{col} {pos * 100:.0f}%")
            kind = "linear-gradient" if fill["type"] == "GRADIENT_LINEAR" else "radial-gradient"
            return f"{kind}({', '.join(parts)})"
        return "transparent"

    @staticmethod
    def _parse_typography(style: dict) -> dict:
        """Convert Figma text style to CSS typography properties."""
        result = {}
        if "fontFamily" in style:
            result["font-family"] = style["fontFamily"]
        if "fontSize" in style:
            result["font-size"] = f"{style['fontSize']}px"
        if "fontWeight" in style:
            result["font-weight"] = str(style["fontWeight"])
        if "lineHeightPx" in style:
            result["line-height"] = f"{style['lineHeightPx']}px"
        if "letterSpacing" in style:
            result["letter-spacing"] = f"{style['letterSpacing']}px"
        if "textAlignHorizontal" in style:
            mapping = {"LEFT": "left", "CENTER": "center", "RIGHT": "right", "JUSTIFIED": "justify"}
            result["text-align"] = mapping.get(style["textAlignHorizontal"], "left")
        return result

    @staticmethod
    def _parse_effect(effect: dict) -> dict:
        """Convert a Figma effect to CSS box-shadow / filter."""
        etype = effect.get("type", "")
        result = {"type": etype, "visible": effect.get("visible", True)}
        if etype in ("DROP_SHADOW", "INNER_SHADOW"):
            c = effect.get("color", {})
            color = FigmaReader._parse_color({"type": "SOLID", "color": c})
            offset = effect.get("offset", {})
            result["css"] = (
                f"{'inset ' if etype == 'INNER_SHADOW' else ''}"
                f"{offset.get('x', 0)}px {offset.get('y', 0)}px "
                f"{effect.get('radius', 0)}px {color}"
            )
        elif etype == "LAYER_BLUR":
            result["css"] = f"blur({effect.get('radius', 0)}px)"
        elif etype == "BACKGROUND_BLUR":
            result["css"] = f"backdrop-filter: blur({effect.get('radius', 0)}px)"
        return result

    def _node_to_css(self, node: dict) -> dict:
        """Extract all CSS-like properties from a single Figma node."""
        css: dict[str, str] = {}
        ntype = node.get("type", "")

        # Dimensions
        bbox = node.get("absoluteBoundingBox", {})
        if bbox:
            css["width"] = f"{bbox.get('width', 0):.0f}px"
            css["height"] = f"{bbox.get('height', 0):.0f}px"

        # Background fills
        fills = node.get("fills", [])
        visible_fills = [f for f in fills if f.get("visible", True)]
        if visible_fills:
            css["background"] = self._parse_color(visible_fills[0])

        # Strokes
        strokes = node.get("strokes", [])
        visible_strokes = [s for s in strokes if s.get("visible", True)]
        if visible_strokes:
            sw = node.get("strokeWeight", 1)
            color = self._parse_color(visible_strokes[0])
            css["border"] = f"{sw}px solid {color}"

        # Border radius
        cr = node.get("cornerRadius")
        if cr:
            css["border-radius"] = f"{cr}px"
        elif node.get("rectangleCornerRadii"):
            radii = node["rectangleCornerRadii"]
            css["border-radius"] = " ".join(f"{r}px" for r in radii)

        # Opacity
        opacity = node.get("opacity")
        if opacity is not None and opacity < 1:
            css["opacity"] = f"{opacity:.2f}"

        # Layout (auto-layout / flex)
        layout_mode = node.get("layoutMode")
        if layout_mode:
            css["display"] = "flex"
            css["flex-direction"] = "column" if layout_mode == "VERTICAL" else "row"
            gap = node.get("itemSpacing", 0)
            if gap:
                css["gap"] = f"{gap}px"

        # Padding
        pt = node.get("paddingTop", 0)
        pr = node.get("paddingRight", 0)
        pb = node.get("paddingBottom", 0)
        pl = node.get("paddingLeft", 0)
        if any([pt, pr, pb, pl]):
            css["padding"] = f"{pt}px {pr}px {pb}px {pl}px"

        # Alignment
        primary = node.get("primaryAxisAlignItems")
        counter = node.get("counterAxisAlignItems")
        if primary:
            mapping = {"MIN": "flex-start", "CENTER": "center", "MAX": "flex-end", "SPACE_BETWEEN": "space-between"}
            css["justify-content"] = mapping.get(primary, primary.lower())
        if counter:
            mapping = {"MIN": "flex-start", "CENTER": "center", "MAX": "flex-end"}
            css["align-items"] = mapping.get(counter, counter.lower())

        # Text
        if ntype == "TEXT":
            ts = node.get("style", {})
            css.update(self._parse_typography(ts))
            fills = node.get("fills", [])
            if fills:
                css["color"] = self._parse_color(fills[0])

        # Effects (shadows, blurs)
        effects = node.get("effects", [])
        shadows = []
        filters = []
        for e in effects:
            if not e.get("visible", True):
                continue
            parsed = self._parse_effect(e)
            if e["type"] in ("DROP_SHADOW", "INNER_SHADOW"):
                shadows.append(parsed.get("css", ""))
            elif e["type"] == "LAYER_BLUR":
                filters.append(parsed.get("css", ""))
        if shadows:
            css["box-shadow"] = ", ".join(shadows)
        if filters:
            css["filter"] = " ".join(filters)

        return css

    # ------------------------------------------------------------------ #
    #  DOM tree builder
    # ------------------------------------------------------------------ #

    # Tailwind spacing scale (approximate)
    _TW_SPACING = {
        0: "0", 1: "px", 2: "0.5", 4: "1", 6: "1.5", 8: "2",
        10: "2.5", 12: "3", 14: "3.5", 16: "4", 20: "5", 24: "6",
        28: "7", 32: "8", 36: "9", 40: "10", 44: "11", 48: "12",
        56: "14", 64: "16", 80: "20", 96: "24",
    }

    @classmethod
    def _px_to_tw(cls, px: float) -> str:
        """Convert pixel value to nearest Tailwind spacing class value."""
        px = round(px)
        if px in cls._TW_SPACING:
            return cls._TW_SPACING[px]
        # Find nearest
        closest = min(cls._TW_SPACING.keys(), key=lambda k: abs(k - px))
        return cls._TW_SPACING[closest]

    @staticmethod
    def _color_to_tw(color_str: str) -> Optional[str]:
        """Best-effort hex color to Tailwind color class."""
        # Common mappings
        tw_colors = {
            "#000000": "black", "#ffffff": "white",
            "#ef4444": "red-500", "#f97316": "orange-500",
            "#eab308": "yellow-500", "#22c55e": "green-500",
            "#3b82f6": "blue-500", "#8b5cf6": "violet-500",
            "#6b7280": "gray-500", "#9ca3af": "gray-400",
            "#d1d5db": "gray-300", "#f3f4f6": "gray-100",
            "#f9fafb": "gray-50", "#111827": "gray-900",
        }
        lower = color_str.lower().strip()
        if lower in tw_colors:
            return tw_colors[lower]
        return None

    def _node_to_dom(self, node: dict) -> dict:
        """Recursively convert a Figma node tree to a simplified DOM."""
        ntype = node.get("type", "")
        name = node.get("name", "")
        result: dict[str, Any] = {}

        # Determine HTML tag
        if ntype == "TEXT":
            result["tag"] = "p"
            result["text"] = node.get("characters", "")
        elif ntype in ("COMPONENT", "INSTANCE", "FRAME", "GROUP", "SECTION"):
            result["tag"] = "div"
        elif ntype == "VECTOR":
            result["tag"] = "svg"
        elif ntype in ("RECTANGLE", "ELLIPSE", "LINE", "STAR", "REGULAR_POLYGON"):
            result["tag"] = "div"
        elif ntype == "BOOLEAN_OPERATION":
            result["tag"] = "svg"
        else:
            result["tag"] = "div"

        # Build Tailwind class string
        classes = self._build_tailwind_classes(node)
        if classes:
            result["class"] = " ".join(classes)

        # Inline styles for anything Tailwind can't express
        css = self._node_to_css(node)
        result["styles"] = css

        # Data attributes for agent context
        result["data-figma-type"] = ntype
        result["data-figma-name"] = name

        # Recurse children
        children = node.get("children", [])
        if children:
            result["children"] = [self._node_to_dom(c) for c in children]

        return result

    def _build_tailwind_classes(self, node: dict) -> list[str]:
        """Generate Tailwind CSS classes from Figma node properties."""
        classes: list[str] = []
        ntype = node.get("type", "")

        # Layout
        layout_mode = node.get("layoutMode")
        if layout_mode:
            classes.append("flex")
            if layout_mode == "VERTICAL":
                classes.append("flex-col")
            gap = node.get("itemSpacing", 0)
            if gap:
                classes.append(f"gap-{self._px_to_tw(gap)}")

        # Padding
        pt = node.get("paddingTop", 0)
        pr = node.get("paddingRight", 0)
        pb = node.get("paddingBottom", 0)
        pl = node.get("paddingLeft", 0)
        if pt == pr == pb == pl and pt > 0:
            classes.append(f"p-{self._px_to_tw(pt)}")
        else:
            if pt:
                classes.append(f"pt-{self._px_to_tw(pt)}")
            if pr:
                classes.append(f"pr-{self._px_to_tw(pr)}")
            if pb:
                classes.append(f"pb-{self._px_to_tw(pb)}")
            if pl:
                classes.append(f"pl-{self._px_to_tw(pl)}")

        # Alignment
        primary = node.get("primaryAxisAlignItems")
        counter = node.get("counterAxisAlignItems")
        if primary:
            mapping = {
                "MIN": "justify-start", "CENTER": "justify-center",
                "MAX": "justify-end", "SPACE_BETWEEN": "justify-between",
            }
            tw = mapping.get(primary)
            if tw:
                classes.append(tw)
        if counter:
            mapping = {"MIN": "items-start", "CENTER": "items-center", "MAX": "items-end"}
            tw = mapping.get(counter)
            if tw:
                classes.append(tw)

        # Border radius
        cr = node.get("cornerRadius")
        if cr:
            if cr >= 9999:
                classes.append("rounded-full")
            elif cr >= 16:
                classes.append("rounded-2xl")
            elif cr >= 12:
                classes.append("rounded-xl")
            elif cr >= 8:
                classes.append("rounded-lg")
            elif cr >= 6:
                classes.append("rounded-md")
            elif cr >= 4:
                classes.append("rounded")
            elif cr >= 2:
                classes.append("rounded-sm")

        # Background
        fills = node.get("fills", [])
        visible_fills = [f for f in fills if f.get("visible", True)]
        if visible_fills:
            color_str = self._parse_color(visible_fills[0])
            tw_color = self._color_to_tw(color_str)
            if tw_color:
                classes.append(f"bg-{tw_color}")

        # Text color
        if ntype == "TEXT" and fills:
            color_str = self._parse_color(fills[0])
            tw_color = self._color_to_tw(color_str)
            if tw_color:
                classes.append(f"text-{tw_color}")

        # Text size
        if ntype == "TEXT":
            fs = node.get("style", {}).get("fontSize")
            if fs:
                size_map = {
                    12: "text-xs", 14: "text-sm", 16: "text-base",
                    18: "text-lg", 20: "text-xl", 24: "text-2xl",
                    30: "text-3xl", 36: "text-4xl", 48: "text-5xl",
                }
                closest = min(size_map.keys(), key=lambda k: abs(k - fs))
                classes.append(size_map[closest])

            fw = node.get("style", {}).get("fontWeight")
            if fw:
                weight_map = {
                    100: "font-thin", 200: "font-extralight", 300: "font-light",
                    400: "font-normal", 500: "font-medium", 600: "font-semibold",
                    700: "font-bold", 800: "font-extrabold", 900: "font-black",
                }
                closest = min(weight_map.keys(), key=lambda k: abs(k - fw))
                classes.append(weight_map[closest])

        # Opacity
        opacity = node.get("opacity")
        if opacity is not None and opacity < 1:
            pct = round(opacity * 100)
            opacity_map = {0: "opacity-0", 5: "opacity-5", 10: "opacity-10",
                           20: "opacity-20", 25: "opacity-25", 30: "opacity-30",
                           40: "opacity-40", 50: "opacity-50", 60: "opacity-60",
                           70: "opacity-70", 75: "opacity-75", 80: "opacity-80",
                           90: "opacity-90", 95: "opacity-95", 100: "opacity-100"}
            closest = min(opacity_map.keys(), key=lambda k: abs(k - pct))
            classes.append(opacity_map[closest])

        # Overflow
        if node.get("clipsContent"):
            classes.append("overflow-hidden")

        return classes


# ------------------------------------------------------------------ #
#  CLI entry point for agent use
# ------------------------------------------------------------------ #

def main():
    """CLI interface for agent-driven Figma operations."""
    if len(sys.argv) < 3:
        print(
            json.dumps({"error": "Usage: figma_reader.py <command> <file_id> [node_id] [options]"}),
            file=sys.stderr,
        )
        sys.exit(1)

    command = sys.argv[1]
    file_id = sys.argv[2]
    node_id = sys.argv[3] if len(sys.argv) > 3 else None

    reader = FigmaReader()

    if command == "styles":
        if not node_id:
            print(json.dumps({"error": "node_id required for styles command"}), file=sys.stderr)
            sys.exit(1)
        result = reader.extract_node_styles(file_id, node_id)
    elif command == "export":
        if not node_id:
            print(json.dumps({"error": "node_id required for export command"}), file=sys.stderr)
            sys.exit(1)
        fmt = sys.argv[4] if len(sys.argv) > 4 else "png"
        scale = float(sys.argv[5]) if len(sys.argv) > 5 else 2
        result = reader.export_assets(file_id, node_id, format=fmt, scale=scale)
    elif command == "tree":
        result = reader.parse_design_tree(file_id, node_id)
    elif command == "components":
        result = reader.list_components(file_id)
    elif command == "tokens":
        result = reader.get_design_tokens(file_id)
    else:
        print(
            json.dumps({"error": f"Unknown command: {command}. Use: styles, export, tree, components, tokens"}),
            file=sys.stderr,
        )
        sys.exit(1)

    # Machine-readable JSON to stdout
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
