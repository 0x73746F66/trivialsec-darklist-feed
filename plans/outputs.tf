output "feed_processor_darklist_arn" {
  value = aws_lambda_function.feed_processor_darklist.arn
}
output "feed_processor_darklist_role" {
  value = aws_iam_role.feed_processor_darklist_role.name
}
output "feed_processor_darklist_role_arn" {
  value = aws_iam_role.feed_processor_darklist_role.arn
}
output "feed_processor_darklist_policy_arn" {
  value = aws_iam_policy.feed_processor_darklist_policy.arn
}
