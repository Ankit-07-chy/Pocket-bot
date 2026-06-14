import React, { useState, useEffect } from 'react';
import { expenses } from '../api';

function Expenses() {
    const [expenseList, setExpenseList] = useState([]);
    const [form, setForm] = useState({ amount: '', category: 'food', description: '', date: new Date().toISOString().split('T')[0] });
    const [summary, setSummary] = useState(null);
    const [alert, setAlert] = useState(null);
    const [error, setError] = useState('');
    const [success, setSuccess] = useState('');

    useEffect(() => { loadData(); }, []);

    async function loadData() {
        try {
            const [list, sum] = await Promise.all([
                expenses.list('limit=20'),
                expenses.summary(7)
            ]);
            setExpenseList(list);
            setSummary(sum);
        } catch (err) {
            console.error(err);
        }
    }

    async function handleSubmit(e) {
        e.preventDefault();
        setError('');
        setSuccess('');
        setAlert(null);

        try {
            const result = await expenses.add({
                ...form,
                amount: parseFloat(form.amount)
            });
            setSuccess(result.message);
            if (result.alert) setAlert(result.alert);
            setForm({ ...form, amount: '', description: '' });
            loadData();
        } catch (err) {
            setError(err.message);
        }
    }

    async function handleDelete(id) {
        try {
            await expenses.delete(id);
            loadData();
        } catch (err) {
            setError(err.message);
        }
    }

    return (
        <div>
            <h1 style={{ marginBottom: '24px' }}>💰 Expense Management</h1>

            {/* Add Expense Form */}
            <div className="card">
                <div className="card-header"><h2>Add Expense</h2></div>

                {error && <div className="alert alert-danger">{error}</div>}
                {success && <div className="alert alert-success">{success}</div>}
                {alert && <div className="alert alert-warning">⚠️ {alert.message}</div>}

                <form onSubmit={handleSubmit}>
                    <div className="form-row">
                        <div className="form-group">
                            <label htmlFor="amount">Amount (₹)</label>
                            <input id="amount" type="number" step="0.01" min="0.01" value={form.amount}
                                onChange={(e) => setForm({ ...form, amount: e.target.value })}
                                placeholder="150.00" required />
                        </div>
                        <div className="form-group">
                            <label htmlFor="category">Category</label>
                            <select id="category" value={form.category}
                                onChange={(e) => setForm({ ...form, category: e.target.value })}>
                                <option value="food">🍕 Food</option>
                                <option value="transport">🚌 Transport</option>
                                <option value="entertainment">🎬 Entertainment</option>
                                <option value="utilities">💡 Utilities</option>
                                <option value="education">📚 Education</option>
                                <option value="health">💊 Health</option>
                                <option value="other">📦 Other</option>
                            </select>
                        </div>
                    </div>
                    <div className="form-row">
                        <div className="form-group">
                            <label htmlFor="description">Description</label>
                            <input id="description" type="text" value={form.description}
                                onChange={(e) => setForm({ ...form, description: e.target.value })}
                                placeholder="Coffee at campus cafe" />
                        </div>
                        <div className="form-group">
                            <label htmlFor="expense-date">Date</label>
                            <input id="expense-date" type="date" value={form.date}
                                onChange={(e) => setForm({ ...form, date: e.target.value })} />
                        </div>
                    </div>
                    <button type="submit" className="btn btn-primary">Add Expense</button>
                </form>
            </div>

            {/* Summary Stats */}
            {summary && (
                <div className="stats-grid">
                    <div className="stat-card">
                        <div className="stat-value">₹{summary.total_spent.toFixed(2)}</div>
                        <div className="stat-label">Last 7 days</div>
                    </div>
                    <div className="stat-card">
                        <div className="stat-value">₹{summary.daily_average.toFixed(2)}</div>
                        <div className="stat-label">Daily avg</div>
                    </div>
                    <div className="stat-card">
                        <div className="stat-value" style={{ color: summary.over_budget ? 'var(--danger)' : 'var(--success)' }}>
                            ₹{summary.daily_budget.toFixed(2)}
                        </div>
                        <div className="stat-label">Daily budget</div>
                    </div>
                </div>
            )}

            {/* Expense List */}
            <div className="card">
                <div className="card-header"><h2>Recent Expenses</h2></div>
                {expenseList.length === 0 ? (
                    <div className="empty-state">
                        <p>No expenses yet. Start adding to track your spending!</p>
                    </div>
                ) : (
                    <div className="table-container">
                        <table>
                            <thead>
                                <tr>
                                    <th>Date</th>
                                    <th>Category</th>
                                    <th>Description</th>
                                    <th>Amount</th>
                                    <th>Action</th>
                                </tr>
                            </thead>
                            <tbody>
                                {expenseList.map(exp => (
                                    <tr key={exp.id}>
                                        <td>{exp.date}</td>
                                        <td style={{ textTransform: 'capitalize' }}>{exp.category}</td>
                                        <td>{exp.description || '—'}</td>
                                        <td><strong>₹{exp.amount.toFixed(2)}</strong></td>
                                        <td>
                                            <button className="btn btn-danger btn-small" onClick={() => handleDelete(exp.id)}>
                                                Delete
                                            </button>
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                )}
            </div>
        </div>
    );
}

export default Expenses;
