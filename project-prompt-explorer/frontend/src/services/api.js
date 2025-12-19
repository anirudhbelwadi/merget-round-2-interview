import axios from "axios";

// Allow override via env var for different environments
// Defaults to localhost for dev - production would have to set REACT_APP_API_URL
const API_BASE_URL = process.env.REACT_APP_API_URL || "http://localhost:5001";

const api = axios.create({
    baseURL: API_BASE_URL,
    headers: {
        "Content-Type": "application/json",
    },
});

// Helper to extract body from backend response wrapper
const extractBody = (response) => {
    const data = response.data;
    if (data.errorCode !== 200 && data.errorCode !== null) {
        throw new Error(data.errorMessage || "API request failed");
    }

    // Extract the actual body (everything except errorCode and errorMessage)
    const { errorCode, errorMessage, ...body } = data;
    return body;
};

export const fetchTree = async () => {
    const response = await api.get("/tree");
    return extractBody(response);
};

export const fetchPrompt = async (promptId) => {
    const response = await api.get(`/prompts/${promptId}`);
    return extractBody(response);
};

export const fetchPromptNodes = async (promptId) => {
    const response = await api.get(`/prompts/${promptId}/nodes`);
    const body = extractBody(response);
    return body.nodes || [];
};

export const addPrompt = async (parentId, promptData) => {
    const response = await api.post(`/prompts/${parentId}`, promptData);
    return extractBody(response);
};

export const addNode = async (promptId, nodeData) => {
    const response = await api.post(`/prompts/${promptId}/nodes`, nodeData);
    return extractBody(response);
};

export const fetchNotes = async (promptId) => {
    const response = await api.get(`/prompts/${promptId}/notes`);
    const body = extractBody(response);
    return body.notes || [];
};

export const addNote = async (promptId, noteData) => {
    const response = await api.post(`/prompts/${promptId}/notes`, noteData);
    return extractBody(response);
};
