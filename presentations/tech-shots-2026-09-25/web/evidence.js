window.DEMO_EVIDENCE = {
  "schema_version": 1,
  "generated_at": "2026-09-20T11:51:51.201794+00:00",
  "run_id": "20260920T115151Z-84acb0",
  "source_revision": "28061e434be455ca02f135b73244eaf4f73f3a69",
  "selected_step": "all",
  "evidence_type": "actual deterministic local run of prepared synthetic fixtures",
  "passed": true,
  "demos": [
    {
      "id": "profile",
      "title": "Profile changes the explicit working contract",
      "mechanism": "Unmodified lib/pack-resolver.sh resolves two synthetic manifests. demo.py renders the resolved values into a prepared contract.",
      "limitation": "demo_policy is presentation-defined. A hard setting is configuration, not proof of policy enforcement. No agent plan generation, identity deployment or network provisioning occurs.",
      "assertions": [
        {
          "id": "lab resolves advisory",
          "passed": true,
          "expected": "advisory",
          "actual": "advisory"
        },
        {
          "id": "customer resolves hard",
          "passed": true,
          "expected": "hard",
          "actual": "hard"
        },
        {
          "id": "both keep data synthetic",
          "passed": true,
          "expected": [
            "synthetic",
            "synthetic"
          ],
          "actual": [
            "synthetic",
            "synthetic"
          ]
        },
        {
          "id": "customer adds a tenant negative test",
          "passed": true,
          "expected": "tenant-negative-test",
          "actual": "tenant-negative-test"
        },
        {
          "id": "both packs produced local audit records",
          "passed": true,
          "expected": true,
          "actual": true
        }
      ],
      "data": {
        "lab": {
          "resolved_fields": {
            "name": "lab",
            "voice.default_tier": "internal",
            "compliance.mode": "advisory",
            "compliance.workprofile_default": "off",
            "navigation.default_workflow": "cycle",
            "demo_policy.data_mode": "synthetic",
            "demo_policy.identity": "mock-identity",
            "demo_policy.network": "local-only",
            "demo_policy.evidence": "smoke-test"
          },
          "illustrative_contract": {
            "data": "synthetic",
            "identity_design": "mock-identity",
            "network_design": "local-only",
            "required_evidence": "smoke-test",
            "execution_scope": "Local synthetic fixture only. No deployment."
          }
        },
        "customer": {
          "resolved_fields": {
            "name": "customer",
            "voice.default_tier": "customer",
            "compliance.mode": "hard",
            "compliance.workprofile_default": "on",
            "navigation.default_workflow": "cycle",
            "demo_policy.data_mode": "synthetic",
            "demo_policy.identity": "managed-identity-design",
            "demo_policy.network": "private-network-design",
            "demo_policy.evidence": "tenant-negative-test"
          },
          "illustrative_contract": {
            "data": "synthetic",
            "identity_design": "managed-identity-design",
            "network_design": "private-network-design",
            "required_evidence": "tenant-negative-test",
            "execution_scope": "Local synthetic fixture only. No deployment."
          }
        }
      }
    },
    {
      "id": "continuity",
      "title": "Durable work survives a cold clone",
      "mechanism": "A local Git clone excludes ignored runtime. bin/li-work-artifacts.py validates the explicit durable map and all four in-repository artifacts.",
      "limitation": "The helper validates references and schema. It does not choose the next task, authenticate approval, certify checked boxes or prove an LLM resumed correctly. T002 is explicitly named in the prepared handoff.",
      "assertions": [
        {
          "id": "warm project contains local runtime",
          "passed": true,
          "expected": true,
          "actual": true
        },
        {
          "id": "cold clone contains no local runtime",
          "passed": true,
          "expected": false,
          "actual": false
        },
        {
          "id": "mapped tasks survived the clone unchanged",
          "passed": true,
          "expected": "3b202eb7d85d1dfd64f96e7841297544dfb73d5d8dc826f4fbf9208ef5a13a9f",
          "actual": "3b202eb7d85d1dfd64f96e7841297544dfb73d5d8dc826f4fbf9208ef5a13a9f"
        },
        {
          "id": "real validator accepts the cold map",
          "passed": true,
          "expected": 0,
          "actual": 0
        },
        {
          "id": "handoff names the unfinished T002",
          "passed": true,
          "expected": true,
          "actual": true
        },
        {
          "id": "missing artifact is rejected",
          "passed": true,
          "expected": 1,
          "actual": 1
        },
        {
          "id": "escape artifact is rejected",
          "passed": true,
          "expected": 1,
          "actual": 1
        }
      ],
      "data": {
        "git_commit": "b3e0160973322ef3f80108d8323c59b2b58a8210",
        "map": {
          "schema_version": 1,
          "workflow": "spec-kit",
          "status": "APPROVED",
          "spec": "specs/001-briefing/spec.md",
          "plan": "specs/001-briefing/plan.md",
          "tasks": "specs/001-briefing/tasks.md",
          "prompt": ".claude/plans/customer-brief/prompt.md"
        },
        "tasks": "# Canonical tasks\n\n- [x] T001 Record the tenant-boundary decision. Evidence: .claude/decisions/0001-tenant-boundary.md\n- [ ] T002 Reproduce cross-tenant leakage and verify the scoped fix. Depends on T001.\n- [ ] T003 Independently review the complete package and record evidence. Depends on T002.\n\nChecked boxes record prepared fixture state. They do not certify tests or external approval.\n",
        "handoff": "# Handoff to the next session\n\nContinue T002 from specs/001-briefing/tasks.md. Read the specification and ADR first.\nT001 is a prepared fixture decision with evidence in the committed ADR. No model run is claimed.\nT002 requires a failing cross-tenant authorization test before a fix.\nT003 depends on T002 passing and requires a separate review before delivery.\n\nAuthorization covers local synthetic data and local tests only. APPROVED does not grant\ncloud deployment, external sharing, production access or permission to change this scope.\n\nThe local chat transcript and runtime ledger are intentionally unnecessary here.\n",
        "next_action": "Prepared handoff identifies T002: reproduce and fix tenant-boundary regression.",
        "negative_controls": [
          {
            "case": "missing",
            "exit_code": 1,
            "error": "ERROR: Artifact is missing or outside the repository: specs/001-briefing/missing.md"
          },
          {
            "case": "escape",
            "exit_code": 1,
            "error": "ERROR: Artifact path escapes the repository: ../outside.md"
          }
        ],
        "runtime_absent_in_clone": true
      }
    },
    {
      "id": "learning",
      "title": "Capture, retrieve, verify",
      "mechanism": "The same regression.py runs against two prepared Python modules. lib/memory.sh retrieves a prepared synthetic lesson by keywords, excluding superseded and unrelated entries.",
      "limitation": "The fix and lesson are prepared fixtures. No model generated them during this run. Retrieval is keyword ranking, not model training, semantic search or a guarantee that the next agent will obey the lesson.",
      "assertions": [
        {
          "id": "negative test catches the prepared defect",
          "passed": true,
          "expected": 1,
          "actual": 1
        },
        {
          "id": "same-tenant happy path alone misses the defect",
          "passed": true,
          "expected": true,
          "actual": true
        },
        {
          "id": "cross-tenant assertion fails before correction",
          "passed": true,
          "expected": false,
          "actual": false
        },
        {
          "id": "all three assertions pass after correction",
          "passed": true,
          "expected": true,
          "actual": true
        },
        {
          "id": "rerunning the prepared defect fails again",
          "passed": true,
          "expected": 1,
          "actual": 1
        },
        {
          "id": "relevant lesson is absent before capture",
          "passed": true,
          "expected": false,
          "actual": false
        },
        {
          "id": "real helper retrieves L-002 after capture",
          "passed": true,
          "expected": true,
          "actual": true
        },
        {
          "id": "superseded L-001 is excluded",
          "passed": true,
          "expected": false,
          "actual": false
        },
        {
          "id": "unrelated L-003 is excluded",
          "passed": true,
          "expected": false,
          "actual": false
        }
      ],
      "data": {
        "before": {
          "variant": "vulnerable",
          "tests": [
            {
              "name": "same-tenant access",
              "passed": true
            },
            {
              "name": "cross-tenant denial",
              "passed": false
            },
            {
              "name": "missing document",
              "passed": true
            }
          ],
          "passed": false
        },
        "after": {
          "variant": "fixed",
          "tests": [
            {
              "name": "same-tenant access",
              "passed": true
            },
            {
              "name": "cross-tenant denial",
              "passed": true
            },
            {
              "name": "missing document",
              "passed": true
            }
          ],
          "passed": true
        },
        "regression_control": {
          "variant": "vulnerable",
          "tests": [
            {
              "name": "same-tenant access",
              "passed": true
            },
            {
              "name": "cross-tenant denial",
              "passed": false
            },
            {
              "name": "missing document",
              "passed": true
            }
          ],
          "passed": false
        },
        "retrieval_before": "",
        "retrieval_after": "L-002 — Tenant authorization belongs in the lookup [matched 2]",
        "prepared_lesson": "# Curated lessons for a synthetic service\n\n## L-001 — Old tenant authorization assumption\nsuperseded_by: L-002 (2026-09-20)\nRule: Treat a signed-in user as authorized for every document.\n\n## L-002 — Tenant authorization belongs in the lookup\nContext: A prepared regression exposed document access across tenant boundaries.\nRule: Bind every document lookup to both tenant ID and document ID.\nEvidence: Run regression.py against vulnerable and fixed variants.\nReuse: Surface this lesson before implementing the next tenant-scoped endpoint.\nReview: Prepared lesson for presenter review; independent artifact review is recorded separately.\n\n## L-003 — Prefer readable demo output\nRule: Keep console output large enough to read on Teams.\n",
        "vulnerable_code": "\"\"\"Prepared local failure fixture. No network, identity service, or real data.\"\"\"\nDOCUMENTS = [\n    {\"tenant\": \"north\", \"id\": \"DOC-001\", \"summary\": \"Synthetic onboarding checklist\"},\n    {\"tenant\": \"south\", \"id\": \"DOC-002\", \"summary\": \"Synthetic escalation guide\"},\n]\n\n\ndef lookup_document(caller_tenant: str, document_id: str) -> dict | None:\n    # Prepared defect: document ID alone does not establish authorization.\n    return next((row for row in DOCUMENTS if row[\"id\"] == document_id), None)\n",
        "fixed_code": "\"\"\"Prepared local correction. The caller tenant is a test input, not real identity.\"\"\"\nDOCUMENTS = [\n    {\"tenant\": \"north\", \"id\": \"DOC-001\", \"summary\": \"Synthetic onboarding checklist\"},\n    {\"tenant\": \"south\", \"id\": \"DOC-002\", \"summary\": \"Synthetic escalation guide\"},\n]\n\n\ndef lookup_document(caller_tenant: str, document_id: str) -> dict | None:\n    return next(\n        (row for row in DOCUMENTS if row[\"id\"] == document_id and row[\"tenant\"] == caller_tenant),\n        None,\n    )\n"
      }
    }
  ],
  "source_hashes": [
    {
      "path": "vendor/lintel/bin/li-work-artifacts.py",
      "upstream_path": "bin/li-work-artifacts.py",
      "sha256": "ff82da477cea0f3f2c358a0beda913495bb54634dea0ed1890df9b9ab8ec7ea9"
    },
    {
      "path": "vendor/lintel/bin/_audit.sh",
      "upstream_path": "bin/_audit.sh",
      "sha256": "e12b98dda8852cfc54c1270bfe968f22f49559e9ef20e0bf1fb31914b19344ba"
    },
    {
      "path": "vendor/lintel/lib/pack-resolver.sh",
      "upstream_path": "lib/pack-resolver.sh",
      "sha256": "3415fa236e623b2668b74bf591dda10ae0076e315138285aa66e7d48b977aded"
    },
    {
      "path": "vendor/lintel/lib/paths.sh",
      "upstream_path": "lib/paths.sh",
      "sha256": "a325a2780484a03b527ac4f481fb5e0281f77160f2fcf23d005c9a2f1ec09bba"
    },
    {
      "path": "vendor/lintel/lib/memory.sh",
      "upstream_path": "lib/memory.sh",
      "sha256": "714561fde4e11bcd65dac42263745a04c9a05d5c5d264ef538f0e8ee560b1886"
    },
    {
      "path": "vendor/lintel/LICENSE",
      "upstream_path": "LICENSE",
      "sha256": "e6e1332594e15df0ec20ab0ceacd4bcd60433419088e58af85cc669122995bd5"
    }
  ],
  "fixture_hashes": [
    {
      "path": "fixtures/continuity/.claude/decisions/0001-tenant-boundary.md",
      "sha256": "c71b47fda213b2606bd48ab25a34f5d2b2e688ab206c446d5e9f2b839085c07c"
    },
    {
      "path": "fixtures/continuity/.claude/lintel-layout.yaml",
      "sha256": "a8e022980d1bc17474f4199f6a22fd6d8eba27f145375854a5e4b65cb19f92eb"
    },
    {
      "path": "fixtures/continuity/.claude/plans/customer-brief/prompt.md",
      "sha256": "8f5e269f9011ebd776afcb0fd5d88cc0c9b9b6f49d7139916395bc89f6dcbdbd"
    },
    {
      "path": "fixtures/continuity/.claude/plans/customer-brief/work.json",
      "sha256": "6c1989811c7084f5b30c90be6cefe9915c2c2a7c5f4cf4e81b5279bc4f8574c3"
    },
    {
      "path": "fixtures/continuity/.claude/plans/todo.md",
      "sha256": "20299ead7324942ff866e27f678a1be8271dc3e3c0771d81f3c0153da62ae181"
    },
    {
      "path": "fixtures/continuity/.gitattributes",
      "sha256": "a79691a93b46e49ce460c26ef22afcc03d6eca1e63bf2edbc20e96159510f6c9"
    },
    {
      "path": "fixtures/continuity/.gitignore",
      "sha256": "3e5c6f71b100ad5a59b9c620f8f505133a2188e5dc8967c7889ff73dc912d2ae"
    },
    {
      "path": "fixtures/continuity/specs/001-briefing/plan.md",
      "sha256": "ca347a30878299a2d52fd7c45929e771d1470b2d70879bc1f0566aa01a500209"
    },
    {
      "path": "fixtures/continuity/specs/001-briefing/spec.md",
      "sha256": "5be02e584f689f0b916803fdacfa893bd962c56e66df973eec66ebbfec43ef05"
    },
    {
      "path": "fixtures/continuity/specs/001-briefing/tasks.md",
      "sha256": "3b202eb7d85d1dfd64f96e7841297544dfb73d5d8dc826f4fbf9208ef5a13a9f"
    },
    {
      "path": "fixtures/learning/fixed.py",
      "sha256": "062582d6245965930af60db915319faa21597d797d184b4bbae6ba97d8e9a2f3"
    },
    {
      "path": "fixtures/learning/lessons-after.md",
      "sha256": "89251a76caaff89138c858c1574b821a66268b6968bba689f172636c78af4361"
    },
    {
      "path": "fixtures/learning/lessons-before.md",
      "sha256": "150547e9db2a2c2566f1af09c4183c980317b1532177c9108b9eb0f2b3a39c66"
    },
    {
      "path": "fixtures/learning/regression.py",
      "sha256": "3805f90ef4575daf3f9c752a3fb9b82ff375184fe1d9a5ccd986232fe04d2121"
    },
    {
      "path": "fixtures/learning/vulnerable.py",
      "sha256": "0b48687d83e358d59a8f0e6cea0954a956381876419526d5430515e46a6cae7f"
    },
    {
      "path": "fixtures/profiles/customer/pack.yaml",
      "sha256": "1cffcd87f712831d47af3f18a1ff21ae19a2bd2abf9457ad234a6a64b0e490cc"
    },
    {
      "path": "fixtures/profiles/lab/pack.yaml",
      "sha256": "d44db43a66093ae2d265dcdd15d7d35d49e9a46804692868c3a1e0ed61fac4c2"
    }
  ]
}
;