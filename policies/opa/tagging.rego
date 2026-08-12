package terraform.tagging

# Mandatory tagging policy — enforced org-wide across every Atlas repo.
#
# Rationale: Checkov and tfsec scan for vulnerabilities and misconfigurations,
# not for organizational conventions. A resource missing an Owner tag isn't a
# security finding — but it's exactly the kind of gap that turns a routine
# incident into a scavenger hunt for "whose resource is this and can I touch
# it." This policy exists to make that gap impossible to merge.
#
# Input: `terraform show -json <plan>` (a Terraform plan in JSON form), which
# is what `conftest test` is pointed at in reusable-opa-scan.yml.

required_tags := {"Environment", "ManagedBy", "Owner"}

# Resource types this policy applies to. Deliberately explicit rather than
# "every resource with a tags argument" — some AWS resources (e.g. IAM
# policies, route table associations) don't support tags at all, and a
# blanket rule would produce noise the team learns to ignore.
taggable_types := {
	"aws_s3_bucket",
	"aws_vpc",
	"aws_subnet",
	"aws_security_group",
	"aws_db_instance",
	"aws_db_subnet_group",
	"aws_internet_gateway",
	"aws_route_table",
}

# One deny message per resource, per missing tag — specific enough that a CI
# failure tells you exactly what to fix without opening the policy source.
deny[msg] {
	change := input.resource_changes[_]
	taggable_types[change.type]
	not is_being_destroyed(change)

	tags := object.get(change.change.after, "tags", {})
	missing := required_tags - {k | tags[k]}
	count(missing) > 0

	msg := sprintf(
		"%s (%s) is missing required tag(s): %v",
		[change.address, change.type, missing],
	)
}

is_being_destroyed(change) {
	change.change.actions[_] == "delete"
	count(change.change.actions) == 1
}