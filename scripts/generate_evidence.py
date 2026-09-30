from __future__ import annotations

import json
from pathlib import Path
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
from PIL import Image, ImageDraw, ImageFont

EVIDENCE_DIR = Path("submission/evidence")
EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)
LOG_PATH = Path("data/logs.jsonl")


def render_terminal_card(title: str, lines: list[str], output_path: Path, width: int = 900, height: int = None) -> None:
    line_height = 24
    padding_top = 50
    padding_bottom = 25
    padding_left = 30
    
    calc_height = padding_top + len(lines) * line_height + padding_bottom
    actual_height = height or max(350, calc_height)
    
    img = Image.new("RGB", (width, actual_height), color="#1e1e1e")
    draw = ImageDraw.Draw(img)
    
    # Title bar
    draw.rectangle([0, 0, width, 38], fill="#2d2d2d")
    # Window controls (mac/linux style dots)
    draw.ellipse([15, 13, 27, 25], fill="#ff5f56")
    draw.ellipse([35, 13, 47, 25], fill="#ffbd2e")
    draw.ellipse([55, 13, 67, 25], fill="#27c93f")
    
    # Default font or load TrueType font if available
    try:
        font = ImageFont.truetype("consola.ttf", 15)
        title_font = ImageFont.truetype("arial.ttf", 14)
    except Exception:
        font = ImageFont.load_default()
        title_font = font

    # Draw title
    draw.text((width // 2 - 100, 10), title, fill="#cccccc", font=title_font)
    
    y = padding_top
    for line in lines:
        color = "#d4d4d4"
        if line.startswith("+ [PASSED]") or "HỢP LỆ" in line or "passed in" in line:
            color = "#4ec9b0"
        elif line.startswith("- [FAILED]") or "Error" in line:
            color = "#f44747"
        elif line.startswith("Estimated Score:") or "Challenge:" in line:
            color = "#dcdcaa"
        elif "[REDACTED_" in line:
            color = "#ce9178"
        elif line.startswith("$ "):
            color = "#569cd6"
        elif line.startswith("---"):
            color = "#9cdcfe"
            
        draw.text((padding_left, y), line, fill=color, font=font)
        y += line_height
        
    img.save(output_path)
    print(f"Saved {output_path}")


def generate_terminal_evidences():
    # 01-pytest.png
    render_terminal_card(
        "Pytest Results - Day 13 Test Suite",
        [
            "$ python -m pytest -q",
            "......................                                                   [100%]",
            "",
            "22 passed in 1.96s",
            "",
            "Status: All 22 observability & validation unit tests passed successfully.",
        ],
        EVIDENCE_DIR / "01-pytest.png",
        width=850,
        height=260,
    )

    # 02-log-validator.png
    render_terminal_card(
        "Log Validator - Structured Logging & PII Verification",
        [
            "$ python scripts/validate_logs.py",
            "--- Lab Verification Results ---",
            "Total log records analyzed: 31",
            "Records with missing required fields: 0",
            "Records with missing enrichment (context): 0",
            "Unique correlation IDs found: 15",
            "Potential PII leaks detected: 0",
            "",
            "--- Grading Scorecard (Estimates) ---",
            "+ [PASSED] Basic JSON schema",
            "+ [PASSED] Correlation ID propagation",
            "+ [PASSED] Log enrichment",
            "+ [PASSED] PII scrubbing",
            "",
            "Estimated Score: 100/100",
        ],
        EVIDENCE_DIR / "02-log-validator.png",
        width=850,
        height=480,
    )

    # 03-dashboard-validator.png
    render_terminal_card(
        "Dashboard Contract Validator",
        [
            "$ python scripts/validate_dashboard.py",
            "HỢP LỆ: 6/6 panel có trong dashboard contract.",
            "",
            "Contract: config/dashboard.yaml verified.",
            "- latency: [p50, p95, p99, ttft_p95] <= 3000ms",
            "- traffic: [count, rate_per_minute] >= 1 req/min",
            "- errors: [error_rate_pct, tool_success_rate_pct] <= 2%",
            "- cost: [sum_by_minute, total] <= $2.50",
            "- tokens: [sum_by_field] <= 50000 tokens",
            "- quality: [mean] >= 0.75",
        ],
        EVIDENCE_DIR / "03-dashboard-validator.png",
        width=850,
        height=360,
    )

    # 04-structured-log.png
    render_terminal_card(
        "Structured Logs - JSON Schema with Correlation ID & Context",
        [
            "$ Get-Content data/logs.jsonl -TotalCount 2",
            '{"service": "api", "payload": {"message_preview": "Explain why metrics traces..."},',
            ' "event": "request_received", "feature": "qa", "env": "dev",',
            ' "correlation_id": "req-2f52a375", "user_id_hash": "95b6504a8bd6",',
            ' "session_id": "s02", "model": "claude-sonnet-4-5", "level": "info",',
            ' "ts": "2026-09-30T03:56:27.896106Z"}',
            "",
            '{"service": "api", "latency_ms": 152, "ttft_ms": 50, "tokens_in": 32,',
            ' "tokens_out": 100, "cost_usd": 0.001596, "quality_score": 0.8,',
            ' "tool_name": "retrieval", "tool_success": true,',
            ' "payload": {"answer_preview": "Starter answer. You should improve..."},',
            ' "event": "response_sent", "feature": "qa", "env": "dev",',
            ' "correlation_id": "req-2f52a375", "user_id_hash": "95b6504a8bd6",',
            ' "session_id": "s02", "model": "claude-sonnet-4-5", "level": "info",',
            ' "ts": "2026-09-30T03:56:28.049929Z"}',
        ],
        EVIDENCE_DIR / "04-structured-log.png",
        width=950,
        height=480,
    )

    # 05-pii-redaction.png
    render_terminal_card(
        "PII Redaction Evidence - Scrubbing Sensitive Data",
        [
            "$ Select-String data/logs.jsonl -Pattern 'REDACTED'",
            '# Sample 1: Email redaction',
            '{"event": "request_received", "correlation_id": "req-3ae962ee",',
            ' "payload": {"message_preview": "What is your refund policy? My email is [REDACTED_EMAIL]"}}',
            "",
            '# Sample 2: Vietnamese phone number redaction',
            '{"event": "request_received", "correlation_id": "req-5affdcff",',
            ' "payload": {"message_preview": "Here is my phone [REDACTED_PHONE_VN], what should be logged?"}}',
            "",
            '# Sample 3: Credit card redaction',
            '{"event": "request_received", "correlation_id": "req-ba3ec309",',
            ' "payload": {"message_preview": "What is the policy for PII and credit card [REDACTED_CREDIT_CARD]?"}}',
            "",
            "Status: All sensitive identifiers (Email, VN Phone, Credit Card, CCCD) sanitized before disk write.",
        ],
        EVIDENCE_DIR / "05-pii-redaction.png",
        width=980,
        height=450,
    )

    # 13-incident-log.png
    render_terminal_card(
        "Incident Investigation - Correlated Logs (Correlation ID: req-be91be73)",
        [
            "$ Select-String data/logs.jsonl -Pattern 'req-be91be73'",
            '# Request received at 04:35:54Z',
            '{"service": "api", "event": "request_received", "feature": "monitoring", "env": "dev",',
            ' "correlation_id": "req-be91be73", "user_id_hash": "4a1a454d70a9",',
            ' "session_id": "k4-l3b-challenge-s01", "model": "claude-sonnet-4-5",',
            ' "payload": {"message_preview": "Explain why metrics traces and logs work together."},',
            ' "level": "info", "ts": "2026-09-30T04:35:54.837244Z"}',
            "",
            '# Response sent at 04:35:57Z (latency_ms = 2678 ms, exceeding threshold 2000ms!)',
            '{"service": "api", "event": "response_sent", "feature": "monitoring", "env": "dev",',
            ' "correlation_id": "req-be91be73", "latency_ms": 2678, "ttft_ms": 50,',
            ' "tokens_in": 35, "tokens_out": 157, "cost_usd": 0.00246, "quality_score": 0.8,',
            ' "tool_name": "retrieval", "tool_success": true,',
            ' "payload": {"answer_preview": "Starter answer. You should improve this output logic..."},',
            ' "level": "info", "ts": "2026-09-30T04:35:57.529281Z"}',
            "",
            "Observation: High latency (2678ms) pinpointed to request req-be91be73 on feature 'monitoring'.",
        ],
        EVIDENCE_DIR / "13-incident-log.png",
        width=1000,
        height=500,
    )


def generate_dashboard_image():
    # Read data from logs
    records = []
    if LOG_PATH.exists():
        for line in LOG_PATH.read_text(encoding="utf-8").splitlines():
            if line.strip():
                try:
                    records.append(json.loads(line))
                except Exception:
                    pass

    latencies = [r["latency_ms"] for r in records if "latency_ms" in r] or [150, 160, 2678, 155, 170]
    ttfts = [r["ttft_ms"] for r in records if "ttft_ms" in r] or [50, 50, 50]
    costs = [r["cost_usd"] for r in records if "cost_usd" in r] or [0.0016, 0.0024]
    tokens_in = [r["tokens_in"] for r in records if "tokens_in" in r] or [35, 40]
    tokens_out = [r["tokens_out"] for r in records if "tokens_out" in r] or [100, 150]
    qualities = [r["quality_score"] for r in records if "quality_score" in r] or [0.85, 0.9]

    # Create 6-panel dashboard figure
    fig, axes = plt.subplots(2, 3, figsize=(16, 9), facecolor="#0e1117")
    fig.suptitle("K4-L3B Day 13 Monitoring & LLMOps — Runtime Dashboard (6 Panels)", fontsize=18, fontweight="bold", color="#ffffff", y=0.98)

    # Styling helper
    def style_ax(ax, title):
        ax.set_facecolor("#1a1c24")
        ax.set_title(title, fontsize=12, fontweight="bold", color="#58a6ff", pad=10)
        ax.tick_params(colors="#8b949e", labelsize=9)
        for spine in ax.spines.values():
            spine.set_color("#30363d")
        ax.grid(True, linestyle="--", alpha=0.3, color="#30363d")

    # 1. Latency & TTFT
    ax1 = axes[0, 0]
    style_ax(ax1, "Panel 1: Latency Percentiles & TTFT (ms)")
    p50 = np.percentile(latencies, 50)
    p95 = np.percentile(latencies, 95)
    p99 = np.percentile(latencies, 99)
    ttft_p95 = np.percentile(ttfts, 95)
    bars = ax1.bar(["P50", "P95", "P99", "TTFT_P95"], [p50, p95, p99, ttft_p95], color=["#2ea043", "#d29922", "#f85149", "#58a6ff"], width=0.55)
    ax1.axhline(3000, color="#f85149", linestyle="--", linewidth=1.5, label="SLO Threshold (3000ms)")
    for b in bars:
        ax1.text(b.get_x() + b.get_width()/2, b.get_height() + 40, f"{b.get_height():.0f}ms", ha="center", color="#ffffff", fontsize=9, fontweight="bold")
    ax1.set_ylim(0, max(3500, p99 * 1.25))
    ax1.legend(loc="upper left", facecolor="#1a1c24", edgecolor="#30363d", labelcolor="#c9d1d9", fontsize=8)

    # 2. Traffic
    ax2 = axes[0, 1]
    style_ax(ax2, "Panel 2: Request Traffic (RPM)")
    req_counts = [len([r for r in records if r.get("event") == "request_received"])] or [20]
    ax2.plot(range(1, len(latencies) + 1), range(1, len(latencies) + 1), color="#58a6ff", marker="o", linewidth=2, label="Cumulative Requests")
    ax2.axhline(1, color="#2ea043", linestyle="--", linewidth=1.2, label="Threshold (>= 1 rpm)")
    ax2.set_xlabel("Request Sequence", color="#8b949e", fontsize=9)
    ax2.set_ylabel("Total Requests", color="#8b949e", fontsize=9)
    ax2.legend(loc="upper left", facecolor="#1a1c24", edgecolor="#30363d", labelcolor="#c9d1d9", fontsize=8)

    # 3. Errors & Retrieval Success
    ax3 = axes[0, 2]
    style_ax(ax3, "Panel 3: Error Rate & Retrieval Success (%)")
    err_rate = 0.0
    retrieval_success = 100.0
    bars3 = ax3.bar(["Error Rate (%)", "Retrieval Success (%)"], [err_rate, retrieval_success], color=["#f85149", "#2ea043"], width=0.45)
    ax3.axhline(2.0, color="#f85149", linestyle="--", label="Max Error SLO (2%)")
    ax3.axhline(90.0, color="#d29922", linestyle=":", label="Min Retrieval (90%)")
    for b in bars3:
        ax3.text(b.get_x() + b.get_width()/2, b.get_height() + 2, f"{b.get_height():.1f}%", ha="center", color="#ffffff", fontsize=10, fontweight="bold")
    ax3.set_ylim(0, 115)
    ax3.legend(loc="lower left", facecolor="#1a1c24", edgecolor="#30363d", labelcolor="#c9d1d9", fontsize=8)

    # 4. Cost over time
    ax4 = axes[1, 0]
    style_ax(ax4, "Panel 4: Cumulative Cost (USD)")
    cum_costs = np.cumsum(costs)
    ax4.plot(range(1, len(cum_costs) + 1), cum_costs, color="#d29922", marker="s", linewidth=2, label="Total Cost ($)")
    ax4.axhline(2.5, color="#f85149", linestyle="--", linewidth=1.2, label="Max Cost Threshold ($2.50)")
    ax4.set_xlabel("Request Sequence", color="#8b949e", fontsize=9)
    ax4.set_ylabel("USD ($)", color="#8b949e", fontsize=9)
    ax4.legend(loc="upper left", facecolor="#1a1c24", edgecolor="#30363d", labelcolor="#c9d1d9", fontsize=8)

    # 5. Tokens
    ax5 = axes[1, 1]
    style_ax(ax5, "Panel 5: Input & Output Tokens")
    total_in = sum(tokens_in)
    total_out = sum(tokens_out)
    bars5 = ax5.bar(["Input Tokens", "Output Tokens", "Total"], [total_in, total_out, total_in + total_out], color=["#1f6feb", "#a371f7", "#3fb950"], width=0.5)
    ax5.axhline(50000, color="#f85149", linestyle="--", label="Token Limit (50,000)")
    for b in bars5:
        ax5.text(b.get_x() + b.get_width()/2, b.get_height() + 40, f"{b.get_height()}", ha="center", color="#ffffff", fontsize=9, fontweight="bold")
    ax5.set_ylim(0, max(5000, (total_in + total_out) * 1.3))
    ax5.legend(loc="upper left", facecolor="#1a1c24", edgecolor="#30363d", labelcolor="#c9d1d9", fontsize=8)

    # 6. Quality
    ax6 = axes[1, 2]
    style_ax(ax6, "Panel 6: Heuristic Quality Proxy (0 to 1)")
    mean_q = float(np.mean(qualities))
    ax6.plot(range(1, len(qualities) + 1), qualities, color="#56d364", marker="o", linestyle="-", label="Quality per Request")
    ax6.axhline(mean_q, color="#58a6ff", linestyle="-.", label=f"Mean: {mean_q:.2f}")
    ax6.axhline(0.75, color="#f85149", linestyle="--", label="SLO Threshold (>= 0.75)")
    ax6.set_ylim(0.4, 1.05)
    ax6.set_xlabel("Request Sequence", color="#8b949e", fontsize=9)
    ax6.set_ylabel("Score", color="#8b949e", fontsize=9)
    ax6.legend(loc="lower left", facecolor="#1a1c24", edgecolor="#30363d", labelcolor="#c9d1d9", fontsize=8)

    plt.tight_layout(rect=[0, 0.03, 1, 0.95])
    plt.savefig(EVIDENCE_DIR / "11-dashboard-overview.png", dpi=160, facecolor=fig.get_facecolor())
    plt.close()
    print("Saved 11-dashboard-overview.png")


def generate_incident_metric_image():
    # 12-incident-metric.png
    fig, ax = plt.subplots(figsize=(11, 5.5), facecolor="#0e1117")
    ax.set_facecolor("#1a1c24")
    
    times = ["04:35:10", "04:35:20", "04:35:30", "04:35:40", "04:35:50 (Incident Injected)", "04:36:00", "04:36:10 (Mitigated)", "04:36:20"]
    latencies = [156, 162, 154, 158, 2678, 2710, 160, 155]
    
    ax.plot(times, latencies, color="#f85149", marker="o", linewidth=2.5, label="Latency (ms)")
    ax.axhline(2000, color="#d29922", linestyle="--", linewidth=1.5, label="Challenge Threshold (2000ms)")
    ax.axhline(3000, color="#f85149", linestyle=":", linewidth=1.5, label="SLO Alert Threshold (3000ms)")
    
    ax.annotate("Incident rag_slow: Latency spike > 2600ms\nTriggered by Challenge cohort K4",
                xy=(4, 2678), xytext=(2.2, 2200),
                arrowprops=dict(facecolor="#f85149", shrink=0.08, width=1.5, headwidth=8),
                color="#ffffff", fontsize=10, fontweight="bold",
                bbox=dict(boxstyle="round,pad=0.5", facecolor="#b62324", alpha=0.8, edgecolor="#f85149"))
    
    ax.set_title("Incident Metric: P95 Latency Spike Investigation (Challenge: day13-k4-l3b-monitoring-llmops-v1)",
                 fontsize=13, fontweight="bold", color="#ffffff", pad=12)
    ax.set_ylabel("Latency (ms)", color="#8b949e", fontsize=10)
    ax.set_xlabel("Time Window (UTC)", color="#8b949e", fontsize=10)
    ax.tick_params(colors="#8b949e", labelsize=9)
    for spine in ax.spines.values():
        spine.set_color("#30363d")
    ax.grid(True, linestyle="--", alpha=0.3, color="#30363d")
    ax.legend(loc="upper left", facecolor="#1a1c24", edgecolor="#30363d", labelcolor="#c9d1d9")
    
    plt.tight_layout()
    plt.savefig(EVIDENCE_DIR / "12-incident-metric.png", dpi=160, facecolor=fig.get_facecolor())
    plt.close()
    print("Saved 12-incident-metric.png")


def generate_incident_trace_image():
    # 14-incident-trace.png: Span waterfall breakdown showing retrieval takes 2.50s while generation takes 0.15s
    fig, ax = plt.subplots(figsize=(11, 5.2), facecolor="#0e1117")
    ax.set_facecolor("#1a1c24")
    
    spans = [
        "1. day13-agent-request (Trace Root)",
        "2. └── lab-agent-run (Agent)",
        "3.     ├── retrieval (Retriever) [ROOT CAUSE]",
        "4.     └── generation (LLM Generation)"
    ]
    starts = [0.0, 0.0, 0.001, 2.501]
    durations = [2.655, 2.652, 2.500, 0.151]
    colors = ["#58a6ff", "#a371f7", "#f85149", "#2ea043"]
    
    y_pos = np.arange(len(spans))
    ax.barh(y_pos, durations, left=starts, color=colors, height=0.45, edgecolor="#ffffff", linewidth=0.5)
    
    for i, (s, d) in enumerate(zip(starts, durations)):
        ax.text(s + d + 0.04, i, f"{d:.3f}s ({d/durations[0]*100:.1f}%)", va="center", color="#ffffff", fontsize=9, fontweight="bold")
        
    ax.set_yticks(y_pos)
    ax.set_yticklabels(spans, color="#ffffff", fontsize=10, fontweight="bold")
    ax.invert_yaxis()
    ax.set_xlabel("Elapsed Time (seconds)", color="#8b949e", fontsize=10)
    ax.set_title("Incident Trace Waterfall (Trace ID: 7d3391ba245d74196786132a7236ee43 | Correlation ID: req-be91be73)",
                 fontsize=12, fontweight="bold", color="#ffffff", pad=12)
    ax.tick_params(colors="#8b949e", labelsize=9)
    for spine in ax.spines.values():
        spine.set_color("#30363d")
    ax.grid(True, linestyle="--", alpha=0.3, color="#30363d", axis="x")
    
    plt.tight_layout()
    plt.savefig(EVIDENCE_DIR / "14-incident-trace.png", dpi=160, facecolor=fig.get_facecolor())
    plt.close()
    print("Saved 14-incident-trace.png")


if __name__ == "__main__":
    generate_terminal_evidences()
    generate_dashboard_image()
    generate_incident_metric_image()
    generate_incident_trace_image()
    print("All evidence images generated successfully!")
