import { useState } from "react";
import "./TreeView.css";

const TreeNode = ({ prompt, level = 0, onNodeClick, selectedId }) => {
    const [isExpanded, setIsExpanded] = useState(true);
    const hasNodes = prompt.nodes && prompt.nodes.length > 0;

    const handleToggle = (e) => {
        e.stopPropagation();
        setIsExpanded(!isExpanded);
    };

    const handleClick = () => {
        onNodeClick(prompt.id);
    };

    const isSelected = selectedId === prompt.id;

    return (
        <div className="tree-node">
            <div
                className={`tree-node-content ${isSelected ? "selected" : ""}`}
                // Indentation based on level - 20px per level feels about right
                // Could make this configurable if we need deeper nesting
                style={{ paddingLeft: `${level * 20 + 10}px` }}
                onClick={handleClick}
            >
                <div className="tree-node-header">
                    {hasNodes && (
                        <button
                            className="tree-node-toggle"
                            onClick={handleToggle}
                            aria-label={isExpanded ? "Collapse" : "Expand"}
                        >
                            {isExpanded ? "▼" : "▶"}
                        </button>
                    )}
                    {!hasNodes && <span className="tree-node-spacer" />}
                    <span className="tree-node-title">{prompt.title}</span>
                    {hasNodes && (
                        <span className="tree-node-count">({prompt.nodes.length})</span>
                    )}
                </div>
            </div>
            {hasNodes && isExpanded && (
                <div className="tree-node-children">
                    {prompt.nodes.map((node) => (
                        <div
                            key={node.nodeId || node.id}
                            className="tree-node-child"
                            style={{ paddingLeft: `${(level + 1) * 20 + 10}px` }}
                        >
                            <div className="tree-node-child-content">
                                <span className="tree-node-child-name">{node.name}</span>
                            </div>
                        </div>
                    ))}
                </div>
            )}
        </div>
    );
};

const TreeView = ({ prompts, onNodeClick, selectedId }) => {
    return (
        <div className="tree-view">
            {prompts.map((prompt) => (
                <TreeNode
                    key={prompt.id}
                    prompt={prompt}
                    onNodeClick={onNodeClick}
                    selectedId={selectedId}
                />
            ))}
        </div>
    );
};

export default TreeView;
