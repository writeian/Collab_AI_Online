"""Document storage management - Railway PostgreSQL version with room scoping"""

from flask import request, jsonify, current_app, session, make_response
from functools import wraps
import os

from . import library
from src.utils.documents.indexer import delete_document_and_chunks, delete_document_by_id, delete_all_documents, get_all_documents
from src.utils.documents.database import get_room_storage_usage, get_document_by_file_id, get_document_by_id
from src.app.access_control import get_current_user
from src.app import db
from src.models.room import Room

from .access_control import can_access_room_for_library as can_access_room


def login_required(f):
    """Session-based login required decorator."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'error': 'Authentication required'}), 401
        return f(*args, **kwargs)
    return decorated_function


@library.route('/key-documents/delete', methods=['POST'])
@login_required
def delete_key_document():
    """
    Delete a key document by its database id (primary key).
    Simpler path - no file_id lookup. Room instructor only.
    """
    try:
        data = request.get_json() or {}
        doc_id = data.get('doc_id')
        file_id = data.get('file_id')
        room_id = data.get('room_id')
        current_app.logger.info(
            f"Key doc delete request payload: doc_id={doc_id!r} file_id={file_id!r} room_id={room_id!r}"
        )
        if room_id is not None:
            try:
                room_id = int(room_id)
            except (ValueError, TypeError):
                room_id = None
        if not room_id:
            return jsonify({'error': 'room_id is required'}), 400

        normalized_doc_id = None
        if doc_id is not None and str(doc_id).strip() != '':
            try:
                normalized_doc_id = int(doc_id)
            except (ValueError, TypeError):
                return jsonify({'error': 'Invalid doc_id'}), 400

        normalized_file_id = str(file_id).strip() if file_id is not None else None
        if not normalized_doc_id and not normalized_file_id:
            return jsonify({'error': 'doc_id or file_id is required'}), 400

        user = get_current_user()
        if not user:
            return jsonify({'error': 'Authentication required'}), 401
        if not can_access_room(user.id, room_id):
            return jsonify({'error': 'You do not have access to this room.'}), 403

        room = Room.query.get(room_id)
        is_owner = room and user.id == room.owner_id
        doc = None
        if normalized_doc_id:
            doc = get_document_by_id(normalized_doc_id, room_id)
        if not doc and normalized_file_id:
            doc = get_document_by_file_id(normalized_file_id, room_id)
        if not doc:
            current_app.logger.warning(
                f"Key doc delete: document not found doc_id={normalized_doc_id} file_id={normalized_file_id!r} room_id={room_id}"
            )
            return jsonify({'error': 'Document not found', 'deleted_count': 0}), 200
        if getattr(doc, 'key_document_type', None) and not is_owner:
            return jsonify({'error': 'Only the room instructor can delete key documents.'}), 403

        # Snapshot values before deletion; ORM instance may become invalid after commit.
        target_doc_id = int(doc.id)
        target_file_id = str(doc.file_id) if doc.file_id is not None else None

        # Use direct SQL deletion for maximum reliability across SQLite/PostgreSQL.
        try:
            db.session.execute(
                db.text("DELETE FROM document_chunk WHERE document_id = :doc_id"),
                {"doc_id": target_doc_id}
            )
            deleted_doc = db.session.execute(
                db.text("DELETE FROM document WHERE id = :doc_id AND room_id = :room_id"),
                {"doc_id": target_doc_id, "room_id": room_id}
            )
            db.session.commit()
            deleted_count = int(deleted_doc.rowcount or 0)
            if deleted_count > 0:
                current_app.logger.info(f"Key doc deleted via SQL: id={target_doc_id} file_id={target_file_id}")
                return jsonify({'success': True, 'deleted_count': 1}), 200
            current_app.logger.warning(f"Key doc SQL delete rowcount=0 for id={target_doc_id} room_id={room_id}")
            return jsonify({'error': 'Delete failed', 'deleted_count': 0}), 200
        except Exception as sql_err:
            db.session.rollback()
            current_app.logger.error(f"Key doc SQL delete error for id={target_doc_id}: {sql_err}", exc_info=True)
            # Fallback to existing helper path to maximize chance of deletion.
            if delete_document_by_id(target_doc_id):
                current_app.logger.info(f"Key doc deleted via fallback helper: id={target_doc_id} file_id={target_file_id}")
                return jsonify({'success': True, 'deleted_count': 1}), 200
            return jsonify({'error': f'Delete failed: {sql_err}', 'deleted_count': 0}), 200
    except Exception as e:
        current_app.logger.error(f"Key document delete error: {e}", exc_info=True)
        return jsonify({'error': str(e), 'deleted_count': 0}), 500


@library.route('/clear', methods=['POST'])
@login_required
def clear_storage():
    """
    Delete documents from storage, scoped to room.
    
    Request body:
        {
            "ids": ["file-id-1", "file-id-2"],  // optional, deletes all in room if omitted
            "room_id": 123  // Required
        }
    """
    try:
        data = request.get_json() or {}
        ids = data.get('ids') or []
        doc_ids = data.get('doc_ids') or []
        room_id = data.get('room_id')
        if room_id is not None:
            try:
                room_id = int(room_id)
            except (ValueError, TypeError):
                room_id = None
        
        if not room_id:
            return jsonify({'error': 'room_id is required'}), 400
        
        # Get current user from session
        user = get_current_user()
        if not user:
            return jsonify({'error': 'Authentication required'}), 401
        
        # Verify user has access to room
        if not can_access_room(user.id, room_id):
            current_app.logger.warning(
                f"User {user.id} attempted to delete documents in room {room_id} without access"
            )
            return jsonify({
                'error': 'You do not have access to this room.'
            }), 403
        
        room = Room.query.get(room_id)
        is_owner = room and user.id == room.owner_id

        deleted_count = 0

        if ids or doc_ids:
            # Delete specific documents (scoped to room)
            # Key documents require owner (instructor) to delete
            current_app.logger.info(f"Deleting from room {room_id}, ids={ids}, doc_ids={doc_ids}")
            # Try by file_id first
            for fid in ids:
                file_id = str(fid).strip() if fid is not None else None
                if not file_id:
                    continue
                doc = get_document_by_file_id(file_id, room_id)
                if not doc:
                    current_app.logger.warning(f"Document not found: file_id={repr(file_id)} room_id={room_id}")
                    continue
                if getattr(doc, 'key_document_type', None) and not is_owner:
                    return jsonify({
                        'error': 'Only the room instructor can delete key documents.'
                    }), 403
                if delete_document_and_chunks(file_id, room_id=room_id):
                    deleted_count += 1
            # Fallback: try by document id when file_id lookup failed
            for did in doc_ids:
                doc = get_document_by_id(did, room_id)
                if not doc:
                    current_app.logger.warning(f"Document not found: doc_id={did} room_id={room_id}")
                    continue
                if getattr(doc, 'key_document_type', None) and not is_owner:
                    return jsonify({
                        'error': 'Only the room instructor can delete key documents.'
                    }), 403
                if delete_document_and_chunks(doc.file_id, room_id=room_id):
                    deleted_count += 1
        else:
            # Delete all documents in room - only owner can do this (includes key docs)
            if not is_owner:
                return jsonify({
                    'error': 'Only the room instructor can delete all documents.'
                }), 403
            current_app.logger.info(f"Deleting all documents from room {room_id}")
            if delete_all_documents(room_id=room_id):
                deleted_count = -1  # Indicate "all deleted"
        
        current_app.logger.info(f"Deleted {deleted_count} documents from room {room_id}")
        
        return jsonify({
            'success': True,
            'deleted_count': deleted_count
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Clear storage error: {e}")
        return jsonify({'error': f'Failed to clear storage: {str(e)}'}), 500


@library.route('/documents', methods=['GET'])
@login_required
def list_documents():
    """
    Get list of all uploaded documents in a room.
    
    Query parameters:
        room_id: Required - Room ID to list documents for
    
    Returns:
        {
            "documents": [
                {
                    "id": "uuid",
                    "file_id": "uuid",
                    "name": "document.pdf",
                    "uploaded_at": "2025-11-03T...",
                    "chunk_count": 5,
                    "summary": "..."
                }
            ]
        }
    """
    try:
        room_id = request.args.get('room_id', type=int)
        
        if not room_id:
            return jsonify({'error': 'room_id query parameter is required'}), 400
        
        # Get current user from session
        user = get_current_user()
        if not user:
            return jsonify({'error': 'Authentication required'}), 401
        
        # Verify user has access to room
        if not can_access_room(user.id, room_id):
            current_app.logger.warning(
                f"User {user.id} attempted to list documents in room {room_id} without access"
            )
            return jsonify({
                'error': 'You do not have access to this room.'
            }), 403
        
        try:
            documents = get_all_documents(room_id=room_id)
            
            current_app.logger.info(f"Retrieved {len(documents)} documents for room {room_id}")
            
            resp = make_response(jsonify({'documents': documents}), 200)
            resp.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate'
            return resp
        except Exception as e:
            current_app.logger.error(f"List documents error: {e}")
            # Return empty list if tables don't exist
            return jsonify({
                'documents': [],
                'error': 'Database tables not initialized. Run migration to enable Library Tool.'
            }), 200
        
    except Exception as e:
        current_app.logger.error(f"List documents error: {e}")
        return jsonify({'error': f'Failed to list documents: {str(e)}'}), 500


@library.route('/storage/stats', methods=['GET'])
@login_required
def get_storage_stats():
    """
    Get storage usage statistics for a room.
    
    Query parameters:
        room_id: Required - Room ID to get stats for
    
    Returns:
        {
            "used_bytes": 1234567,
            "limit_bytes": 10485760,
            "used_mb": 1.18,
            "limit_mb": 10.0,
            "percentage": 11.77,
            "documents_count": 5
        }
    """
    try:
        room_id = request.args.get('room_id', type=int)
        
        if not room_id:
            return jsonify({'error': 'room_id query parameter is required'}), 400
        
        # Get current user from session
        user = get_current_user()
        if not user:
            return jsonify({'error': 'Authentication required'}), 401
        
        # Verify user has access to room
        if not can_access_room(user.id, room_id):
            current_app.logger.warning(
                f"User {user.id} attempted to get storage stats for room {room_id} without access"
            )
            return jsonify({
                'error': 'You do not have access to this room.'
            }), 403
        
        storage_stats = get_room_storage_usage(room_id)
        
        stats = {
            'used_bytes': storage_stats['total_bytes'],
            'limit_bytes': storage_stats['limit_bytes'],
            'used_mb': round(storage_stats['total_bytes'] / (1024 * 1024), 2),
            'limit_mb': round(storage_stats['limit_bytes'] / (1024 * 1024), 2),
            'percentage': storage_stats['percent_used'],
            'documents_count': storage_stats['file_count']
        }
        
        current_app.logger.info(
            f"Storage stats for room {room_id}: {stats['used_mb']}MB / {stats['limit_mb']}MB ({stats['percentage']}%)"
        )
        
        return jsonify(stats), 200
        
    except Exception as e:
        current_app.logger.error(f"Get storage stats error: {e}")
        # Return empty stats if tables don't exist (graceful degradation)
        error_msg = str(e)
        if 'no such table' in error_msg.lower() or ('relation' in error_msg.lower() and 'does not exist' in error_msg.lower()):
            return jsonify({
                'used_bytes': 0,
                'limit_bytes': 10 * 1024 * 1024,
                'used_mb': 0,
                'limit_mb': 10.0,
                'percentage': 0,
                'documents_count': 0
            }), 200
        return jsonify({'error': f'Failed to get storage stats: {str(e)}'}), 500
