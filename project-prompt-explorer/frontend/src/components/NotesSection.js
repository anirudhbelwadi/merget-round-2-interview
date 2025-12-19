import { useState, useEffect, useCallback } from "react";
import "./NotesSection.css";
import { fetchNotes, addNote } from "../services/api";

const NotesSection = ({ promptId, onNoteAdded }) => {
    const [notes, setNotes] = useState([]);
    const [newNote, setNewNote] = useState("");
    const [loading, setLoading] = useState(true);
    const [submitting, setSubmitting] = useState(false);

    // Using useCallback so this function reference stays stable
    // Prevents unnecessary re-renders when NotesSection parent re-renders
    const loadNotes = useCallback(async () => {
        try {
            setLoading(true);
            const data = await fetchNotes(promptId);
            setNotes(data);
        } catch (err) {
            // Silently fail - user can retry by switching tabs or refreshing
            // Could add a retry button here if needed
            console.error("Failed to load notes:", err);
        } finally {
            setLoading(false);
        }
    }, [promptId]);

    useEffect(() => {
        loadNotes();
    }, [loadNotes]);

    const handleSubmit = async (e) => {
        e.preventDefault();
        if (!newNote.trim()) return;

        try {
            setSubmitting(true);
            await addNote(promptId, { content: newNote });
            setNewNote("");
            // Reload to get the new note with server-generated ID and timestamp
            // Could optimistically add it, but this ensures we have the real data
            await loadNotes();
            if (onNoteAdded) {
                onNoteAdded();
            }
        } catch (err) {
            console.error("Failed to add note:", err);
            // Using alert for now - could replace with a toast notification later
            alert("Failed to add note. Please try again.");
        } finally {
            setSubmitting(false);
        }
    };

    const formatDate = (dateString) => {
        // Formatting dates client-side - could use a library like date-fns
        // but this is simple enough and keeps dependencies low
        const date = new Date(dateString);
        return date.toLocaleString("en-US", {
            year: "numeric",
            month: "short",
            day: "numeric",
            hour: "2-digit",
            minute: "2-digit",
        });
    };

    if (loading) {
        return <div className="notes-loading">Loading notes...</div>;
    }

    return (
        <div className="notes-section">
            <form onSubmit={handleSubmit} className="notes-form">
                <textarea
                    value={newNote}
                    onChange={(e) => setNewNote(e.target.value)}
                    placeholder="Add a note..."
                    className="notes-input"
                    rows="4"
                />
                <button
                    type="submit"
                    disabled={!newNote.trim() || submitting}
                    className="notes-submit-button"
                >
                    {submitting ? "Adding..." : "Add Note"}
                </button>
            </form>
            <div className="notes-list">
                {notes.length === 0 ? (
                    <div className="notes-empty">No notes yet. Add one above!</div>
                ) : (
                    notes.map((note) => (
                        <div key={note.noteId || note.id} className="note-item">
                            <div className="note-content">{note.content}</div>
                            <div className="note-date">{formatDate(note.createdAt || note.created_at)}</div>
                        </div>
                    ))
                )}
            </div>
        </div>
    );
};

export default NotesSection;
