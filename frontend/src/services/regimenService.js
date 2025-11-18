const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const getAuthHeaders = () => {
    const token = localStorage.getItem('access_token');
    return {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`,
    };
};

export const regimenService = {
    // Get all regimens
    getRegimens: async () => {
        const response = await fetch(`${API_URL}/api/regimens/`, {
            headers: getAuthHeaders(),
        });
        if (!response.ok) {
            throw new Error('Failed to fetch regimens');
        }
        return response.json();
    },

    // Get a specific regimen
    getRegimen: async (id) => {
        const response = await fetch(`${API_URL}/api/regimens/${id}`, {
            headers: getAuthHeaders(),
        });
        if (!response.ok) {
            throw new Error('Failed to fetch regimen');
        }
        return response.json();
    },

    // Create a new regimen
    createRegimen: async (data) => {
        const response = await fetch(`${API_URL}/api/regimens/`, {
            method: 'POST',
            headers: getAuthHeaders(),
            body: JSON.stringify(data),
        });
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Failed to create regimen');
        }
        return response.json();
    },

    // Update a regimen
    updateRegimen: async (id, data) => {
        const response = await fetch(`${API_URL}/api/regimens/${id}`, {
            method: 'PUT',
            headers: getAuthHeaders(),
            body: JSON.stringify(data),
        });
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Failed to update regimen');
        }
        return response.json();
    },

    // Delete a regimen
    deleteRegimen: async (id) => {
        const response = await fetch(`${API_URL}/api/regimens/${id}`, {
            method: 'DELETE',
            headers: getAuthHeaders(),
        });
        if (!response.ok) {
            throw new Error('Failed to delete regimen');
        }
    },

    // Add medication to regimen
    addMedicationToRegimen: async (regimenId, medicationId) => {
        const response = await fetch(`${API_URL}/api/regimens/${regimenId}/medications/${medicationId}`, {
            method: 'POST',
            headers: getAuthHeaders(),
        });
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Failed to add medication to regimen');
        }
        return response.json();
    },

    // Remove medication from regimen
    removeMedicationFromRegimen: async (regimenId, medicationId) => {
        const response = await fetch(`${API_URL}/api/regimens/${regimenId}/medications/${medicationId}`, {
            method: 'DELETE',
            headers: getAuthHeaders(),
        });
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Failed to remove medication from regimen');
        }
        return response.json();
    },
};

export default regimenService;
