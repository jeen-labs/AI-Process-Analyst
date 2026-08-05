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
        Normalize enterprise activities into the canonical schema.
        """

        if not isinstance(
            activities,
            list
        ):

            return []

        normalized = []

        for index, activity in enumerate(
            activities,
            start=1
        ):

            #
            # Support simple activity names.
            #

            if isinstance(
                activity,
                str
            ):

                activity = {
                    "name": activity
                }

            if not isinstance(
                activity,
                dict
            ):

                continue

            #
            # Sequence
            #

            sequence = activity.get(
                "sequence_number",
                activity.get(
                    "sequence",
                    activity.get(
                        "step_number",
                        activity.get(
                            "step",
                            index
                        )
                    )
                )
            )

            try:

                sequence = int(sequence)

            except Exception:

                sequence = index

            #
            # Activity Name
            #

            activity_name = activity.get(
                "activity_name",
                activity.get(
                    "name",
                    f"Activity {sequence}"
                )
            )

            #
            # Activity Type
            #

            activity_type = activity.get(
                "activity_type",
                "Task"
            )

            #
            # Some LLMs misuse "phase".
            # Preserve it as a note instead.
            #

            phase = activity.get(
                "phase"
            )

            normalized_activity = {

                "activity_id":
                    f"ACT-{sequence:03d}",

                "activity_name":
                    str(activity_name),

                "activity_type":
                    str(activity_type),

                "sequence_number":
                    sequence,
            }

            #
            # Description
            #

            description = activity.get(
                "activity_description",
                activity.get(
                    "description"
                )
            )

            if description:

                normalized_activity[
                    "activity_description"
                ] = str(description)

            #
            # Actor Reference
            #

            actor = (
                activity.get("actor_id")
                or activity.get("performed_by")
                or activity.get("actors")
            )

            if isinstance(
                actor,
                list
            ) and actor:

                normalized_activity[
                    "actor_id"
                ] = str(actor[0])

            elif isinstance(
                actor,
                str
            ):

                normalized_activity[
                    "actor_id"
                ] = actor

            #
            # Systems
            #

            systems = activity.get(
                "systems",
                []
            )

            if isinstance(
                systems,
                list
            ) and systems:

                normalized_activity[
                    "system_id"
                ] = str(systems[0])

            #
            # Documents
            #

            inputs = activity.get(
                "input_documents",
                activity.get(
                    "inputs",
                    []
                )
            )

            if isinstance(
                inputs,
                list
            ):

                normalized_activity[
                    "input_documents"
                ] = [

                    str(item)

                    for item in inputs
                ]

            outputs = activity.get(
                "output_documents",
                activity.get(
                    "outputs",
                    []
                )
            )

            if isinstance(
                outputs,
                list
            ):

                normalized_activity[
                    "output_documents"
                ] = [

                    str(item)

                    for item in outputs
                ]

            #
            # Business Rule References
            #

            rules = activity.get(
                "business_rule_ids",
                activity.get(
                    "business_rules",
                    []
                )
            )

            if isinstance(
                rules,
                list
            ):

                normalized_activity[
                    "business_rule_ids"
                ] = [

                    str(rule)

                    for rule in rules
                ]

            #
            # Navigation
            #

            next_activity = activity.get(
                "next_activity"
            )

            if next_activity:

                normalized_activity[
                    "next_activity"
                ] = str(next_activity)

            exception_flow = activity.get(
                "exception_flow"
            )

            if exception_flow:

                normalized_activity[
                    "exception_flow"
                ] = str(exception_flow)

            #
            # Duration
            #

            duration = activity.get(
                "estimated_duration",
                activity.get(
                    "duration"
                )
            )

            if duration:

                normalized_activity[
                    "estimated_duration"
                ] = str(duration)

            #
            # Automation Candidate
            #

            automation = activity.get(
                "automation_candidate"
            )

            if isinstance(
                automation,
                bool
            ):

                normalized_activity[
                    "automation_candidate"
                ] = automation

            #
            # Notes
            #

            notes = []

            if phase:

                notes.append(
                    f"Phase: {phase}"
                )

            details = activity.get(
                "details"
            )

            if details:

                notes.append(
                    str(details)
                )

            if notes:

                normalized_activity[
                    "notes"
                ] = "\n".join(
                    notes
                )

            normalized.append(
                normalized_activity
            )

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
        Normalize enterprise decision points into the canonical schema.
        """

        if not isinstance(
            decisions,
            list
        ):

            return []

        normalized = []

        for index, decision in enumerate(
            decisions,
            start=1
        ):

            #
            # Ignore invalid objects.
            #

            if not isinstance(
                decision,
                dict
            ):

                continue

            #
            # Decision Name
            #

            decision_name = decision.get(
                "decision_name",
                decision.get(
                    "name",
                    decision.get(
                        "decision",
                        f"Decision {index}"
                    )
                )
            )

            #
            # Decision Question
            #

            decision_question = decision.get(
                "decision_question",
                decision.get(
                    "question",
                    decision.get(
                        "condition",
                        "Decision?"
                    )
                )
            )

            #
            # Decision Type
            #

            decision_type = decision.get(
                "decision_type",
                "Exclusive"
            )

            normalized_decision = {

                "decision_id":
                    f"DEC-{index:03d}",

                "decision_name":
                    str(decision_name),

                "decision_question":
                    str(decision_question),

                "decision_type":
                    str(decision_type)
            }

            #
            # Description
            #

            description = decision.get(
                "description"
            )

            if description:

                normalized_decision[
                    "decision_description"
                ] = str(description)

            #
            # Criteria
            #

            criteria = decision.get(
                "criteria"
            )

            if isinstance(criteria, list):

                normalized_decision["decision_criteria"] = [
                    str(item)
                    for item in criteria
                ]

            elif criteria:

                normalized_decision["decision_criteria"] = [
                    str(criteria)
                ]

            #
            # Incoming Activity
            #

            incoming = decision.get(
                "incoming_activity"
            )

            if incoming:

                normalized_decision[
                    "incoming_activity"
                ] = str(incoming)

            #
            # Default Path
            #

            default_path = decision.get(
                "default_path"
            )

            if default_path:

                normalized_decision[
                    "default_path"
                ] = str(default_path)

            #
            # Actor Reference
            #

            actors = (
                decision.get("actors")
                or decision.get("performed_by")
                or decision.get("actor")
            )

            if isinstance(
                actors,
                list
            ) and actors:

                normalized_decision[
                    "actor_id"
                ] = str(actors[0])

            elif isinstance(
                actors,
                str
            ):

                normalized_decision[
                    "actor_id"
                ] = actors

            #
            # System Reference
            #

            systems = decision.get(
                "systems",
                []
            )

            if isinstance(
                systems,
                list
            ) and systems:

                normalized_decision[
                    "system_id"
                ] = str(systems[0])

            #
            # Business Rules
            #

            rules = decision.get(
                "business_rule_ids",
                decision.get(
                    "business_rules",
                    []
                )
            )

            if isinstance(
                rules,
                list
            ):

                normalized_decision[
                    "business_rule_ids"
                ] = [

                    str(rule)

                    for rule in rules

                ]

            #
            # Build outgoing paths.
            #

            outgoing_paths = []

            #
            # Canonical structure
            #

            if isinstance(
                decision.get("outgoing_paths"),
                list
            ):

                for path in decision["outgoing_paths"]:

                    if not isinstance(
                        path,
                        dict
                    ):

                        continue

                    outgoing_paths.append({

                        "condition":
                            str(
                                path.get(
                                    "condition",
                                    "Unknown"
                                )
                            ),

                        "next_activity":
                            str(
                                path.get(
                                    "next_activity",
                                    path.get(
                                        "outcome",
                                        ""
                                    )
                                )
                            ),

                        "business_rule_id":
                            path.get(
                                "business_rule_id"
                            )

                    })

            #
            # Generic options
            #

            elif isinstance(
                decision.get("options"),
                list
            ):

                for option in decision["options"]:

                    if not isinstance(
                        option,
                        dict
                    ):

                        continue

                    outgoing_paths.append({

                        "condition":
                            str(
                                option.get(
                                    "condition",
                                    "Unknown"
                                )
                            ),

                        "next_activity":
                            str(
                                option.get(
                                    "outcome",
                                    ""
                                )
                            ),

                        "business_rule_id":
                            None

                    })

            #
            # Yes / No
            #

            elif (

                "yes_path" in decision
                or
                "no_path" in decision

            ):

                if decision.get("yes_path"):

                    outgoing_paths.append({

                        "condition":
                            "Yes",

                        "next_activity":
                            str(
                                decision["yes_path"]
                            ),

                        "business_rule_id":
                            None

                    })

                if decision.get("no_path"):

                    outgoing_paths.append({

                        "condition":
                            "No",

                        "next_activity":
                            str(
                                decision["no_path"]
                            ),

                        "business_rule_id":
                            None

                    })

            #
            # Pass / Fail
            #

            elif (

                "pass_path" in decision
                or
                "fail_path" in decision

            ):

                if decision.get("pass_path"):

                    outgoing_paths.append({

                        "condition":
                            "Pass",

                        "next_activity":
                            str(
                                decision["pass_path"]
                            ),

                        "business_rule_id":
                            None

                    })

                if decision.get("fail_path"):

                    outgoing_paths.append({

                        "condition":
                            "Fail",

                        "next_activity":
                            str(
                                decision["fail_path"]
                            ),

                        "business_rule_id":
                            None

                    })

            #
            # True / False
            #

            elif (

                "outcome_true" in decision
                or
                "outcome_false" in decision

            ):

                if decision.get("outcome_true"):

                    outgoing_paths.append({

                        "condition":
                            "True",

                        "next_activity":
                            str(
                                decision["outcome_true"]
                            ),

                        "business_rule_id":
                            None

                    })

                if decision.get("outcome_false"):

                    outgoing_paths.append({

                        "condition":
                            "False",

                        "next_activity":
                            str(
                                decision["outcome_false"]
                            ),

                        "business_rule_id":
                            None

                    })

            if outgoing_paths:

                normalized_decision[
                    "outgoing_paths"
                ] = outgoing_paths

            #
            # Notes
            #

            notes = []

            for field in (

                "details",
                "notes",
                "comments"

            ):

                value = decision.get(field)

                if value:

                    notes.append(
                        str(value)
                    )

            if notes:

                normalized_decision[
                    "notes"
                ] = "\n".join(
                    notes
                )

            normalized.append(
                normalized_decision
            )

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