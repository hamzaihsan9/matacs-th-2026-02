import matplotlib.pyplot as plt
import matplotlib.patches as patches

def create_flow_diagram(output_path):
    fig, ax = plt.subplots(figsize=(15, 20), dpi=300)
    ax.set_facecolor("#f8fafc")
    fig.patch.set_facecolor("#f8fafc")
    ax.axis("off")
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)

    # Palette
    c_ai = "#4f46e5"      # Indigo - AI Step
    c_rule = "#059669"    # Emerald - Rule-Based Step
    c_human = "#d97706"   # Amber - Human Checkpoint
    c_store = "#475569"   # Slate - Storage / Database
    c_danger = "#dc2626"  # Red - Disqualification / Ineligible
    c_flag = "#ea580c"    # Orange - Security Flag
    c_box_bg = "#ffffff"

    # Header
    plt.text(50, 97.5, "AI-Assisted Proposal Triage System Architecture",
             fontsize=19, fontweight="bold", ha="center", color="#0f172a", family="sans-serif")
    plt.text(50, 95.8, "Process Flow: Upload to Ranked Output with AI Extraction, Rule-Based Scoring & Human Oversight",
             fontsize=11, ha="center", color="#475569", family="sans-serif")
    plt.text(50, 94.4, "Reference: MATACS-TH-2026-02",
             fontsize=10, fontweight="bold", ha="center", color="#64748b", family="sans-serif")

    # Legend
    legend_items = [
        ("AI-Powered Step", c_ai),
        ("Rule-Based / Deterministic Step", c_rule),
        ("Human-in-the-Loop Checkpoint", c_human),
        ("Data Store / Versioned Schema", c_store),
        ("Triage Disposition (Flag / Ineligible)", c_danger)
    ]
    for idx, (label, color) in enumerate(legend_items):
        lx = 5.0 + idx * 19.0
        rect = patches.FancyBboxPatch((lx, 91.5), 3.0, 1.6, boxstyle="round,pad=0.2",
                                      facecolor=color, edgecolor="none")
        ax.add_patch(rect)
        plt.text(lx + 3.8, 92.3, label, fontsize=8.5, fontweight="bold",
                 va="center", color="#1e293b", family="sans-serif")

    def draw_box(x, y, w, h, title, subtitle, color, border_color=None, bg_color="#ffffff", shape="round,pad=0.4"):
        b_color = border_color if border_color else color
        rect = patches.FancyBboxPatch((x, y), w, h, boxstyle=shape,
                                      facecolor=bg_color, edgecolor=b_color, linewidth=2.0)
        ax.add_patch(rect)
        # Header banner inside box
        banner = patches.FancyBboxPatch((x, y + h - 2.2), w, 2.2, boxstyle="round,pad=0.1",
                                        facecolor=color, edgecolor="none")
        ax.add_patch(banner)
        plt.text(x + w / 2, y + h - 1.1, title, fontsize=9.5, fontweight="bold",
                 ha="center", va="center", color="#ffffff", family="sans-serif")
        plt.text(x + w / 2, y + (h - 2.2) / 2, subtitle, fontsize=8,
                 ha="center", va="center", color="#334155", family="sans-serif")

    def draw_arrow(x1, y1, x2, y2, label="", color="#64748b", style="simple", curve=0.0):
        connection = f"arc3,rad={curve}" if curve != 0.0 else "arc3,rad=0.0"
        arrow = patches.FancyArrowPatch((x1, y1), (x2, y2),
                                        connectionstyle=connection,
                                        arrowstyle="->,head_width=3.5,head_length=5",
                                        color=color, linewidth=1.8)
        ax.add_patch(arrow)
        if label:
            mx, my = (x1 + x2) / 2, (y1 + y2) / 2
            plt.text(mx + 1.2, my, label, fontsize=7.5, fontweight="bold", color=color, family="sans-serif")

    # STAGE 1: ADMINISTRATION & INGESTION
    plt.text(4, 87.5, "STAGE 1: ADMINISTRATION & DOCUMENT INGESTION",
             fontsize=10.5, fontweight="bold", color="#1e293b", family="sans-serif")
    ax.axhline(86.8, color="#cbd5e1", linestyle="--", linewidth=1.2, xmin=0.04, xmax=0.96)

    # Box 1: Admin Definition (Human)
    draw_box(6, 76, 26, 9, "Admin Criteria Setup",
             "Admin defines categories,\nmandatory criteria & weights\nvia web UI (never hardcoded)",
             c_human)

    # Box 2: Criteria Store (Store)
    draw_box(37, 76, 26, 9, "Versioned Criteria DB",
             "Semantic schema versioning\n(e.g., Solar_v1.0.0)\nCriteria, weights & thresholds",
             c_store)

    # Box 3: Proposal Ingestion (Human / Input)
    draw_box(68, 76, 26, 9, "Reviewer Proposal Upload",
             "Reviewer selects category\n& uploads vendor PDF proposals\n(Proposals A, B, C, D, E)",
             c_human)

    draw_arrow(32, 80.5, 37, 80.5, "Publish Schema", c_human)
    draw_arrow(50, 76, 50, 68, "Active Criteria", c_store)
    draw_arrow(81, 76, 81, 68, "Raw PDFs", c_human)

    # STAGE 2: PREPROCESSING, SECURITY & AI EXTRACTION
    plt.text(4, 71.0, "STAGE 2: PREPROCESSING, SECURITY & AI-POWERED EXTRACTION",
             fontsize=10.5, fontweight="bold", color="#1e293b", family="sans-serif")
    ax.axhline(70.3, color="#cbd5e1", linestyle="--", linewidth=1.2, xmin=0.04, xmax=0.96)

    # Preprocessing
    draw_box(68, 59, 26, 9, "Document Preprocessing",
             "PyMuPDF text & table extraction\nPage & layout chunking\nCharacter sanitization",
             c_rule)

    # Security Filter
    draw_box(37, 59, 26, 9, "Injection & Security Guard",
             "Rule-based regex & heuristic scan\nDetects prompt injection attempts\n(e.g., Proposal C bypass note)",
             c_rule)

    draw_arrow(68, 63.5, 63, 63.5, "Clean Text", c_rule)

    # Flagged Branch (Proposal C)
    draw_box(6, 59, 26, 9, "Flagged Proposals Queue",
             "status: 'flagged' | rank: null\nSecurity alert & triage reason\n(Adversarial attack caught)",
             c_flag)

    draw_arrow(37, 63.5, 32, 63.5, "Suspicious Pattern", c_danger)

    # AI Fact Extraction Step
    draw_box(37, 44, 26, 11, "AI Fact Extraction Engine",
             "LLM with temperature 0.0\nStrict JSON Schema extraction\nExtracts license, experience, price,\ntimeline, warranty, team details\nRequires verbatim quotes for each field",
             c_ai)

    draw_arrow(50, 59, 50, 55, "Verified Safe", c_rule)

    # Grounding Validator
    draw_box(68, 44, 26, 11, "Grounding Citation Check",
             "Deterministic quote verification:\nquote in raw_document_text\nFlags hallucinations or missing data\n(Prevents AI fabrication)",
             c_rule)

    draw_arrow(63, 49.5, 68, 49.5, "Extracted JSON", c_ai)
    draw_arrow(81, 44, 81, 37, "Validated Facts", c_rule)

    # STAGE 3: COMPLIANCE & DETERMINISTIC SCORING
    plt.text(4, 40.0, "STAGE 3: COMPLIANCE GATING & DETERMINISTIC SCORING",
             fontsize=10.5, fontweight="bold", color="#1e293b", family="sans-serif")
    ax.axhline(39.3, color="#cbd5e1", linestyle="--", linewidth=1.2, xmin=0.04, xmax=0.96)

    # Mandatory Check Gate
    draw_box(68, 26, 26, 11, "Mandatory Compliance Gate",
             "Rule-based boolean check:\n- Ontario license held by bidder\n- WSIB clearance & $5M insurance\n- Budget ceiling compliance",
             c_rule)

    # Disqualified Branch (Proposal B)
    draw_box(6, 26, 26, 11, "Ineligible Proposals Queue",
             "status: 'ineligible' | rank: null\nDisqualified: Bidder does not\nhold license (Proposal B)\nAudit reason documented",
             c_danger)

    draw_arrow(68, 31.5, 32, 31.5, "Failed Mandatory", c_danger)

    # Deterministic Scoring Engine
    draw_box(37, 26, 26, 11, "Deterministic Scoring Engine",
             "Pure mathematical scoring (0-100):\n- Experience (30%): >=100kW installs\n- Price (25%): Lower cost formula\n- Timeline (15%): Shorter duration\n- Warranty (15%): Panel & labor\n- Team & Approach (15%): Crew/plan",
             c_rule)

    draw_arrow(68, 35, 63, 35, "Pass Mandatory", c_rule)

    # Ranking & Formatting
    draw_box(37, 12, 26, 10, "Ranking & JSON Formatter",
             "Sorts eligible bids by score desc\nAssigns integer ranks (1, 2, 3...)\nOutputs ranking.json format\n(Proposals A, E, D scored & ranked)",
             c_rule)

    draw_arrow(50, 26, 50, 22, "Itemized Scores", c_rule)

    # STAGE 4: HUMAN OVERSIGHT & AUDIT
    plt.text(4, 19.0, "STAGE 4: HUMAN OVERSIGHT, AUDIT & FINAL AWARD",
             fontsize=10.5, fontweight="bold", color="#1e293b", family="sans-serif")
    ax.axhline(18.3, color="#cbd5e1", linestyle="--", linewidth=1.2, xmin=0.04, xmax=0.96)

    # Reviewer Workspace (Human Checkpoint)
    draw_box(68, 8, 26, 11, "Reviewer Triage Workspace",
             "Human-in-the-Loop Workspace:\n- Side-by-side PDF quote inspect\n- Review flagged & ineligible bids\n- Resolve ambiguities / overrides\n- Mandatory reason for any change",
             c_human)

    # Audit Ledger
    draw_box(6, 8, 26, 11, "Immutable Audit Ledger",
             "Append-only log:\n- Criteria version & model snapshot\n- Input hashes & raw LLM JSON\n- Rule calculations & scores\n- Reviewer actions & override diffs",
             c_store)

    draw_arrow(63, 14, 68, 14, "Draft Rankings", c_rule)
    draw_arrow(68, 11, 32, 11, "Audit Events", c_store)

    # Final Award Decision (Human Decision)
    draw_box(37, 0.5, 26, 8.5, "Final Award Decision",
             "Human Officer signs award\n(Tool advises, human awards contract)\nComplete audit trail preserved",
             c_human)

    draw_arrow(81, 8, 63, 4.5, "Review Complete", c_human, curve=0.2)

    # Lateral connections to queues
    draw_arrow(19, 59, 19, 37, "", c_flag)
    draw_arrow(19, 26, 19, 19, "", c_danger)

    plt.tight_layout()
    plt.savefig(output_path, dpi=300, facecolor=fig.get_facecolor(), edgecolor="none")
    plt.close()
    print(f"Diagram successfully saved to {output_path}")

if __name__ == "__main__":
    create_flow_diagram("/home/kali/matacs-th-2026-02/diagram/process_flow.png")
