import argparse
import os

from .generator import QRGenerator
from .logos import LOGO_PRESETS, get_logo_svg
from .mosaic import MosaicBlender, STYLES
from .svg import QRSvgGenerator


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="qr-mosaic",
        description="Generate QR codes and blend them with images.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # --- generate ---
    gen_parser = subparsers.add_parser("generate", help="Generate a plain QR code")
    gen_parser.add_argument("--data", required=True, help="Data to encode")
    gen_parser.add_argument("--output", required=True, help="Output image path")
    gen_parser.add_argument("--size", type=int, default=512, help="Image size in pixels")
    gen_parser.add_argument(
        "--error-correction",
        choices=["L", "M", "Q", "H"],
        default="H",
        help="Error correction level",
    )

    # --- mosaic ---
    mos_parser = subparsers.add_parser("mosaic", help="Blend QR code with a background image")
    mos_parser.add_argument("--data", required=True, help="Data to encode in QR")
    mos_parser.add_argument("--background", required=True, help="Background image path")
    mos_parser.add_argument("--output", required=True, help="Output image path")
    mos_parser.add_argument("--size", type=int, default=512, help="QR size in pixels")
    mos_parser.add_argument("--opacity", type=float, default=0.5, help="Blend opacity (0.0-1.0)")
    mos_parser.add_argument(
        "--style",
        choices=list(STYLES),
        default="overlay",
        help="Blending style",
    )

    # --- svg ---
    svg_parser = subparsers.add_parser("svg", help="Generate a vector SVG QR code")
    svg_parser.add_argument("--data", required=True, help="Data to encode")
    svg_parser.add_argument("--output", required=True, help="Output .svg path")
    svg_parser.add_argument(
        "--logo",
        default=None,
        help=f"Logo preset ({', '.join(LOGO_PRESETS)}) or path to an SVG file",
    )
    svg_parser.add_argument("--fg", default="#000000", help="Foreground color (default #000000)")
    svg_parser.add_argument("--bg", default="#FFFFFF", help="Background color (default #FFFFFF)")
    svg_parser.add_argument("--rounded", action="store_true", help="Rounded module corners")
    svg_parser.add_argument("--module-size", type=int, default=10, help="Module size in px")
    svg_parser.add_argument("--border", type=int, default=4, help="Quiet zone in modules")

    args = parser.parse_args()

    if args.command == "generate":
        gen = QRGenerator()
        img = gen.generate(
            data=args.data,
            size=args.size,
            error_correction=args.error_correction,
        )
        img.save(args.output)
        print(f"QR code saved to {args.output}")

    elif args.command == "mosaic":
        blender = MosaicBlender()
        blender.blend_from_paths(
            qr_data=args.data,
            bg_path=args.background,
            output_path=args.output,
            opacity=args.opacity,
            style=args.style,
            qr_size=args.size,
        )
        print(f"Mosaic saved to {args.output}")

    elif args.command == "svg":
        gen = QRSvgGenerator()
        svg_kwargs = dict(
            module_size=args.module_size,
            fg=args.fg,
            bg=args.bg,
            rounded=args.rounded,
            border=args.border,
        )
        if args.logo is None:
            gen.save_svg(args.data, args.output, **svg_kwargs)
        else:
            if args.logo in LOGO_PRESETS:
                logo_svg = get_logo_svg(args.logo)
            elif os.path.isfile(args.logo):
                from pathlib import Path
                logo_svg = Path(args.logo).read_text(encoding="utf-8")
            else:
                parser.error(
                    f"--logo must be a preset name ({', '.join(LOGO_PRESETS)}) "
                    f"or an existing SVG file path"
                )
            gen.save_svg_with_logo(args.data, logo_svg, args.output, **svg_kwargs)
        print(f"SVG QR code saved to {args.output}")


if __name__ == "__main__":
    main()
