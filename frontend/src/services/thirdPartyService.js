const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const getAuthHeaders = () => {
    const token = localStorage.getItem('access_token');
    return {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`,
    };
};

export const thirdPartyService = {
    // Get all third parties
    getThirdParties: async () => {
        const response = await fetch(`${API_URL}/api/third-parties/`, {
            headers: getAuthHeaders(),
        });
        if (!response.ok) {
            throw new Error('Failed to fetch third parties');
        }
        return response.json();
    },

    // Get a specific third party
    getThirdParty: async (id) => {
        const response = await fetch(`${API_URL}/api/third-parties/${id}`, {
            headers: getAuthHeaders(),
        });
        if (!response.ok) {
            throw new Error('Failed to fetch third party');
        }
        return response.json();
    },

    // Create a new third party
    createThirdParty: async (data) => {
        const response = await fetch(`${API_URL}/api/third-parties/`, {
            method: 'POST',
            headers: getAuthHeaders(),
            body: JSON.stringify(data),
        });
        if (!response.ok) {
            throw new Error('Failed to create third party');
        }
        return response.json();
    },

    // Update a third party
    updateThirdParty: async (id, data) => {
        const response = await fetch(`${API_URL}/api/third-parties/${id}`, {
            method: 'PUT',
            headers: getAuthHeaders(),
            body: JSON.stringify(data),
        });
        if (!response.ok) {
            throw new Error('Failed to update third party');
        }
        return response.json();
    },

    // Delete a third party
    deleteThirdParty: async (id) => {
        const response = await fetch(`${API_URL}/api/third-parties/${id}`, {
            method: 'DELETE',
            headers: getAuthHeaders(),
        });
        if (!response.ok) {
            throw new Error('Failed to delete third party');
        }
    },
};
