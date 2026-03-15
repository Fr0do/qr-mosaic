import xml.etree.ElementTree as ET
from pathlib import Path

import qrcode
from qrcode.constants import ERROR_CORRECT_H


class QRSvgGenerator:
    def generate_svg(
        self,
        data: str,
        module_size: int = 10,
        fg: str = "#000000",
        bg: str = "#FFFFFF",
        rounded: bool = False,
        border: int = 4,
    ) -> str:
        matrix = self._make_matrix(data)
        return self._render_svg(matrix, module_size, fg, bg, rounded, border)

    def generate_svg_with_logo(
        self,
        data: str,
        logo_svg: str,
        module_size: int = 10,
        fg: str = "#000000",
        bg: str = "#FFFFFF",
        rounded: bool = False,
        border: int = 4,
    ) -> str:
        matrix = self._make_matrix(data)
        svg_body = self._render_svg(matrix, module_size, fg, bg, rounded, border, close=False)

        n = len(matrix)
        total = (n + 2 * border) * module_size
        logo_size = total * 0.20
        logo_x = (total - logo_size) / 2
        logo_y = (total - logo_size) / 2

        # White backdrop for logo legibility
        pad = logo_size * 0.15
        rect = (
            f'<rect x="{logo_x - pad:.2f}" y="{logo_y - pad:.2f}" '
            f'width="{logo_size + 2 * pad:.2f}" height="{logo_size + 2 * pad:.2f}" '
            f'fill="{bg}"/>'
        )

        # Inline the logo SVG as a nested <svg> element with scaling
        logo_tag = (
            f'<svg x="{logo_x:.2f}" y="{logo_y:.2f}" '
            f'width="{logo_size:.2f}" height="{logo_size:.2f}" '
            f'viewBox="0 0 24 24" preserveAspectRatio="xMidYMid meet">'
            f'{self._extract_logo_inner(logo_svg)}'
            f"</svg>"
        )

        return svg_body + rect + logo_tag + "</svg>"

    def save_svg(self, data: str, output_path: str, **kwargs) -> None:
        svg = self.generate_svg(data, **kwargs)
        Path(output_path).write_text(svg, encoding="utf-8")

    def save_svg_with_logo(
        self, data: str, logo_svg: str, output_path: str, **kwargs
    ) -> None:
        svg = self.generate_svg_with_logo(data, logo_svg, **kwargs)
        Path(output_path).write_text(svg, encoding="utf-8")

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _make_matrix(self, data: str):
        qr = qrcode.QRCode(error_correction=ERROR_CORRECT_H, border=0)
        qr.add_data(data)
        qr.make(fit=True)
        return qr.get_matrix()

    def _render_svg(
        self,
        matrix,
        module_size: int,
        fg: str,
        bg: str,
        rounded: bool,
        border: int,
        close: bool = True,
    ) -> str:
        n = len(matrix)
        total = (n + 2 * border) * module_size
        offset = border * module_size
        rx = (module_size * 0.3) if rounded else 0

        parts = [
            f'<svg xmlns="http://www.w3.org/2000/svg" '
            f'width="{total}" height="{total}" '
            f'viewBox="0 0 {total} {total}">',
            f'<rect width="{total}" height="{total}" fill="{bg}"/>',
        ]

        for row_idx, row in enumerate(matrix):
            for col_idx, cell in enumerate(row):
                if cell:
                    x = offset + col_idx * module_size
                    y = offset + row_idx * module_size
                    if rounded:
                        parts.append(
                            f'<rect x="{x}" y="{y}" '
                            f'width="{module_size}" height="{module_size}" '
                            f'rx="{rx:.1f}" ry="{rx:.1f}" fill="{fg}"/>'
                        )
                    else:
                        parts.append(
                            f'<rect x="{x}" y="{y}" '
                            f'width="{module_size}" height="{module_size}" '
                            f'fill="{fg}"/>'
                        )

        if close:
            parts.append("</svg>")
        return "".join(parts)

    def _extract_logo_inner(self, logo_svg: str) -> str:
        # Return the inner content of the SVG (children of <svg> root).
        try:
            root = ET.fromstring(logo_svg)
            # Re-serialise child elements
            return "".join(ET.tostring(child, encoding="unicode") for child in root)
        except ET.ParseError:
            # Fall back to embedding as-is if parsing fails
            return logo_svg
