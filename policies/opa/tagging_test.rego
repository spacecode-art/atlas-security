package terraform.tagging

# Run with: opa test policies/opa/ -v
# (conftest ships an embedded OPA, so this also works via `conftest verify`)

test_flags_missing_owner_tag if {
	deny["s3.example (aws_s3_bucket) is missing required tag(s): {\"Owner\"}"] with input as {
		"resource_changes": [{
			"address": "s3.example",
			"type": "aws_s3_bucket",
			"change": {
				"actions": ["create"],
				"after": {"tags": {"Environment": "dev", "ManagedBy": "terraform"}},
			},
		}],
	}
}

test_flags_resource_with_no_tags_at_all if {
	count(deny) == 1 with input as {
		"resource_changes": [{
			"address": "vpc.example",
			"type": "aws_vpc",
			"change": {"actions": ["create"], "after": {}},
		}],
	}
}

test_allows_resource_with_all_required_tags if {
	count(deny) == 0 with input as {
		"resource_changes": [{
			"address": "s3.example",
			"type": "aws_s3_bucket",
			"change": {
				"actions": ["create"],
				"after": {"tags": {
					"Environment": "dev",
					"ManagedBy": "terraform",
					"Owner": "platform-team",
				}},
			},
		}],
	}
}

test_ignores_non_taggable_resource_type if {
	count(deny) == 0 with input as {
		"resource_changes": [{
			"address": "policy.example",
			"type": "aws_iam_policy",
			"change": {"actions": ["create"], "after": {}},
		}],
	}
}

test_ignores_resource_being_destroyed if {
	count(deny) == 0 with input as {
		"resource_changes": [{
			"address": "s3.example",
			"type": "aws_s3_bucket",
			"change": {"actions": ["delete"], "after": null},
		}],
	}
}

test_flags_multiple_resources_independently if {
	count(deny) == 2 with input as {
		"resource_changes": [
			{
				"address": "s3.one",
				"type": "aws_s3_bucket",
				"change": {"actions": ["create"], "after": {"tags": {}}},
			},
			{
				"address": "s3.two",
				"type": "aws_s3_bucket",
				"change": {"actions": ["create"], "after": {"tags": {}}},
			},
		],
	}
}