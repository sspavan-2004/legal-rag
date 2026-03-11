"""
Sample Legal Documents Database
These are simplified legal text snippets for RAG retrieval
"""

LEGAL_DOCUMENTS = [
    {
        "id": 1,
        "title": "Contract Law - Essential Elements",
        "content": """A valid contract requires four essential elements: offer, acceptance, consideration, and mutual intent to be bound. The offer must be clear, definite, and communicated to the offeree. Acceptance must be unequivocal and mirror the terms of the offer (mirror image rule). Consideration involves something of value exchanged between parties - it can be a promise, performance, or forbearance. Both parties must have the legal capacity to contract and the agreement must be for a lawful purpose. Without these elements, a contract may be void or voidable."""
    },
    {
        "id": 2,
        "title": "Copyright Law - Protection Duration",
        "content": """Copyright protection generally lasts for the life of the author plus 70 years. For works made for hire, anonymous works, and pseudonymous works, copyright lasts 95 years from publication or 120 years from creation, whichever is shorter. Copyright protects original works of authorship fixed in a tangible medium, including literary works, musical compositions, dramatic works, choreography, pictorial and graphic works, audiovisual works, sound recordings, and architectural works. Copyright does not protect ideas, facts, or methods of operation."""
    },
    {
        "id": 3,
        "title": "Tort Law - Negligence Standard",
        "content": """To establish negligence, a plaintiff must prove four elements: duty, breach, causation, and damages. The defendant must have owed a duty of care to the plaintiff, breached that duty by failing to meet the standard of reasonable care, and this breach must have been the actual and proximate cause of the plaintiff's damages. The reasonable person standard is objective - what would a reasonable person do under similar circumstances. Damages must be proven and can include economic losses, pain and suffering, and in some cases, punitive damages."""
    },
    {
        "id": 4,
        "title": "Criminal Law - Burden of Proof",
        "content": """In criminal proceedings, the prosecution bears the burden of proving the defendant's guilt beyond a reasonable doubt. This is the highest standard of proof in the legal system, reflecting the serious consequences of criminal conviction. The defendant is presumed innocent until proven guilty. The prosecution must prove every element of the charged offense. Unlike civil cases where preponderance of evidence (more likely than not) suffices, criminal convictions require this higher threshold to protect individual liberty and ensure fair trials."""
    },
    {
        "id": 5,
        "title": "Property Law - Adverse Possession",
        "content": """Adverse possession allows a person to gain legal ownership of property through continuous, open, notorious, exclusive, and hostile possession for a statutory period, typically 10-20 years depending on jurisdiction. The possession must be actual and exclusive, meaning the possessor treats the property as their own. It must be open and notorious, giving the true owner notice. The possession must be adverse or hostile, without the owner's permission. If all elements are satisfied for the required period, the adverse possessor can claim legal title through a quiet title action."""
    },
    {
        "id": 6,
        "title": "Constitutional Law - First Amendment",
        "content": """The First Amendment protects freedom of speech, religion, press, assembly, and petition. Speech protection extends to verbal, written, and symbolic expression. However, certain categories receive limited or no protection: obscenity, defamation, fraud, incitement to imminent lawless action, true threats, and fighting words. Government restrictions on speech are subject to different levels of scrutiny depending on whether they are content-based or content-neutral. Prior restraints on speech face a heavy presumption against constitutional validity."""
    },
    {
        "id": 7,
        "title": "Employment Law - At-Will Doctrine",
        "content": """The at-will employment doctrine allows either employer or employee to terminate the employment relationship at any time, for any reason, or no reason at all, with or without notice. However, significant exceptions exist: employment cannot be terminated for illegal reasons (discrimination based on race, gender, religion, age, disability), in violation of public policy (refusing to commit illegal acts, whistleblowing), or in breach of an implied or express employment contract. Many jurisdictions recognize implied covenants of good faith and fair dealing."""
    },
    {
        "id": 8,
        "title": "Evidence Law - Hearsay Rule",
        "content": """Hearsay is an out-of-court statement offered to prove the truth of the matter asserted and is generally inadmissible. The rule exists because such statements lack the safeguards of cross-examination and observation of witness demeanor. However, numerous exceptions exist, including statements against interest, dying declarations, excited utterances, present sense impressions, statements for medical diagnosis, recorded recollections, business records, and public records. Some jurisdictions have adopted broader residual exceptions for statements with circumstantial guarantees of trustworthiness."""
    },
    {
        "id": 9,
        "title": "Corporate Law - Fiduciary Duties",
        "content": """Corporate directors and officers owe fiduciary duties of care and loyalty to the corporation and its shareholders. The duty of care requires directors to act with the care that a reasonably prudent person would exercise in similar circumstances, making informed decisions. The duty of loyalty requires directors to act in good faith and in the corporation's best interests, avoiding conflicts of interest and self-dealing. The business judgment rule protects directors from liability for decisions made in good faith, with reasonable information, and in the honest belief that the action was in the corporation's best interest."""
    },
    {
        "id": 10,
        "title": "Family Law - Child Custody Standards",
        "content": """Courts determine child custody based on the best interests of the child standard. Factors considered include the child's age, health, and emotional ties with parents; each parent's ability to provide care, stability, and continuity in the child's education and community life; the mental and physical health of all parties; the child's preference if of sufficient age and capacity; and any history of domestic violence. Courts may award sole custody to one parent or joint custody. Most jurisdictions favor arrangements that maintain meaningful relationships with both parents absent evidence of harm to the child."""
    }
]

def get_all_documents():
    """Return all legal documents"""
    return LEGAL_DOCUMENTS

def get_document_by_id(doc_id):
    """Get a specific document by ID"""
    for doc in LEGAL_DOCUMENTS:
        if doc["id"] == doc_id:
            return doc
    return None

def get_documents_content():
    """Return just the content of all documents for embedding"""
    return [doc["content"] for doc in LEGAL_DOCUMENTS]

def get_documents_with_metadata():
    """Return documents with title and content for context"""
    return [(doc["title"], doc["content"]) for doc in LEGAL_DOCUMENTS]
