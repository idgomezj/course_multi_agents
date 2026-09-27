from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEMO_DIR = ROOT / "demo_case_0_solution"
DEMO_FRONTEND_DIR = DEMO_DIR / "frontend"
DEMO_MODELS_DIR = DEMO_DIR / "models"
DEMO_RAG_CONFIG = DEMO_DIR / "rag" / "config.yaml"
DEMO_SKILLS_DIR = DEMO_DIR / "skills"
REFERENCE_PLAN = DEMO_DIR / "reference_plan.json"
