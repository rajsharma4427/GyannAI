from typing import Optional, Set
from backend.contracts import Topic, MistakeAnalysis, BacktraceInfo, GapType

MAX_BACKTRACE_DEPTH = 3


class GraphValidationError(ValueError):
    pass


def validate_topic_graph(topics: list[Topic]) -> None:
    """Validate that topic list forms a valid, acyclic directed graph of prerequisites.
    
    Checks:
    - All topic IDs are non-empty and unique.
    - No topic has a prerequisite pointing to itself.
    - Every prerequisite ID references an existing topic in the list.
    - The graph contains no cycles.
    """
    seen_ids: Set[str] = set()
    for topic in topics:
        if not topic.id or not topic.id.strip():
            raise GraphValidationError("Topic ID cannot be empty.")
        if topic.id in seen_ids:
            raise GraphValidationError(f"Duplicate topic ID found: '{topic.id}'")
        seen_ids.add(topic.id)

    # Validate prerequisites exist and no self-loops
    for topic in topics:
        for prereq_id in topic.prereq_ids:
            if prereq_id == topic.id:
                raise GraphValidationError(
                    f"Topic '{topic.id}' cannot have itself as a prerequisite."
                )
            if prereq_id not in seen_ids:
                raise GraphValidationError(
                    f"Topic '{topic.id}' references non-existent prerequisite '{prereq_id}'"
                )

    # Cycle detection using DFS (White=unvisited, Gray=visiting, Black=visited)
    adj: dict[str, list[str]] = {t.id: t.prereq_ids for t in topics}
    visiting: Set[str] = set()
    visited: Set[str] = set()

    def dfs(node: str, path: list[str]) -> None:
        visiting.add(node)
        path.append(node)
        for neighbor in adj.get(node, []):
            if neighbor in visiting:
                cycle_str = " -> ".join(path + [neighbor])
                raise GraphValidationError(f"Cycle detected in topic graph: {cycle_str}")
            if neighbor not in visited:
                dfs(neighbor, path)
        path.pop()
        visiting.remove(node)
        visited.add(node)

    for topic_id in seen_ids:
        if topic_id not in visited:
            dfs(topic_id, [])


def evaluate_backtrace_step(
    analysis: MistakeAnalysis,
    current_topic_id: str,
    allowed_prereq_ids: list[str],
    visited_topics: list[str],
    current_depth: int,
) -> tuple[Optional[str], Optional[BacktraceInfo], Optional[GapType]]:
    """Determine the next step during a diagnostic incorrect answer.
    
    Returns:
      (next_topic_id, backtrace_info, gap_recorded)
    """
    is_prereq_gap = analysis.gap_type == "prerequisite"
    suspected = analysis.suspected_prereq_id

    # Must be valid prerequisite belonging to current topic
    if is_prereq_gap and suspected and (suspected in allowed_prereq_ids):
        # Prevent cycles / repeated visits
        if suspected in visited_topics:
            # Already visited, stop backtrace and record root gap
            return None, None, analysis.gap_type

        # Check maximum backtrace depth (depth is 1-indexed for jumps)
        if current_depth >= MAX_BACKTRACE_DEPTH:
            # Reached max depth, mark as gap
            return None, None, analysis.gap_type

        # Valid backtrace jump
        backtrace_info = BacktraceInfo(
            from_topic_id=current_topic_id,
            to_topic_id=suspected,
            reason=analysis.reason or f"Prerequisite gap suspected in {suspected}",
        )
        return suspected, backtrace_info, None

    # Not a prerequisite jump or invalid target -> record gap on current topic
    return None, None, analysis.gap_type
