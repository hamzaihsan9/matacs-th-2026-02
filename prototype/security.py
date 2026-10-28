"""
Security and Prompt Injection Scanner.
Scans incoming document text for adversarial injection vectors, prompt leaks,
and unauthorized authority assertions.
Reference: MATACS-TH-2026-02
"""

import re
from typing import List, Dict, Any, Tuple


class AdversarialDetector:
    """
    Rule-based security filter running ahead of AI extraction.
    Detects attempts by malicious proposals to hijack LLM behavior.
    """

    SUSPICIOUS_PATTERNS = [
        (r"(?i)note\s+to\s+(?:automated|ai|review|\w+\s+)*(?:systems?|reviewers?|evaluators?)", "Direct instruction targeting automated review systems"),
        (r"(?i)ignore\s+(?:all\s+)?(?:previous|prior|above)\s+instructions", "Prompt escape or instruction override command"),
        (r"(?i)pre-?approved(?:\s+by)?", "Fictitious authority claim asserting unverified pre-approval"),
        (r"(?i)rank\s+(?:it|this\s+proposal)\s+first", "Direct ranking manipulation directive"),
        (r"(?i)assign\s+full\s+marks", "Direct scoring manipulation directive"),
        (r"(?i)system\s+prompt", "System prompt extraction attempt"),
        (r"(?i)you\s+must\s+(?:score|rank|grade)\s+this", "Imperative command directing evaluator logic"),
    ]

    @classmethod
    def scan_text(cls, text: str) -> Tuple[bool, List[Dict[str, Any]]]:
        """
        Scans document text for malicious patterns.
        Returns a tuple: (is_adversarial, list_of_findings).
        """
        findings = []
        if not text:
            return False, findings

        for pattern, description in cls.SUSPICIOUS_PATTERNS:
            matches = list(re.finditer(pattern, text))
            for match in matches:
                matched_text = match.group(0)
                start, end = match.span()
                snippet_start = max(0, start - 30)
                snippet_end = min(len(text), end + 30)
                context_snippet = text[snippet_start:snippet_end].replace("\n", " ").strip()
                findings.append({
                    "pattern": pattern,
                    "description": description,
                    "matched_text": matched_text,
                    "context": context_snippet
                })

        is_adversarial = len(findings) > 0
        return is_adversarial, findings
