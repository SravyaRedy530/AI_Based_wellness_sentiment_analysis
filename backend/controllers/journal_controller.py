from flask import Blueprint, request, Response
from flask_jwt_extended import jwt_required, get_jwt_identity
from backend.services.journal_service import JournalService
from backend.utils.helpers import success_response, error_response

journal_bp = Blueprint("journal", __name__, url_prefix="/api/journal")


@journal_bp.route("", methods=["GET"])
@jwt_required()
def list_entries():
    """Lists and filters journal entries for the authenticated user."""
    user_id = int(get_jwt_identity())
    search = request.args.get("search", "")
    emotion = request.args.get("emotion", "")
    sentiment = request.args.get("sentiment", "")
    start_date = request.args.get("start_date", None)
    end_date = request.args.get("end_date", None)
    sort_by = request.args.get("sort_by", "date_desc")

    entries = JournalService.get_entries(
        user_id=user_id,
        search_query=search,
        emotion_filter=emotion,
        sentiment_filter=sentiment,
        start_date=start_date,
        end_date=end_date,
        sort_by=sort_by
    )

    return success_response(data={"entries": entries, "count": len(entries)})


@journal_bp.route("", methods=["POST"])
@jwt_required()
def create_entry():
    """Creates a new journal entry and runs the AI emotion analysis pipeline."""
    user_id = int(get_jwt_identity())
    data = request.get_json() or {}

    title = data.get("title", "").strip()
    content = data.get("content", "").strip()
    tags = data.get("tags", "")
    entry_date = data.get("entry_date", None)

    if not title:
        return error_response("Journal entry title is required.", 400)
    if not content:
        return error_response("Journal entry content cannot be empty.", 400)

    try:
        new_entry = JournalService.create_entry(
            user_id=user_id,
            title=title,
            content=content,
            tags=tags,
            entry_date=entry_date
        )
        return success_response(
            data={"entry": new_entry},
            message="Journal entry saved and analyzed successfully!",
            status_code=201
        )
    except Exception as e:
        return error_response(f"Failed to create entry: {str(e)}", 500)


@journal_bp.route("/<int:entry_id>", methods=["GET"])
@jwt_required()
def get_entry(entry_id: int):
    """Retrieves a single journal entry by ID."""
    user_id = int(get_jwt_identity())
    entry = JournalService.get_entry_by_id(entry_id, user_id)
    if not entry:
        return error_response("Journal entry not found.", 404)
    return success_response(data={"entry": entry})


@journal_bp.route("/<int:entry_id>", methods=["PUT"])
@jwt_required()
def update_entry(entry_id: int):
    """Updates an existing journal entry and refreshes analysis."""
    user_id = int(get_jwt_identity())
    data = request.get_json() or {}

    title = data.get("title")
    content = data.get("content")
    tags = data.get("tags")
    entry_date = data.get("entry_date")
    reanalyze = data.get("reanalyze", True)

    try:
        updated = JournalService.update_entry(
            entry_id=entry_id,
            user_id=user_id,
            title=title,
            content=content,
            tags=tags,
            entry_date=entry_date,
            reanalyze=reanalyze
        )
        if not updated:
            return error_response("Journal entry not found or unauthorized.", 404)
        return success_response(data={"entry": updated}, message="Journal entry updated successfully!")
    except Exception as e:
        return error_response(f"Update failed: {str(e)}", 500)


@journal_bp.route("/<int:entry_id>", methods=["DELETE"])
@jwt_required()
def delete_entry(entry_id: int):
    """Deletes a journal entry."""
    user_id = int(get_jwt_identity())
    deleted = JournalService.delete_entry(entry_id, user_id)
    if not deleted:
        return error_response("Journal entry not found or unauthorized.", 404)
    return success_response(message="Journal entry deleted successfully.")


@journal_bp.route("/export/csv", methods=["GET"])
@jwt_required()
def export_csv():
    """Streams CSV file of user journal history with AI analysis."""
    user_id = int(get_jwt_identity())
    format_type = request.args.get("format", request.args.get("columns", "journal"))
    csv_content = JournalService.export_csv_data(user_id, format_type=format_type)

    return Response(
        csv_content,
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment;filename=moodmentor_journal_export.csv"}
    )
