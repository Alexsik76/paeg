from typing import Set, Optional, Any


class SVGProtocolVisualizer:
    """
    Handles rendering of a modern SVG-based network scheme with smooth CSS animations.
    Designed specifically for Lab 6 topology.
    """

    def __init__(self, duration: float = 1.5):
        self.active_routes: Set[str] = set()
        self.active_node: Optional[str] = None  # Node id to show spinner around
        self.message: str = ""
        self.is_final: bool = False  # If True, highlights the message with a border
        self.duration: float = duration
        # Topology coordinates (scaled for 650x500 SVG)
        self.coords = {
            "voter": (100, 300),
            "rb": (300, 100),
            "cec": (550, 300),
            "lc1": (300, 200),
            "lc2": (300, 270),
            "lc3": (300, 340),
            "lc4": (300, 410),
            "mc1": (450, 235),
            "mc2": (450, 375),
        }
        self.routes = {
            "e_reg": ("voter", "rb"),
            "e_blind": ("voter", "cec"),
            "e_v1_lc1": ("voter", "lc1"),
            "e_v1_lc2": ("voter", "lc2"),
            "e_v2_lc3": ("voter", "lc3"),
            "e_v2_lc4": ("voter", "lc4"),
            "e_lc1_mc1": ("lc1", "mc1"),
            "e_lc2_mc1": ("lc2", "mc1"),
            "e_lc3_mc2": ("lc3", "mc2"),
            "e_lc4_mc2": ("lc4", "mc2"),
            "e_mc1_cec": ("mc1", "cec"),
            "e_mc2_cec": ("mc2", "cec"),
            "e_rb_v": ("rb", "voter"),
            "e_cec_v": ("cec", "voter"),
        }

    def activate_flow(self, edge_id: str, message: str = "") -> None:
        self.active_routes.add(edge_id)
        if message:
            self.message = message

    def deactivate_all_flows(self) -> None:
        """Clears moving packets and node spinners, but preserves the status message."""
        self.active_routes.clear()
        self.active_node = None

    def clear_all(self) -> None:
        """Fully resets the visualizer state including messages and boxed styling."""
        self.active_routes.clear()
        self.active_node = None
        self.message = ""
        self.is_final = False

    def render(self, placeholder: Any) -> None:
        if placeholder is None:
            return

        import streamlit.components.v1 as components

        # Generate CSS animations dynamically based on active routes
        animation_css = ""
        packets_html = ""

        if self.active_routes:
            for route_id in self.active_routes:
                if route_id in self.routes:
                    start_node, end_node = self.routes[route_id]
                    x1, y1 = self.coords[start_node]
                    x2, y2 = self.coords[end_node]

                    animation_css += f"""
                    .packet_{route_id} {{
                        animation: movePacket_{route_id} {self.duration}s ease-in-out infinite;
                    }}
                    @keyframes movePacket_{route_id} {{
                        0% {{ transform: translate({x1}px, {y1}px); opacity: 0; }}
                        10% {{ opacity: 1; }}
                        90% {{ opacity: 1; }}
                        100% {{ transform: translate({x2}px, {y2}px); opacity: 0; }}
                    }}
                    """
                    packets_html += f'<circle cx="0" cy="0" r="6" class="packet packet_{route_id}" />'

        if not animation_css:
            animation_css = ".packet { display: none; }"

        html_code = f"""
        <!DOCTYPE html>
        <html>
        <head>
        <style>
            body {{
                background-color: transparent;
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                color: #E0E0E0;
                display: flex;
                flex-direction: column;
                align-items: center;
                margin: 0;
                overflow: hidden;
            }}

            .status-wrapper {{
                min-height: 80px; 
                width: 100%;
                display: flex;
                align-items: center;
                justify-content: center;
                margin-bottom: 5px;
                padding: 0 15px; 
                box-sizing: border-box;
            }}

            .status-text {{
                font-size: 16px;
                font-weight: 600;
                color: #4CAF50;
                padding: 8px 20px;
                border: 2px solid transparent;
                border-radius: 8px;
                text-align: center;
                transition: all 0.3s ease;
                box-sizing: border-box;
                white-space: pre-line;
            }}

            .final-box {{
                border-color: #4CAF50;
                background: rgba(76, 175, 80, 0.1);
                box-shadow: 0 0 15px rgba(76, 175, 80, 0.2);
            }}

            svg {{
                background: #121212;
                border-radius: 16px;
                box-shadow: 0 10px 30px rgba(0,0,0,0.5);
                border: 1px solid #333;
                isolation: isolate; 
                transform: translateZ(0);
            }}
            
            .node text {{
                fill: #FFFFFF;
                font-size: 12px;
                font-weight: 500;
                text-anchor: middle;
                dominant-baseline: middle;
                pointer-events: none;
            }}
            .node text {{
                fill: #FFFFFF;
                font-size: 12px;
                font-weight: 500;
                text-anchor: middle;
                dominant-baseline: middle;
                pointer-events: none;
            }}
            .node circle {{
                stroke-width: 2;
                transition: all 0.3s ease;
            }}
            .voter circle {{ fill: #1B5E20; stroke: #4CAF50; }}
            .rb circle {{ fill: #E65100; stroke: #FF9800; }}
            .cvk circle {{ fill: #4A148C; stroke: #9C27B0; }}
            .commission circle {{ fill: #0D47A1; stroke: #2196F3; }}
            
            .link {{
                stroke: #444;
                stroke-width: 1.5;
                stroke-dasharray: 4, 4;
                opacity: 0.6;
            }}
            
            .packet {{
                fill: #FFEB3B;
                stroke: #F57F17;
                stroke-width: 1.5;
                # filter: drop-shadow(0 0 5px #FFEB3B);
                will-change: transform;
                transform: translateZ(0);
                backface-visibility: hidden;
            }}

            .spinner {{
                fill: none;
                stroke: #4CAF50;
                stroke-width: 3;
                stroke-dasharray: 40, 100;
                animation: rotateSpinner 1.5s linear infinite;
                # filter: drop-shadow(0 0 8px #4CAF50);
                opacity: 0.8;
                transform-box: fill-box;
                transform-origin: center;
            }}

            @keyframes rotateSpinner {{
                0% {{ transform: rotate(0deg); }}
                100% {{ transform: rotate(360deg); }}
            }}

            {animation_css}
        </style>
        </head>
        <body>
            <div class="status-text {"final-box" if self.is_final else ""}">{self.message}</div>
            <svg viewBox="0 0 650 500" style="width: 100%; max-width: 650px; height: auto;">
                <!-- Connections -->
                {" ".join([f'<line x1="{self.coords[st][0]}" y1="{self.coords[st][1]}" x2="{self.coords[en][0]}" y2="{self.coords[en][1]}" class="link" />' for st, en in self.routes.values()])}

                <!-- Packets -->
                {packets_html}

                <!-- Activity Spinner -->
                {f'<circle cx="{self.coords[self.active_node][0]}" cy="{self.coords[self.active_node][1]}" r="45" class="spinner" />' if self.active_node and self.active_node in self.coords else ""}

                <!-- Nodes -->
                <g class="node voter" transform="translate(100, 300)">
                    <circle r="35" />
                    <text>Виборець</text>
                </g>
                <g class="node rb" transform="translate(300, 100)">
                    <circle r="30" />
                    <text>RB</text>
                </g>
                <g class="node cvk" transform="translate(550, 300)">
                    <circle r="35" />
                    <text>ЦВК</text>
                </g>
                
                <g class="node commission" transform="translate(300, 200)">
                    <circle r="20" />
                    <text dy="25">LC-1</text>
                </g>
                <g class="node commission" transform="translate(300, 270)">
                    <circle r="20" />
                    <text dy="25">LC-2</text>
                </g>
                <g class="node commission" transform="translate(300, 340)">
                    <circle r="20" />
                    <text dy="25">LC-3</text>
                </g>
                <g class="node commission" transform="translate(300, 410)">
                    <circle r="20" />
                    <text dy="25">LC-4</text>
                </g>

                <g class="node commission" transform="translate(450, 235)">
                    <circle r="25" />
                    <text dy="30">MC-1</text>
                </g>
                <g class="node commission" transform="translate(450, 375)">
                    <circle r="25" />
                    <text dy="30">MC-2</text>
                </g>
            </svg>
        </body>
        </html>
        """
        with placeholder:
            components.html(html_code, height=580)
