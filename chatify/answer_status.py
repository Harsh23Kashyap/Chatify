"""Display/export limitation, never a semantic verdict or answer-body rewrite."""
UNVERIFIED_NOTE = ('Not independently verified. Citations point to retrieved sources, but do not prove every claim. '
                   'Check the source passage for uncertainty, attribution and the outcome actually studied.')

def answer_note(turn):
    # No current path performs independent verification. Legacy missing status,
    # preview and caller-supplied true values cannot establish that it occurred.
    return UNVERIFIED_NOTE if turn.get('evidence') else ''
