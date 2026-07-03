"""Run this to inspect all stored data: python3 check_db.py"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from dotenv import load_dotenv
load_dotenv()

from app import create_app
from models import db, User, Document, Query

app = create_app()

with app.app_context():
    users = User.query.all()
    print(f"\n{'='*60}")
    print(f"  USERS ({len(users)} total)")
    print(f"{'='*60}")
    for u in users:
        docs = Document.query.filter_by(user_id=u.id).all()
        queries = Query.query.filter_by(user_id=u.id).all()
        print(f"  id={u.id}  username='{u.username}'  "
              f"docs={len(docs)}  queries={len(queries)}  "
              f"joined={u.created_at.strftime('%Y-%m-%d %H:%M')}")

    print(f"\n{'='*60}")
    print(f"  DOCUMENTS ({Document.query.count()} total)")
    print(f"{'='*60}")
    for d in Document.query.order_by(Document.uploaded_at.desc()).all():
        print(f"  id={d.id}  user_id={d.user_id}  filename='{d.filename}'  "
              f"chunks={d.chunks}  uploaded={d.uploaded_at.strftime('%Y-%m-%d %H:%M')}")

    print(f"\n{'='*60}")
    print(f"  QUERIES ({Query.query.count()} total)")
    print(f"{'='*60}")
    for q in Query.query.order_by(Query.asked_at.desc()).all():
        print(f"\n  id={q.id}  user_id={q.user_id}  doc_id={q.document_id}"
              f"  asked={q.asked_at.strftime('%Y-%m-%d %H:%M')}")
        print(f"  Q: {q.question}")
        print(f"  A: {(q.answer or '')[:120]}{'...' if q.answer and len(q.answer) > 120 else ''}")
        print(f"  sources={q.sources}  pages={q.pages}")

    print(f"\n{'='*60}\n")
