import { useState, useEffect } from 'react';
import { thirdPartyService } from '../../services/thirdPartyService';
import './ThirdParties.css';

function ThirdParties() {
    const [thirdParties, setThirdParties] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [showAddForm, setShowAddForm] = useState(false);
    const [editingId, setEditingId] = useState(null);
    const [formData, setFormData] = useState({
        name: '',
        relationship_type: '',
        date_of_birth: '',
        notes: '',
    });

    useEffect(() => {
        loadThirdParties();
    }, []);

    const loadThirdParties = async () => {
        try {
            setLoading(true);
            const data = await thirdPartyService.getThirdParties();
            setThirdParties(data);
        } catch (err) {
            setError(err.message);
        } finally {
            setLoading(false);
        }
    };

    const handleInputChange = (e) => {
        const { name, value } = e.target;
        setFormData(prev => ({
            ...prev,
            [name]: value,
        }));
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        try {
            if (editingId) {
                // Update existing third party
                const updated = await thirdPartyService.updateThirdParty(editingId, formData);
                setThirdParties(thirdParties.map(tp =>
                    tp.id === editingId ? updated : tp
                ));
                setEditingId(null);
            } else {
                // Create new third party
                const newThirdParty = await thirdPartyService.createThirdParty(formData);
                setThirdParties([...thirdParties, newThirdParty]);
            }

            // Reset form
            setFormData({
                name: '',
                relationship_type: '',
                date_of_birth: '',
                notes: '',
            });
            setShowAddForm(false);
        } catch (err) {
            setError(err.message);
        }
    };

    const handleEdit = (thirdParty) => {
        setFormData({
            name: thirdParty.name,
            relationship_type: thirdParty.relationship_type || '',
            date_of_birth: thirdParty.date_of_birth || '',
            notes: thirdParty.notes || '',
        });
        setEditingId(thirdParty.id);
        setShowAddForm(true);
    };

    const handleDelete = async (id) => {
        if (!window.confirm('Are you sure you want to delete this person? This will not delete their medications.')) {
            return;
        }

        try {
            await thirdPartyService.deleteThirdParty(id);
            setThirdParties(thirdParties.filter(tp => tp.id !== id));
        } catch (err) {
            setError(err.message);
        }
    };

    const handleCancel = () => {
        setFormData({
            name: '',
            relationship_type: '',
            date_of_birth: '',
            notes: '',
        });
        setEditingId(null);
        setShowAddForm(false);
    };

    if (loading) {
        return <div className="loading">Loading...</div>;
    }

    return (
        <div className="third-parties-container">
            <div className="third-parties-header">
                <h2>Family & Others</h2>
                <button
                    className="btn-add-third-party"
                    onClick={() => setShowAddForm(!showAddForm)}
                >
                    {showAddForm ? 'Cancel' : '+ Add Person'}
                </button>
            </div>

            {error && <div className="error-message">{error}</div>}

            {showAddForm && (
                <div className="third-party-form-card">
                    <h3>{editingId ? 'Edit Person' : 'Add New Person'}</h3>
                    <form onSubmit={handleSubmit} className="third-party-form">
                        <div className="form-group">
                            <label htmlFor="name">Name *</label>
                            <input
                                type="text"
                                id="name"
                                name="name"
                                value={formData.name}
                                onChange={handleInputChange}
                                required
                                placeholder="Enter name"
                            />
                        </div>

                        <div className="form-group">
                            <label htmlFor="relationship_type">Relationship</label>
                            <input
                                type="text"
                                id="relationship_type"
                                name="relationship_type"
                                value={formData.relationship_type}
                                onChange={handleInputChange}
                                placeholder="e.g., Child, Parent, Spouse"
                            />
                        </div>

                        <div className="form-group">
                            <label htmlFor="date_of_birth">Date of Birth</label>
                            <input
                                type="date"
                                id="date_of_birth"
                                name="date_of_birth"
                                value={formData.date_of_birth}
                                onChange={handleInputChange}
                            />
                        </div>

                        <div className="form-group">
                            <label htmlFor="notes">Notes</label>
                            <textarea
                                id="notes"
                                name="notes"
                                value={formData.notes}
                                onChange={handleInputChange}
                                rows="3"
                                placeholder="Additional information"
                            />
                        </div>

                        <div className="form-actions">
                            <button type="button" className="btn-cancel" onClick={handleCancel}>
                                Cancel
                            </button>
                            <button type="submit" className="btn-submit">
                                {editingId ? 'Update' : 'Add'} Person
                            </button>
                        </div>
                    </form>
                </div>
            )}

            <div className="third-parties-list">
                {thirdParties.length === 0 ? (
                    <div className="empty-state">
                        <p>No people added yet.</p>
                        <p>Add family members or others you manage medications for.</p>
                    </div>
                ) : (
                    <div className="third-parties-grid">
                        {thirdParties.map((thirdParty) => (
                            <div key={thirdParty.id} className="third-party-card">
                                <div className="third-party-header">
                                    <h3>{thirdParty.name}</h3>
                                    <div className="third-party-actions">
                                        <button
                                            className="btn-icon"
                                            onClick={() => handleEdit(thirdParty)}
                                            title="Edit"
                                        >
                                            ✏️
                                        </button>
                                        <button
                                            className="btn-icon"
                                            onClick={() => handleDelete(thirdParty.id)}
                                            title="Delete"
                                        >
                                            🗑️
                                        </button>
                                    </div>
                                </div>

                                {thirdParty.relationship_type && (
                                    <div className="third-party-info">
                                        <span className="info-label">Relationship:</span>
                                        <span className="info-value">{thirdParty.relationship_type}</span>
                                    </div>
                                )}

                                {thirdParty.date_of_birth && (
                                    <div className="third-party-info">
                                        <span className="info-label">Date of Birth:</span>
                                        <span className="info-value">
                                            {new Date(thirdParty.date_of_birth).toLocaleDateString()}
                                        </span>
                                    </div>
                                )}

                                {thirdParty.notes && (
                                    <div className="third-party-notes">
                                        <span className="info-label">Notes:</span>
                                        <p>{thirdParty.notes}</p>
                                    </div>
                                )}
                            </div>
                        ))}
                    </div>
                )}
            </div>
        </div>
    );
}

export default ThirdParties;
