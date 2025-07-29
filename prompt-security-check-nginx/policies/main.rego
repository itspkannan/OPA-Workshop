package itspkannan.security

import data.itspkannan.security.llma.policy_check.check_blocked_word
import data.itspkannan.security.llma.policy_check.check_prompt_length

default allow = false

allow if{
  not check_blocked_word(input.prompt)
  not check_prompt_length(input.prompt)
}