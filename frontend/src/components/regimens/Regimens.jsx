import { useState, useEffect } from 'react';
import regimenService from '../../services/regimenService';
import medicationService from '../../services/medicationService';
import './Regimens.css';

function Regimens() {
    const [regimens, setRegimens] = useState([]);
    const [medications, setMedications] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [showAddForm, setShowAddForm] = useState(false);
    const [editingId, setEditingId] = useState(null);
    const [expandedId, setExpandedId] = useState(null);

    const [formData, setFormData] = useState({
        name: '',
        description: '',
        color: '#007bff',
        medication_ids: [],
    });

    useEffect(() => {
        loadData();
    }, []);

    const loadData = async () => {
        try {
            setLoading(true);
            const [regimensData, medsData] = await Promise.all([
                regimenService.getRegimens(),
                medicationService.getMedications({ active: true })
            ]);
            setRegimens(regimensData.regimens || []);
            setMedications(medsData.medications || []);
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

    const handleMedicationToggle = (medId) => {
        setFormData(prev => ({
            ...prev,
            medication_ids: prev.medication_ids.includes(medId)
                ? prev.medication_ids.filter(id => id !== medId)
                : [...prev.medication_ids, medId]
        }));
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        try {
            if (editingId) {
                // Update existing regimen (name, description, color only)
                const { medication_ids, ...updateData } = formData;
                const updated = await regimenService.updateRegimen(editingId, updateData);
                setRegimens(regimens.map(r => r.id === editingId ? updated : r));
                setEditingId(null);
            } else {
                // Create new regimen
                const newRegimen = await regimenService.createRegimen(formData);
                setRegimens([...regimens, newRegimen]);
            }

            // Reset form
            setFormData({
                name: '',
                description: '',
                color: '#007bff',
                medication_ids: [],
            });
            setShowAddForm(false);
        } catch (err) {
            setError(err.message);
        }
    };

    const handleEdit = (regimen) => {
        setFormData({
            name: regimen.name,
            description: regimen.description || '',
            color: regimen.color || '#007bff',
            medication_ids: regimen.medications.map(m => m.id),
        });
        setEditingId(regimen.id);
        setShowAddForm(true);
    };

    const handleDelete = async (id) => {
        if (!window.confirm('Are you sure you want to delete this regimen? The medications will not be deleted.')) {
            return;
        }

        try {
            await regimenService.deleteRegimen(id);
            setRegimens(regimens.filter(r => r.id !== id));
        } catch (err) {
            setError(err.message);
        }
    };

    const handleCancel = () => {
        setFormData({
            name: '',
            description: '',
            color: '#007bff',
            medication_ids: [],
        });
        setEditingId(null);
        setShowAddForm(false);
    };

    const handleAddMedication = async (regimenId, medicationId) => {
        try {
            const updated = await regimenService.addMedicationToRegimen(regimenId, medicationId);
            setRegimens(regimens.map(r => r.id === regimenId ? updated : r));
        } catch (err) {
            setError(err.message);
        }
    };

    const handleRemoveMedication = async (regimenId, medicationId) => {
        try {
            const updated = await regimenService.removeMedicationFromRegimen(regimenId, medicationId);
            setRegimens(regimens.map(r => r.id === regimenId ? updated : r));
        } catch (err) {
            setError(err.message);
        }
    };

    if (loading) {
        return <div className="loading">Loading...</div>;
    }

    return (
        <div className="regimens-container">
            <div className="regimens-header">
                <h2>Medication Regimens</h2>
                <button
                    className="btn-add-regimen"
                    onClick={() => setShowAddForm(!showAddForm)}
                >
                    {showAddForm ? 'Cancel' : '+ Create Regimen'}
                </button>
            </div>

            {error && <div className="error-message">{error}</div>}

            {showAddForm && (
                <div className="regimen-form-card">
                    <h3>{editingId ? 'Edit Regimen' : 'Create New Regimen'}</h3>
                    <form onSubmit={handleSubmit} className="regimen-form">
                        <div className="form-group">
                            <label htmlFor="name">Name *</label>
                            <input
                                type="text"
                                id="name"
                                name="name"
                                value={formData.name}
                                onChange={handleInputChange}
                                required
                                placeholder="e.g., Morning Routine, Bedtime Meds"
                            />
                        </div>

                        <div className="form-group">
                            <label htmlFor="description">Description</label>
                            <textarea
                                id="description"
                                name="description"
                                value={formData.description}
                                onChange={handleInputChange}
                                rows="2"
                                placeholder="Optional description"
                            />
                        </div>

                        <div className="form-group">
                            <label htmlFor="color">Color</label>
                            <input
                                type="color"
                                id="color"
                                name="color"
                                value={formData.color}
                                onChange={handleInputChange}
                            />
                        </div>

                        {!editingId && (
                            <div className="form-group">
                                <label>Medications</label>
                                <div className="medication-checkboxes">
                                    {medications.map((med) => (
                                        <label key={med.id} className="checkbox-label">
                                            <input
                                                type="checkbox"
                                                checked={formData.medication_ids.includes(med.id)}
                                                onChange={() => handleMedicationToggle(med.id)}
                                            />
                                            <span>{med.drug_name}</span>
                                        </label>
                                    ))}
                                </div>
                            </div>
                        )}

                        <div className="form-actions">
                            <button type="button" className="btn-cancel" onClick={handleCancel}>
                                Cancel
                            </button>
                            <button type="submit" className="btn-submit">
                                {editingId ? 'Update' : 'Create'} Regimen
                            </button>
                        </div>
                    </form>
                </div>
            )}

            <div className="regimens-list">
                {regimens.length === 0 ? (
                    <div className="empty-state">
                        <p>No regimens created yet.</p>
                        <p>Create a regimen to group medications you take together.</p>
                    </div>
                ) : (
                    <div className="regimens-grid">
                        {regimens.map((regimen) => (
                            <div key={regimen.id} className="regimen-card">
                                <div className="regimen-header">
                                    <div className="regimen-title">
                                        <div
                                            className="regimen-color-indicator"
                                            style={{ backgroundColor: regimen.color || '#007bff' }}
                                        />
                                        <h3>{regimen.name}</h3>
                                    </div>
                                    <div className="regimen-actions">
                                        <button
                                            className="btn-icon"
                                            onClick={() => handleEdit(regimen)}
                                            title="Edit"
                                        >
                                            ✏️
                                        </button>
                                        <button
                                            className="btn-icon"
                                            onClick={() => handleDelete(regimen.id)}
                                            title="Delete"
                                        >
                                            🗑️
                                        </button>
                                    </div>
                                </div>

                                {regimen.description && (
                                    <p className="regimen-description">{regimen.description}</p>
                                )}

                                <div className="regimen-medications">
                                    <div className="medications-header">
                                        <span className="med-count">
                                            {regimen.medications.length} medication{regimen.medications.length !== 1 ? 's' : ''}
                                        </span>
                                        <button
                                            className="btn-expand"
                                            onClick={() => setExpandedId(expandedId === regimen.id ? null : regimen.id)}
                                        >
                                            {expandedId === regimen.id ? '▼' : '▶'}
                                        </button>
                                    </div>

                                    {expandedId === regimen.id && (
                                        <div className="medications-list">
                                            {regimen.medications.map((med) => (
                                                <div key={med.id} className="medication-item">
                                                    <div className="med-info">
                                                        <span className="med-name">{med.drug_name}</span>
                                                        <span className="med-dose">{med.standard_dose}</span>
                                                    </div>
                                                    <button
                                                        className="btn-remove-med"
                                                        onClick={() => handleRemoveMedication(regimen.id, med.id)}
                                                        title="Remove from regimen"
                                                    >
                                                        ×
                                                    </button>
                                                </div>
                                            ))}

                                            {medications.filter(m => !regimen.medications.find(rm => rm.id === m.id)).length > 0 && (
                                                <div className="add-medication-section">
                                                    <select
                                                        onChange={(e) => {
                                                            if (e.target.value) {
                                                                handleAddMedication(regimen.id, e.target.value);
                                                                e.target.value = '';
                                                            }
                                                        }}
                                                        className="add-med-select"
                                                    >
                                                        <option value="">+ Add medication</option>
                                                        {medications
                                                            .filter(m => !regimen.medications.find(rm => rm.id === m.id))
                                                            .map((med) => (
                                                                <option key={med.id} value={med.id}>
                                                                    {med.drug_name}
                                                                </option>
                                                            ))}
                                                    </select>
                                                </div>
                                            )}
                                        </div>
                                    )}
                                </div>
                            </div>
                        ))}
                    </div>
                )}
            </div>
        </div>
    );
}

export default Regimens;
