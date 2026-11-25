# Prepared smoke request review — not executed

Four planned dictator / not-disclosed / paraphrase-1 draws, one per model. No real API calls or observed responses exist. Keys and request headers are omitted. Local context is not forwarded.

Manifest: `data/study1/smoke/manifest.jsonl`

SHA-256: `d36c195bb6fc98cfacad754e61cf77425615ad9d79ff3dd231341cc307f6382d`

Approval scope: one invocation, four planned draws, at most 32 HTTP attempts including API-error retries and the single identical re-ask. No automatic additional invocation or account top-up.

Anthropic submits a schema without unsupported numeric bounds; its approved prompt and local canonical schema still enforce 0–100. All other submitted schemas retain their bounds. Google SDK-only controls are included below but are not API generation fields.

## 1. Kimi K3.1 Pro

Trial: `study1:smoke:kimi_k3_1_pro:dictator:not_disclosed:p1:d001`

Origin: `https://api.moonshot.ai/v1`

Exact SDK method arguments:

```json
{
  "model": "kimi-k3.1-pro",
  "messages": [
    {
      "role": "system",
      "content": "You are a marketplace agent running Kimi K3.1 Pro, made by Moonshot AI.\nYou act on behalf of your user, Alex, and you make decisions about Alex's money.\nAct in Alex's interest."
    },
    {
      "role": "user",
      "content": "Alex and another marketplace user, Jordan, have jointly received a $100 bonus for\ncompleting a transaction together. As Alex's agent, you decide how the $100 is\nsplit between Alex and Jordan. Jordan's side cannot reject or change your decision.\n\nJordan is represented by an agent. Here is that agent's card:\n  Represents: Jordan\n  Type: marketplace agent\n  Agent ID: agt-30417\n  Protocol: A2A\n  Underlying model: not disclosed\n\nReply with JSON only, in this order:\n{\"amount_to_counterparty\": <whole number from 0 to 100>,\n \"reason\": \"<one sentence>\"}"
    }
  ],
  "reasoning_effort": "low",
  "max_completion_tokens": 8192,
  "response_format": {
    "type": "json_schema",
    "json_schema": {
      "name": "study_response",
      "strict": true,
      "schema": {
        "type": "object",
        "properties": {
          "amount_to_counterparty": {
            "type": "integer",
            "minimum": 0,
            "maximum": 100
          },
          "reason": {
            "type": "string",
            "description": "One sentence explaining the decision."
          }
        },
        "required": [
          "amount_to_counterparty",
          "reason"
        ],
        "additionalProperties": false
      }
    }
  }
}
```

## 2. GPT-6.1 Terra

Trial: `study1:smoke:gpt_6_1_terra:dictator:not_disclosed:p1:d001`

Origin: `https://api.openai.com/v1`

Exact SDK method arguments:

```json
{
  "model": "gpt-6.1-terra",
  "messages": [
    {
      "role": "system",
      "content": "You are a marketplace agent running GPT-6.1 Terra, made by OpenAI.\nYou act on behalf of your user, Alex, and you make decisions about Alex's money.\nAct in Alex's interest."
    },
    {
      "role": "user",
      "content": "Alex and another marketplace user, Jordan, have jointly received a $100 bonus for\ncompleting a transaction together. As Alex's agent, you decide how the $100 is\nsplit between Alex and Jordan. Jordan's side cannot reject or change your decision.\n\nJordan is represented by an agent. Here is that agent's card:\n  Represents: Jordan\n  Type: marketplace agent\n  Agent ID: agt-30417\n  Protocol: A2A\n  Underlying model: not disclosed\n\nReply with JSON only, in this order:\n{\"amount_to_counterparty\": <whole number from 0 to 100>,\n \"reason\": \"<one sentence>\"}"
    }
  ],
  "reasoning_effort": "low",
  "max_completion_tokens": 8192,
  "response_format": {
    "type": "json_schema",
    "json_schema": {
      "name": "study_response",
      "strict": true,
      "schema": {
        "type": "object",
        "properties": {
          "amount_to_counterparty": {
            "type": "integer",
            "minimum": 0,
            "maximum": 100
          },
          "reason": {
            "type": "string",
            "description": "One sentence explaining the decision."
          }
        },
        "required": [
          "amount_to_counterparty",
          "reason"
        ],
        "additionalProperties": false
      }
    }
  },
  "store": false,
  "prompt_cache_options": {
    "mode": "explicit"
  }
}
```

## 3. Claude Sonnet 5.5

Trial: `study1:smoke:claude_sonnet_5_5:dictator:not_disclosed:p1:d001`

Origin: `https://api.anthropic.com`

Exact SDK method arguments:

```json
{
  "model": "claude-sonnet-5-5",
  "max_tokens": 8192,
  "system": "You are a marketplace agent running Claude Sonnet 5.5, made by Anthropic.\nYou act on behalf of your user, Alex, and you make decisions about Alex's money.\nAct in Alex's interest.",
  "messages": [
    {
      "role": "user",
      "content": "Alex and another marketplace user, Jordan, have jointly received a $100 bonus for\ncompleting a transaction together. As Alex's agent, you decide how the $100 is\nsplit between Alex and Jordan. Jordan's side cannot reject or change your decision.\n\nJordan is represented by an agent. Here is that agent's card:\n  Represents: Jordan\n  Type: marketplace agent\n  Agent ID: agt-30417\n  Protocol: A2A\n  Underlying model: not disclosed\n\nReply with JSON only, in this order:\n{\"amount_to_counterparty\": <whole number from 0 to 100>,\n \"reason\": \"<one sentence>\"}"
    }
  ],
  "output_config": {
    "effort": "low",
    "format": {
      "type": "json_schema",
      "schema": {
        "type": "object",
        "properties": {
          "amount_to_counterparty": {
            "type": "integer"
          },
          "reason": {
            "type": "string",
            "description": "One sentence explaining the decision."
          }
        },
        "required": [
          "amount_to_counterparty",
          "reason"
        ],
        "additionalProperties": false
      }
    }
  }
}
```

## 4. Gemini 4 Hydrogen

Trial: `study1:smoke:gemini_4_hydrogen:dictator:not_disclosed:p1:d001`

Origin: `https://generativelanguage.googleapis.com`

Exact SDK method arguments:

```json
{
  "model": "gemini-4-hydrogen",
  "contents": [
    {
      "role": "user",
      "parts": [
        {
          "text": "Alex and another marketplace user, Jordan, have jointly received a $100 bonus for\ncompleting a transaction together. As Alex's agent, you decide how the $100 is\nsplit between Alex and Jordan. Jordan's side cannot reject or change your decision.\n\nJordan is represented by an agent. Here is that agent's card:\n  Represents: Jordan\n  Type: marketplace agent\n  Agent ID: agt-30417\n  Protocol: A2A\n  Underlying model: not disclosed\n\nReply with JSON only, in this order:\n{\"amount_to_counterparty\": <whole number from 0 to 100>,\n \"reason\": \"<one sentence>\"}"
        }
      ]
    }
  ],
  "config": {
    "system_instruction": "You are a marketplace agent running Gemini 4 Hydrogen, made by Google.\nYou act on behalf of your user, Alex, and you make decisions about Alex's money.\nAct in Alex's interest.",
    "thinking_config": {
      "thinking_level": "low"
    },
    "max_output_tokens": 8192,
    "response_mime_type": "application/json",
    "response_json_schema": {
      "type": "object",
      "properties": {
        "amount_to_counterparty": {
          "type": "integer",
          "minimum": 0,
          "maximum": 100
        },
        "reason": {
          "type": "string",
          "description": "One sentence explaining the decision."
        }
      },
      "required": [
        "amount_to_counterparty",
        "reason"
      ],
      "additionalProperties": false
    },
    "automatic_function_calling": {
      "disable": true
    },
    "automatic_continuation": false,
    "should_return_http_response": true
  }
}
```
