from self_healing_vio.recovery import RuleBasedRecoveryPolicy


def test_rule_based_recovery_policy_returns_valid_action():
    policy = RuleBasedRecoveryPolicy()
    action = policy.select_action(
        {"motion_blur": 0.1, "image_entropy": 0.6},
        {"camera": 0.8, "nominal": 0.2},
        40.0,
    )
    assert action.value in policy.valid_actions
