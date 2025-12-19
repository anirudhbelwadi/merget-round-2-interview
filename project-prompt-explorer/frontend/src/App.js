import { useState, useEffect } from "react";
import "./App.css";
import TreeView from "./components/TreeView";
import SidePanel from "./components/SidePanel";
import { fetchTree, fetchPrompt, fetchPromptNodes } from "./services/api";

function App() {
    const [treeData, setTreeData] = useState(null);
    const [prompts, setPrompts] = useState([]);
    const [selectedPrompt, setSelectedPrompt] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        loadTree();
    }, []);

    const loadTree = async () => {
        try {
            setLoading(true);
            const data = await fetchTree();

            // Backend returns prompt IDs related to the seeded project
            // We need to fetch full details for each prompt
            const promptIds = data.prompts || [];
            // Fetching all prompts in parallel - could be slow with many prompts
            // but the dataset is small so this is fine. Could optimize later with batching
            const promptDetails = await Promise.all(
                promptIds.map(async (promptId) => {
                    try {
                        const prompt = await fetchPrompt(promptId);
                        const nodes = await fetchPromptNodes(promptId);
                        // Combining prompt and nodes here so TreeView doesn't need to fetch again
                        return {
                            id: promptId,
                            title: prompt.title,
                            description: prompt.description,
                            parentPromptId: prompt.parentPromptId,
                            projectId: prompt.projectId,
                            nodes: nodes || []
                        };
                    } catch (err) {
                        // Don't fail the whole tree if one prompt fails - just skip it
                        console.error(`Failed to load prompt ${promptId}:`, err);
                        return null;
                    }
                })
            );

            // Filter out any failed fetches
            const validPrompts = promptDetails.filter(p => p !== null);

            setTreeData(data);
            setPrompts(validPrompts);
            setError(null);
        } catch (err) {
            setError("Failed to load tree data");
            console.error(err);
        } finally {
            setLoading(false);
        }
    };

    const handleNodeClick = async (promptId) => {
        try {
            const prompt = await fetchPrompt(promptId);
            const nodes = await fetchPromptNodes(promptId);
            setSelectedPrompt({
                id: promptId,
                title: prompt.title,
                description: prompt.description,
                parentPromptId: prompt.parentPromptId,
                projectId: prompt.projectId,
                nodes: nodes || []
            });
        } catch (err) {
            console.error("Failed to load prompt details:", err);
        }
    };

    const handleClosePanel = () => {
        setSelectedPrompt(null);
    };

    const handleNoteAdded = () => {
        // Reload the selected prompt to show new note
        if (selectedPrompt) {
            handleNodeClick(selectedPrompt.id);
        }
    };

    if (loading) {
        return (
            <div className="app-loading">
                <div>Loading...</div>
            </div>
        );
    }

    if (error) {
        return (
            <div className="app-error">
                <div>{error}</div>
                <button onClick={loadTree}>Retry</button>
            </div>
        );
    }

    return (
        <div className="app">
            <header className="app-header">
                <h1>Prompt Tree Explorer</h1>
                {treeData && (
                    <div className="app-header-info">
                        <h2>{treeData.project}</h2>
                        <br></br>
                        <p className="main-request">
                            <b>Main Request:</b> {treeData.mainRequest}
                        </p>
                        <p className="final-integration">
                            <b>Final Integration:</b> {treeData.finalIntegration}
                        </p>
                    </div>
                )}
            </header>
            <div className="app-content">
                <div className="tree-container">
                    {prompts.length > 0 && (
                        <TreeView
                            prompts={prompts}
                            onNodeClick={handleNodeClick}
                            selectedId={selectedPrompt?.id}
                        />
                    )}
                </div>
                {selectedPrompt && (
                    <SidePanel
                        prompt={selectedPrompt}
                        onClose={handleClosePanel}
                        onNoteAdded={handleNoteAdded}
                    />
                )}
            </div>
        </div>
    );
}

export default App;
