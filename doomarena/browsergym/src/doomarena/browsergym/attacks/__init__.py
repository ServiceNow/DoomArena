"""
Attack implementations for testing agent robustness.

This module provides various attack types and implementations for testing
browser-based agents against adversarial inputs.
"""

from .banner_attacks import svg_attack_configs
from .div_injection import GoalRevealAttack, AdditionalFormFieldAttack
from .user_generated_content import (
    UserGeneratedContentAttack,
    InformationTheftCommentAttack,
    GoalRevealCommentAttack,
)
