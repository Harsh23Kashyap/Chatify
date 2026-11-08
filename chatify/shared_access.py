"""Fail-closed access boundary for shared built-in gallery apps.

Not an authentication system. Imported, visitor-owned children and standalone apps
keep their existing authorization. Unknown shared-app API routes are denied.
"""
PUBLIC_READS = frozenset(('/api/config','/api/theme','/api/health','/api/guide-seen','/api/actions'))
VISITOR_READS = frozenset(('/api/scopes','/api/chats','/api/turns','/api/export-all','/api/profile','/api/similar','/api/ratings','/api/stats','/api/export','/api/uploads','/api/topics','/api/topic-turns','/api/bibtex','/api/answer-markdown','/api/pdf'))
VISITOR_POSTS = frozenset(('/api/chats','/api/profile','/api/rate','/api/import','/api/ask','/api/ask-stream','/api/regenerate','/api/branch','/api/rename','/api/pin','/api/delete','/api/restore','/api/delete-turn','/api/restore-turn','/api/uploads','/api/upload-file','/api/upload-pdf','/api/load-url','/api/delete-upload','/api/rename-topic','/api/suggestions','/api/actions/prepare','/api/actions/execute'))

def allowed(path, method):
    return (method == 'GET' and path in PUBLIC_READS | VISITOR_READS) or (method == 'POST' and path in VISITOR_POSTS)

def needs_visitor(path):
    return path not in PUBLIC_READS
