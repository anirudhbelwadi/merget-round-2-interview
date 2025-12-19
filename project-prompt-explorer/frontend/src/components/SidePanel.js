import { useState } from "react";
import "./SidePanel.css";
import NotesSection from "./NotesSection";

const SidePanel = ({ prompt, onClose, onNoteAdded }) => {
    const [activeTab, setActiveTab] = useState("details");

    return (
        <div className="side-panel">
            <div className="side-panel-header">
                <h2>{prompt.title}</h2>
                <button className="close-button" onClick={onClose} aria-label="Close">
                    ×
                </button>
            </div>
            <div className="side-panel-tabs">
                <button
                    className={`tab-button ${activeTab === "details" ? "active" : ""}`}
                    onClick={() => setActiveTab("details")}
                >
                    Details
                </button>
                <button
                    className={`tab-button ${activeTab === "notes" ? "active" : ""}`}
                    onClick={() => setActiveTab("notes")}
                >
                    Notes
                </button>
            </div>
            <div className="side-panel-content">
                {activeTab === "details" && (
                    <div className="details-tab">
                        {prompt.description && (
                            <div className="detail-section">
                                <h3>Description</h3>
                                <p>{prompt.description}</p>
                            </div>
                        )}
                        {prompt.nodes && prompt.nodes.length > 0 && (
                            <div className="detail-section">
                                <h3>Nodes ({prompt.nodes.length})</h3>
                                <div className="nodes-list">
                                    {prompt.nodes.map((node) => (
                                        <div key={node.nodeId || node.id} className="node-item">
                                            <div className="node-name">{node.name}</div>
                                            {node.action && (
                                                <div className="node-action">{node.action}</div>
                                            )}
                                        </div>
                                    ))}
                                </div>
                            </div>
                        )}
                        {(!prompt.nodes || prompt.nodes.length === 0) && (
                            <div className="empty-state">No nodes for this prompt</div>
                        )}
                    </div>
                )}
                {activeTab === "notes" && (
                    <NotesSection promptId={prompt.id} onNoteAdded={onNoteAdded} />
                )}
            </div>
        </div>
    );
};

export default SidePanel;
