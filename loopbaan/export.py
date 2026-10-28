from django.forms.models import model_to_dict


def user_data(user):
    """Everything Ambitus stores about one person, for the data export."""
    profile = getattr(user, "profile", None)
    return {
        "account": {
            "email": user.email,
            "first_name": user.first_name,
            "language": user.language,
            "date_joined": user.date_joined,
        },
        "profile": model_to_dict(profile, exclude=["id", "user"]) if profile else None,
        "orientations": [
            {"created_at": o.created_at, "answers": o.answers, "summary": o.summary, "directions": o.directions}
            for o in user.orientations.all()
        ],
        "applications": [
            {
                **model_to_dict(a, exclude=["id", "user"]),
                "created_at": a.created_at,
                "history": [{"status": h.status, "changed_at": h.changed_at} for h in a.history.all()],
                "documents": [
                    {"kind": d.kind, "language": d.language, "content": d.content, "created_at": d.created_at}
                    for d in a.documents.all()
                ],
                "interview_preps": [
                    {
                        "created_at": p.created_at,
                        "briefing": p.briefing,
                        "questions": p.questions,
                        "questions_to_ask": p.questions_to_ask,
                        "practice": [
                            {"question_index": r.question_index, "answer": r.answer, "feedback": r.feedback}
                            for r in p.answers.all()
                        ],
                    }
                    for p in a.interview_preps.all()
                ],
            }
            for a in user.applications.all()
        ],
    }
