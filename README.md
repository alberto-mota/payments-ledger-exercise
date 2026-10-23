# Payments ledger exercise

A small, self-contained problem for a live technical session. It takes about
35 minutes of focused work. Use whatever language, editor and tools you
normally use, AI assistants included. We are interested in how you work and
how you reason about the problem, not in a specific stack.

There is nothing to install. The input is one file of JSON lines and the
output is one JSON document.

## Context

A payment provider sends us webhook events about customers: payments that
succeeded or failed, refunds, and subscription status changes. Webhook
delivery is at-least-once and not ordered, so the same event can show up more
than once and events can arrive out of sequence.

We need a per-customer ledger built from those events.

## Your task

Write a program that reads `fixtures/events.jsonl` and writes a
`summary.json` with one entry per customer, following the rules below.

### Input

One event per line:

```json
{"id":"evt_001","type":"payment.succeeded","created":"2026-09-01T10:00:00Z",
 "data":{"customer_id":"cus_alpha","payment_id":"pay_a1","amount":4999,"currency":"usd"}}
```

Event types and their `data` fields:

| type                   | data fields                                              |
|------------------------|----------------------------------------------------------|
| `payment.succeeded`    | `customer_id`, `payment_id`, `amount`, `currency`        |
| `payment.failed`       | `customer_id`, `payment_id`, `amount`, `currency`, `reason` |
| `refund.created`       | `customer_id`, `payment_id`, `refund_id`, `amount`, `currency` |
| `subscription.updated` | `customer_id`, `subscription_id`, `status`               |

Amounts are integers in the smallest currency unit (cents). `created` is an
ISO 8601 UTC timestamp.

### Rules

1. An event `id` may appear more than once. Apply each event once.
2. Apply events in `created` order. If two events share a timestamp, use file order.
3. `paid` is the sum of `payment.succeeded` amounts.
4. `refunded` is the sum of `refund.created` amounts that reference a payment
   that succeeded, as long as the cumulative refunds for that payment do not
   exceed the payment amount. A refund that breaks either condition is not
   counted.
5. `net` is `paid - refunded`.
6. `failed_payments` is the count of `payment.failed` events.
7. `subscription_status` is the `status` from the latest `subscription.updated`
   event, or `null` if there is none.
8. `last_event_at` is the `created` of the latest event applied to the
   customer, across all four known types.
9. Events of a type not listed above are not applied.

### Output

```json
{
  "customers": {
    "cus_alpha": {
      "paid": 9998,
      "refunded": 1500,
      "net": 8498,
      "failed_payments": 0,
      "subscription_status": "active",
      "last_event_at": "2026-09-08T10:00:00Z"
    }
  },
  "anomalies": []
}
```

`anomalies` is a list of things your program chose not to apply, or applied
with reservations: duplicates, refunds it rejected, unknown event types, and
anything else you think an operator would want to see. The shape of each
entry is up to you, but include the event id and a reason.

### Things the rules do not settle

- One customer has a payment in a currency other than USD. Decide how to
  treat it and say why. `fixtures/expected.json` leaves that customer out.
- What belongs in `anomalies`, and what an operator should do with it.

Pick an answer, write it down in a short `NOTES.md` or in comments, and move
on. There is no single right call.

## Checking your output

```
python3 scripts/check.py summary.json
```

This compares the `customers` section against `fixtures/expected.json`.

## If you have time

Pick one. We will talk through whichever you choose, finished or not.

- **Incremental runs.** Make the program accept a previous `summary.json`
  (or a state file) plus a new batch of events, so running it twice over
  split batches gives the same result as one run over everything.
- **Scale.** Nothing to code. Sketch how you would run this against millions
  of events a day with several workers and at-least-once delivery, and where
  it breaks.

## Working together

Share your screen and think out loud. Ask questions whenever the spec is
unclear. If you use an AI assistant, that is fine. We would like to see how
you prompt it, how you check what it gives you, and what you change.

At the end, leave the code in whatever state it is in. A working core with
clear notes beats a polished half.
