package itspkannan.security.llma.policy_check

# adding word to prevent any flagging in github

deny_keywords = ["bad", "ugly"]
max_prompt_length = 300

check_blocked_word(prompt) if{
  contains(lower(prompt), deny_keywords[_])
}

check_prompt_length(prompt) if{
  count(prompt) > max_prompt_length
}