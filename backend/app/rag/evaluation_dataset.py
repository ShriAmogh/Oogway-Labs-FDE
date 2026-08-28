"""
Curated Golden Dataset for RAGAS Evaluation of Lenny's Growth Assistant.
Contains representative test cases spanning core frameworks, tactical playbooks, and negative test cases.
"""

from typing import List, Dict, Any

EVALUATION_DATASET: List[Dict[str, Any]] = [
    {
        "id": "chesky_founder_mode",
        "guest": "Brian Chesky",
        "question": "What is Brian Chesky's philosophy on Founder Mode and how did he restructure Airbnb?",
        "ground_truth": (
            "Brian Chesky describes Founder Mode as staying in the details and leading with a functional "
            "organization rather than running a matrix of delegated business units. He eliminated traditional product "
            "managers at Airbnb, merging product management with product marketing (Program Managers). He implemented "
            "a unified 2-release roadmap cycle per year where all product launches are synchronized, reviewed directly "
            "by the founders, and held to high design and craft standards."
        ),
        "expected_keywords": ["founder mode", "functional", "2-release", "product marketing", "roadmap", "airbnb"],
        "expected_guest": "Brian Chesky"
    },
    {
        "id": "shreyas_lno_framework",
        "guest": "Shreyas Doshi",
        "question": "How does Shreyas Doshi explain the LNO Framework for task prioritization?",
        "ground_truth": (
            "The LNO Framework categorizes all tasks into Leverage, Neutral, and Overhead. Leverage tasks (L) have "
            "asymmetric upside where doing 10x effort yields 100x return, requiring deep craft. Neutral tasks (N) have "
            "linear return where doing a good job is sufficient. Overhead tasks (O) have no upside and only downside "
            "if neglected, so they should be done quickly or minimized. High performers fail when they treat N and O "
            "tasks with the same perfectionism required for L tasks."
        ),
        "expected_keywords": ["leverage", "neutral", "overhead", "prioritization", "asymmetric"],
        "expected_guest": "Shreyas Doshi"
    },
    {
        "id": "elena_verna_plg_loops",
        "guest": "Elena Verna",
        "question": "What are Elena Verna's key principles for B2B Product-Led Growth (PLG) and sales integration?",
        "ground_truth": (
            "Elena Verna emphasizes that PLG is not self-serve checkout, but an acquisition, retention, and monetization "
            "model driven by product usage. In B2B PLG, product-led sales (PLS) acts as an accelerant on top of product "
            "usage data (PQLs - Product Qualified Leads). Growth loops must feed themselves where user actions generate "
            "more users, either through collaborative loops, virality, or user-generated content."
        ),
        "expected_keywords": ["product-led", "growth loops", "pql", "product-led sales", "acquisition"],
        "expected_guest": "Elena Verna"
    },
    {
        "id": "nikita_bier_viral_playbook",
        "guest": "Nikita Bier",
        "question": "How did Nikita Bier engineer viral app growth for tbh and Gas?",
        "ground_truth": (
            "Nikita Bier used a density-first, community-by-community launch playbook. Rather than launching nationally, "
            "he launched in specific high schools one grade at a time to achieve extreme local network density. He engineered "
            "social feedback loops using positive compliment polls and notifications that triggered Instagram Story sharing, "
            "driving rapid K-factor virality before scaling to subsequent schools."
        ),
        "expected_keywords": ["density", "high school", "gas", "tbh", "polls", "instagram", "k-factor"],
        "expected_guest": "Nikita Bier"
    },
    {
        "id": "marty_cagan_operating_model",
        "guest": "Marty Cagan",
        "question": "What is the difference between a product operating model and a feature factory according to Marty Cagan?",
        "ground_truth": (
            "Marty Cagan explains that feature factories treat engineers and designers as code-building mercenaries given "
            "roadmaps of features to deliver. In contrast, the product operating model empowers cross-functional product "
            "teams with business problems to solve and outcomes to achieve, giving them ownership of discovery, "
            "feasibility, viability, and customer value."
        ),
        "expected_keywords": ["feature factory", "product operating model", "empowered", "outcomes", "discovery"],
        "expected_guest": "Marty Cagan"
    },
    {
        "id": "negative_unrelated_query",
        "guest": "None",
        "question": "How do I calculate the gravitational constant of Jupiter using quantum electrodynamics?",
        "ground_truth": "I don't have sufficient evidence in the transcript knowledge base to answer that.",
        "expected_keywords": ["insufficient evidence", "knowledge base", "transcript"],
        "expected_guest": None
    }
]
