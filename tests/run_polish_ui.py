"""Run local UI state regressions without paid model requests.
Requires Chrome and Playwright. CUSTOMCHAT_TEST_URL must point at a disposable
CustomChat fixture, not a user's running workspace. Requests mutate fixtures.
"""
import os,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parent
CASES=['review_precision','save_guards','first_paint','appearance_states','freshness_states','navigation_races','source_states','code_states','completion_boundaries','motion_safety','font_menu_truth','review_capabilities','prompt_save_states','setup_states','setup_roundtrip','budget_captured','answer_captured','helper_key_states','prompt_generation_states','helper_copy_states','preset_preview','source_services','logo_states','config_labels','about_team','config_header','config_utility','config_layout','config_workspace','config_actions','config_alignment','local_model_estimates','local_download_states','cloud_recommendation','provider_layout','shared_components','editing_contrast','editing_actions','editing_typography','settings_finder_clarity','connector_clarity','connector_geometry','helper_execution_clarity','category_selection','chat_icon_targets','answer_actions','clipboard_feedback']
if __name__=='__main__':
 if not os.environ.get('CUSTOMCHAT_TEST_URL'):raise SystemExit('Set CUSTOMCHAT_TEST_URL to a disposable fixture before running.')
 for case in CASES:subprocess.run(['node',str(ROOT/(case+'_browser.cjs'))],check=True,env=os.environ)
