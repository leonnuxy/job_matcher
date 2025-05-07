"""
Shared utilities and constants for job parsing.

This module contains shared resources used across the job parser modules:
- Common stop words for filtering job description text
- Shared utility functions for text cleaning and normalization
"""
import string
import logging
import re

# Configure logging (optional, but highly recommended)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Define common non-skill words found in job descriptions
# NOTE: This list is extensive and may need refinement based on testing
# Added more common filler words based on test results
JOB_DESCRIPTION_STOP_WORDS = set([
    'ability', 'able', 'about', 'above', 'across', 'act', 'action', 'addition', 'additional', 'administration',
    'advantage', 'agency', 'all', 'allow', 'also', 'an', 'analysis', 'analyst', 'and', 'annual', 'any', 'application',
    'apply', 'approach', 'appropriate', 'are', 'area', 'around', 'as', 'ask', 'aspect', 'assessment', 'asset',
    'assist', 'assistance', 'at', 'attitude', 'audience', 'authorization', 'background', 'base', 'based', 'be',
    'become', 'been', 'before', 'being', 'below', 'benefit', 'best', 'between', 'bonus', 'bring', 'build', 'business',
    'but', 'by', 'calgary', 'canada', 'candidate', 'candidates', 'capability', 'career', 'cause', 'center', 'certification',
    'challenge', 'chance', 'change', 'client', 'cloud', 'code', 'collaborate', 'collaboration', 'collection',
    'combination', 'come', 'commit', 'commitment', 'communicate', 'communication', 'communications', 'community', 'company',
    'compensation', 'compete', 'competitive', 'complete', 'compliance', 'computer', 'concept', 'conduct', 'connect', 'consider', 'consideration',
    'consist', 'consult', 'consulting', 'contact', 'content', 'contract', 'contribute', 'contribution', 'control',
    'coordinate', 'core', 'cost', 'country', 'cover', 'create', 'creation', 'credit', 'cross', 'culture', 'currency',
    'current', 'customer', 'data', 'database', 'date', 'datum', 'day', 'deal', 'decision', 'degree', 'deliver',
    'delivery', 'department', 'depend', 'describe', 'description', 'design', 'desire', 'detail', 'develop', 'developer',
    'development', 'difference', 'digital', 'direction', 'disability', 'discipline', 'discuss', 'diversity', 'do',
    'document', 'documentation', 'domain', 'drive', 'duty', 'duties', 'dynamic', 'edge', 'education', 'effect', 'effective',
    'effectively', 'efficiency', 'effort', 'e.g.', 'either', 'eligibility', 'email', 'embrace', 'employee', 'employer',
    'employment', 'empower', 'enable', 'encourage', 'end', 'energy', 'engage', 'engagement', 'engineer', 'engineering',
    'enhance', 'enhancement', 'ensure', 'enterprise', 'environment', 'equal', 'equipment', 'equivalent', 'etc',
    'evaluate', 'evaluation', 'event', 'every', 'example', 'excellence', 'excellent', 'execute', 'execution', 'expect',
    'expectation', 'experience', 'expert', 'expertise', 'explain', 'explore', 'exposure', 'external', 'facilitate',
    'factor', 'familiarity', 'family', 'fast', 'feature', 'feel', 'field', 'file', 'fill', 'final', 'finance', 'find',
    'firm', 'first', 'fit', 'flexibility', 'flexible', 'focus', 'follow', 'following', 'for', 'form', 'format',
    'foster', 'foundation', 'framework', 'from', 'full', 'function', 'functional', 'future', 'gain', 'gender', 'get',
    'give', 'global', 'go', 'goal', 'good', 'govern', 'governance', 'group', 'grow', 'growth', 'guidance', 'guide',
    'handle', 'hand', 'have', 'head', 'health', 'help', 'high', 'highly', 'hire', 'hiring', 'history', 'hold', 'home',
    'hour', 'how', 'hr', 'html', 'i.e.', 'idea', 'identify', 'identity', 'if', 'impact', 'implement', 'implementation',
    'important', 'improve', 'improvement', 'in', 'incentive', 'include', 'including', 'inclusion', 'individual',
    'industry', 'influence', 'inform', 'information', 'infrastructure', 'initiative', 'innovate', 'innovation',
    'insight', 'install', 'installation', 'institution', 'instruct', 'insurance', 'integrate', 'integration',
    'integrity', 'intelligence', 'interact', 'interaction', 'interest', 'internal', 'international', 'interpersonal',
    'interpret', 'interview', 'into', 'introduce', 'investigate', 'involve', 'is', 'issue', 'it', 'item', 'its', 'job',
    'join', 'journey', 'judgment', 'keep', 'key', 'kind', 'know', 'knowledge', 'language', 'large', 'last', 'law',
    'lead', 'leader', 'leadership', 'learn', 'learning', 'leave', 'legal', 'less', 'letter', 'level', 'leverage',
    'liaise', 'life', 'like', 'limited', 'link', 'list', 'listen', 'live', 'locate', 'location', 'log', 'look', 'ltd',
    'maintain', 'maintenance', 'make', 'manage', 'management', 'manager', 'manner', 'manual', 'market', 'master',
    'match', 'material', 'matter', 'may', 'mean', 'measure', 'mechanism', 'media', 'medium', 'meet', 'meeting',
    'member', 'membership', 'mentor', 'message', 'method', 'methodology', 'microsoft', 'migrate', 'migration',
    'minimum', 'mission', 'model', 'modeling', 'monitor', 'month', 'more', 'motivate', 'motivation', 'move', 'multi',
    'multiple', 'must', 'need', 'negotiate', 'network', 'new', 'next', 'no', 'non', 'north', 'note', 'number',
    'objective', 'observe', 'obtain', 'of', 'offer', 'office', 'often', 'on', 'ongoing', 'only', 'open', 'operate',
    'operation', 'operational', 'opportunity', 'opportunities', 'optimize', 'optimization', 'option', 'or', 'oral', 'order',
    'organization', 'organizational', 'orient', 'orientation', 'origin', 'other', 'our', 'outcome', 'outline',
    'outlook', 'over', 'overall', 'oversee', 'overview', 'own', 'owner', 'ownership', 'pace', 'package', 'page',
    'part', 'participate', 'partner', 'partnership', 'party', 'pass', 'passion', 'passionate', 'pay', 'people', 'perform',
    'performance', 'period', 'permission', 'person', 'personal', 'personnel', 'perspective', 'phase', 'phone',
    'physical', 'plan', 'platform', 'play', 'please', 'plus', 'point', 'policy', 'position', 'positive', 'possess',
    'post', 'potential', 'power', 'practice', 'practices', 'prepare', 'preparation', 'presence', 'present', 'presentation',
    'previous', 'primary', 'principle', 'prior', 'priority', 'privacy', 'proactive', 'problem', 'procedure',
    'process', 'processing', 'produce', 'product', 'professional', 'proficiency', 'proficient', 'program', 'progress',
    'project', 'promote', 'prompt', 'proof', 'propose', 'protect', 'provide', 'proven', 'purpose', 'pursuant', 'qualification', 'qualifications',
    'quality', 'question', 'range', 'rate', 'reach', 'read', 'real', 'receive', 'recognize', 'recommend',
    'recommendation', 'record', 'recruit', 'recruitment', 'reduce', 'refine', 'regard', 'region', 'register',
    'regulation', 'regulatory', 'relate', 'related', 'relationship', 'release', 'relevance', 'relevant', 'reliability',
    'religion', 'remote', 'report', 'reporting', 'represent', 'request', 'require', 'required', 'requirement', 'requirements',
    'research', 'reserve', 'residence', 'resolution', 'resolve', 'resource', 'respect', 'respond', 'response',
    'responsibility', 'responsibilities', 'responsible', 'rest', 'result', 'resume', 'retain', 'review', 'reward', 'right', 'risk', 'role',
    'routine', 'rule', 'run', 'safe', 'safety', 'salary', 'sale', 'satisfaction', 'save', 'scale', 'schedule',
    'science', 'scope', 'screen', 'script', 'search', 'sector', 'secure', 'security', 'see', 'seek', 'select',
    'selection', 'self', 'senior', 'sense', 'sensitive', 'serve', 'service', 'set', 'setting', 'shape', 'share',
    'shift', 'ship', 'show', 'similar', 'simple', 'site', 'skill', 'skills', 'skillset', 'so', 'social', 'software', 'solution', 'solutions',
    'solve', 'solving', 'some', 'someone', 'source', 'space', 'speak', 'special', 'specific', 'specification', 'sponsor',
    'sponsorship', 'stability', 'staff', 'stage', 'stakeholder', 'standard', 'start', 'state', 'statement', 'status',
    'stay', 'step', 'stock', 'store', 'strategic', 'strategy', 'streamline', 'strength', 'stress', 'strong',
    'structure', 'student', 'study', 'style', 'subject', 'submit', 'success', 'successful', 'such', 'suggest', 'suite',
    'summary', 'supervise', 'support', 'system', 'table', 'tackle', 'take', 'talent', 'target', 'task', 'team',
    'teammate', 'teamwork', 'tech', 'technical', 'technique', 'technology', 'term', 'test', 'testing', 'than', 'that',
    'the', 'their', 'them', 'then', 'there', 'these', 'they', 'thing', 'think', 'this', 'thorough', 'those', 'thought',
    'threat', 'through', 'throughout', 'ticket', 'time', 'timeline', 'timely', 'title', 'to', 'today', 'together',
    'tool', 'tooling', 'top', 'total', 'track', 'trade', 'train', 'training', 'transfer', 'transform', 'transformation',
    'transition', 'travel', 'treatment', 'trend', 'troubleshoot', 'troubleshooting', 'trust', 'try', 'turn', 'type',
    'typical', 'under', 'understand', 'understanding', 'undertake', 'unit', 'university', 'unless', 'until', 'up',
    'update', 'upgrade', 'upon', 'us', 'usa', 'usability', 'usage', 'use', 'user', 'utilize', 'vacation', 'validate',
    'validation', 'value', 'various', 'verbal', 'verify', 'version', 'via', 'view', 'visa', 'vision', 'visit', 'visual',
    'volume', 'want', 'way', 'we', 'web', 'website', 'week', 'welcome', 'well', 'what', 'when', 'where', 'whether',
    'which', 'while', 'who', 'whole', 'why', 'wide', 'will', 'willing', 'willingness', 'with', 'within', 'without',
    'work', 'workday', 'workflow', 'working', 'workplace', 'world', 'would', 'write', 'written', 'year', 'years', 'yet', 'you',
    'your', 'zone',
    # Added common single letters/symbols often left after basic cleaning
    'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z',
    '-', '+', '=', '_', '*', '&', '^', '%', '$', '#', '@', '!', '?', '.', ',', ';', ':', '(', ')', '[', ']', '{', '}', '<', '>', '/', '\\', '|', '~', '`',
    # Added numbers as strings
    '0', '1', '2', '3', '4', '5', '6', '7', '8', '9',
    # Added based on potential noise
    'bachelor', 'master', 'phd', 'associate', 'preferred', 'nice', 'have', 'minimum', 'maximum', 'equivalent',
    'problem-solving', 'analytical', 'verbal', 'written', 'interpersonal', 'organizational', 'management',
    'oriented', 'driven', 'focused', 'based', 'related', 'field', 'etc', 'eg', 'ie', 'various', 'including',
    'such', 'other', 'new', 'current', 'ongoing', 'full-time', 'part-time', 'contract', 'permanent', 'temporary',
    'remote', 'hybrid', 'office', 'on-site', 'benefits', 'paid', 'time', 'off', 'pto', 'health', 'dental', 'vision',
    'insurance', 'plan', 'bonus', 'equity', 'stock', 'options', 'salary', 'compensation', 'range', 'per', 'annum',
    'hourly', 'rate', 'competitive', 'commensurate', 'experience', 'level', 'entry', 'mid', 'lead', 'principal',
    'staff', 'architect', 'director', 'vp', 'executive', 'citizenship', 'authorization', 'work', 'status', 'equal',
    'opportunity', 'employer', 'affirmative', 'action', 'diversity', 'inclusion', 'background', 'check', 'drug', 'screen',
    'travel', 'required', 'willingness', 'ability', 'relocate', 'company', 'culture', 'values', 'mission', 'vision',
    'apply', 'submit', 'resume', 'cover', 'letter', 'portfolio', 'website', 'link', 'contact', 'information', 'email',
    'phone', 'address', 'location', 'city', 'state', 'province', 'country', 'zip', 'postal', 'code'
])

# Define punctuation to remove, keeping '#' and '+' for C#/C++
PUNCTUATION_TO_REMOVE = string.punctuation.replace('#', '').replace('+', '')
TRANSLATOR = str.maketrans('', '', PUNCTUATION_TO_REMOVE)

# Shared utility functions
def clean_text(text):
    """
    Performs basic cleaning operations on text:
    - Converts to lowercase
    - Removes URLs
    - Normalizes whitespace
    - Removes common prefixes like 'e.g.', 'i.e.'
    
    Args:
        text (str): Raw text to clean
        
    Returns:
        str: Cleaned text
    """
    if not text:
        return ""
        
    # Convert to lowercase
    text_lower = text.lower()
    
    # Remove URLs
    text_lower = re.sub(r'https?://\S+|www\.\S+', '', text_lower)
    
    # Normalize whitespace
    text_lower = re.sub(r'\s+', ' ', text_lower).strip()
    
    # Remove common prefixes
    text_lower = re.sub(r'\b(e\.g\.|i\.e\.)\s*', '', text_lower)
    
    return text_lower
