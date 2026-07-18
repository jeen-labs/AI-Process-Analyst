"""
===============================================================================
AI Process Analyst
===============================================================================

Module:
    response_normalizer.py

Purpose:
    Normalize flexible LLM extraction responses into the canonical enterprise
    process schema expected by the schema validator.

Responsibilities:
    - Convert legacy/flexible LLM field names into canonical names
    - Generate required metadata fields
    - Normalize activities
    - Normalize actors
    - Normalize decisions
    - Normalize business rules
    - Normalize inputs, outputs, systems, risks, and controls
    - Produce schema-compatible process data

Author:
    Jeen Labs

Version:
    0.5.0

Status:
    Development
===============================================================================
"""

# =============================================================================
# Standard Library Imports
# =============================================================================

from typing import Any


# =============================================================================
# Constants
# =============================================================================

SCHEMA_VERSION = "1.0.0"

DEFAULT_PROCESS_LEVEL = 1

DEFAULT_STATUS = "Draft"


# =============================================================================
# Normalizer
# =============================================================================


class ResponseNormalizer:
    """
    Convert flexible LLM responses into the canonical enterprise process schema.
    """

    # -------------------------------------------------------------------------

    def normalize(
        self,
        response: dict[str, Any]
    ) -> dict[str, Any]:
        """
        Normalize an LLM response.

        Parameters
        ----------
        response : dict[str, Any]
            Parsed LLM response.

        Returns
        -------
        dict[str, Any]
            Canonical process schema structure.
        """

        if not isinstance(response, dict):

            raise ValueError(
                "Response to normalize must be a dictionary."
            )

        process_name = self._get_process_name(response)

        normalized = {

            "metadata": self._normalize_metadata(
                response
            ),

            "overview": self._normalize_overview(
                response
            ),

            "actors": self._normalize_actors(
                response.get(
                    "actors",
                    []
                )
            ),

            "systems": self._normalize_string_list(
                response.get(
                    "systems",
                    []
                )
            ),

            "documents": self._normalize_documents(
                response
            ),

            "inputs": self._normalize_string_list(
                response.get(
                    "inputs",
                    []
                )
            ),

            "outputs": self._normalize_string_list(
                response.get(
                    "outputs",
                    []
                )
            ),

            "activities": self._normalize_activities(
                response.get(
                    "activities",
                    []
                )
            ),

            "decisions": self._normalize_decisions(
                response.get(
                    "decision_points",
                    response.get(
                        "decisions",
                        []
                    )
                )
            ),

            "business_rules": self._normalize_business_rules(
                response.get(
                    "business_rules",
                    []
                )
            ),

            "risks": self._normalize_string_list(
                response.get(
                    "risks",
                    []
                )
            ),

            "controls": self._normalize_controls(
                response
            ),

            "kpis": self._normalize_kpis(
                response
            ),

            "relationships": self._normalize_relationships(
                response
            ),

            "source": self._normalize_source(
                response
            ),
        }

        #
        # Remove optional fields with empty values.
        #

        normalized = {
            key: value
            for key, value in normalized.items()
            if value not in (
                None,
                [],
                {}
            )
        }

        #
        # These fields are mandatory according to the schema.
        #

        if "metadata" not in normalized:

            normalized["metadata"] = self._normalize_metadata(
                response
            )

        if "overview" not in normalized:

            normalized["overview"] = {

                "description": "",

                "objective": "",

                "scope": "",
            }

        if "activities" not in normalized:

            normalized["activities"] = []

        return normalized

    # -------------------------------------------------------------------------

    def _get_process_name(
        self,
        response: dict[str, Any]
    ) -> str:
        """
        Extract process name.
        """

        metadata = response.get(
            "metadata",
            {}
        )

        if isinstance(metadata, dict):

            process_name = metadata.get(
                "process_name"
            )

            if process_name:

                return str(
                    process_name
                )

        process_name = response.get(
            "process_name",
            ""
        )

        return str(
            process_name
        )

    # -------------------------------------------------------------------------

    def _normalize_metadata(
        self,
        response: dict[str, Any]
    ) -> dict[str, Any]:
        """
        Normalize metadata into the canonical metadata structure.
        """

        source_metadata = response.get(
            "metadata",
            {}
        )

        if not isinstance(
            source_metadata,
            dict
        ):

            source_metadata = {}

        process_name = self._get_process_name(
            response
        )

        process_id = source_metadata.get(
            "process_id",
            source_metadata.get(
                "document_id",
                self._generate_process_id(
                    process_name
                )
            )
        )

        version = source_metadata.get(
            "version",
            "1.0"
        )

        status = source_metadata.get(
            "status",
            DEFAULT_STATUS
        )

        if status not in (
            "Draft",
            "Active",
            "Retired"
        ):

            status = DEFAULT_STATUS

        metadata = {

            "process_id": str(
                process_id
            ),

            "process_name": process_name,

            "process_level": DEFAULT_PROCESS_LEVEL,

            "version": str(
                version
            ),

            "status": status,

            "schema_version": SCHEMA_VERSION,
        }

        #
        # Optional metadata fields.
        #

        optional_fields = [

            "parent_process",

            "previous_process",

            "next_process",

            "created_by",

            "created_on",
        ]

        for field_name in optional_fields:

            if field_name in source_metadata:

                metadata[field_name] = (
                    source_metadata[field_name]
                )

        return metadata

    # -------------------------------------------------------------------------

    def _generate_process_id(
        self,
        process_name: str
    ) -> str:
        """
        Generate a stable process identifier.
        """

        normalized_name = (
            process_name
            .strip()
            .upper()
            .replace(
                " ",
                "-"
            )
        )

        return (
            f"PROC-{normalized_name}"
        )

    # -------------------------------------------------------------------------

    def _normalize_overview(
        self,
        response: dict[str, Any]
    ) -> dict[str, Any]:
        """
        Normalize process overview.
        """

        description = response.get(
            "description",
            ""
        )

        if not description:

            description = response.get(
                "process_description",
                ""
            )

        objective = response.get(
            "objective",
            ""
        )

        if isinstance(
            objective,
            list
        ):

            objective = "; ".join(
                str(
                    item
                )
                for item in objective
            )

        scope = response.get(
            "scope",
            ""
        )

        if isinstance(
            scope,
            dict
        ):

            scope_parts = []

            in_scope = scope.get(
                "in_scope",
                []
            )

            out_of_scope = scope.get(
                "out_of_scope",
                []
            )

            if in_scope:

                scope_parts.append(
                    "In scope: "
                    + ", ".join(
                        str(
                            item
                        )
                        for item in in_scope
                    )
                )

            if out_of_scope:

                scope_parts.append(
                    "Out of scope: "
                    + ", ".join(
                        str(
                            item
                        )
                        for item in out_of_scope
                    )
                )

            scope = "; ".join(
                scope_parts
            )

        overview = {

            "description": str(
                description
            ),

            "objective": str(
                objective
            ),

            "scope": str(
                scope
            ),
        }

        trigger = response.get(
            "trigger"
        )

        if trigger:

            overview["trigger"] = str(
                trigger
            )

        end_condition = response.get(
            "end_condition"
        )

        if end_condition:

            overview["end_condition"] = str(
                end_condition
            )

        return overview

    # -------------------------------------------------------------------------

    def _normalize_activities(
        self,
        activities: Any
    ) -> list[dict[str, Any]]:
        """
        Normalize activities into the enterprise schema.
        """

        if not isinstance(activities, list):
            return []

        normalized = []

        for index, activity in enumerate(activities, start=1):

            if isinstance(activity, str):
                activity = {
                    "activity_name": activity
                }

            if not isinstance(activity, dict):
                continue

            sequence = activity.get(
                "sequence_number",
                activity.get(
                    "sequence",
                    activity.get(
                        "step_number",
                        index
                    )
                )
            )

            name = activity.get(
                "activity_name",
                activity.get(
                    "name",
                    f"Activity {index}"
                )
            )

            description = activity.get(
                "activity_description",
                activity.get(
                    "description",
                    ""
                )
            )

            activity_type = activity.get(
                "activity_type",
                "Task"
            )

            normalized.append({

                "activity_id": f"ACT-{index:03d}",

                "activity_name": str(name),

                "activity_description": str(description),

                "activity_type": str(activity_type),

                "sequence_number": int(sequence),

                "actor_id": activity.get("actor_id"),

                "system_id": activity.get("system_id"),

                "input_documents": activity.get(
                    "input_documents",
                    []
                ),

                "output_documents": activity.get(
                    "output_documents",
                    []
                ),

                "business_rule_ids": activity.get(
                    "business_rule_ids",
                    []
                ),

                "next_activity": activity.get(
                    "next_activity"
                ),

                "exception_flow": activity.get(
                    "exception_flow"
                ),

                "estimated_duration": activity.get(
                    "estimated_duration"
                ),

                "automation_candidate": activity.get(
                    "automation_candidate",
                    False
                ),

                "notes": activity.get(
                    "notes",
                    ""
                )

            })

        return normalized

    # -------------------------------------------------------------------------

    def _normalize_actors(
        self,
        actors: Any
    ) -> list[dict[str, Any]]:
        """
        Normalize actors.
        """

        if not isinstance(
            actors,
            list
        ):

            return []

        normalized = []

        for index, actor in enumerate(
            actors,
            start=1
        ):

            if isinstance(
                actor,
                str
            ):

                actor = {

                    "actor_name": actor
                }

            if not isinstance(
                actor,
                dict
            ):

                continue

            actor_name = actor.get(
                "actor_name",
                actor.get(
                    "role",
                    actor.get(
                        "name",
                        f"Actor {index}"
                    )
                )
            )

            actor_type = actor.get(
                "actor_type",
                "Human"
            )

            normalized_actor = {

                "actor_id": (
                    f"ACTOR-{index:03d}"
                ),

                "actor_name": str(
                    actor_name
                ),

                "actor_type": str(
                    actor_type
                ),
            }

            normalized.append(
                normalized_actor
            )

        return normalized

    # -------------------------------------------------------------------------

    def _normalize_decisions(
        self,
        decisions: Any
    ) -> list[dict[str, Any]]:
        """
        Normalize decision points.
        """

        if not isinstance(decisions, list):
            return []

        normalized = []

        for index, decision in enumerate(decisions, start=1):

            if not isinstance(decision, dict):
                continue

            question = decision.get(
                "decision_question",
                decision.get(
                    "condition",
                    decision.get(
                        "question",
                        "Decision?"
                    )
                )
            )

            name = decision.get(
                "decision_name",
                decision.get(
                    "name",
                    f"Decision {index}"
                )
            )

            outgoing_paths = []

            if "outgoing_paths" in decision:

                outgoing_paths = decision["outgoing_paths"]

            else:

                true_path = decision.get(
                    "outcome_true",
                    "Next Activity"
                )

                false_path = decision.get(
                    "outcome_false",
                    "End"
                )

                outgoing_paths = [

                    {
                        "condition": "Yes",
                        "next_activity": str(true_path),
                        "business_rule_id": None
                    },

                    {
                        "condition": "No",
                        "next_activity": str(false_path),
                        "business_rule_id": None
                    }

                ]

            normalized.append({

                "decision_id": f"DEC-{index:03d}",

                "decision_name": str(name),

                "decision_question": str(question),

                "decision_type": decision.get(
                    "decision_type",
                    "Exclusive"
                ),

                "incoming_activity": decision.get(
                    "incoming_activity"
                ),

                "outgoing_paths": outgoing_paths,

                "default_path": decision.get(
                    "default_path"
                ),

                "notes": decision.get(
                    "notes",
                    ""
                )

            })

        return normalized

    # -------------------------------------------------------------------------

    def _normalize_business_rules(
        self,
        rules: Any
    ) -> list[dict[str, Any]]:
        """
        Normalize business rules.
        """

        if not isinstance(rules, list):
            return []

        normalized = []

        for index, rule in enumerate(rules, start=1):

            if isinstance(rule, str):

                rule = {
                    "rule_statement": rule
                }

            if not isinstance(rule, dict):
                continue

            statement = rule.get(
                "rule_statement",
                rule.get(
                    "rule",
                    rule.get(
                        "description",
                        ""
                    )
                )
            )

            name = rule.get(
                "rule_name",
                f"Business Rule {index}"
            )

            normalized.append({

                "rule_id": f"RULE-{index:03d}",

                "rule_name": str(name),

                "rule_description": rule.get(
                    "rule_description",
                    ""
                ),

                "rule_type": rule.get(
                    "rule_type",
                    "Other"
                ),

                "rule_statement": str(statement),

                "source_reference": rule.get(
                    "source_reference"
                ),

                "applies_to_activities": rule.get(
                    "applies_to_activities",
                    []
                ),

                "related_decisions": rule.get(
                    "related_decisions",
                    []
                ),

                "priority": rule.get(
                    "priority",
                    "Medium"
                ),

                "mandatory": rule.get(
                    "mandatory",
                    False
                ),

                "automatable": rule.get(
                    "automatable",
                    False
                ),

                "owner": rule.get(
                    "owner"
                ),

                "effective_date": rule.get(
                    "effective_date"
                ),

                "review_date": rule.get(
                    "review_date"
                ),

                "notes": rule.get(
                    "notes",
                    ""
                )

            })

        return normalized

    # -------------------------------------------------------------------------

    def _normalize_string_list(
        self,
        values: Any
    ) -> list[str]:
        """
        Normalize values into a list of strings.
        """

        if not isinstance(
            values,
            list
        ):

            return []

        normalized = []

        for value in values:

            if isinstance(
                value,
                str
            ):

                normalized.append(
                    value
                )

            elif isinstance(
                value,
                dict
            ):

                name = value.get(
                    "name"
                )

                if name:

                    normalized.append(
                        str(
                            name
                        )
                    )

        return normalized

    # -------------------------------------------------------------------------

    def _normalize_documents(
        self,
        response: dict[str, Any]
    ) -> list[str]:
        """
        Extract document names from inputs and source data.
        """

        documents = response.get(
            "documents",
            []
        )

        return self._normalize_string_list(
            documents
        )

    # -------------------------------------------------------------------------

    def _normalize_controls(
        self,
        response: dict[str, Any]
    ) -> list[str]:
        """
        Normalize controls.
        """

        controls = response.get(
            "controls",
            []
        )

        return self._normalize_string_list(
            controls
        )

    # -------------------------------------------------------------------------

    def _normalize_kpis(
        self,
        response: dict[str, Any]
    ) -> list[str]:
        """
        Normalize KPIs.
        """

        kpis = response.get(
            "kpis",
            []
        )

        if isinstance(
            kpis,
            list
        ):

            normalized = []

            for kpi in kpis:

                if isinstance(
                    kpi,
                    str
                ):

                    normalized.append(
                        kpi
                    )

                elif isinstance(
                    kpi,
                    dict
                ):

                    metric = kpi.get(
                        "metric"
                    )

                    target = kpi.get(
                        "target"
                    )

                    if metric and target:

                        normalized.append(
                            f"{metric}: {target}"
                        )

                    elif metric:

                        normalized.append(
                            str(
                                metric
                            )
                        )

            return normalized

        return []

    # -------------------------------------------------------------------------

    def _normalize_relationships(
        self,
        response: dict[str, Any]
    ) -> dict[str, Any]:
        """
        Normalize process relationships.
        """

        relationships = response.get(
            "relationships",
            {}
        )

        if not isinstance(
            relationships,
            dict
        ):

            relationships = {}

        for field_name in (
            "previous_process",
            "next_process",
            "subprocesses",
        ):

            if field_name in response:

                relationships[
                    field_name
                ] = response[
                    field_name
                ]

        return relationships

    # -------------------------------------------------------------------------

    def _normalize_source(
        self,
        response: dict[str, Any]
    ) -> dict[str, Any]:
        """
        Normalize source information.
        """

        source = response.get(
            "source",
            {}
        )

        if not isinstance(
            source,
            dict
        ):

            return {}

        return source


# =============================================================================
# Main
# =============================================================================

if __name__ == "__main__":

    normalizer = ResponseNormalizer()

    sample_response = {

        "process_name": "Customer Onboarding",

        "description": (
            "A customer onboarding process."
        ),

        "objective": [
            "Ensure consistent onboarding."
        ],

        "activities": [

            {

                "sequence": 1,

                "name": "Receive Application",

                "description": (
                    "Receive the customer application."
                ),
            }
        ],

        "actors": [

            "Customer Service Officer"
        ],

        "systems": [

            "CRM"
        ],

        "inputs": [

            "Customer Application"
        ],

        "outputs": [

            "Customer Record"
        ],
    }

    normalized = normalizer.normalize(
        sample_response
    )

    import json

    print(
        json.dumps(
            normalized,
            indent=4
        )
    )