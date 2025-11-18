const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const getAuthHeaders = () => {
    const token = localStorage.getItem('access_token');
    return {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`,
    };
};

export const logService = {
    // Create a medication log entry
    createLog: async (logData) => {
        const response = await fetch(`${API_URL}/api/logs/`, {
            method: 'POST',
            headers: getAuthHeaders(),
            body: JSON.stringify(logData),
        });
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Failed to create log entry');
        }
        return response.json();
    },

    // Get medication logs with optional filters
    getLogs: async (params = {}) => {
        const queryParams = new URLSearchParams();

        if (params.skip !== undefined) queryParams.append('skip', params.skip);
        if (params.limit !== undefined) queryParams.append('limit', params.limit);
        if (params.medication_id) queryParams.append('medication_id', params.medication_id);
        if (params.start_date) queryParams.append('start_date', params.start_date);
        if (params.end_date) queryParams.append('end_date', params.end_date);

        const response = await fetch(`${API_URL}/api/logs/?${queryParams}`, {
            headers: getAuthHeaders(),
        });
        if (!response.ok) {
            throw new Error('Failed to fetch logs');
        }
        return response.json();
    },

    // Get a specific log entry
    getLog: async (logId) => {
        const response = await fetch(`${API_URL}/api/logs/${logId}`, {
            headers: getAuthHeaders(),
        });
        if (!response.ok) {
            throw new Error('Failed to fetch log entry');
        }
        return response.json();
    },

    // Update a log entry
    updateLog: async (logId, logData) => {
        const response = await fetch(`${API_URL}/api/logs/${logId}`, {
            method: 'PUT',
            headers: getAuthHeaders(),
            body: JSON.stringify(logData),
        });
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Failed to update log entry');
        }
        return response.json();
    },

    // Delete a log entry
    deleteLog: async (logId) => {
        const response = await fetch(`${API_URL}/api/logs/${logId}`, {
            method: 'DELETE',
            headers: getAuthHeaders(),
        });
        if (!response.ok) {
            throw new Error('Failed to delete log entry');
        }
    },

    // Get adherence statistics
    getAdherenceStats: async (days = 30, medicationId = null) => {
        const queryParams = new URLSearchParams();
        queryParams.append('days', days);
        if (medicationId) queryParams.append('medication_id', medicationId);

        const response = await fetch(`${API_URL}/api/logs/stats/adherence?${queryParams}`, {
            headers: getAuthHeaders(),
        });
        if (!response.ok) {
            throw new Error('Failed to fetch adherence stats');
        }
        return response.json();
    },
};

export default logService;
